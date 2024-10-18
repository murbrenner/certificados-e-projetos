from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    original_window = driver.current_window_handle
    driver.find_element(By.ID, '1').click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    driver.find_element(By.LINK_TEXT, "Manter Imóvel").click()
    driver.find_element(By.ID, '2').click()
    try:
        driver.find_element(By.NAME, "confirmar").click()
    except:
        pass
    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[5]/tbody/tr[2]/td/div/table/tbody/tr/td[2]/a").click()

    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]), Keys.ENTER)
            driver.find_element(By.NAME, "complemento").clear()
            driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]), Keys.ENTER)
            driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()
            driver.switch_to.window(original_window)
            driver.find_element(By.ID, "botaoConcluir").click()

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, '1').click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    endereco = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[2]/tbody/tr[2]/td/table/tbody/tr[2]/td/div").text
    print(str(df['MATRICULA'][i]), "Endereço atualizado:", endereco)
