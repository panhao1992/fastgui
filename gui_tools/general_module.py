# -*- coding;utf-8 -*-
"""
File name : general_module.PY
Create file time: 2022/6/28 10:45
File Create By Author : Admin
"""
import os
import subprocess
import time
from tinui.TinUI import BasicTinUI
from gui_tools.base_common import *
import configparser
import re
import tkinter.messagebox
import webbrowser
from otii_tcp_client import otii_connection, otii as otii_application


def update(devicesn, flag, updatefile, *ctrlbin):
    """station OTA 升级"""
    os.popen(f"adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,1'")
    os.popen(f'adb -s {devicesn} shell stationclient_test ClearOTACameraFlag')
    if ctrlbin:
        pi = subprocess.Popen(f'adb -s {devicesn} shell "stationclient_test UpdateFW 3 sdcard/{updatefile} '
                              f'sdcard/{ctrlbin}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        pi = subprocess.Popen(f'adb -s {devicesn} shell "stationclient_test {flag} sdcard/{updatefile}"',
                              shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pi


def controllerverupdate(devicesn, updatefiles, updatectr):
    """手柄单独升级"""
    if updatectr == '双手柄升级':
        ctrid = '2'
    elif updatectr == '左手柄升级':
        ctrid = '4'
    elif updatectr == '右手柄升级':
        ctrid = '5'
    elif updatectr == 'station升级':
        ctrid = '1'
    else:
        ctrid = '3'
    if devicesn:
        if updatefiles:
            if len(updatefiles) == 1 and ctrid != '3':
                os.popen(f"adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,1'")
                os.popen(f'adb -s {devicesn} shell stationclient_test ClearOTACameraFlag')
                os.popen(f'adb -s {devicesn} shell timeout 100 stationclient_test UpdateFW {ctrid} sdcard/{updatefiles[0]}')
                return '升级开始，请查看设备监控确认版本！'
            elif len(updatefiles) == 2 and ctrid == '3':
                os.popen(f"adb -s {devicesn} shell pxrconfigservicetest -p test -j 'pxr.trackingservice.trackingmode,1'")
                os.popen(f'adb -s {devicesn} shell stationclient_test ClearOTACameraFlag')
                if 'Sta' in updatefiles[0] and 'Ctrl' in updatefiles[1]:
                    stafile = updatefiles[0]
                    ctrlfile = updatefiles[1]
                elif 'Sta' in updatefiles[1] and 'Ctrl' in updatefiles[0]:
                    stafile = updatefiles[1]
                    ctrlfile = updatefiles[0]
                else:
                    return 'station和ctrl文件无法识别或选择错误，请检查！'
                os.popen(f'adb -s {devicesn} shell timeout 100 stationclient_test UpdateFW {ctrid} sdcard/{stafile} sdcard/{ctrlfile}')
                return '升级开始，请查看设备监控确认版本！'
            else:
                return '文件数量选择与升级类型对应错误！请检查！'
        else:
            return '请先选择升级文件！'
    else:
        return '请选择设备！'


def go_platform():
    webbrowser.open("http://10.68.99.34:8000", new=0)


def login(master, loginconfig):
    """登录页面封装"""
    login_frame = tkinter.Frame(master)
    login_frame.pack(fill='both', expand=True, pady=5, padx=5)

    tkinter.ttk.Label(login_frame, text='\n\n\n\n\n\n\n\n\n\n\n\nFAST-GUI自动化测试工具框架', font=('fangsong', 15, 'bold'), foreground='blue').pack(pady=10)

    def start_input_openid(*args):
        if openid.get() == '请输入登录用户':
            openid.set('')

    def loss_focus(*args):
        if not openid.get():
            openid.set('请输入登录用户')

    openid = StringVar(value='请输入登录用户')
    openidinput = tkinter.ttk.Entry(login_frame, textvariable=openid, width=45)
    openidinput.pack(pady=10)
    openidinput.bind('<Button-1>', start_input_openid)
    openidinput.bind('<FocusOut>', loss_focus)


    checkvalue = IntVar()
    tkinter.Checkbutton(login_frame, text='本机自动登录', onvalue=1, offvalue=0, variable=checkvalue).pack(pady=10)

    loginuser = []

    def cert():
        if openid.get():
            result = check_user(openid.get())
            if result == 'error':
                tkinter.messagebox.showerror(title='登录提示', message='请求失败，请检查网络，确认为公司内网')
            elif not result:
                tkinter.messagebox.showerror(title='登录提示', message='登录失败,请先前往机架挂机平台登录获取OPEN-ID！')
            else:
                tkinter.messagebox.showinfo(title='登录提示', message='登录校验成功！')
                loginuser.append(result)
                if checkvalue.get():
                    loginconfig.set("loginconfig", "loginuser", result)
                    loginconfig.set("loginconfig", "loginopenid", openid.get())
                    loginconfig.write(open(f"{dataspath}tools_config.ini", 'w+', encoding="utf-8-sig"))
                login_frame.destroy()
        else:
            tkinter.messagebox.showerror(title='登录提示', message='请输入OPEN-ID')

    tkinter.ttk.Button(login_frame, text='登   录', command=cert, width=10).pack(pady=10)


    return [login_frame, loginuser, openid.get()]


def writelogg(textname, info):
    """ 写入log """
    textname.config(state=tkinter.NORMAL)
    textname.insert(-1.0, info)
    textname.config(state=tkinter.DISABLED)


def clearlogg(textname):
    """ 清除log """
    textname.config(state=tkinter.NORMAL)
    textname.delete(0.0, tkinter.END)
    textname.config(state=tkinter.DISABLED)


def job(devicesn):
    try:
        a = os.popen(f'adb -s {devicesn} shell dumpsys peripheral_service').readlines()
        SwiftProperties = []
        BondedDevices = []
        # [1]设备连接数量 [2]全局模式开关状态 [3]性能模式开关状态 [4]当前连接频率 [5]当前传输频率 [8,9]配对的tracker状态信息
        for i in a[1:6]:
            b = i.strip()
            SwiftProperties.append(b)
        for i in a[8:]:
            c = i.strip()
            BondedDevices.append(c)
        return SwiftProperties, BondedDevices
    except:
        return ''


def swiftinfo_get(devicesn):
    try:
        if devicesn == '':
            return ''
        else:
            swift_ins = job(devicesn)
            connections_info = swift_ins[0][0].split(":")[1].strip()
            globalmode_info = swift_ins[0][1].split(":")[1].strip()
            performancemode_info = swift_ins[0][2].split(":")[1].strip()
            imu_interval_info = swift_ins[0][3].split(":")[1].strip()
            imu_frequency_info = swift_ins[0][4].split(":")[1].strip()
            device_swiftinfo = "全局追踪：{} | 性能模式：{} | 连接频率：{} | 上报频率：{}".format(globalmode_info, performancemode_info, imu_interval_info, imu_frequency_info)
            if not swift_ins[1]:
                var_bondeddevices = "当前设备未绑定swift!"
            else:
                if connections_info == '0':
                    var_bondeddevices = "当前设备未连接swift，请检查swift状态!"
                elif connections_info == '2':
                    swift_info_A = [swift_ins[1][0].split(',')[3].strip().split(':')[1].strip(),
                                    swift_ins[1][0].split(',')[1].strip()[9:],
                                    swift_ins[1][0].split(',')[4].strip().split(':')[1].strip(),
                                    swift_ins[1][0].split(',')[5].strip().split(':')[1].strip(),
                                    swift_ins[1][0].split(',')[7].strip().split(':')[1].strip()]
                    swift_info_B = [swift_ins[1][1].split(',')[3].strip().split(':')[1].strip(),
                                    swift_ins[1][1].split(',')[1].strip()[9:],
                                    swift_ins[1][1].split(',')[4].strip().split(':')[1].strip(),
                                    swift_ins[1][1].split(',')[5].strip().split(':')[1].strip(),
                                    swift_ins[1][1].split(',')[7].strip().split(':')[1].strip()]
                    var_bondeddevices = "--- trackerA --- \nSN : {}\nMAC : {} \n软件版本 : {}   硬件版本 : {}   电量信息 : {}\n--- trackerB --- \nSN : {}\nMAC : {} \n软件版本 : {}   硬件版本 : {}   电量信息 : {}".format(swift_info_A[0], swift_info_A[1], swift_info_A[2], swift_info_A[3], swift_info_A[4], swift_info_B[0], swift_info_B[1], swift_info_B[2], swift_info_B[3], swift_info_B[4])
                else:
                    if len(swift_ins[1]) == 1:
                        swift_info_A = [swift_ins[1][0].split(',')[3].strip().split(':')[1].strip(),
                                        swift_ins[1][0].split(',')[1].strip()[9:],
                                        swift_ins[1][0].split(',')[4].strip().split(':')[1].strip(),
                                        swift_ins[1][0].split(',')[5].strip().split(':')[1].strip(),
                                        swift_ins[1][0].split(',')[7].strip().split(':')[1].strip()]
                        var_bondeddevices = "--- 当前已配对连接1个tracker --- \nSN : {}\nMAC : {} \n软件版本 : {}   硬件版本 : {}   电量信息 : {}".format(swift_info_A[0], swift_info_A[1], swift_info_A[2], swift_info_A[3], swift_info_A[4])
                    else:
                        if swift_ins[1][1].split(',')[7].strip().split(':')[1].strip() == '-1':
                            swift_info_A = [swift_ins[1][0].split(',')[3].strip().split(':')[1].strip(),
                                            swift_ins[1][0].split(',')[1].strip()[9:],
                                            swift_ins[1][0].split(',')[4].strip().split(':')[1].strip(),
                                            swift_ins[1][0].split(',')[5].strip().split(':')[1].strip(),
                                            swift_ins[1][0].split(',')[7].strip().split(':')[1].strip()]
                            var_bondeddevices = "--- 当前仅连接1个tracker --- \n---设备 {} 未连接---\nSN : {}\nMAC : {} \n软件版本 : {}   硬件版本 : {}   电量信息 : {}".format(swift_ins[1][1].split(',')[1].strip()[9:], swift_info_A[0], swift_info_A[1], swift_info_A[2], swift_info_A[3], swift_info_A[4])
                        else:
                            swift_info_A = [swift_ins[1][1].split(',')[3].strip().split(':')[1].strip(),
                                            swift_ins[1][1].split(',')[1].strip()[9:],
                                            swift_ins[1][1].split(',')[4].strip().split(':')[1].strip(),
                                            swift_ins[1][1].split(',')[5].strip().split(':')[1].strip(),
                                            swift_ins[1][1].split(',')[7].strip().split(':')[1].strip()]
                            var_bondeddevices = "--- 当前仅连接1个tracker --- \n---设备 {} 未连接---\nSN : {}\nMAC : {} \n软件版本 : {}   硬件版本 : {}   电量信息 : {}".format(swift_ins[1][0].split(',')[1].strip()[9:], swift_info_A[0], swift_info_A[1], swift_info_A[2], swift_info_A[3], swift_info_A[4])
            return f"** Swift1.0 **\n{device_swiftinfo}\n{var_bondeddevices}"
    except Exception as msg:
        return '获取失败，请检查ROM版本是否适用'


def open_otii3_window():
    openexe = os.popen("C:\\Users\\Admin\\AppData\\Local\\otii3\\Otii 3.exe")
    time.sleep(1)
    return openexe


def close_otii3_window():
    os.popen('taskkill /F /IM "otii 3.exe"')
    time.sleep(1)


def start_otii_server():
    HOSTNAME = '127.0.0.1'
    PORT = 1905
    connection = otii_connection.OtiiConnection(HOSTNAME, PORT)
    connect_response = connection.connect_to_server()
    if connect_response["type"] == "error":
        errorinfo = f"Exit! Error code: {connect_response['errorcode']}, Description: {connect_response['payload']['message']}"
        close_otii3_window()
        return errorinfo
    else:
        otii = otii_application.Otii(connection)
        devices = otii.get_devices()
        arc = devices[0]
        project = otii.create_project()
        return [otii, arc, project]


def recording_once(otiiinfo, recordname):
    otii = otiiinfo[0]
    project = otiiinfo[2]
    deviceid = otii.get_device_id('Arc')
    time.sleep(1)
    project.start_recording()
    time.sleep(60)
    project.stop_recording()
    time.sleep(1)
    recording = project.get_last_recording()
    recording.rename(recordname)
    recording_result = recording.get_channel_statistics(device_id=deviceid, channel='mc', from_time=0, to_time=60)
    return recording_result


def recording_halfonce(otiiinfo, recordname):
    otii = otiiinfo[0]
    project = otiiinfo[2]
    deviceid = otii.get_device_id('Arc')
    time.sleep(1)
    project.start_recording()
    time.sleep(30)
    project.stop_recording()
    time.sleep(1)
    recording = project.get_last_recording()
    recording.rename(recordname)
    recording_result = recording.get_channel_statistics(device_id=deviceid, channel='mc', from_time=0, to_time=30)
    return recording_result


def quit_otii():
    otiiexe = open_otii3_window()
    HOSTNAME = '127.0.0.1'
    PORT = 1905
    connection = otii_connection.OtiiConnection(HOSTNAME, PORT)
    connect_response = connection.connect_to_server()
    if connect_response["type"] == "error":
        errorinfo = f"Exit! Error code: {connect_response['errorcode']}, Description: {connect_response['payload']['message']}"
        tkinter.messagebox.showerror(errorinfo)
    else:
        otii = otii_application.Otii(connection)
        otii.return_license(4698)
        otii.logout()
    otiiexe.close()


def start_otii():
    try:
        open_otii3_window()
        HOSTNAME = '127.0.0.1'
        PORT = 1905
        connection = otii_connection.OtiiConnection(HOSTNAME, PORT)
        connect_response = connection.connect_to_server()
        if connect_response["type"] == "error":
            errorinfo = f"Exit! Error code: {connect_response['errorcode']}, Description: {connect_response['payload']['message']}"
            tkinter.messagebox.showerror(errorinfo)
        else:
            otii = otii_application.Otii(connection)
            otii.login('pico_qa', 'Picomcu123')
            time.sleep(3)
            otii.reserve_license(4698)
            loginlicense = otii.get_licenses()
            for license in loginlicense:
                if license['id'] == 4698:
                    if license['reserved_to'] == 'pico_qa':
                        if otii.get_devices():
                            otiilogin.clear()
                            otiilogin.append('OTII初始化成功，电流仪连接中，可以开始测试！')
                        else:
                            otiilogin.clear()
                            otiilogin.append('OTII初始化成功，当前未检测到电流仪连接，请连接后开始测试')
                    else:
                        otiilogin.clear()
                        otiilogin.append('OTII初始化失败，License激活失败，请检查是否被他人占用中！')
                else:
                    pass
    except Exception as msg:
        otiilogin.clear()
        otiilogin.append('启动失败，请重试！')


def otii_logout():
    quit_otii()
    otiilogin.clear()
    tkinter.messagebox.showinfo(title='Otii提醒', message='Otii已退出！')


def ispath(device, path, mkf=1):
    """ 判断路径是否存在，并根据flag创建 """
    ls = subprocess.getoutput(f'adb -s {device} shell ls -l {path}')
    if 'total' in ls:
        return 1
    if not mkf:
        return 0
    subprocess.Popen(f'adb -s {device} shell rm -f {path}')
    while subprocess.getoutput(f'adb -s {device} shell mkdir {path}'):
        if path[-1] == '/':
            path = path.rstrip('/')
        new_path = path[0:path.rfind('/', 0, len(path))]
        if ispath(device, new_path):
            pass
    return 1


def start_shell(devicesn):
    """ 启动cmd窗口 """
    if devicesn:
        subprocess.getoutput(f"start adb -s {devicesn} root")
        time.sleep(1)
        subprocess.run(f"start adb -s {devicesn} shell", shell=True)
    else:
        tkinter.messagebox.showerror(title='启动错误', message='当前未连接设备！')


def device_remount(devicesn):
    """ 启动cmd窗口 """
    if devicesn:
        subprocess.getoutput(f"start adb -s {devicesn} root")
        time.sleep(1)
        result = subprocess.getoutput(f"adb -s {devicesn} remount")
        toast_ui('remount结果', result, duration=5000)
    else:
        tkinter.messagebox.showerror(title='启动错误', message='当前未连接设备！')


def device_fastboot(devicesn):
    """ 启动cmd窗口 """
    if devicesn:
        subprocess.run(f"start adb -s {devicesn} reboot bootloader", shell=True)
    else:
        tkinter.messagebox.showerror(title='启动错误', message='当前未连接设备！')


def get_logs(devicesn):
    tkinter.messagebox.showinfo(title='pull提醒', message=f'开始pull出设备{devicesn}的logs，pull出完成后将自动打开文件夹，请留意！')
    if not os.path.exists(f'{dataspath}logs_home'):
        os.mkdir(f'{dataspath}logs_home')
    else:
        shutil.rmtree(f'{dataspath}logs_home')
        os.mkdir(f'{dataspath}logs_home')
    logspath = f'{dataspath}logs_home/logs_{devicesn}_{time.strftime("%H%M%S")}'
    subprocess.getoutput(f'adb -s {devicesn} pull /data/logs {logspath}')
    subprocess.getoutput(f'adb -s {devicesn} pull /data/syslog/monitor/fatal {logspath}')
    os.system('start {}'.format(os.path.abspath(f'{dataspath}logs_home')))


def check_imuinfo(devicesn, item):
    subprocess.getoutput(f'adb -s {devicesn} root')
    match item:
        case '1':
            subprocess.run(f'start adb -s {devicesn} shell pvrtracking_controller_test imu-interval', shell=True)
        case '2':
            subprocess.run(f'start adb -s {devicesn} shell pvrtracking_controller_test imu-data', shell=True)
        case '3':
            subprocess.run(f'start adb -s {devicesn} shell pvrtracking_swift_test imu-statistics 300 0', shell=True)
        case '4':
            subprocess.run(f'start adb -s {devicesn} shell "pvrtracking_controller_test imu-data |grep bat"', shell=True)


def sota_monitor(devicesn):
    subprocess.run(f'start adb -s {devicesn} shell "logcat |grep -i sota"', shell=True)
