from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import *
from db_arquivos import *
from db_funcoes import *
import csv, time

df = pd.read_csv(databaseCSV3)
login()

relatorioGsan = relatorioGsan3

with open(databaseCSV3, 'r', encoding='utf-8') as db:
    totalRow = sum(1 for row in db) - 1  # subtrai 1 se tiver cabeçalho

header = ['#', 'MATRICULA', 'LOCAL', 'SETOR', 'QUADRA', 'LOTE', 'SUBLOTE', 'SEQUENCIA', 'ROTA']
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    escritor = csv.writer(relatorioGsan)
    escritor.writerow(header)

    for i in df.index:        
        driver.get("http://g1.caema.ma.gov.br/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "3").click()
        time.sleep(0.2)
        matricula = str(df['imv_id'][i])
        if matricula != "0":
            driver.find_element(By.NAME, "idImovelAnaliseMedicaoConsumo").send_keys(matricula, Keys.ENTER)
            time.sleep(1)
            try:
                janela = driver.window_handles[0]
                popup = driver.window_handles[1]
                driver.switch_to.window(popup)
                driver.close()
                driver.switch_to.window(janela)
            except:
                pass
        
            roteirizacao = driver.find_element(By.NAME, "matriculaImovelAnaliseMedicaoConsumo").get_attribute('value')        
            rota = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[2]/td[5]/div").text
            local = roteirizacao[:3]
            setor = roteirizacao[4:7]
            quadra = roteirizacao[8:11]
            lote = roteirizacao[12:16]
            sublote = roteirizacao[17:20]    
            sequencia = lote#driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[2]/td[6]/div").text 
            if roteirizacao == 'IMÓVEL INEXISTENTE':
                row = i+1, matricula, 'IMÓVEL INEXISTENTE'
                escritor.writerow(row)
            else:
                row = i+1, matricula, local, setor, quadra, lote, sublote, sequencia, rota
                escritor.writerow(row)
    
        elif matricula == "0":
            row = i+1, matricula, 0, 0, 0, 0, 0, 0, 0
            escritor.writerow(row)

        calculoPorcentagem(i+1, totalRow)

