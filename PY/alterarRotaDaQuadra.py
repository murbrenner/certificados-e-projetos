from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
import csv, time

df = pd.read_csv(databaseCSV1)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarQuadraAction.do?menu=sim")        

    local = '925'
    setor = '400'
    quadra = str(df['quadra'][i])
    rota_nova = str(df['rota_nova'][i])
    
    time.sleep(0.3)
    driver.find_element(By.NAME, "localidadeID").send_keys(local)#, Keys.ENTER)
    #time.sleep(0.3)
    driver.find_element(By.NAME, "setorComercialCD").send_keys(setor)#, Keys.ENTER)
    #time.sleep(0.3)
    driver.find_element(By.NAME, "quadraNM").send_keys(quadra)
    #time.sleep(0.3)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    time.sleep(0.3)

    driver.find_element(By.NAME, "codigoRota").clear() 
    driver.find_element(By.NAME, "codigoRota").send_keys(rota_nova, Keys.ENTER) 
    time.sleep(0.3)
    
    driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()

    #print(i+1, local, setor, quadra, rota)

    try:
        time.sleep(0.3)
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text    
        print(i+1, local, setor, quadra, rota_nova, msg_ok)        
    except:
        time.sleep(0.3)
        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i+1, local, setor, quadra, rota_nova, msg_er)
        