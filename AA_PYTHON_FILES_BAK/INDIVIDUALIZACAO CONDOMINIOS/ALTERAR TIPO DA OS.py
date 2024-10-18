from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import teste
from login import murilo, driver

df = pd.read_csv(teste)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()
    driver.find_element(By.NAME, "idServicoTipo").clear()
    driver.find_element(By.NAME, "idServicoTipo").send_keys('92', Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()
    try:
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(i + 1, msg_ok, sep=';')
    except:
        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i + 1, str(df['MATRICULA'][i]), msg_er, sep=';')
        pass