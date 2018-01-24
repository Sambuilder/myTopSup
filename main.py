# -*- coding:utf-8 -*-
"""

    问答助手~

"""

import win32gui
from pyhooked import Hook, KeyboardEvent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from core.ocr import get_text_from_image_hanwang, get_text_from_image_baidu
from core.windows import analyze_current_screen_text
import configparser


def pre_process_question(keyword):
    """
    strip charactor and strip ?
    :param question:
    :return:
    """
    for char, repl in [("“", ""), ("”", ""), (" ", ""), ("\t", "")]:
        keyword = keyword.replace(char, repl)
    keyword = keyword.split(r".")[-1]
    tag = keyword.find("?")
    if tag != -1:
        keyword = keyword[:tag]
    tag = keyword.find("？")
    if tag != -1:
        keyword = keyword[:tag]
    keywords = keyword.split(" ")
    keyword = "".join([e.strip("\r\n") for e in keywords if e])
    return keyword


class TopSupHelper(object):

    def __init__(self,
                 data_directory='screenshots',
                 vm_name='夜深模拟器',
                 app_name='西瓜视频',
                 search_engine='http://www.baidu.com',
                 hot_key='F2',
                 ocr_engine='baidu',
                 api_version='0',
                 hanwan_appcode='3cc4f16c357e4f329dab5e71c810a871',
                 app_id='10697165',
                 app_key='CjCUKNSPrzduq1VftrQYGXlA',
                 app_secret='mWX6i7Dq6GmyjrQWtt20OKQtrWo19CGM'):
        conf = configparser.ConfigParser()
        conf.read("config.ini", encoding="utf-8")
        self.data_directory = conf.get('config', "data_directory")
        self.vm_name = conf.get('config', "vm_name")
        self.app_name = conf.get('config', "app_name")
        self.search_engine = conf.get('config', "search_engine")
        self.hot_key = conf.get('config', "hot_key")
        # ocr_engine = 'baidu'
        self.ocr_engine = conf.get('config', "ocr_engine")
        # baidu ocr
        self.app_id = conf.get('config', "app_id")
        self.app_key = conf.get('config', "app_key")
        self.app_secret = conf.get('config', "app_secret")
        # 0 表示普通识别，1 表示精确识别
        self.api_version = conf.get('config', "api_version")
        # hanwang orc
        self.hanwan_appcode = conf.get('config', "hanwan_appcode")

    def main(self):
        print('我来识别这个题目是啥!!!')
        text_binary = analyze_current_screen_text(label=self.vm_name, directory=self.data_directory)
        if self.ocr_engine == 'baidu':
            print("用百度去OCR识别了!!!\n")
            keyword = get_text_from_image_baidu(
                image_data=text_binary,
                app_id=self.app_id,
                app_key=self.app_key,
                app_secret=self.app_secret,
                api_version=self.api_version,
                timeout=5)
            keyword = "".join([e.strip("\r\n") for e in keyword if e])
        else:
            print("用汉王去OCR识别了!!!\n")
            keyword = get_text_from_image_hanwang(image_data=text_binary, appcode=self.hanwan_appcode)

        if not keyword:
            print("没识别出来，随机选吧!!!\n")
            print("题目出现的时候按F2，我就自动帮你去搜啦~\n")
            return

        keyword = pre_process_question(keyword)

        if len(keyword) < 2:
            print("没识别出来，随机选吧!!!\n")
            print("题目出现的时候按F2，我就自动帮你去搜啦~\n")
            return
        print("我用关键词:\" ", keyword, "\"去百度答案啦!")

        elem = browser.find_element_by_id("kw")
        elem.clear()
        elem.send_keys(keyword)
        elem.send_keys(Keys.RETURN)

        print("结果在浏览器里啦~\n")
        print("题目出现的时候按F2，我就自动帮你去搜啦~\n")

    def handle_events(self, args):
        if isinstance(args, KeyboardEvent):
            if args.current_key == self.hot_key and args.event_type == 'key down':
                self.main()
            elif args.current_key == 'Q' and args.event_type == 'key down':
                hk.stop()
                print('退出啦~')


if __name__ == "__main__":
    try:
        helper = TopSupHelper()
        print("配置文件正常加载!\n")
    except:
        print("配置文件异常，尝试使用默认配置\n")
    try:
        browser = webdriver.Chrome(r'.\tools\chromedriver.exe')
        browser.get(helper.search_engine)
    except:
        print("chrome浏览器打开异常，可能是版本不对\n")
    hld = win32gui.FindWindow(None, helper.vm_name)
    if hld > 0:
        print('使用前记得去config.ini把配置改好哦~~,主要是自己申请换key,不然次数很快就用完啦~~\n\n用模拟器打开对应应用~~\n题目出现的时候按F2，我就自动帮你去搜啦~\n')
        hk = Hook()
        hk.handler = helper.handle_events
        hk.hook()
    else:
        print('咦，你没打开' + helper.vm_name + '吧!请打开' + helper.vm_name + '并重启下start.exe')
