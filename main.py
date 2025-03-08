#! /usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import logging
import os
import threading
from datetime import datetime

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
import urllib3

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
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 检查环境变量 WQ_LOG_TO_FILE 是否存在且值为 True
if os.getenv('WQ_LOG_TO_FILE', '').lower() == 'true':
    # 创建日志目录
    log_dir = os.path.join('log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建文件处理器
    log_file = os.path.join(log_dir, f"api_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


class WQSession(requests.Session):
    def __init__(self, **kwargs):
        super().__init__()
        self.lock = threading.Lock()
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

        # 结果文件
        if not os.path.exists('data'):
            os.makedirs('data')
        self.csv_file = os.path.join("data", "api_results.csv")

        # 如果环境变量中未设置 email 或 password，则从 json_fn 文件中读取
        if not self.email or not self.password:
            try:
                with open(self.json_fn, 'r') as f:
                    creds = json.loads(f.read())
                    self.email = creds['email']
                    self.password = creds['password']
            except Exception as e:
                raise ValueError(f"Failed to read email and password from {self.json_fn}: {e}")

        # 检查 email 和 password 是否都有值
        if not self.email or not self.password:
            raise ValueError("Email and password must be provided via environment variables or credentials file.")

        self.auth = (self.email, self.password)

    def login(self):
        with open(self.json_fn, 'r') as f:
            creds = json.loads(f.read())
            email, password = creds['email'], creds['password']
            self.auth = (email, password)

        try:
            r = self.post(self.auth_url, proxies=self.proxies, verify=False)
            if 'user' not in r.json():
                if 'inquiry' in r.json():
                    input(
                        f"Please complete biometric authentication at {r.url}/persona?inquiry={r.json()['inquiry']} before continuing...")
                    self.post(f"{r.url}/persona", json=r.json())
                else:
                    message = r.json()['detail']
                    logging.warning(f'WARNING! {message}')
                    raise Exception(f'failed! {message}')
            logger.info('Logged into WQBrain!')
            self.login_expired = False
        except Exception as e:
            logger.error(f'login into WQBrain:{e}')
            raise

    def process_simulation(self, simulation):
        with self.lock:
            if self.login_expired:
                logger.info(f'Login expired, re-logging in...')
                try:
                    self.login()
                except Exception as e:
                    logger.error(f're-login into WQBrain:{e}')
                    raise

        thread = current_thread().name
        alpha = simulation['code'].strip()
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
        while True:
            # keep sending a post request until the simulation link is found
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
                r = self.post(self.simulate_url, json=payload)
                nxt = r.headers['Location']
                break
            except Exception as e:
                try:
                    if 'credentials' in r.json()['detail']:
                        self.login_expired = True
                        return
                except Exception as e:
                    logger.info(f'{thread} -- {r.content}')  # usually gateway timeout
                    return
        logger.info(f'{thread} -- Obtained simulation link: {nxt}')
        ok = True
        alpha_link = None
        while True:
            r = self.get(nxt).json()
            if 'alpha' in r:
                alpha_link = r['alpha']
                break

            try:
                logger.info(f"{thread} -- 【{alpha}】 - {int(100 * r['progress'])}%")
            except Exception as e:
                ok = (False, r['message'])
                break

            time.sleep(10)

        weight_check = None
        subsharpe = None

        if ok is not True:
            logger.info(f'{thread} -- Issue when sending simulation request [{alpha}]: {ok[1]}')
            row = [
                0, delay, region,
                neutralization, decay, truncation,
                0, 0, 0, 'FAIL', 0, -1, universe, nxt, alpha
            ]
        else:
            r = self.get(f'{self.status_base_url}{alpha_link}').json()
            logger.info(
                f'{thread} -- Obtained alpha link: {self.alpha_base_url}{alpha_link}')
            passed = 0
            for check in r['is']['checks']:
                passed += check['result'] == 'PASS'
                if check['name'] == 'CONCENTRATED_WEIGHT':
                    weight_check = check['result']
                if check['name'] == 'LOW_SUB_UNIVERSE_SHARPE':
                    subsharpe = check.get('value', -1)

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
                        'subsharpe', 'correlation', 'universe', 'link', 'code'
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
            print(f'Issue occurred! {type(e).__name__}: {e}')
        finally:
            # 将 self.rows_processed 的数据追加到 data/processed.txt 文件中
            with open(self.processed_file_name, 'a') as processed_file:
                for row in self.rows_processed:
                    processed_file.write(f"{row['code']}\n")

        logger.info(f'total {len(self.rows_processed)} simulations completed!')

        return [sim for sim in data if sim not in self.rows_processed]

    @staticmethod
    def load_data(processed_file_name, factor_file_name):
        """
        从 processed.txt 中读取已处理的数据，并从 factor_library.csv 中读取数据，排除已处理的数据。

        :param processed_file_name: 已处理数据的文件名（processed.txt）
        :param factor_file_name: 因子库的文件名（factor_library.csv）
        :return: 未处理的数据列表
        """
        # 从 processed.txt 中读取已处理的数据
        processed = set()
        try:
            with open(processed_file_name, 'r') as processed_file:
                processed = set(line.strip() for line in processed_file)
        except FileNotFoundError:
            pass

        # 从 factor_library.csv 中读取数据，并排除已处理的数据
        with open(factor_file_name, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过第一行
            data = [{'code': row[0]} for row in reader if row[0] not in processed]  # 将第一列作为code，并排除已处理的数据

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
