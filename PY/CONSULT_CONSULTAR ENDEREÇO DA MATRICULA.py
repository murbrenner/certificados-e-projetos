from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import elaboration, teste, inserir_imovel
from db_login import login, driver
import csv

df = pd.read_csv(elaboration)
login()

cabeçalho = ['MATRICULA', 'ENDERECO', 'AGUA', 'ESGOTO']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)
    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, '1').click()
        driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        endereco = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/div").text
        agua = driver.find_element(By.NAME, "situacaoAguaDadosCadastrais").get_attribute('value')
        esgoto = driver.find_element(By.NAME, "situacaoEsgotoDadosCadastrais").get_attribute('value')
        linha = (str(df['MATRICULA'][i]), endereco, agua, esgoto)
        escritor.writerow(linha)