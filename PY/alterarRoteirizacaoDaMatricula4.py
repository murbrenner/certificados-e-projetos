from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import *
from db_arquivos import *
from db_funcoes import *
import time, csv

df = pd.read_csv(databaseCSV4)
login()

relatorioGsan = relatorioGsan4

header = ['#', 'MATRICULA', 'MENSAGEM']

with open(databaseCSV4, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:  
        contador = i+1
        # matricula = int(df["imv_id"][i])
        # alterar = int(df["alterar"][i])
        # local = int(df['localidade'][i])
        # setor = int(df['Setor'][i])
        # quadra = int(df['quadra'][i])
        # lote = int(df['seq_id'][i])
        # sublote = '0'#int(df['sublote'][i])
        # #testada = int(df['TESTADA'][i])
        # sequencia = int(df['seq_id'][i])
        # latitude = str(df['latitude'][i])
        # longitude = str(df['longitude'][i])

        matricula = int(df["MATRICULA"][i])
        alterar = int(df["ALTERAR"][i])
        local = int(df['LOCAL'][i])
        setor = int(df['SETOR'][i])
        quadra = int(df['QUADRA'][i])
        lote = int(df['LOTE'][i])
        sublote = int(df['SUBLOTE'][i])
        testada = int(df['TESTADA'][i])
        sequencia = int(df['SEQUENCIA'][i])
        latitude = str(df['LATITUDE'][i])
        longitude = str(df['LONGITUDE'][i])

        if alterar == 1:    
            if matricula != 0:
                driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")              
                driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
                driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                time.sleep(0.5)            
                
                try:                
                    msg0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                    row = i + 1, matricula, msg0
                    writer.writerow(row)
                except:
                    time.sleep(0.1)
                    driver.find_element(By.NAME, "idLocalidade").clear()
                    driver.find_element(By.NAME, "idLocalidade").send_keys(local)
                    time.sleep(0.1)
                    driver.find_element(By.NAME, "idSetorComercial").clear()
                    driver.find_element(By.NAME, "idSetorComercial").send_keys(setor)
                    time.sleep(0.1)            
                    driver.find_element(By.NAME, "idQuadra").clear()
                    driver.find_element(By.NAME, "idQuadra").send_keys(quadra, Keys.ENTER) 
                    time.sleep(0.3)
                    driver.find_element(By.NAME, "lote").clear() 
                    time.sleep(0.2)                                        
                    driver.find_element(By.NAME, "lote").send_keys(lote)               
                    time.sleep(0.1)
                    driver.find_element(By.NAME, "subLote").clear()
                    driver.find_element(By.NAME, "subLote").send_keys(sublote)
                    #time.sleep(0.1)
                    #driver.find_element(By.NAME, "testadaLote").clear()
                    #driver.find_element(By.NAME, "testadaLote").send_keys(testada)
                    time.sleep(0.1)
                    driver.find_element(By.NAME, "sequencialRota").clear()
                    driver.find_element(By.NAME, "sequencialRota").send_keys(sequencia)
                    
                    driver.find_element(By.ID, "5").click()
                    time.sleep(0.3)
                    
                    try:
                        msg1 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text                        
                        row = i + 1, matricula, msg1
                        writer.writerow(row)
                                    
                    except:
                        pass

                    try:
                        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                    except:               
                        pass 

                    pavimentoCalcada = '02 - CIMENTO'
                    pavimentoRua = '02 - ASFALTO'
                    fonteAbastecimento = '01 - CAEMA'
                    idLigacaoEsgotoEsgotamento = 'NORMAL'
                    perfilImovel = '05 - NORMAL'
                    tipoDespejo = '01 - RESIDENCIAL'
                    imovelTipoHabitacao = '01 - HABITADO'
                    imovelTipoPropriedade = '01 - PROPRIO'
                    imovelTipoConstrucao = '03 - ALVENARIA'
                    imovelTipoCobertura = '02 - TELHA CERAMICA'             
                    time.sleep(0.3)
                    driver.find_element(By.NAME, 'pavimentoCalcada').send_keys(pavimentoCalcada)
                    driver.find_element(By.NAME, 'pavimentoRua').send_keys(pavimentoRua)
                    driver.find_element(By.NAME, 'fonteAbastecimento').send_keys(fonteAbastecimento)
                    try:
                        driver.find_element(By.NAME, 'idLigacaoEsgotoEsgotamento').send_keys(idLigacaoEsgotoEsgotamento)
                    except:
                        pass
                    try:
                        driver.find_element(By.NAME, 'perfilImovel').send_keys(perfilImovel)
                    except:
                        pass
                    driver.find_element(By.NAME, 'tipoDespejo').send_keys(tipoDespejo)
                    driver.find_element(By.NAME, 'imovelTipoHabitacao').send_keys(imovelTipoHabitacao)
                    driver.find_element(By.NAME, 'imovelTipoPropriedade').send_keys(imovelTipoPropriedade)
                    driver.find_element(By.NAME, 'imovelTipoConstrucao').send_keys(imovelTipoConstrucao)
                    driver.find_element(By.NAME, 'imovelTipoCobertura').send_keys(imovelTipoCobertura)
                    driver.find_element(By.NAME, 'reservatorioInferior').clear()
                    driver.find_element(By.NAME, 'faixaReservatorioInferior').send_keys(Keys.HOME)

                    driver.find_element(By.ID, "6").click()
                    time.sleep(0.3)
                    driver.find_element(By.NAME, "cordenadasUtmX").clear()
                    driver.find_element(By.NAME, "cordenadasUtmX").send_keys(longitude)
                    driver.find_element(By.NAME, "cordenadasUtmY").clear()
                    driver.find_element(By.NAME, "cordenadasUtmY").send_keys(latitude)
                    time.sleep(0.1)
                    driver.find_element(By.XPATH, f"//*[@value='Concluir']").click()   
                    time.sleep(0.3)         
                    
                    try:
                        driver.find_element(By.XPATH, f"//*[@value='Não']").click()   
                        time.sleep(0.3)             
                    except:
                        pass
                    try:                                   
                        driver.find_element(By.XPATH, f"//*[@value='Sim']").click() 
                        time.sleep(0.3) 
                        msg2 = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text                        
                        row = i + 1, matricula, msg2
                        writer.writerow(row)
                    except:
                        try:                    
                            driver.find_element(By.NAME, "cancelar").click()  
                            time.sleep(0.3)   
                            msg3 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text                            
                            row = i + 1, matricula, msg3
                            writer.writerow(row)
                        except:
                            try:     
                                time.sleep(0.3)  
                                msg4 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                                row = i + 1, matricula, msg4
                                writer.writerow(row)
                            except: 
                                time.sleep(0.3)  
                                msg5 = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                                row = i + 1, matricula, msg5
                                writer.writerow(row)
                        
            elif matricula == 0:
                msg6 = "matricula zerada"
                row = i + 1, matricula, msg6
                writer.writerow(row)
                pass
        elif alterar == 0:     
            msg7 = "NÃO ALTERAR"
            row = i + 1, matricula, msg7
            writer.writerow(row)
            pass
        
        calculoPorcentagem(contador, totalRow)
