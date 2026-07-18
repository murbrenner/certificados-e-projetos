import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
import csv

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'MATRICULA', 'MSG']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
        matricula = int(df['MATRICULA'][i])
        driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
        driver.find_element(By.NAME, "atualizarFiltro").click()
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        try:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            row = i+1, matricula, msg_er
            writer.writerow(row)            
        except:                 
            driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='idRegistrosRemocao']").click()    
            driver.find_element(By.XPATH, "//input[@value='Remover']").click()
            popup = driver.switch_to.alert
            popup.accept()
            try:
                msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                row = i+1, matricula, msg_ok
                writer.writerow(row)
            except:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                row = i+1, matricula, msg_er
                writer.writerow(row)