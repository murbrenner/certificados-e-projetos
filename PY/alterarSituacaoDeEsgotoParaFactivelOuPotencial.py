from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *

df = pd.read_csv(databaseCSV1)
login()

situacao = 'POTENCIAL'

for i in df.index:
    url = ("http://gsan.caema.ma.gov.br:8080/gsan/exibirAlterarSituacaoLigacaoAction.do?menu=sim")
    driver.get(url)
    driver.find_element(By.NAME, "idOrdemServico").send_keys(str(df['OS'][i]), Keys.ENTER)
    try:
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/strong[2]/input[2]").click()
        driver.find_element(By.NAME, "situacaoLigacaoEsgotoNova").send_keys(situacao)
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[5]/td/table/tbody/tr/td[2]/input").click()
        print(i+1, str(df['MATRICULA'][i]), 'Alterado.', sep=';')
        alt = 1
    except:
        print(i+1, str(df['MATRICULA'][i]), 'Inalterado.', sep=';')
        alt = 0

    if alt == 1:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
        driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        sit_ra = driver.find_element(By.NAME, 'situacaoRA').get_attribute('value')
        if sit_ra == 'Pendente':
            driver.find_element(By.NAME, "ButtonEncerrar").click()
            try:
                driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('CONCLUSAO DO SERVICO')#INDEFERIDO
                driver.find_element(By.NAME, "parecerEncerramento").send_keys(str(df['OBSERVACAO'][i]))
            except:
                pass
                #driver.find_element(By.NAME, "motivoEncerramentoId").send_keys('DEFERIDO')
                #driver.find_element(By.NAME, "parecerEncerramento").send_keys('IMOVEL ESTA DENTRO DA PROGRAMACAO DE ATUALIZACAO DE ROTAS DO CADASTRO COMERCIAL')
            driver.find_element(By.NAME, "botaoConcluir").click()
            j = i + 1
            print('Registro de atendimento {} encerrado com sucesso!'.format(str(df['RA'][i])))
        elif sit_ra == 'Encerrado':
            j = i + 1
            print('Registro de atendimento {} já encerrado!'.format(str(df['RA'][i])))
            pass
    elif alt == 0:
        print('Registro de atendimento {} não foi encerrado!!!'.format(str(df['RA'][i])))
        pass