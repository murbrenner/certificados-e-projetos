from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
from db_funcoes import *
import csv

df = pd.read_csv(databaseCSV2)
login()

relatorioGsan = relatorioGsan2

header = ['#', 'MATRICULA', 'AGUA', 'ESGOTO']

with open(databaseCSV2, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        contador = i+1
        matricula = int(df['MATRICULA'][i])
        if matricula != 0:
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "1").click()  
            time.sleep(0.2)          
            driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
            time.sleep(0.4)
            agua = driver.find_element(By.NAME, "situacaoAguaDadosCadastrais").get_attribute('value')
            esgoto = driver.find_element(By.NAME, "situacaoEsgotoDadosCadastrais").get_attribute('value')
            roteirizacao = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
            if roteirizacao == 'IMÓVEL INEXISTENTE':            
                linha = i+1, matricula, 'IMÓVEL INEXISTENTE'
                writer.writerow(linha)
            else:            
                linha = i+1, matricula, agua, esgoto
                writer.writerow(linha)
        elif matricula == 0:
            row = i+1, 'MAT INEXISTENTE', 'MAT INEXISTENTE', 'MAT INEXISTENTE'
            writer.writerow(row)

        calculoPorcentagem(contador, totalRow)
