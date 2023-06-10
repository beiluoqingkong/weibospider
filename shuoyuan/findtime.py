
from datetime import datetime, timedelta
import requests
from lxml import etree
from threading import Thread as PyThread
import spider


def findfirsttime(keywords, start, end):
    yourcookie = 'SINAGLOBAL=2603107289436.293.1675522222904; UOR=,,cn.bing.com; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5.Aap9wgTyUKMB.F4zxYcd5JpX5KMhUgL.FoMfehn01KzpeK52dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMpe0eR1KepS0ME; ALF=1678603839; SSOLoginState=1676011839; SCF=AlD7SMY5okWeWCTQax_FsWfB5IKJ_EOx_Ixm1Fb1ReZUZ_DS8KLNKHVyarYuWgPBbxk1xzz7woABRgdS5WKhnug.; SUB=_2A25O4ZlvDeRhGeFL61oS-SzNyjyIHXVtlo2nrDV8PUNbmtANLXf_kW9NQpkafH0cuExd4GX-DNaoq9FFCrCALl_q; _s_tentry=weibo.com; Apache=411274957712.8527.1676011848869; ULV=1676011848902:6:6:5:411274957712.8527.1676011848869:1675954171555'
    # keywords = input("输入关键字：")
    # start = input("输入起始时间：")
    # end = input("输入终止时间：")
    keywords = keywords
    start = start
    end = end
    pages = 1  #############
    is_data = 1
    url = 'https://s.weibo.com/weibo?q={0}&typeall=1&suball=1&timescope=custom:{1}:{2}&Refer=g&page={3}'.format(
        keywords,
        start, end,
        pages)
    header = {
        'authority': 's.weibo.com',
        'method': 'GET',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'cookie': yourcookie
        # 'referer':url
    }
    # now=datetime.now()
    # print(datetime.strptime(end,"%Y-%m-%d").date())
    # print((datetime.strptime(end,"%Y-%m-%d").date()-datetime.strptime(start,"%Y-%m-%d").date()).days)
    # print(now-timedelta(days=0.5))

    response = requests.get(url=url, headers=header)
    context = response.text

    # 提取时间
    tree = etree.HTML(context)
    # 检查是否有返回结果
    result = tree.xpath('//div[@class="card card-no-result s-pt20b40"]')

    if len(result) == 1:
        print("没有找到相关结果")
        is_data = 0
    else:
        l = datetime.strptime(start, "%Y-%m-%d").date()
        r = datetime.strptime(end, "%Y-%m-%d").date()
        thedays = (r - l).days
        # print(thedays)
        flag = 1
        value1 = 0
        while flag == 1:
            if thedays != 1:
                if is_data == 1:
                    value1 = thedays % 2
                    thedays = int(thedays / 2)
                    r = r - timedelta(days=thedays + value1)
                else:
                    r = r + timedelta(days=thedays + value1)
                    l = l + timedelta(days=thedays + value1)

            else:
                print("开始日期是:{0}到{1}之间".format(l,r))
                # print(tkinter.messagebox.showinfo('溯源结果',"第一条消息的日期是:{0}到{1}之间".format(l,r)))
                thread_searchold=PyThread(target=spider.search,args=(keywords, l, r,2))
                thread_searchold.setDaemon(True)
                thread_searchold.start()
                flag = 0
                break
            url = 'https://s.weibo.com/weibo?q={0}&typeall=1&suball=1&timescope=custom:{1}:{2}&Refer=g&page={3}'.format(
                keywords, str(l), str(r), pages)
            response = requests.get(url=url, headers=header)
            context = response.text
            tree = etree.HTML(context)
            result = tree.xpath('//div[@class="card card-no-result s-pt20b40"]')
            if len(result) == 1:
                is_data = 0
                # print("没有")
            else:
                is_data = 1
                # user_name = tree.xpath(
                #     '//div[@class="m-wrap"]/div[1]/div[2]/div[{0}]//div[@class="content"]/div/div[2]/a[1]/text()'.format(
                #         1))[0]
                # print(user_name)
                # print("{0}-----------{1}".format(l,r))

    # return r


if __name__ == "__main__":
    findfirsttime('李白', '2022-1-1', '2023-1-2')
