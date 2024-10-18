import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import listagem, down_path

df = pd.read_csv(listagem)
login()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelOutrosCriteriosConsumidoresInscricao.do?menu=sim&gerarRelatorio=RelatorioCadastroConsumidoresInscricao")
    driver.find_element(By.NAME, 'localidadeOrigemID').send_keys(str(df['LOCAL'][i]))
    driver.find_element(By.NAME, 'setorComercialOrigemCD').send_keys(str(df['GRUPO'][i]))
    driver.find_element(By.NAME, 'cdRotaInicial').send_keys(str(df['ROTA'][i]))
    msg_ero = driver.find_element(By.NAME, "descRotaInicial").get_attribute('value')
    driver.find_element(By.NAME, 'ordenacaoRelatorio').send_keys('R')
    driver.find_element(By.NAME, 'concluir').click()
    csv_file = driver.find_element(By.NAME, 'escolhaTipoRelatorio')
    # if csv_file.get_attribute('value') == '6':
    #     csv_file.click()
    driver.find_element(By.XPATH, "//*[@id='demodiv']/table/tbody/tr[4]/td/span/input").click()#"//input[@value='6']").click()
    driver.find_element(By.XPATH, "//input[@value='Gerar']").click()
    try:
        batch_ero = driver.find_element(By.XPATH, "/html/body/div[1]/form/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(str(df['SETOR'][i]), "/", str(df['ROTA'][i]), " - ", msg_ero.capitalize(), ".", sep='')
        print(str(df['SETOR'][i]), "/", str(df['ROTA'][i]), " - ", batch_ero)
    except:
        try:
            batch_ero2 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print(str(df['GRUPO'][i]), "/", str(df['ROTA'][i]), " - ", batch_ero2)
        except:
            pass
            msg_ok = driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span').text
            print(str(df['GRUPO'][i]), "/", str(df['ROTA'][i]), " - ", msg_ok, sep='')
            pass

        time.sleep(2)

        caminho_pasta_downloads = down_path
        arquivos_csv = glob.glob(os.path.join(caminho_pasta_downloads, '*.csv'))
        arquivos_csv = sorted(arquivos_csv, key=os.path.getmtime, reverse=True)
        if arquivos_csv:
            subprocess.run(['start', '', arquivos_csv[0]], shell=True)
        else:
            print('Nenhum arquivo PDF encontrado na pasta de downloads.')