from selenium.webdriver.common.by import By
import pandas as pd
from login import murilo, driver
from arquivos import prog_fisc, elab_date
from fiscais import abrev_nomes, abrev_nomes_joined, fiscais

df = pd.read_csv(prog_fisc)
murilo()

for d in df.index:
    today = str(df['DATA'][d])
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
    for i in df.index:
        new_day = str(df['DATA_NEW'][i])
        try:
            driver.find_element(By.PARTIAL_LINK_TEXT, abrev_nomes).click()
            driver.find_element(By.XPATH, "//input[@value='{}___{}']".format(str(df['OS'][i]), abrev_nomes_joined)).click()

            driver.find_element(By.NAME, "ButtonReprogramarOS").click()
            janela_principal = driver.window_handles[0]
            popup = driver.window_handles[1]
            driver.switch_to.window(popup)
            driver.find_element(By.XPATH, "//option[@value='{}']".format(fiscais)).click()
            driver.find_element(By.NAME, "novaDataRoteiro").clear()
            driver.find_element(By.NAME, "novaDataRoteiro").send_keys(new_day)
            driver.find_element(By.XPATH, "//input[@value='Reprogramar']").click()
            driver.switch_to.window(janela_principal)
        except:
            pass