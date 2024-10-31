import time, csv
import pandas as pd
from db_login import login, driver
from db_arquivos import teste, elaboration
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

df = pd.read_csv(elaboration)
login()

header = ['MATRICULA', 'COORD. X', 'COORD. Y']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        matricula = str(df['MATRICULA'][i])
        if matricula != "0":
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "1").click()
            matricula = str(df['MATRICULA'][i])
            driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
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
            escritor.writerow(linha)
        elif matricula == "0":
            linha = '0', '0', '0'
            escritor.writerow(linha)
            pass