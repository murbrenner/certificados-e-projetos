from selenium.webdriver.common.by import By
import pandas as pd
from login import murilo2, driver
from arquivos import inserir_imovel, elaboration
from funcoes import cpf_ok, cnpj_ok

df = pd.read_csv(inserir_imovel)
murilo2()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")
    cpf = str(df['CPF'][i])
    cpf = cpf_ok(cpf)

    if len(cpf) == 11:
        cpf = cpf_ok(cpf)
        driver.find_element(By.NAME, "cpfClienteFiltro").send_keys(cpf)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()


    if cpf == '00000000000':
        print("Cliente com CPF invalido".format(cpf))

    else:
        try:
            j = 1
            while j < 10:
                try:
                    num_cod = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[3]/td/table[1]/tbody/tr[{}]/td[2]".format(j)).text
                    print(num_cod, sep=',')
                    print("O numero de CPF {} possui mais de um código.".format(cpf))
                except:
                    break
                j = j + 1
        except:
            j = j + 1
            pass

    try:
        codigo = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
        print(i+1,"Cliente de CPF {} ja possui código nº: {}".format(cpf, codigo))
    except:
        try:
            msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i+1, msg_err)
        except:
            print(i+1, "????")
            pass







