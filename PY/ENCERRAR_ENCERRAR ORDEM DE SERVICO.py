from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from db_arquivos import elaboration, abrir_ra
from db_login import login, driver

df = pd.read_csv(abrir_ra)
login()

hoje = date.today()
hoje = hoje.strftime("%d/%m/%Y")
motivo = "CONCLUSAO DO SERVIÇO"

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    status_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    if status_os != 'Encerrada':    
        driver.find_element(By.XPATH, "//input[@value='Encerrar']").click()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
        driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
        driver.find_element(By.NAME, "observacaoEncerramento").send_keys('CORRECAO DOS HIDROMETROS INSTALADOS.')#(str(df['PARECER'][i]))
        driver.find_element(By.NAME, "ButtonAtividade").click()
        popup = driver.window_handles[1]
        janela = driver.window_handles[0]
        driver.switch_to.window(popup)
        driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr/td/table[3]/tbody/tr[9]/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[4]/a/img').click()
        time.sleep(0.3)
        driver.find_element(By.NAME, 'horaInicioExecucao').send_keys("0800")
        driver.find_element(By.NAME, 'horaFimExecucao').send_keys("1800")
        driver.find_element(By.NAME, "idEquipeNaoProgramada").send_keys("CAEMA-CADASTRO SEDE")
        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
        driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
        driver.switch_to.window(janela)    
        driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[1]/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[10]/td[2]/input[1]").click()
        driver.find_element(By.NAME, "ButtonEncerrar").click()    
        try:
            driver.find_element(By.XPATH, "//input[@value='Cancelar']").click()
            driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
            driver.find_element(By.XPATH, "//input[@value='ButtonCancelar']").click()
            driver.find_element(By.XPATH, "//input[@value='ButtonVoltar']").click()
        except:
            pass