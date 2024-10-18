import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
from db_arquivos import abrir_ra, teste
from db_login import login, driver
import csv

df = pd.read_csv(abrir_ra)
login()

cabeçalho = ['#', 'MATRICULA', 'RA', 'OS']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get('https://gsan.caema.ma.gov.br/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim')
        driver.find_element(By.NAME, "unidade").clear()
        driver.find_element(By.NAME, "unidade").send_keys('550', Keys.ENTER)
        driver.find_element(By.NAME, "tipoSolicitacao").send_keys('1.04')
        driver.find_element(By.NAME, "especificacao").send_keys('INSTALACAO DE HIDROMETRO NO RAMAL')
        driver.find_element(By.NAME, "observacao").send_keys(' ')#(str(df['OBSERVACAO'][i]))
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
                linha = (j, str(df['MATRICULA'][i]), inex)
                escritor.writerow(linha)

            else:
                try:
                    driver.find_element(By.NAME, "avancar").click()
                    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/a[2]/img").click()
                    driver.find_element(By.NAME, "idUnidadeSolicitante").send_keys('550', Keys.ENTER)
                    driver.find_element(By.NAME, "idFuncionarioResponsavel").send_keys('44669', Keys.ENTER)

                    driver.find_element(By.XPATH, f"//*[@value='Avançar']").click()
                    driver.find_element(By.NAME, "concluir").click()
                    txt = driver.find_element(By.CSS_SELECTOR,
                                              'body > table:nth-child(5) > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > div > span').text
                    num = re.findall(r'\d+', txt)
                    num_ra = ' '.join(num).replace("'", '').replace('[', '').replace(']', '')
                    num_ra = num_ra.replace(' ', ',')
                    num_ra_ok = num_ra[0:7]
                    num_os = num_ra[8:15]
                    j = i + 1
                    print(j, str(df['MATRICULA'][i]), num_ra_ok, num_os)
                    time.sleep(0.2)
                    linha = (j, str(df['MATRICULA'][i]), num_ra_ok, num_os)
                    escritor.writerow(linha)

                except:
                    erro1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                    j = i + 1
                    print(j, str(df['MATRICULA'][i]), erro1)
                    time.sleep(0.2)
                    linha = (j, str(df['MATRICULA'][i]), erro1)
                    escritor.writerow(linha)

        except:
            try:
                erro2 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                j = i + 1
                print(j, str(df['MATRICULA'][i]), erro2)
                time.sleep(0.2)
                linha = (j, str(df['MATRICULA'][i]), erro2)
                escritor.writerow(linha)
            except:
                erro3 = "ALGUM ERRO"
                j = i + 1
                print(j, str(df['MATRICULA'][i]), erro3)
                time.sleep(0.2)
                linha = (j, str(df['MATRICULA'][i]), erro3)
                escritor.writerow(linha)
