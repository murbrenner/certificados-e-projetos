import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, inserir_imovel

df = pd.read_csv(inserir_imovel)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, "matriculaFiltro").send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        err1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i+1, err1)
    except:               
        
        driver.find_element(By.NAME, "idLocalidade").clear()
        driver.find_element(By.NAME, "idLocalidade").send_keys(str(df['LOCAL'][i]), Keys.ENTER)
        driver.find_element(By.NAME, "idSetorComercial").clear()
        driver.find_element(By.NAME, "idSetorComercial").send_keys(str(df['SETOR'][i]), Keys.ENTER)
        driver.find_element(By.NAME, "idQuadra").clear()
        driver.find_element(By.NAME, "idQuadra").send_keys(str(df['QUADRA'][i]), Keys.ENTER)
        #seq_lote = driver.find_element(By.NAME, "sequencialRota").get_attribute('value')
        driver.find_element(By.NAME, "lote").clear()
        driver.find_element(By.NAME, "lote").send_keys(str(df['LOTE'][i]), Keys.ENTER)#.send_keys(seq_lote)
        driver.find_element(By.NAME, "subLote").clear()
        driver.find_element(By.NAME, "subLote").send_keys(str(df['SUBLOTE'][i]), Keys.ENTER)
        testada = driver.find_element(By.NAME, "testadaLote").get_attribute('value')        
        if testada == '':
            driver.find_element(By.NAME, "testadaLote").clear()
            driver.find_element(By.NAME, "testadaLote").send_keys(str(df['TESTADA'][i]), Keys.ENTER)
        driver.find_element(By.NAME, "sequencialRota").clear()
        driver.find_element(By.NAME, "sequencialRota").send_keys(str(df['SEQUENCIA'][i]), Keys.ENTER)

        
        driver.find_element(By.XPATH, f"//*[@value='Concluir']").click()
        try:
            driver.find_element(By.XPATH, f"//*[@value='Confirmar']").click()
            print(i + 1, driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text)
        except:
            try:
                driver.find_element(By.NAME, "cancelar").click()
                print(i + 1, driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text)
            except:
                try:
                    print(i + 1, driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text)
                except:
                    print(i + 1, driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text)
    