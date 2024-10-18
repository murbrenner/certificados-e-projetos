from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver

filename = 'C:\\Users\\Murilo Brenner\\Downloads\\CREDITO - SEDUC.csv'
df = pd.read_csv(filename)

murilo()

for i in df.index:
    url = ("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.get(url)
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
    print((str(df['RA'][i])), end=" ")
    try:
        driver.find_element(By.NAME, "Submit").click()
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('CANCELADO PELA CAEMA')
        driver.find_element(By.NAME, "parecerEncerramento").send_keys('CANCELAR R.A. NAO HA DUPLICIDADE DE PAGAMENTO DO MÊS 10/2022 PARA ESTA MATRICULA')
        driver.find_element(By.NAME, "botaoConcluir").click()
        print('ENCERRADO')
    except NoSuchElementException:
        print('DEU ALGUM ERRO')


