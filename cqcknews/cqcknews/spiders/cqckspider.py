import scrapy
import bs4
import json
from cqcknews.items import CqcknewsItem
from bs4 import BeautifulSoup
from scrapy.http import Request  # 一个单独的request的模块，需要跟进URL的时候，需要用它

#TODO:爬虫异常日志
class dayu_spider(scrapy.Spider):
    '''重庆大渝网新闻爬虫类'''
    name = 'cqcknews'  # entrypoint调试入口
    allowed_domains = ['cq.qq.com']
    base_url = 'https://cq.qq.com/'

    def start_requests(self):
        yield Request(self.base_url, callback=self.get_city_list)

    def get_city_list(self, response):
        '''获取首页城市列表'''
        soup = BeautifulSoup(response.text, 'lxml')
        for tag in soup.find(class_='other-city').children:
            if isinstance(tag, bs4.element.Tag):
                yield Request(tag.attrs['href'], callback=self.get_city_more, meta={'city': tag.string})

    def get_city_more(self, response):
        '''获取该区域城市的更多新闻'''
        soup = BeautifulSoup(response.text, 'lxml')
        more_a = soup.find(class_='news-word')
        if not more_a:
            more_a = list(soup.find(class_='lm-tit').children)[3]
        link_more = more_a.attrs["href"]

        yield Request(link_more, callback=self.get_city_link, meta=response.meta)

    def get_city_link(self, response):
        '''获取该区域全部的新闻链接'''
        city = response.meta['city']
        soup = BeautifulSoup(response.text, 'lxml')
        for link in list(soup.find(id='PageSet').find_all(name='a', class_='black')):
            if isinstance(link, bs4.element.Tag):
                yield Request('https://cq.qq.com' + link.attrs["href"], callback=self.get_news,
                              meta={'city': city, 'title': link.get_text()})

    def get_news(self, response):
        '''获取新闻'''
        title = response.meta['title']
        city = response.meta['city']
        soup = BeautifulSoup(response.text, 'lxml')
        news_g = soup.find(id='Cnt-Main-Article-QQ').descendants
        time_tag = soup.find(name='span', attrs={'class': 'article-time'})
        time = time_tag.get_text() if time_tag else ''
        author_1 = soup.find(name='span', attrs={'class': 'color-a-1'})
        author_2 = soup.find(name='span', attrs={'class': 'color-a-3'})
        author = author_1.get_text() if author_1 else '' + author_2.get_text() if author_2 else ''

        news = ''
        cover_list = []
        for p in list(news_g):
            if p.name == 'img':
                if p.attrs['src'].find('http') < 0:
                    img_src = 'https:' + p.attrs['src']
                    p_str = str(p).replace('//', 'https://', 1)
                else:
                    img_src = p.attrs['src']
                    p_str = str(p)
                cover_list.append(img_src)
            else:
                p_str = str(p)
            news += p_str

        item = CqcknewsItem()
        item['title'] = title
        item['city'] = city
        item['link'] = response.url
        item['author'] = author
        item['time'] = time
        item['content'] = news
        item['cover'] = json.dumps(cover_list, ensure_ascii=False)
        item['province'] = '重庆'

        yield item


class fuling_spider(scrapy.Spider):
    '''涪陵公交网新闻爬虫类'''
    # name = 'cqcknews'  # entrypoint调试入口
    allowed_domains = ['fuling.gongjiao.com']
    base_url = 'http://fuling.gongjiao.com/new_18128'
    link_list = []

    def start_requests(self):
        yield Request(self.base_url, callback=self.get_news_links)

    def get_news_links(self, response):
        '''获取全部新闻链接'''

        soup = BeautifulSoup(response.text, 'html.parser')
        li = soup.find(name='div', attrs={'class': 'm-widget-bd'}).ul.children
        li_list = list(li)
        for item in li_list:
            if isinstance(item, bs4.element.Tag):
                self.link_list.append(item.a['href'])

        for link in self.link_list:
            yield Request(link, callback=self.get_news)

    def get_news(self, response):
        '''获取新闻内容'''

        soup = BeautifulSoup(response.text, 'lxml')
        soup.prettify()

        meta_desc = soup.find(name='meta', attrs={'name': 'description'})
        # description = meta_desc["content"] if meta_desc["content"] else ''
        # keywords = meta_desc["content"] if meta_desc.find_next_sibling()["content"] else ''

        article = soup.find(name='div', attrs={'class': 'article'})
        title = article.h1.string.strip()
        time_str = article.find(class_='metas').string.strip()
        p_nodes = list(article.find(class_='content').find_all('p'))
        str = ''
        for p in p_nodes:
            if p.string:
                str += p.string.replace(u'\u3000', u'')
        item = CqcknewsItem()
        item['title'] = title
        item['city'] = '涪陵'
        item['link'] = response.url
        item['author'] = '涪陵公交网'
        item['time'] = time_str
        item['content'] = str
        item['cover'] = ''
        item['city_type'] = '重庆城区'
        item['province'] = '重庆'

        yield item
