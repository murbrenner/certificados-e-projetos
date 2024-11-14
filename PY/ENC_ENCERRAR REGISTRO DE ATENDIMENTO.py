from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, abrir_ra, teste

df = pd.read_csv(elaboration)
login()

for i in df.index:
    num_ra = str(df['RA'][i])
    observacao = str(df['OBSERVACAO'][i])
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(num_ra, Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    sit_ra = driver.find_element(By.NAME, 'situacaoRA').get_attribute('value')
    if sit_ra == 'Pendente':
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        try:
            driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('INDEFERIDO')#INDEFERIDO
            driver.find_element(By.NAME, "parecerEncerramento").send_keys(observacao)#CANCELAMENTO PELA CAEMA
        except:
            pass
            #driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('DEFERIDO')
            #driver.find_element(By.NAME, "parecerEncerramento").send_keys('IMOVEL ESTA DENTRO DA PROGRAMACAO DE ATUALIZACAO DE ROTAS DO CADASTRO COMERCIAL')
        driver.find_element(By.NAME, "botaoConcluir").click()
        j = i + 1
        print(j, 'Registro de atendimento {} encerrado com sucesso!'.format(num_ra))
    elif sit_ra == 'Encerrado':
        j = i + 1
        print(j, 'Registro de atendimento {} já encerrado!'.format(num_ra))
        pass