from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, abrir_ra

df = pd.read_csv(abrir_ra)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirEfetuarLigacaoAguaComInstalacaoHidrometroSemRAAction.do?menu=sim")

    driver.find_element(By.NAME, "matriculaImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    data_lig = str(df['DATA_LIG'][i]).replace('/', '')
    driver.find_element(By.NAME, "dataLigacao").send_keys(data_lig)#(str(df['DATA_LIG'][i]))
    driver.find_element(By.NAME, "materialLigacao").send_keys('PVC SOLDAVEL')
    driver.find_element(By.NAME, "diametroLigacao").send_keys('3/4')
    driver.find_element(By.NAME, "perfilLigacao").send_keys('NORMAL')

    # driver.find_element(By.NAME, "numeroHidrometro").send_keys(str(df['NUMERO_HD'][i]))
    # data_inst = str(df['DATA_LIG'][i]).replace('/', '')
    # driver.find_element(By.NAME, "dataInstalacao").send_keys(data_inst)
    # driver.find_element(By.NAME, "localInstalacao").send_keys('INTERNO')
    # driver.find_element(By.NAME, "protecao").send_keys('COM LACRE')
    # driver.find_element(By.NAME, "leituraInstalacao").send_keys(str(df['LEITURA'][i]))

    driver.find_element(By.XPATH, "//input[@value='Efetuar']").click()