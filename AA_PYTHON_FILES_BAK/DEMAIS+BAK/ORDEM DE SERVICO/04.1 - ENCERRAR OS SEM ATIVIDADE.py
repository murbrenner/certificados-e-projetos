import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import elaboration
from login import murilo, driver

df = pd.read_csv(elaboration)
murilo()

hoje = date.today().strftime("%d/%m/%Y")
motivo = "CANCELADO POR DECURSO DE PRAZO"
hoje = '31/10/2023'

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    enc = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    if enc == 'Pendente':
        driver.find_element(By.NAME, "btnEncerrar").click()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
        driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
        driver.find_element(By.NAME, "observacaoEncerramento").send_keys(str(df['PARECER'][i]))
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        driver.find_element(By.NAME, "confirmar").click()
        j = i + 1
        print(j, "OS {} ENCERRADA".format(str(df['OS'][i])))
    elif enc == 'Encerrada':
        j = i + 1
        print(j, "OS {} JÁ ENCERRADA".format(str(df['OS'][i])))
        pass