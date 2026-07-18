import time, csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_funcoes import *
from db_arquivos import *

df = pd.read_csv(databaseCSV2)
login()

relatorioGsan = relatorioGsan2

header = ['#', 'MATRICULA', 'NOME', 'CPF', 'CODIGO', 'AGUA', 'ESGOTO']

with open(databaseCSV2, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        contador = i+1
        matricula = str(df['MATRICULA'][i])
        alterar = int(df['ALTERAR'][i])
        if alterar == 1:
            if matricula != '0':                
                driver.get("http://g1.caema.ma.gov.br/gsan/exibirConsultarImovelAction.do?menu=sim")
                driver.find_element(By.ID, "1").click()
                time.sleep(0.3)
                driver.find_element(By.NAME, 'idImovelDadosCadastrais').send_keys(matricula, Keys.ENTER)
                time.sleep(0.4)
                imvInexistente = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')  
                imvInexistente = imvInexistente.strip()
                if imvInexistente != 'IMÓVEL INEXISTENTE':                              
                    time.sleep(0.3)       
                    tipoCliente = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/div/font").text
                    tipoCliente = tipoCliente.strip()        
                    if tipoCliente == 'USUARIO':
                        nomeCLiente = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr/td[1]/div/font/a").click()
                        time.sleep(0.3)
                        janela = driver.window_handles[0]
                        popup = driver.window_handles[1]
                        driver.switch_to.window(popup) 
                        time.sleep(0.3)
                        codigoCLiente = driver.find_element(By.NAME, 'codigoCliente').get_attribute('value')            
                        nomeCLiente = driver.find_element(By.NAME, 'nomeCliente').get_attribute('value')     
                        try:
                            cpfCLiente = driver.find_element(By.NAME, 'cpfCliente').get_attribute('value')
                        except:
                            cpfCLiente = driver.find_element(By.NAME, 'cnpjCliente').get_attribute('value')     
                        
                        driver.find_element(By.XPATH, "//input[@value='Fechar']").click()   
                        time.sleep(0.2)
                        driver.switch_to.window(janela)

                        time.sleep(0.2)  

                        situacaoAgua = driver.find_element(By.NAME, 'situacaoAguaDadosCadastrais').get_attribute('value')
                        time.sleep(0.1)  
                        situacaoEsgoto = driver.find_element(By.NAME, 'situacaoEsgotoDadosCadastrais').get_attribute('value')
                        time.sleep(0.1)

                        row = i+1, matricula, nomeCLiente, cpfCLiente, codigoCLiente, situacaoAgua, situacaoEsgoto
                        writer.writerow(row)  
                        
                    elif tipoCliente == 'PROPRIETARIO' or 'RESPONSAVEL':            
                        nomeCLiente = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td[1]/div/font/a").text
                        tipoCliente = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td[2]/div/font").text
                        tipoCliente = tipoCliente.strip()            
                        
                        if tipoCliente == 'USUARIO':
                            driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td[1]/div/font/a").click()                
                            time.sleep(0.3)
                            janela = driver.window_handles[0]
                            popup = driver.window_handles[1]
                            driver.switch_to.window(popup) 
                            time.sleep(0.3)
                            codigoCLiente = driver.find_element(By.NAME, 'codigoCliente').get_attribute('value')                
                            nomeCLiente = driver.find_element(By.NAME, 'nomeCliente').get_attribute('value')                
                            try:
                                cpfCLiente = driver.find_element(By.NAME, 'cpfCliente').get_attribute('value')
                            except:
                                cpfCLiente = driver.find_element(By.NAME, 'cnpjCliente').get_attribute('value')
                            time.sleep(0.2)
                            driver.find_element(By.XPATH, "//input[@value='Fechar']").click()   
                            time.sleep(0.2)
                            driver.switch_to.window(janela)

                            row = i+1, matricula, nomeCLiente, cpfCLiente, codigoCLiente, situacaoAgua, situacaoEsgoto
                            writer.writerow(row)  
                    else:
                        break
                            
                elif imvInexistente == 'IMÓVEL INEXISTENTE':
                    row = i+1, matricula, 'IMÓVEL INEXISTENTE', 'IMÓVEL INEXISTENTE', 'IMÓVEL INEXISTENTE', 'IMÓVEL INEXISTENTE', 'IMÓVEL INEXISTENTE'
                    writer.writerow(row)  
                    
            elif matricula == '0':
                pass
                row = i+1, matricula, 0, 0, 0, 0, 0
                writer.writerow(row)  


        calculoPorcentagem(contador, totalRow)