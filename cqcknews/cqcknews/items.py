# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CqcknewsItem(scrapy.Item):
    # 新闻地区
    city = scrapy.Field()
    # 新闻标题
    title = scrapy.Field()
    # 新闻原链接
    link = scrapy.Field()
    # 新闻作者
    author = scrapy.Field()
    # 新闻内容
    content = scrapy.Field()
    # 新闻发布时间
    time = scrapy.Field()
    # 新闻封面图
    cover = scrapy.Field()
