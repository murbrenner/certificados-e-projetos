from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, csv
from db_arquivos import *
from db_login import login, driver
from db_funcoes import *

df = pd.read_csv(databaseCSV2)
login()

hoje = date.today()
hoje = hoje.strftime("%d/%m/%Y")
motivo = "CONCLUSAO DO SERVIÇO"

header = ['#', 'MSG']

relatorioGsan = relatorioGsan2

with open(databaseCSV2, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        contador = i + 1
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
        os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
        parecer = str(df['PARECER'][i])
        time.sleep(0.3)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        time.sleep(0.3)
        status_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        if status_os != 'Encerrada':    
            driver.find_element(By.XPATH, "//input[@value='Encerrar']").click()
            time.sleep(0.3)
            driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
            time.sleep(0.1)
            driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
            time.sleep(0.1)
            driver.find_element(By.NAME, "observacaoEncerramento").send_keys(parecer)
            time.sleep(0.1)
            driver.find_element(By.NAME, "ButtonAtividade").click()
            time.sleep(0.5)
            popup = driver.window_handles[1]
            janela = driver.window_handles[0]
            driver.switch_to.window(popup)
            driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr/td/table[3]/tbody/tr[9]/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[4]/a/img').click()
            time.sleep(0.3)
            driver.find_element(By.NAME, 'horaInicioExecucao').send_keys("0800")
            time.sleep(0.1)
            driver.find_element(By.NAME, 'horaFimExecucao').send_keys("1800")
            time.sleep(0.1)
            driver.find_element(By.NAME, "idEquipeNaoProgramada").send_keys("CAEMA-CADASTRO SEDE")
            time.sleep(0.1)
            driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
            time.sleep(0.3)
            driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
            time.sleep(0.3)
            driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
            time.sleep(0.3)
            driver.switch_to.window(janela)   
            time.sleep(0.3)
            driver.find_element(By.NAME, "ButtonEncerrar").click() 
            time.sleep(0.5)            
            driver.find_element(By.XPATH, "//input[@value='Efetuar']").click()
            time.sleep(0.5)
            driver.find_element(By.XPATH, "//input[@value='Sim']").click()
            time.sleep(0.5)
            try:
                msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                row = i+1, msg_ok
                writer.writerow(row)
            except:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                row = i + 1, msg_er
                writer.writerow(row)

        elif status_os == 'Encerrada':  
            msg_enc = "ORDEM DE SERVIÇO JÁ ENCONTRADA COMO ENCERRADA."
            row = i + 1, msg_enc
            writer.writerow(row)     
        
        calculoPorcentagem(contador, totalRow)