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
# from parameters import DATA
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json', **kwargs):
        super().__init__()
        self.lock = threading.Lock()
        self.max_workers = kwargs.get('max_workers', 2)
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')
        self.json_fn = json_fn
        self.processed_file_name = kwargs.get('processed_file_name', 'processed.txt')
        self.auth_url = 'https://api.worldquantbrain.com/authentication'
        self.simulate_url = 'https://api.worldquantbrain.com/simulations'
        self.status_base_url = 'https://api.worldquantbrain.com/alphas/'
        self.proxies = kwargs.get('proxies')
        old_get, old_post = self.get, self.post

        def new_get(*args, **kwargs):
            try:
                kwargs['proxies'] = self.proxies
                return old_get(*args, **kwargs)
            except:
                return new_get(*args, **kwargs)

        def new_post(*args, **kwargs):
            try:
                kwargs['proxies'] = self.proxies
                return old_post(*args, **kwargs)
            except:
                return new_post(*args, **kwargs)

        self.get, self.post = new_get, new_post
        self.login_expired = False
        self.rows_processed = []

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
                    print(f'WARNING! {r.json()}')
                    input('Press enter to quit...')
            logging.info('Logged into WQBrain!')
        except Exception as e:
            logging.error(f'login into WQBrain:{e}')
            raise

    def process_simulation(self, simulation):
        with self.lock:
            if self.login_expired:
                logging.info(f'Login expired, re-logging in...')
                try:
                    self.login()
                except Exception as e:
                    logging.error(f're-login into WQBrain:{e}')
                    raise

        thread = current_thread().name
        alpha = simulation['code'].strip()
        delay = simulation.get('delay', 1)
        universe = simulation.get('universe', 'TOP3000')
        truncation = simulation.get('truncation', 0.02)
        region = simulation.get('region', 'USA')
        decay = simulation.get('decay', 8)
        neutralization = simulation.get('neutralization', 'SUBINDUSTRY').upper()
        pasteurization = simulation.get('pasteurization', 'ON')
        nan = simulation.get('nanHandling', 'OFF')
        logging.info(f"{thread} -- Simulating alpha: {alpha}")
        while True:
            # keep sending a post request until the simulation link is found
            try:
                payload = {
                    'regular': alpha,
                    'type': 'REGULAR',
                    'settings': {
                        "nanHandling": nan,
                        "instrumentType": "EQUITY",
                        "delay": delay,
                        "universe": universe,
                        "truncation": truncation,
                        "unitHandling": "VERIFY",
                        "pasteurization": pasteurization,
                        "region": region,
                        "language": "FASTEXPR",
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
                    logging.info(f'{thread} -- {r.content}')  # usually gateway timeout
                    return
        logging.info(f'{thread} -- Obtained simulation link: {nxt}')
        ok = True
        alpha_link = None
        while True:
            r = self.get(nxt).json()
            if 'alpha' in r:
                alpha_link = r['alpha']
                break

            try:
                logging.info(f"{thread} -- 【{alpha}】 ({int(100 * r['progress'])}%)")
            except Exception as e:
                ok = (False, r['message'])
                break

            time.sleep(10)

        weight_check = None
        subsharpe = None

        if ok is not True:
            logging.info(f'{thread} -- Issue when sending simulation request [{alpha}]: {ok[1]}')
            row = [
                0, delay, region,
                neutralization, decay, truncation,
                0, 0, 0, 'FAIL', 0, -1, universe, nxt, alpha
            ]
        else:
            r = self.get(f'{self.status_base_url}{alpha_link}').json()
            logging.info(
                f'{thread} -- Obtained alpha link: https://platform.worldquantbrain.com/alpha/{alpha_link}')
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
                f'https://platform.worldquantbrain.com/alpha/{alpha_link}',
                alpha
            ]

        return row

    def simulate(self, data, **kwargs):
        self.rows_processed = []

        if not os.path.exists('data'):
            os.makedirs('data')
        csv_file = os.path.join("data", "api_results.csv")

        self.login()

        # 主函数处理部分
        try:
            # for handler in logging.root.handlers:
            #     logging.root.removeHandler(handler)


            # 固定CSV文件名
            file_exists = os.path.isfile(csv_file)

            with open(csv_file, 'a', newline='') as f:
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
                            logging.info(f'Result added to CSV: {row[-1]}')  # 记录日志
        except Exception as e:
            print(f'Issue occurred! {type(e).__name__}: {e}')
        finally:
            # 将 self.rows_processed 的数据追加到 data/processed.txt 文件中
            with open(self.processed_file_name, 'a') as processed_file:
                for row in self.rows_processed:
                    processed_file.write(f"{row['code']}\n")

        logging.info(f'total {len(self.rows_processed)} simulations completed!')

        return [sim for sim in data if sim not in self.rows_processed]


def main():
    processed_file_name = 'processed.txt'
    factor_file_name = 'factor_library.csv'
    proxies = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
    # proxies = None

    log_file = os.path.join('data', f"api_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")
    logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s',
                        filename=log_file)

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

    total_rows = len(data)
    if data:
        wq = WQSession(proxies=proxies)
        logging.info('start alpha simulations')
        processed_data = wq.simulate(data)
        if processed_data:
            logging.info(f'{total_rows - len(processed_data)}/{total_rows} alpha simulations completed.')
        else:
            logging.info(f'All {total_rows} alpha simulations completed.')


if __name__ == '__main__':
    main()
