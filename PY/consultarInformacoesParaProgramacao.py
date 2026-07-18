from selenium.webdriver.common.by import By
from db_arquivos import *
from db_login import login, driver
import csv, time
from datetime import datetime

login()

relatorioGsan = relatorioGsan1

cabeçalho = ['#', 'RA', 'OS', 'MATRICULA', 'LOCAL', 'SETOR', 'QUADRA', 'ROTA', 'SEQUENCIA', 'FISCAL', 'ENDERECO']
with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(cabeçalho)

    today = datetime.today().strftime("%d/%m/%Y")
    driver.get("http://g1.caema.ma.gov.br/gsan/exibirElaborarOrdemServicoRoteiroCriteriosAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
    time.sleep(0.2)
    try:
        driver.find_element(By.XPATH, "//option[@value='890']").click()
        time.sleep(0.2)
    except:
        driver.find_element(By.XPATH, "//option[@value='613']").click()
        time.sleep(0.2)
    driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[7]/td/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/input").click()
    time.sleep(0.2)
    driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
    time.sleep(0.2)
    selecionadas = driver.find_element(By.NAME, "selecionadas").get_attribute('value')
    selecionadas = int(selecionadas)
    time.sleep(0.2)
    j = 1
    while j <= selecionadas:        
        ra1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[7]/div/a".format(j))
        os1 =  driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[8]/div/a".format(j))
        num_ra = ra1.text
        num_os = os1.text                
        jan_princ = driver.window_handles[0]     
        time.sleep(0.2)       
        ra1.click()
        time.sleep(0.2)
        popup = driver.window_handles[1]
        driver.switch_to.window(popup)
        time.sleep(0.4)
        
        #observ = driver.find_element(By.NAME, "observacao").get_attribute('value')
        driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        endereco = driver.find_element(By.NAME, "enderecoOcorrencia").get_attribute('value')
        local = driver.find_element(By.NAME, "idLocalidade").get_attribute('value')
        setor = driver.find_element(By.NAME, "idSetorComercial").get_attribute('value')
        quadra = driver.find_element(By.NAME, "idQuadra").get_attribute('value')
        rota = driver.find_element(By.NAME, "rota").get_attribute('value')
        matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
        sequencia = driver.find_element(By.NAME, "sequencialRota").get_attribute('value')
        driver.close()
        driver.switch_to.window(jan_princ)
        linha = j, num_ra, num_os, matricula, local, setor, quadra, rota, sequencia, "" , endereco #observ
        writer.writerow(linha)
        j = j+1