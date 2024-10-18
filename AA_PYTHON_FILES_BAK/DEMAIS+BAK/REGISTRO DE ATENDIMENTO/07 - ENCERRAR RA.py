from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, abrir_ra, teste

df = pd.read_csv(abrir_ra)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "Submit").click()
    sit_ra = driver.find_element(By.NAME, 'situacaoRA').get_attribute('value')
    if sit_ra == 'Pendente':
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('CONCLUSAO DO SERVICO')
        driver.find_element(By.NAME, "parecerEncerramento").send_keys(str(df['OBSERVACAO'][i]))#('SERVIÇO EXECUTADO')
        driver.find_element(By.NAME, "botaoConcluir").click()
        j = i + 1
        print(j, 'Registro de atendimento {} encerrado com sucesso!'.format(str(df['RA'][i])))
    elif sit_ra == 'Encerrado':
        j = i + 1
        print(j, 'Registro de atendimento {} já encerrado!'.format(str(df['RA'][i])))

