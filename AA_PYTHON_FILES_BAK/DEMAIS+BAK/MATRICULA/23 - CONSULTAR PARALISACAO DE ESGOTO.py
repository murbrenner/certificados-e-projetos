from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

df = pd.read_csv('G:\\teste.csv')

driver = webdriver.Chrome()

def enter():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('7355')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, '2').click()
        driver.find_element(By.NAME, "idImovelDadosComplementares").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        print((str(df['MATRICULA'][i])), end=',')
        try:
            txt = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[1]/td[1]/div/font/a").text
            txt1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[1]/td[3]/div/font").text
            txt2 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[1]/td[4]/font").text
            print((str(txt)), end=',')
            print((str(txt1)), end=',')
            print((str(txt2)), end=',')

            txt3 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[2]/td[1]/div/font/a").text
            txt4 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[2]/td[3]/div/font").text
            txt5 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[2]/td[4]/font").text
            print((str(txt3)), end=',')
            print((str(txt4)), end=',')
            print((str(txt5)))

        except:
            try:
                txt6 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[3]/td[1]/div/font/a").text
                txt7 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[3]/td[3]/div/font").text
                txt8 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[12]/td/table[5]/tbody/tr[3]/td/div/table/tbody/tr[3]/td[4]/font").text
                print((str(txt6)), end=',')
                print((str(txt7)), end=',')
                print((str(txt8)))
            except NoSuchElementException:
                print("SEM (OUTRA) PARALISAÇÃO")



enter()

while True:
    pass

