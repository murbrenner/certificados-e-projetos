from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
import csv
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'MATRICULA', 'CATEGORIA1', 'CATEGORIA2']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index: 
        matricula = int(df['MATRICULA'][i])
        if matricula != 0:               
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "1").click()
            driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
            roteirizacao = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
            if roteirizacao != 'IMÓVEL INEXISTENTE':
                try:
                    categoria = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/div/font").text
                    categoria = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[2]/div/font").text
                    categoria2 = driver.find_element(By.XPATH, f"/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td[2]/div/font").text
                    linha = i+1, matricula, categoria, categoria2,
                    writer.writerow(linha) 
                except:  
                    linha = i+1, matricula, categoria 
                    writer.writerow(linha)                      
                            
            else:
                linha = i+1, matricula, 'IMÓVEL INEXISTENTE'
                writer.writerow(linha)
                
        elif matricula == 0:
            linha = i+1, matricula, 'MATRICULA ZERADA'
            writer.writerow(linha)


