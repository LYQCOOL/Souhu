# coding: utf-8
import json
import time
from Pipe import MongoDB
import requests
import re


class NewsComment(object):
    def __init__(self):
        self.mongo = MongoDB()

    def run(self, news_url, _id, page):
        # comment_url = 'http://apiv2.sohu.com/api/topic/load?page_size=10' \
        #                '&topic_source_id=%s&page_no=1&hot_size=5&topic_url=%s&source_id=%s' % (_id,news_url,_id)
        if news_url.endswith('shtml'):
            pass
        else:
            tow_ids = news_url.split('/')[-1].split('_')
            media_id = tow_ids[1]
            source_id = tow_ids[0]
            comment_url = 'http://apiv2.sohu.com/api/topic/load?callback=jQuery1124008187733188312629_1539945526218&page_size=10' \
                          '&topic_source_id=%s&page_no=1&media_id=%s&source_id=mp_%s' % (_id, media_id, source_id)
            # print comment_url
            json_object = dict()
            flag = 1
            while 1:
                try:
                    # json_object = json.loads(requests.get(comment_url, timeout=30).content)
                    comments=requests.get(comment_url,timeout=30).content
                    json_object = json.loads(re.match('.*218\((.*?)\);', comments).group(1))
                    break
                except Exception as e:
                    flag += 1
                    print "获取评论错误：", e

                if flag > 5:
                    return
                count = 0
            if (json_object[u'jsonObject'].has_key(u'topic_id') == False):
                print "暂时无法获取topic_id"

            else:
                item = json_object[u'jsonObject'][u'topic_id']

                # comment_URL = 'http://apiv2.sohu.com/api/comment/list?page_size=10&topic_id=%s&page_no=%d&source_id=%s' % (item, page,_id)
                comment_URL = 'http://apiv2.sohu.com/api/topic/load?callback=jQuery1124008187733188312629_1539945526218&page_size=10' \
                              '&topic_id=%s&page_no=%s&media_id=%s&source_id=mp_%s' % (item, page, media_id, source_id)
                Json_object = dict()
                comment_dict = dict()
                flag = 1
                while 1:
                    try:
                        # json_object = json.loads(requests.get(comment_url, timeout=30).content)
                        comments = requests.get(comment_URL, timeout=30).content
                        Json_object = json.loads(re.match('.*218\((.*?)\);', comments).group(1))
                        break
                    except Exception as e:
                        flag += 1
                        print "获取评论错误：", e

                    if flag > 5:
                        return

                count = 0
                for item in Json_object[u'jsonObject'][u'comments']:

                    # 评论文章url
                    news_url = news_url

                    # 评论内容
                    ping_lun_nei_rong = item["content"]
                    comment_dict['ping_lun_nei_rong'] = ping_lun_nei_rong

                    # 评论时间
                    ping_lun_shi_jian = item["create_time"]
                    comment_dict['ping_lun_shi_jian'] = ping_lun_shi_jian

                    # 回复数量
                    hui_fu_shu = item["reply_count"]
                    comment_dict['hui_fu_shu'] = hui_fu_shu

                    # 点赞数量
                    dian_zan_shu = item["support_count"]
                    comment_dict['dian_zan_shu'] = dian_zan_shu

                    # 评论id
                    ping_lun_id = item["comment_id"]
                    comment_dict['ping_lun_id'] = ping_lun_id

                    # 用户昵称
                    if (item[u'passport'].has_key(u'nickname') == False):
                        yong_hu_ming = None
                    else:
                        yong_hu_ming = item[u'passport']["nickname"]
                    comment_dict['yong_hu_ming'] = yong_hu_ming
                    # 性别
                    xing_bie = None
                    comment_dict['xing_bie'] = xing_bie

                    # 用户等级
                    yong_hu_deng_ji = None
                    comment_dict['yong_hu_deng_ji'] = yong_hu_deng_ji

                    # 用户省份
                    yong_hu_sheng_fen = item["ip_location"]
                    comment_dict['yong_hu_sheng_fen'] = yong_hu_sheng_fen

                    # 抓取时间
                    do_time = time.time()
                    comment_dict['do_time'] = do_time

                    # 抓取网站
                    zhan_dian = u'搜狐网'
                    comment_dict['zhan_dian'] = zhan_dian

                    # 主键
                    comment_dict['_id'] = str(ping_lun_id) + '|_|' + news_url
                    #
                    count += 1
                    # print json.dumps(comment_dict, ensure_ascii=False, indent=4)
                    self.mongo.put_comment(comment_dict)


if __name__ == '__main__':
    comment = NewsComment()
    for i in range(1, 2):
        comment.run('http://www.sohu.com/a/160690501_114941', '0', i)
