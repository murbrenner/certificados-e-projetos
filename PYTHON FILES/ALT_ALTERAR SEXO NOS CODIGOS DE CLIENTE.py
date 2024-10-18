import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste
from db_funcoes import cpf_ok
import csv

df = pd.read_csv(elaboration)
login()

cabeçalho = ['#', 'MSG', 'COD']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        cod_cliente = int(df['COD_CLIENTE'][i])
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")
        driver.find_element(By.NAME, "codigoClienteFiltro").send_keys(cod_cliente)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        driver.find_element(By.ID, "2").click()
        driver.find_element(By.NAME, "idPessoaSexo").send_keys("01 - MASCULINO")
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            print(i+1, msg_ok, "[{}]".format(cod_cliente))
            linha = i+1, msg_ok, "[{}]".format(cod_cliente)
            escritor.writerow(linha)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text     
            print(i+1, msg_ok, "[{}]".format(cod_cliente))  
            linha = i+1, msg_er, "[{}]".format(cod_cliente)
            escritor.writerow(linha)       
            pass