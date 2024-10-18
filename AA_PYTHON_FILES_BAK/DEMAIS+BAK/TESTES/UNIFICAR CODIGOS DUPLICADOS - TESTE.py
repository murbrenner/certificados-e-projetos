import time
from selenium.webdriver.common.by import By
import pandas as pd
from login import driver, murilo
from arquivos import elaboration, teste
import csv

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim')
    driver.find_element(By.XPATH, "//img[@title='Pesquisar Imóvel']").click()
    main_window_handle = driver.current_window_handle
    all_window_handles = driver.window_handles
    for handle in all_window_handles:
        if handle != main_window_handle:
            driver.switch_to.window(handle)
            driver.find_element(By.XPATH, "//img[@title='Pesquisar Cliente']").click()
            driver.find_element(By.NAME, "cpf").send_keys(str(df['CPF']))
            driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
            j = 2
            while j < 10:
                try:
                    cod = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[{}]/td[1]".format(j)).text
                    cod.df.index[j] = cod
                    print(cod.df.index[j])
                except:
                    pass
                j += 1

