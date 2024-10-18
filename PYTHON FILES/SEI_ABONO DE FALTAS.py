import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import os
import shutil
from db_login import sei_login, driver
from db_arquivos import elaboration, teste

df = pd.read_csv(elaboration)
sei_login()

for i in df.index:
    funcionario = str(df['FUNC'][i])
    driver.find_element(By.LINK_TEXT, "Iniciar Processo").click()
    driver.find_element(By.LINK_TEXT, "Abono de Faltas").click()
    driver.find_element(By.ID, "txtDescricao").send_keys("ABONO DE FALTAS - {}".format(funcionario))
    driver.find_element(By.ID, "txtInteressadoProcedimento").send_keys("")
    time.sleep(0.2)
    driver.find_element(By.ID, "txtAssunto").send_keys('FALTAS')
    time.sleep(1)
    driver.find_element(By.ID, "txtAssunto").send_keys(Keys.ARROW_DOWN, Keys.ENTER)
    time.sleep(0.2)
    driver.find_element(By.ID, "txtInteressadoProcedimento").send_keys("{}".format(funcionario))
    time.sleep(1.5)
    driver.find_element(By.ID, "txtInteressadoProcedimento").send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ENTER)
    time.sleep(0.2)
    driver.find_element(By.XPATH, "//label[@for='optRestrito']").click()
    hipotese = driver.find_element(By.ID, "selHipoteseLegal")
    hipotese.click()
    time.sleep(0.2)
    hipotese.send_keys('CONTROLE INTERNO', Keys.ENTER)        
    driver.find_element(By.NAME, "btnSalvar").click()  


    # time.sleep(3)
    # novo_doc = 1
    # driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/a[1]/img").click()#.format(novo_doc)).click()
    # time.sleep(1111)
    # driver.find_element(By.LINK_TEXT, "Abono de Faltas").click()
    # driver.find_element(By.ID, "txtDescricao").send_keys("ABONO DE FALTAS - {}".format(funcionario))
    # driver.find_element(By.ID, "txtInteressadoProcedimento").send_keys("")
    # time.sleep(0.2)
    # driver.find_element(By.ID, "txtAssunto").send_keys('FALTAS')
    # time.sleep(1)
    # driver.find_element(By.ID, "txtAssunto").send_keys(Keys.ARROW_DOWN, Keys.ENTER)
    # time.sleep(0.2)
    # driver.find_element(By.ID, "txtInteressadoProcedimento").send_keys("{}".format(funcionario))
    # time.sleep(1.5)
    # driver.find_element(By.ID, "txtInteressadoProcedimento").send_keys(Keys.ARROW_DOWN, Keys.ARROW_DOWN, Keys.ENTER)
    # time.sleep(0.2)
    # driver.find_element(By.XPATH, "//label[@for='optRestrito']").click()
    # hipotese = driver.find_element(By.ID, "selHipoteseLegal")
    # hipotese.click()
    # time.sleep(0.2)
    # hipotese.send_keys('CONTROLE INTERNO', Keys.ENTER)    
    # driver.find_element(By.NAME, "btnSalvar").click()  
    
    
    # time.sleep(11111)