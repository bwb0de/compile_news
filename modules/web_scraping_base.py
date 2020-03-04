#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import time
import requests
import urllib3
import itertools
import codecs
import os
import time
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from modules.news_pastas_de_dados import pasta_modulos
from modules.passwinfo import uid, pwd

bbc_br = 'https://www.bbc.com/portuguese'
folha = 'https://www.folha.uol.com.br'
br_de_fato = 'https://www.brasildefato.com.br/politica'
correioweb_cidades = 'https://www.correiobraziliense.com.br/cidades---df/'
correioweb_politica = 'https://www.correiobraziliense.com.br/politica/'
unb_noticias = 'http://www.noticias.unb.br/'
unb_ciencias = 'http://www.unbciencia.unb.br/ultimas'

def convert_to_readaloud():
    os.system('for FILE in $(ls); do echo "$FILE"; iconv -c -f utf-8 -t iso-8859-15 "$FILE" > "nv-$FILE"; done')


def get_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Erro de carregamento na página. Você está conectado?")
        return
    return response.text

def post_page(url):
    response = requests.get(url)
    if response.status != 200:
        print("Erro de carregamento na página. Você está conectado?")
        return
    return response.data

def get_js_page(url):
    option = Options()
    option.headless = True
    driver = webdriver.Firefox(options=option)
    driver.get(url)
    http_static_response = driver.execute_script('return document.documentElement.outerHTML')
    return http_static_response



def parse_url(url, static_url=True, html_class=False):
    if static_url:
        http_doc = get_page(url)
    else:
        http_doc = get_js_page(url)
        
    http_response_info = BeautifulSoup(http_doc, 'html.parser')

    return http_response_info


def get_page_links(url, static_url=True):
    http_response_info = parse_url(url, static_url=static_url)
    for link in http_response_info.find_all('a'):
        yield link


def get_page_info(url, html_tag):
    http_response_info = parse_url(url)
    
    selected_elements = http_response_info.find_all(html_tag)

    for item in selected_elements:
        yield item


def get_unb_news(target_folder='', encoding='utf8'):

    http_response_unb_noticias = get_page_info(unb_noticias, 'h2')
    http_response_unb_ciencia = get_page_info(unb_ciencias, 'h2')
    
    news_link = []
    
    for title in http_response_unb_noticias:
        title_info = title.get_text().strip()
        link = unb_noticias+title.find('a').get('href')[1:]
        news_link.append((title_info, link))
    
    for title in http_response_unb_ciencia:
        if title.find('a'): #.get('href'):
            title_info = title.get_text().strip()
            link = unb_ciencias+title.find('a').get('href')[1:]
            news_link.append((title_info, link))
    
    for new in news_link:
        get_unb_news_fulltext(new[0], new[1])


def get_unb_news_fulltext(title, url):
    
    http_response = get_page_info(url, 'p')
    
    for i in http_response:
        print(i.get_text().strip())
        print()
    input('PAUSAR....')




def get_bbc_news(url=bbc_br, html_tag='a', target_folder='', encoding='utf8'):
    #Necessário converter arquivos finais com 'convert_to_readaloud'...
    
    http_response_info = get_page_links(url)

    n = itertools.count()

    for selected_info in http_response_info:
        sub_selected_session = selected_info.find_all('h3')
        
        for sub_selected_info in sub_selected_session:
            title = sub_selected_info.get_text().strip()
            link = selected_info.get('href').strip()
            link = bbc_br.replace('/portuguese', link) 
            ignore_text = False

            try:
                fulltext_data = get_bbc_news_fulltext(link, encoding=encoding)
            except requests.exceptions.ConnectionError:
                ignore_text = True

            with open(target_folder+'noticias_bbc_{}.txt'.format(next(n)), 'wb') as f:
                nl = os.linesep.encode(encoding)
                title = title.encode(encoding)
                link = link.encode(encoding)

                f.write(title+nl)
                f.write(link+nl*3)
                if not ignore_text:
                    f.write(fulltext_data)


def charset_fix(text, encoding='utf8'):
    info = text
    info = info.replace('—', '---')
    info = info.replace('“', '"')
    info = info.replace('”', '"')
    info = info.replace(' – ', '---')
    info = info.replace('‘', "'")
    info = info.replace('’', "'")
    info = info.replace('…', '...')
    try:
        return info.encode(encoding)
    except UnicodeEncodeError:
        return info.encode('utf8')



def get_bbc_news_fulltext(url, html_tag='a', encoding='utf8'):
    http_response_info = parse_url(url)
    info = ''
    for paragrafo in http_response_info.find_all('p'):
        info += paragrafo.get_text() + os.linesep*2
    info = info.split('Já assistiu aos nossos novos vídeos no YouTube? Inscreva-se no nosso canal!')[0]
    info = info.split('Estes são links externos e abrirão numa nova janela')[1]
    info = charset_fix(info)
    return info



def get_folha_news_fulltext(url, title='', html_tag='a', target_folder='', news_num=0):
    http_response_info = parse_url(url)
    encoding = 'latin1'

    title_info = ''

    for t in http_response_info.find_all('h1'):
        title_info = t.get_text().strip().encode(encoding)

    url_info = url.encode(encoding)
    nl = os.linesep.encode(encoding)


    output_info = []
    output_info.append(title_info+nl)
    output_info.append(url_info+nl*3)

    for paragrafo in http_response_info.find_all('p'):

        p_info = paragrafo.get_text().strip()
        re_time_tag = re.search(r'\d\d\.\w\w\w\.\d\d\d\d\s..\s', p_info)

        if p_info.find('Assinantes podem liberar 5 acessos por dia para cont') != -1:
            pass

        elif p_info.find('Gostaria de receber as principais not') != -1:
            pass

        elif p_info.find('O site de entretenimento da Folha') != -1:
            pass

        elif p_info.find('editoriais@grupofolha.com.br') != -1:
            break

        elif p_info.find('Os artigos publicados com assinatura n') != -1:
            break

        elif re_time_tag != None:
            pass

        elif p_info.find('Copyright') != -1:
            break

        elif re.search(r'Os coment*rios n*o representam a opini*o do jornal', p_info) != None:
            break
        
        elif p_info.find('vantagens de ser assinante da Folha?') != -1:
            break

        elif p_info.find('Seu e-mail foi cadastrado com sucesso!') != -1:
            break
        
        else:
            p_info = charset_fix(p_info, encoding=encoding)
            if len(p_info) < 15:
                pass
            else:
                output_info.append(p_info+nl*2)
    
    with open(target_folder+'noticias_folha_{}.txt'.format(news_num), 'wb') as f:
        for line in output_info:
            f.write(line)
    

   
def get_folha_news(url=folha, html_tag='h2', target_folder=''):
    #Necessário converter arquivos finais com 'convert_to_readaloud'...

    http_response_info = get_page_info(url, html_tag)

    n = itertools.count()

    for selected_info in http_response_info:
        try:
            title = selected_info.get_text().strip()
            link = selected_info.parent.get('href').strip()
            ignore_text = False
        except AttributeError: 
            ignore_text = True

        if not ignore_text:
            try: get_folha_news_fulltext(link, title=title, target_folder=target_folder, news_num=next(n))
            except urllib3.exceptions.MaxRetryError: pass


    return http_response_info


def get_correioweb_news(target_folder=''):
    option = Options()
    option.headless = True
    driver = webdriver.Firefox(options=option)

    url = 'https://www.correiobraziliense.com.br/ultimas-noticias/'
    driver.get(url)
    
    http_static_response = driver.execute_script('return document.documentElement.outerHTML')
    http_static_response = BeautifulSoup(http_static_response, "html.parser")

    n = itertools.count()

    news_links = []

    for ln in http_static_response.find_all('a'):
        if ln.parent.find('h4'):
            titulo = ln.get('title').strip()
            link = ln.get('href').strip()
            news_links.append((titulo, link))

    for new in news_links:
        with open(target_folder+'noticias_correioweb_{}.txt'.format(next(n)), 'w') as f:
            f.write(new[0]+os.linesep)
            f.write(new[1]+os.linesep*3)
            new_info = parse_url(new[1])
            for paragrafo in new_info.find_all('p'):
                if paragrafo.get_text().strip() == 'Quem Somos':
                    break
                else:
                    f.write(paragrafo.get_text()+os.linesep*2)


    print(news_links)


def grab_and_decode(
        http_response,\
        encoding,\
        file_label='noticias',\
        breakers=[],\
        label_location='parent', #child, inside...
        label_tag='h3',\
        target_folder=''):
    
    n = itertools.count()

    news_links = []

    for ln in http_response:
        if label_location == 'parent':
            if ln.parent.find(label_tag):
                titulo = charset_fix(ln.parent.find(label_tag).get_text().strip(), encoding=encoding)
                link = ln.get('href').strip()
                news_links.append((titulo, link))

        elif label_location == 'child': 
            if ln.find(label_tag):
                titulo = charset_fix(ln.find(label_tag).get_text().strip(), encoding=encoding)
                link = ln.get('href').strip()
                news_links.append((titulo, link))
        
        elif label_location == 'inside':
            titulo = charset_fix(ln.get('title').strip().strip(), encoding=encoding)
            link = ln.get('href').strip()
            news_links.append((titulo, link))

    print(news_links)
    
    for new in news_links:
        with open(target_folder+'{file_label}_{n}.txt'.format(file_label=file_label, n=next(n)), 'wb') as f:
            nl = os.linesep.encode(encoding)
            link_byte = new[1].encode(encoding)
            f.write(new[0]+nl)
            f.write(link_byte+nl*3)
            new_info = parse_url(new[1])
            for paragrafo in new_info.find_all('p'):
                if paragrafo.get_text().strip() in breakers:
                    break
                elif len(paragrafo.get_text().strip()) < 15:
                    pass
                else:
                    paragrafo_info = charset_fix(paragrafo.get_text().strip(), encoding=encoding)
                    f.write(paragrafo_info+nl*2)

    return news_links



def get_br_de_fato_news(url=br_de_fato, target_folder=''):
    #Não necessário converter arquivos finais...

    http_response = get_page_links(url)
    breakers=['Quem Somos']
    target_folder=target_folder
    label_tag='h3'
    file_label='noticias_br_d_fato'

    grab_and_decode(http_response,\
        'latin1',\
        breakers=breakers,\
        target_folder=target_folder,\
        label_tag=label_tag,\
        file_label=file_label)


def get_bbc2_news(url=bbc_br, target_folder=''):
    http_response = get_page_links(url)
    breakers=['Quem Somos']
    target_folder=target_folder
    label_tag='h3'
    file_label='noticias_bbc_br'

    grab_and_decode(http_response,\
        'utf8',\
        breakers=breakers,\
        target_folder=target_folder,\
        label_tag=label_tag,\
        file_label=file_label)

    

def procurar_no_portal_da_transparencia(cpf):
    option = Options()
    option.headless = True
    driver = webdriver.Firefox(options=option)

    url = 'http://www.portaltransparencia.gov.br/busca?termo='
    driver.get(url+cpf)
    
    http_static_response = driver.execute_script('return document.documentElement.outerHTML')
    http_static_response = BeautifulSoup(http_static_response, "html.parser")
    response = http_static_response.find('ul', {'id': 'resultados'})
    elements = response.find_all('a')
    for element in elements:
        print(element.get_text())
    driver.quit()


def pop_up_consulta_irpf(cpf, data_nascimento):
    driver = webdriver.Firefox()

    url = 'http://servicos.receita.fazenda.gov.br/Servicos/ConsRest/Atual.app/paginas/mobile/restituicaoMobi.asp'

    driver.get(url)

    input_cpf = driver.find_element_by_xpath('//input[@id="cpf"]')
    input_cpf.click()
    input_cpf.send_keys(cpf)

    input_dn = driver.find_element_by_xpath('//input[@id="data_nascimento"]')
    input_dn.click()
    input_dn.send_keys(data_nascimento)

    input_code = driver.find_element_by_xpath('//input[@id="txtTexto_captcha_serpro_gov_br"]')
    input_code.click()


def send_via_whatsappweb():
    driver = webdriver.Firefox()

    url = 'https://web.whatsapp.com/'

    driver.get(url)

    pessoa = driver.find_element_by_xpath('//span[@title="Mari Amore"]')
    pessoa.click()


def pop_up_novo_sae_estudo_info(mat, periodo):
    driver = webdriver.Firefox()

    url1 = 'https://servicos.unb.br/dados/login/index.html?response_type=code&client_id=95&redirect_uri=/sae/index.html'

    driver.get(url1)

    input_uid = driver.find_element_by_xpath('//*[@id="username"]')
    input_uid.click()
    input_uid.send_keys(uid)

    input_pwd = driver.find_element_by_xpath('//*[@id="pass"]')
    input_pwd.click()
    input_pwd.send_keys(pwd)

    input_submit_login = driver.find_element_by_xpath('//*[@id="enter"]')
    input_submit_login.click()

    time.sleep(5)

    driver.find_element_by_xpath('/html/body/my-app/section[1]/unb-navbar/aside/div[1]/ul/li[4]/a').click()

    input_periodo = driver.find_element_by_xpath('//*[@id="mat-input-1"]')
    input_periodo.click()
    input_periodo.clear()
    input_periodo.send_keys(periodo)
    
    input_matricula = driver.find_element_by_xpath('//input[@id="mat-input-2"]')
    input_matricula.click()
    input_matricula.send_keys(mat)

    #Clica em pesquisar
    driver.find_element_by_xpath('/html/body/my-app/section[2]/div/app-estudo-list/estudo-list-filtro/mat-card/form/button').click()
    time.sleep(2)

    input_validacao = driver.find_element_by_xpath('/html/body/my-app/section[2]/div/app-estudo-list/mat-card/div/mat-table/mat-row/mat-cell[9]/div/button[2]')
    input_validacao.click()
    time.sleep(2)

    aba_visualizacao = driver.find_element_by_xpath('/html/body/my-app/section[2]/div/validacao-detail/div/estudo-cabecalho/mat-card/mat-card-actions/estudo-dialog-button/button')
    aba_visualizacao.click()



