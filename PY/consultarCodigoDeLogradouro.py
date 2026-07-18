import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
from db_funcoes import *
import csv

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'STATUS']

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        contador = i+1
        codLog = int(df['COD LOG'][i])
        driver.get("https://g1.caema.ma.gov.br/gsan/exibirFiltrarLogradouroAction.do?menu=sim")
        driver.find_element(By.NAME, "idLogradouro").send_keys(codLog)
        time.sleep(0.1)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        time.sleep(0.3)
        driver.find_element(By.NAME, "idTipo").send_keys('')
        tipoLog = driver.find_element(By.XPATH, "//option[@selected='selected']").get_attribute('value')
        tipoLog = tipoLogFunc['{}'.format(tipoLog)]
        print(tipoLog)
        time.sleep(0.2)
        driver.find_element(By.NAME, "idTitulo").send_keys('')
        titLog = driver.find_element(By.NAME, "idTitulo").get_attribute('value')
        titLog = titLogFunc['{}'.format(titLog)]
        print(titLog)

        time.sleep(111111)

        
