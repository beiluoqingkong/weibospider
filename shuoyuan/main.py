import datetime
import re
import time
import tkinter
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
import clr

import findtime
from Calendar import Calendar
import spider
import CreateHtml
from threading import Thread as PyThread
from db import cnMySQL
import queue
import inspect
import ctypes

# 引入c#的dll
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Threading')
from System.Windows.Forms import Control
from System.Threading import Thread, ApartmentState, ThreadStart

time_format = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')


def _async_raise(tid, exctype):
    """Raises an exception in the threads with id tid"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


# 更新界面文件
def update(keywords, msg_queue):
    while True:
        # 生成HTML
        created = CreateHtml.CreateHtml(keywords=keywords)
        # 有图
        if created:
            msg_queue.put("display")
        else:
            msg_queue.put("waiting")
        print('00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        time.sleep(10)


class UI:
    def __init__(self):
        if not have_runtime():  # 没有webview2 runtime
            install_runtime()

        self.window = tkinter.Tk()
        self.window.title("信息溯源")  # 标题
        self.window.iconbitmap('vscode.ico')  # 图标
        self.window.geometry("800x750+350+20")  # 设置大小及位置
        self.window.resizable(False, False)  # 大小调整

        # 顶层菜单
        menubar = tkinter.Menu(self.window)
        self.window.configure(menu=menubar)
        # 菜单栏选项
        menu = tkinter.Menu(self.window, tearoff=False)
        menu.add_command(label="关于", command=self.about)
        menubar.add_cascade(label="about", menu=menu)  # 向菜单栏上添加菜单选项
        # 输入框
        self.search_keywords = tkinter.StringVar()
        self.entry_keywords = tkinter.Entry(self.window, textvariable=self.search_keywords)
        self.entry_keywords.place(x=200, y=50, width=300, height=35)

        # 搜索按钮
        self.button_search = tkinter.Button(self.window, text="搜索", command=self.search)
        self.button_search.place(x=520, y=50, width=50, height=35)

        # 清除按钮
        self.button_delete = tkinter.Button(self.window, text="清除", command=self.delete_search)
        self.button_delete.place(x=590, y=50, width=50, height=35)

        # 停止按钮
        self.button_stop = tkinter.Button(self.window, text="停止搜索", command=self.stop_search)
        self.button_stop.place(x=660, y=50, width=60, height=35)

        # 开始时间标签
        label_start_time = tkinter.Label(self.window, text="开始时间")
        label_start_time.place(x=90, y=100, width=50, height=30)

        # 开始时间文本
        self.start_time = tkinter.StringVar()
        self.entry_start_time = tkinter.Entry(self.window, textvariable=self.start_time)
        self.entry_start_time.place(x=160, y=100, width=150, height=30)

        # 开始时间选择按钮
        self.button_start_time = tkinter.Button(self.window, text="开始时间", command=self.select_start_time)
        self.button_start_time.place(x=330, y=100, width=60, height=30)

        # 结束时间标签
        label_end_time = tkinter.Label(self.window, text="结束时间")
        label_end_time.place(x=420, y=100, width=50, height=30)

        # 结束时间文本
        self.end_time = tkinter.StringVar()
        self.entry_end_time = tkinter.Entry(self.window, textvariable=self.end_time)
        self.entry_end_time.place(x=490, y=100, width=150, height=30)

        # 结束时间选择按钮
        self.button_end_time = tkinter.Button(self.window, text="结束时间", command=self.select_end_time)
        self.button_end_time.place(x=660, y=100, width=60, height=30)

        # 网页
        html = ""
        with open("templates/start.html") as f:
            html = f.read()
        # print(html)
        self.frame = WebView2(self.window, width=750, height=600)
        self.frame.place(x=25, y=140)
        self.frame.load_html(html)

        # 关闭动作
        self.window.protocol('WM_DELETE_WINDOW', self.close_windows)

        # 搜索线程
        self.thread_search = None
        self.thread_load = None
        self.thread_find=None
        # 数据库
        self.db = cnMySQL()
        # 创建after,不断刷新网页显示
        self.window.after(1000, self.update_html)
        # queue
        self.queue = queue.Queue()
        # 显示窗体
        self.window.mainloop()

    # 更新网页界面
    def update_html(self):
        # 队列不为空
        if not self.queue.empty():
            content = self.queue.get()
            if content == "waiting":
                # 加载HTML
                html = ""
                with open("templates/waiting.html") as f:
                    html = f.read()
                # 重新加载
                self.frame.load_html(html)
            elif content == "display":
                # 加载HTML
                html = ""
                with open("templates/display.html") as f:
                    html = f.read()
                # 重新加载
                self.frame.load_html(html)
        self.window.after(1000, self.update_html)

    # 搜索
    def search(self):
        # 关闭上一个搜索线程
        if self.thread_search is not None and self.thread_search.is_alive():
            stop_thread(self.thread_search)
        if self.thread_load is not None and self.thread_load.is_alive():
            stop_thread(self.thread_load)
        if self.thread_find is not None and self.thread_find.is_alive():
            stop_thread(self.thread_find)
        # 清空数据库
        self.db.delete_all()
        keywords = self.search_keywords.get()
        start_time = self.start_time.get()
        end_time = self.end_time.get()
        # 输入为空检测
        if keywords != "" and start_time != "" and end_time != "":
            # 格式检测
            if re.fullmatch(time_format, start_time) is not None and re.fullmatch(time_format, end_time) is not None:
                st = datetime.datetime(int(start_time.split('-')[0]), int(start_time.split('-')[1]),
                                       int(start_time.split('-')[2]))
                et = datetime.datetime(int(end_time.split('-')[0]), int(end_time.split('-')[1]),
                                       int(end_time.split('-')[2]))
                nt = datetime.datetime.now()
                # 时间逻辑检测
                if st > et or st > nt or et > nt:
                    print(tkinter.messagebox.showwarning('时间错误', '时间选择错误'))
                else:
                    print(keywords)
                    # 爬取数据

                    self.thread_find = PyThread(target=findtime.findfirsttime,args=(keywords,'2009-8-16','2023-2-10'))
                    self.thread_find.setDaemon(True)
                    self.thread_find.start()
                    self.thread_search = PyThread(target=spider.search, args=(keywords,
                                                                              "{}-{}-{}".format(str(st.year),
                                                                                                str(st.month),
                                                                                                str(st.day)),
                                                                              "{}-{}-{}".format(str(et.year),
                                                                                                str(et.month),
                                                                                                str(et.day)),1))
                    self.thread_search.setDaemon(True)
                    self.thread_search.start()
                    # self.thread_search.join()
                    # spider.search(keywords=keywords, start="{}-{}-{}".format(str(st.year), str(st.month), str(st.day)),
                    #               end="{}-{}-{}".format(str(et.year), str(et.month), str(et.day)))
                    self.thread_load = PyThread(target=update, args=(keywords, self.queue))
                    self.thread_load.setDaemon(True)
                    self.thread_load.start()
                    # self.thread_load.join()
            else:
                print(tkinter.messagebox.showwarning('时间错误', '时间格式错误'))
        else:  # 输入错误提示
            msg = ""
            if keywords == "":
                msg += "关键词为空！\n"
            if start_time == "":
                msg += "开始时间为空！\n"
            if end_time == "":
                msg += "结束时间为空！"
            print(tkinter.messagebox.showwarning('输入错误', msg))

    # 停止搜索
    def stop_search(self):
        if self.thread_search.is_alive():
            stop_thread(self.thread_search)
        if self.thread_load.is_alive():
            stop_thread(self.thread_load)
            # html = ""
            # with open("templates/start.html") as f:
            #     html = f.read()
            # self.frame.load_html(html)

    # 关于
    def about(self):
        year = datetime.datetime.now().year
        print(tkinter.messagebox.showinfo('关于',
                                          "本应用基于Tkinter实现可视化\n使用tkwebview2实现html展示\nVersion:   v0.1.9\nCopyright © 2023-{} 御三家".format(
                                              year)))

    # 清除输入框
    def delete_search(self):
        self.search_keywords.set("")

    # 选择开始时间
    def select_start_time(self):
        for date in [Calendar().selection()]:
            if date:
                self.start_time.set(date)

    # 选择结束时间
    def select_end_time(self):
        for date in [Calendar().selection()]:
            if date:
                self.end_time.set(date)

    # 应用关闭
    def close_windows(self):
        self.db.delete_all()  # 清空数据库
        self.db.close()  # 关闭数据库
        self.window.destroy()  # 关闭界面
        t.Abort()  # 退出线程


if __name__ == '__main__':
    t = Thread(ThreadStart(UI))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Join()