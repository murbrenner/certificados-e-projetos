from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, murilo2, login2, driver
from arquivos import elaboration, teste, abrir_ra
import csv, re, time, pyautogui

df = pd.read_csv(elaboration)
murilo2()

header = ['RA', 'ANEXO']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)    

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][0]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

    for i in df.index:        
        rra = str(df['RA'][i])
        driver.find_element(By.NAME, "numeroRA").send_keys(rra)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        driver.find_element(By.LINK_TEXT, "Dados do local da ocorrência").click()
        
        linha = "{}".format(rra), "NAO"
        escritor.writerow(linha)