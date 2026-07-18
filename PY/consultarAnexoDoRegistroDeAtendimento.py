from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
import csv, re, time, pyautogui
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['RA', 'ANEXO']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)    

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][0]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

    for i in df.index:        
        rra = str(df['RA'][i])
        driver.find_element(By.NAME, "numeroRA").send_keys(rra)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        driver.find_element(By.LINK_TEXT, "Anexos").click()
        j = 1
        cont_anexo = 0
        while j < 10:        
            try:
                anexo = driver.find_element(By.XPATH, '//*[@id="layerShowAnexos"]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr/td[1]/a/img')
                #anexo.click()
                #time.sleep(1)
                cont_anexo += 1           
            except: 
                try:
                    anexo = driver.find_element(By.XPATH, '//*[@id="layerShowAnexos"]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr{}/td[1]/a/img'.format(j))
                except:
                    cont_anexo += 1
                    pass
                cont_anexo = 0           
                pass         
            j += 1       
        if cont_anexo >= 1:
            row = "{}".format(rra), "SIM"
            writer.writerow(row)
        else:
            row = "{}".format(rra), "NAO"
            writer.writerow(row)