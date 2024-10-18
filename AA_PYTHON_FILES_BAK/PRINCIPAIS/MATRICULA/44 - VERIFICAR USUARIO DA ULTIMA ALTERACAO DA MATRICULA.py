from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo2, driver
from arquivos import elaboration, inserir_imovel, teste
import time, csv

df = pd.read_csv(elaboration)
murilo2()

header = ['#', 'MATRICULA', 'DATA', 'TIPO', 'USER']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, "2").click()
        matricula = str(df['MATRICULA'][i])
        driver.find_element(By.NAME, "idImovelDadosComplementares").send_keys(matricula, Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar Histórico']").click()    
        j = 1    
        while j < 5:        
            try:   
                data = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[2]/td/div/table/tbody/tr/td[1]/div").text
                data = data[:10]
                tipo_acao =  driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[2]/td/div/table/tbody/tr/td[2]/div").text
                executor = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[2]/td/div/table/tbody/tr/td[3]/div").text
                
            except:
                pass  
            try:         
                data = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/div".format(j)).text
                data = data[:10]
                tipo_acao =  driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[2]/div".format(j)).text
                executor = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[3]/div".format(j)).text
                
            except:
                pass
            linha = j, matricula, data, tipo_acao, executor
            escritor.writerow(linha)     
            j = j + 1  