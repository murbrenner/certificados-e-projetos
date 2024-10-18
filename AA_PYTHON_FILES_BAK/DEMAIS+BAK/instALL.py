import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import elaboration
from login import murilo, driver
from datas import meses

df = pd.read_csv(elaboration)
murilo()

hoje = date.today().strftime("%d/%m/%Y")
motivo = "CANCELAMENTO PELA CAEMA"
mes = meses

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirCalendarioElaboracaoAcompanhamentoRoteiroAction.do?acompanhamento=true")
    driver.find_element(By.NAME, 'Situacao').send_keys('PENDENTES')
    driver.find_element(By.NAME, 'Month').send_keys(mes)
    driver.find_element(By.NAME, 'Year').send_keys('2023')
    time.sleep(100)



