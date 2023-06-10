import datetime
import tkinter

import requests
from lxml import etree
import re
import pymysql

before_seconds = re.compile(r'([1-5]\d|[1-9])秒前')
before_minutes = re.compile(r'([1-5]\d|[1-9])分钟前')
before_hours = re.compile(r'(1\d|[1-9]|20|21|22|23)小时前')
today = re.compile(r'今天(\d{1,2}):(\d{1,2})')
this_year = re.compile(r'(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{1,2})')
global_time = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{1,2})')


# print("样例：")
# print("胡鑫宇")
# print("2022-12-30")
# print("2023-2-4")
def search(keywords, start, end,choice):
    yourcookie = 'SINAGLOBAL=2603107289436.293.1675522222904; UOR=,,cn.bing.com; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5.Aap9wgTyUKMB.F4zxYcd5JpX5KMhUgL.FoMfehn01KzpeK52dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMpe0eR1KepS0ME; ALF=1678603839; SSOLoginState=1676011839; SCF=AlD7SMY5okWeWCTQax_FsWfB5IKJ_EOx_Ixm1Fb1ReZUZ_DS8KLNKHVyarYuWgPBbxk1xzz7woABRgdS5WKhnug.; SUB=_2A25O4ZlvDeRhGeFL61oS-SzNyjyIHXVtlo2nrDV8PUNbmtANLXf_kW9NQpkafH0cuExd4GX-DNaoq9FFCrCALl_q; _s_tentry=weibo.com; Apache=411274957712.8527.1676011848869; ULV=1676011848902:6:6:5:411274957712.8527.1676011848869:1675954171555'
    yourcookie2 = 'SINAGLOBAL=2603107289436.293.1675522222904; UOR=,,cn.bing.com; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5.Aap9wgTyUKMB.F4zxYcd5JpX5KMhUgL.FoMfehn01KzpeK52dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMpe0eR1KepS0ME; ALF=1678603839; SSOLoginState=1676011839; SCF=AlD7SMY5okWeWCTQax_FsWfB5IKJ_EOx_Ixm1Fb1ReZUZ_DS8KLNKHVyarYuWgPBbxk1xzz7woABRgdS5WKhnug.; SUB=_2A25O4ZlvDeRhGeFL61oS-SzNyjyIHXVtlo2nrDV8PUNbmtANLXf_kW9NQpkafH0cuExd4GX-DNaoq9FFCrCALl_q; XSRF-TOKEN=EwONX0uqpGEItK2v3eeHcVWz; _s_tentry=weibo.com; Apache=411274957712.8527.1676011848869; ULV=1676011848902:6:6:5:411274957712.8527.1676011848869:1675954171555; WBPSESS=xWfUfpIE6JTlLktNsRVgjhVe5gHcy3FEcjMjO0DKW6LXp89Ug2IocyE_KSrNBJPLmY_X69IZJDGPOgYY5oTJtPzHE98vgk5yo-YUU8H5on7zeBVTS1Ngt1xWznzSUCHo37rfXFenOM71iSMxlk-uGA=='

    # keywords = input("输入关键字：")
    # start = input("输入起始时间：")
    # end = input("输入终止时间：")
    print(keywords, start, end)
    pages = 1  #
    url = 'https://s.weibo.com/weibo?q={0}&typeall=1&suball=1&timescope=custom%3A{1}%3A{2}&Refer=g&page={3}'.format(
        keywords,
        start, end,
        pages)
    header = {
        'authority': 's.weibo.com',
        'method': 'GET',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'cookie': yourcookie

    }

    response = requests.get(url=url, headers=header)
    context = response.text

    # 提取时间
    tree = etree.HTML(context)
    # 检查是否有返回结果
    result = tree.xpath('//div[@class="card card-no-result s-pt20b40"]')
    if len(result) == 1:
        print("没有找到相关结果")
    else:
        # 连接数据库
        mysqlCN = pymysql.connect(user='root', password='822928', host='localhost', database='python', port=3306,
                                  charset='utf8')
        mysqlCS = mysqlCN.cursor()

        # 获取pages数
        pagecount = len(tree.xpath('//ul[@class="s-scroll"]/li'))
        if pagecount == 0:
            pagecount = 1
        if choice==2:
            pagecount=1
        for p in range(1, pagecount + 1):
            url = 'https://s.weibo.com/weibo?q={0}&typeall=1&suball=1&timescope=custom:{1}:{2}&Refer=g&page={3}'.format(
                keywords, start, end, p)
            response = requests.get(url=url, headers=header)
            everytext = response.text
            tree = etree.HTML(everytext)
            # 获取当前时间
            now_time = datetime.datetime.now()
            # 获取此页用户数
            # users = tree.xpath('//div[@class="main-full"]/div[2]/div')
            # user_count = len(users)
            user_count = 1
            for u in range(1, user_count + 1):
                try:
                    user_name = tree.xpath(
                        '//div[@class="main-full"]/div[2]/div[{0}]//div[@class="content"]/div[1]/div[2]/a/text()'.format(
                            u))[0]
                    user_href = tree.xpath(
                        '//div[@class="main-full"]/div[2]/div[{0}]//div[@class="content"]/div[1]/div[2]/a/@href'.format(
                            u))[0]
                    user_text = tree.xpath(
                        '//div[@class="main-full"]/div[2]/div[{0}]//div[@class="content"]/p/text()'.format(u))[0]
                    user_time = tree.xpath(
                        '//div[@class="main-full"]/div[2]/div[{0}]//div[@class="content"]/div[2]/a/text()'.format(
                            u))[
                        0]
                    # 用户名
                    print("1." + user_name.strip())
                    print("2." + user_href.strip())
                    print("3." + user_text.strip())
                    # 时间
                    print("4." + user_time.strip())
                    if choice == 2:
                        print(tkinter.messagebox.showinfo('溯源结果',
                                                          "{0}\n{1}\n{2}".format(user_name, user_time, user_text
                                                                                      )))
                    newpattern = re.compile(r'com/(\d+)')
                    uid = newpattern.findall(user_href)[0]
                    newurl = 'https://weibo.com/ajax/profile/detail?uid={0}'.format(uid)
                    username = user_name.strip()  # 用户名
                    userhref = "https:" + user_href.strip()  # 用户主页
                    usertext = user_text.strip()  # 用户内容
                    usertime = user_time.strip()  # 发布时间
                    usertimestring = "unknown"  # 发布时间粗略
                    the_time = datetime.datetime(1970, 1, 1)  # 发布时间精确
                    # 几秒、分钟、小时前
                    if re.fullmatch(before_seconds, usertime) is not None or re.fullmatch(before_minutes,
                                                                                          usertime) is not None or re.fullmatch(
                        before_hours, usertime) is not None:
                        usertimestring = "{}-{}-{}".format(str(now_time.year), str(now_time.month), str(now_time.day))
                        if re.fullmatch(before_seconds, usertime) is not None:
                            the_time = now_time - datetime.datetime(0, 0, 0, 0, 0,
                                                                    int(re.fullmatch(before_seconds, usertime).group(
                                                                        1)))
                        if re.fullmatch(before_minutes, usertime) is not None:
                            the_time = now_time - datetime.datetime(0, 0, 0, 0,
                                                                    int(re.fullmatch(before_minutes, usertime).group(
                                                                        1)))
                        if re.fullmatch(before_hours, usertime) is not None:
                            the_time = now_time - datetime.datetime(0, 0, 0,
                                                                    int(re.fullmatch(before_hours, usertime).group(1)))
                    # 今天
                    if re.fullmatch(today, usertime) is not None:
                        usertimestring = "{}-{}-{}".format(str(now_time.year), str(now_time.month), str(now_time.day))
                        the_time = datetime.datetime(now_time.year, now_time.month, now_time.day,
                                                     int(re.fullmatch(today, usertime).group(1)),
                                                     int(re.fullmatch(today, usertime).group(2)))
                    # 今年
                    if re.fullmatch(this_year, usertime) is not None:
                        usertimestring = "{}-{}-{}".format(str(now_time.year),
                                                           str(int(re.fullmatch(this_year, usertime).group(1))),
                                                           str(int(re.fullmatch(this_year, usertime).group(2))))
                        the_time = datetime.datetime(now_time.year, int(re.fullmatch(this_year, usertime).group(1)),
                                                     int(re.fullmatch(this_year, usertime).group(2)),
                                                     int(re.fullmatch(this_year, usertime).group(3)),
                                                     int(re.fullmatch(this_year, usertime).group(4)))
                    # 之前年份
                    if re.fullmatch(global_time, usertime) is not None:
                        usertimestring = "{}-{}-{}".format(str(int(re.fullmatch(global_time, usertime).group(1))),
                                                           str(int(re.fullmatch(global_time, usertime).group(2))),
                                                           str(int(re.fullmatch(global_time, usertime).group(3))))
                        the_time = datetime.datetime(int(re.fullmatch(global_time, usertime).group(1)),
                                                     int(re.fullmatch(global_time, usertime).group(2)),
                                                     int(re.fullmatch(global_time, usertime).group(3)),
                                                     int(re.fullmatch(global_time, usertime).group(4)),
                                                     int(re.fullmatch(global_time, usertime).group(5)))
                    print(usertimestring)
                    # 根据user_href获取ip属地

                    newheader = {
                        'authority': 'weibo.com',
                        'method': 'GET',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                        'cookie': yourcookie2
                    }
                    user_interface = requests.get(url=newurl, headers=newheader)
                    user_info = user_interface.text
                    pattern = re.compile(r'(IP属地.+?)"', re.S)
                    ip = pattern.findall(user_info)[0]
                    # 用户ip
                    print("5." + ip.replace('\\t', ''))

                    userip = ip.replace('\\t', '')

                    userip = userip.replace('IP属地：', '')
                    mysqlCS.execute(
                        "Insert into data value(%s,%s,%s,%s,%s,%s,%s)",
                        [keywords, username, userhref, usertext, usertimestring, userip, the_time])
                    mysqlCN.commit()

                except:
                    continue
                finally:
                    print("------------------------------------------------------")

        mysqlCS.close()
        mysqlCN.close()


if __name__ == '__main__':
    search("李白", "2022-2-1", "2023-2-2")