# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import time
import pymysql
import uuid


class CqcknewsPipeline(object):
    #TODO:去重
    def process_item(self, item, spider):
        '''对Item进行处理'''

        region_str = '城口县,垫江县,丰都县,奉节县,梁平区,彭水苗族土家族自治县,石柱土家族自治县,巫山县,巫溪县,武隆区,秀山土家族苗族自治县,酉阳土家族苗族自治县,云阳县,忠县'
        if len(item['cover'])<=2:
            item['cover'] = ''
        if region_str.find(item['city'],1)==-1:
            item['city_type'] = '重庆城区'
        else:
            item['city_type'] = '重庆郊县'
        return item


class MysqlPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        '''通过依赖注入scrapy的核心组件'''
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        '''spider开启时自动调用'''

        # TODO:数据库连接日志
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        # self,db = pymysql.connect(host='94.191.8.225', user='travel', password='jyck2019.', port=3306, db='cqck-news')
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        '''spider关闭时自动调用'''
        self.db.close()

    def process_item(self, item, spider):
        t_sql = self.get_news_sql(item)
        try:
            self.cursor.execute(t_sql[0])
            self.cursor.execute(t_sql[1])
        except Exception as e:
            #TODO:数据库异常日志
            print(e)
            self.db.rollback()
        else:
            self.db.commit()
        return item

    def get_news_sql(self, item):
        guid = uuid.uuid1()
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        city = item['city']
        link = item['link']
        news_time = item['time']
        title = item['title']
        content = item['content']
        cover = item['cover']
        author = item['author']
        city_type = item['city_type']
        province = item['province']

        #f-string
        news_info = f"insert into news_info(create_time,del_flag,string_id,source_way,status,put_country,news_type,news_from,news_time,title,surface_plot,view_count,click_count,view_status,put_province,put_city,news_link)" \
            f"values (DATE('{time_str}'),1,'{guid}','cqcknews爬虫采集',1,'{city}',10001,'{author}',if('{news_time}' = '', null, str_to_date('{news_time}', '%Y-%m-%d %H:%i:%s')),'{title}','{cover}',0,0,1,'{province}','{city_type}','{link}')"
        news_content = f"insert into news_content(create_time,del_flag,string_id,news_id,news_content,update_time)" \
            f"values (DATE('{time_str}'),1,'{guid}',LAST_INSERT_ID(),'{content}',str_to_date('{time_str}', '%Y-%m-%d %H:%i:%s'))"

        return (news_info, news_content)
