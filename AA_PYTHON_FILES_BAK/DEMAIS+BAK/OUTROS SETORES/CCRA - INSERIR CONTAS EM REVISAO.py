import time, re

import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import login, driver, murilo
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()


for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirManterContaAction.do?menu=sim")
    driver.find_element(By.NAME, 'idImovel').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    time.sleep(0.5)

    try:
        mes11 = driver.find_element(By.PARTIAL_LINK_TEXT, "03/2024").get_attribute('href')
        time.sleep(1111)
        driver.find_element(By.PARTIAL_LINK_TEXT, "11/2022").send_keys('')
        pyautogui.keyDown('Shift')
        pyautogui.keyDown('Tab')
        pyautogui.keyUp('Shift')
        pyautogui.keyUp('Tab')
        pyautogui.keyDown('Space')
        pyautogui.keyUp('Space')
        driver.find_element(By.XPATH, "//input[@value='Colocar Revisão']").click()
        main_window_handle = driver.current_window_handle
        all_window_handles = driver.window_handles
        for handle in all_window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
        time.sleep(0.2)
        driver.find_element(By.NAME, "motivoRevisaoContaID").send_keys("REVISAO POR PROCESSO JUDICIAL")
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
        time.sleep(0.2)
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(0.3)
        driver.switch_to.window(main_window_handle)
        print(i+1, str(df['MATRICULA'][i]), "OK")
    except:
        print(i + 1, str(df['MATRICULA'][i]), "11/2022 NAO ENCONTRADO")
        pass