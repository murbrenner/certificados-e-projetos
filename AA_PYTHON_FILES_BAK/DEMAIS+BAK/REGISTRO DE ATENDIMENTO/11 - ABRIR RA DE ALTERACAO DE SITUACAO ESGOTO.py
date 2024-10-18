from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import abrir_ra
import time

df = pd.read_csv(abrir_ra)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "tipoSolicitacao").send_keys('2.04')
    driver.find_element(By.NAME, "especificacao").send_keys('ALTERAR SITUACAO DA LIGACAO AGUA/ESGOTO')
    driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))
    driver.find_element(By.NAME, "avancar").click()
    driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)

    try:
        driver.find_element(By.NAME, "avancar").click()
    except:
        raios1 = driver.find_element(By.CSS_SELECTOR, "body > table > tbody > tr > td > table:nth-child(4) > tbody > tr:nth-child(1) > td:nth-child(2) > span").get_attribute('value')
        print(raios1, sep=',')
        continue

    driver.find_element(By.NAME, "avancar").click()
    try:
        driver.find_element(By.NAME, "concluir").click()
        raios2 = driver.find_element(By.CSS_SELECTOR, ".centercoltext > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(1) > span:nth-child(1)").get_attribute('value')
        print(raios2, sep=',')
    except:
        driver.find_element(By.NAME, "avancar").click()
        driver.find_element(By.NAME, "concluir").click()
        raios = driver.find_element(By.CSS_SELECTOR, ".centercoltext > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(1) > span:nth-child(1)").get_attribute('value')
        print(raios)
