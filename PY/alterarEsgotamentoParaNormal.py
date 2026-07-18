import time

from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, 'matriculaFiltro').send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.ID, "5").click()

    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass

    sit_esg = driver.find_element(By.NAME, "situacaoLigacaoEsgoto").text
    sit_esg = sit_esg.strip()

    f_abs = driver.find_element(By.NAME, "fonteAbastecimento")
    vf_abs = f_abs.get_attribute('value')
    if vf_abs == '-1':
        f_abs.send_keys('01 - CAEMA')

    res_inf = driver.find_element(By.NAME, "reservatorioInferior")
    v_res_inf = res_inf.get_attribute('value')
    if v_res_inf == '0,00':
        res_inf.clear()

    if sit_esg == '02 - FACTIVEL' or '03 - LIGADO':
        driver.find_element(By.NAME, "idLigacaoEsgotoEsgotamento").send_keys('NORMAL')
    elif sit_esg == '01 - POTENCIAL':
        pass

    area_const = driver.find_element(By.NAME, "areaConstruida")
    v_area_const = area_const.get_attribute('value')
    fx_area_const = driver.find_element(By.NAME, "faixaAreaConstruida").get_attribute('value')
    if fx_area_const != '-1':
        pass
    elif v_area_const == '0,00' or '':
        area_const.clear()
        area_const.send_keys('4800')

    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

    try:
        driver.find_element(By.XPATH, "//input[@value='Não']").click()
    except:
        pass


    msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
    msg_ok_t = bool(msg_ok)
    if msg_ok_t == True:
        print(i+1, msg_ok)
    elif msg_ok_t == False:
        msg_ero = driver.find_element(By.XPATH, "/html/body/div[1]/form/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i+1, msg_ero)
