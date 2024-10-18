from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste, abrir_ra
import csv, re, time, pyautogui

df = pd.read_csv(elaboration)
login()

header = ['RA', 'ANEXO']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)    

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
            linha = "{}".format(rra), "SIM"
            escritor.writerow(linha)
        else:
            linha = "{}".format(rra), "NAO"
            escritor.writerow(linha)