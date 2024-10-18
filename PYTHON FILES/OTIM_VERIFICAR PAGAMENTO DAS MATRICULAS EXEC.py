from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration
import time

df = pd.read_csv(elaboration)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "6").click()
    matricula = str(df['MATRICULA'][i])
    driver.find_element(By.NAME, "idImovelPagamentos").send_keys(matricula, Keys.ENTER)
    try:                                         
        tipo_deb = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[2]/a").text
        valor_guia1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[3]").text
        valor_guia2 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[4]").text
        data_pag = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[5]/a").text
        if tipo_deb == "RELIGACAO NO HIDROMETRO":
            print(i+1, matricula, tipo_deb, valor_guia1, valor_guia2, data_pag, sep=';')
    except:
        try:
            tipo2_deb = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/a").text
            valor2_guia1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[3]").text
            valor2_guia2 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[4]").text
            data2_pag = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[5]").text
            if tipo2_deb == "RELIGACAO NO HIDROMETRO":
                print(i+1, matricula, tipo2_deb, valor2_guia1, valor2_guia2, data2_pag, sep=';')
        except:
            try:
                tipo3_deb = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/a").text
                valor3_guia1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[3]").text
                valor3_guia2 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[4]").text
                data3_pag = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[5]/a").text   
                if tipo3_deb == "RELIGACAO NO HIDROMETRO":
                    print(i+1, matricula, tipo3_deb, valor3_guia1, valor3_guia2, data3_pag, sep=';')
            except:
                print(i+1, matricula, "NADA ENCONTRADO", sep=';')

                #if tipo_deb == "RELIGACAO NO HIDROMETRO":
                    #print(i+1, matricula, tipo_deb, valor_guia1, valor_guia2, data_pag, tipo2_deb, valor2_guia1, valor2_guia2, data2_pag, tipo3_deb, valor3_guia1, valor3_guia2, data3_pag, sep=';')
        



    
        

    
       
    # try:  
    #     tipo2_deb = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/a").text
    #     valor2_guia1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[3]").text
    #     valor2_guia2 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[4]").text
    #     data2_pag = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[5]").text
    #     if tipo2_deb == "RELIGACAO NO HIDROMETRO":
    #         print(i+1, matricula, tipo2_deb, valor2_guia1, valor2_guia2, data2_pag, sep=';')
    # except:
    #     print(i+1, matricula, "NADA ENCONTRADO", sep=';')
    #     pass
    


    # try: 
    #     tipo3_deb = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/a").text
    #     valor3_guia1 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[3]").text
    #     valor3_guia2 = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[4]").text
    #     data3_pag = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[5]/a").text    
    #     if tipo3_deb == "RELIGACAO NO HIDROMETRO":
    #         print(i+1, matricula, tipo3_deb, valor3_guia1, valor3_guia2, data3_pag, sep=';')              
    # except:   
    #     print(i+1, matricula, "NADA ENCONTRADO")
    #     pass

    # time.sleep(1)
    # #print(i+1, matricula, tipo_deb, valor_guia1, valor_guia2, data_pag, tipo_deb2, valor2_guia1, valor2_guia2, data_pag2, tipo_deb3, valor3_guia1, valor3_guia2, data_pag3)


    # # com_sem_hd = driver.find_element(By.NAME, "tipoLigacaoDadosCadastrais").get_attribute('value')
    # # roteirizacao = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
    # # if roteirizacao == 'IMÓVEL INEXISTENTE':
    # #     print(i+1, str(df['MATRICULA'][i]), 'IMÓVEL INEXISTENTE', sep=',')
    # # else:
    # #     print(i+1, str(df['MATRICULA'][i]), com_sem_hd, sep=',')
