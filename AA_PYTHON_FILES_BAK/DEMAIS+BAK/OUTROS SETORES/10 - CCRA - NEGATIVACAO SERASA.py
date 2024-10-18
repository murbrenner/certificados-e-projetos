import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

filename = 'C:\\Users\\ocmvc45555\\Downloads\\ExclusaoNegativacaoSERASA.csv'
df = pd.read_csv(filename)

driver = webdriver.Chrome()

def enter():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('LUIZD')
    driver.find_element(By.NAME, 'senha').send_keys('260154')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirExcluirNegativacaoOnLineAction.do?menu=sim")
        driver.find_element(By.NAME, 'negativador').send_keys('SERASA')
        driver.find_element(By.NAME, 'idImovel').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        print((str(df['MATRICULA'][i])))
        play()

def play():
    try:
        driver.find_element(By.LINK_TEXT, "Dados da Negativação").click()
        driver.find_element(By.NAME, 'cliente').click()
        driver.find_element(By.LINK_TEXT, 'Dados da Exclusão da Negativação').click()
        driver.find_element(By.NAME, 'motivoExclusao').send_keys('MOTIVO NAO')
        driver.find_element(By.NAME, 'idUsuario').send_keys('193', Keys.ENTER)
        driver.find_element(By.NAME, 'Atualizar').click()
        print("DEU CERTO!!!")
    except NoSuchElementException:
        print("DEU CERTO NAO Ó...")

enter()
