

import urllib3
import itertools
import os
import time

from bs4 import BeautifulSoup

bbc_br = 'https://www.bbc.com/portuguese'

def get_page(url):
    http_doc = urllib3.PoolManager()
    response = http_doc.request('GET', url)
    if response.status != 200:
        print("Erro de carregamento na página. Você está conectado?")
        return
    return response.data

def parse_url(url):
    http_doc = get_page(url)
    http_doc_info = BeautifulSoup(http_doc, 'html.parser')
    return http_doc_info

def get_page_links(url):
    http_doc_info = parse_url(url)
    for link in http_doc_info.find_all('a'):
        yield link.get('href')

def get_page_info(url, html_tag):
    http_doc_info = parse_url(url)
    for item in http_doc_info.find_all(html_tag):
        yield item


def get_bbc_news_fulltext(url, html_tag='a'):
    http_doc_info = parse_url(url)
    info = ''
    for paragrafo in http_doc_info.find_all('p'):
        info += paragrafo.get_text() + os.linesep*2
    info = info.split('Já assistiu aos nossos novos vídeos no YouTube? Inscreva-se no nosso canal!')[0]
    info = info.split('Estes são links externos e abrirão numa nova janela')[1]
    return info


def get_bbc_news(url, html_tag='a', target_folder=''):
    http_doc_info = get_page_info(url, html_tag)

    n = itertools.count()

    for selected_info in http_doc_info:
        sub_selected_session = selected_info.find_all('h3')
        
        for sub_selected_info in sub_selected_session:
            headline = sub_selected_info.get_text().strip()
            link = selected_info.get('href').strip()
            link = bbc_br.replace('/portuguese', link) 
            ignore_text = False

            try:
                fulltext_data = get_bbc_news_fulltext(link)
            except urllib3.exceptions.MaxRetryError:
                ignore_text = True

            

            with open(target_folder+'noticias_{}.txt'.format(next(n)), 'w') as f:
                f.write(headline+os.linesep)
                f.write(link+os.linesep*3)
                if not ignore_text:
                    f.write(fulltext_data)
            
            time.sleep(15)


