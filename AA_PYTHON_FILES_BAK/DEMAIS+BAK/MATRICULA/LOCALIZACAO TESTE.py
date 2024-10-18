import time
import pandas as pd
from login import murilo, driver
from arquivos import teste, elaboration
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    mat = str(df['MATRICULA'][i])
    codif = driver.find_element(By.NAME, "matriculaImovelDadosCadastrais").get_attribute('value')
    cx = driver.find_element(By.NAME, "coordenadaXDadosCadastrais").get_attribute('value')
    cy = driver.find_element(By.NAME, "coordenadaYDadosCadastrais").get_attribute('value')
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("http://maps.google.com.br/maps?q={},{}&hl=pt-BR&t=h&z=16".format(cx, cy))
    link_geo = "http://maps.google.com.br/maps?q={},{}&hl=pt-BR&t=h&z=16".format(cx, cy)
    print(mat, codif, link_geo)
    time.sleep(5)
    driver.execute_script("window.close('');")
    driver.switch_to.window(driver.window_handles[0])