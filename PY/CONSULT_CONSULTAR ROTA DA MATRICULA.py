from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste, inserir_imovel
import csv, time

df = pd.read_csv(elaboration)
login()

cabeçalho = ['#', 'MATRICULA', 'LOCAL', 'SETOR', 'QUADRA', 'SEQUENCIA', 'SUBLOTE', 'ROTA']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "3").click()
        matricula = str(df['MATRICULA'][i])
        driver.find_element(By.NAME, "idImovelAnaliseMedicaoConsumo").send_keys(matricula, Keys.ENTER)
        roteirizacao = driver.find_element(By.NAME, "matriculaImovelAnaliseMedicaoConsumo").get_attribute('value')        
        rota = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[2]/td[5]/div").text
        local = roteirizacao[:3]
        setor = roteirizacao[4:7]
        quadra = roteirizacao[8:11]
        sequencia = roteirizacao[12:16]
        sublote = roteirizacao[17:20]       
        if roteirizacao == 'IMÓVEL INEXISTENTE':
            linha = i+1, matricula, 'IMÓVEL INEXISTENTE'
            escritor.writerow(linha)
        else:
            linha = i+1, matricula, local, setor, quadra, sequencia, sublote, rota
            escritor.writerow(linha)

