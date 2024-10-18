import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel, elaboration

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")
    cpf = str(df['CPF'][i])

    if len(cpf) == 11:
        cpf_ok = str(df['CPF'][i])

    if len(cpf) == 10:
        cpf_ok = '0' + str(df['CPF'][i])

    elif len(cpf) == 9:
        cpf_ok = '00' + str(df['CPF'][i])

    elif len(cpf) == 8:
        cpf_ok = '000' + str(df['CPF'][i])

    elif len(cpf) == 7:
        cpf_ok = '0000' + str(df['CPF'][i])

    elif len(cpf) == 6:
        cpf_ok = '00000' + str(df['CPF'][i])

    elif len(cpf) == 5:
        cpf_ok = '000000' + str(df['CPF'][i])

    elif len(cpf) == 4:
        cpf_ok = '0000000' + str(df['CPF'][i])

    elif len(cpf) == 3:
        cpf_ok = '00000000' + str(df['CPF'][i])

    elif len(cpf) == 2:
        cpf_ok = '000000000' + str(df['CPF'][i])

    elif len(cpf) == 1:
        cpf_ok = '0000000000' + str(df['CPF'][i])

    elif len(cpf) == 0:
        cpf_ok = '00000000000' + str(df['CPF'][i])

    driver.find_element(By.NAME, "cpfClienteFiltro").send_keys(cpf_ok)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

    try:
        codigo = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
        print("Cliente de CPF {} ja possui código nº: {}".format(cpf_ok, codigo))
    except:
        try:
            msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(msg_err)
        except:
            print("O numero de CPF {} é inválido".format(cpf_ok))



