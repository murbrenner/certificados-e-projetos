import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
from arquivos import abrir_ra, teste
from login import murilo, driver
import csv

df = pd.read_csv(abrir_ra)
murilo()

for i in df.index:
    driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim')
    driver.find_element(By.NAME, "tipoSolicitacao").send_keys("ATENDIMENTO RAPIDO")
    driver.find_element(By.NAME, "especificacao").send_keys("COMENTARIO")
    driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))
    driver.find_element(By.NAME, "avancar").click()
    driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    time.sleep(0.2)
    try:
        popup = driver.switch_to.alert
        popup.accept()
    except:
        pass
    try:
        inex = driver.find_element(By.NAME, "inscricaoImovel").get_attribute("value")
        if inex == "Imóvel Inexistente":
            j = i + 1
            print(j, str(df['MATRICULA'][i]), inex)
            time.sleep(0.2)
        else:
            try:
                driver.find_element(By.NAME, "avancar").click()
                driver.find_element(By.XPATH, f"//*[@value='Avançar']").click()
                driver.find_element(By.NAME, "concluir").click()
                txt = driver.find_element(By.CSS_SELECTOR,
                                          'body > table:nth-child(5) > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > div > span').text
                num = re.findall(r'\d+', txt)
                num_ra = ' '.join(num).replace("'", '').replace('[', '').replace(']', '')
                num_ra = num_ra[:7]
                num_os = num_ra[7:15]
                j = i + 1
                print(j, str(df['MATRICULA'][i]), num_ra, num_os)
                time.sleep(0.2)


            except:
                erro1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                j = i + 1
                print(j, str(df['MATRICULA'][i]), erro1)
                time.sleep(0.2)
    except:
        try:
            erro2 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            j = i + 1
            print(j, str(df['MATRICULA'][i]), erro2)
            time.sleep(0.2)
        except:
            erro3 = "ALGUM ERRO"
            j = i + 1
            print(j, str(df['MATRICULA'][i]), erro3)
            time.sleep(0.2)