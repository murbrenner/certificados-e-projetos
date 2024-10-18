import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pyautogui
from db_arquivos import abrir_ra
from db_login import login, driver, murilo2
import re

df = pd.read_csv(abrir_ra)
login()

for i in df.index:
    driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim')
    driver.find_element(By.NAME, "tipoSolicitacao").send_keys('ATENDIMENTO RAPIDO')
    driver.find_element(By.NAME, "especificacao").send_keys('COMENTARIO')
    driver.find_element(By.NAME, "observacao").send_keys(str(df['OBSERVACAO'][i]))
    driver.find_element(By.NAME, "avancar").click()
    driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)

    local_anexo = "Z:\\AAA_IMAGENS_ANEXO_CADASTRO\\OUTROS\\REDE ESGOTO CALHAU.pdf"

    try:
        inex = driver.find_element(By.XPATH, "//input[@value='Imóvel Inexistente']").get_attribute("value")
        if inex == "Imóvel Inexistente":
            j = i + 1
            print(j, str(df['MATRICULA'][i]), inex)
    except:
        try:
            ja_existe = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            j = i + 1
            print(j, str(df['MATRICULA'][i]), ja_existe)
        except:
            pass
            driver.find_element(By.ID, "3").click()
            time.sleep(0.5)
            driver.find_element(By.ID, "4").click()
            c = 1
            tempo = 3
            while c <= 6:                
                nome = 'ANEXO_FRAUDE'
                local_anexo = "Z:\\AAA_IMAGENS_ANEXO_CADASTRO\\OUTROS\\{} ({}).jpg".format(nome, c)
                try:
                    driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td[2]").click()
                    time.sleep(1)
                    pyautogui.typewrite(local_anexo)
                    time.sleep(0.2)
                    pyautogui.press('ENTER')   
                    time.sleep(tempo)                 
                    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()                     
                except:                                                                       
                    pass
                tempo = 0.3                
                c = c + 1 
                
            driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            msg_ok = num = re.findall(r'\d+', msg_ok)
            msg_ok = ' '.join(msg_ok).replace("'", '').replace('[', '').replace(']', '')
            j = i + 1
            print(j, str(df['MATRICULA'][i]), msg_ok)
                