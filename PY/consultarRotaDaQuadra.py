from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
import csv, time

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'LOCAL', 'SETOR', 'QUADRA', 'ROTA']
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarQuadraAction.do?menu=sim")        

        local = '404'
        setor = '100'
        quadra = str(df['quadra'][i])
        
        time.sleep(0.3)
        driver.find_element(By.NAME, "localidadeID").send_keys(local)#, Keys.ENTER)
        #time.sleep(0.3)
        driver.find_element(By.NAME, "setorComercialCD").send_keys(setor)#, Keys.ENTER)
        #time.sleep(0.3)
        driver.find_element(By.NAME, "quadraNM").send_keys(quadra)
        #time.sleep(0.3)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        time.sleep(0.3)

        rota = driver.find_element(By.NAME, "codigoRota").get_attribute('value')   

        row = i+1, local, setor, quadra, rota
        writer.writerow(row)