import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste
import csv

df = pd.read_csv(elaboration)
login()

header = ['#', 'MATRICULA', 'MSG']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
        matricula = int(df['MATRICULA'][i])
        driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
        driver.find_element(By.NAME, "atualizarFiltro").click()
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        try:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            linha = i+1, matricula, msg_er
            escritor.writerow(linha)            
        except:                 
            driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='idRegistrosRemocao']").click()    
            driver.find_element(By.XPATH, "//input[@value='Remover']").click()
            popup = driver.switch_to.alert
            popup.accept()
            try:
                msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                linha = i+1, matricula, msg_ok
                escritor.writerow(linha)
            except:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                linha = i+1, matricula, msg_er
                escritor.writerow(linha)