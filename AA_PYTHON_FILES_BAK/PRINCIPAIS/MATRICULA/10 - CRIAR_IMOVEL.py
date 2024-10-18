import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, login, murilo2
from arquivos import inserir_imovel, teste
import csv

df = pd.read_csv(inserir_imovel)
murilo2()

header = ['#', 'STATUS']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        matricula = int(df['MATRICULA'][i])
        tipo_hab = str(df['TIPO_HAB'][i])
        complemento = str(df['COMPLEMENTO'][i])
        cx = str(df['CX'][i])
        cy = str(df['CY'][i])  

        if matricula == 0:
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirImovelAction.do?menu=sim")
            driver.find_element(By.NAME, "idLocalidade").send_keys(str(df['LOCAL'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "idSetorComercial").send_keys(str(df['SETOR'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "idQuadra").send_keys(str(df['QUADRA'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "lote").send_keys(str(df['LOTE'][i]))
            driver.find_element(By.NAME, "subLote").send_keys(str(df['SUBLOTE'][i]))
            driver.find_element(By.NAME, "testadaLote").send_keys(str(df['TESTADA'][i]))
            driver.find_element(By.NAME, "sequencialRota").send_keys(str(df['SEQUENCIA'][i]))
            
            driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

            try:
                driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
            except:
                pass

            driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
            janela_principal = driver.window_handles[0]
            janela_endereco = driver.window_handles[1]
            driver.switch_to.window(janela_endereco)
            driver.find_element(By.NAME, "logradouro").send_keys(str(df['COD_LOG'][i]), Keys.ENTER)
            try:
                driver.find_element(By.XPATH, "//input[@value='1']").click()
                driver.find_element(By.NAME, "cepSelecionado").click()
            except:
                pass
            #driver.find_element(By.XPATH, "//input[@value='7390']").click()
            driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
            driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
            if complemento != '0':
                driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))

            driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
            driver.switch_to.window(janela_principal)
            driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
            id_cliente = str(df['COD_CLIENTE'][i])                
            driver.find_element(By.NAME, "idCliente").send_keys(str(df['COD_CLIENTE'][i]), Keys.ENTER)
            time.sleep(0.2)
            driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
            driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
            time.sleep(0.2)
            driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

            categoria_res = str(df['RES'][i])
            categoria_com = str(df['COM'][i])
            categoria_pub = str(df['PUB'][i])
            if categoria_res >= '1':
                driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
                driver.find_element(By.NAME, "idSubCategoria").send_keys('01 - RESIDENCIAL')
                driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                driver.find_element(By.NAME, "botaoAdicionar").click()
            elif categoria_pub >= '1':
                driver.find_element(By.NAME, "idCategoria").send_keys('01 - PUBLICO')
                driver.find_element(By.NAME, "idSubCategoria").send_keys('04 - PUBLICO MUNICIPAL')
                driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                driver.find_element(By.NAME, "botaoAdicionar").click()
            elif categoria_com >= '1':
                driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
                driver.find_element(By.NAME, "idSubCategoria").send_keys('02 - COMERCIAL')
                driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com)
                driver.find_element(By.NAME, "botaoAdicionar").click()

            driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

            driver.find_element(By.NAME, "areaConstruida").send_keys(str(df['AREA'][i]), '00')
            
            driver.find_element(By.NAME, "pavimentoCalcada").send_keys('02 - CIMENTO')
            driver.find_element(By.NAME, "pavimentoRua").send_keys('02 - ASFALTO')
            driver.find_element(By.NAME, "fonteAbastecimento").send_keys('01 - CAEMA')
            driver.find_element(By.NAME, "situacaoLigacaoAgua").send_keys('02 - FACTIVEL')
            driver.find_element(By.NAME, "situacaoLigacaoEsgoto").send_keys('01 - POTENCIAL')
            #driver.find_element(By.NAME, "idLigacaoEsgotoEsgotamento").send_keys('NORMAL')
            driver.find_element(By.NAME, "perfilImovel").send_keys('05 - NORMAL')
            driver.find_element(By.NAME, "tipoDespejo").send_keys('01 - RESIDENCIAL')

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
            
            driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

            #driver.find_element(By.NAME, "numeroPontos").send_keys('6')
            #driver.find_element(By.NAME, "numeroMoradores").send_keys('2')

            if cx != "0":
                driver.find_element(By.NAME, "cordenadasUtmX").send_keys(cx)
                driver.find_element(By.NAME, "cordenadasUtmY").send_keys(cy)
                      
            
            driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            linha = i+1, msg_ok
            escritor.writerow(linha)
        else:
            try:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                linha = i+1, msg_er
                escritor.writerow(linha)
            except:
                linha = i+1, "JA POSSUI MATRICULA [{}]".format(matricula)
                escritor.writerow(linha)
                pass