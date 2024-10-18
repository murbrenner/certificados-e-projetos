from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration

df = pd.read_csv(elaboration)
login()

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroOS').send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

for i in df.index:
    driver.find_element(By.NAME, 'numeroOSParametro').send_keys(str(df['OS'][i]))
    driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
    try:
        situacao = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        print(i + 1, str(df['OS'][i]), situacao)
    except:
        msg1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i + 1, str(df['OS'][i]), msg1)
        driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
        driver.find_element(By.NAME, 'numeroOSParametro').clear()
        pass
