from selenium.webdriver.common.by import By
from db_arquivos import teste
from db_login import login, driver
import csv, time
from datetime import datetime

login()

cabeçalho = ['#', 'RA', 'OS', 'MAT', 'LOCAL', 'SETOR', 'QUADRA', 'ROTA', 'SEQUENCIA', 'FISCAL', 'OBSERV_OS']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    today = datetime.today().strftime("%d/%m/%Y")
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirElaborarOrdemServicoRoteiroCriteriosAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
    driver.find_element(By.XPATH, "//option[@value='890']").click()
    driver.find_element(By.XPATH, "//option[@value='613']").click()
    driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[7]/td/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/input").click()
    driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
    selecionadas = driver.find_element(By.NAME, "selecionadas").get_attribute('value')
    selecionadas = int(selecionadas)
    j = 1
    while j <= selecionadas:        
        ra1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[7]/div/a".format(j))
        os1 =  driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[8]/div/a".format(j))
        num_ra = ra1.text
        num_os = os1.text                
        jan_princ = driver.window_handles[0]            
        ra1.click()
        popup = driver.window_handles[1]
        driver.switch_to.window(popup)
        time.sleep(0.4)
        observ = driver.find_element(By.NAME, "observacao").get_attribute('value')
        driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        local = driver.find_element(By.NAME, "idLocalidade").get_attribute('value')
        setor = driver.find_element(By.NAME, "idSetorComercial").get_attribute('value')
        quadra = driver.find_element(By.NAME, "idQuadra").get_attribute('value')
        rota = driver.find_element(By.NAME, "rota").get_attribute('value')
        matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
        sequencia = driver.find_element(By.NAME, "sequencialRota").get_attribute('value')
        driver.close()
        driver.switch_to.window(jan_princ)
        linha = j, num_ra, num_os, matricula, local, setor, quadra, rota, sequencia, "" ,observ
        escritor.writerow(linha)
        j = j+1