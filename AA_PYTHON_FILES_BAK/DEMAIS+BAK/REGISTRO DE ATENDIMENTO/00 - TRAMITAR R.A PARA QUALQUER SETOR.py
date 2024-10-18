from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import tramite

df = pd.read_csv(tramite)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, 'numeroRA').send_keys(str(df['RA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    tramite_ok = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
    if tramite_ok == 'Pendente':
        driver.find_element(By.XPATH, "//input[@value='Tramitar']").click()
        driver.find_element(By.NAME, "unidadeDestinoId").send_keys(str(df['CODIGO'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Tramitar']").click()
        try:
            msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
            j = i + 1
            print(j, msg_ok, "Código {}.".format(str(df['CODIGO'][i])))
        except:
            msg_ero = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            j = i + 1
            print(j, (df['RA'][i]), msg_ero, "Código {}.".format(str(df['CODIGO'][i])))
    elif tramite_ok == 'Encerrado':
        msg_enc = "O R.A. {} encontra-se encerrado. Não foi possível tramitar para o codigo {}".format(str(df['RA'][i]), str(df['CODIGO'][i]))
        j = i + 1
        print(j, msg_enc, "Código {}.".format(str(df['CODIGO'][i])))