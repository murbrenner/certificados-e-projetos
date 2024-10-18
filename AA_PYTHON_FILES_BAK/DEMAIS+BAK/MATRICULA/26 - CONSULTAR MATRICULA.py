from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    mat = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
    print(i+1, mat, str(df['OS'][i]))