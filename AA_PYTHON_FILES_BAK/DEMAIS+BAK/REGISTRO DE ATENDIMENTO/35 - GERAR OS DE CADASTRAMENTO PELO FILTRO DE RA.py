from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver

df = pd.read_csv('C:\\Users\\Murilo\\Desktop\\PROJETOS PYTHON\\CSV FILES\\GERAR_CAD.csv')

murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, '//input[@value="Filtrar"]').click()
    driver.find_element(By.XPATH, "//input[@value='Gerar O.S']").click()
    driver.find_element(By.NAME, "idServicoTipo").send_keys("CAD")
    try:
        os_nao_gerada = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(os_nao_gerada)
    except:
        driver.find_element(By.XPATH, "//input[@value='Gerar']").click()
        os_gerada = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(os_gerada)