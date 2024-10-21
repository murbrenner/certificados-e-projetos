from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste, inserir_imovel
import csv

df = pd.read_csv(elaboration)
login()

header = ['#', 'MATRICULA', 'AGUA', 'ESGOTO']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "1").click()
        matricula = str(df['MATRICULA'][i])
        driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
        agua = driver.find_element(By.NAME, "situacaoAguaDadosCadastrais").get_attribute('value')
        esgoto = driver.find_element(By.NAME, "situacaoEsgotoDadosCadastrais").get_attribute('value')
        roteirizacao = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
        if roteirizacao == 'IMÓVEL INEXISTENTE':            
            linha = i+1, matricula, 'IMÓVEL INEXISTENTE'
            escritor.writerow(linha)
        else:            
            linha = i+1, matricula, agua, esgoto
            escritor.writerow(linha)

