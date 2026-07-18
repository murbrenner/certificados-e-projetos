import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import *
from db_arquivos import *
from db_funcoes import *
import csv

df = pd.read_csv(databaseCSV1)
login()

cabeçalho = ['#', 'MSG', 'COD']

relatorioGsan = relatorioGsan1

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(cabeçalho)

    for i in df.index:        
        contador = i+1
        driver.get("http://g1.caema.ma.gov.br/gsan/exibirInserirClienteAction.do?menu=sim")

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
        alterar = int(df['ALTERAR'][i])

        
        if alterar == 1: 
            if cod == 0:            
                if pf == 1:
                    cpf = cpf_ok(cpf)
                    driver.find_element(By.NAME, "nome").send_keys(nome)
                    driver.find_element(By.XPATH, "//input[@name='indicadorPessoaFisicaJuridica' and @value='1']").click()                 
                    if email != '0':
                        driver.find_element(By.NAME, "email").send_keys(email)
                    else:
                        pass
                    time.sleep(0.2)  
                    driver.find_element(By.NAME, "tipoPessoa").send_keys(tipo_pessoa)   
                    time.sleep(0.2)             
                    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                    time.sleep(0.3)  
                                    
                    if cpf == '00000000000':
                        cpf = ''                  
                    driver.find_element(By.NAME, "cpf").send_keys(cpf, Keys.ENTER)
                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='1']").click()
                    time.sleep(0.2)  

                    if data_exp != '0':
                        rg = rg_ok(rg)
                        driver.find_element(By.NAME, "rg").send_keys(rg)
                        driver.find_element(By.NAME, "dataEmissao").send_keys(data_exp)
                        time.sleep(0.3)  
                        driver.find_element(By.NAME, "idOrgaoExpedidor").send_keys('SSP')
                        time.sleep(0.4)  
                        driver.find_element(By.NAME, "idUnidadeFederacao").send_keys('MA')
                        time.sleep(0.3)                          
                        nasc = driver.find_element(By.NAME, "dataNascimento").send_keys(data_nasc)
                    driver.find_element(By.NAME, "idPessoaSexo").send_keys(sexo)
                    if mae != '0':
                        driver.find_element(By.NAME, "nomeMae").send_keys(mae)
                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                    time.sleep(0.4)
                    try:
                        time.sleep(0.2)
                        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text 
                        time.sleep(0.5)                       
                        row = i + 1, msg_er
                        writer.writerow(row)

                    except:                    
                        time.sleep(0.8)
                        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                        time.sleep(0.3)
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
                        time.sleep(0.2)
                        driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                        time.sleep(0.2)
                        driver.close()
                        driver.switch_to.window(janela_principal)
                        time.sleep(0.2)
                        driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

                        if ddd != '0':
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "idTipoTelefone").send_keys('03 - CELULAR')
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "idMunicipio").send_keys('1', Keys.ENTER)
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "ddd").clear()
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "ddd").send_keys(ddd)
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "telefone").send_keys(telefone)
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "contato").send_keys(nome)
                            time.sleep(0.2)
                            driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                            time.sleep(0.4)  
                        time.sleep(0.2)
                        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                        time.sleep(0.2)

                        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text                            
                        #print(i+1, msg_ok, "[{}]".format(msg_ok[18:26]))
                        row = i+1, msg_ok, "[{}]".format(msg_ok[18:26])
                        writer.writerow(row)   

                       

                else:
                    try:
                        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        #print(i + 1, msg_er)
                        row = i + 1, msg_er
                        writer.writerow(row)

                    except:
                        pass
            if cod != 0:
                    #print(i+1, "CLIENTE JA POSSUI CODIGO [{}]".format(cod))
                    row = i+1, "CLIENTE JA POSSUI CODIGO [{}]".format(cod)
                    writer.writerow(row)            
                    pass
        
        elif alterar == 0:
            pass
            

        calculoPorcentagem(contador, totalRow)