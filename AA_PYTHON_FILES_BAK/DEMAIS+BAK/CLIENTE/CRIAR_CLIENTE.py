import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirClienteAction.do?menu=sim")
    nome = str(df['NOME'][i])
    cpf = str(df['CPF'][i])
    cod = str(df['ID_CLIENTE'][i])

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

    if cod == '0':
        driver.find_element(By.NAME, "nome").send_keys(str(df['NOME'][i]))
        driver.find_element(By.NAME, "indicadorPessoaFisicaJuridica").click()
        email = str(df['EMAIL'][i])
        if email != '0':
            driver.find_element(By.NAME, "email").send_keys(str(df['EMAIL'][i]))
        else:
            pass
        driver.find_element(By.NAME, "tipoPessoa").send_keys('100 - RESIDENCIA')

        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

        driver.find_element(By.NAME, "cpf").send_keys(cpf_ok)
        driver.find_element(By.XPATH, "//input[@value='1']").click()
        driver.find_element(By.NAME, "rg").send_keys('')#send_keys(str(df['RG'][i]))
        driver.find_element(By.NAME, "dataEmissao").send_keys('')#.send_keys(str(df['EMISSAO'][i]))
        driver.find_element(By.NAME, "idOrgaoExpedidor").send_keys('')#.send_keys('SSP')
        driver.find_element(By.NAME, "idUnidadeFederacao").send_keys('')#.send_keys('MA')
        nasc = driver.find_element(By.NAME, "dataNascimento").send_keys(str(df['DATA NASC'][i]))
        driver.find_element(By.NAME, "idPessoaSexo").send_keys(str(df['SEXO'][i]))
        driver.find_element(By.NAME, "nomeMae").send_keys('')#.send_keys(str(df['MAE'][i]))

        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        main_window_handle = driver.current_window_handle
        all_window_handles = driver.window_handles
        for handle in all_window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                driver.find_element(By.NAME, "tipo").send_keys('01 - RESIDENCIAL')
                driver.find_element(By.NAME, "logradouro").send_keys('11583', Keys.ENTER)
                driver.find_element(By.NAME, "bairro").send_keys('JD ELDORADO')
                driver.find_element(By.NAME, "enderecoReferencia").send_keys('01 - NUMERO')
                driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
                driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))
                driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                driver.close()
            driver.switch_to.window(main_window_handle)

        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

        driver.find_element(By.NAME, "idTipoTelefone").send_keys('03 - CELULAR')
        driver.find_element(By.NAME, "idMunicipio").send_keys('1', Keys.ENTER)
        driver.find_element(By.NAME, "ddd").clear()
        driver.find_element(By.NAME, "ddd").send_keys(str(df['DDD'][i]))
        driver.find_element(By.NAME, "telefone").send_keys(str(df['TELEFONE'][i]))
        driver.find_element(By.NAME, "contato").send_keys(str(df['NOME'][i]))
        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(msg_ok)
    else:
        pass