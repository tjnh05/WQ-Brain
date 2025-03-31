import requests
import json
from os.path import expanduser
from requests.auth import HTTPBasicAuth

# 加载凭据文件
with open(expanduser('brain.txt')) as f:
    credentials = json.load(f)

# 从列表中提取用户名和密码
username, password = credentials

# 创建会话对象
sess = requests.Session()

# 设置基本身份验证
sess.auth = HTTPBasicAuth(username, password)

# 向API发送POST请求进行身份验证
response = sess.post('https://api.worldquantbrain.com/authentication')

# 打印响应状态和内容以调试
print(response.status_code)
print(response.json())


# 获取数据集ID为fundamental6（Company Fundamental Data for Equity）下的所有数据字段
### Get Data_fields like Data Explorer 获取所有满足条件的数据字段及其ID
def get_datafields(
        s,
        searchScope,
        dataset_id: str = '',
        search: str = ''
):
    import pandas as pd
    instrument_type = searchScope['instrumentType']
    region = searchScope['region']
    delay = searchScope['delay']
    universe = searchScope['universe']

    if len(search) == 0:
        url_template = "https://api.worldquantbrain.com/data-fields?" + \
                       f"&instrumentType={instrument_type}" + \
                       f"&region={region}&delay={str(delay)}&universe={universe}&dataset.id={dataset_id}&limit=50" + \
                       "&offset={x}"
        count = s.get(url_template.format(x=0)).json()['count']
    else:
        url_template = "https://api.worldquantbrain.com/data-fields?" + \
                       f"&instrumentType={instrument_type}" + \
                       f"&region={region}&delay={str(delay)}&universe={universe}&limit=50" + \
                       f"&search={search}" + \
                       "&offset={x}"
        count = 100

    datafields_list = []
    for x in range(0, count, 50):
        datafields = s.get(url_template.format(x=x))
        datafields_list.append(datafields.json()['results'])

    datafields_list_flat = [item for sublist in datafields_list for item in sublist]

    datafields_df = pd.DataFrame(datafields_list_flat)
    return datafields_df

# 爬取id
searchScope = {'region': 'USA', 'delay': '1', 'universe': 'TOP3000', 'instrumentType': 'EQUITY'}
fundamental6 = get_datafields(s=sess, searchScope=searchScope, dataset_id='fundamental6') # id设置

# 筛选（这里是type的MATRIX）
fundamental6 = fundamental6[fundamental6['type'] == "MATRIX"]
fundamental6.head()

datafields_list_fundamental6 = fundamental6['id'].values
print(datafields_list_fundamental6)
print(len(datafields_list_fundamental6))


# 将datafield替换到Alpha模板(框架)中group_rank({fundamental model data}/cap,subindustry)批量生成Alpha
alpha_list = []

for index,datafield in enumerate(datafields_list_fundamental6,start=1):
    print(f"正在循环第 {index} 个元素")
    print("正在将如下alpha表达式与setting封装")
    alpha_expression = f'group_rank(({datafield})/cap, subindustry)'
    print(alpha_expression)
    simulation_data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": alpha_expression
    }
    alpha_list.append(simulation_data)
    print(f"there are {len(alpha_list)} Alphas to simulate")

print(alpha_list[1])


# 将Alpha一个一个发送至服务器进行回测（已经测试前两个了）
from time import sleep

for index,alpha in enumerate(alpha_list,start=1):
    sim_resp = sess.post(
        'https://api.worldquantbrain.com/simulations',
        json=alpha,
    )

    try:
        sim_progress_url = sim_resp.headers['Location']
        while True:
            sim_progress_resp = sess.get(sim_progress_url)
            retry_after_sec = float(sim_progress_resp.headers.get("Retry-After", 0))
            if retry_after_sec == 0:  # simulation done!模拟完成!
                break
            sleep(retry_after_sec)
        alpha_id = sim_progress_resp.json()["alpha"]  # the final simulation result.# 最终模拟结果
        print(alpha_id)
    except:
        print("no location, sleep for 10 seconds and try next alpha.“没有位置，睡10秒然后尝试下一个字母。”")
        sleep(10)

##################测试前两个##############################
from time import sleep

for index,alpha in enumerate(alpha_list[0:2],start=1):
    sim_resp = sess.post(
        'https://api.worldquantbrain.com/simulations',
        json=alpha,
    )

    try:
        sim_progress_url = sim_resp.headers['Location']
        while True:
            sim_progress_resp = sess.get(sim_progress_url)
            retry_after_sec = float(sim_progress_resp.headers.get("Retry-After", 0))
            if retry_after_sec == 0:  # simulation done!模拟完成!
                break
            sleep(retry_after_sec)
        alpha_id = sim_progress_resp.json()["alpha"]  # the final simulation result.# 最终模拟结果
        print(alpha_id)
    except:
        print("no location, sleep for 10 seconds and try next alpha.“没有位置，睡10秒然后尝试下一个字母。”")
        sleep(10)

#################################################
