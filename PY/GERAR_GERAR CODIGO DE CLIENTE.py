import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import inserir_imovel, teste
from db_funcoes import cpf_ok, cnpj_ok, rg_ok
import csv

df = pd.read_csv(inserir_imovel)
login()

cabeçalho = ['#', 'MSG', 'COD']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirClienteAction.do?menu=sim")

        nome = str(df['NOME'][i])
        cpf = str(df['CPF'][i])
        cod = int(df['COD_CLIENTE'][i])
        ddd = str(df['DDD'][i])
        complemento = str(df['COMPLEMENTO'][i])
        mae = str(df['MAE'][i])
        data_exp = str(df['DATA_EXP'][i])
        pf = int(df['V_CPF'][i])
        pj = int(df['V_CNPJ'][i])
        tipo_pessoa = str(df['TIPO_CLIENTE'][i])
        email = str(df['EMAIL'][i])
        data_nasc = str(df['DATA_NASC'][i])
        rg = str(df['RG'][i])
        sexo = str(df['SEXO'][i])
        cod_log = str(df['COD_LOG'][i])
        bairro = str(df['BAIRRO'][i])
        numero = str(df['NUMERO'][i])
        complemento = str(df['COMPLEMENTO'][i])
        telefone = str(df['TELEFONE'][i])
        cep_gsan = int(df['CEP_GSAN'][i])
                
        if cod == 0:            
            if pf == 1:
                cpf = cpf_ok(cpf)
                driver.find_element(By.NAME, "nome").send_keys(nome)
                driver.find_element(By.XPATH, "//input[@name='indicadorPessoaFisicaJuridica' and @value='1']").click()                 
                if email != '0':
                    driver.find_element(By.NAME, "email").send_keys(email)
                else:
                    pass
                driver.find_element(By.NAME, "tipoPessoa").send_keys(tipo_pessoa)                
                driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                                
                if cpf == '00000000000':
                    cpf = ''                  
                driver.find_element(By.NAME, "cpf").send_keys(cpf, Keys.ENTER)
                driver.find_element(By.XPATH, "//input[@value='1']").click()

                if data_exp != '0':
                    rg = rg_ok(rg)
                    driver.find_element(By.NAME, "rg").send_keys(rg)
                    driver.find_element(By.NAME, "dataEmissao").send_keys(data_exp)
                    driver.find_element(By.NAME, "idOrgaoExpedidor").send_keys('SSP')
                    driver.find_element(By.NAME, "idUnidadeFederacao").send_keys('MA')
                    nasc = driver.find_element(By.NAME, "dataNascimento").send_keys(data_nasc)
                driver.find_element(By.NAME, "idPessoaSexo").send_keys(sexo)
                if mae != '0':
                    driver.find_element(By.NAME, "nomeMae").send_keys(mae)
                time.sleep(0.6)
                driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

                time.sleep(0.6)
                driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                time.sleep(0.2)
                janela_principal = driver.window_handles[0]
                janela_endereco = driver.window_handles[1]
                driver.switch_to.window(janela_endereco)
                time.sleep(0.2)
                driver.find_element(By.NAME, "tipo").send_keys('01 - RESIDENCIAL')
                time.sleep(0.2)
                driver.find_element(By.NAME, "logradouro").send_keys(cod_log, Keys.ENTER)              
                time.sleep(0.2)                
                driver.find_element(By.XPATH, "//input[@value='{}']".format(cep_gsan)).click()
                time.sleep(0.2)   
                driver.find_element(By.NAME, "bairro").send_keys(bairro)
                time.sleep(0.2)
                driver.find_element(By.NAME, "numero").send_keys(numero)
                time.sleep(0.2)
                if complemento != '0':
                    driver.find_element(By.NAME, "complemento").send_keys(complemento)
                driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                time.sleep(0.2)
                driver.close()
                driver.switch_to.window(janela_principal)
                time.sleep(0.2)
                driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

                if ddd != '0':
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "idTipoTelefone").send_keys('03 - CELULAR')
                    driver.find_element(By.NAME, "idMunicipio").send_keys('1', Keys.ENTER)
                    driver.find_element(By.NAME, "ddd").clear()
                    driver.find_element(By.NAME, "ddd").send_keys(ddd)
                    driver.find_element(By.NAME, "telefone").send_keys(telefone)
                    driver.find_element(By.NAME, "contato").send_keys(nome)
                    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()

            if pj == 1:
                cpf = cnpj_ok(cpf)
                driver.find_element(By.NAME, "nome").send_keys(nome)            
                driver.find_element(By.XPATH, "//input[@name='indicadorPessoaFisicaJuridica' and @value='2']").click()                
                if email != '0':
                    driver.find_element(By.NAME, "email").send_keys(email)
                else:
                    pass
                driver.find_element(By.NAME, "tipoPessoa").send_keys(tipo_pessoa)
                driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                
                if cpf == '00000000000000':
                    cpf = ''      
                driver.find_element(By.NAME, "cnpj").send_keys(cpf, Keys.ENTER)
                driver.find_element(By.XPATH, "//input[@value='1']").click()
                driver.find_element(By.NAME, "idRamoAtividade").send_keys(tipo_pessoa)

                driver.find_element(By.XPATH, "//input[@value='Avançar']").click()               

                time.sleep(0.6)
                driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                time.sleep(0.2)
                janela_principal = driver.window_handles[0]
                janela_endereco = driver.window_handles[1]
                driver.switch_to.window(janela_endereco)
                time.sleep(0.2)
                driver.find_element(By.NAME, "tipo").send_keys('01 - RESIDENCIAL')
                time.sleep(0.2)
                driver.find_element(By.NAME, "logradouro").send_keys(cod_log, Keys.ENTER)              
                time.sleep(0.2)                                
                driver.find_element(By.XPATH, "//input[@value='7018']").click()
                time.sleep(0.2)
                driver.find_element(By.NAME, "bairro").send_keys(bairro)
                time.sleep(0.2)
                driver.find_element(By.NAME, "numero").send_keys(numero)
                time.sleep(0.2)
                if complemento != '0':
                    driver.find_element(By.NAME, "complemento").send_keys(complemento)
                driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                time.sleep(0.2)
                driver.close()
                driver.switch_to.window(janela_principal)
                time.sleep(0.2)
                driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

                if ddd != '0':
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "idTipoTelefone").send_keys('03 - CELULAR')
                    driver.find_element(By.NAME, "idMunicipio").send_keys('1', Keys.ENTER)
                    driver.find_element(By.NAME, "ddd").clear()
                    driver.find_element(By.NAME, "ddd").send_keys(ddd)
                    driver.find_element(By.NAME, "telefone").send_keys(telefone)
                    driver.find_element(By.NAME, "contato").send_keys(nome)
                    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
            
            driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            
            print(i+1, msg_ok, "[{}]".format(cod))
            linha = i+1, msg_ok, "[{}]".format(cod)
            escritor.writerow(linha)        

        else:
            try:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                print(i + 1, msg_er)
                linha = i + 1, msg_er
                escritor.writerow(linha)

            except:
                pass
        if cod != 0:
                print(i+1, "CLIENTE JA POSSUI CODIGO [{}]".format(cod))
                linha = i+1, "CLIENTE JA POSSUI CODIGO [{}]".format(cod)
                escritor.writerow(linha)            
                pass