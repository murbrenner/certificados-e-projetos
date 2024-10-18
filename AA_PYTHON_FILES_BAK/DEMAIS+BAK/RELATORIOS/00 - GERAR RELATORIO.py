import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import listagem

df = pd.read_csv(listagem)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelOutrosCriteriosConsumidoresInscricao.do?menu=sim&gerarRelatorio=RelatorioCadastroConsumidoresInscricao")
    driver.find_element(By.NAME, 'localidadeOrigemID').send_keys(str(df['LOCAL'][i]), Keys.ENTER)
    driver.find_element(By.NAME, 'setorComercialOrigemCD').send_keys(str(df['GRUPO'][i]), Keys.ENTER)
    driver.find_element(By.NAME, 'cdRotaInicial').send_keys(str(df['ROTA'][i]), Keys.ENTER)
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

        time.sleep(1)
        caminho_pasta_downloads = 'C:/Users/Murilo/Downloads'
        arquivos_pdf = glob.glob(os.path.join(caminho_pasta_downloads, '*.pdf'))
        arquivos_pdf = sorted(arquivos_pdf, key=os.path.getmtime, reverse=True)
        if arquivos_pdf:
            subprocess.run(['start', '', arquivos_pdf[0]], shell=True)
        else:
            print('Nenhum arquivo PDF encontrado na pasta de downloads.')