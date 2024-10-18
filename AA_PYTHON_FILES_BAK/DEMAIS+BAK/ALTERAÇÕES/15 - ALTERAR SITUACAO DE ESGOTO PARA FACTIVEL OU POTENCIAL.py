from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import abrir_ra, elaboration

df = pd.read_csv(abrir_ra)
murilo()

situacao = 'POTENCIAL'

for i in df.index:
    url = ("http://gsan.caema.ma.gov.br:8080/gsan/exibirAlterarSituacaoLigacaoAction.do?menu=sim")
    driver.get(url)
    driver.find_element(By.NAME, "idOrdemServico").send_keys(str(df['OS'][i]), Keys.ENTER)
    print((str(df['MATRICULA'][i])))
    try:
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/strong[2]/input[2]").click()
        driver.find_element(By.NAME, "situacaoLigacaoEsgotoNova").send_keys(situacao)
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[5]/td/table/tbody/tr/td[2]/input").click()
        print(i+1, str(df['MATRICULA'][i]), 'Alterado')
    except:
        print(i+1, str(df['MATRICULA'][i]), 'Inalterado')