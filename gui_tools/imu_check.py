import datetime
import json
import os
import re
import subprocess
import time
import requests
from numpy import mean
from queue import Queue



Swift_files = f'../datas/Swift-logs/swift-connect'
imu_filequeue = Queue()

error_reason = []


error_cn = ['', '最大丢包率过大', 'interval过大', 'imu包数不足', '丢包率过大', 'cost过大', ]

#loss_rate_max,interval_max,imu_len,imu_loss,const_max


def imu_ana(file):
    trackerA_data = []
    trackerB_data = []
    trackerC_data = []


    swift_data = open(file, 'r').readlines()

    for i in swift_data[1:-1]:

        if len(i.strip().split(',')) == 22:
            try:
                trackerid = i.strip().split(',')[0]
                index = eval(i.strip().split(',')[1])
                interval = eval(i.strip().split(',')[6])
                cost = eval(i.strip().split(',')[7])
                latency = eval(i.strip().split(',')[8])
                loss_rate = float(i.strip().split(',')[9][:-1])

                # 0-trackerid;1-index;2-timestamp;4-processtime;5-servicelatency;6-interval;7-cost;8-latency;9-loss_rate;
                if not trackerA_data:
                    trackerA_data.append([trackerid, index, loss_rate, interval, cost, latency])
                else:
                    if trackerA_data[0][0] == trackerid:
                        trackerA_data.append([trackerid, index, loss_rate, interval, cost, latency])
                    else:
                        if not trackerB_data:
                            trackerB_data.append([trackerid, index, loss_rate, interval, cost, latency])
                        else:
                            if trackerB_data[0][0] == trackerid:
                                trackerB_data.append([trackerid, index, loss_rate, interval, cost, latency])
                            else:
                                if not trackerC_data:

                                    trackerC_data.append([trackerid, index, loss_rate, interval, cost, latency])
                                else:
                                    if trackerC_data[0][0] == trackerid:
                                        trackerC_data.append([trackerid, index, loss_rate, interval, cost, latency])
                                    else:
                                        error_reason.append('0')

                                        # id异常
            except:

                error_reason.append('1')
                # 原始数据异常：单数据格式异常
                continue
        else:

            error_reason.append('2')
            # 原始数据异常：数据量异常

    if not trackerB_data:
        if not trackerA_data:
            error_reason.append('3-0')
            # 原始数据异常：id异常（连接上报数<2）
            return ['', 0]

        else:
            error_reason.append('3-1')
            # 原始数据异常：id异常（连接上报数<2）
            return ['', 1]



    else:
        if trackerC_data:
            trackerA_cost = tk_cost_check(trackerA_data)
            trackerB_cost = tk_cost_check(trackerB_data)
            trackerC_cost = tk_cost_check(trackerC_data)
            trackerA_loss_rate_max = loss_rate_max_check(trackerA_data)
            trackerB_loss_rate_max = loss_rate_max_check(trackerB_data)
            trackerC_loss_rate_max = loss_rate_max_check(trackerC_data)
            trackerA_loss_amount = tk_loss_amount_check(trackerA_data)
            trackerB_loss_amount = tk_loss_amount_check(trackerB_data)
            trackerC_loss_amount = tk_loss_amount_check(trackerC_data)
            trackerA_interval = tk_interval_check(trackerA_data)
            trackerB_interval = tk_interval_check(trackerB_data)
            trackerC_interval = tk_interval_check(trackerC_data)

            xls_datas = [[trackerA_loss_rate_max[0], trackerA_loss_rate_max[1], trackerA_interval[1],
                         trackerA_loss_amount[3], trackerA_loss_amount[4], trackerA_cost[1], trackerA_loss_amount[0]],
                         [trackerB_loss_rate_max[0], trackerB_loss_rate_max[1], trackerB_interval[1],
                          trackerB_loss_amount[3], trackerB_loss_amount[4], trackerB_cost[1], trackerB_loss_amount[0]],
                         [trackerC_loss_rate_max[0], trackerC_loss_rate_max[1], trackerC_interval[1],
                          trackerC_loss_amount[3], trackerC_loss_amount[4], trackerC_cost[1], trackerC_loss_amount[0]]]
            return [xls_datas, 3]

        else:
            trackerA_cost = tk_cost_check(trackerA_data)
            trackerB_cost = tk_cost_check(trackerB_data)
            trackerA_loss_rate_max = loss_rate_max_check(trackerA_data)
            trackerB_loss_rate_max = loss_rate_max_check(trackerB_data)
            trackerA_loss_amount = tk_loss_amount_check(trackerA_data)
            trackerB_loss_amount = tk_loss_amount_check(trackerB_data)
            trackerA_interval = tk_interval_check(trackerA_data)
            trackerB_interval = tk_interval_check(trackerB_data)
            xls_datas = [[trackerA_loss_rate_max[0], trackerA_loss_rate_max[1], trackerA_interval[1],
                          trackerA_loss_amount[3], trackerA_loss_amount[4], trackerA_cost[1], trackerA_loss_amount[0]],
                         [trackerB_loss_rate_max[0], trackerB_loss_rate_max[1], trackerB_interval[1],
                          trackerB_loss_amount[3], trackerB_loss_amount[4], trackerB_cost[1], trackerB_loss_amount[0]],
                         ['', '', '', '', '', '']]


            # [trackerid, loss_rate_max, interval_max, imu_len, imu_loss, const_max]

            return [xls_datas, 2]

def tk_cost_check(tracker_datas):
    tracker_cost = []
    [tracker_cost.append(int(i[4])) for i in tracker_datas]
    cost_average = int(mean(tracker_cost))
    cost_max = max(tracker_cost)
    return [cost_average, cost_max]

def loss_rate_max_check(tracker_data):
    trackerID = tracker_data[0][0]
    loss_rate_list = extract(tracker_data, 2, 0)
    loss_rate_list = [i for i in loss_rate_list]

    return [trackerID, max(loss_rate_list)]

def tk_loss_amount_check(tracker_datas):
    interval_len = len(tracker_datas) - 1
    index_list = [[tracker_datas[i + 1][1] - tracker_datas[i][1] - 1, tracker_datas[i + 1][3]] if
        tracker_datas[i + 1][1] > tracker_datas[i][1] else [
        tracker_datas[i + 1][1] + 256 - tracker_datas[i][1] - 1, tracker_datas[i + 1][3]] for i in
                  range(len(tracker_datas) - 1)]
    index_c_list = extract(index_list, 0, 1)
    loss_rate_c = float("%.2f" % (sum(index_c_list) / (sum(index_c_list) + interval_len) * 100))
    loss_amount = [0, 0, 0, 0, 0, 0]
    loss_sss = [0, 0, 0, 0, 0, 0]
    for i in index_list:
        if i[0] < 1:
            loss_amount[0] += 1
        elif 1 <= i[0] < 4:
            loss_amount[1] += 1
        elif 4 <= i[0] < 6:
            loss_amount[2] += 1
        elif 6 <= i[0] <= 10:
            loss_amount[3] += 1
        elif i[0] > 10:
            loss_amount[4] += 1
    for d, g in enumerate(loss_amount):
        loss_sss[d] = "%.2f%%" % (int(g) / sum(loss_amount) * 100)

    interval_scopelist = []
    interval_averlist = []

    for i in index_list:
        interval_scopelist.append(round(abs(i[1]) / (i[0] + 1)))
        interval_averlist.append(i)
    interval_n = extract(interval_averlist, 0, 1)
    interval_s = extract(interval_averlist, 1, 1)
    interval_average = round(sum(interval_s) / (sum(interval_n) + len(interval_n)))

    interval_amount = [0, 0, 0, 0, 0]
    interval_amount_z = []

    for i in interval_scopelist:
        if abs(i - interval_average) <= 10:
            interval_amount[0] += 1
        elif 10 < abs(i - interval_average) <= 20:

            interval_amount[1] += 1
        elif 20 < abs(i - interval_average) <= 30:
            interval_amount[2] += 1
        elif 30 < abs(i - interval_average) <= 50:
            interval_amount[3] += 1
        else:
            interval_amount[4] += 1

        interval_amount_z.append(abs(i - interval_average))

    # interval_amount偏移范围次数[0~10,10~20,21~30,31~50,50以上]
    # loss_amount丢包次数列表[不丢包，丢1包，丢2包，丢3包，丢4包，丢4包以上]
    # interval_n有效数据丢包次数列表
    # interval_s有效数据inteval列表
    # interval_average有效数据内interval数据偏移平均值
    return [interval_amount[4], interval_average, loss_amount, interval_len, loss_rate_c, loss_sss]

def extract(lst, num, a):
    if a == 1:
        return [int(item[num]) for item in lst]
    if a == 0:
        return [item[num] for item in lst]


def tk_interval_check(tracker_datas):
    tracker_interval = []

    [tracker_interval.append(int(i[3])) for i in tracker_datas]
    for i in tracker_interval:
        if i < 0:
            error_reason.append('4-1')
            '''interval 负值'''
        elif i == 0:
            error_reason.append('4-0')
            '''interval 0'''


    interval_average = round(mean(tracker_interval))
    interval_max = max(tracker_interval)
    return [interval_average, interval_max]



def requesting(s, method, url, header, datatype, data):
    # requests封装基础调用方法
    try:
        if datatype == 'data':
            r = s.request(method=method, url=url, headers=header, data=data, timeout=3)
            dicts = json.loads(r.text)
        else:
            r = s.request(method=method, url=url, headers=header, json=data, timeout=3)
            dicts = json.loads(r.text)
        return dicts
    except Exception as msg:
        return r.text


def req(method, url, header, datatype, data):
    # 加入session
    s = requests.session()
    result = requesting(s, method, url, header, datatype, data)
    return result


def send_msg_swift(sendtype, sendinfo, url, open_id):
    if url:
        sendurl = {
                    "tag": "a",
                    "text": "\n点击下载log   ",
                    "href": url
                 }
    else:
        sendurl = {
                    "tag": "a",
                    "text": "\n",
                    "href": url
                 }
    if open_id:
        atuser = {
                    "tag": "at",
                    "user_id": open_id
                 }
    else:
        atuser = {
                    "tag": "text",
                    "text": ''
                 }
    data = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f'{sendtype}通知：',
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": sendinfo
                            },
                            sendurl,
                            atuser
                        ]
                    ]
                }
            }
        }
    }
    header = {"Content-Type": "application/json"}
    token = 'd1f826af-481f-4cd1-ad17-6b1f8cbce616'
    result = req('post', f'https://open.feishu.cn/open-apis/bot/v2/hook/{token}', header, 'json', data)
    if result != 'reqerror':
        return result
    else:
        return '飞书机器人接口请求失败！'

def pull_logs(devicesn, file_address):

    subprocess.Popen(f'adb -s {devicesn} pull /data/logs {file_address}')



def contrast(devicesn, data, lens, connect_logs, imu_check_config, y):
    if y:
        standard = open(imu_check_config).readlines()[0].strip().split(',')
    else:
        standard = imu_check_config
    contrast_flag = 1
    if lens == 2:
        if data[1] == 2:
            for id in data[0][:-1]:

                for index, da in enumerate(id[1:]):

                    if index + 1 == 3:
                        if da > int(standard[index + 1]):
                            pass
                        else:
                            contrast_flag = 0
                            error_reason.append(f'-{index + 1}')
                    elif index + 1 == 6:
                        if da:
                            contrast_flag = 0
                            error_reason.append(f'-{index + 1}')
                        else:
                            pass
                    else:
                        if da < int(standard[index + 1]):
                            pass
                        else:
                            contrast_flag = 0
                            error_reason.append(f'-{index + 1}')
        else:
            contrast_flag = 0
    else:
        if data[1] == 3:
            for id in data[0]:
                for index, da in enumerate(id[1:]):
                    if index+1 == 3:
                        if da > int(standard[index+1]):
                            pass
                        else:
                            contrast_flag = 0
                            error_reason.append(f'-{index+1}')
                    elif index + 1 == 6:
                        if da:
                            pass
                        else:
                            contrast_flag = 0
                            error_reason.append(f'-{index + 1}')
                    else:
                        if da < int(standard[index+1]):
                            pass
                        else:
                            contrast_flag = 0
                            error_reason.append(f'-{index+1}')
        elif data[1] == 2:
            contrast_flag = 0
            error_reason.append(f'3-2')
        else:
            contrast_flag = 0
    if contrast_flag:
        if y:
            run_log(connect_logs, f'check结果--PASS：{data}', devicesn)
        else:
            pass
        if error_reason:
            return [False, data]
        else:
            return [True, data]
    else:
        if y:
            run_log(connect_logs, f'check结果--FAIL：{data}', devicesn)
        else:
            pass

        return [False, data]

def run_log(logfilename, run_msg, devicesn):

    #writetime = os.popen(f'adb -s {devicesn} shell date').read().strip('\n').split(' ')[-3]
    writetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logfile = open(logfilename, 'a')
    logfile.write(f'--{writetime}--{run_msg}\n')
    logfile.close()


def imu_check_return(devicesn, swiftimu_file):
    # 单次执行15s imu数据检查
    # 调用传入设备SN,文件可存放路径
    # 方法返回 [检查结果:True/False , 解析数据, 异常原因(正常则返回None)]
    # 对比指标值根据需要变更['', 每秒最大丢包率, interval最大值, 实际包数, 总丢包率, const最大值]
    tklist = []
    imu_check_config = ['', '30', '250000', '2600', '10', '32000']

    for i in os.popen(f'adb -s {devicesn} shell tracker_test getworkmode').readlines():
        if re.findall('ret = 0', i) and not re.findall('radio_interval = 255', i):
            tklist.append(i.strip().split(',')[1].strip())
    if len(tklist) >= 2:
        error_reason.clear()
        filetime = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        os.popen(f'adb -s {devicesn} shell pvrtracking_swift_test imu-statistics 15 1 {filetime}')
        time.sleep(16)
        os.popen(f'adb -s {devicesn} pull /sdcard/pvrtracking/{filetime}_swift-imu-statistics.csv {swiftimu_file}')
        time.sleep(2)
        imu_loss_data = contrast(devicesn, imu_ana(f'{swiftimu_file}//{filetime}_swift-imu-statistics.csv'), len(tklist), '', imu_check_config, 0)
        if imu_loss_data[0]:

            return [True, imu_loss_data[1], None]
        else:
            return [False, imu_loss_data[1], error_reason]




# [trackerid, loss_rate_max, interval_max, imu_len, imu_loss, const_max]