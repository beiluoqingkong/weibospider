from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType
from db import cnMySQL


def CreateHtml(keywords):
    # 连接数据库
    db = cnMySQL()
    # address = ['深圳', '杭州', '哈尔滨', '重庆', '上海', '乌鲁木齐']
    # times = ['2013-6', '2013-6', '2013-6', '2013-6', '2013-6', '2013-6-9']
    address = db.readmysql_ip(keywords, 'user_ip')
    times = db.readmysql_time(keywords, 'user_time')
    db.close()
    print(address)
    print(times)
    if address and times:
        # 要确保两个列表是一样长的
        datas = [i for i in zip(address, times)]
        # pprint(datas)
        address2 = ["1"]
        for item in address:
            address2.append(item)
        address.append("2")
        datas2 = [i for i in zip(address2, address)]
        # pprint(datas2)
        del (datas2[0])
        datas2.pop()
        # pprint(datas2)

        c = (
            Geo()
            .add_schema(maptype="china")
            .add("",
                 datas, type_=ChartType.EFFECT_SCATTER, color="green",
                 )
            .add("传播路线",
                 datas2, type_=ChartType.LINES, effect_opts=opts.EffectOpts(
                    symbol=SymbolType.ARROW, symbol_size=6, color="blue"),
                 linestyle_opts=opts.LineStyleOpts(curve=0.2)
                 )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=keywords))
        )

        c.render("templates/display.html")
        return True
    else:
        return False


if __name__ == '__main__':
    CreateHtml("李白")
