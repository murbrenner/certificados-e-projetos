import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel, elaboration, teste
from funcoes import cpf_ok
import csv

df = pd.read_csv(elaboration)
murilo()


for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarClienteAction.do?menu=sim")
    cpf = str(df['CPF'][i])
    cpf = cpf_ok(cpf)

    driver.find_element(By.NAME, "cpfClienteFiltro").send_keys(cpf)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

    try:
        time.sleep(0.3)
        alert = driver.switch_to.alert
        alert.accept()
        alert = bool(alert)
        if alert is True:
            if cpf != '00000000000':
                print(i + 1, "Cliente com CPF [{}] inválido.".format(cpf))
    except:
        pass

    if cpf == '00000000000':
        print(i + 1, "Cliente com CPF [{}] inválido.".format(cpf))

    else:
        try:
            j = 1
            while j < 10:
                try:
                    num_cod = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[3]/td/table[1]/tbody/tr[{}]/td[2]".format(j)).text
                    print(num_cod, sep=',')
                    print(i + 1, "O numero de CPF [{}] possui mais de um código.".format(cpf))
                except:
                    break
                j = j + 1
        except:
            j = j + 1
            pass

    try:
        codigo = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
        nome = driver.find_element(By.NAME, "nome").get_attribute('value')
        print(i + 1, "Cliente de CPF {} ja possui código nº: [{}]".format(cpf, codigo), nome)
    except:
        try:
            msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i + 1, msg_err)
        except:
            pass







