"""
    电影爬虫程序:
        1.douban : https://movie.douban.com/explore
        2.获取电影信息并存入数据库
"""

import requests
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime
import re

PASSWORD = '7758521'
url_begin = "https://movie.douban.com/j/search_subjects"
headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
           'Accept - Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
           'Connection': 'Keep-Alive',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}


def begin_crawl(pages=1, url=url_begin):
    movies = []
    for page in range(pages):
        params = {
            'type': 'movie',
            'tag': '热门',
            'sort': 'recommend',
            'page_limit': '20',
            'page_start': '{}'.format(page * 20)
        }

        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()

        for movie in response.json()['subjects']:
            movie_msg = {}  # movie info
            user_msg = []  # user and comments info

            movie_msg['score'] = movie.get('rate')
            movie_msg['title'] = movie.get('title')
            movie_msg['details_url'] = movie.get('url')  # 不是电影播放地址,是电影详情页面地址
            movie_msg['movie_picture'] = movie.get('cover')

            get_movie_details(movie_msg, user_msg)
            movies.append({"movie_msg": movie_msg, "user_msg": user_msg})
            # 把数据全部插到数据库中
            # print("{:*^80}".format(movie_msg['title']))
            # print('movie title:\t', movie_msg['title'])
            # print('score:\t', movie_msg['score'])
            # print("movie_url:\t", movie_msg['movie_url'])
            # print("tags:\t", movie_msg['tags'])
            #
            # print("comments:\n")
            # for index, user in enumerate(user_msg, 1):
            #     print(index, '\t', user.get('username'), '\t', user.get('comment'), '\t', user.get('timestamp'))
            # print("\n\n\n")
    return movies


def get_movie_details(movie_msg, user_msg):
    details_url = movie_msg.get('details_url')

    response = requests.get(url=details_url, headers=headers)
    response.raise_for_status()

    html = etree.HTML(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取电影的详细信息

    movie_msg['director'] = html.xpath('//a[@rel="v:directedBy"]/text()')
    movie_msg['tags'] = html.xpath('//div[@id="info"]/span[@property="v:genre"]/text()')
    movie_msg['year'] = html.xpath('//div[@id="info"]/span[@property="v:initialReleaseDate"]/text()')
    movie_msg['time'] = html.xpath('//div[@id="info"]/span[@property="v:runtime"]/text()')
    movie_msg['summary'] = html.xpath('//span[@property="v:summary"]/text()')[0].strip()
    finally_url = html.xpath('//li[@class="label-trailer"]/a[@class="related-pic-video"]/@href')

    # actors = html.xpath('//span[@class="attrs"]/span/a[@rel]')    why it is unuseful? fucking you!!!
    actors = []
    for i in soup.find("span", class_="actor").find("span", class_="attrs").find_all("a"):
        actors.append(i.string)
    movie_msg['actors'] = actors

    pattern = '制片国家/地区:</span>(.*?)<br/>.*>语言:</span>(.*?)<br/>'  # 网页上是<br>，但是这里必须写<br/>才能匹配
    try:
        result = re.search(pattern, response.text, re.M | re.S).groups()
        movie_msg['country'] = result[0]
        movie_msg['language'] = result[1]
    except:
        movie_msg['country'] = "我也不知道呀！"
        movie_msg['language'] = "你来看啊(滑稽)"

    if finally_url:
        get_movie_comment(movie_msg, user_msg, finally_url[0])
    else:
        movie_msg['movie_url'] = "../static/video/htpy.mp4"
    # 电影信息获取结束


def get_movie_comment(movie_msg, user_msg, finally_url):
    response = requests.get(url=finally_url, headers=headers)
    response.raise_for_status()
    text = response.text.replace('<br/>', '\n')  # 评论中的多行内容(被<br/>分开)，可以被匹配
    # text = response.text
    html = etree.HTML(text)
    movie_msg['movie_url'] = html.xpath('//source[@type="video/mp4"]/@src')[0]

    # 获取用户和评论的信息
    head_picture = html.xpath('//div[@id="comments"]/div/div[1]/a/img/@src')
    username = html.xpath('//div[@id="comments"]/div/div[1]/a/img/@alt')
    timestamp = datetime.utcnow()
    body = html.xpath('//div[@id="comments"]/div/div[2]/p/text()')

    for h, u, b in zip(head_picture, username, body):
        user_ = {}
        user_['head_picture'] = h
        user_['username'] = u
        user_['password'] = PASSWORD
        user_['timestamp'] = timestamp
        user_['comment'] = b
        user_msg.append(user_)


begin_crawl()
