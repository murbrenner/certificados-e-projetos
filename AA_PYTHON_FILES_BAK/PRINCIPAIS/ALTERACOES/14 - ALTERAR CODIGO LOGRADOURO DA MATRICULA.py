import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, "matriculaFiltro").send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.ID, "2").click()
    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass
    time.sleep(0.5)
    driver.find_element(By.XPATH, "//img[@src='/gsan/imagens/Error.gif']").click()
    alert = driver.switch_to.alert
    alert.accept()
    #driver.find_element(By.PARTIAL_LINK_TEXT, " - ").click()
    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
    janela = driver.window_handles[0]
    popup = driver.window_handles[1]
    driver.switch_to.window(popup)
    #driver.find_element(By.NAME, "logradouro").clear()
    driver.find_element(By.NAME, "logradouro").send_keys(int(df['COD_LOG'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='5720']").click()

    driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
    #driver.find_element(By.NAME, "enderecoReferencia").click()
    driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
    complemento = int(df['COMPLEMENTO'][i])
    if complemento != 0:
        driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))
    driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
    driver.switch_to.window(janela)
    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
    try:
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(msg_ok)
    except:
        msg_ero = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(msg_ero)