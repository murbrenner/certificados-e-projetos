from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, murilo2
from arquivos import desprog_fisc, elaboration, prog_fisc, teste

df = pd.read_csv(elaboration)
murilo2()

for i in df.index:
    try:
        driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim')
        num_os = str(df['OS'][i])
        driver.find_element(By.NAME, "numeroOS").send_keys(num_os, Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        if sit_os == 'Pendente':
            driver.find_element(By.LINK_TEXT, "Dados da Programação").click()
            data = driver.find_element(By.NAME, "dataProgramacao").get_attribute('value')
            fiscal = driver.find_element(By.NAME, "equipeProgramacao").get_attribute('value')
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(data))
            nome = str(fiscal).replace(" ", "")
            driver.find_element(By.PARTIAL_LINK_TEXT, fiscal).click()
            driver.find_element(By.XPATH, "//input[@value='{}___{}']".format(num_os, nome)).click()
            driver.find_element(By.NAME, "ButtonInformarSituacao").click()
            janela1 = driver.window_handles[0]
            popup = driver.window_handles[1]
            driver.switch_to.window(popup)
            driver.find_element(By.NAME, "situacaoOrdemServico").send_keys('PENDENTES')
            driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
            driver.switch_to.window(janela1)
            print(i + 1, "ORDEM DE SERVIÇO {} [DESPROGRAMADA] COM SUCESSO!".format(num_os))  
        elif sit_os == 'Encerrada':
            print(i+1, "ORDEM DE SERVIÇO {} [JA ENCERRADA!]".format(num_os))
            pass
    except:
        print(i+1, "ORDEM DE SERVIÇO {} [NÃO PROGRAMADA!]".format(num_os))
        pass