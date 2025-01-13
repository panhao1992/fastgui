# -*- coding;utf-8 -*-
"""
File name : base_common.PY
Create file time: 2023/1/16 14:59
File Create By Author : Admin
"""
import serial
from serial.tools import list_ports
import os
import re
import datetime
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from ttkbootstrap.toast import ToastNotification
import time
import tkinter.ttk
import xlwt
import csv
from tkinter import *
from tkinter import filedialog, messagebox
import json
import requests
import logging
import inspect
import ctypes
import shutil
from queue import Queue
import time
import re
import numpy as np
from functools import wraps
from device_connection_api import controller_check, device, device_shell, controller, ctrlserial

workhost = 'http://10.68.99.34:9006/'
dataspath = '../datas/'
otiilogin = []
online_devices = []
logmonitorprocess = []
commonitorprocess = []
use_dict = {}
special_tasks = {}

"""基础方法封装"""
Swift_files = f'{dataspath}Swift-logs'
otafile = f'{dataspath}otadir/'



def adb_order(order):
    """基于subprocess的命令请求方法"""
    run = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
    result = run.stdout.read().decode('utf-8')
    return result


def update_chosedevice(chosepart, *args):
    chosepart.set('')
    chosepart['values'] = tuple(online_devices)


# 样式设置
def set_style(name, size, color, borders_size, color_fore, blod=False):
    """excel样式设置封装"""
    style = xlwt.XFStyle()  # 初始化样式
    # 字体
    font = xlwt.Font()
    font.name = name
    font.height = 20 * size  # 字号
    font.bold = blod  # 加粗
    font.colour_index = color  # 默认：0x7FFF 黑色：0x08
    style.font = font
    # 居中
    alignment = xlwt.Alignment()  # 居中
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    style.alignment = alignment
    # 边框
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = borders_size  # 自定义：1：细线；2：中细线；3：虚线；4：点线
    style.borders = borders
    # 背景颜色
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置背景颜色的模式(NO_PATTERN; SOLID_PATTERN)
    pattern.pattern_fore_colour = color_fore  # 默认：无色：0x7FFF；黄色：0x0D；蓝色：0x0C
    style.pattern = pattern

    return style


def requesting(s, method, url, header, datatype, data):
    """requests封装基础调用方法"""
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
    """加入session"""
    s = requests.session()
    result = requesting(s, method, url, header, datatype, data)
    return result


def send_msg(sendtype, sendinfo, url, open_id, robot):
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
    if robot == 'qa':
        token = '3736ce15-2d45-44eb-89a6-af635a309896'
    elif robot == 'all':
        token = '48e4eeb3-8dd2-42ac-bdb0-4986083f4528'
    else:
        token = '9dab1cd5-7724-486e-b50b-74de8fc171b8'
    result = req('post', f'https://open.feishu.cn/open-apis/bot/v2/hook/{token}', header, 'json', data)
    if result != 'reqerror':
        return result
    else:
        return '飞书机器人接口请求失败！'


def check_user(openid):
    if openid == 'Admin':
        return 'Admin'
    else:
        return 'error'


def show_devices():
    """获取与主机连接设备的设备SN数组"""
    try:
        devices_list = []
        result = adb_order('adb devices')
        devicesinfo = re.sub('List of devices attached', '', result)
        devices = re.findall(".*?\tdevice", devicesinfo)
        if devices:
            for device in devices:
                if device:
                    deviceid = re.sub('\tdevice', '', device)
                    devices_list.append(deviceid)
                else:
                    return []
            return devices_list
        else:
            return []
    except:
        return []


def getverinfo(info_lines, keyword, splitkey):
    """一次性命令返回关键词获取方法"""
    pid = []
    for line in info_lines:
        if line.startswith(keyword):
            pid = list(filter(None, line.split(splitkey)))
        else:
            pass
    return pid


def getrominfo(devicesn):
    """获取设备rom"""
    try:
        if devicesn:
            if devicesn in [device for device in show_devices()]:
                romversion = adb_order(f'adb -s {devicesn} shell getprop ro.pvr.internal.version')
                return romversion.replace('\n', '')
            else:
                return '设备未连接！'
        else:
            return '设备未选择！'
    except Exception as msg:
        return f'{str(msg)}--获取失败'


def get_stationservice_pid(devicesn):
    stationservicepid = subprocess.getoutput(f'adb -s {devicesn} shell pidof stationservice')
    return stationservicepid


def get_stationupdate_flag(devicesn):
    updateflag = subprocess.getoutput(f'adb -s {devicesn} shell "getprop | grep station.upgrade.flag"')
    return updateflag


def getstationversion(devicesn):
    """获取station版本"""
    try:
        stationver = os.popen(f"adb -s {devicesn} shell stationclient_test stationver1").readlines()
        version = getverinfo(stationver, 'station version1:', ':')
        if 'error' in version[1]:
            return 'error'
        else:
            return version[1].replace('\n', '')
    except Exception as msg:
        return f'{str(msg)}--获取失败'


def getcontrollerver(devicesn):
    """获取controller版本"""
    try:
        controller = subprocess.Popen(f'adb -s {devicesn} shell stationclient_test controllerver', shell=True,
                                      stdout=subprocess.PIPE)
        controllerver = controller.stdout.read().decode(errors='ignore').split('\n')
        leftlist = getverinfo(controllerver, 'left', ',')
        if re.findall("left controller .+ online", leftlist[0]):
            left_v = leftlist[2]
        else:
            left_v = "左手柄断连"
        rightlist = getverinfo(controllerver, 'right', ',')
        if re.findall("right controller .+ online", rightlist[0]):
            right_v = rightlist[2]
        else:
            right_v = "右手柄断连"
        return [left_v, right_v]
    except Exception as msg:
        return ['获取失败', '获取失败']


def chosefile():
    """gui的文件选择方法"""
    filepathlist = filedialog.askopenfilenames()
    pathlist = []
    for filepath in filepathlist:
        path = filepath.replace("/", "\\\\")
        pathlist.append(path)
    return pathlist


def chosedir():
    dirpath = filedialog.askdirectory()
    return dirpath


def getdevicefile(devicesn, path='/sdcard/', *args):
    """获取设备sdcard文件列表"""
    if devicesn:
        sdcardfiles = os.popen(f"adb -s {devicesn} shell ls {path}").readlines()
        filelist = []
        for sdcardfile in sdcardfiles:
            if '.bin' in sdcardfile:
                filelist.append(sdcardfile.replace('\n', ''))
        return filelist
    else:
        return []


def adb_push(devicesn, filepath, devicepath='/sdcard'):
    """push方法封装"""
    if devicesn:
        if filepath:
            os.popen(f'adb -s {devicesn} push {filepath} {devicepath}')
            return f'{devicesn}_file:[{filepath}]push——success！'
        else:
            return '请选择本地文件！'
    else:
        return '请先选择设备！'


def check_device(devicesn):
    """检查设备是否在线"""
    if devicesn in device.Device()():
        return devicesn
    else:
        return ''


def waitfor_device(devicesn):
    """等待设备连接方法封装"""
    for i in range(15):
        deviceconnect = check_device(devicesn)
        if deviceconnect:
            return 0
        else:
            time.sleep(2)
            pass
    return 1


def comlist():
    """获取所有串口返回数组"""
    try:
        comlist = []
        prot_list = list(serial.tools.list_ports.comports())
        for prot in prot_list:
            comlist.append(list(prot)[0])
        return comlist
    except Exception:
        pass


def getcontroller(devicesn):
    try:
        controller = subprocess.Popen(f'adb -s {devicesn} shell stationclient_test controllerver', shell=True,
                                      stdout=subprocess.PIPE)
        controllerver = controller.stdout.read().decode(errors='ignore').split('\n')
        leftlist = getverinfo(controllerver, 'left', ',')
        if re.findall("left controller .+ online", leftlist[0]):
            left_v = leftlist
        else:
            left_v = "左手柄断连"
        rightlist = getverinfo(controllerver, 'right', ',')
        if re.findall("right controller .+ online", rightlist[0]):
            right_v = rightlist
        else:
            right_v = "右手柄断连"
        return [left_v, right_v]
    except Exception as msg:
        return ['获取失败', '获取失败']


def close_ctrl_still(devicesn, ctrl, type):
    if ctrl == 0:
        controller = 'left'
    else:
        controller = 'right'
    subprocess.getoutput(f'adb -s {devicesn} shell stationclient_test controllerstill {controller} {type}')


def take_controller_slow(devicesn, ctrl, window=0):
    if ctrl == 0:
        controller = 'left'
    else:
        controller = 'right'
    if window:
        subprocess.run(f'start adb -s {devicesn} shell timeout 2 stationclient_test slow-adv {controller}', shell=True)
    else:
        subprocess.getoutput(f'adb -s {devicesn} shell timeout 2 stationclient_test slow-adv {controller}')


def take_stationreset(devicesn, window=0):
    if window:
        subprocess.run(f'start adb -s {devicesn} shell "stationclient_test stationreset"', shell=True)
    else:
        subprocess.getoutput(f'adb -s {devicesn} shell stationclient_test stationreset')


def take_controller_poweroff(devicesn, ctrl, window=0):
    if ctrl == 0:
        controller = 'left'
    else:
        controller = 'right'
    if window:
        subprocess.run(f'start adb -s {devicesn} shell "stationclient_test controller poweroff {controller}"', shell=True)
    else:
        subprocess.getoutput(f'adb -s {devicesn} shell stationclient_test controller poweroff {controller}')


def select_controller_still(devicesn, ctrl):
    if ctrl == 0:
        controller = 'left'
    else:
        controller = 'right'
    status = subprocess.getoutput(f'adb -s {devicesn} shell stationclient_test controllerstill {controller}')
    if re.findall('mode: still', status):
        return 'still'
    else:
        return 'normal'


def check_stillstatus(devicesn):
    allresult = []
    leftresult = subprocess.Popen(f'adb -s {devicesn} shell timeout 1 stationclient_test getstillstatus left', shell=True,
                                  stdout=subprocess.PIPE, encoding='utf-8')
    leftresults = leftresult.stdout.readlines()
    leftkeyword = re.findall(".静止\n|\d+\n", leftresults[-1])
    if leftkeyword:
        allresult.append(leftkeyword[0].replace('\n', ''))
    else:
        allresult.append(leftresults[-1])
    rightresult = subprocess.Popen(f'adb -s {devicesn} shell timeout 1 stationclient_test getstillstatus right', shell=True,
                                   stdout=subprocess.PIPE, encoding='utf-8')
    rightresults = rightresult.stdout.readlines()
    rightkeyword = re.findall(".静止\n|\d+\n", rightresults[-1])
    if rightkeyword:
        allresult.append(rightkeyword[0].replace('\n', ''))
    else:
        allresult.append(rightresults[-1])
    return allresult


def take_cmd(devicesn, order, window=0):
    """ run 方法 """
    if window:
        subprocess.run(f'start adb -s {devicesn} shell timeout 2 {order}', shell=True)
    else:
        result = subprocess.getoutput(f'adb -s {devicesn} shell {order}')
        return result


def deal_mc(mc_figure):
    um = mc_figure * 1000000
    if um > 1000:
        ma = um / 1000
        return f'{str(round(ma, 2))}mA'
    else:
        return f'{str(round(um, 2))}uA'


def getdevicebat(devicesn):
    try:
        devicebat = subprocess.getoutput(f'adb -s {devicesn} shell dumpsys battery | findstr level')
        if devicebat:
            return "{}%".format(re.findall("\d+", devicebat)[0])
        else:
            return '获取失败'
    except Exception as msg:
        return '获取失败'


def get_swifts(devicesn):
    for i in range(3):
        swifts = subprocess.getoutput(f'adb -s {devicesn} shell dumpsys peripheral_service')
        if re.findall("Connected devices size: 2", swifts):
            return 'online'
        else:
            time.sleep(3)
            pass
    return ''


def get_trackerver(devicesn):
    try:
        trackerinfo = subprocess.getoutput(f'adb -s {devicesn} shell tracker_test tracker', encoding='utf-8')
        allversion = []
        if trackerinfo:
            for tracker in trackerinfo.split('\n'):
                trackerid = re.findall("tracker\d, online", tracker)
                if trackerid:
                    allversion.append('{}: {}'.format(trackerid[0],re.findall("sw:TR\d+,", tracker)[0].replace('sw:', '').replace(',', '')))
            if allversion:
                return allversion
            else:
                return '未连接Swift2'
        else:
            return '无设备连接'
    except Exception as msg:
        return ['获取失败']


def take_device_bluetooth(devicesn, takeid, window=0):
    if window:
        if takeid:
            subprocess.run(f'start adb -s {devicesn} shell "svc bluetooth enable"', shell=True)
        else:
            subprocess.run(f'start adb -s {devicesn} shell "svc bluetooth disable"', shell=True)
    else:
        if takeid:
            subprocess.getoutput(f'adb -s {devicesn} shell svc bluetooth enable')
        else:
            subprocess.getoutput(f'adb -s {devicesn} shell svc bluetooth disable')


def take_device_powerreboot(devicesn, window=0):
    if 'userdebug' in getrominfo(devicesn):
        if window:
            subprocess.getoutput(f'adb -s {devicesn} root')
            subprocess.run(f'start adb -s {devicesn} shell "svc power reboot"', shell=True)
        else:
            subprocess.getoutput(f'adb -s {devicesn} shell svc power reboot')
    else:
        subprocess.getoutput(f'adb -s {devicesn} reboot')


def take_device_reback(devicesn, window=0):
    if window:
        subprocess.run(f'start adb -s {devicesn} shell "am broadcast -a android.intent.action.FACTORY_RESET -p android"', shell=True)
    else:
        subprocess.getoutput(f'adb -s {devicesn} shell am broadcast -a android.intent.action.FACTORY_RESET -p android')


def location_track(devicesn, status=0, window=0):
    """开关定位追踪"""
    if window:
        if status:
            subprocess.run(f"start adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,3'", shell=True)
        else:
            subprocess.run(f"start adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,1'", shell=True)
    else:
        if status:
            os.popen(f"adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,3'")
        else:
            os.popen(f"adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,1'")


def input_android_key(devicesn, keyword):
    os.popen(f"adb -s {devicesn} shell input keyevent {str(keyword)}")


def start_game(devicesn):
    os.popen(f'adb -s {devicesn} shell am start -n com.bytedance.cipher/.MainActivity')


def findlastpid():
    adbpids = os.popen('tasklist |findstr adb').readlines()
    lastpid = re.findall("\d+", adbpids[-1])[0]
    return lastpid


def motor_test(devicesn, times, rale):
    if not waitfor_device(devicesn):
        os.popen(f'adb -s {devicesn} shell "stationclient_test test_motor {str(times)} {str(rale)} &"')
        lastpid = findlastpid()
        os.popen(f'taskkill /f /t /im {str(lastpid)}')
        return '震动已启动！'
    else:
        return '设备未连接，请检查后重试！'


def deal_bt(devicesn, status=0):
    if status:
        os.popen(f'adb -s {devicesn} shell svc bluetooth enable')
    else:
        os.popen(f'adb -s {devicesn} shell svc bluetooth disable')


def take_tracker_broad(devicesn, hz):
    os.popen(
        f'adb -s {devicesn} shell am broadcast -a com.pvr.btperipheral.service.action.AUTO_TEST_SET_FREQUENCY --ei com.pvr.btperipheral.service.extra.AUTO_TEST_FREQUENCY_MODE {str(hz)} -f 0x01000000')


def get_tracker_broad(devicesn, broad):
    swifts = subprocess.getoutput(f'adb -s {devicesn} shell dumpsys peripheral_service')
    if re.findall(f"Imu transmission frequency: {str(broad)}", swifts):
        return 'success'
    else:
        return ''


def take_thread(func, *args, daemon=True):
    threadinfo = threading.Thread(target=func, args=args, daemon=daemon)
    threadinfo.start()


def get_tracker_frequency(devicesn):
    if devicesn == '':
        return 'no device'
    else:
        trackers_status = []
        As = os.popen(f'adb -s {devicesn} shell tracker_test getworkmode').readlines()
        getlist = [f"{As[4].strip().split(',')[2].strip().split('=')[1].strip()},{As[4].strip().split(',')[3].strip().split(':')[1].strip()}",
                   f"{As[5].strip().split(',')[2].strip().split('=')[1].strip()},{As[5].strip().split(',')[3].strip().split(':')[1].strip()}",
                   f"{As[6].strip().split(',')[2].strip().split('=')[1].strip()},{As[6].strip().split(',')[3].strip().split(':')[1].strip()}",
                   ]
        for idx,i in enumerate(getlist):
            if i == "0,7":
                getlist[idx] = '200hz'
            elif i == "3,11":
                getlist[idx] = '12.5hz'
            elif i == "3,9":
                getlist[idx] = '50hz'
            elif i == "3,128":
                getlist[idx] = '0hz'
            elif i == "3,129":
                getlist[idx] = '静止'
            elif i == "255,255":
                getlist[idx] = '未连接'
            else:
                getlist[idx] = '异常'
            trackers_status.append(getlist[idx])
    return trackers_status


def toast_ui(title, msg, duration=0):
    if duration:
        toast_update = ToastNotification(
            title=f"{title}",
            message=msg,
            duration=duration,
            icon='',
            alert=False,
            position=(0, 30, 'ne')
        )
        toast_update.show_toast()
    else:
        toast_update = ToastNotification(
            title=f"{title}(点击消失)",
            message=msg,
            icon='',
            alert=False,
            position=(0, 30, 'ne')
        )
        toast_update.show_toast()

def alone_thread(func):
    @wraps(func)
    def inner(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return inner

def tool_thread(func):
    @wraps(func)
    def inner(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
    return inner

@alone_thread
def add_usecount(usecountinfo):
    url = f"{workhost}add_usecount/{usecountinfo}"
    response = requests.get(url, timeout=3)
    if response.status_code == 200:
        return True
    else:
        return False

def update_usecount(func):
    if use_dict:
        if func in use_dict.keys():
            use_dict[func] = use_dict[func] + 1
        else:
            use_dict[func] = 1
    else:
        use_dict[func] = 1
    return True


def runing_log(logfilename, run_msg):
    writetime = time.strftime('%Y%m%d_%H%M%S')
    logfile = open(logfilename, 'a+')
    logfile.write(f'{writetime}-{run_msg}\n')
    logfile.close()


def get_se_status(devicesn):
    result = subprocess.getoutput(f'adb -s {devicesn} shell getprop ro.vendor.secure_boot')
    return result


def install_apkfile(devicesn, apkfile):
    if devicesn:
        result = subprocess.getoutput(f'adb -s {devicesn} install {apkfile}')
        if 'Success' not in result:
            toast_ui('安装失败', f'{result}\n安装失败！请检查原因！')
    else:
        toast_ui('安装失败', '未选择设备！', duration=2000)