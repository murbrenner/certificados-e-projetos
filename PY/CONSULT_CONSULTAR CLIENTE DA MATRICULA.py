import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import inserir_imovel, elaboration, abrir_ra

df = pd.read_csv(elaboration)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, 'idImovelDadosCadastrais').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)

    try:
        nome_user = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[1]/div/font/a").text
        doc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[5]/font/a/font").text        
        print(i+1, f"[{nome_user}]", f"[{doc}]")
    except:        
        try:
            nome_user = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[1]/div/font/a").text
            doc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[5]/font/a/font").text                                                
            doc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td[5]/font/a/font").text
            doc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[3]/td[5]/font/a/font").text
            print(i+1, nome_user, doc)          
        except:
            print(i+1, f"[{nome_user}]", "[SEM CPF]")
            pass