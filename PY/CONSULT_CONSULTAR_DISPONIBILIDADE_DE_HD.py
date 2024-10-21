from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import abrir_ra, teste, elaboration
from db_login import login, driver
import time

df = pd.read_csv(elaboration)
login()

for i in df.index:
    num_hd = str(df['HIDROMETRO'][i])
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarHistoricoInstalacaoHidrometroInformarAction.do?menu=sim")
    driver.find_element(By.NAME, "codigoHidrometro").send_keys(num_hd, Keys.ENTER)
    sit_hd = driver.find_element(By.NAME, "descricaoHidrometro").get_attribute('value')
    driver.find_element(By.XPATH, f"//*[@value='Consultar']").click()
    if sit_hd == "Hidrômetro Inexistente":
        print(i+1, "SITUACAO HD {}: {} ".format(num_hd, sit_hd))
    else:        
        matricula = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[2]/table[4]/tbody/tr/td/table/tbody/tr[3]/td[1]/div/a").text
        hd_ok = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[1]/td/table/tbody/tr[3]/td[8]/div").text   
        if hd_ok == "INSTALADO ":
            print(i+1, "SITUACAO HD {}: {}NA MATRICULA {}".format(num_hd, hd_ok, matricula))
        elif hd_ok == "DISPONIVEL ":
            print(i+1, "SITUACAO HD {}: {} ".format(num_hd, hd_ok)) 
                    
    
    
     