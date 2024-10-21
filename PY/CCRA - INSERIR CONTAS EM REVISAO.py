import time, re

import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration

df = pd.read_csv(elaboration)
login()


for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirManterContaAction.do?menu=sim")
    driver.find_element(By.NAME, 'idImovel').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    time.sleep(0.5)

    try:
        mes11 = driver.find_element(By.PARTIAL_LINK_TEXT, "03/2024").get_attribute('href')
        driver.find_element(By.PARTIAL_LINK_TEXT, "03/2024").send_keys('')

        pyautogui.keyDown('Shift')
        pyautogui.keyDown('Tab')
        pyautogui.keyUp('Shift')
        pyautogui.keyUp('Tab')
        pyautogui.keyDown('Space')
        pyautogui.keyUp('Space')
        driver.find_element(By.XPATH, "//input[@value='Colocar Revisão']").click()
        time.sleep(1111)
        janela1 = driver.window_handles[0]
        janela2 = driver.window_handles[1]
        driver.switch_to.window(janela2)
        time.sleep(0.2)
        driver.find_element(By.NAME, "motivoRevisaoContaID").send_keys("REVISAO POR PROCESSO JUDICIAL")
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
        time.sleep(0.2)
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(0.3)
        driver.switch_to.window(janela1)
        print(i+1, str(df['MATRICULA'][i]), "OK")
    except:
        print(i + 1, str(df['MATRICULA'][i]), "11/2022 NAO ENCONTRADO")
        pass