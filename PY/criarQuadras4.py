import time, csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *

df = pd.read_csv(databaseCSV4)
login()

relatorioGsan = relatorioGsan4

header = ['#', 'QUADRA', 'MENSAGEM']

with open(databaseCSV4, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)   

    for i in df.index:
        contador = i+1
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirQuadraAction.do?menu=sim")
        local = int(df['LOCAL'][i])
        setor = int(df['SETOR'][i])
        quadra = int(df['QUADRA'][i])    
        rota = int(df['ROTA'][i])    
        cod_bairro = 50
        esgoto = 'nao'
        dist_op_interior = local
        
        driver.find_element(By.NAME, "localidadeID").send_keys(local, Keys.ENTER)
        time.sleep(0.5)
        driver.find_element(By.NAME, "setorComercialCD").send_keys(setor, Keys.ENTER)
        time.sleep(0.5)
        driver.find_element(By.NAME, "quadraNM").clear()
        time.sleep(0.5)
        driver.find_element(By.NAME, "quadraNM").send_keys(quadra)
        time.sleep(0.5)
        driver.find_element(By.NAME, "codigoRota").send_keys(rota, Keys.ENTER)
        time.sleep(0.5)
        driver.find_element(By.NAME, "bairroID").send_keys(cod_bairro, Keys.ENTER)
        time.sleep(0.5)

        driver.find_element(By.XPATH, "//input[@name='indicadorIncrementoLote' and @value='2']").click()
        driver.find_element(By.NAME, "areaTipoID").send_keys('URBANA')
        time.sleep(0.2)
        driver.find_element(By.NAME, "perfilQuadra").send_keys('NORMAL')
        time.sleep(0.2)
        driver.find_element(By.XPATH, "//input[@name='indicadorRedeAguaAux' and @value='3']").click()

        if esgoto == 'sim':
            driver.find_element(By.XPATH, "//input[@name='indicadorRedeEsgotoAux' and @value='3']").click()    
            driver.find_element(By.NAME, "sistemaEsgotoID").send_keys('SIS01')
            time.sleep(0.2)
            driver.find_element(By.NAME, "baciaID").send_keys('BACIA 1')
            time.sleep(0.2)
        elif esgoto != 'sim':
            driver.find_element(By.XPATH, "//input[@name='indicadorRedeEsgotoAux' and @value='1']").click()
        
        driver.find_element(By.NAME, "distritoOperacionalID").send_keys(dist_op_interior, Keys.ENTER)
        time.sleep(0.5)
        driver.find_element(By.NAME, "setorCensitarioID").send_keys('1', Keys.ENTER)
        time.sleep(0.5) 
        driver.find_element(By.NAME, "zeisID").send_keys('ZEIS 1')  
        
        
        driver.find_element(By.XPATH, "//input[@value='Inserir']").click()

        time.sleep(0.3)
        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text    
            print(i+1, quadra, msg_ok)
            row = i+1, quadra, msg_ok
            writer.writerow(row)
            time.sleep(0.3)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i + 1, quadra, msg_er)
            row = i+1, quadra, msg_er
            writer.writerow(row)
            time.sleep(0.3)

        percent1 = ((contador-1)*100)/totalRow
        percent1 = int(percent1)
        percent2 = (contador*100)/totalRow
        percent2 = int(percent2)
        if percent1 != percent2:            
            if percent2 != 100:
                print(f'{percent2}% CONCLUÍDO...')
            else:
                print(f'{percent2}% CONCLUÍDO!')
        

        
        # 
        # z1_centro = 1
        # z2_mte_cast = 2   
        # z3_cohab = 3 	
        # z4_tir = 4 
        # z5a_calhau = 5
        # z5b_cohama = 6
        # z5c_olho = 7
        # z6a_ufma = 8
        # z6b_anjo = 9
        # z7a_maiob = 10
        # z7b_cid_op = 11
        # z99_br135 = 12