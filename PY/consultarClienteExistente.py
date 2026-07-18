import pandas as pd
from db_funcoes import cpf_ok, cnpj_ok
import csv, time, sys
from db_arquivos import *
from db_funcoes import *
from selenium.webdriver.common.by import By
from db_login import login, driver

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['NOME', 'CPF', 'COD_CLIENTE']

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1 

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)
    
    for i in df.index:
        contador = i+1
        cpfInvalido = 0  
        driver.get("http://g1.caema.ma.gov.br/gsan/exibirFiltrarClienteAction.do?menu=sim")        
        nome = str(df['NOME'][i])
        cpf = str(df['CPF'][i])
        cnpj = str(df['CNPJ'][i])
        v_cpf = int(df['V_CPF'][i])
        v_cnpj = int(df['V_CNPJ'][i])
        codCliente = int(df['COD_CLIENTE'][i])
        
        if v_cpf == 1:
            cpf = cpf_ok(cpf)
            driver.find_element(By.NAME, "cpfClienteFiltro").send_keys(cpf)
            time.sleep(0.2)
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()      
            time.sleep(0.3)

            try:
                popup = driver.switch_to.alert
                popup.accept()
                cpfInvalido = 1
            except:  
                cpfInvalido = 0

            if cpfInvalido == 1:
                row = contador, nome, cpf, codCliente
                writer.writerow(row)
            
            if cpfInvalido == 0:
                try:                      
                    codCliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
                    row = contador, nome, cpf, codCliente
                    writer.writerow(row)
                except:
                    codCliente = 0
                    row = contador, nome, cpf, codCliente
                    writer.writerow(row)  

        if v_cnpj == 1:      
            cnpj = cnpj_ok(cnpj)
            driver.find_element(By.NAME, "cnpjClienteFiltro").send_keys(cnpj)
            time.sleep(0.2)
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()      
            time.sleep(0.3)

            try:
                popup = driver.switch_to.alert
                popup.accept()
                cnpjInvalido = 1
            except:  
                cnpjInvalido = 0

            if cnpjInvalido == 1:
                row = contador, nome, cnpj, codCliente
                writer.writerow(row)
            
            if cnpjInvalido == 0:
                try:                      
                    codCliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
                    row = contador, nome, cnpj, codCliente
                    writer.writerow(row)
                except:
                    codCliente = 0
                    row = contador, nome, cnpj, codCliente
                    writer.writerow(row)  

        calculoPorcentagem(contador, totalRow)
