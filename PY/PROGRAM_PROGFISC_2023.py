from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import prog_fisc, teste, elaboration
from db_fiscais import fiscais
import time

df = pd.read_csv(elaboration)
login()

today = datetime.today()
tomorrow = datetime.today() + timedelta(days=1)
segunda = datetime.today() + timedelta(days=3)
another_day = datetime.today() + timedelta(days=2)
data_prog = tomorrow
data_prog = data_prog.strftime("%d/%m/%Y")

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirElaborarOrdemServicoRoteiroCriteriosAction.do?menu=sim&filtro=0&dataRoteiro={}".format(data_prog))
try:
    driver.find_element(By.XPATH, "//option[@value='613']").click()
    driver.find_element(By.XPATH, "//option[@value='890']").click()
    driver.find_element(By.XPATH, "//option[@value='9125']").click()
except:
    pass
driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()

for i in df.index:
    fiscal = fiscais['{}'.format(df['FISCAL'][i])]
    driver.find_element(By.XPATH, "//option[@value='{}']".format(fiscal)).click()

    driver.find_element(By.XPATH, "//input[@value='  >  ']").click()

    try:
        driver.find_element(By.XPATH, "//input[@value='{}']".format(str(df['OS'][i]))).click()
        driver.find_element(By.XPATH, "//input[@value='Programar']").click()
        j = i + 1
        print(j, "Ordem de serviço {} programada com sucesso!".format(str(df['OS'][i])))
    except:
        j = i + 1
        print(j, "Ordem de serviço {} não localizada. Falha na programação.".format(str(df['OS'][i])))
        driver.find_element(By.XPATH, "//input[@value=' << ']").click()
        pass

driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
