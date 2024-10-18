from selenium.webdriver.common.by import By
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel, elaboration
from funcoes import cpf_ok

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")
    cpf = str(df['CPF'][i])
    cpf = cpf_ok(cpf)

    driver.find_element(By.NAME, 'cpfClienteFiltro').send_keys(cpf)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

    try:
        cod_cliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]").text
        print(i+1, "Código", cod_cliente, "para o CPF", cpf)
    except:
        v = 1
        while v < 10:
            try:
                w = driver.find_element(By.XPATH,"/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[3]/td/table[1]/tbody/tr[{}]/td[2]".format(v)).text
                v = v + 1
                if v > 1:
                    print(i+1, "Duplicidade de código para o CPF {}".format(cpf))
                    break
            except:
                if v == 1:
                    print(i+1, "Não tem código para o CPF {}".format(cpf))
                    break









