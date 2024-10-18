import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, 'matriculaFiltro').send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.ID, "3").click()
    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass
    try:
        tipo_cliente = driver.find_element(By.XPATH,"//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[5]/div").text
        if tipo_cliente == "USUARIO":
            date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[6]").text
    except:
        pass
    j = 1
    while j < 4:
        try:
            tipo_cliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[5]/div".format(j)).text
            print(tipo_cliente)
            if tipo_cliente == "USUARIO":
                print('aaaa')
                date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[6]".format(j)).text
                print(date_inicio_rel)
                driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/div/input".format(j)).click()

        except:
            break
        j = j + 1
    driver.find_element(By.XPATH, "//input[@value='Remover']").click()

    alert = driver.switch_to.alert
    alert = alert.accept()
    time.sleep(1)
    handle = driver.window_handles[1]
    driver.switch_to.window(handle)
    time.sleep(1)
    driver.find_element(By.NAME, 'dataTerminoRelacao').send_keys(date_inicio_rel)
    driver.find_element(By.NAME, 'idMotivo').send_keys('ATUALIZ. CADASTRAL')
    driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()

    time.sleep(11111)





