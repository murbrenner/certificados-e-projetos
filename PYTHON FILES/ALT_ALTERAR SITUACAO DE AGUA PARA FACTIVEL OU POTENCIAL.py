import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import teste, elaboration, abrir_ra

df = pd.read_csv(elaboration)
login()

nova_situacao = 'FACTIVEL'

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAlterarSituacaoLigacaoAction.do?menu=sim")
    driver.find_element(By.NAME, "idOrdemServico").send_keys(str(df['OS'][i]), Keys.ENTER)
    try:
        driver.find_element(By.XPATH, "//input[@value='1']").click()
        driver.find_element(By.NAME, "situacaoLigacaoAguaNova").send_keys(nova_situacao)
        driver.find_element(By.XPATH, "//input[@value='Alterar']").click()
        alt_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(i+1, "str(df['MATRICULA'][i])", alt_ok)
        ok = '1'
    except:
        nao_alt = driver.find_element(By.XPATH, '/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span').text
        print(i+1, "str(df['MATRICULA'][i])", nao_alt)
        ok = '0'

    time.sleep(1)

    if ok == '1':
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
        driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        sit_ra = driver.find_element(By.NAME, 'situacaoRA').get_attribute('value')
        if sit_ra == 'Pendente':
            driver.find_element(By.NAME, "ButtonEncerrar").click()
            time.sleep(0.3)
            driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('CONCLUSAO DO SERVICO')
            driver.find_element(By.NAME, "parecerEncerramento").send_keys('SITUAÇÃO DE ÁGUA ALTERADA PARA {}'.format(nova_situacao))
            driver.find_element(By.NAME, "botaoConcluir").click()
            j = i + 1
            print(j, 'Registro de atendimento {} encerrado com sucesso!'.format(str(df['RA'][i])))
        elif sit_ra == 'Encerrado':
            j = i + 1
            print(j, 'Registro de atendimento {} já encerrado!'.format(str(df['RA'][i])))
            pass
    elif ok == '0':
        print("R.A. [{}] não encerrado".format(str(df['RA'][i])))
