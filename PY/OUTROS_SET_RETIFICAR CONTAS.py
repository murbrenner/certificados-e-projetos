import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration

df = pd.read_csv(elaboration)
login()

for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirManterContaAction.do?menu=sim")
    driver.find_element(By.NAME, 'idImovel').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    time.sleep(0.2)
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT, "03/2024").click()
        driver.find_element(By.NAME, "motivoRetificacaoID").send_keys('COBRANCA INDEVIDA DE SERVICOS')
        driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))
        driver.find_element(By.NAME, "consumoAgua").clear()
        driver.find_element(By.NAME, "consumoAgua").send_keys('10')#(str(df['CONSUMO_AGUA'][i]))
        driver.find_element(By.NAME, "consumoEsgoto").clear()
        driver.find_element(By.NAME, "consumoEsgoto").send_keys('10')#(str(df['CONSUMO_ESGOTO'][i]))
        driver.find_element(By.XPATH, "//input[@value='Calcular']").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//input[@value='Retificar']").click()
        alert = driver.switch_to.alert
        alert.accept()
        driver.find_element(By.XPATH, "//input[@value='Sim']").click()
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(i+1, msg_ok)
    except:
        erro1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i+1, erro1)
        pass