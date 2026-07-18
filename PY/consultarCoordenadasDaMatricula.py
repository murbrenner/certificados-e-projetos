import time, csv
import pandas as pd
from db_login import login, driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from db_arquivos import *

relatorioGsan = relatorioGsan1

df = pd.read_csv(databaseCSV1)
login()

header = ['MATRICULA', 'COORD. X', 'COORD. Y']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        matricula = str(df['MATRICULA'][i])
        if matricula != "0":
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "1").click()
            time.sleep(0.2)
            matricula = str(df['MATRICULA'][i])
            driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
            time.sleep(0.2)
            codif = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
            coordx = driver.find_element(By.NAME, "coordenadaXDadosCadastrais").get_attribute('value')
            if coordx == '':
                coordx = '0'
            coordx = coordx.replace('.', ',')
            coordy = driver.find_element(By.NAME, "coordenadaYDadosCadastrais").get_attribute('value')
            if coordy == '':
                coordy = '0'
            coordy = coordy.replace('.', ',')
            linha = matricula, coordx, coordy
            writer.writerow(linha)
        elif matricula == "0":
            linha = '0', '0', '0'
            writer.writerow(linha)
            pass