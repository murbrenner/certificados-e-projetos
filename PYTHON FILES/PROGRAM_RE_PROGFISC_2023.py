from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import pandas as pd
from db_login import login, driver
from db_arquivos import prog_fisc, teste, elaboration
from db_fiscais import fiscais, nomes_sep_join, name_to_value, abrev_nomes_joined
import time

df = pd.read_csv(teste)
login()

today = datetime.today()
tomorrow = datetime.today() + timedelta(days=1)
segunda = datetime.today() + timedelta(days=3)
data_prog = tomorrow
data_prog = data_prog.strftime("%d/%m/%Y")

for i in df.index: #COMANDO 'FOR' PARA INICIAR O LOOP
    try:
        driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim')
        driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        driver.find_element(By.LINK_TEXT, "Dados da Programação").click()
        data = driver.find_element(By.NAME, "dataProgramacao").get_attribute('value')
        fiscal = driver.find_element(By.NAME, "equipeProgramacao").get_attribute('value')
        fiscal2 = name_to_value['{}'.format(fiscal)]
        fiscal3 = nomes_sep_join['{}'.format(fiscal)]
        fiscal4 = str(df['FISCAL'][i])
        fiscal5 = abrev_nomes_joined['{}'.format(fiscal4)]
        sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        time.sleep(0.2)
        if sit_os == "Pendente":
            new_day = data_prog.replace('/', '')
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(data))
            driver.find_element(By.PARTIAL_LINK_TEXT, fiscal).click()
            time.sleep(0.2)
            driver.find_element(By.XPATH, "//input[@value='{}___{}']".format(str(df['OS'][i]), fiscal3)).click()
            time.sleep(0.2)
            driver.find_element(By.NAME, "ButtonReprogramarOS").click()
            time.sleep(0.2)
            janela1 = driver.window_handles[0]
            popup = driver.window_handles[1]
            driver.switch_to.window(popup)
            time.sleep(0.2)
            driver.find_element(By.NAME, "equipe").send_keys(fiscais)
            driver.find_element(By.NAME, "novaDataRoteiro").clear()
            driver.find_element(By.NAME, "novaDataRoteiro").send_keys(new_day)            
            time.sleep(0.2)
            driver.find_element(By.XPATH, "//input[@value='Reprogramar']").click()
            driver.switch_to.window(janela1)
            
            print(i + 1, "ORDEM DE SERVIÇO {} [REPROGRAMADA] COM SUCESSO PARA O FISCAL [{}] PRO DIA [{}]!".format(str(df['OS'][i]), fiscal5, data_prog))
        elif sit_os == 'Encerrada':
            msg_ero = driver.find_element(By.XPATH, "/html/body/div[1]/form/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(i+1, "ORDEM DE SERVIÇO {} [ENCERRADA!]".format(str(df['OS'][i])), msg_ero)
    except:
        print(i+1, "ORDEM DE SERVIÇO {} [NÃO REPROGRAMADA!]".format(str(df['OS'][i])))        
        pass
    