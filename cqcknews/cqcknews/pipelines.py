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
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=3306)
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
        #f-string
        news_info = f"insert into news_info(create_time,del_flag,string_id,source_way,status,put_area,news_type,news_from,news_time,title,surface_plot,view_count,click_count,view_status)" \
            f"values (DATE('{time_str}'),1,'{guid}','爬虫采集',1,'{city}',10000,'{link}',DATE('{news_time}'),'{title}','{cover}',0,0,1)"
        news_content = f"insert into news_content(create_time,del_flag,string_id,news_id,news_content,update_time,reserved_1)" \
            f"values (DATE('{time_str}'),1,'{guid}',LAST_INSERT_ID(),'{content}',DATE('{time_str}'),'{author}')"

        return (news_info, news_content)
