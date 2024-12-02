import time, os, csv, chardet
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elab_date, down_path, teste

df = pd.read_csv(elab_date)
login()

hoje = datetime.today()
hoje = hoje.strftime("%d/%m/%Y")

contador = 1

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "situacaoOrdemServico").send_keys("ENCERRADOS")
    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[8]/td[2]/input[1]")
    driver.find_element(By.XPATH, "//option[@value='713']").click()
    driver.find_element(By.XPATH, "//option[@value='714']").click()   
    driver.find_element(By.XPATH, "//option[@value='9162']").click()    
    driver.find_element(By.XPATH, "//input[@value='  >  ']").click()    
    driver.find_element(By.NAME, "periodoGeracaoInicial").clear()   
    driver.find_element(By.NAME, "periodoGeracaoFinal").clear()       
    driver.find_element(By.NAME, "periodoEncerramentoInicial").clear()
    driver.find_element(By.NAME, "periodoEncerramentoInicial").send_keys(str(df['INICIO'][i]))
    driver.find_element(By.NAME, "periodoEncerramentoFinal").clear()
    driver.find_element(By.NAME, "periodoEncerramentoFinal").send_keys(str(df['FIM'][i]))    
    driver.find_element(By.NAME, "municipio").send_keys("1"), Keys.ENTER
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    
    try:
        driver.find_element(By.XPATH, "//img[@title='Imprimir Ordens de Serviço']").click()
        driver.find_element(By.XPATH, "//input[@value='6']").click()        
        driver.find_element(By.XPATH, "//input[@value='Gerar']").click()
        print("MÊS {}/{} GERADO".format(contador, str(df['ANO'][i])))
    except:
        print("MÊS {}/{} SEM O.S".format(contador, str(df['ANO'][i])))
        pass   
    time.sleep(1)

    
    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(down_path)
    full_path = [os.path.join(down_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

        
    with open(latest_file, mode="r", encoding='ISO-8859-1') as latest_file:
        reader = csv.reader(latest_file)        

        df2 = pd.read_csv(latest_file, delimiter=';')     

        with open(teste, mode="w", newline="") as teste:
            escritor = csv.writer(teste)
            header = ['MATRICULA', 'ESPECIFICACAO', 'MOTIVO', 'DATA_ENC_CORTE']
            escritor.writerow(header) 

            for j in df2.index:                
                motivo = str(df2["Motivo Encerramento"][j])                 
                matricula = str(df2['Imovel'][j]) 
                data_enc =  str(df2['Data Encerramento'][j]) 
                especif =  str(df2['Especificacao'][j])
                data_enc = data_enc[:10]
                data_enc = datetime.strptime(data_enc, "%Y-%m-%d")
                data_enc = data_enc.strftime("%d/%m/%Y")
                if motivo == 'CONCLUSAO DO SERVICO': 
                    linha = matricula, especif, motivo, data_enc
                    escritor.writerow(linha)
                
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
            driver.find_element(By.ID, "10").click()
            driver.find_element(By.NAME, "idImovelRegistroAtendimento").send_keys(matricula, Keys.ENTER)
            k = 1
            try:
                while k < 15:                            
                    tipo_os = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[2]".format(k)).text
                    if tipo_os == 'RELIGACAO NO HIDROMETRO':
                        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/a".format(k)).click()
                        time.sleep(0.5)
                        janela1 = driver.window_handles[0]
                        janela2 = driver.window_handles[1]                                
                        janela3 = driver.window_handles[2]
                        driver.switch_to.window(janela3)                             
                        
                        driver.find_element(By.LINK_TEXT, "Dados do Encerramento da Ordem de Serviço").click()
                        motivo2 = driver.find_element(By.NAME, "motivoEncerramento").get_attribute('value')
                        situacao = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
                        driver.find_element(By.XPATH, "//input[@value='Fechar']").click() 
                        situacao = driver.find_element(By.NAME, "unidadeEncerramentoDtUltimaAlteracao").get_attribute('value')         
                        driver.switch_to.window(janela1)                                
                        
                        #situacao = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[4]".format(k)).text
                        print(tipo_os, situacao, motivo2)                            
                    k = k+1
            except:
                pass