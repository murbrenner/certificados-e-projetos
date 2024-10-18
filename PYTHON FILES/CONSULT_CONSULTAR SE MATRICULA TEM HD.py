from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, abrir_ra

df = pd.read_csv(elaboration)
login()

for i in df.index:    
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    roteirizacao = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
    if roteirizacao != 'IMÓVEL INEXISTENTE':
        try:
            categoria = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/div/font").text
            categoria = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[2]/div/font").text
            categoria2 = driver.find_element(By.XPATH, f"/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td[2]/div/font").text
            print(i+1, str(df['MATRICULA'][i]), categoria, categoria2, sep=',') 
        except:  
            print(i+1, str(df['MATRICULA'][i]), categoria, sep=',') 
            pass      
                     
    else:
        print(i+1, str(df['MATRICULA'][i]), 'IMÓVEL INEXISTENTE', sep=',')
        pass
