# coding: utf-8
import re
import requests
import  json


def Run():
    html = ''
    sport = 'http://sports.sohu.com/'
    yule = 'http://yule.sohu.com/'
    _dict = [sport, yule]

    for URL in _dict:
        while 1:
            try:
                html = requests.get(URL, timeout=30).content
                break
            except Exception as e:
                print e
        re_ = '//www.sohu.com/a/[0-9]*?\_[0-9]*|//sports.sohu.com/\d*?/[n]\d*?.shtml'
        news_url_list = re.findall(re_, html)

        for news_url in set(news_url_list):
            yield 'http:' + news_url
    json_object = dict()
    _dic = dict()
    for i in range(1, 20):
        url = 'http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=43&page=%d&size=20' % i
        json_object = json.loads(requests.get(url, timeout=30).content)
        for item in json_object:
            if (item["authorName"] == u'环球网'):
                continue
            _dic["id"] = item["id"]
            _dic["authorId"] = item["authorId"]
            URL = "http://www.sohu.com/a/%s_%s" % (_dic["id"], _dic["authorId"])
            yield URL
    Json_object = dict()
    _dict = dict()
    for i in range(1, 20):
        URl = 'http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=15&page=%d&size=20' % i
        Json_object = json.loads(requests.get(URl, timeout=30).content)
        for item in Json_object:
            if (item["authorName"] == u'环球网'):
                continue
            elif(item["authorName"]==u'观察者网'):
                continue
            _dict["id"] = item["id"]
            _dict["authorId"] = item["authorId"]
            URL = "http://www.sohu.com/a/%s_%s" % (_dict["id"], _dict["authorId"])
            yield URL


class NewsUrl(object):
    def __init__(self):
       pass

if __name__ == '__main__':
    a=Run()
    # for x in a:
    #    if x.endswith('html'):
    #        print x
