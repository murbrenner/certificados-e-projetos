from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, murilo2
from arquivos import elaboration, teste
import time
import csv

df = pd.read_csv(elaboration)
murilo2()

header = ['#', 'MATRICULA', 'HIDROMETRO', 'LEITURA', 'STATUS AGUA']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "3").click()
        driver.find_element(By.NAME, "idImovelAnaliseMedicaoConsumo").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        nhd = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[5]/td/table/tbody/tr[3]/td[3]/a").text
        driver.find_element(By.PARTIAL_LINK_TEXT, "Histórico de Medição e Consumo da Ligação de Água").click()
        situacao_agua = driver.find_element(By.NAME, "situacaoAguaAnaliseMedicaoConsumo").get_attribute('value')
        leitura_atual = driver.find_element(By.XPATH, "//*[@id='layerShowLigacaoAgua']/table/tbody/tr[2]/td/table/tbody/tr[3]/td[6]").text
        linha = i+1, str(df['MATRICULA'][i]), nhd, leitura_atual, situacao_agua
        escritor.writerow(linha)