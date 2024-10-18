import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, murilo2
from arquivos import inserir_imovel, elaboration

df = pd.read_csv(elaboration)
murilo2()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, 'idImovelDadosCadastrais').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        
    try:
        nome_user = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[1]/div/font/a").text
    except:
        nome_user = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[1]/div/font/a").text
    
    print(i+1, nome_user)