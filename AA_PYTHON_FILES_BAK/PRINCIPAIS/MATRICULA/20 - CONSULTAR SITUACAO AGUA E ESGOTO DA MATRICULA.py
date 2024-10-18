from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo2, driver
from arquivos import elaboration, abrir_ra

df = pd.read_csv(abrir_ra)
murilo2()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    agua = driver.find_element(By.NAME, "situacaoAguaDadosCadastrais").get_attribute('value')
    esgoto = driver.find_element(By.NAME, "situacaoEsgotoDadosCadastrais").get_attribute('value')
    roteirizacao = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
    if roteirizacao == 'IMÓVEL INEXISTENTE':
        print(i+1, str(df['MATRICULA'][i]), 'IMÓVEL INEXISTENTE', sep=';')
    else:
        print(i+1, str(df['MATRICULA'][i]), agua, esgoto, sep=';')

