import time
import os
import shutil
from datetime import date
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration
from db_fiscais import num_nomes, num_nomes_joined

data = date.today().strftime("%d/%m/%Y")
data_dash = date.today().strftime("%d-%m-%Y")
df = pd.read_csv(elaboration)
login()

for i in num_nomes:
    pasta_fiscal = "C:\\Users\\Murilo\\Desktop\\SERVICO {}\\{}".format(data_dash, num_nomes[i])

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(data))
    driver.find_element(By.LINK_TEXT, "{}".format(num_nomes[i])).click()
    driver.find_element(By.LINK_TEXT, 'Todos').click()
    driver.find_element(By.XPATH, "//input[@value='Imprimir OS']").click()
    time.sleep(1)
    os.makedirs(pasta_fiscal)
