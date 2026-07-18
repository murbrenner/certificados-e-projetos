import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import *
from db_login import login, driver

df = pd.read_csv(databaseCSV1)
login()

hoje = date.today().strftime("%d/%m/%Y")
motivo = "DEFERIDO"

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(int(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    enc = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    if enc == 'Pendente':
        driver.find_element(By.NAME, "btnEncerrar").click()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
        driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
        driver.find_element(By.NAME, "observacaoEncerramento").send_keys(str(df['OBSERVACAO'][i]), str(df['OS'][i]))
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        try:
            driver.find_element(By.NAME, "confirmar").click()
        except:
            pass
        try:
            driver.find_element(By.NAME, "Sim").click()
        except:
            pass
        j = i + 1
        print(j, "OS {} ENCERRADA".format(int(df['OS'][i])))
    elif enc == 'Encerrada':
        j = i + 1
        print(j, "OS {} JÁ ENCERRADA".format(int(df['OS'][i])))
        pass