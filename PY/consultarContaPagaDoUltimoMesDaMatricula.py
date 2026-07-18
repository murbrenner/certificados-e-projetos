import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
import csv
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'MATRICULA', 'MES', 'VALOR AGUA', 'VALOR ESGOTO', 'STATUS RETIF']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        matricula = str(df['MATRICULA'][i])
        driver.find_element(By.NAME, "idImovelDebitos").send_keys(matricula, Keys.ENTER)    
        try:
            mes_ref = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[3]/td[1]/div/font/a").text
            mes_ref = mes_ref.replace(' ', '')
            if mes_ref != '06/2024':
                retif = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[3]/td[10]/div/font").text
                valor_agua = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[3]/td[3]/div/font").text  
                valor_esg = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[3]/td[4]/div/font").text  
                qtd = i+1 
                linha = qtd, matricula, mes_ref, valor_agua, valor_esg, retif
                writer.writerow(linha)
            elif mes_ref == '06/2024':
                    driver.find_element(By.ID, '6').click()
                    mes_ref = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/a").text                    
                    valor_conta = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]").text
                    valor_conta = valor_conta.replace(',', '.')
                    valor_conta = valor_conta.replace(' ', '')        
                    valor_agua = float(valor_conta) / 2
                    valor_agua = str(valor_agua).replace('.', ',')
                    valor_esg = valor_agua
                    retif = 'CONTA PAGA'
                    qtd = i+1
                    linha = qtd, matricula, mes_ref, valor_agua, valor_esg, retif
                    writer.writerow(linha)
            elif mes_ref == '':
                driver.find_element(By.ID, '6').click()
                mes_ref = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/a").text
                valor_conta = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]").text
                valor_conta = valor_conta.replace(',', '.')
                valor_conta = valor_conta.replace(' ', '')        
                valor_agua = float(valor_conta) / 2
                valor_agua = str(valor_agua).replace('.', ',')
                valor_esg = valor_agua
                retif = 'CONTA PAGA'
                qtd = i+1
                linha = qtd, matricula, mes_ref, valor_agua, valor_esg, retif
                writer.writerow(linha)
        except:    
            driver.find_element(By.ID, '6').click()
            mes_ref = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/a").text            
            valor_conta = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]").text
            valor_conta = valor_conta.replace(',', '.')
            valor_conta = valor_conta.replace(' ', '')        
            valor_agua = float(valor_conta) / 2
            valor_agua = str(valor_agua).replace('.', ',')
            valor_esg = valor_agua
            retif = 'CONTA PAGA'
            qtd = i+1
            linha = qtd, matricula, mes_ref, valor_agua, valor_esg, retif
            writer.writerow(linha)