from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, teste

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    #driver.find_element(By.NAME, "situacaoOrdemServico").send_keys("PENDENTES")
    driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
    #driver.find_element(By.NAME, "periodoGeracaoInicial").send_keys("08/08/2023")
    #driver.find_element(By.NAME, "periodoGeracaoFinal").send_keys("08/08/2023")
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    try:
        driver.find_element(By.LINK_TEXT, "Dados do Encerramento da Ordem de Serviço").click()
        obs = driver.find_element(By.NAME, "parecerEncerramento").get_attribute("value")
        #obs = driver.find_element(By.NAME, "observacao").get_attribute("value")
        os = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute("value")
        ra = driver.find_element(By.NAME, "numeroRA").get_attribute("value")
        obs = obs.replace("\n", " ")
        j = i + 1
        print(j, obs, os, ra, sep=';')
    except:
        j = i + 1
        print(j, obs, "0", "0", sep=';')
