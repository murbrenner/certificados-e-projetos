import time, re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
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
        #nhd = str(df['HIDROMETRO'][i])
        #leitura = str(df['LEITURA'][i])
        driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim')
        #driver.find_element(By.NAME, "unidade").clear()
        #driver.find_element(By.NAME, "unidade").send_keys('550', Keys.ENTER)
        driver.find_element(By.NAME, "tipoSolicitacao").send_keys('2.04')
        driver.find_element(By.NAME, "especificacao").send_keys('LEVANTAMENTO DE DADOS PARA ATUALIZACAO CADASTRAL')
        try:
            popup = driver.switch_to.alert
            popup.accept()
        except:
            pass
        driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))#.send_keys("INSERIR HD {} NO SISTEMA. LEITURA: {}. CONDOMINIO VILLAGE DEL ESTE V".format(nhd, leitura))#(str(df['OBSERVACAO'][i]))
        time.sleep(0.5)
        driver.find_element(By.ID, "2").click()
        time.sleep(0.2)
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
                time.sleep(0.2)
            else:
                try:                    
                    driver.find_element(By.ID, "3").click()
                    time.sleep(0.2)
                    try:
                        popup = driver.switch_to.alert
                        popup.accept()
                    except:
                        pass
                    try:
                        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.2)
                    except:
                        pass
                    time.sleep(0.2)
                    driver.find_element(By.ID, "4").click()
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "concluir").click()
                    time.sleep(0.2)
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
                    time.sleep(0.2)
                except:
                    erro1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                    j = i + 1
                    print(j, str(df['MATRICULA'][i]), erro1)
                    time.sleep(0.2)
                    linha = (j, str(df['MATRICULA'][i]), erro1)
                    escritor.writerow(linha)
                    time.sleep(0.2)
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