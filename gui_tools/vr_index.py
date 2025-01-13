# -*- coding;utf-8 -*-
"""
File name : vr_index.PY
Create file time: 2024/1/10 16:00
File Create By Author : PICO_QA
"""

import os.path
import sys
from gui_tools.base_common import *
import time
import ttkbootstrap
from tkinter import ttk
from gui_tools.pico_basetools import *
from gui_tools.general_module import *
import tkinter as tk


class Vrpage:
    def __init__(self, picovr, loginuser, loginopenid):
        self.nodetesttool = None
        self.cavasframe = None
        self.toolcavas = None
        self.snlistframe = None
        self.casetesttool = None
        self.update_device_list_btn = None
        self.device_list = None
        self.specialtool = None
        self.monitortool = None
        self.menuframe = None
        self.testtool = None
        self.rominfo = StringVar()
        self.mcuinfo = StringVar()
        self.handinfo = StringVar()
        self.swiftinfo = StringVar()
        self.picovr = picovr
        self.loginuser = loginuser
        self.loginopenid = loginopenid
        self.snchose = tkinter.StringVar()
        self.menulist()
        self.devicesframe = ttk.Frame(self.picovr, padding=(1, 1))
        self.devicesframe.pack(side='top', fill='x', padx=5, pady=5)
        self.snlistframe = ttk.LabelFrame(self.devicesframe, text='展示项目列表', padding=(1, 1), labelanchor='n')
        self.snlistframe.grid(row=0, column=0, sticky=N+S+W, padx=5, pady=5)
        self.infoframe = ttk.LabelFrame(self.devicesframe, text='顶栏常驻信息', padding=(1, 1), labelanchor='n')
        self.infoframe.grid(row=0, column=1, sticky=N+S+W+E, padx=5)
        self.actionframe = ttk.LabelFrame(self.devicesframe, text='功能与操作', padding=(1, 1), labelanchor='n')
        self.actionframe.grid(row=0, column=3, sticky=N+S+W+E, padx=5)
        take_thread(self.sn_listshow)
        self.toolframe = ttk.LabelFrame(self.picovr, text='详情', width=800, height=680, padding=(5, 5), labelanchor='n')
        self.toolframe.pack(side='right', fill='both', expand=True, padx=5)
        self.run_adbbasetool()

    def menulist(self):
        self.menuframe = ttk.Frame(self.picovr, padding=(1, 1))
        self.menuframe.pack(side='left', fill='y', padx=3)
        self.specialtool = ttk.LabelFrame(self.menuframe, text='菜单', padding=(1, 1), labelanchor='n')
        self.specialtool.grid(column=0, row=0, padx=5, pady=5, sticky=W+E)
        specialtools_menu_names = ['功能1', '功能2', '功能3', '功能4', '功能5']
        variable_chose = StringVar()
        variable_chose.set(specialtools_menu_names[0])
        run_to_specialtools = [self.run_adbbasetool, print('...'), print('...'), print('...'), print('...')]
        for i in range(len(specialtools_menu_names)):
            ttk.Radiobutton(self.specialtool, text=specialtools_menu_names[i], variable=variable_chose, value=specialtools_menu_names[i], width=12, bootstyle="dark-outline-toolbutton",
                            command=run_to_specialtools[i]).grid(column=0, row=i, pady=5, padx=5)

    def sn_listshow(self):
        devices = show_devices()
        self.snlistframe.destroy()
        self.snlistframe = ttk.LabelFrame(self.devicesframe, text='展示项目列表', padding=(5, 5), labelanchor='n')
        self.snlistframe.grid(row=0, column=0, sticky=N + S + W, padx=5)
        if not devices:
            ttk.Label(self.snlistframe, text='无设备连接,连接设备后【刷新列表】').grid(row=0, column=0)
            ttk.Button(self.snlistframe, text='刷新列表', command=self.sn_listshow, bootstyle='info').grid(row=1, column=0, pady=5)
            self.showallinfo('')
        else:
            self.snchose.set(devices[0])
            for i in range(len(devices)):
                ttk.Radiobutton(self.snlistframe, text=devices[i], variable=self.snchose, value=devices[i], width=20, bootstyle="info", command=lambda: self.showallinfo(self.snchose.get())).grid(row=i, column=0, padx=5, pady=2)
            self.showallinfo(devices[0])
        return True

    def showallinfo(self, devicesn):
        if check_device(devicesn) or devicesn == '':
            self.device_info(devicesn)
            self.action_buttons(devicesn)
            take_thread(self.device_info_update, devicesn)
        else:
            tkinter.messagebox.showwarning(title='warning', message='设备不存在，请刷新列表！')

    def device_info(self, devicesn):
        try:
            self.infoframe.destroy()
            self.infoframe = ttk.LabelFrame(self.devicesframe, text='顶栏常驻信息', padding=(5, 5), labelanchor='n')
            self.infoframe.grid(row=0, column=1, sticky=N + S + W, padx=5)
            if not devicesn:
                ttk.Label(self.infoframe, text='未选择设备').grid(row=0, column=0)
            elif not check_device(devicesn):
                self.sn_listshow()
            else:
                Entry(self.infoframe, textvariable=self.rominfo, state='readonly', width=80).grid(row=0, column=0, sticky=W)
                Entry(self.infoframe, textvariable=self.mcuinfo, state='readonly', width=80).grid(row=1, column=0, sticky=W)
                Entry(self.infoframe, textvariable=self.handinfo, state='readonly', width=80).grid(row=2, column=0, sticky=W)
                Entry(self.infoframe, textvariable=self.swiftinfo, state='readonly', width=80).grid(row=3, column=0, sticky=W)
            return True
        except:
            return True

    def device_info_update(self, devicesn):
        if check_device(devicesn):
            ctrlinfo = getcontrollerver(devicesn)
            self.rominfo.set(f'设备: 【{get_se_status(devicesn)}】{getrominfo(devicesn)[:-1]} ({getdevicebat(devicesn)})')
            self.mcuinfo.set(f'MCU: StationVer: {getstationversion(devicesn)} |  StationservicePID: {get_stationservice_pid(devicesn)} |  {get_stationupdate_flag(devicesn)}')
            self.handinfo.set(f'手柄: LEFT: {ctrlinfo[0]} |  RIGHT: {ctrlinfo[1]}')
            self.swiftinfo.set(f'Swift2: {get_trackerver(devicesn)}')
            toast_ui('信息更新', '设备信息更新完成！', duration=2000)
        else:
            self.rominfo.set('设备未连接，请刷新设备列表')
            self.mcuinfo.set('设备未连接，请刷新设备列表')
            self.handinfo.set('设备未连接，请刷新设备列表')
            self.swiftinfo.set('设备未连接，请刷新设备列表')

    def action_buttons(self, devicesn=''):
        try:
            self.actionframe.destroy()
            self.actionframe = ttk.LabelFrame(self.devicesframe, text='功能与操作', padding=(5, 5), labelanchor='n')
            self.actionframe.grid(row=0, column=3, sticky=N + S + W, padx=5)
            if not devicesn:
                ttk.Label(self.actionframe, text='未选择设备').grid(row=0, column=0)
            else:
                ttk.Button(self.actionframe, text='刷新', command=lambda: print('...'), bootstyle='info', width=8).grid(row=0, column=0, padx=5, pady=5)
                ttk.Button(self.actionframe, text='重启', command=lambda: print('...'), bootstyle='info', width=8).grid(row=1, column=0, padx=5, pady=5)
                ttk.Button(self.actionframe, text='获取', command=lambda: print('...'), bootstyle='info', width=8).grid(row=0, column=1, padx=5, pady=5)
                ttk.Button(self.actionframe, text='打印', command=lambda: print('...'), bootstyle='info', width=8).grid(row=1, column=1, padx=5, pady=5)
                ttk.Button(self.actionframe, text='查看', command=lambda: print('...'), bootstyle='info', width=8).grid(row=0, column=2, padx=5, pady=5)
                ttk.Button(self.actionframe, text='。。。', command=lambda: print('...'), bootstyle='info', width=8).grid(row=1, column=2, padx=5, pady=5)

                imu_buttons = ttk.Menubutton(self.actionframe, text="功能菜单A", bootstyle='info', width=7)
                imu_buttons.grid(row=0, column=3, padx=5, pady=5)
                imu_menu = tk.Menu(imu_buttons)
                imu_menu.add_command(label='A功能', command=lambda: print('...'))
                imu_menu.add_command(label='B功能', command=lambda: print('...'))
                imu_menu.add_command(label='C功能', command=lambda: print('...'))
                imu_menu.add_command(label='D功能', command=lambda: print('...'))
                imu_menu.add_command(label='E功能', command=lambda: print('...'))
                imu_buttons.config(menu=imu_menu)

                android_key = ttk.Menubutton(self.actionframe, text="功能菜单B", bootstyle='info', width=7)
                android_key.grid(row=1, column=3, padx=5, pady=5)
                android_key_menu = tk.Menu(android_key)
                android_key_menu.add_command(label='A功能', command=lambda: print('...'))
                android_key_menu.add_command(label='B功能', command=lambda: print('...'))
                android_key_menu.add_command(label='C功能', command=lambda: print('...'))
                android_key_menu.add_command(label='D功能', command=lambda: print('...'))
                android_key_menu.add_command(label='E功能', command=lambda: print('...'))
                android_key.config(menu=android_key_menu)
            return True
        except:
            return True

    def toolframe_update(self, partname):
        self.toolframe.destroy()
        self.toolframe = ttk.LabelFrame(self.picovr, text=partname, width=800, height=680, padding=(1, 1), labelanchor='n')
        self.toolframe.pack(side='right', fill='both', expand=True, padx=11)
        self.toolcavas = Canvas(self.toolframe)
        self.cavasframe = Frame(self.toolcavas, height=960)
        self.toolcavas.create_window((0, 0), window=self.cavasframe, anchor="nw", tags="frame")
        self.cavasframe.bind("<Configure>", lambda event, cavas=self.toolcavas: self.toolcavas.configure(scrollregion=self.toolcavas.bbox("all")))
        vsb = ttk.Scrollbar(self.toolframe, bootstyle='primary-round', orient="vertical", command=self.toolcavas.yview)
        vsb.pack(side='right', fill='y')
        self.toolcavas.configure(yscrollcommand=vsb.set)
        self.toolcavas.pack(fill='both', expand=True)

    def run_adbbasetool(self):
        self.toolframe_update('指令辅助')
        Picotools_page(self.cavasframe, self.loginuser)


class Picotools_page:
    def __init__(self, picovr, loginuser):
        self.picobasetools_frame = None
        self.picovr = picovr
        self.loginuser = loginuser
        self.picobasetools_page()

    def picobasetools_page(self):
        self.picobasetools_frame = Frame(self.picovr, width=1400, height=900)
        self.picobasetools_frame.grid(row=1, column=0, rowspan=20, columnspan=6)
        picobasetools_framepage(self.picobasetools_frame)
