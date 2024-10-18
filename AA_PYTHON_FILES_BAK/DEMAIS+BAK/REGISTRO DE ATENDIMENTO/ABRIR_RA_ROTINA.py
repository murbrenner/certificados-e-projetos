import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pyautogui
import re
from arquivos import abrir_ra
from login import murilo, driver

df = pd.read_csv(abrir_ra)
murilo()

for i in df.index:
    driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRegistroAtendimentoAction.do?menu=sim')
    driver.find_element(By.NAME, "tipoSolicitacao").send_keys('2.09')
    driver.find_element(By.NAME, "especificacao").send_keys('PROGRAMA HIDROMETRACAO 2023')
    driver.find_element(By.NAME, "observacao").send_keys(' ')#(str(df['OBSERVACAO'][i]))
    driver.find_element(By.NAME, "avancar").click()
    driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    time.sleep(0.5)
    pyautogui.keyDown('ESC')
    pyautogui.keyUp('ESC')
    try:
        inex = driver.find_element(By.NAME, "inscricaoImovel").get_attribute("value")
        if inex == "Imóvel Inexistente":
            j = i + 1
            print(j, str(df['MATRICULA'][i]), inex)
        else:
            try:
                driver.find_element(By.XPATH, "//*[@value='Avançar']").click()
                driver.find_element(By.XPATH, "//*[@value='Avançar']").click()
                driver.find_element(By.NAME, "concluir").click()
                txt = driver.find_element(By.CSS_SELECTOR,
                                          'body > table:nth-child(5) > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > div > span').text
                num = re.findall(r'\d+', txt)
                num_ra = ' '.join(num).replace("'", '').replace('[', '').replace(']', '')
                j = i + 1
                print(j, str(df['MATRICULA'][i]), num_ra)
            except:
                j = i + 1
                print(j, str(df['MATRICULA'][i]), "JA TEM O.S?")
                pass
    except:
        j = i + 1
        print(j, str(df['MATRICULA'][i]), "ERRO 2")

        pass