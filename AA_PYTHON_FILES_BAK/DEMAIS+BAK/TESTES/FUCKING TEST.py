import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from login import driver, murilo
from arquivos import elaboration
import pandas as pd

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, "idImovelDebitos").send_keys('671', Keys.ENTER)#.send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    j = 1
    while j < 100:
        try:
            driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[1]/div/font/a".format(j)).click()
            time.sleep(1)
            main_window_handle = driver.current_window_handle
            all_window_handles = driver.window_handles
            for handle in all_window_handles:
                if handle != main_window_handle:
                    driver.switch_to.window(handle)
                    try:
                        motivorevisao1 = driver.find_element(By.XPATH, "//input=[@name='contaMotivoRevisao']").get_attribute('value')
                        print(str(df['MATRICULA'][i]), "Não está em revisão")
                    except:
                        motivorevisao2 = driver.find_element(By.XPATH, "//input[@name='contaMotivoRevisao.descricaoMotivoRevisaoConta']").get_attribute(
                            'value')
                        print(str(df['MATRICULA'][i]), motivorevisao2)
                    driver.close()
                    driver.switch_to.window(main_window_handle)


        except:
            pass
        j += 1

