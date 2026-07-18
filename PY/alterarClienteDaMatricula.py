from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import *
from db_arquivos import *
from db_funcoes import *
import time, csv

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'MATRICULA', 'MENSAGEM']

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1 

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:  
        contador = i+1  
        driver.get("http://g1.caema.ma.gov.br/gsan/exibirFiltrarImovelAction.do?menu=sim")    
        #CABEÇALHO PLANILHA DATABASE (UTF-8): imv_id,alterar,codigo
        matricula = int(df['MATRICULA'][i])
        alterar = int(df['ALTERAR'][i])
        codigo = int(df['COD_CLIENTE'][i])
        
        if matricula > 1:
            driver.find_element(By.NAME, 'matriculaFiltro').send_keys(matricula)
            time.sleep(0.1)
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()    
            time.sleep(0.5)
            try:
                time.sleep(0.2)
                msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                row = i + 1, matricula, msg_err
                writer.writerow(row)
            except:
                time.sleep(0.2)
                driver.find_element(By.ID, "3").click()
                time.sleep(0.3)
            
                if codigo > 1:
                    if alterar == 1:      
                        try:
                            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                            time.sleep(0.2)
                        except:
                            pass               
                        user_cod = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[3]/div").text
                            
                        if user_cod != codigo:
                            try:          
                                tipo_cliente = driver.find_element(By.XPATH,"//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[5]/div").text
                                if tipo_cliente == "USUARIO":
                                    time.sleep(0.1)
                                    date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[6]").text
                            except:
                                pass           
                            j = 1
                            while j < 4:
                                try:
                                    tipo_cliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[5]/div".format(j)).text
                                    if tipo_cliente == "USUARIO":
                                        date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[6]".format(j)).text
                                        time.sleep(0.1)
                                        driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/div/input".format(j)).click()
                                        time.sleep(0.3)
                                except:
                                    break
                                j = j + 1

                            time.sleep(0.2)            
                            driver.find_element(By.XPATH, "//input[@value='Remover']").click()
                            time.sleep(0.3)
                            alert = driver.switch_to.alert
                            alert = alert.accept()
                            time.sleep(0.1)
                            try:
                                driver.find_element(By.XPATH, "//input[@value='Prosseguir']").click()
                                time.sleep(0.3)
                            except:
                                pass            
                            time.sleep(1) 
                            janela = driver.window_handles[0]
                            popup = driver.window_handles[1]
                            driver.switch_to.window(popup)        
                            date_inicio_rel = date_inicio_rel.replace('/', '')     
                            driver.find_element(By.NAME, 'dataTerminoRelacao').clear()
                            time.sleep(0.1)
                            driver.find_element(By.NAME, 'dataTerminoRelacao').send_keys(date_inicio_rel)
                            time.sleep(0.1)
                            driver.find_element(By.NAME, 'idMotivo').send_keys('ATUALIZ. CADASTRAL')
                            time.sleep(0.1)
                            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                            time.sleep(0.3)
                        
                            try:
                                time.sleep(0.2)
                                msg_err0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span")                    
                                time.sleep(0.1)
                                row = i + 1, matricula, msg_err0.text
                                writer.writerow(row)
                                msg_er1 = bool(msg_err0)                
                        
                                driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
                                time.sleep(0.3)
                                driver.close()
                                time.sleep(0.5)
                                driver.switch_to.window(janela)      
                                time.sleep(0.1)         
                                driver.find_element(By.XPATH, "//input[@value='Cancelar']").click()
                                time.sleep(0.3)
                            except:
                                time.sleep(0.2)
                                driver.switch_to.window(janela)
                                time.sleep(0.1)
                                janela = driver.window_handles[0]               
                                driver.switch_to.window(janela)
                                time.sleep(0.5)                
                                
                                driver.find_element(By.NAME, "idCliente").send_keys(codigo, Keys.ENTER)
                                time.sleep(0.5)
                                driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
                                time.sleep(0.5)
                                driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()               
                                time.sleep(0.3)
                                try:                                
                                    driver.find_element(By.XPATH, "//input[@value='Sim']").click()
                                    time.sleep(0.3)
                                    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()    
                                    time.sleep(0.3)                
                                    msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                                    time.sleep(0.1)
                                    row = i + 1, matricula, msg_ok
                                    writer.writerow(row)
                                except:    
                                    time.sleep(0.3)               
                                    msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                                    time.sleep(0.1)
                                    row = i + 1, matricula, msg_err
                                    writer.writerow(row)
                else:           
                    time.sleep(0.1)
                    row = i + 1, "Cliente com o mesmo codigo ja inserido na matrícula: {}".format(matricula)
                    writer.writerow(row)
                    pass


        calculoPorcentagem(contador, totalRow)
