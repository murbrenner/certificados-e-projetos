from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re



filename = 'F:\\teste.csv'
df = pd.read_csv(filename)

driver = webdriver.Chrome()

def login():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('7355')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "1").click()
        driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        driver.find_element(By.CSS_SELECTOR, ".centercoltext > table:nth-child(4) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(1) > a:nth-child(1) > strong:nth-child(1)").click()
        driver.find_element(By.ID, "5").click()
        driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys("04 - TERRENO")
        driver.find_element(By.NAME, "concluir").click()
        retorno = driver.find_element(By.CSS_SELECTOR, "body > table:nth-child(5) > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > div > span").text
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
        #retorno1 = re.sub('[^0-9]', '', retorno)
        #retorno2 = retorno1[:7] + "," + retorno1[7:]
        print((str(df['MATRICULA'][i])), end=',')
        print(retorno)


login()

while True:
    pass