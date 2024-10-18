from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, inserir_imovel

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, "matriculaFiltro").send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.NAME, "idLocalidade").clear()
    driver.find_element(By.NAME, "idLocalidade").send_keys(str(df['LOCALIDADE'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "idSetorComercial").clear()
    driver.find_element(By.NAME, "idSetorComercial").send_keys(str(df['SETOR'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "idQuadra").clear()
    driver.find_element(By.NAME, "idQuadra").send_keys(str(df['QUADRA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "lote").clear()
    driver.find_element(By.NAME, "lote").send_keys(str(df['LOTE'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "subLote").clear()
    driver.find_element(By.NAME, "subLote").send_keys(str(df['SUBLOTE'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "testadaLote").clear()
    driver.find_element(By.NAME, "testadaLote").send_keys('5')#(str(df['TESTADA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "sequencialRota").clear()
    driver.find_element(By.NAME, "sequencialRota").send_keys(str(df['SEQUENCIA'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, f"//*[@value='Concluir']").click()
    try:
        driver.find_element(By.XPATH, f"//*[@value='Confirmar']").click()
        j = i + 1
        print(j, "Codificação da matrícula {} alterada com sucesso!".format(str(df['MATRICULA'][i])))
    except:
        j = i + 1
        print(j, "Matricula {} não atualizada. Conflito de sequência.".format(str(df['MATRICULA'][i])))
        pass