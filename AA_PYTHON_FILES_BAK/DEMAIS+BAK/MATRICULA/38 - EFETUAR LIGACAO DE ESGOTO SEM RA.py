from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration
from datetime import date

df = pd.read_csv(elaboration)
murilo()
hoje = date.today().strftime('%d/%m/%Y')
hoje = hoje.replace('/', '')

for i in df.index:
    driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirEfetuarLigacaoEsgotoAction.do?funcionalidade=semRA')
    try:
        driver.find_element(By.NAME, 'matriculaImovel').send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        driver.find_element(By.NAME, 'dataLigacao').send_keys(hoje)
        driver.find_element(By.NAME, 'diametroLigacao').send_keys('4 POLEGADAS')
        driver.find_element(By.NAME, 'materialLigacao').send_keys('PVC')
        driver.find_element(By.NAME, 'perfilLigacao').send_keys('CONVENCIONAL')
        driver.find_element(By.XPATH, "//input[@value='Efetuar']").click()
        msg_ok = driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span').text
        print(i+1, str(df['MATRICULA'][i]), msg_ok)
    except:
        erro_sit = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span').text
        print(i+1, str(df['MATRICULA'][i]), erro_sit)



