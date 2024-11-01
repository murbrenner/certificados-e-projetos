import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import inserir_imovel, elaboration

df = pd.read_csv(inserir_imovel)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    matricula = str(df['MATRICULA'][i])
    alterar = str(df['ALTERAR'][i])
    cep_gsan = int(df['CEP_GSAN'][i]) 
    complemento = str(df['COMPLEMENTO'][i])
    if alterar == '1':
        driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        driver.find_element(By.ID, "2").click()
        try:
            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
        except:
            pass
        driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[5]/tbody/tr[2]/td/div/table/tbody/tr/td[1]/a/img").click()
        alert = driver.switch_to.alert
        alert.accept()
        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        main_window_handle = driver.current_window_handle
        all_window_handles = driver.window_handles
        for handle in all_window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                time.sleep(0.2)
                driver.find_element(By.NAME, "logradouro").send_keys(str(df['COD_LOG'][i]), Keys.ENTER)
                time.sleep(0.2)
                driver.find_element(By.XPATH, "//input[@value='{}']".format(cep_gsan)).click()
                time.sleep(0.2)
                driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
                time.sleep(0.2)
                driver.find_element(By.NAME, "enderecoReferencia").send_keys('01 - NUMERO')
                time.sleep(0.2)
                driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i])) 
                time.sleep(0.2)
                if complemento != '0':
                    driver.find_element(By.NAME, "complemento").send_keys(complemento)
                    time.sleep(0.2)
                driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
            driver.switch_to.window(main_window_handle)    
            time.sleep(0.2)
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
        try:
            driver.find_element(By.XPATH, "//input[@value='Não']").click()
            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
        except:
            pass
        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            print(i+1, matricula, msg_ok)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i+1, matricula, msg_er)
    elif alterar == '0':
        print(i+1, 'Imóvel de matrícula [{}] ja está com o endereço atualizado!'.format(matricula))