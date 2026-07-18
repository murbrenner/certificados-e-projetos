import time
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import *
from db_funcoes import *

df = pd.read_csv(databaseCSV1)
login()

relatorioGsan = relatorioGsan1

header = ['#', 'MATRICULA', 'MENSAGEM']

with open(databaseCSV1, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1
    
#ARQUIVO DE SAÍDA:
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index: 

        #REQUISITOS PLANILHA (VARIÁVEIS):  
        categoria_res = int(df['RES'][i])
        categoria_com = int(df['COM'][i])
        categoria_pub = int(df['PUB'][i])
        categoria_com_peq = int(df['PEQ'][i])
        categoria_res_pop = int(df['POP'][i])
        categoria_ind = int(df['IND'][i])
        alterar = int(df['ALTERAR'][i])
        matricula = int(df['MATRICULA'][i])

        #CÓDIGO:
        if alterar == 1:        
            if matricula != 0:  
                driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")        
                driver.find_element(By.NAME, 'matriculaFiltro').send_keys(matricula)
                driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()    
                time.sleep(0.3)
                try:                
                    msg0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                    row = i + 1, matricula, msg0
                    writer.writerow(row)
                except:
                    time.sleep(0.5)
                    driver.find_element(By.ID, "4").click()                
                    time.sleep(0.5)
                    try:
                        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                        time.sleep(0.3)
                    except:
                        pass    

                    driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[1]/div/a/img").click()
                    time.sleep(0.3)
                    popup = driver.switch_to.alert
                    popup.accept()          
                    time.sleep(0.3)

                    try:
                        driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[1]/div/a/img").click()
                        time.sleep(0.3)
                        popup = driver.switch_to.alert
                        popup.accept()          
                        time.sleep(0.3)
                    except:
                        pass
                            
                    if categoria_res >= 1:
                        if categoria_res_pop >= 1:                
                            driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
                            time.sleep(0.3) 
                            driver.find_element(By.NAME, "idSubCategoria").send_keys('07 - RESIDENCIAL POPULAR')
                            time.sleep(0.3)
                            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                            driver.find_element(By.NAME, "botaoAdicionar").click()
                            time.sleep(0.3) 
                        elif categoria_res_pop == 0:                
                            driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
                            time.sleep(0.3)
                            driver.find_element(By.NAME, "idSubCategoria").send_keys('01 - RESIDENCIAL')
                            time.sleep(0.3)
                            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                            driver.find_element(By.NAME, "botaoAdicionar").click()     
                            time.sleep(0.3)    
                    
                    if categoria_pub >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('01 - PUBLICO')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('04 - PUBLICO MUNICIPAL')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                        driver.find_element(By.NAME, "botaoAdicionar").click()
                        time.sleep(0.3) 

                    if categoria_com >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('02 - COMERCIAL')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com)
                        driver.find_element(By.NAME, "botaoAdicionar").click()
                        time.sleep(0.3) 

                    if categoria_com_peq >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('08 - COM. PEQ. NEGOCIOS')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com_peq)
                        driver.find_element(By.NAME, "botaoAdicionar").click()
                        time.sleep(0.3) 

                    if categoria_ind >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('03 - INDUSTRIAL')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('03 - INDUSTRIAL')
                        time.sleep(0.3)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_ind)
                        driver.find_element(By.NAME, "botaoAdicionar").click()                
                        time.sleep(0.3)

                    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                    time.sleep(0.3) 
                    try:
                        driver.find_element(By.XPATH, "//input[@value='Não']").click()
                        time.sleep(0.3) 
                    except:
                        pass  
                    
                    try:
                        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text                        
                        row = i+1, matricula, msg_ok
                        writer.writerow(row)
                    except:
                        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text                        
                        row = i+1, matricula, msg_er
                        writer.writerow(row)

                else:        
                    row = i+1, matricula, "NAO PRECISA ALTERAR"
                    writer.writerow(row)


        calculoPorcentagem(i, totalRow)