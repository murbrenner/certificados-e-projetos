import time, os, glob, subprocess
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import listagem, down_path

df = pd.read_csv(listagem)
login()

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelOutrosCriteriosConsumidoresInscricao.do?menu=sim&gerarRelatorio=RelatorioCadastroConsumidoresInscricao")

for i in df.index:
    driver.find_element(By.NAME, 'localidadeOrigemID').clear()
    driver.find_element(By.NAME, 'localidadeOrigemID').send_keys(str(df['LOCAL'][i]))
    driver.find_element(By.NAME, 'setorComercialOrigemCD').clear()
    driver.find_element(By.NAME, 'setorComercialOrigemCD').send_keys(str(df['GRUPO'][i]))
    driver.find_element(By.NAME, 'cdRotaInicial').clear()
    driver.find_element(By.NAME, 'cdRotaInicial').send_keys(str(df['ROTA'][i]))
    msg_ero = driver.find_element(By.NAME, "descRotaInicial").get_attribute('value')
    driver.find_element(By.NAME, 'ordenacaoRelatorio').send_keys('ROTA')
    driver.find_element(By.NAME, 'concluir').click()
    driver.find_element(By.XPATH, "//input[@value='Gerar']").click()
    try:
        batch_ero = driver.find_element(By.XPATH, "/html/body/div[1]/form/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(str(df['GRUPO'][i]), "/", str(df['ROTA'][i]), " - ", msg_ero.capitalize(), ".", sep='')
    except:
        pass
        msg_ok = driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span').text
        print(str(df['GRUPO'][i]), "/", str(df['ROTA'][i]), " - ", msg_ok, sep='')

        time.sleep(2)
        caminho_pasta_downloads = down_path
        arquivos_pdf = glob.glob(os.path.join(caminho_pasta_downloads, '*.pdf'))
        arquivos_pdf = sorted(arquivos_pdf, key=os.path.getmtime, reverse=True)

        if arquivos_pdf:
            subprocess.run(['start', '', arquivos_pdf[0]], shell=True)
        else:
            print('Nenhum arquivo PDF encontrado na pasta de downloads.')

    driver.find_element(By.LINK_TEXT, "Novo Relatório").click()
# MATRICULA,LOCAL,SETOR,QUADRA,LOTE,SUBLOTE,TESTADA,SEQUENCIA,COD_LOG,ENDERECO,BAIRRO,NUMERO,COMPLEMENTO,RES,COM,PUB,SITUACAO AGUA,AREA,TIPO_HAB,NOME,CPF,EMAIL,ID_CLIENTE,SEXO,DDD,TELEFONE a;b  c