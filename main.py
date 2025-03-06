import csv
import logging
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

        self.login()
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
            logging.info('Logged in to WQBrain!')
        except Exception as e:
            logging.info(f'failed to login to WQBrain:{e}')
            raise

    def simulate(self, data, **kwargs):
        self.rows_processed = []

        def process_simulation(writer, f, simulation):
            if self.login_expired:
                return  # expired credentials

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
                    logging.info(f"{thread} -- 【{alpha_link}】 ({int(100 * r['progress'])}%)")
                except Exception as e:
                    ok = (False, r['message'])
                    break

                time.sleep(10)

            row = []
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
                        subsharpe = check['value']

                self.rows_processed.append(simulation)

                try:
                    subsharpe
                except Exception as e:
                    subsharpe = -1

                row = [
                    passed, delay, region,
                    neutralization, decay, truncation,
                    r['is']['sharpe'],
                    r['is']['fitness'],
                    round(100 * r['is']['turnover'], 2),
                    weight_check, subsharpe, -1,
                    universe, f'https://platform.worldquantbrain.com/alpha/{alpha_link}', alpha
                ]

            writer.writerow(row)
            f.flush()
            logging.info(f'{thread} -- Result added to CSV!')

        try:
            for handler in logging.root.handlers:
                logging.root.removeHandler(handler)

            csv_file = f"data/api_{str(time.time()).replace('.', '_')}.csv"
            logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s',
                                filename=csv_file.replace('csv', 'log'))
            logging.info(f'Creating CSV file: {csv_file}')

            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                header = [
                    'passed', 'delay', 'region', 'neutralization', 'decay', 'truncation',
                    'sharpe', 'fitness', 'turnover', 'weight',
                    'subsharpe', 'correlation', 'universe', 'link', 'code'
                ]
                writer.writerow(header)
                with ThreadPoolExecutor(
                        max_workers=self.max_workers) as executor:  # 10 threads, only 3 can go in concurrently so this is no harm
                    _ = executor.map(lambda sim: process_simulation(writer, f, sim), data)
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
    # proxies = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
    proxies = None

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
        print(f'start alpha simulations...')
        processed_data = wq.simulate(data)
        if processed_data:
            print(f'{total_rows - len(processed_data)}/{total_rows} alpha simulations completed.')
        else:
            print(f'All {total_rows} alpha simulations completed.')


if __name__ == '__main__':
    main()
