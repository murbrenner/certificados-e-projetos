import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from arquivos import elaboration
from login import murilo, driver

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    #PREENCHER TUDO
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    original_window = driver.current_window_handle
    driver.find_element(By.ID, '1').click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    time.sleep(0.5)
    try:
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[4]/td/a/strong").click()
        time.sleep(0.5)
        driver.find_element(By.ID, '2').click()
        try:
            driver.find_element(By.NAME, "confirmar").click()
        except:
            pass
        driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[5]/tbody/tr[2]/td/div/table/tbody/tr/td[2]/a").click()
        time.sleep(0.5)
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                try:
                    driver.find_element(By.NAME, "bairro").send_keys("DIVINEIA")
                    driver.find_element(By.CLASS_NAME, "bottonRightCol").click()
                    driver.switch_to.window(original_window)
                except:
                    try:
                        driver.find_element(By.NAME, "botaoFechar").click()
                    except:
                        break

        driver.switch_to.window(original_window)
        driver.find_element(By.NAME, "concluir").click()
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
        print(str(df['MATRICULA'][i]), end=',')
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
        driver.find_element(By.ID, '1').click()
        driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        endereco = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/div").text
        print(endereco)
    except:
        break