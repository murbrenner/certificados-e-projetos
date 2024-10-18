from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo2, driver
from arquivos import elaboration, inserir_imovel
import time

df = pd.read_csv(elaboration)
murilo2()

for i in df.index:   
    matricula = str(df["MATRICULA"][i])
    if matricula != "0": 
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")              
        driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        try:
            err0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text        
            print(i + 1, matricula, err0)
        except:
            driver.find_element(By.NAME, "idLocalidade").clear()
            driver.find_element(By.NAME, "idLocalidade").send_keys(str(df['LOCAL'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "idSetorComercial").clear()
            driver.find_element(By.NAME, "idSetorComercial").send_keys(str(df['SETOR'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "idQuadra").clear()
            driver.find_element(By.NAME, "idQuadra").send_keys(str(df['QUADRA'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "lote").clear()
            driver.find_element(By.NAME, "lote").send_keys(str(df['LOTE'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "subLote").clear()
            driver.find_element(By.NAME, "subLote").send_keys(str(df['SUBLOTE'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "testadaLote").clear()
            driver.find_element(By.NAME, "testadaLote").send_keys(str(df['TESTADA'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "sequencialRota").clear()
            driver.find_element(By.NAME, "sequencialRota").send_keys(str(df['SEQUENCIA'][i]), Keys.ENTER)
        

            driver.find_element(By.XPATH, f"//*[@value='Concluir']").click()

            try:
                driver.find_element(By.XPATH, f"//*[@value='Não']").click()
            except:
                pass
            try:
                driver.find_element(By.XPATH, f"//*[@value='Confirmar']").click()
                driver.find_element(By.XPATH, f"//*[@value='Sim']").click()
                print(i + 1, matricula, driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text)
            except:
                try:
                    driver.find_element(By.NAME, "cancelar").click()
                    print(i + 1, matricula, driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text)
                except:
                    try:
                        print(i + 1, matricula, driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text)
                    except:
                        print(i + 1, matricula, driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text)
                    

    elif matricula == "0":
        err0 = "matricula zerada"
        print(i + 1, matricula, err0)
        pass