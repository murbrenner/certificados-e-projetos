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

cabeçalho = ['#', 'OS', 'MATRICULA']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        num_os = str(df['OS'][i])        
        driver.find_element(By.NAME, 'numeroOSParametro').send_keys(str(df['OS'][i]))
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        try:
            erro1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            linha = i + 1, num_os, erro1
            escritor.writerow(linha)
        except:
            pass
        driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')        
        linha = i + 1, num_os, matricula
        escritor.writerow(linha)