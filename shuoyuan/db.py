# -*-coding = utf-8 -*-
# @Time : 2023/2/6 13:22
# @Author : zou
# @File : db.py
# @Software : PyCharm
# 数据库链接
import pymysql

address_list = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃',
                '青海', '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']


class cnMySQL:
    def __init__(self):
        self._dbhost = 'localhost'
        self._dbuser = 'root'
        self._dbpassword = '822928'
        self._dbname = 'python'
        self._dbcharset = 'utf8'
        self._dbport = int(3306)
        self._conn = self.connectMySQL()

        if (self._conn):
            self._cursor = self._conn.cursor(cursor=pymysql.cursors.DictCursor)

    def connectMySQL(self):
        try:
            conn = pymysql.connect(host=self._dbhost,
                                   user=self._dbuser,
                                   passwd=self._dbpassword,
                                   db=self._dbname,
                                   port=self._dbport,
                                   cursorclass=pymysql.cursors.DictCursor,
                                   charset=self._dbcharset)
        except Exception as e:
            raise
            # print("数据库连接出错")
            conn = False
        return conn

    def close(self):
        if (self._conn):
            try:
                if (type(self._cursor) == 'object'):
                    self._conn.close()
                if (type(self._conn) == 'object'):
                    self._conn.close()
            except Exception:
                print("关闭数据库连接异常")

    def readmysql_ip(self, keywords, conntext):
        if (self._conn):
            try:
                # 获取到sql执行的全部结果
                self._cursor.execute(
                    "select user_ip from data where user_time!='unknown' and keywords='{}' order by the_time asc;".format(
                        keywords))

                results = self._cursor.fetchall()
                # print(results)
                table_list = []
                for r in results:
                    if (r["user_ip"] in address_list):
                        table_list.append(r[conntext])
            except Exception:
                results = False
                print("查询异常")
            self.close()

        return table_list  # 返回一个list

    def readmysql_time(self, keywords, conntext):
        # 创建游标
        # 执行sql语句
        if (self._conn):
            try:
                # 获取到sql执行的全部结果
                self._cursor.execute(
                    "select user_ip,user_time,user_text from data where user_time!='unknown' and keywords='{}' order by the_time asc;".format(
                        keywords))

                results = self._cursor.fetchall()
                # print(results)
                table_list = []
                for r in results:
                    if (r["user_ip"] in address_list):
                        utxt = 'user_text'
                        conntxt = r[conntext] +'<br>'+ r[utxt]
                        table_list.append(conntxt)
            except Exception:
                results = False
                print("查询异常")
            self.close()

        return table_list  # 返回一个

    def delete_all(self):
        self._cursor.execute("TRUNCATE TABLE data;")