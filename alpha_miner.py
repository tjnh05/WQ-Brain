import json

import requests
from itertools import product

from requests.auth import HTTPBasicAuth


class AlphaMiner:
    def __init__(self, credentials_path, verify=True):
        self.sess = requests.Session()
        self.setup_auth(credentials_path)
        self.auth_url = 'https://api.worldquantbrain.com/authentication'  # 将认证的URL作为成员变量
        self.simulation_url = 'https://api.worldquantbrain.com/simulations'
        self.verify = verify

    def setup_auth(self, credentials_path):
        with open(credentials_path) as f:
            credentials = json.load(f)
        self.sess.auth = HTTPBasicAuth(credentials["username"], credentials["password"])
        response = self.sess.post(self.auth_url, verify=self.verify)
        if response.status_code != 201:
            raise Exception("Authentication failed")

    def test_alpha(self, expression):
        simulation_data = {
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": 0,
                "neutralization": "INDUSTRY",
                "truncation": 0.08,
                "pasteurization": "ON",
                "language": "FASTEXPR"
            },
            "regular": expression
        }
        response = self.sess.post(url=self.simulation_url,
                                  json=simulation_data,
                                  verify=self.verify)
        if response.status_code != 201:
            return None
        return response.json()

    @classmethod
    def generate_parameter_combinations(cls, max_values, steps=None, starts=None):
        """
        max_values: 每个参数的最大值列表（如 [5,3]）
        steps: 步长列表（可选，默认全1）
        starts: 起始值列表（可选，默认全1）
        """
        # 参数校验
        n = len(max_values)
        steps = steps if steps is not None else [1] * n
        starts = starts if starts is not None else [1] * n

        if len(steps) != n or len(starts) != n:
            raise ValueError("max_values/steps/starts 长度必须一致")

        # 生成参数范围
        ranges = []
        for start, max_val, step in zip(starts, max_values, steps):
            current = start
            values = []
            while current <= max_val:
                values.append(current)
                current += step
            ranges.append(values)

        return list(product(*ranges))

    def run(self, base_expression, params, max_values):
        combinations = self.generate_parameter_combinations(params, max_values)
        for combination in combinations:
            new_expression = base_expression.format(*combination)
            result = self.test_alpha(new_expression)
            if result:
                print(f"Expression: {new_expression}, Result: {result}")


def main():
    miner = AlphaMiner("credentials.json")
    # base_expression = "close_{} / open_{}"
    base_expression = "(Sales_Current - Sales_Past) / Sales_Past * 100"
    params = [1, 2]
    max_values = [5, 5]
    miner.run(base_expression, params, max_values)


# 示例用法
if __name__ == "__main__":
    main()
