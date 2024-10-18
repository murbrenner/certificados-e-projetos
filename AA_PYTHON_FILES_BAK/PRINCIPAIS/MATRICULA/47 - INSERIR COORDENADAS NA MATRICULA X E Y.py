import time

import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo2, driver
from arquivos import inserir_imovel, elaboration

df = pd.read_csv(elaboration)
murilo2()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    matricula = str(df['MATRICULA'][i])
    cx = str(df['X'][i])
    cy = str(df['Y'][i])        
    driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(msg_er)
        pass
    except:
        driver.find_element(By.ID, "2").click()
        try:
            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
        except:
            pass
        time.sleep(0.1)
        driver.find_element(By.ID, "6").click()        
        time.sleep(0.1)
        driver.find_element(By.NAME, "cordenadasUtmX").clear()
        driver.find_element(By.NAME, "cordenadasUtmY").clear()
        time.sleep(0.1)
        driver.find_element(By.NAME, "cordenadasUtmX").send_keys(cx)
        driver.find_element(By.NAME, "cordenadasUtmY").send_keys(cy)
        time.sleep(0.1)
        
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
        try:
            driver.find_element(By.XPATH, "//input[@value='Não']").click()
            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
        except:
            pass
        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            print(msg_ok)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(msg_er)
