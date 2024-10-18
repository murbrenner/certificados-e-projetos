from selenium.webdriver.common.by import By
import pandas as pd
from login import driver, murilo
from arquivos import elaboration, teste
import csv

df = pd.read_csv(elaboration)
murilo()

cabeçalho = ['#', 'MATRICULA', 'RA', 'STATUS_RA', 'OS', 'STATUS_OS']
print("EXECUTANDO...AGUARDE")

with open(teste, mode="w", newline="") as csv_file:
    escritor = csv.writer(csv_file)
    escritor.writerow(cabeçalho)
    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
        driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]))
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        driver.find_element(By.PARTIAL_LINK_TEXT,"Dados do Local da Ocorrência").click()
        mat = driver.find_element(By.NAME, "matriculaImovel").get_attribute("value")
        rra = driver.find_element(By.NAME, "numeroRA").get_attribute("value")
        sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute("value")
        sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute("value")
        j = i + 1
        print(j, mat, rra, sit_ra, str(df['OS'][i]), sit_os)
        linha = (j, mat, rra, sit_ra, str(df['OS'][i]), sit_os)
        escritor.writerow(linha)
        try:
            msg_ero = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print("DEU RUIM PRA OS {}".format(str(df['OS'][i])))
        except:
            pass





