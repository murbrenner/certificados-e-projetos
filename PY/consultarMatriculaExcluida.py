import time, csv
import pandas as pd
from db_login import login, driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

header = ['#', 'MATRICULA', 'MSG']

relatorioGsan = relatorioGsan1

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        matricula = str(df['imv_id'][i])
        if matricula != "0":
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            time.sleep(0.1)
            driver.find_element(By.ID, "1").click()
            time.sleep(0.2)
            matricula = str(df['imv_id'][i])
            driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
            time.sleep(0.3)
            try:
                imvInex = driver.find_element(By.NAME, 'matriculaImovelDadosCadastrais').get_attribute('value')
                row = i+1, matricula, imvInex
                writer.writerow(row)
            except:
                pass

            try:                
                msg_exc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr/td[2]/strong/font").text
                msg_exc = msg_exc.replace('í', 'i')
                row = i+1, matricula, msg_exc
                writer.writerow(row)
            except:
                row = i+1, matricula, '(Ativo)'
                writer.writerow(row)            
        elif matricula == "0":
            row = i+1, '0', '(Matrícula Zerada)'
            writer.writerow(row)
            pass