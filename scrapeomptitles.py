from bs4 import BeautifulSoup
import yaml 
import requests 


url = 'http://www.langsci-press.org/catalog' 
html = requests.get(url).text

soup = BeautifulSoup(html, 'html.parser')

monographs =  [m.find('a','title').text.strip()+' -- '+m.find('div').text.strip() for m in soup.find_all(class_='obj_monograph_summary')]
[m.find('a','title').text.strip()+' -- '+m.find('div').text.strip() for m in soup.find_all(class_='obj_monograph_summary')]
for i in sorted(monographs):
  print(i,'\n')


