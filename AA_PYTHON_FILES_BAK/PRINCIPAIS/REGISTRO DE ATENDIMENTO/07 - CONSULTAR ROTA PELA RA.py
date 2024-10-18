from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import elaboration, teste
from login import murilo2, driver
import csv

df = pd.read_csv(elaboration)
murilo2()

cabeçalho = ['#', 'RA', 'OS', 'MAT', 'LOCAL', 'SETOR', 'QUADRA', 'SEQUENCIA', 'ROTA']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
        driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, '//*[@value="Filtrar"]').click()
        driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        local = driver.find_element(By.NAME, "idLocalidade").get_attribute('value')
        setor = driver.find_element(By.NAME, "idSetorComercial").get_attribute('value')
        quadra = driver.find_element(By.NAME, "idQuadra").get_attribute('value')
        rota = driver.find_element(By.NAME, "rota").get_attribute('value')
        matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
        sequencia = driver.find_element(By.NAME, "sequencialRota").get_attribute('value')
        linha = i+1, str(df['RA'][i]), str(df['OS'][i]), matricula, local, setor, quadra, sequencia, rota
        escritor.writerow(linha)