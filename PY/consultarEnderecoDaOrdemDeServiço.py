import time
import csv
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroOS').send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

cabeçalho = ['#', 'OS', 'SITUACAO', 'MATRICULA', 'ENDERECO']
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(cabeçalho)

    for i in df.index:
        ord_serv = str(df['OS'][i])
        driver.find_element(By.NAME, 'numeroOSParametro').send_keys(ord_serv)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        situacao = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        endereco = driver.find_element(By.NAME, "enderecoOcorrencia").get_attribute('value')
        matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
        linha = (i+1, ord_serv, situacao, matricula, endereco)
        writer.writerow(linha)       