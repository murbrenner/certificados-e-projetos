from selenium.webdriver.common.by import By
from db_arquivos import teste
from db_login import login, driver
import csv, time
from datetime import datetime
from db_fiscais import fiscais, num_nomes, num_nomes_joined

login()

cabeçalho = ['#', 'RA', 'OS', 'MAT', 'LOCAL', 'SETOR', 'QUADRA', 'SEQUENCIA', 'ROTA', 'FISCAL']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    today = datetime.today().strftime("%d/%m/%Y")
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
    driver.find_element(By.XPATH, "//a[@href='javascript:facilitador(this,'DIMASDIASCOSTA')']").click()
    
    time.sleep(11111)
    fiscal = num_nomes_joined
    j = 0
    l = 1
    while j <= 35:                     
        try: 
            driver.find_element(By.XPATH, "href='javascript:facilitador(this,'{}')").format(fiscal[l])
            print(num_nomes_joined[l])
            time.sleep(1111)
            j = j + 1
            fiscal_link = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/div[{}]/table/tbody/tr/td[1]/table/tbody/tr/td[2]/a/b".format(j))
            fiscal_link.click()            
            todas_fisc = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/div[{}]/table/tbody/tr[2]/td/table/tbody/tr[1]/td[1]/div/strong/a".format(l))
            todas_fisc.click()
            todas_fisc.click()
            # print("J: ", j, "L: ", l)            
            
            
            
            # os1 =  driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[8]/div/a".format(j))
            # num_ra = ra1.text
            # num_os = os1.text                
            # jan_princ = driver.window_handles[0]            
            
            # popup = driver.window_handles[1]
            # driver.switch_to.window(popup)
            # time.sleep(0.4)
            # driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
            # local = driver.find_element(By.NAME, "idLocalidade").get_attribute('value')
            # setor = driver.find_element(By.NAME, "idSetorComercial").get_attribute('value')
            # quadra = driver.find_element(By.NAME, "idQuadra").get_attribute('value')
            # rota = driver.find_element(By.NAME, "rota").get_attribute('value')
            # matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
            # sequencia = driver.find_element(By.NAME, "sequencialRota").get_attribute('value')
            # driver.close()
            # driver.switch_to.window(jan_princ)
            # linha = j, num_ra, num_os, matricula, local, setor, quadra, sequencia, rota
            # escritor.writerow(linha)
            
        except:            
            j = j + 1
            time.sleep(1111)
            pass
        