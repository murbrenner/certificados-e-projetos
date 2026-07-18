import csv, time
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroOS').send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

header = ['#', 'RA', 'OS', 'MATRICULA']
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    escritor = csv.writer(relatorioGsan)
    escritor.writerow(header)

    for i in df.index:
        num_os = str(df['OS'][i])     
        time.sleep(0.3)   
        driver.find_element(By.NAME, 'numeroOSParametro').send_keys(num_os)
        time.sleep(0.3)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        time.sleep(0.3)
        try:
            time.sleep(0.3)
            erro1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            row = i + 1, num_os, erro1
            escritor.writerow(row)
        except:
            pass
        time.sleep(0.3)
        driver.find_element(By.NAME, "numeroRA").get_attribute('value')
        matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')        
        row = i + 1, num_os, matricula
        escritor.writerow(row)