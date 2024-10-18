
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, teste
import csv

df = pd.read_csv(elaboration)
murilo()

cabeçalho = ['#', 'MATRICULA', 'RA', 'OS']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
        #driver.find_element(By.NAME, "situacaoOrdemServico").send_keys('PENDENTES')
        #driver.find_element(By.XPATH, "//option[@value='910']").click()
        driver.find_element(By.NAME, "matriculaImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        try:
            k = 3
            tipo_ra = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[4]/td[{}]/div/font".format(k)).text
            if tipo_ra == 'LEVANTAMENTO DE DADOS PARA ATUALIZACAO CADASTRAL':
                driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[4]/td[2]/div/a/font".format(k-1)).click()
        except:
            try:
                eer1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                j = i + 1
                print(j, str(df['MATRICULA'][i]), eer1)
                linha = (j, str(df['MATRICULA'][i]), eer1)
                escritor.writerow(linha)
            except:
                pass
        try:
            ord_serv = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
            rra = driver.find_element(By.NAME, "numeroRA").get_attribute('value')
            #driver.find_element(By.XPATH, "//input[@value='Imprimir']").click()
            j = i + 1
            print(j, str(df['MATRICULA'][i]), "{} {}".format(ord_serv, rra))
            linha = (j, str(df['MATRICULA'][i]), "{} {}".format(ord_serv, rra))
            escritor.writerow(linha)
        except:
            # j = i + 1
            # print(j, str(df['MATRICULA'][i]), "Nenhuma Ordem de Serviço tipo INST. HD PROGRAMA HIDRO 2023 encontrada.")
            # linha = (j, str(df['MATRICULA'][i]), "Nenhuma Ordem de Serviço tipo INST. HD PROGRAMA HIDRO 2023 encontrada.")
            # escritor.writerow(linha)
            pass
        #time.sleep(1)