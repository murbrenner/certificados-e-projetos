import time
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver, murilo2
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]))    
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()    
    driver.find_element(By.XPATH, "//input[@value='Consultar O.S']").click()
    janela = driver.window_handles[0]
    popup = driver.window_handles[1]
    driver.switch_to.window(popup)    
    os = driver.find_element(By.XPATH, "/html/body/form/table/tbody/tr/td/table[4]/tbody/tr[3]/td/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td[1]/div").text
    driver.close()
    print(i+1, os)
    driver.switch_to.window(janela)