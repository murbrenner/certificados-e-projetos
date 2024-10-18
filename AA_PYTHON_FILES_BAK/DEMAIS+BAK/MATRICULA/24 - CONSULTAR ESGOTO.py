from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "3").click()
    driver.find_element(By.NAME, "idImovelAnaliseMedicaoConsumo").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    esgoto = str(driver.find_element(By.NAME, "situacaoEsgotoAnaliseMedicaoConsumo").get_attribute('value'))
    perfil_esg = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[6]/td/table/tbody/tr[5]/td[3]").text
    print(str(df['MATRICULA'][i]), esgoto, perfil_esg)
