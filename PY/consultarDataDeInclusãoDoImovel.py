from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import *
from db_login import login, driver
import csv, time
from db_funcoes import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

cabeçalho = ['#', 'MATRICULA', 'DATA_CRIACAO']

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(cabeçalho)

    for i in df.index:
        contador = i+1 
        matricula = str(df['MATRICULA'][i])       
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, '2').click()
        time.sleep(0.3)
        driver.find_element(By.NAME, "idImovelDadosComplementares").send_keys(matricula, Keys.ENTER)
        time.sleep(0.2)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar Histórico']").click()
        time.sleep(0.2)
        driver.find_element(By.LINK_TEXT, "INSERIR IMOVEL").click()
        time.sleep(0.2)
        janela = driver.window_handles[0]
        popup = driver.window_handles[1]
        driver.switch_to.window(popup) 
        dataInclusao = driver.find_element(By.XPATH, "//input[@name='textfield223' and @maxlength='10']").get_attribute('value')    
        driver.find_element(By.XPATH, "//input[@value='Fechar']").click()
        time.sleep(0.2)
        driver.switch_to.window(janela) 
        row = contador, matricula, dataInclusao
        writer.writerow(row)

        calculoPorcentagem(contador, totalRow)