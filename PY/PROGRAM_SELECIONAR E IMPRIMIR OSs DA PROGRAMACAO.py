from selenium.webdriver.common.by import By
from db_arquivos import teste
from db_login import login, driver
import csv, time
from datetime import datetime
from db_fiscais import fiscais, num_nomes, num_nomes_joined

login()

i=1
while i <= 35:
    fiscal = num_nomes_joined[i]
    fiscal1 = num_nomes
    print(fiscal)    
    
    today = datetime.today().strftime("%d/%m/%Y")
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
    try:
        driver.find_element(By.LINK_TEXT, fiscal1[i]).click()
        driver.find_element(By.XPATH, '//a[@title="Consultar Dados da Ordem de Serviço"]').click()
        time.sleep(1111)
        while j <= 20:
            driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='osSelecionada']").click()
            time.sleep(1111)
            j = j+1
        time.sleep(1111)
    except:
        pass
    #driver.find_element(By.XPATH, "//a[@href='javascript:facilitador(this,'{}')']".format()).click()
    driver.find_element(By.XPATH, "//*[@href='javascript:facilitador(this,'{}')']".format(fiscal)).click()
    time.sleep(1111)
    "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/div[2]/table/tbody/tr[1]/td[1]/table/tbody/tr/td[1]/input"
    "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/div[4]/table/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/div/input"
    "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/div[4]/table/tbody/tr[2]/td/table/tbody/tr[4]/td[1]/div/input"