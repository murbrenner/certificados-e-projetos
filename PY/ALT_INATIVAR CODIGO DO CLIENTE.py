from selenium.webdriver.common.by import By
from db_arquivos import teste, elaboration
from db_login import login, driver
import pandas as pd
from datetime import datetime, timedelta
import EXC_EXCLUIR_CODIGO_DE_CLIENTE as del_cod
import time

df = pd.read_csv(elaboration)
login()


for i in df.index:
    cod_cliente = int(df['COD_CLIENTE'][i])

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/ExibirConsultarRelacaoClienteImovelAction.do?menu=sim")
    time.sleep(11111)
    
    # driver.find_element(By.NAME, "idCliente").send_keys(cod_cliente)
    # driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    # time.sleep(11111)
    # try:
    #     msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
    #     print(i+1, cod_cliente, msg_er)
    #     v_msg_er = 1
    # except:
    #     v_msg_er = 0
    #     pass

    # if v_msg_er == 1:
    #     print("del_cod")
    #     time.sleep(11111)
    #     #del_cod()
    # elif v_msg_er == 0:
    #     print("DEU CERTO NAO")
    #     time.sleep(11111)
        
