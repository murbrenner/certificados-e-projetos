from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import abrir_ra, teste
from login import murilo, driver, login


df = pd.read_csv(abrir_ra)
murilo()

for i in df.index:
    num_hd = str(df['HIDROMETRO'][i])
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirConsultarHistoricoInstalacaoHidrometroInformarAction.do?menu=sim")
    driver.find_element(By.NAME, "codigoHidrometro").send_keys(num_hd, Keys.ENTER)
    sit_hd = driver.find_element(By.NAME, "descricaoHidrometro").get_attribute('value')
    if sit_hd != "Hidrômetro Inexistente":
        driver.find_element(By.XPATH, f"//*[@value='Consultar']").click()
        hd_ok = driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[1]/td/table/tbody/tr[3]/td[8]/div").text
        print(i+1, "SITUACAO HD {}: {} ".format(num_hd, hd_ok))
    elif sit_hd == "Hidrômetro Inexistente":
        print(i+1, "SITUACAO HD {}: {} ".format(num_hd, sit_hd))