from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, abrir_ra

df = pd.read_csv(elaboration)
login()

for i in df.index:       
    mat = int(df['MATRICULA'][i]) 
    if mat != 0:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "3").click()
        driver.find_element(By.NAME, "idImovelAnaliseMedicaoConsumo").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        status_hd = driver.find_element(By.NAME, "tipoLigacaoAnaliseMedicaoConsumo").get_attribute('value')
        numero_hd = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[5]/td/table/tbody/tr[3]/td[3]/a").text
        print(i+1, mat, status_hd, numero_hd)
    elif mat == 0:
        print(i+1, '0', '0', '0')