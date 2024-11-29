from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import inserir_imovel, teste, elaboration
from db_funcoes import cpf_ok, cnpj_ok
import csv

df = pd.read_csv(inserir_imovel)
login()

header = ['#', 'MSG']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")
        cpf = str(df['CPF'][i])
        v_cpf = int(df['V_CPF'][i])
        v_cnpj = int(df['V_CNPJ'][i])

        if v_cpf == 1:
            cpf = cpf_ok(cpf)
            driver.find_element(By.NAME, "cpfClienteFiltro").send_keys(cpf)
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
            
                

            try:
                popup = driver.switch_to.alert
                popup.accept()
                linha = i+1, "Cliente com CPF {} invalido".format(cpf)
                escritor.writerow(linha)
            except:                
                try:
                    msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                    linha = i+1, msg_err
                    escritor.writerow(linha)
                except:
                    pass    
            try:
                if cpf == '00000000000':
                    linha = i+1, "Cliente com CPF {} zerado".format(cpf)
                    escritor.writerow(linha)
                if cpf == '00000000000000':
                    linha = i+1, "Cliente com CPF {} zerado".format(cpf)
                    escritor.writerow(linha)           
            except:
                codigo = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
                linha = i+1,"Cliente de CPF {} ja possui código nº: {}".format(cpf, codigo)
                escritor.writerow(linha)
                pass

            j = 1
            while j < 10:
                try:
                    num_cod = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[3]/td/table[1]/tbody/tr[{}]/td[2]".format(j)).text
                    linha = i+1,"Cliente de CPF {} possui mais de um código".format(cpf)
                    escritor.writerow(linha)                
                except:                
                    pass
                j = j + 1