import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration

df = pd.read_csv(elaboration)
login()

for i in df.index:
    cod_log = int(df['COD_LOG'][i])
    bairro_ant = str(df['BAIRRO_ANT'][i])
    bairro_atual = str(df['BAIRRO_ATUAL'][i])

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarLogradouroAction.do?menu=sim")
    driver.find_element(By.NAME, "idLogradouro").send_keys(cod_log)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        driver.find_element(By.LINK_TEXT, bairro_ant).click()   
             
        j1 = driver.window_handles[0]
        j2 = driver.window_handles[1]
        driver.switch_to.window(j2)
        
        time.sleep(0.2)
        driver.find_element(By.NAME, "idMunicipio").send_keys('1')
        driver.find_element(By.NAME, "nomeBairro").send_keys(bairro_atual)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()        
        driver.find_element(By.PARTIAL_LINK_TEXT, bairro_atual).click()        
        driver.switch_to.window(j1)       
        driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()
        try:
            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            print(i+1, cod_log, msg_ok)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i+1, cod_log, msg_er)
            pass        
    except:
        print(i+1, cod_log, "Não existe bairro com o nome do bairro antigo: {}".format(bairro_ant))
        pass

    
