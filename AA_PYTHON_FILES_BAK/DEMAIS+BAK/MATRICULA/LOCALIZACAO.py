import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import teste, teste2, elaboration
from login import murilo, driver
from datetime import date
import csv

df = pd.read_csv(elaboration)
murilo()

cabeçalho = ['#', 'RA', 'COORDENADA NORTE', 'COORDENADA LESTE']

with open(teste2, mode="w", newline="") as teste2:
    escritor = csv.writer(teste2)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
        driver.find_element(By.NAME, 'numeroRA').send_keys(str(df['RA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        driver.find_element(By.LINK_TEXT, 'Dados do Local da Ocorrência').click()
        c_north = driver.find_element(By.NAME, "numeroCoordenadaNorte").get_attribute('value')
        c_west = driver.find_element(By.NAME, "numeroCoordenadaLeste").get_attribute('value')
        linha = i+1, str(df['RA'][i]), c_north, c_west
        escritor.writerow(linha)

