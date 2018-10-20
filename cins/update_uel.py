# # coding: utf-8
# import MySQLdb
#
# class   update_uel(object):
#     def __init__(self):
#         self.conn = MySQLdb.connect('localhost','root','1995','newsurl' ,use_unicode=True)
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item):
#         select_sql = """select url from news where url = %s"""
#         data = self.cursor.execute(select_sql,item['url'] )
#         print data
#         self.conn.commit()
#
#         if (data==0):
#                 insert_sql = """
#                              insert into news(url,_id,ping_lun_shu_liang) value (%s, %s, %s)"""
#                 self.cursor.execute(insert_sql, (item['url'], item['_id'], item['ping_lun_shu_liang']))
#
#                 self.conn.commit()
#                 print  "插入成功"
#         else:
#                return
#
# if __name__ == '__main__':
#     sd = update_uel()
#     sd.process_item('http://sports.sohu.com/20170724/n503681274.shtml')