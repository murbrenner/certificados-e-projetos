from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from selenium.common import NoSuchElementException

df = pd.read_csv('C:\\Users\\ocmvc45555\\Downloads\\inserir revisao.csv')

driver = webdriver.Chrome()
login = "http://gsan.caema.ma.gov.br:8080/gsan"
url1 = "http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim"

def enter():
    driver.get(login)
    driver.find_element(By.NAME, 'login').send_keys('LUIZD')
    driver.find_element(By.NAME, 'senha').send_keys('260154')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    for i in df.index:
        driver.get(url1)
        driver.find_element(By.NAME, "tipoSolicitacao").send_keys('2.02')
        driver.find_element(By.NAME, "especificacao").send_keys('INSERIR REVISAO PROCESSO JUDICIAL')
        driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))
        driver.find_element(By.NAME, "avancar").click()
        driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        try:
            driver.find_element(By.NAME, "avancar").click()
        except NoSuchElementException:
            raios1 = driver.find_element(By.CSS_SELECTOR, "body > table > tbody > tr > td > table:nth-child(4) > tbody > tr:nth-child(1) > td:nth-child(2) > span").get_attribute('value')
            print(raios1, sep=',')
            continue

        driver.find_element(By.NAME, "avancar").click()
        try:
            driver.find_element(By.NAME, "concluir").click()
            raios2 = driver.find_element(By.CSS_SELECTOR, ".centercoltext > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(1) > span:nth-child(1)").get_attribute('value')
            print(raios2, sep=',')
        except NoSuchElementException:
            driver.find_element(By.NAME, "avancar").click()
            driver.find_element(By.NAME, "concluir").click()
            raios = driver.find_element(By.CSS_SELECTOR, ".centercoltext > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(1) > span:nth-child(1)").get_attribute('value')
            print(raios)


        # driver.find_element(By.NAME, "idImovelDebitos").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)


enter()

while True:
    pass