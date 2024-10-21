import time
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import inserir_imovel, elaboration

df = pd.read_csv(inserir_imovel)
login()


for i in df.index:    
    categoria_res = int(df['RES'][i])
    categoria_com = int(df['COM'][i])
    categoria_pub = int(df['PUB'][i])
    categoria_com_peq = int(df['PEQ'][i])
    categoria_res_pop = int(df['POP'][i])
    categoria_ind = int(df['IND'][i])

    alterar = int(df['ALTERAR'][i])
    matricula = int(df['MATRICULA'][i])

    if alterar == 1:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
        
        driver.find_element(By.NAME, 'matriculaFiltro').send_keys(matricula)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        driver.find_element(By.ID, "4").click()

        try:
            driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
        except:
            pass
        
        driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[1]/div/a/img").click()
        popup = driver.switch_to.alert
        popup.accept()

        # try:
            
        #     driver.find_element(By.XPATH, "//*[@src='/gsan/imagens/Error.gif']").click()
        #     popup = driver.switch_to.alert
        #     popup.accept()
        # except:
        #     pass

        time.sleep(0.2)        

        if categoria_res >= 1:
            if categoria_res_pop >= 1:
                driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
                time.sleep(0.2) 
                driver.find_element(By.NAME, "idSubCategoria").send_keys('07 - RESIDENCIAL POPULAR')
                driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                driver.find_element(By.NAME, "botaoAdicionar").click()
            elif categoria_res_pop == 0:
                driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
                time.sleep(0.2) 
                driver.find_element(By.NAME, "idSubCategoria").send_keys('01 - RESIDENCIAL')
                driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                driver.find_element(By.NAME, "botaoAdicionar").click()
        if categoria_pub >= 1:
            driver.find_element(By.NAME, "idCategoria").send_keys('01 - PUBLICO')
            time.sleep(0.2) 
            driver.find_element(By.NAME, "idSubCategoria").send_keys('04 - PUBLICO MUNICIPAL')
            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
            driver.find_element(By.NAME, "botaoAdicionar").click()
        if categoria_com >= 1:
            driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
            time.sleep(0.2) 
            driver.find_element(By.NAME, "idSubCategoria").send_keys('02 - COMERCIAL')
            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com)
            driver.find_element(By.NAME, "botaoAdicionar").click()
        if categoria_com_peq >= 1:
            driver.find_element(By.NAME, "idCategoria").send_keys('02 - COMERCIAL')
            time.sleep(0.2) 
            driver.find_element(By.NAME, "idSubCategoria").send_keys('08 - COM. PEQ. NEGOCIOS')
            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com_peq)
            driver.find_element(By.NAME, "botaoAdicionar").click()
        if categoria_ind >= 1:
            driver.find_element(By.NAME, "idCategoria").send_keys('03 - INDUSTRIAL')
            time.sleep(0.2) 
            driver.find_element(By.NAME, "idSubCategoria").send_keys('03 - INDUSTRIAL')
            driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_ind)
            driver.find_element(By.NAME, "botaoAdicionar").click()
        
        
        time.sleep(0.2)
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
        
        try:
            driver.find_element(By.XPATH, "//input[@value='Não']").click()
        except:
            pass        

        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            print(i+1, matricula, msg_ok)
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i+1, matricula, msg_er)

    else:
        print(i+1, matricula, "NAO PRECISA ALTERAR")