import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, murilo2
from arquivos import inserir_imovel, teste, elaboration
from funcoes import cpf_ok
import csv

df = pd.read_csv(elaboration)
murilo2()

for i in df.index:
    roteiro = "{}/{}".format(str(df['SETOR'][i]), str(df['ROTA'][i]))
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirGerarRoteiroDispositivoMovelAction.do?menu=sim")
    driver.find_element(By.NAME, "idEmpresa").send_keys('MG SETEL')
    try:
        driver.find_element(By.NAME, "idLocalidade").send_keys(str(df['LOCAL'][i]))#CENTRO, COHAB, VINHAIS...        
        driver.find_element(By.NAME, "codigoSetorComercial").send_keys(str(df['SETOR'][i]))#102,103,104... 
        time.sleep(1)       
        try:
            driver.find_element(By.XPATH, "//option[@value='{}']".format(str(df['QUADRA'][i]))).click()
        except:
            driver.find_element(By.XPATH, "//option[@value='{}']".format(str(df['ROTA'][i]))).click()
        
        driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
        
        driver.find_element(By.XPATH, "//input[@name='clienteUsuario' and @value='2']").click()
        driver.find_element(By.XPATH, "//input[@name='indicadorSituacaoImovel' and @value='1']").click()
        driver.find_element(By.XPATH, "//input[@name='indicadorSituacaoImovel' and @value='2']").click()
        driver.find_element(By.XPATH, "//input[@name='indicadorSituacaoImovel' and @value='3']").click()
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        time.sleep(1)
        driver.find_element(By.NAME, "cadastrador").send_keys('DENILSON DIEL')
        driver.find_element(By.PARTIAL_LINK_TEXT, "Todos").click()
        time.sleep(111111)        
        #driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(i+1, roteiro, msg_ok) 
    except:
        err0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i+1, roteiro, err0)               
        pass
