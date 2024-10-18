import time
import csv
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste

df = pd.read_csv(elaboration)
login()

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroOS').send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

cabeçalho = ['#', 'SITUACAO', 'OS', 'DATA PROG', 'EQUIPE']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.find_element(By.NAME, 'numeroOSParametro').send_keys(str(df['OS'][i]))
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        situacao = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        num_os = len(str(df['OS'][i]))
        driver.find_element(By.LINK_TEXT, "Dados da Programação").click()
        data = driver.find_element(By.NAME, "dataProgramacao").get_attribute('value')
        equipe = driver.find_element(By.NAME, "equipeProgramacao").get_attribute('value')
        linha = (i + 1, situacao, str(df['OS'][i]), data, equipe)
        escritor.writerow(linha)