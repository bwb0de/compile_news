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

def parse_url(url):
    http_doc = get_page(url)
    http_response_info = BeautifulSoup(http_doc, 'html.parser')
    return http_response_info

def get_page_links(url):
    http_response_info = parse_url(url)
    for link in http_response_info.find_all('a'):
        yield link#.get('href')

def get_page_info(url, html_tag):
    http_response_info = parse_url(url)
    for item in http_response_info.find_all(html_tag):
        yield item


def get_bbc_news_fulltext(url, html_tag='a'):
    http_response_info = parse_url(url)
    info = ''
    for paragrafo in http_response_info.find_all('p'):
        info += paragrafo.get_text() + os.linesep*2
    info = info.split('Já assistiu aos nossos novos vídeos no YouTube? Inscreva-se no nosso canal!')[0]
    info = info.split('Estes são links externos e abrirão numa nova janela')[1]
    return info


def get_bbc_news(url=bbc_br, html_tag='a', target_folder=''):
    http_response_info = get_page_info(url, html_tag)

    n = itertools.count()

    for selected_info in http_response_info:
        sub_selected_session = selected_info.find_all('h3')
        
        for sub_selected_info in sub_selected_session:
            title = sub_selected_info.get_text().strip()
            link = selected_info.get('href').strip()
            link = bbc_br.replace('/portuguese', link) 
            ignore_text = False

            try:
                fulltext_data = get_bbc_news_fulltext(link)
            except requests.exceptions.ConnectionError:
                ignore_text = True

            with open(target_folder+'noticias_bbc_{}.txt'.format(next(n)), 'w') as f:
                f.write(title+os.linesep)
                f.write(link+os.linesep*3)
                if not ignore_text:
                    f.write(fulltext_data)
            
            time.sleep(0.2)


def get_folha_news_fulltext(url, title='', html_tag='a', target_folder='', news_num=0):
    http_response_info = parse_url(url)
    encoding = 'utf8'#http_response_info.original_encoding

    title_info = ''

    for t in http_response_info.find_all('h1'):
        title_info = t.get_text().strip()

    output_info = []
    output_info.append(title_info.encode('raw_unicode_escape'))

    info = ''

    for paragrafo in http_response_info.find_all('p'):

        p_info = paragrafo.get_text().strip()
        p_info = p_info.encode('raw_unicode_escape')

        output_info.append(p_info)

        """
        try:
            p_info = p_info.encode('raw_unicode_escape')
            p_info = codecs.decode(p_info, 'utf8')
        except UnicodeDecodeError:
            p_info = codecs.decode(p_info, 'latin1')
            p_info = paragrafo.get_text().strip().encode('raw_unicode_escape')
            p_info = codecs.decode(p_info, 'utf8')
        """
        '''
        print(p_info)
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

        elif p_info.find('Copyright Folha de S.Paulo. Todos os direitos reservados.') != -1:
            break
        
        elif p_info.find('vantagens de ser assinante da Folha?') != -1:
            break

        elif p_info.find('Seu e-mail foi cadastrado com sucesso!') != -1:
            break
        
        else:
            info += p_info
            #output_info.append(p_info)
        '''
    """
    while True:
        if info.find('\n\n\n') != -1: 
            info = info.replace('\n\n\n', '\n\n')
            info = info.replace('Gostaria de receber as principais notícias do Brasil e do mundo?','')
            info = info.replace('Assinantes podem liberar 5 acessos por dia para conteúdos da Folha','')
            info = info.replace('Assinantes podem liberar 5 acessos por dia para conteúdos da Folha','')
        else: break
    """
    #info_b = bytes(info, encoding)
    #output_info.append(info_b)

    print(info)

    
    with open(target_folder+'noticias_folha_{}.txt'.format(news_num), 'wb') as f:
        for line in output_info:
            f.write(line)
    
    """
    with open(target_folder+'noticias_folha_{}.txt'.format(news_num), 'w', encoding=encoding) as f:
        f.write(title_info+os.linesep*2)
        f.write(info)
    """
    '''
    o = []
    with open(target_folder+'noticias_folha_{}.txt'.format(news_num), 'rb') as f:
        for line in f.readlines():
            s = codecs.decode(line, encoding='utf-8')
            o.append(s)
    
    for i in o:
        print(i)
    '''
    
    input('CTRL+C')



def get_folha_news(url=folha, html_tag='h2', target_folder=''):
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



def get_br_de_fato_news(url=br_de_fato, target_folder=''):
    http_response = get_page_links(url)

    n = itertools.count()

    news_links = []

    for ln in http_response:
        if ln.parent.find('h3'):
            titulo = ln.parent.find('h3').get_text().strip()
            link = ln.get('href').strip()
            news_links.append((titulo, link))
    
    for new in news_links:
        with open(target_folder+'noticias_br_de_fato_{}.txt'.format(next(n)), 'w') as f:
            f.write(new[0]+os.linesep)
            f.write(new[1]+os.linesep*3)
            new_info = parse_url(new[1])
            for paragrafo in new_info.find_all('p'):
                if paragrafo.get_text().strip() == 'Quem Somos':
                    break
                else:
                    f.write(paragrafo.get_text()+os.linesep*2)

    return news_links
    

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



