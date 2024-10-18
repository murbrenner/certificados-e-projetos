import time
import re
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.common import NoSuchElementException

filename = 'C:\\Users\\Murilo Brenner\\Downloads\\CREDITO - SEDUC.csv'
df = pd.read_csv(filename)

driver = webdriver.Chrome()
login = "http://gsan.caema.ma.gov.br:8080/gsan"
url1 = "http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim"

def enter():
    driver.get(login)
    driver.find_element(By.NAME, 'login').send_keys('LUIZD')
    driver.find_element(By.NAME, 'senha').send_keys('223906')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    for i in df.index:
        driver.get(url1)
        driver.find_element(By.NAME, "tipoSolicitacao").send_keys('1.02')
        driver.find_element(By.NAME, "especificacao").send_keys('DEVOLUCAO DE PAGAMENTO')
        driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))
        driver.find_element(By.NAME, "avancar").click()
        driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        time.sleep(0.7)
        print((str(df['MATRICULA'][i])), end=',')

        try:
            pyautogui.press('esc')
            pyautogui.keyUp('esc')
            driver.find_element(By.NAME, "avancar").click()
            driver.find_element(By.NAME, "avancar").click()
            driver.find_element(By.NAME, "concluir").click()
            print("R.A ABERTA", end=',')
            regatend = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            raok = re.sub(r'[^0-9]', '', regatend)
            print(raok)


        except NoSuchElementException:
            try:
                driver.find_element(By.NAME, "botaoVoltar").click()
                driver.find_element(By.NAME, "cancelar").click()
                print("JA EXISTE PENDENTE")
            except NoSuchElementException:
                print("DEU ERRO")
                pyautogui.press('F5')
                pyautogui.keyUp('F5')
                driver.find_element(By.NAME, "botaoVoltar").click()
                break


enter()

while True:
    pass