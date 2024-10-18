import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, "matriculaFiltro").send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.ID, "2").click()
    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass
    #driver.find_element(By.PARTIAL_LINK_TEXT, " - ").click()
    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[5]/tbody/tr[2]/td/div/table/tbody/tr/td[1]/a/img").click()
    alert = driver.switch_to.alert
    alert.accept()
    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
    main_window_handle = driver.current_window_handle
    all_window_handles = driver.window_handles
    for handle in all_window_handles:
        if handle != main_window_handle:
            driver.switch_to.window(handle)
            driver.find_element(By.NAME, "logradouro").clear()
            driver.find_element(By.NAME, "logradouro").send_keys('28699', Keys.ENTER)
            driver.find_element(By.NAME, "bairro").send_keys('RS PLAN VINHAIS II')
            driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
            driver.find_element(By.NAME, "complemento").clear()
            driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))#('COND BELLA CITTA')#
            driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
        driver.switch_to.window(main_window_handle)
    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
    try:
        driver.find_element(By.XPATH, "//input[@value='Não']").click()
    except:
        pass
    msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
    print(msg_ok)