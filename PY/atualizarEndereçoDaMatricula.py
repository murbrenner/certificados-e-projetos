import time, csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
from db_funcoes import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'MATRICULA', 'MENSAGEM']

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        contador = i+1
        matricula = str(df['MATRICULA'][i])
        cep_gsan = int(df['CEP_GSAN'][i]) 
        complemento = str(df['COMPLEMENTO'][i])
        alterar = int(df['ALTERAR'][i])
        cod_log = str(df['COD_LOG'][i])
        bairro = str(df['BAIRRO'][i])
        numero = str(df['NUMERO'][i])
        
        if alterar == 1:
            if matricula != '0':
                driver.get("http://g1.caema.ma.gov.br/gsan/exibirFiltrarImovelAction.do?menu=sim")
                time.sleep(0.3)        
            
                driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
                time.sleep(0.3)  
                driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                time.sleep(0.5)

                try:                
                    msg0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text  
                    #print(i + 1, matricula, msg0)
                    row = i + 1, matricula, msg0
                    writer.writerow(row)
                except:
                    driver.find_element(By.ID, "2").click()
                    time.sleep(0.3)
                    try:
                        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                        time.sleep(0.3)
                    except:
                        pass
                    
                    janela_principal = driver.window_handles[0]                
                    
                    if cod_log == '0':
                        try:                        
                            driver.find_element(By.PARTIAL_LINK_TEXT, "MA").click()                        
                            time.sleep(0.3)
                            janela_popup = driver.window_handles[1]
                            driver.switch_to.window(janela_popup)                                                
                            cod_log = driver.find_element(By.NAME, "logradouro").get_attribute("value")                            
                            time.sleep(0.3)
                            driver.switch_to.window(janela_principal)       
                        except:
                            pass      
                        
                    time.sleep(0.3)
                    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[5]/tbody/tr[2]/td/div/table/tbody/tr/td[1]/a/img").click()
                    time.sleep(0.3)
                    alert = driver.switch_to.alert
                    alert.accept()
                    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                    time.sleep(0.3)
                    janela_principal = driver.window_handles[0]                
                    janela_popup = driver.window_handles[1]
                    driver.switch_to.window(janela_popup)  
                    time.sleep(0.3)
                    driver.find_element(By.NAME, "logradouro").send_keys(cod_log, Keys.ENTER)
                    time.sleep(0.3)
                    driver.find_element(By.XPATH, "//input[@name='cepSelecionado' and @value='{}']".format(cep_gsan)).click()
                    time.sleep(0.3)
                    driver.find_element(By.NAME, "bairro").send_keys(bairro)
                    time.sleep(0.3)
                    #driver.find_element(By.NAME, "enderecoReferencia").send_keys('01 - NUMERO')
                    #time.sleep(0.2)
                    driver.find_element(By.NAME, "numero").send_keys(numero) 
                    time.sleep(0.3)
                    if complemento != '0':
                        driver.find_element(By.NAME, "complemento").send_keys(complemento)
                        time.sleep(0.3)
                    driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                    time.sleep(0.3)
                    driver.switch_to.window(janela_principal)    
                    time.sleep(0.3)
                    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                    time.sleep(0.3)
                    try:
                        driver.find_element(By.XPATH, "//input[@value='Não']").click()
                        time.sleep(0.3)
                        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                        time.sleep(0.3)
                    except:
                        pass
                    try:
                        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                        #print(i+1, matricula, msg_ok)
                        row = i+1, matricula, msg_ok
                        writer.writerow(row)
                    except:
                        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        #print(i+1, matricula, msg_er)
                        row = i+1, matricula, msg_er
                        writer.writerow(row)
            elif alterar == '0':
                #print(i+1, 'Imóvel de matrícula [{}] ja está com o endereço atualizado!'.format(matricula))
                row = i+1, 'Imóvel de matrícula [{}] ja está com o endereço atualizado!'.format(matricula)
                writer.writerow(row)

        calculoPorcentagem(i, totalRow)