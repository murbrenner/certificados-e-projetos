import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elab_date

hoje = date.today()
hoje = hoje.strftime("%d/%m/%Y")

df = pd.read_csv(elab_date)
login()

for i in df.index:
    inicio = str(df['INICIO'][i])
    fim = str(df['FIM'][i])
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    situacao = driver.find_element(By.XPATH, "//input[@value='1']").click()
    driver.find_element(By.XPATH, "//option[@value='78']").click()
    #driver.find_element(By.XPATH, "//option[@value='1']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//option[@value='970']").click()
    #driver.find_element(By.XPATH, "//option[@value='9176']").click()
    #time.sleep(1111)
    driver.find_element(By.NAME, "periodoAtendimentoInicial").clear()
    driver.find_element(By.NAME, "periodoAtendimentoInicial").send_keys(inicio)
    driver.find_element(By.NAME, "periodoAtendimentoFinal").clear()
    driver.find_element(By.NAME, "periodoAtendimentoFinal").send_keys(fim)
    #driver.find_element(By.NAME, "periodoEncerramentoInicial").clear()
    #driver.find_element(By.NAME, "periodoEncerramentoInicial").clear()
    #driver.find_element(By.NAME, "periodoEncerramentoFinal").clear()
    #driver.find_element(By.NAME, "periodoEncerramentoFinal").clear()
    driver.find_element(By.NAME, "municipioId").send_keys('1', Keys.ENTER)
    time.sleep(1)

    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[2]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[3]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[10]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[17]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[18]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[19]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[20]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[21]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[32]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[36]").click()
    driver.find_element(By.XPATH,
                        "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[25]/td[2]/span/strong/select/option[13]").click()

    #driver.find_element(By.NAME, "unidadeAtualId").send_keys("38")
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        driver.find_element(By.NAME, "ButtonImprimirTodasOs").click()
    except:
        pass
    time.sleep(1)
