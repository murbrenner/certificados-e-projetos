from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")
    driver.find_element(By.ID, "1").click()
    driver.find_element(By.NAME, "idImovelDadosCadastrais").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
    driver.find_element(By.LINK_TEXT, "Manter Imóvel").click()
    driver.find_element(By.ID, "5").click()
    try:
        driver.find_element(By.NAME, "confirmar").click()
    except:
        pass
    driver.find_element(By.NAME, "perfilImovel").send_keys("01 - GRANDE") #(07 - CONTR. PREF; 01 - GRANDE; 05 - NORMAL)
    driver.find_element(By.NAME, "reservatorioInferior").clear()
    esgotamento = driver.find_element(By.NAME, "idLigacaoEsgotoEsgotamento").get_attribute('value')
    if str(esgotamento) == '':
        try:
            driver.find_element(By.NAME, "idLigacaoEsgotoEsgotamento").send_keys('NORMAL')
        except:
            pass
    else:
        pass
    fnt_abast = driver.find_element(By.NAME, "fonteAbastecimento").get_attribute('value')
    sit_lig_ag = driver.find_element(By.NAME, "situacaoLigacaoAgua").get_attribute('value')
    sit_lig_esg = driver.find_element(By.NAME, "situacaoLigacaoEsgoto").get_attribute('value')


    if fnt_abast == '-1':
        if sit_lig_ag == '2':
            driver.find_element(By.NAME, "fonteAbastecimento").send_keys('02 - PROPRIO')
        elif sit_lig_ag == '1':
            driver.find_element(By.NAME, "fonteAbastecimento").send_keys('02 - PROPRIO')
        elif sit_lig_ag == '3':
            driver.find_element(By.NAME, "fonteAbastecimento").send_keys('01 - CAEMA')
    if sit_lig_esg == '3':
            driver.find_element(By.NAME, "idLigacaoEsgotoEsgotamento").send_keys('NORMAL')



    driver.find_element(By.NAME, "concluir").click()
    try:
        driver.find_element(By.XPATH, "//input[@value='Não']").click()
    except:
        pass

    retorno = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    j = i + 1
    print(j, str(df['MATRICULA'][i]), retorno)

