#! /usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import logging
import os
import random
import threading
import traceback
from datetime import datetime

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
import urllib3
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取本模块的 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 移除默认的日志处理器
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# 创建标准输出处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 检查环境变量 WQ_LOG_TO_FILE 是否存在且值为 True
if os.getenv('WQ_LOG_TO_FILE', '').lower() == 'true':
    # 创建日志目录
    log_dir = os.path.join('data', 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建文件处理器
    log_file = os.path.join(log_dir, f"api_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


class WQSession(requests.Session):
    def __init__(self, **kwargs):
        super().__init__()
        self.lock = threading.Lock()
        self.verify = kwargs.get('verify', os.getenv("WQ_CERT_VERIFY", 'True')) == 'True'
        self.max_workers = kwargs.get('max_workers', 2)
        self.json_fn = kwargs.get('json_fn', os.path.join('data', 'credentials.json'))
        self.processed_file_name = kwargs.get('processed_file_name', os.path.join('data', 'processed.txt'))
        self.auth_url = 'https://api.worldquantbrain.com/authentication'
        self.simulate_url = 'https://api.worldquantbrain.com/simulations'
        self.status_base_url = 'https://api.worldquantbrain.com/alphas/'
        self.alpha_base_url = 'https://platform.worldquantbrain.com/alphas/'
        self.proxies = kwargs.get('proxies')
        self.login_expired = False
        self.rows_processed = []

        # 读取 email 和 password
        self.email = os.getenv('WQ_EMAIL')
        self.password = os.getenv('WQ_PASSWORD')
        self._load_credentials()
        self.auth = (self.email, self.password)

        # 结果文件
        if not os.path.exists('data'):
            os.makedirs('data')
        self.csv_file = os.path.join("data", "api_results.csv")

    def _load_credentials(self):
        """
        从 self.json_fn 文件中读取 email 和 password。
        如果文件不存在或格式不正确，抛出异常。
        """
        if self.email and self.password:
            return  # 如果环境变量中已经设置了 email 和 password，直接返回

        try:
            with open(self.json_fn, 'r') as f:
                creds = json.load(f)  # 使用 json.load 直接加载文件内容
                if not isinstance(creds, dict):
                    raise ValueError(f"Invalid JSON format in {self.json_fn}: expected a dictionary.")

                self.email = creds.get('email')
                self.password = creds.get('password')

                if not self.email or not self.password:
                    raise ValueError(f"Email or password is missing in {self.json_fn}.")

        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file {self.json_fn} not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {self.json_fn}.")
        except Exception as e:
            raise ValueError(f"Failed to load credentials from {self.json_fn}: {e}")

        # 确保 email 和 password 都有值
        if not self.email or not self.password:
            raise ValueError("Email and password must be provided via environment variables or credentials file.")

        # self.auth = HTTPBasicAuth(self.email, self.password)
        self.auth = (self.email, self.password)

    def login(self):
        try:
            response = self.post(self.auth_url, proxies=self.proxies, verify=self.verify)
            response_data = response.json()

            if 'user' in response_data:
                logger.info(f'user {response_data['user'].get('id')} has logged into WQBrain!')
                self.login_expired = False
                return True
            elif 'inquiry' in response_data:
                inquiry_url = f"{response.url}/persona?inquiry={response_data['inquiry']}"
                input(f"Please complete biometric authentication at {inquiry_url} before continuing...")
                self.post(f"{response.url}/persona", json=response_data, proxies=self.proxies, verify=self.verify)
                return True
            else:
                logger.warning(f'Login failed: {response_data}')
                raise Exception(f'Login failed: {response_data}')
        except Exception as e:
            logger.error(f'Login error: {e}')
            raise


    def process_simulation(self, simulation):
        alpha = simulation.get('regular')
        if not alpha:
            logger.error(f'No alpha code found in simulation: {simulation}')
            raise ValueError(f'No alpha code found in simulation: {simulation}')

        with self.lock:
            if self.login_expired:
                logger.info(f'Login expired, re-logging in...')
                try:
                    self.login()
                except Exception as e:
                    logger.error(f're-login into WQBrain:{e}')
                    raise

        thread = current_thread().name
        delay = simulation.get('delay', os.getenv('WQ_DELAY', 1))
        universe = simulation.get('universe', os.getenv('WQ_UNIVERSE', 'TOP3000'))
        truncation = simulation.get('truncation', os.getenv('WQ_TRUNCATION', 0.02))
        region = simulation.get('region', os.getenv('WQ_REGION', 'USA'))
        decay = simulation.get('decay', os.getenv('WQ_DECAY', 8))
        neutralization = simulation.get('neutralization', os.getenv('WQ_NEUTRALIZATION', 'SUBINDUSTRY')).upper()
        pasteurization = simulation.get('pasteurization', os.getenv('WQ_PASTEURIZATION', 'ON'))
        nan = simulation.get('nanHandling', os.getenv('WQ_NANHANDLING', 'OFF'))
        language = simulation.get('language', os.getenv('WQ_LANGUAGE', 'FASTEXPR'))
        wq_type = simulation.get('type', os.getenv('WQ_TYPE', 'REGULAR'))
        instrument_type = simulation.get('instrumentType', os.getenv('WQ_INSTRUMENTTYPE', 'EQUITY'))
        unit_handling = simulation.get('unitHandling', os.getenv('WQ_UNITHANDLING', 'VERIFY'))
        logger.info(f"{thread} -- Simulating alpha: {alpha}")

        nxt = None
        while True:
            # keep sending a post request until the simulation link is found
            r = None
            try:
                payload = {
                    'regular': alpha,
                    'type': wq_type,
                    'settings': {
                        "nanHandling": nan,
                        "instrumentType": instrument_type,
                        "delay": delay,
                        "universe": universe,
                        "truncation": truncation,
                        "unitHandling": unit_handling,
                        "pasteurization": pasteurization,
                        "region": region,
                        "language": language,
                        "decay": decay,
                        "neutralization": neutralization,
                        "visualization": False
                    }
                }
                logger.info(
                    f'{thread} -- decay: {decay}, truncation: {truncation}, neutralization: {neutralization}')
                r = self.post(self.simulate_url, json=payload)
                r.raise_for_status()
                if r is not None:
                    nxt = r.headers['Location']
                    logger.info(f'{thread} -- Obtained simulation link: {nxt}')
                break
            except Exception as e:
                try:
                    if r is not None and 'credentials' in r.json().get('detail'):
                        self.login_expired = True
                        return
                except:
                    if r is not None:
                        logger.error(f'{thread} -- {r.content}')  # usually gateway timeout
                    return
                finally:
                    logger.error(f'{thread} -- {e}')

        ok = True
        alpha_link = None
        while nxt:
            sim_progress_resp = self.get(nxt)
            retry_after_sec = float(sim_progress_resp.headers.get("Retry-After", 0))
            response = sim_progress_resp.json()
            if retry_after_sec == 0:  # simulation done!模拟完成!
                if 'alpha' in response:
                    alpha_link = response['alpha']
                else:
                    logger.error(f'{thread} -- Issue when sending simulation request [{alpha}]: {response}')
                break
            else:
                try:
                    progress = int(100 * response['progress'])
                    logger.info(f"{thread} -- {alpha} - {progress}%")
                    if progress < 80:
                        time.sleep(retry_after_sec + random.uniform(5, 10))
                    else:
                        time.sleep(retry_after_sec)
                except Exception as e:
                    logger.error(f'{thread} -- {e}')
                    ok = (False, response.get('message', 'Unknown error'))
                    break

        weight_check = None
        subsharpe = None

        if ok is not True:
            logger.error(f'{thread} -- Issue when sending simulation request [{alpha}]: {ok[1]}')
            row = [
                0, delay, region,
                neutralization, decay, truncation,
                0, 0, 0, 'FAIL', 0, -1, universe, nxt, alpha
            ]
        else:
            r = self.get(f'{self.status_base_url}{alpha_link}').json()
            logger.info(
                f'{thread} -- Obtained alpha link: {self.alpha_base_url}{alpha_link}')

            passed, failed_count = 0, 0
            for check in r['is']['checks']:
                if check['name'] == 'CONCENTRATED_WEIGHT':
                    weight_check = check['result']
                if check['name'] == 'LOW_SUB_UNIVERSE_SHARPE':
                    subsharpe = check.get('value', -1)

                # 如果检查未通过，输出失败原因
                if check['result'] == 'PASS':
                    passed += 1
                elif check['result'] == 'FAIL':
                    failed_count += 1
                    reason = f"Check item '{check['name']}' failed: Current value {check.get('value', 'N/A')}, Limit value {check.get('limit', 'N/A')}"
                    logger.info(f'{thread} -- {alpha_link} - {reason}')
            logger.info(f'{thread} -- {alpha_link} - sharpe: {r["is"]["sharpe"]}, fitness: {r["is"]["fitness"]}, turnover: {round(100 * r["is"]["turnover"], 2)}%')
            logger.info(f'{thread} -- {alpha_link} - Total PASS: {passed}, Total FAIL: {failed_count}')

            self.rows_processed.append(simulation)

            row = [
                passed, delay, region,
                neutralization, decay, truncation,
                r['is']['sharpe'],
                r['is']['fitness'],
                round(100 * r['is']['turnover'], 2),
                weight_check,
                subsharpe,
                -1,
                universe,
                f'{self.alpha_base_url}{alpha_link}',
                alpha
            ]

        return row

    def simulate(self, data, **kwargs):
        self.rows_processed = []
        self.login()

        # 主函数处理部分
        try:
            # 固定CSV文件名
            file_exists = os.path.isfile(self.csv_file)

            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                # 如果文件不存在，写入header
                if not file_exists:
                    header = [
                        'passed', 'delay', 'region', 'neutralization', 'decay', 'truncation',
                        'sharpe', 'fitness', 'turnover', 'weight',
                        'subsharpe', 'correlation', 'universe', 'link', 'regular'
                    ]
                    writer.writerow(header)

                # 使用线程池处理数据
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    for row in executor.map(self.process_simulation, data):
                        if row:  # 如果row不为空，写入CSV
                            writer.writerow(row)
                            f.flush()  # 确保数据立即写入文件
                            logger.info(f'Result added to CSV: {row[-1]}')  # 记录日志
        except Exception as e:
            logger.error(f'Issue occurred! {type(e).__name__}: {e}')
            # 输出堆栈跟踪信息到日志文件
            logger.info(traceback.format_exc())
        finally:
            # 将 self.rows_processed 的数据追加到 data/processed.txt 文件中，
            with open(self.processed_file_name, 'a') as processed_file:
                for row in self.rows_processed:
                    # 把每行以JSON形式保存
                    processed_file.write(json.dumps(row) + '\n')

        logger.info(f'total {len(self.rows_processed)} simulations completed!')

        return [sim for sim in data if sim not in self.rows_processed]

    @staticmethod
    def load_data(processed_file_name, factor_file_name=None):
        """
        从 processed.txt 中读取已处理的数据，并从 parameters.py 中的 FORMULAS 变量加载数据，排除已处理的数据。

        :param processed_file_name: 已处理数据的文件名（processed.txt）
        :param factor_file_name: 因子库的文件名（factor_library.csv），不再使用
        :return: 未处理的数据列表
        """
        # 从 processed.txt 中读取已处理的数据
        processed = []
        processed_codes = set()
        try:
            with open(processed_file_name, 'r') as processed_file:
                lines = processed_file.readlines()[1:]  # 忽略第一行
                for line in lines:
                    stripped_line = line.strip()
                    if not stripped_line.startswith('#'):  # 忽略以 # 开头的行
                        try:
                            simulation = json.loads(stripped_line)
                        except Exception as e:
                            simulation = {'regular': stripped_line}
                        if simulation not in processed:
                            processed.append(simulation)
            processed_codes = {item['regular'] for item in processed}
        except FileNotFoundError:
            pass

        # 从 parameters.py 中加载 FORMULAS 变量
        from parameters import FORMULAS

        # 遍历 FORMULAS 数组，处理数据
        data = []
        for item in FORMULAS:
            if isinstance(item, str):  # 如果是字符串
                if item not in processed_codes:  # 如果未处理过
                    logger.info(f'Adding {item} to data.')
                    data.append({'regular': item})
            elif isinstance(item, dict):  # 如果是字典
                if item not in processed:  # 如果未处理过
                    data.append(item)
            # 其他情况忽略

        return data


def main():
    processed_file_name = os.path.join('data', 'processed.txt')
    factor_file_name = os.path.join('data', 'factor_library.csv')
    # proxies = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
    proxies = None

    data = WQSession.load_data(processed_file_name, factor_file_name)
    total_rows = len(data)
    if data:
        try:
            wq = WQSession(proxies=proxies)
            logger.info('start alpha simulations')
            processed_data = wq.simulate(data)
            if processed_data:
                logger.info(f'{total_rows - len(processed_data)}/{total_rows} alpha simulations completed.')
            else:
                logger.info(f'All {total_rows} alpha simulations completed.')
        except Exception as e:
            logger.error(f'An error occurred: {e}')
    else:
        logger.info('No new alpha simulations to process.')


if __name__ == '__main__':
    main()
