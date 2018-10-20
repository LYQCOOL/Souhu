# coding:utf-8
import time
from lxml import etree
from Xpath import *
from NewsComment import NewsComment
# from  update_uel import update_uel
from Pipe import MongoDB
import requests
import NewsUrl
import json
import math
import urllib2
# import  MySQLdb
import re
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class NewsMessage(object):
    def __init__(self):
        self.comment = NewsComment()
        self.mongo = MongoDB()
        # self.update = update_uel()
        # self.conn = MySQLdb.connect('localhost', 'root', '1995', 'newsurl', charset='utf8', use_unicode=True)
        # self.cursor = self.conn.cursor()

    def getNewsMessage(self):
        count = 0
        for news_url in NewsUrl.Run():
            req = urllib2.Request(news_url)
            try:
                urllib2.urlopen(req)
            except urllib2.URLError, e:
                if hasattr(e, 'code'):
                    print 'Error code: ', e.code
                elif hasattr(e, 'reason'):
                    print 'Reason: ', e.reason
                continue

            re_ = 'http://sports.sohu.com/\d*?/[n]\d*?.shtml'
            if (re.match(re_, news_url)):
                print  news_url
                html = ''
                flag = 1
                while 1:
                    try:
                        html = requests.get(news_url, timeout=30)
                        html.encoding = 'gb2312'
                        break
                    except Exception as e:
                        flag += 1
                        print e
                    if flag > 10:
                        return

                soup = BeautifulSoup(html.text, 'html.parser')
                re_ = '.*[n](\d*?).shtml'
                _id = re.match(re_, news_url).group(1)
                title = soup.find_all('title')[0].text
                if (title == "404,您访问的页面已经不存在!"):
                    continue
                """这一段代码是用来获取阅读数和评论数的"""
                comment_number = self.getCommentNumber(news_url, _id)
                if comment_number:
                    yue_du_shu = comment_number[0]
                    ping_lun_shu_liang = comment_number[1]
                else:
                    yue_du_shu = 0
                    ping_lun_shu_liang = 0
                # select_sql = """
                #               select ping_lun_shu_liang from news where url = %s"""
                # if (self.cursor.execute(select_sql, news_url)):
                #     data = self.cursor.fetchone()
                #     # print  data[0]
                #     if (data[0] == ping_lun_shu_liang):
                #         continue
                # else:
                message_dict = dict()
                ping_dic = dict()
                # 发布时间


                # shijian1 = tiongoe.strftime('%Y-%m-%d', time.localtime(time.time() - 2 * 24 * 60 * 60))
                shijian = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                fa_bu_shi_jian = soup.find_all(id='pubtime_baidu')[0].text
                if (not re.search(shijian, fa_bu_shi_jian)):
                    continue

                message_dict['fa_bu_shi_jian'] = fa_bu_shi_jian
                # print fa_bu_shi_jian

                # 文章网址
                wen_zhang_wang_zhi = news_url
                message_dict['wen_zhang_wang_zhi'] = wen_zhang_wang_zhi

                # 文章标题
                wen_zhang_biao = soup.title.string.encode('utf-8')
                # print wen_zhang_biao
                wen_ = '(.*?)\-.*?'
                wen_zhang_biao_ti = re.search(wen_, wen_zhang_biao).group(1)
                # print  wen_zhang_biao_ti
                message_dict['wen_zhang_biao_ti'] = wen_zhang_biao_ti

                # 评论数量
                ping_lun_shu_liang = ping_lun_shu_liang
                message_dict['ping_lun_shu_liang'] = ping_lun_shu_liang

                # 文章来源

                wen_zhang_lai_yuan = soup.find_all(id="media_span")[0].text.encode('utf-8')

                message_dict['wen_zhang_lai_yuan'] = wen_zhang_lai_yuan

                # 文章正文
                li = []
                for i in soup.select("div#contentText"):
                    for wen_zhang_zheng_wen in i.select('p'):
                        li.append(wen_zhang_zheng_wen.text.encode('utf-8'))
                message_dict['wen_zhang_zheng_wen'] = ",".join(li)

                # 抓取时间
                do_time = time.time()
                message_dict['do_time'] = do_time

                # 抓取网站
                zhan_dian = u'搜狐网'
                message_dict['zhan_dian'] = zhan_dian

                # 图片链接n
                tu_pian_lian_jie = None
                message_dict['tu_pian_lian_jie'] = tu_pian_lian_jie

                # 文章栏目
                wen_zhang_lan_mu = u'搜狐体育' + soup.select("div#mypos")[0].text.encode('utf-8')

                try:
                    message_dict['wen_zhang_lan_mu'] = wen_zhang_lan_mu.replace('>', '->')
                except Exception as e:
                    print e
                    message_dict['wen_zhang_lan_mu'] = wen_zhang_lan_mu

                # 文章作者
                wen_zhang_zuo_zhe = soup.find_all(id="author")[0].text.encode('utf-8')
                message_dict['wen_zhang_zuo_zhe'] = wen_zhang_zuo_zhe

                # 关键词
                guan_jian_ci = None
                message_dict['guan_jian_ci'] = guan_jian_ci

                # 相关标签
                xiang_guan_biao_qian = None
                message_dict['xiang_guan_biao_qian'] = xiang_guan_biao_qian

                # 阅读数量
                yue_du_shu = yue_du_shu
                message_dict['yue_du_shu'] = yue_du_shu

                # 主键
                message_dict['_id'] = _id + '|_|' + news_url

                count += 1
                # print count
                ping_dic['url'] = news_url
                ping_dic['_id'] = _id
                ping_dic['ping_lun_shu_liang'] = ping_lun_shu_liang
                # self.update.process_item(ping_dic)

                # print json.dumps(message_dict, ensure_ascii=False, indent=4)
                self.mongo.put_content(message_dict)

                flag1 = 0
                if ping_lun_shu_liang > 0:
                    all_page = int(math.ceil(ping_lun_shu_liang / 10.0))
                    for page in xrange(1, all_page + 1):
                        try:
                            self.comment.run(news_url, _id, page)
                        except Exception as e:
                            print e
                            self.comment.run(news_url, _id, page)
                            continue
            else:
                print  news_url
                html1 = ''
                flag = 1
                while 1:
                    try:
                        html1 = requests.get(news_url, timeout=30)
                        html1.encoding = 'utf-8'
                        break
                    except Exception as e:
                        flag += 1
                        print e
                    if flag > 10:
                        return
                tree = etree.HTML(html1.text)
                soup = BeautifulSoup(html1.text, 'html.parser')
                # print soup.text
                re_ = "http://www.sohu.com/a/(\d*?)\_"
                title = soup.find_all('title')[0].text
                if (title == "404,您访问的页面已经不存在!"):
                    continue
                # print soup.select("#mp-comment")
                if (soup.select("#mp-comment") != []):
                    _id = soup.select("#mp-comment")[0]['sid'].encode("utf-8")
                    # print _id
                    if (int(_id) == 0):
                        _id = 'mp_' + re.search(re_, news_url).group(1)
                else:
                    continue
                """这一段代码是用来获取阅读数和评论数的"""
                comment_number = self.getCommentNumber(news_url, _id)
                if comment_number:
                    yue_du_shu = comment_number[0]
                    ping_lun_shu_liang = comment_number[1]
                else:
                    yue_du_shu = 0
                    ping_lun_shu_liang = 0
                # select_sql = """  select ping_lun_shu_liang from news where url = %s"""
                # if(self.cursor.execute(select_sql, news_url)):
                #     data = self.cursor.fetchone()
                #     #print  data[0]
                #     if (data[0] == ping_lun_shu_liang):
                #         continue
                # else:

                message_dict = dict()
                ping_dic = dict()
                # 发布时间
                shijian = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                try:
                    fa_bu_shi_jian = soup.select('span#news-time')[0].text
                except:
                    fa_bu_shi_jian=soup.select('span.time')[0].text
                if (not re.search(shijian, fa_bu_shi_jian)):
                    continue

                message_dict['fa_bu_shi_jian'] = fa_bu_shi_jian
                # 文章网址
                wen_zhang_wang_zhi = news_url
                message_dict['wen_zhang_wang_zhi'] = wen_zhang_wang_zhi

                # 文章标题
                wen_zhang_biao = soup.title.string.encode('utf-8')
                wen_ = '(.*?)\_.*?'
                try:
                    wen_zhang_biao_ti = re.search(wen_, wen_zhang_biao).group(1)
                    message_dict['wen_zhang_biao_ti'] = wen_zhang_biao_ti
                except:
                    message_dict['wen_zhang_biao_ti'] = "无"

                # 评论数量
                ping_lun_shu_liang = ping_lun_shu_liang
                message_dict['ping_lun_shu_liang'] = ping_lun_shu_liang

                # 文章来源
                try:
                    wen_zhang_lai_yuan = soup.select("#user-info h4 a")[0].text.encode('utf-8')
                    message_dict['wen_zhang_lai_yuan'] = wen_zhang_lai_yuan
                except:
                    message_dict['wen_zhang_lai_yuan'] = "空"

                # 文章正文
                li = []
                for i in soup.select("article.article"):
                    for wen_zhang_zheng_wen in i.select('p'):
                        li.append(wen_zhang_zheng_wen.text.encode('utf-8'))
                message_dict['wen_zhang_zheng_wen'] = ','.join(li)
                # 抓取时间
                do_time = time.time()
                message_dict['do_time'] = do_time

                # 抓取网站
                zhan_dian = u'搜狐网'
                message_dict['zhan_dian'] = zhan_dian

                # 图片链接
                if (not soup.select('.article img')):
                    tu_pian_lian_jie = None
                    message_dict['tu_pian_lian_jie'] = tu_pian_lian_jie
                else:
                    tu_pian = soup.select('.article img')
                    tu = []
                    for tu_pian_lian_jie in tu_pian:
                        if (not re.search('http', tu_pian_lian_jie['src'])):
                            tu.append("http:" + tu_pian_lian_jie['src'])

                        else:
                            tu.append(tu_pian_lian_jie['src'])
                    message_dict['tu_pian_lian_jie'] = " ".join(tu)

                # 文章栏目
                try:
                    wen_zhang_lan_mu = soup.select(".location.area")[0].text.encode('utf-8')
                except:
                    wen_zhang_lan_mu=""
                try:
                    message_dict['wen_zhang_lan_mu'] = wen_zhang_lan_mu.replace('>', '->')
                except Exception as e:
                    print e
                    message_dict['wen_zhang_lan_mu'] = wen_zhang_lan_mu

                # 文章作者
                wen_zhang_zuo_zhe = None
                message_dict['wen_zhang_zuo_zhe'] = wen_zhang_zuo_zhe

                # 关键词
                guan_jian_ci = None
                message_dict['guan_jian_ci'] = guan_jian_ci

                # 相关标签
                xiang_guan_biao_qian = None
                message_dict['xiang_guan_biao_qian'] = xiang_guan_biao_qian

                # 阅读数量
                yue_du_shu = yue_du_shu
                message_dict['yue_du_shu'] = yue_du_shu

                # 主键
                message_dict['_id'] = _id + '|_|' + news_url

                count += 1

                # print count
                ping_dic['url'] = news_url
                ping_dic['_id'] = _id
                ping_dic['ping_lun_shu_liang'] = ping_lun_shu_liang
                # self.update.process_item(ping_dic)

                # print json.dumps(message_dict, ensure_ascii=False, indent=4)

                self.mongo.put_content(message_dict)
                flag2 = 0
                if ping_lun_shu_liang > 0:
                    all_page = int(math.ceil(ping_lun_shu_liang / 10.0))
                    for page in xrange(1, all_page + 1):
                        try:
                            self.comment.run(news_url, _id, page)
                        except Exception as e:
                            print e
                            self.comment.run(news_url, _id, page)
                            continue

    def getCommentNumber(self, news_url, _id):
        # comment_url = 'http://apiv2.sohu.com/api/topic/load?page_size=10' \
        #               '&topic_source_id=%s&page_no=1&hot_size=5&topic_url=%s&source_id=%s' % (_id, news_url,_id)
        if news_url.endswith('shtml'):
            pass
        else:
            tow_ids = news_url.split('/')[-1].split('_')
            media_id = tow_ids[1]
            source_id = tow_ids[0]
            comment_url = 'http://apiv2.sohu.com/api/topic/load?callback=jQuery1124008187733188312629_1539945526218&page_size=10' \
                          '&topic_source_id=%s&page_no=1&media_id=%s&source_id=mp_%s' % (_id, media_id, source_id)
            flag = 1
            while 1:
                try:
                    #把评论转化为json格式
                    comments = requests.get(comment_url, timeout=30).content
                    # json_object = json.loads(requests.get(comment_url, timeout=30).content)
                    json_object=json.loads(re.match('.*218\((.*?)\);',comments).group(1))
                    break
                except Exception as e:
                    flag += 1
                    print "获取评论错误：", e

                if flag > 5:
                    return


                    # 阅读数
            if (json_object[u"jsonObject"].has_key(u'participation_sum') == False):
                yue_du_shu = None
            else:
                yue_du_shu = json_object[u"jsonObject"][u'participation_sum']
                # 评论数
            if (json_object[u"jsonObject"].has_key(u'cmt_sum') == False):
                ping_lun_shu_liang = 0
            else:
                ping_lun_shu_liang = json_object[u"jsonObject"][u'outer_cmt_sum']

            return yue_du_shu, ping_lun_shu_liang


if __name__ == '__main__':
    newMessage = NewsMessage()
    while 1:
        newMessage.getNewsMessage()
        print "休眠5小时"
        time.sleep(60 * 60 * 5)
