import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, login
from arquivos import inserir_imovel
from funcoes import cpf_ok

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirInserirClienteAction.do?menu=sim")
    nome = str(df['NOME'][i])
    cpf = str(df['CPF'][i])
    cod = int(df['ID_CLIENTE'][i])
    ddd = str(df['DDD'][i])

    cpf = cpf_ok(cpf)

    if cod == 0:

        driver.find_element(By.NAME, "nome").send_keys(str(df['NOME'][i]))
        driver.find_element(By.NAME, "indicadorPessoaFisicaJuridica").click()
        email = str(df['EMAIL'][i])
        if email != 'n':
            driver.find_element(By.NAME, "email").send_keys(str(df['EMAIL'][i]))
        else:
           pass
        driver.find_element(By.NAME, "tipoPessoa").send_keys('100 - RESIDENCIA')

        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
        if cpf == '00000000000':
            cpf = ''

        driver.find_element(By.NAME, "cpf").send_keys(cpf)


        driver.find_element(By.XPATH, "//input[@value='1']").click()
        #driver.find_element(By.NAME, "rg").send_keys('')#send_keys(str(df['RG'][i]))
        #driver.find_element(By.NAME, "dataEmissao").send_keys('')#.send_keys(str(df['EMISSAO'][i]))
        #driver.find_element(By.NAME, "idOrgaoExpedidor").send_keys('')#.send_keys('SSP')
        #driver.find_element(By.NAME, "idUnidadeFederacao").send_keys('')#.send_keys('MA')
        #nasc = driver.find_element(By.NAME, "dataNascimento").send_keys('')#(str(df['DATA NASC'][i]))
        driver.find_element(By.NAME, "idPessoaSexo").send_keys(str(df['SEXO'][i]))
        #driver.find_element(By.NAME, "nomeMae").send_keys('')#.send_keys(str(df['MAE'][i]))
        time.sleep(0.3)
        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        time.sleep(0.3)
        janela_principal = driver.window_handles[0]
        janela_endereco = driver.window_handles[1]
        driver.switch_to.window(janela_endereco)
        driver.find_element(By.NAME, "tipo").send_keys('01 - RESIDENCIAL')
        driver.find_element(By.NAME, "logradouro").send_keys(int(df['COD_LOG'][i]), Keys.ENTER)
        try:
            driver.find_element(By.XPATH, "//input[@value='1']").click() #MUDAR!!!!! PARA CADA CODIGO DE LOGRADOURO!!!!!!!
            driver.find_element(By.NAME, "cepSelecionado").click()
        except:
            pass
        driver.find_element(By.XPATH, "//input[@value='1']").click()
        driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
        driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
        driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))
        driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
        driver.close()
        driver.switch_to.window(janela_principal)

        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

        if ddd != 'n':
            driver.find_element(By.NAME, "idTipoTelefone").send_keys('03 - CELULAR')
            driver.find_element(By.NAME, "idMunicipio").send_keys('1', Keys.ENTER)
            driver.find_element(By.NAME, "ddd").clear()
            driver.find_element(By.NAME, "ddd").send_keys(str(df['DDD'][i]))
            driver.find_element(By.NAME, "telefone").send_keys(str(df['TELEFONE'][i]))
            driver.find_element(By.NAME, "contato").send_keys(str(df['NOME'][i]))
            driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()


        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text

        print(i+1, msg_ok)
    else:
        try:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i + 1, msg_er)
        except:
            pass
    time.sleep(0.3)