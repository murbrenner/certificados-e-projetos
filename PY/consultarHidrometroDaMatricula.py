from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
import time, csv

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

cabeçalho = ['#', 'MATRICULA', 'STATUS HD', 'NUMERO HD']
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(cabeçalho)

    for i in df.index:       
        mat = int(df['MATRICULA'][i]) 
        if mat != 0:
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "3").click()
            time.sleep(0.3)
            driver.find_element(By.NAME, "idImovelAnaliseMedicaoConsumo").send_keys(mat, Keys.ENTER)
            time.sleep(0.3)
            try:            
                status_hd = driver.find_element(By.NAME, "tipoLigacaoAnaliseMedicaoConsumo").get_attribute('value')                   
                numero_hd = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[5]/td/table/tbody/tr[3]/td[3]/a").text
                print(i+1, mat, status_hd, numero_hd)
                linha = i+1, mat, status_hd, numero_hd
                writer.writerow(linha)
            except:
                print(i+1, mat, "SEM HID", "SEM HID")
                linha = i+1, mat, "SEM HID", "SEM HID"
                writer.writerow(linha)
        elif mat == 0:
            #print(i+1, '0', '0', '0')
            linha = i+1, '0', '0', '0'
            writer.writerow(linha)