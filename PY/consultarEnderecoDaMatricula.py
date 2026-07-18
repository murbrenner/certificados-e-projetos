from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import *
from db_login import login, driver
import csv, time

df = pd.read_csv(databaseCSV2)
login()

relatorioGsan = relatorioGsan2

cabeçalho = ['MATRICULA', 'ENDERECO', 'AGUA', 'ESGOTO']

with open(databaseCSV2, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(cabeçalho)
    for i in df.index:
        contador = i+1
        time.sleep(0.2)
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, '1').click()
        time.sleep(0.3)
        driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['imv_id'][i]), Keys.ENTER)
        time.sleep(0.2)
        endereco = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/div").text
        agua = driver.find_element(By.NAME, "situacaoAguaDadosCadastrais").get_attribute('value')
        esgoto = driver.find_element(By.NAME, "situacaoEsgotoDadosCadastrais").get_attribute('value')
        linha = (str(df['imv_id'][i]), endereco, agua, esgoto)
        writer.writerow(linha)

        percent1 = ((contador-1)*100)/totalRow
        percent1 = int(percent1)
        percent2 = (contador*100)/totalRow
        percent2 = int(percent2)
        if percent1 != percent2:            
            if percent2 != 100:
                print(f'{percent2}% CONCLUÍDO...')
            else:
                print(f'{percent2}% CONCLUÍDO!')