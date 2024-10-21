from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import tramite, teste, elaboration
import csv

df = pd.read_csv(elaboration)
login()

driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroRA').send_keys(str(df['RA'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

cabeçalho = ['#', 'RA', 'SIT RA', 'UNIDADE ORIGEM', 'UNIDADE ATUAL', 'DATA TRAMITE', 'HORA TRAMITE']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.find_element(By.NAME, 'numeroRA').send_keys(str(df['RA'][i]))
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
        driver.find_element(By.LINK_TEXT, "Dados da Última Tramitação").click()
        und_orig = driver.find_element(By.NAME, "unidadeOrigem").get_attribute('value')
        und_atual = driver.find_element(By.NAME, "unidadeAtualTramitacao").get_attribute('value')
        data_tram = driver.find_element(By.NAME, "dataTramite").get_attribute('value')
        hora_tram = driver.find_element(By.NAME, "horaTramite").get_attribute('value')
        linha = (i+1, str(df['RA'][i]), sit_ra, und_orig, und_atual, data_tram, hora_tram)
        escritor.writerow(linha)