import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import elaboration, abrir_ra
from login import murilo, driver

df = pd.read_csv(abrir_ra)
murilo()

hoje = date.today().strftime("%d/%m/%Y")
motivo = "CODIGO SERVICO ERRADO"

for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(int(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    enc = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    if enc == 'Pendente':
        driver.find_element(By.NAME, "btnEncerrar").click()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
        driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
        driver.find_element(By.NAME, "observacaoEncerramento").send_keys(str(df['PARECER'][i]), str(df['OS'][i]))
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        try:
            driver.find_element(By.NAME, "confirmar").click()
        except:
            pass
        j = i + 1
        print(j, "OS {} ENCERRADA".format(int(df['OS'][i])))
    elif enc == 'Encerrada':
        j = i + 1
        print(j, "OS {} JÁ ENCERRADA".format(int(df['OS'][i])))
        pass