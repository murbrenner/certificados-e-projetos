import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elab_date

df = pd.read_csv(elab_date)
login()

hoje = date.today()
hoje = hoje.strftime("%d/%m/%Y")

contador = 1

for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "situacaoOrdemServico").send_keys("PENDENTES")
    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[8]/td[2]/input[1]")
    #driver.find_element(By.XPATH, "//option[@value='613']").click()
    driver.find_element(By.XPATH, "//option[@value='91']").click()
    #driver.find_element(By.XPATH, "//option[@value='890']").click()
    #driver.find_element(By.XPATH, "//option[@value='9125']").click()
    driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
    driver.find_element(By.NAME, "periodoGeracaoInicial").clear()
    driver.find_element(By.NAME, "periodoGeracaoInicial").send_keys(str(df['INICIO'][i]))
    driver.find_element(By.NAME, "periodoGeracaoFinal").clear()
    driver.find_element(By.NAME, "periodoGeracaoFinal").send_keys(str(df['FIM'][i]))
    driver.find_element(By.NAME, "municipio").send_keys("1"), Keys.ENTER
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        driver.find_element(By.XPATH, "//img[@title='Imprimir Ordens de Serviço']").click()
        driver.find_element(By.XPATH, "//input[@value='6']").click()
        #driver.find_element(By.XPATH, "//input[@value='1']").click()
        driver.find_element(By.XPATH, "//input[@value='Gerar']").click()
        print("MÊS {}/{} GERADO".format(contador, str(df['ANO'][i])))
    except:
        print("MÊS {}/{} SEM O.S".format(contador, str(df['ANO'][i])))
        pass
    contador += 1

    if contador > 12:
        contador = 1
    else:
        pass
    time.sleep(1)