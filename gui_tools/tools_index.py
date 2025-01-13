# -*- coding;utf-8 -*-
"""
File name : tools_index.PY
Create file time: 2023/1/3 17:09
File Create By Author : PICO_QA
"""
import os.path
import random
from gui_tools.base_common import *
import time
import ttkbootstrap
from ttkbootstrap.constants import *
import tkinter
from gui_tools.vr_index import *

ver = 'V1.00(正式版本)'

def show_verinfo():
    """展示版本信息"""
    verlog = """1.00【新增功能】FASTGUI框架定义
            """
    verinfo = f'工具版本已更新至 {ver} \n更新日志：\n{verlog.replace(" ", "")}'
    return tkinter.messagebox.showinfo(title='版本更新', message=verinfo)


def read_usebook():
    webbrowser.open("https://bytedance.feishu.cn/docx/Yu3OdI0ugotE4XxaJZzcJeJEndh", new=0)


class Index:
    def __init__(self, picovr):
        self.picovr = picovr
        ttkbootstrap.Style().theme_use('sandstone')
        self.picovr.geometry('1550x900')
        self.picovr.iconbitmap('title.ico')
        self.picoframe = ttk.LabelFrame(self.picovr, text='PICO', padding=(5, 5), labelanchor='s')
        self.picoframe.pack(fill='both', expand=True)
        # self.loginconfig = configparser.ConfigParser()
        # if not self.loginconfig['loginconfig']['loginuser']:
        #     loginwindow = login(self.picoframe, self.loginconfig)
        #     self.picoframe.wait_window(window=loginwindow[0])
        #     if loginwindow[1]:
        #         self.loginuser = loginwindow[1][0]
        #         self.loginopenid = loginwindow[2]
        #     else:
        #         exit()
        # else:
        #     self.loginuser = self.loginconfig['loginconfig']['loginuser']
        #     self.loginopenid = self.loginconfig['loginconfig']['loginopenid']
        self.picovr.title(f'FAST GUI {ver}  Admin')
        self.headmenuinfo()
        self.mainpage = Vrpage(self.picoframe, 'Admin', 'Admin')
        if not os.path.exists('firststart.txt'):
            open('firststart.txt', 'w').close()
            take_thread(show_verinfo)

    def headmenuinfo(self):
        menu_bar = tkinter.Menu(self.picovr)
        helpmenu = tkinter.Menu(menu_bar, activebackground='blue')
        helpmenu.add_command(label='更新日志', command=show_verinfo)
        helpmenu.add_command(label='使用说明', command=read_usebook)
        menu_bar.add_cascade(label='帮助', menu=helpmenu)
        self.picovr.config(menu=menu_bar)
