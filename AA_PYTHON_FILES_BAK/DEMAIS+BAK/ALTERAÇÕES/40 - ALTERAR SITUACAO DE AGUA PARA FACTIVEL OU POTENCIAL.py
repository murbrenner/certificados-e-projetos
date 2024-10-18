import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import teste, elaboration

df = pd.read_csv(elaboration)
murilo()

nova_situacao = 'POTENCIAL'

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAlterarSituacaoLigacaoAction.do?menu=sim")
    driver.find_element(By.NAME, "idOrdemServico").send_keys(str(df['OS'][i]), Keys.ENTER)
    try:
        driver.find_element(By.XPATH, "//input[@value='1']").click()
        time.sleep(0.5)
        driver.find_element(By.NAME, "situacaoLigacaoAguaNova").send_keys(nova_situacao)
        driver.find_element(By.XPATH, "//input[@value='Alterar']").click()
        alt_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(i+1, str(df['MATRICULA'][i]), alt_ok)
    except:
        nao_alt = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span').text
        print(i+1, str(df['MATRICULA'][i]), nao_alt)