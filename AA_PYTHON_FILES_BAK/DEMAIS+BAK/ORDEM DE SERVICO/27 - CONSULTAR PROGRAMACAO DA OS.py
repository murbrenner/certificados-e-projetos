from selenium.webdriver.common.by import By
import pandas as pd
from login import driver, murilo
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroOS').send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

for i in df.index:
    driver.find_element(By.NAME, 'numeroOSParametro').send_keys(str(df['OS'][i]))
    driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
    situacao = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    driver.find_element(By.LINK_TEXT, "Dados da Programação").click()
    data = driver.find_element(By.NAME, "dataProgramacao").get_attribute('value')
    equipe = driver.find_element(By.NAME, "equipeProgramacao").get_attribute('value')
    if data == '':
        print(i+1, situacao, str(df['OS'][i]), 'Ordem de Serviço não programada', sep=',')
        pass
    else:
        print(i+1, situacao, str(df['OS'][i]), equipe, data, sep=',')