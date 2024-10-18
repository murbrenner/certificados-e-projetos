from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import elaboration

df = pd.read_csv(elaboration)

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
        driver.find_element(By.ID, '1').click()
        driver.find_element(By.NAME, 'idImovelDadosCadastrais').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[4]/td/a/strong").click()
        driver.find_element(By.ID, '5').click()
        driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('04')
        driver.find_element(By.NAME, 'concluir').click()
        driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[5]/td/a/strong").click()
        driver.find_element(By.ID, '1').click()
        txt = driver.find_element(By.NAME, "tipoHabitacaoDadosCadastrais").get_attribute('value')
        print((str(df['MATRICULA'][i])), end=',')
        print((str(txt)))


enter()

while True:
    pass

