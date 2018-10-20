# coding:utf-8
from  NewsMessage import  NewsMessage
import time
from lxml import etree
from Xpath import *
from NewsComment import NewsComment
from Pipe import MongoDB
import requests
import json
import  math
import  urllib2
import  MySQLdb
import re
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class ReNews(object):
    def __init__(self):
        self.comment = NewsComment()
        self.mongo = MongoDB()
        self.conn = MySQLdb.connect('localhost', 'root', '1995', 'newsurl',charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()
        self.message = NewsMessage()

    def process(self):
       insert_sql = """
                              select * from news1"""
       delete_sql = """delete from news1 where url = %s"""
       update_sql = """update news1 set ping_lun_shu_liang = %s where url = %s"""
       self.cursor.execute(insert_sql)
       data = self.cursor.fetchall()
       for ds in data:
          comment_number = self.message.getCommentNumber(ds[0],ds[1])
          ping_lun_shu_liang = comment_number[1]
          if (ping_lun_shu_liang == ds[2]):
              self.cursor.execute(delete_sql,ds[0])
              self.conn.commit()
          else:
             self.cursor.execute(update_sql,(ping_lun_shu_liang,ds[0]))
             self.conn.commit()
             url =  ds[0]
             req = urllib2.Request(url)
             try:
                 urllib2.urlopen(req)
             except urllib2.URLError, e:
                 if hasattr(e, "reason"):
                     print e.reason
                     continue
             print  url
             re_ = 'http://sports.sohu.com/\d*?/[n]\d*?.shtml'

             if (re.match(re_, url)):
                 html = ''
                 flag = 1
                 while 1:
                     try:
                         html = requests.get(url, timeout=30)
                         html.encoding = 'gb2312'
                         break
                     except Exception as e:
                         flag += 1
                         print e
                     if flag > 10:
                         return

                 soup = BeautifulSoup(html.text, 'html.parser')

                 re_ = '.*[n](\d*?).shtml'
                 _id = re.match(re_, url).group(1)
                 # print _id

                 """这一段代码是用来获取阅读数和评论数的"""
                 comment_number = self.getCommentNumber(url, _id)
                 if comment_number:
                     yue_du_shu = comment_number[0]
                     ping_lun_shu_liang = comment_number[1]
                 else:
                     yue_du_shu = 0
                     ping_lun_shu_liang = 0

                 message_dict = dict()
                 ping_dic = dict()

                 # 抓取时间
                 do_time = time.time()
                 message_dict['do_time'] = do_time

                 #self.update.process_item(ping_dic)

                 print json.dumps(message_dict, ensure_ascii=False, indent=4)
                 # self.mongo.put_content(message_dict)

                 flag1 = 0
                 if ping_lun_shu_liang > 0:
                     all_page = int(math.ceil(ping_lun_shu_liang / 10.0))
                     for page in xrange(1, all_page + 1):
                         try:
                             self.comment.run(url, _id, page)
                         except Exception as e:
                             print e
                             flag1 += 1
                             if (flag1 > 2):
                                 return False
                             else:
                                 return self.comment.run(url, _id, page)
             else:
                 html1 = ''
                 flag = 1
                 while 1:
                     try:
                         html1 = requests.get(url, timeout=30)
                         html1.encoding = 'utf-8'
                         break
                     except Exception as e:
                         flag += 1
                         print e
                     if flag > 10:
                         return
                 tree = etree.HTML(html1.text)
                 soup = BeautifulSoup(html1.text, 'html.parser')
                 re_ = "http://www.sohu.com/a/(\d*?)\_"

                 _id = soup.select("#mp-comment")[0]['sid'].encode("utf-8")
                 if (int(_id) == 0):
                     _id = 'mp_' + re.search(re_, url).group(1)
                     print _id



                 """这一段代码是用来获取阅读数和评论数的"""
                 comment_number = self.getCommentNumber(url, _id)
                 if comment_number:
                     yue_du_shu = comment_number[0]
                     ping_lun_shu_liang = comment_number[1]
                 else:
                     yue_du_shu = 0
                     ping_lun_shu_liang = 0


                 message_dict = dict()
                 ping_dic = dict()

                 # 抓取时间
                 do_time = time.time()
                 message_dict['do_time'] = do_time

                 print json.dumps(message_dict, ensure_ascii=False, indent=4)

                 # self.mongo.put_content(message_dict)
                 flag2 = 0
                 if ping_lun_shu_liang > 0:
                     all_page = int(math.ceil(ping_lun_shu_liang / 10.0))
                     for page in xrange(1, all_page + 1):
                         try:
                             self.comment.run(url, _id, page)
                         except Exception as e:
                             print e
                             flag2 += 1
                             if (flag2 > 2):
                                 continue
                             else:
                                 return self.comment.run(url, _id, page)

    def getCommentNumber(self, news_url, _id):

              comment_url = 'http://apiv2.sohu.com/api/topic/load?page_size=10' \
                            '&topic_source_id=%s&page_no=1&hot_size=5&topic_url=%s' % (_id, news_url)
              json_object = dict()
              flag = 1
              while 1:
                  try:
                      json_object = json.loads(requests.get(comment_url, timeout=30).content)

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
   news = ReNews()
   news.process()
