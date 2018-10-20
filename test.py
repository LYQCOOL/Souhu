# _*_ encoding:utf-8 _*_
from bs4 import BeautifulSoup
import requests
content=requests.get('https://www.sohu.com/picture/260187395').content
soup=BeautifulSoup(content,'lxml')
print soup.select()

