from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import teste

df = pd.read_csv(teste)
murilo()


for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    agua = driver.find_element(By.NAME, "situacaoAguaDadosCadastrais").get_attribute('value')
    print(i+1, str(df['MATRICULA'][i]), agua)