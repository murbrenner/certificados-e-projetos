import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration

df = pd.read_csv(elaboration)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirQuadraAction.do?menu=sim")

    local = int(df['LOCAL'][i])
    grupo = int(df['GRUPO'][i])
    quadra = int(df['QUADRA'][i])
    rota = int(df['ROTA'][i])
    cod_bairro = int(df['COD_BAIRRO'][i])

    z1_centro = 1
    z2_mte_cast = 2   
    z3_cohab = 3 	
    z4_tir = 4 
    z5a_calhau = 5
    z5b_cohama = 6
    z5c_olho = 7
    z6a_ufma = 8
    z6b_anjo = 9
    z7a_maiob = 10
    z7b_cid_op = 11
    z99_br135 = 12

    driver.find_element(By.NAME, "localidadeID").send_keys(local, Keys.ENTER)
    driver.find_element(By.NAME, "setorComercialCD").send_keys(grupo, Keys.ENTER)
    driver.find_element(By.NAME, "quadraNM").clear()
    driver.find_element(By.NAME, "quadraNM").send_keys(quadra, Keys.ENTER)
    driver.find_element(By.NAME, "codigoRota").send_keys(rota, Keys.ENTER)
    driver.find_element(By.NAME, "bairroID").send_keys(cod_bairro, Keys.ENTER)

    driver.find_element(By.XPATH, "//input[@name='indicadorIncrementoLote' and @value='2']").click()
    driver.find_element(By.NAME, "areaTipoID").send_keys('URBANA')
    time.sleep(0.2)
    driver.find_element(By.NAME, "perfilQuadra").send_keys('NORMAL')
    time.sleep(0.2)
    driver.find_element(By.XPATH, "//input[@name='indicadorRedeAguaAux' and @value='3']").click()
    driver.find_element(By.XPATH, "//input[@name='indicadorRedeEsgotoAux' and @value='3']").click()
    driver.find_element(By.NAME, "sistemaEsgotoID").send_keys('SIS01')
    time.sleep(0.2)
    driver.find_element(By.NAME, "baciaID").send_keys('BACIA 1')
    time.sleep(0.2)
    driver.find_element(By.NAME, "distritoOperacionalID").send_keys(z5c_olho, Keys.ENTER)
    driver.find_element(By.NAME, "setorCensitarioID").send_keys('1', Keys.ENTER)
    driver.find_element(By.NAME, "zeisID").send_keys('ZEIS 1')    
    driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
    try:
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text    
        print(i+1, quadra, msg_ok)
    except:
        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i + 1, quadra, msg_er)