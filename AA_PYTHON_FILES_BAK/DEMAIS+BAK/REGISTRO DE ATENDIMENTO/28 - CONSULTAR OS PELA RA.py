import time

from selenium.webdriver.common.by import By
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, teste

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    j = 1
    while j < 10:
        try:
            tipo_os = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[3]/div/font".format(j)).text
            if tipo_os == 'LEVANT DE DADOS PARA ATUALIZ CADASTRAL':
                driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[2]/div/a/font".format(j)).click()
                time.sleep(0.1)
            elif tipo_os == 'LEVANTAMENTO DE DADOS PARA ATUALIZACAO CADASTRAL':
                driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[2]/div/a/font".format(j)).click()
                time.sleep(0.1)
        except:
            pass
        j += 1
    driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
    matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
    oos = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
    j = i + 1
    print(j, str(df['RA'][i]), str(oos))
    #driver.find_element(By.NAME, "btnImprimir").click()
    #time.sleep(0.5)