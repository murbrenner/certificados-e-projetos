import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration

df = pd.read_csv(elaboration)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")
    cod_cliente = int(df['COD_CLIENTE'][i])
    driver.find_element(By.NAME, "codigoClienteFiltro").send_keys(cod_cliente)
    driver.find_element(By.NAME, "atualizarFiltro").click()    
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i+1, cod_cliente, msg_er)            
    except:
        driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='idRegistrosRemocao' and @value='{}']".format(cod_cliente)).click()
        time.sleep(1111)    
        driver.find_element(By.XPATH, "//input[@value='Remover']").click()
        popup = driver.switch_to.alert
        popup.accept()
        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            print(i+1, cod_cliente, msg_ok)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i+1, cod_cliente, msg_er)
