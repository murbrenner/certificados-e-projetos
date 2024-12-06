import time, csv
import pandas as pd
from db_login import login, driver
from db_arquivos import teste, elaboration
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

df = pd.read_csv(elaboration)
login()

header = ['MATRICULA', 'MSG']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        matricula = str(df['MATRICULA'][i])
        if matricula != "0":
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "1").click()
            matricula = str(df['MATRICULA'][i])
            driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(matricula, Keys.ENTER)
            try:
                msg_exc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr/td[2]/strong/font").text
                msg_exc = msg_exc.replace('í', 'i')
                linha = matricula, msg_exc
                escritor.writerow(linha)
            except:
                linha = matricula, '(Ativo)'
                escritor.writerow(linha)            
        elif matricula == "0":
            linha = '0', '(Matrícula Zerada)'
            escritor.writerow(linha)
            pass