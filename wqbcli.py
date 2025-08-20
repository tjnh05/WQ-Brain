import os
import sys  # 新增：引入 sys 模块
from datetime import datetime

import yaml
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

import wqb
from wqb import wqb_urls
wqb_urls.URL_ALPHAS_ALPHAID_SUBMIT.replace('http', 'https')
from wqb import WQBSession, FilterRange

import json
import argparse
import asyncio
import sqlite3
import itertools  # 新增：引入 itertools 模块
from typing import List, Dict, Any, Iterator, Generator, Set
import time
import pickle  # 新增：导入pickle模块
from pprint import pprint
import re  # 新增：引入 re 模块
import duckdb  # 新增：引入 duckdb 模块
import ast  # 新增：引入 ast 模块
import urllib3  # 新增：引入 urllib3 模块


class WorldQuantBRAINClient:
    def __init__(self, **kwargs):
        # 加载 .env 文件中的环境变量
        load_dotenv()

        # 从环境变量中读取 email 和 password
        self.email = os.getenv('WQB_EMAIL')
        self.password = os.getenv('WQB_PASSWORD')

        if not self.email or not self.password:
            raise ValueError("Missing WQB_EMAIL or WQB_PASSWORD in environment variables.")

        # 检查是否有输入参数log_name
        if 'log_name' in kwargs:
            log_name = kwargs['log_name']
            # 检查文件名是否包含目录
            if os.path.dirname(log_name):
                # 提取目录并创建
                log_dir = os.path.dirname(log_name)
                os.makedirs(log_dir, exist_ok=True)
            # 调用wqb.wqb_logger时输入参数名name
            self.logger = wqb.wqb_logger(name=log_name)
        else:
            self.logger = wqb.wqb_logger()

        # 新增：禁用SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 修改：在创建session时禁用SSL验证
        self.verified = False if os.getenv('VERIFIED') == 'false' else True
        self.session = WQBSession((self.email, self.password), logger=self.logger, verify=self.verified)
        # self.session = WQBSession((self.email, self.password), logger=self.logger)

        self.processed = False
        self.comment_pattern = re.compile(r'^\s*(//|#).*')  # 新增：定义注释行的正则表达式
        
        # 初始化 start_time 和 total_alphas
        self.start_time = None
        self.total_alphas = 0
        self.total_alphas_processed = 0

    # 新增：设置 start_time 的方法
    def set_start_time(self):
        self.start_time = time.time()

    # 新增：累加 total_alphas 的方法
    def increment_total_alphas(self, increment_value: int):
        self.total_alphas_processed += increment_value

    # 新增：统计输入文件中未处理的表达式数量
    def count_unprocessed_expressions(self, input_file: str):
        """统计输入文件中排除以 # 或 // 开头的行的数量"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError as e:
            self.logger.error(f"Input file not found: {input_file}")
            return

        unprocessed_count = sum(
            1 for line in lines if line.strip() and not self.comment_pattern.match(line.strip())
        )
        self.total_alphas = unprocessed_count
        self.logger.info(f"Total unprocessed expressions in {input_file}: {self.total_alphas}")

    # 新增：从fast expression中提取变量名的方法
    def extract_fields_from_expression(self, expression: str) -> Set[str]:
        """
        从fast expression字符串中提取字段名
        
        :param expression: fast expression字符串
        :return: 包含所有字段名的集合
        """
        try:
            # 使用 ast 解析表达式
            tree = ast.parse(expression, mode='eval')
            fields = set()
            
            # 遍历抽象语法树中的所有节点
            for node in ast.walk(tree):
                # 如果节点是名称节点且不是函数调用的一部分
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    # 检查父节点是否为函数调用，以排除函数名
                    is_function_name = False
                    for parent_node in ast.walk(tree):
                        if isinstance(parent_node, ast.Call) and parent_node.func is node:
                            is_function_name = True
                            break
                    
                    if not is_function_name:
                        fields.add(node.id)
            
            # 过滤掉以"pv13_"为前缀以及特定的变量名
            filtered_fields = {
                field for field in fields 
                if not field.startswith('pv13_') 
                and field.lower() not in {'subindustry',
                                          'industry',
                                          'sector',
                                          'market',
                                          'open',
                                          'close',
                                          'vwap',
                                          'volume'}
            }
            
            return filtered_fields
        except SyntaxError as e:
            self.logger.error(f"Failed to parse expression: {expression}, error: {e}")
            return set()

    def authenticate(self):
        """完成认证并测试连接"""
        resp = self.session.auth_request()
        self.logger.info(f"Authentication status code: {resp.status_code}")
        self.logger.info(f"User ID: {resp.json()['user']['id']}")

    def fetch_all_datasets(self, region: str, delay: int, universe: str):
        """获取平台上的所有数据集信息"""
        datasets_generator = self.session.search_datasets(
            region=region,
            delay=delay,
            universe=universe)
        datasets = []
        for resp in datasets_generator:
            try:
                # 修改：从 resp.json() 中提取 'results' 键的值，并添加异常处理
                if resp.content and resp.content.strip():
                    datasets.extend(resp.json()['results'])
                else:
                    self.logger.warning("Empty response received from server.")
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                # 异常处理：记录错误信息
                self.logger.error(f"Failed to parse response JSON: {e}")
                self.logger.error(f"Response content: {resp.text}")
        self.logger.info(f"Total datasets found: {len(datasets)}")
        return datasets

    def search_fields_with_alpha_count(self, region: str, delay: int, universe: str, dataset_id: str):
        """搜索数据集下的所有字段"""
        resps = self.session.search_fields(
            region=region,
            delay=delay,
            universe=universe,
            dataset_id=dataset_id
        )

        all_fields = []
        for idx, resp in enumerate(resps, start=1):
            self.logger.info(f"Processing response {idx}")
            fields = resp.json()
            for field in fields.get('results', []):
                # 增加 dataset_id 信息
                field['dataset_id'] = dataset_id
                all_fields.append(field)
                self.logger.info(f"Found field: {field}")

        # 按照 alphaCount 进行降序排序
        sorted_fields = sorted(all_fields, key=lambda x: x.get('alphaCount', 0), reverse=True)
        return sorted_fields

    def fetch_all_fields(self, region: str, delay: int, universe: str):
        """爬取所有数据集的字段信息"""
        datasets = self.fetch_all_datasets(region, delay, universe)
        all_fields = []

        for dataset in datasets:
            dataset_id = dataset['id']
            dataset_name = dataset['name']
            self.logger.info(f"Fetching fields for dataset: {dataset_name} (ID: {dataset_id})")
            fields = self.search_fields_with_alpha_count(region, delay, universe, dataset_id)
            all_fields.extend(fields)

        return all_fields

    def fetch_all_operators(self, region: str, delay: int, universe: str):
        """获取平台上的所有 operator 信息"""
        operators_generator = self.session.search_operators()
        operators = []

        # 检查 operators_generator 是否有 ok 属性且为 True
        if hasattr(operators_generator, 'ok') and operators_generator.ok:
            try:
                # 使用 text 键的值作为 json.loads 的参数
                resp_data = json.loads(operators_generator.text)
                # 从 resp_data 中提取 'results' 键的值
                operators.extend(resp_data)
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                # 异常处理：记录错误信息
                self.logger.warning(f"Failed to parse response: {e}")
                self.logger.warning(f"Response content: {operators_generator}")
        else:
            self.logger.warning("operators_generator does not have 'ok' attribute or it is not True.")

        self.logger.info(f"Total operators found: {len(operators)}")
        return operators

    def read_fields_from_file(self, file_path: str, alpha_count_threshold: int = 0, field_type: str = 'MATRIX'):
        """从文件中读取字段信息，并筛选符合条件的字段"""
        with open(file_path, 'r', encoding='utf-8') as f:
            all_fields = json.load(f)

        filtered_fields = [field for field in all_fields if field.get('alphaCount', 0) >= alpha_count_threshold and field.get('type') == field_type]
        self.logger.info(f"Filtered fields count: {len(filtered_fields)}")
        return filtered_fields

    def read_operators_from_file(self, file_path: str):
        """从文件中读取操作符信息"""
        with open(file_path, 'r', encoding='utf-8') as f:
            operators = json.load(f)
        self.logger.info(f"Total operators loaded from file: {len(operators)}")
        return operators

    def read_alpha_expressions_from_file(self, file_path: str):
        """从文件中逐行读取alpha表达式，返回生成器，并忽略以 // 或 # 开头的行"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                # 忽略空行和注释行
                if not stripped_line or self.comment_pattern.match(stripped_line):
                    continue
                yield stripped_line  # 直接返回表达式字符串

    def save_results_to_sqlite(self, results: List[Dict[str, Any]], db_path: str = 'alpha_results.db'):
        """将处理结果保存到SQLite数据库"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alpha_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT,
                description TEXT,
                result TEXT,
                error TEXT,
                start_time REAL,
                end_time REAL,
                duration REAL
            )
        ''')
        
        for result in results:
            if 'error' in result:
                cursor.execute('''
                    INSERT INTO alpha_results (expression, description, error, start_time, end_time, duration)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (result.get('regular', ''), result.get('description', ''), result['error'], result['start_time'], result['end_time'], result['duration']))
            else:
                cursor.execute('''
                    INSERT INTO alpha_results (expression, description, result, start_time, end_time, duration)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (result.get('regular', ''), result.get('description', ''), json.dumps(result), result['start_time'], result['end_time'], result['duration']))
        
        conn.commit()
        conn.close()
        self.logger.info(f"Results saved to SQLite database: {db_path}")

    def batch_concurrent_simulate_and_save(self,
                                           alpha_expressions: Generator[str, Any, None],
                                           output_file: str,
                                           concurrency: int = 6,
                                           size: int = 10,
                                           region: str = "USA",
                                           universe: str = "TOP3000",
                                           delay: int = 1,
                                           decay: int = 0,
                                           neutralization: str = "SUBINDUSTRY",
                                           truncation: float = 0.01,
                                           pasteurization: str = "ON",
                                           unit_handling: str = "VERIFY",
                                           nan_handling: str = "OFF",
                                           visualization: bool = False):
        """使用 concurrent_simulate 批量回测 alpha 表达式，并将结果保存到 pickle 文件"""
        window_size = concurrency * size  # 滑动窗口大小
        results = []  # 存储所有批次的结果

        try:
            while True:
                # 获取当前窗口的 alpha 表达式
                window_alphas = [
                    {
                        'type': 'REGULAR',
                        'settings': {
                            'instrumentType': 'EQUITY',
                            'region': region,  # 动态设置 region
                            'universe': universe,  # 动态设置 universe
                            'delay': delay,  # 动态设置 delay
                            'decay': decay,  # 动态设置 decay
                            'neutralization': neutralization,  # 动态设置 neutralization
                            'truncation': truncation,  # 动态设置 truncation
                            'pasteurization': pasteurization,  # 动态设置 pasteurization
                            'unitHandling': unit_handling,  # 动态设置 unit_handling
                            'nanHandling': nan_handling,  # 动态设置 nan_handling
                            'language': 'FASTEXPR',
                            'visualization': visualization  # 动态设置 visualization
                        },
                        'regular': expr
                    }
                    for expr in itertools.islice(alpha_expressions, window_size)
                ]

                # 如果窗口为空，表示已经处理完所有表达式
                if not window_alphas:
                    break

                # 将 alphas 转换为 multi_alphas
                multi_alphas = wqb.to_multi_alphas(window_alphas, size)

                # 使用 concurrent_simulate 进行批量回测
                resps = asyncio.run(
                    self.session.concurrent_simulate(
                        multi_alphas,  # 使用 multi_alphas
                        concurrency,
                        return_exceptions=True,
                        on_nolocation=lambda vars: self.logger.info(f"No location for target: {vars['target']}"),
                        on_start=lambda vars: self.logger.info(f"Task started with URL: {vars['url']}"),
                        on_finish=lambda vars: self.logger.info(f"Task finished with response: {vars['resp']}"),
                        on_success=lambda vars: self.logger.info(f"Task succeeded with response: {vars['resp']}"),
                        on_failure=lambda vars: self.logger.error(f"Task failed with response: {vars['resp']}")
                    )
                )

                # 处理响应结果
                for idx, resp in enumerate(resps, start=1):
                    self.logger.info(f"idx: {idx}, resp: {resp}")
                    # 修改：检查resp是否为异常对象
                    if isinstance(resp, Exception):
                        self.logger.error(f"Error occurred during simulation: {resp}")
                        continue
                    # 修改：检查是否有status_code属性且等于200
                    elif hasattr(resp, 'status_code') and resp.status_code == 200:
                        # 从 window_alphas 中提取第 idx 块内的 regular 数据
                        start_idx = (idx - 1) * size
                        end_idx = min(start_idx + size, len(window_alphas))
                        block_regular_values = [alpha['regular'] for alpha in window_alphas[start_idx:end_idx]]
                        self.logger.info(f"Block {idx} regular values: {block_regular_values}")
                        
                        # 将 block_regular_values 的每个元素追加到 results 列表中
                        results.extend(block_regular_values)
                        
                        # 记录已有表达式被处理
                        self.processed = True
                        
                        # 调用 increment_total_alphas 增加累计值 size
                        self.increment_total_alphas(size)

                        # 统计并显示当前累计处理的 alpha 数量、耗时及处理速度
                        elapsed_seconds, formatted_time, speed_per_minute, speed_per_day, progress_percentage = self.calculate_processing_speed()
                        self.logger.info(f"Current processed alphas: {self.total_alphas_processed} / {self.total_alphas}, progress: {progress_percentage}%")
                        self.logger.info(f"Elapsed time: {elapsed_seconds:.2f} seconds (~{formatted_time})")
                        self.logger.info(f"Processing speed: {speed_per_minute:.2f} alphas per minute, {speed_per_day:.2f} alphas per day")

                    else:
                        # 修改：安全地获取状态码
                        status_code = getattr(resp, 'status_code', 'Unknown')
                        self.logger.warning(f"Response status code: {status_code}. Skipping this block.")

        except Exception as e:
            self.logger.error(f"Error during batch simulation: {e}")
            raise
        finally:
            # 将最终结果保存到 pickle 文件
            if self.processed:
                with open(output_file, 'wb') as f:
                    pickle.dump(results, f)

            self.logger.info(f"Batch simulation results saved to {output_file}")

    def simulate_with_variants(self, expression: str, output_file: str, region: str = "USA",
                               universe: str = "TOP3000", delay: int = 1,
                               pasteurization: str = "ON", unit_handling: str = "VERIFY",
                               nan_handling: bool = False, visualization: bool = False):
        """
        对单个fast expression进行回测，遍历neutralization、decay和truncation的组合
        
        :param expression: fast expression字符串
        :param output_file: 输出文件路径
        :param region: 区域
        :param universe: 股票池
        :param delay: 延迟
        :param pasteurization: pasteurization设置
        :param unit_handling: unit handling设置
        :param nan_handling: NaN handling设置
        :param visualization: 是否可视化
        """
        # 定义参数组合
        neutralizations = ["SUBINDUSTRY", "INDUSTRY", "SECTOR", "MARKET"]
        decays = [0, 3, 6, 9, 12, 15, 18, 21]
        truncations = [0, 0.01, 0.05, 0.08, 0.1, 0.12, 0.15]
        
        # 生成所有参数组合
        param_combinations = list(itertools.product(neutralizations, decays, truncations))
        self.logger.info(f"Total combinations to simulate: {len(param_combinations)}")
        
        results = []
        
        # 设置开始时间
        self.set_start_time()
        self.total_alphas = len(param_combinations)
        
        try:
            for i, (neutralization, decay, truncation) in enumerate(param_combinations, 1):
                self.logger.info(f"Simulating combination {i}/{len(param_combinations)}: "
                                f"neutralization={neutralization}, decay={decay}, truncation={truncation}")
                
                # 构造alpha表达式
                alpha = [{
                    'type': 'REGULAR',
                    'settings': {
                        'instrumentType': 'EQUITY',
                        'region': region,
                        'universe': universe,
                        'delay': delay,
                        'decay': decay,
                        'neutralization': neutralization,
                        'truncation': truncation,
                        'pasteurization': pasteurization,
                        'unitHandling': unit_handling,
                        'nanHandling': "ON" if nan_handling else "OFF",
                        'language': 'FASTEXPR',
                        'visualization': visualization
                    },
                    'regular': expression
                }]
                
                # 执行回测 (concurrency=1)
                resps = asyncio.run(
                    self.session.concurrent_simulate(
                        alpha,
                        1,  # concurrency为1
                        return_exceptions=True,
                        on_nolocation=lambda vars: self.logger.info(f"No location for target: {vars['target']}"),
                        on_start=lambda vars: self.logger.info(f"Task started with URL: {vars['url']}"),
                        on_finish=lambda vars: self.logger.info(f"Task finished with response: {vars['resp']}"),
                        on_success=lambda vars: self.logger.info(f"Task succeeded with response: {vars['resp']}"),
                        on_failure=lambda vars: self.logger.error(f"Task failed with response: {vars['resp']}")
                    )
                )
                
                # 处理结果
                for resp in resps:
                    result_entry = {
                        'expression': expression,
                        'settings': {
                            'neutralization': neutralization,
                            'decay': decay,
                            'truncation': truncation,
                            'region': region,
                            'universe': universe,
                            'delay': delay,
                            'pasteurization': pasteurization,
                            'unitHandling': unit_handling,
                            'nanHandling': "ON" if nan_handling else "OFF"
                        },
                        'response': {
                            'status_code': resp.status_code
                        }
                    }
                    
                    if resp.status_code == 200:
                        try:
                            resp_data = resp.json()
                            result_entry['response']['data'] = resp_data
                            self.logger.info(f"Simulation successful: {neutralization}, {decay}, {truncation}")
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Failed to decode response JSON: {e}")
                            result_entry['response']['error'] = str(e)
                    else:
                        self.logger.warning(f"Simulation failed with status code: {resp.status_code}")
                        result_entry['response']['error'] = f"Status code: {resp.status_code}"
                        try:
                            result_entry['response']['error_details'] = resp.text
                        except:
                            pass
                    
                    results.append(result_entry)
                
                # 更新进度
                self.increment_total_alphas(1)
                elapsed_seconds, formatted_time, speed_per_minute, speed_per_day, progress_percentage = self.calculate_processing_speed()
                self.logger.info(f"Progress: {i}/{len(param_combinations)} ({progress_percentage:.1f}%)")
        
        except Exception as e:
            self.logger.error(f"Error during simulation: {e}")
            raise
        finally:
            # 保存结果到文件
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Simulation results saved to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to save results to {output_file}: {e}")
            
            # 输出最终统计
            elapsed_seconds, formatted_time, speed_per_minute, speed_per_day, progress_percentage = self.calculate_processing_speed()
            self.logger.info(f"Simulation completed. Total time: {formatted_time}")
            self.logger.info(f"Processing speed: {speed_per_minute:.2f} simulations per minute")

    def mark_processed_expressions(self, input_file: str, output_file: str) -> object:
        """
        标记已处理的 alpha 表达式，在 input_file 中对应的行首添加 //。
        :rtype: object
        :return: 
        :param input_file: 输入文件路径
        :param output_file: 输出文件路径（包含已处理的表达式）
        """
        try:
            # 使用 pickle 加载 output_file 中的内容
            with open(output_file, 'rb') as f:
                processed_expressions = set(pickle.load(f))  # 将 processed_expressions 转换为 set
        except (FileNotFoundError, EOFError) as e:
            self.logger.warning(f"Failed to load processed expressions from {output_file}: {e}")
            return

        if not processed_expressions:
            self.logger.warning("No processed expressions found.")
            return

        # 读取 input_file 的所有行
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError as e:
            self.logger.error(f"Input file not found: {input_file}")
            return
        except IOError as e:
            self.logger.error(f"Error reading input file: {e}")
            return

        # 修改 input_file 中对应的行，在行首添加 //
        modified_lines = []
        for line in lines:
            stripped_line = line.strip()
            try:
                # 忽略空行和注释行
                if stripped_line and not self.comment_pattern.match(stripped_line):
                    if stripped_line in processed_expressions:
                        modified_lines.append(f"//{line}")  # 在行首添加 //
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)
            except Exception as e:
                self.logger.warning(f"Failed to mark line: {e}")
                modified_lines.append(line)

        # 将修改后的内容写回 input_file
        try:
            with open(input_file, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
        except IOError as e:
            self.logger.error(f"Error writing to input file: {e}")
            return

        self.logger.info(f"Marked processed expressions in {input_file} with //")

    def calculate_processing_speed(self):
        """
        根据 start_time 和 total_alphas 计算平均处理速度。
        返回值：
        - elapsed_seconds: 经过的时间（秒）
        - formatted_time: 格式化的时间字符串（HH:MM:SS）
        - speed_per_minute: 每分钟处理的 alpha 个数
        - speed_per_day: 每天处理的 alpha 个数
        - progress_percentage: 已处理的 alpha 数目占总 alpha 数目的百分比
        """
        if self.start_time is None or self.total_alphas == 0:
            return 0, "00:00:00", 0, 0, 0

        # 计算经过的时间（秒）
        elapsed_seconds = time.time() - self.start_time

        # 防止除零错误
        if elapsed_seconds <= 0:
            return 0, "00:00:00", 0, 0, 0

        # 格式化时间字符串
        formatted_time = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))

        # 计算每分钟处理的 alpha 个数
        speed_per_minute = (self.total_alphas_processed / elapsed_seconds) * 60

        # 计算每天处理的 alpha 个数
        speed_per_day = speed_per_minute * 60 * 24

        # 新增：计算处理进度百分比
        progress_percentage = round((self.total_alphas_processed / self.total_alphas) * 100) if self.total_alphas > 0 else 0

        return elapsed_seconds, formatted_time, speed_per_minute, speed_per_day, progress_percentage

    def generate_config_file(self, output_file: str, fields_file: str = None, **kwargs):
        """
        生成类似 config.yaml 的配置文件。
        matrix fields 和 vector fields 分别通过 read_fields_from_file 方法获取。
        支持从 kwargs 中传入自定义的配置项。
        """
        try:
            # 检查 fields_file 是否为 None
            if fields_file is None:
                # 从 kwargs 中获取 matrix_fields 和 vector_fields
                matrix_fields = kwargs.get('matrix_fields', [])
                vector_fields = kwargs.get('vector_fields', [])
            else:
                # 检查文件是否存在
                if not os.path.exists(fields_file):
                    raise FileNotFoundError(f"Fields file not found: {fields_file}")
                
                # 调用 self.read_fields_from_file 获取 matrix_fields 和 vector_fields
                vector_fields = [field['id'] for field in self.read_fields_from_file(fields_file, field_type='VECTOR')]
                matrix_fields = [field['id'] for field in self.read_fields_from_file(fields_file, field_type='MATRIX')]

            # 构建配置字典，支持从 kwargs 中传入自定义值
            config = {
                "cs_operators": kwargs.get('cs_operators', [
                    "rank",
                    "score",
                    "zscore"
                ]),
                "ts_operators": kwargs.get('ts_operators', ['ts_zscore',
                                                             'ts_returns',
                                                             'ts_scale',
                                                             'ts_sum',
                                                             'ts_av_diff',
                                                             'ts_kurtosis',
                                                             'ts_mean',
                                                             'ts_rank',
                                                             'ts_ir',
                                                             'ts_delay',
                                                             'ts_quantile',
                                                             'ts_count_nans',
                                                             'ts_arg_min',  
                                                             'ts_delta',
                                                             'ts_backfill']),
                "ts_vec_operators": kwargs.get('ts_vec_operators', []),
                "group_operators": kwargs.get('group_operators', [ 'group_rank',  
                                                                   'group_scale',  
                                                                   'group_zscore',  
                                                                   'group_count',  
                                                                   'group_sum',  
                                                                   'group_neutralize']),
                "group_vec_operators": kwargs.get('group_vec_operators', []),
                "vector_fields": vector_fields,
                "matrix_fields": matrix_fields,
                "days": kwargs.get('days', [200, 600]),
                "groups": kwargs.get('groups', [
                    "subindustry",
                    "industry",
                    "sector",
                    "market",
                    "densify(pv13_h_f1_sector)"
                ])
            }

            # 将配置写入 YAML 文件
            with open(output_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(config, f, allow_unicode=True, sort_keys=False)

            self.logger.info(f"Configuration file generated successfully: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to generate configuration file: {e}")

    def render_fast_expressions(self, template_name: str, config_path: str, output_file: str):
        """
        根据提供的模板和配置文件渲染表达式，并将结果保存到输出文件。
        :param template_name: 模板文件名
        :param config_path: 配置文件路径
        :param output_file: 输出文件路径
        """
        try:
            # 加载配置
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)

            # 设置模板加载器
            env = Environment(loader=FileSystemLoader('templates'))
            
            # 加载模板
            template = env.get_template(template_name)
            
            # 渲染模板，使用 **config 扩展字典为键值对
            rendered_output = template.render(**config)
            
            # 删除空白行
            cleaned_output = [line for line in rendered_output.splitlines() if line.strip()]
            
            # 将列表转换为字符串并写入文件
            with open(output_file, 'w') as f:
                f.write("\n".join(cleaned_output))
        
            self.logger.info(f"Rendering completed, result saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to render expressions: {e}")

    def filter_alphas(self, status: str = 'UNSUBMITTED', region: str = 'USA', delay: int = 1, universe: str = 'TOP3000',
                      sharpe: FilterRange = None, fitness: FilterRange = None, turnover: FilterRange = None,
                      date_created: FilterRange = None, order: str = 'dateCreated', long_count: FilterRange = None):
        """
        根据指定条件过滤 alpha 表达式。
        :param status: Alpha 状态（默认为 'UNSUBMITTED'）
        :param region: 区域（默认为 'USA'）
        :param delay: 延迟设置（默认为 1）
        :param universe: 宇宙设置（默认为 'TOP3000'）
        :param sharpe: Sharpe 比率范围
        :param fitness: 适应度范围
        :param turnover: 转换率范围
        :param date_created: 创建日期范围
        :param order: 排序字段（默认为 'dateCreated'）
        :param long_count: Long count 范围（新增参数）
        :return: 符合条件的 alpha 结果生成器
        """
        resps = self.session.filter_alphas(
            status=status,
            region=region,
            delay=delay,
            universe=universe,
            sharpe=sharpe,
            fitness=fitness,
            turnover=turnover,
            date_created=date_created,
            order=order,
            long_count=long_count  # 新增：传递 long_count 参数
        )

        for resp in resps:
            try:
                results = resp.json().get('results', [])
                for result in results:
                    yield result
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                self.logger.error(f"Failed to parse response JSON: {e}")
                self.logger.error(f"Response content: {resp.text}")

    def update_duckdb(self, input_file: str, db_path: str = "alphas.duckdb"):
        """
        将输入文件中的 JSON 数据更新到 DuckDB 数据库中。
        :param input_file: 输入文件路径（JSON 格式）
        :param db_path: DuckDB 数据库路径
        """
        try:
            # 读取 JSON 文件
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 连接到 DuckDB 数据库
            conn = duckdb.connect(db_path)
            cursor = conn.cursor()

            # 创建表（如果不存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alphas (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    author TEXT,
                    settings TEXT,
                    regular TEXT,
                    dateCreated TEXT,
                    dateSubmitted TEXT,
                    dateModified TEXT,
                    name TEXT,
                    favorite BOOLEAN,
                    hidden BOOLEAN,
                    color TEXT,
                    category TEXT,
                    tags TEXT,
                    classifications TEXT,
                    grade TEXT,
                    stage TEXT,
                    status TEXT,
                    isData TEXT,
                    osData TEXT,
                    trainData TEXT,
                    testData TEXT,
                    prodData TEXT,
                    competitions TEXT,
                    themes TEXT,
                    pyramids TEXT,
                    pyramidThemes TEXT,
                    team TEXT
                )
            """)

            # 插入或更新数据
            for item in data:
                # 将 settings 等字段序列化为 JSON 字符串，并为缺失字段提供默认值
                settings_json = json.dumps(item.get("settings", {}))
                regular_json = json.dumps(item.get("regular", {}))
                is_data_json = json.dumps(item.get("is", {}))
                os_data_json = json.dumps(item.get("os", {}))
                train_data_json = json.dumps(item.get("train", {}))
                test_data_json = json.dumps(item.get("test", {}))
                prod_data_json = json.dumps(item.get("prod", {}))
                competitions_json = json.dumps(item.get("competitions", []))
                themes_json = json.dumps(item.get("themes", []))
                pyramids_json = json.dumps(item.get("pyramids", []))
                pyramid_themes_json = json.dumps(item.get("pyramidThemes", []))

                # 构造 SQL 插入语句，确保所有字段都有值
                cursor.execute("""
                    INSERT INTO alphas (
                        id, type, author, settings, regular, dateCreated, dateSubmitted, dateModified, name, favorite,
                        hidden, color, category, tags, classifications, grade, stage, status, isData, osData,
                        trainData, testData, prodData, competitions, themes, pyramids, pyramidThemes, team
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        type = excluded.type,
                        author = excluded.author,
                        settings = excluded.settings,
                        regular = excluded.regular,
                        dateCreated = excluded.dateCreated,
                        dateSubmitted = excluded.dateSubmitted,
                        dateModified = excluded.dateModified,
                        name = excluded.name,
                        favorite = excluded.favorite,
                        hidden = excluded.hidden,
                        color = excluded.color,
                        category = excluded.category,
                        tags = excluded.tags,
                        classifications = excluded.classifications,
                        grade = excluded.grade,
                        stage = excluded.stage,
                        status = excluded.status,
                        isData = excluded.isData,
                        osData = excluded.osData,
                        trainData = excluded.trainData,
                        testData = excluded.testData,
                        prodData = excluded.prodData,
                        competitions = excluded.competitions,
                        themes = excluded.themes,
                        pyramids = excluded.pyramids,
                        pyramidThemes = excluded.pyramidThemes,
                        team = excluded.team
                """, (
                    item.get("id", ""),  # 提供默认值
                    item.get("type", ""),
                    item.get("author", ""),
                    settings_json,
                    regular_json,
                    item.get("dateCreated", ""),
                    item.get("dateSubmitted", ""),
                    item.get("dateModified", ""),
                    item.get("name", ""),
                    item.get("favorite", False),
                    item.get("hidden", False),
                    item.get("color", ""),
                    item.get("category", ""),
                    json.dumps(item.get("tags", [])),
                    json.dumps(item.get("classifications", [])),
                    item.get("grade", ""),
                    item.get("stage", ""),
                    item.get("status", ""),
                    is_data_json,
                    os_data_json,
                    train_data_json,
                    test_data_json,
                    prod_data_json,
                    competitions_json,
                    themes_json,
                    pyramids_json,
                    pyramid_themes_json,
                    item.get("team", "")
                ))

            # 提交事务
            conn.commit()
            self.logger.info(f"Data from {input_file} has been updated to DuckDB database at {db_path}")
        except Exception as e:
            self.logger.error(f"Failed to update DuckDB: {e}")
        finally:
            # 关闭数据库连接
            conn.close()

    def check_alphas(self, alpha_ids: List[str], concurrency: int = 2):
        """
        检查指定的 alpha 表达式。
        :param alpha_ids: Alpha ID 列表
        :param concurrency: 并发级别
        """
        try:
            # 使用 concurrent_check 方法进行批量检查
            resps = asyncio.run(
                self.session.concurrent_check(
                    alpha_ids,
                    concurrency,
                    return_exceptions=True,
                    on_start=lambda vars: self.logger.info(f"Check started with URL: {vars['url']}"),
                    on_finish=lambda vars: self.logger.info(f"Check finished with response: {vars['resp']}"),
                    on_success=lambda vars: self.logger.info(f"Check succeeded: {vars['resp']}"),
                    on_failure=lambda vars: self.logger.error(f"Check failed: {vars['resp']}")
                )
            )

            # 将 alpha_ids 和 resps 通过 zip 组合，并通过生成器返回键值对
            for alpha_id, resp in zip(alpha_ids, resps):
                if isinstance(resp, Exception):
                    self.logger.error(f"Error checking alpha ID {alpha_id}: {str(resp)}")
                else:
                    try:
                        result = resp.json()
                        yield {alpha_id: result}
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to parse JSON response for alpha ID {alpha_id}")

        except Exception as e:
            self.logger.error(f"An error occurred during alpha checking: {e}")
            raise

    def submit_alpha(self, alpha_id: str):
        """
        提交指定的 Alpha 表达式。
        :param alpha_id: Alpha ID
        :return: 提交结果的响应对象
        """
        try:
            resp = asyncio.run(
                self.session.submit(
                    alpha_id,
                    on_start=lambda vars: self.logger.info(f"Submit started with URL: {vars['url']}"),
                    on_finish=lambda vars: self.logger.info(f"Submit finished with response: {vars['resp']}"),
                    on_success=lambda vars: self.logger.info(f"Submit succeeded with response: {vars['resp']}"),
                    on_failure=lambda vars: self.logger.error(f"Submit failed with response: {vars['resp']}"),
                    verify=self.verified
                )
            )
            self.logger.info(f"Alpha submission status code: {resp.status_code}")
            self.logger.info(f"Alpha submission response: {resp.text}")
            return resp
        except Exception as e:
            self.logger.error(f"An error occurred while submitting alpha: {e}")
            raise


def main():
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="Fetch data fields or operators from WorldQuant BRAIN platform.")
    
    # 修改：添加 --extract-variables 参数，支持不带参数的情况
    parser.add_argument("--extract-variables", nargs="?", const=True, default=None, help="Extract variable names from fast expression strings")
    
    # 新增：添加 --submit-alpha 参数
    parser.add_argument("--submit-alpha", type=str, help="Submit an alpha expression by providing its ID")

    # 修改：将 --check-alphas 参数改为接收多个参数值，移除 --alpha-ids 参数
    parser.add_argument("--check-alphas", type=str, nargs="*", help="Trigger alpha check process with specific alpha IDs")
    # 修改：将 --concurrency-check 参数的默认值从 2 改为 1
    parser.add_argument("--concurrency-check", type=int, default=1, help="Concurrency level for alpha checking (default: 1)")

    # 新增：添加 --start-date 和 --end-date 参数
    parser.add_argument("--start-date", type=str, help="Start date for filtering alphas (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--end-date", type=str, help="End date for filtering alphas (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")

    # 新增：添加 --sharpe-min 参数，默认值为 1.58
    parser.add_argument("--sharpe-min", type=float, default=1.58, help="Minimum Sharpe ratio for filtering alphas (default: 1.58)")
    
    # 新增：添加 --fitness-min 参数，默认值为 1
    parser.add_argument("--fitness-min", type=float, default=1, help="Minimum fitness for filtering alphas (default: 1)")
    
    # 新增：添加 --turnover-max 参数，默认值为 0.7
    parser.add_argument("--turnover-max", type=float, default=0.7, help="Maximum turnover for filtering alphas (default: 0.7)")

    parser.add_argument("--datasets", action="store_true",
                        help="Fetch and filter datasets based on alphaCount threshold")  # 新增：--datasets 参数
    parser.add_argument("--dataset-alpha-count", type=int, default=10000,  # 修改：参数名从 --alpha-count-threshold 改为 --dataset-alpha-count
                        help="Alpha count threshold for filtering datasets")  # 修改：缺省值改为10000
    parser.add_argument("--fields", action="store_true", help="Fetch fields for a specific dataset and save the results to <dataset_id>_fields.json and all_fileds.json")
    parser.add_argument("--dataset", type=str, required="--fields" in sys.argv, help="Dataset ID to fetch fields for")
    parser.add_argument("--operators", action="store_true", 
                        help="Fetch all operators and save the results to all_operators.json")
    parser.add_argument("--field-alpha-count", type=int, default=500, help="Field alpha count threshold (default: 0)")  # 修改：参数默认值从 800 改为 0
    parser.add_argument("--concurrency", type=int, default=7, help="Concurrency level for alpha processing (default: 7)")
    parser.add_argument("--convert", action="store_true", help="Convert alpha expressions to parameters.py")  # 修改：参数名从 --convert-alpha 改为 --convert
    parser.add_argument("--input-file", type=str, help="Input file path for alpha expressions")
    parser.add_argument("--output-file", type=str, help="Output file path for alpha expressions")  # 新增：输出文件参数
    parser.add_argument("--region", type=str, default="USA", help="Region to fetch data from (default: USA)")  # 新增：region参数
    parser.add_argument("--delay", type=int, default=1, help="Delay setting (default: 1)")  # 新增：delay参数
    parser.add_argument("--universe", type=str, default="TOP3000", help="Universe setting (default: TOP3000)")  # 新增：universe参数
    parser.add_argument("--multi-simulate", action="store_true", help="Batch simulate unprocessed alpha expressions concurrently")  # 新增：--multi-simulate 参数
    parser.add_argument("--size", type=int, default=10, help="Size parameter for batch simulation (default: 10)")  # 新增：--size 参数
    parser.add_argument("--decay", type=int, default=0, help="Decay setting (default: 0)")  # 新增：decay参数
    parser.add_argument("--neutralization", type=str, default="SUBINDUSTRY", help="Neutralization setting (default: SUBINDUSTRY)")  # 新增：neutralization参数
    parser.add_argument("--truncation", type=float, default=0.01, help="Truncation setting (default: 0.01)")  # 新增：truncation参数
    parser.add_argument("--pasteurization", type=str, default="ON", help="Pasteurization setting (default: ON)")  # 新增：pasteurization参数
    parser.add_argument("--unit-handling", type=str, default="VERIFY", help="Unit handling setting (default: VERIFY)")  # 新增：unit_handling参数
    parser.add_argument("--nan-handling", type=str, default="OFF", help="NaN handling setting (default: OFF)")  # 新增：nan_handling参数
    parser.add_argument("--visualization", action="store_true", default=False, help="Enable visualization (default: False)")  # 新增：visualization参数
    parser.add_argument("--periods", type=int, nargs="+", default=[60, 120, 250], help="Time periods for ts operators (default: [60, 120, 250])")  # 新增：--periods 参数
    parser.add_argument("--generate-config-file", action="store_true", help="Generate configuration file using generate_config_file method")
    parser.add_argument("--fields-file", type=str, required="--generate-config-file" in sys.argv, help="Fields file path for generating config file")
    parser.add_argument("--render-expressions", action="store_true", help="Render fast expressions using a template and configuration file")
    parser.add_argument("--template-file", type=str, help="Template file name for rendering expressions")
    parser.add_argument("--config-file", type=str, help="Configuration file path for rendering expressions")
    parser.add_argument("--output-render-file", type=str, help="Output file path for rendered expressions")
    parser.add_argument("--filter-alphas", action="store_true", help="Filter alphas based on specified criteria")  # 新增：--filter-alphas 参数
    parser.add_argument("--update-duckdb", action="store_true", help="Update DuckDB database with data from JSON file")  # 修改：类型从 str 改为 store_true
    parser.add_argument("--long-count-min", type=int, default=None, help="Minimum long count for filtering alphas (default: None)")

    parser.add_argument("--simulate-variants", type=str, help="Simulate expression variants with different parameter combinations")
    parser.add_argument("--nan-handling-bool", action="store_true", help="NaN handling as boolean flag (default: False)")

    args = parser.parse_args()

    if not any([args.dataset, args.datasets, args.operators,
                args.multi_simulate, args.convert, args.generate_config_file, args.render_expressions, args.filter_alphas, args.update_duckdb, args.check_alphas, args.submit_alpha, args.extract_variables, args.simulate_variants]):  # 新增：添加 --submit-alpha 到检查列表
        parser.print_help()
        return

    log_name = os.path.join("logs", "wqbcli"+ datetime.now().strftime('%Y%m%d%H%M%S'))

    # 初始化客户端（会自动从 .env 文件读取认证信息）
    client = WorldQuantBRAINClient(log_name=log_name)

    # 完成认证
    client.authenticate()
    
    # 新增：处理 --simulate-variants 参数
    if args.simulate_variants:
        if not args.output_file:
            client.logger.error("The '--output-file' parameter is required when using the '--simulate-variants' option.")
            return
            
        try:
            client.simulate_with_variants(
                expression=args.simulate_variants,
                output_file=args.output_file,
                region=args.region,
                universe=args.universe,
                delay=args.delay,
                pasteurization=args.pasteurization,
                unit_handling=args.unit_handling,
                nan_handling=args.nan_handling_bool,  # 使用布尔值参数
                visualization=args.visualization
            )
        except Exception as e:
            client.logger.error(f"An error occurred during variant simulation: {e}")
        return

    # 新增：处理 --extract-variables 参数
    if args.extract_variables is not None:
        try:
            # 获取所有需要处理的表达式
            expressions = []
            
            # 如果提供了输入文件，则从文件中读取表达式
            if args.input_file:
                try:
                    with open(args.input_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 从字典列表中提取regular.code字段
                        expressions = [item.get('regular', {}).get('code') for item in data if item.get('regular', {}).get('code')]
                except FileNotFoundError:
                    client.logger.error(f"Input file not found: {args.input_file}")
                    return
                except json.JSONDecodeError as e:
                    client.logger.error(f"Failed to parse JSON file: {args.input_file}, error: {e}")
                    return
            else:
                # 如果没有提供输入文件，则使用命令行参数中的表达式
                # 检查是否提供了表达式参数
                if args.extract_variables:
                    expressions = args.extract_variables
                else:
                    client.logger.error("Either --input-file or expressions must be provided for --extract-variables")
                    return
            
            # 遍历处理所有表达式，收集所有字段
            all_fields = set()  # 使用集合自动去重
            for expr in expressions:
                fields = client.extract_fields_from_expression(expr)
                all_fields.update(fields)
                
                # 输出到屏幕（保持原有逻辑）
                print(f"Expression: {expr}")
                print("Extracted fields:")
                for field in sorted(fields):
                    print(f"  {field}")
                print()  # 添加空行分隔不同表达式的输出
            
            # 转换为排序后的列表
            sorted_fields = sorted(list(all_fields))
            
            # 构建结果（不包含expression字段）
            result = {
                "fields": sorted_fields
            }
            
            # 如果提供了输出文件参数，则将结果保存到JSON文件
            if args.output_file:
                try:
                    with open(args.output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=4, ensure_ascii=False)
                    # 修改为warning级别日志
                    client.logger.warning(f"Extracted fields have been saved to {args.output_file}")
                except Exception as e:
                    client.logger.error(f"Failed to save results to file: {e}")
            else:
                # 如果没有提供输出文件，则输出到屏幕
                print("All unique fields (sorted):")
                for field in sorted_fields:
                    print(field)
                
            return
        except Exception as e:
            client.logger.error(f"An error occurred while extracting fields: {e}")
            return

    if args.submit_alpha:  # 新增：处理 --submit-alpha 参数
        try:
            # 调用 submit_alpha 方法提交指定的 Alpha ID
            resp = client.submit_alpha(alpha_id=args.submit_alpha)
            
            # 在终端上输出返回的信息
            print(f"Alpha submission status code: {resp.status_code}")
            print(f"Alpha submission response: {resp.text}")
        except Exception as e:
            client.logger.error(f"An error occurred while submitting alpha: {e}")
        return

    if args.check_alphas:  # 新增：处理 --check-alphas 参数
        try:
            # 如果没有指定 --check_alphas，则从输入文件中读取 alpha ID 列表
            if not args.check_alphas:
                input_file = args.input_file or f"{args.region}_{args.delay}_{args.universe}_alphas.json"
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    args.check_alphas = [item.get("id") for item in data if item.get("id")]
                except FileNotFoundError:
                    client.logger.error(f"Input file not found: {input_file}")
                    return
                except json.JSONDecodeError:
                    client.logger.error(f"Failed to parse JSON file: {input_file}")
                    return

            # 设置输出文件名
            output_file = args.output_file or f"{args.region}_{args.delay}_{args.universe}_check.json"

            # 调用 check_alphas 方法进行批量检查
            checked_results = []
            for result in client.check_alphas(alpha_ids=args.check_alphas, concurrency=args.concurrency_check):
                checked_results.append(result)

            # 比较 args.alpha_ids 和 checked_results 的长度
            if len(args.check_alphas) > len(checked_results):
                client.logger.warning(f"Some alpha IDs did not have their check results retrieved. Expected: {len(args.alpha_ids)}, Retrieved: {len(checked_results)}")

            # 将检查结果保存到输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(checked_results, f, indent=4, ensure_ascii=False)

            client.logger.info(f"Alpha check report has been saved to {output_file}")
            
            # 新增：将检查结果输出到屏幕
            client.logger.warning("Alpha check results:")
            for result in checked_results:
                client.logger.warning(json.dumps(result, indent=2, ensure_ascii=False))

        except Exception as e:
            client.logger.error(f"An error occurred during alpha checking: {e}")
        return

    if args.update_duckdb:  # 新增：处理 --update-duckdb 参数
        try:
            # 如果 args.input_file 为空或 None，则使用默认文件名
            input_file = args.input_file or f"{args.region}_{args.delay}_{args.universe}_alphas.json"
            
            # 调用 update_duckdb 方法，并传入动态生成的输入文件名
            client.update_duckdb(input_file)
        except Exception as e:
            client.logger.error(f"An error occurred while updating DuckDB: {e}")
        return

    if args.render_expressions:
        # 检查是否提供了 --template-file 和 --config-file 参数
        if not args.template_file or not args.config_file or not args.output_render_file:
            client.logger.error(
                "The '--template-file', '--config-file', and '--output-render-file' parameters are required when using the '--render-expressions' option.")
            return

        try:
            # 调用 render_fast_expressions 方法渲染表达式
            client.render_fast_expressions(
                template_name=args.template_file,
                config_path=args.config_file,
                output_file=args.output_render_file
            )
        except Exception as e:
            client.logger.error(f"Failed to render expressions: {e}")
        return

    if args.generate_config_file:
        # 检查是否提供了 --output-file 和 --fields-file 参数
        if not args.output_file or not args.fields_file:
            client.logger.error(
                "The '--output-file' and '--fields-file' parameters are required when using the '--generate-config-file' option.")
            return

        try:
            # 调用 generate_config_file 方法生成配置文件
            client.generate_config_file(output_file=args.output_file,
                                        fields_file=args.fields_file,
                                        days=args.periods)
        except Exception as e:
            client.logger.error(f"Failed to generate configuration file: {e}")
        return

    if args.multi_simulate:  # 新增：处理 --multi-simulate 参数
        # 检查是否提供了 --input-file 和 --output-file 参数
        if not args.input_file or not args.output_file:
            client.logger.error(
                "The '--input-file' and '--output-file' parameters are required when using the '--multi-simulate' option.")
            return

        # 统计未处理的表达式数量
        client.count_unprocessed_expressions(args.input_file)

        # 如果输出文件存在，则尝试标识已处理的表达式
        if os.path.exists(args.output_file):
            client.mark_processed_expressions(args.input_file, args.output_file)

        # 获取未处理的 alpha 表达式
        unprocessed_alphas = client.read_alpha_expressions_from_file(file_path=args.input_file)

        try:
            # 设置开始时间
            client.set_start_time()

            # 批量并行回测未处理的 alpha 表达式
            client.batch_concurrent_simulate_and_save(
                alpha_expressions=unprocessed_alphas,  # 直接传递迭代器
                output_file=args.output_file,
                concurrency=args.concurrency,
                size=args.size,  # 新增：传递 size 参数
                region=args.region,
                universe=args.universe,
                delay=args.delay,
                decay=args.decay,  # 新增：传递 decay 参数
                neutralization=args.neutralization,  # 新增：传递 neutralization 参数
                truncation=args.truncation,  # 新增：传递 truncation 参数
                pasteurization=args.pasteurization,  # 新增：传递 pasteurization 参数
                unit_handling=args.unit_handling,  # 新增：传递 unit_handling 参数
                nan_handling=args.nan_handling,  # 新增：传递 nan_handling 参数
                visualization=args.visualization  # 新增：传递 visualization 参数
            )
        except Exception as e:
            # 捕获异常并记录错误日志
            client.logger.error(f"An error occurred during multi-simulation: {e}")

        finally:
            # 计算处理速度和进度
            elapsed_seconds, formatted_time, speed_per_minute, speed_per_day, progress_percentage = client.calculate_processing_speed()

            # 输出统计信息到日志
            client.logger.info(
                f"Current processed alphas: {client.total_alphas_processed} / {client.total_alphas}, progress: {progress_percentage}%")
            client.logger.info(f"Elapsed time: {elapsed_seconds:.2f} seconds (~{formatted_time})")
            client.logger.info(
                f"Processing speed: {speed_per_minute:.2f} alphas per minute, {speed_per_day:.2f} alphas per day")
            client.logger.info(f"Progress: {progress_percentage:.2f}%")  # 新增：输出处理进度

            # 在 finally 块中执行标记已处理表达式的操作
            if client.processed:
                try:
                    client.mark_processed_expressions(args.input_file, args.output_file)
                except Exception as e:
                    client.logger.warning(f"Failed to mark processed expressions. {e}")

            client.logger.info(f"Batch simulation completed. Results saved to {args.output_file}.")

        return

    if args.datasets:  
        datasets = client.fetch_all_datasets(
            region=args.region,
            delay=args.delay,
            universe=args.universe,
        )
        
        # 修改：使用 args.output_file 或默认文件名
        output_file = args.output_file or f"{args.region}_{args.delay}_{args.universe}_datasets.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(datasets, f, indent=4, ensure_ascii=False)

        # 修改：在过滤数据集后按 alphaCount 降序排序
        filtered_datasets = [dataset['id'] for dataset in datasets if dataset['alphaCount'] >= args.dataset_alpha_count]
        filtered_datasets_sorted = sorted(filtered_datasets, key=lambda id: next(d['alphaCount'] for d in datasets if d['id'] == id), reverse=True)
        pprint(filtered_datasets_sorted)
        client.logger.info(f"Datasets have been saved to {output_file}")

    if args.fields:
        # 获取指定数据集的字段信息
        dataset_id = args.dataset
        fields = client.search_fields_with_alpha_count(
            region=args.region,
            delay=args.delay,
            universe=args.universe,
            dataset_id=dataset_id
        )

        # 修改：使用 args.output_file 或默认文件名
        output_file = args.output_file or f"{args.region}_{args.delay}_{args.universe}_fields.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(fields, f, indent=4, ensure_ascii=False)
        client.logger.info(f"Fields for dataset {dataset_id} have been saved to {output_file}")

    if args.filter_alphas:  # 新增：处理 --filter-alphas 参数
        try:
            # 解析 --start-date 和 --end-date 参数
            start_date = args.start_date
            end_date = args.end_date

            # 如果日期格式为 YYYY-MM-DD，则自动补全为 YYYY-MM-DDT00:00:00
            if start_date and len(start_date) == 10:
                start_date += "T00:00:00-08:00"
            if end_date and len(end_date) == 10:
                end_date += "T00:00:00-08:00"

            # 将日期字符串转换为 datetime 对象
            start_date = datetime.fromisoformat(start_date) if start_date else None
            end_date = datetime.fromisoformat(end_date) if end_date else None
            
            # 构造 date_created 范围
            date_created_range = FilterRange.from_str(f"[{start_date.isoformat()}, {end_date.isoformat()})") if start_date and end_date else None

            # 新增：构造 long_count 范围
            long_count_range = FilterRange.from_str(f"[{args.long_count_min}, inf)") if args.long_count_min is not None else None

            # 调用 filter_alphas 方法，直接返回结果
            results = list(client.filter_alphas(
                status='UNSUBMITTED',
                region=args.region,
                delay=args.delay,
                universe=args.universe,
                sharpe=FilterRange.from_str(f"[{args.sharpe_min}, inf)"),
                fitness=FilterRange.from_str(f"[{args.fitness_min}, inf)"),
                turnover=FilterRange.from_str(f"(-inf, {args.turnover_max}]"),
                date_created=date_created_range,
                order='dateCreated',
                long_count=long_count_range  # 新增：传递 long_count 范围
            ))

            # 设置缺省输出文件名
            output_file = args.output_file or f"{args.region}_{args.delay}_{args.universe}_alphas.json"

            # 将 results 保存到 JSON 文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            
            client.logger.info(f"Filtered alphas have been saved to {output_file}")
        except Exception as e:
            client.logger.error(f"An error occurred while filtering alphas: {e}")
        return

    # 修改：新增对 --update-duckdb 参数的逻辑调整
    if args.update_duckdb:  # 新增：处理 --update-duckdb 参数
        try:
            # 如果 args.input_file 为空或 None，则使用默认文件名
            input_file = args.input_file or f"{args.region}_{args.delay}_{args.universe}_alphas.json"
            
            # 调用 update_duckdb 方法，并传入动态生成的输入文件名
            client.update_duckdb(input_file)
        except Exception as e:
            client.logger.error(f"An error occurred while updating DuckDB: {e}")
        return


if __name__ == "__main__":
    main()

