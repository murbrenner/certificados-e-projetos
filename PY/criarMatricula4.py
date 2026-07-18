import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *
import csv

df = pd.read_csv(databaseCSV4)
login()

relatorioGsan = relatorioGsan4

header = ['#', 'STATUS']

with open(databaseCSV4, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        contador = i+1
        local = int(df['LOCAL'][i])
        setor = int(df['SETOR'][i])
        quadra = int(df['QUADRA'][i])
        lote = int(df['LOTE'][i])
        sublote = int(df['SUBLOTE'][i])
        #testada = int(df['TESTADA'][i])
        sequencia = int(df['LOTE'][i])
        id_cliente = str(df['COD_CLIENTE'][i])   
        matricula = int(df['MATRICULA'][i])
        tipo_hab = str(df['TIPO_HAB'][i])
        complemento = str(df['COMPLEMENTO'][i])
        cx = str(df['CX'][i])
        cy = str(df['CY'][i])
        cep_gsan = int(df['CEP_GSAN'][i])      
        alterar = int(df['ALTERAR'][i])  

        if alterar == 1:
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirImovelAction.do?menu=sim")
            driver.find_element(By.NAME, "idLocalidade").clear()
            driver.find_element(By.NAME, "idLocalidade").send_keys(local)#, Keys.ENTER)
            #time.sleep(0.5)
            driver.find_element(By.NAME, "idSetorComercial").clear()
            driver.find_element(By.NAME, "idSetorComercial").send_keys(setor)#, Keys.ENTER)
            #time.sleep(0.5)            
            driver.find_element(By.NAME, "idQuadra").clear()
            driver.find_element(By.NAME, "idQuadra").send_keys(quadra, Keys.ENTER) 
            time.sleep(0.3)
            driver.find_element(By.NAME, "lote").clear() 
            time.sleep(0.2)                                        
            driver.find_element(By.NAME, "lote").send_keys(lote)               
            
            driver.find_element(By.NAME, "subLote").clear()
            driver.find_element(By.NAME, "subLote").send_keys(sublote)
            
            #driver.find_element(By.NAME, "testadaLote").clear()
            #driver.find_element(By.NAME, "testadaLote").send_keys(testada)
            
            driver.find_element(By.NAME, "sequencialRota").clear()
            driver.find_element(By.NAME, "sequencialRota").send_keys(sequencia)
            
            driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
            time.sleep(0.3)            

            try:                
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text   
                msg_er = re.findall(r'\d+', msg_er)
                msg_er = ''.join(msg_er)
                row = i+1, matricula, msg_er
                writer.writerow(row)
                mat_fail = 1
            except:                
                mat_fail = 0

            try:
                driver.find_element(By.XPATH, "//input[@value='Confirmar']").click() 
                time.sleep(0.3)
            except:
                pass            

            if matricula != 0:
                row = i+1, matricula
                writer.writerow(row)

            if matricula == 0:                
                if mat_fail == 0:      
                    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                    time.sleep(0.3)
                    janela_principal = driver.window_handles[0]
                    janela_endereco = driver.window_handles[1]
                    driver.switch_to.window(janela_endereco)
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "logradouro").send_keys(str(df['COD_LOG'][i]), Keys.ENTER)
                    time.sleep(0.2)                
                    driver.find_element(By.XPATH, "//input[@value='{}']".format(cep_gsan)).click()
                    time.sleep(0.2)            
                    driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
                    if complemento != '0':
                        driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))

                    driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                    time.sleep(0.2)
                    driver.switch_to.window(janela_principal)
                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                    time.sleep(0.4)                         
                    driver.find_element(By.NAME, "idCliente").send_keys(str(df['COD_CLIENTE'][i]), Keys.ENTER)
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()         
                    time.sleep(0.2)

                    categoria_res = int(df['RES'][i])
                    categoria_com = int(df['COM'][i])
                    categoria_pub = int(df['PUB'][i])
                    categoria_pub_mun = int(df['MUN'][i])
                    categoria_pub_est = int(df['EST'][i])
                    categoria_pub_fed = int(df['FED'][i])
                    categoria_com_peq = int(df['PEQ'][i])
                    categoria_ind = int(df['IND'][i])
                    time.sleep(0.2)

                    if categoria_res >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('01 - RESIDENCIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                        time.sleep(0.2)
                        driver.find_element(By.NAME, "botaoAdicionar").click()
                        time.sleep(0.2)
                    if categoria_pub >= 1:
                        if categoria_pub_mun >= 1:
                            driver.find_element(By.NAME, "idCategoria").send_keys('01 - PUBLICO')
                            time.sleep(0.4)
                            driver.find_element(By.NAME, "idSubCategoria").send_keys('04 - PUBLICO MUNICIPAL')
                            time.sleep(0.4)
                            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "botaoAdicionar").click()
                            time.sleep(0.2)
                    if categoria_pub >= 1:
                        if categoria_pub_est >= 1:
                            driver.find_element(By.NAME, "idCategoria").send_keys('01 - PUBLICO')
                            time.sleep(0.4)
                            driver.find_element(By.NAME, "idSubCategoria").send_keys('05 - PUBLICO ESTADUAL')
                            time.sleep(0.4)
                            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "botaoAdicionar").click()
                            time.sleep(0.2)

                    if categoria_pub >= 1:
                        if categoria_pub_fed >= 1:
                            driver.find_element(By.NAME, "idCategoria").send_keys('01 - PUBLICO')
                            time.sleep(0.4)
                            driver.find_element(By.NAME, "idSubCategoria").send_keys('06 - PUBLICO FEDERAL')
                            time.sleep(0.4)
                            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                            time.sleep(0.2)
                            driver.find_element(By.NAME, "botaoAdicionar").click()
                            time.sleep(0.2)
                    if categoria_com >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('02 - COMERCIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com)
                        time.sleep(0.2)
                        driver.find_element(By.NAME, "botaoAdicionar").click()  
                        time.sleep(0.2)          
                    if categoria_com_peq >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('08 - COM. PEQ. NEGOCIOS')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com_peq)
                        time.sleep(0.2)
                        driver.find_element(By.NAME, "botaoAdicionar").click()
                    if categoria_ind >= 1:
                        driver.find_element(By.NAME, "idCategoria").send_keys('03 - INDUSTRIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "idSubCategoria").send_keys('03 - INDUSTRIAL')
                        time.sleep(0.4)
                        driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_ind)
                        time.sleep(0.2)
                        driver.find_element(By.NAME, "botaoAdicionar").click()

                    time.sleep(0.5)

                    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                    time.sleep(0.3)

                    driver.find_element(By.NAME, "areaConstruida").send_keys(str(df['AREA'][i]), '00')
                    time.sleep(0.2)
                    driver.find_element(By.NAME, "pavimentoCalcada").send_keys('02 - CIMENTO')
                    driver.find_element(By.NAME, "pavimentoRua").send_keys('02 - ASFALTO')
                    driver.find_element(By.NAME, "fonteAbastecimento").send_keys('01 - CAEMA')
                    driver.find_element(By.NAME, "situacaoLigacaoAgua").send_keys('02 - FACTIVEL')
                    driver.find_element(By.NAME, "situacaoLigacaoEsgoto").send_keys('01 - POTENCIAL')
                    #driver.find_element(By.NAME, "idLigacaoEsgotoEsgotamento").send_keys('NORMAL')
                    driver.find_element(By.NAME, "perfilImovel").send_keys('05 - NORMAL')
                    driver.find_element(By.NAME, "tipoDespejo").send_keys('01 - RESIDENCIAL')

                    time.sleep(0.2)

                    if tipo_hab == '0':
                        driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('04 - TERRENO')
                        driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('09 - OUTROS')
                        driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('09 - OUTROS')
                        driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('09 - OUTROS')
                    elif tipo_hab == '1':
                        driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('01 - HABITADO')
                        driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('01 - PROPRIO')
                        driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('03 - ALVENARIA')
                        driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('02 - TELHA CERAMICA')

                    elif tipo_hab == '2':
                        driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('05 - CONSTRUCAO')
                        driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('01 - PROPRIO')
                        driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('03 - ALVENARIA')
                        driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('02 - TELHA CERAMICA')

                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                    time.sleep(0.2)
                    #driver.find_element(By.NAME, "numeroPontos").send_keys('6')
                    #driver.find_element(By.NAME, "numeroMoradores").send_keys('2')

                    if cx != "0":
                        driver.find_element(By.NAME, "cordenadasUtmX").send_keys(cx)
                        driver.find_element(By.NAME, "cordenadasUtmY").send_keys(cy)
                            
                    time.sleep(0.2)
                    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                    time.sleep(0.2)

                    msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                    row = i+1, msg_ok
                    writer.writerow(row) 

        percent1 = ((contador-1)*100)/totalRow
        percent1 = int(percent1)
        percent2 = (contador*100)/totalRow
        percent2 = int(percent2)
        if percent1 != percent2:            
            if percent2 != 100:
                print(f'{percent2}% CONCLUÍDO...')
            else:
                print(f'{percent2}% CONCLUÍDO!')