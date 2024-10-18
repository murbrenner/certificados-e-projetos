from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from selenium.common import NoSuchElementException


df = pd.read_csv("C:\\Users\\Murilo\\Desktop\\PROJETOS PYTHON\\CSV FILES\\ELABORATION.csv")
driver = webdriver.Chrome()

def enter():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('7355')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    hoje = date.today()
    formatted_date = hoje.strftime("%d/%m/%Y")
    hoje = formatted_date
    motivo = "CANCELADO POR DECURSO DE PRAZO"
    parecer = " "

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
        os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
        print(str(df['OS'][i]), end=',')
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        try:
            driver.find_element(By.XPATH, "//input[@value='Encerrar']").click()
            driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
            driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
            driver.find_element(By.NAME, "observacaoEncerramento").send_keys(parecer) # .send_keys(str(df['PARECER'][i]))
            driver.find_element(By.NAME, "ButtonEncerrar").click()
            print("OS {} ENCERRADA".format(str(df['OS'][i])))
        except:
            print("OS {} JÁ TAVA ENCERRADA".format(str(df['OS'][i])))
            pass

enter()