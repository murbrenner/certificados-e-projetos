import csv
from selenium.webdriver.common.by import By
import pandas as pd
from login import driver, murilo, murilo2
from arquivos import elaboration, teste

df = pd.read_csv(elaboration)
murilo2()

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, 'numeroOS').send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

cabeçalho = ['#', 'SITUACAO', 'OS', 'USER_ENC', 'DATA_ENC1', 'HORA_ENC1', 'DATA_ENC2', 'HORA_ENC2']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        num_os = str(df['OS'][i])
        if num_os != "0":
            driver.find_element(By.NAME, 'numeroOSParametro').send_keys(str(df['OS'][i]))
            driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
            situacao = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        if situacao == "Encerrada":
            driver.find_element(By.LINK_TEXT, "Dados do Encerramento da Ordem de Serviço").click()
            user_enc = driver.find_element(By.NAME, "usuarioEncerramentoNome").get_attribute('value')
            data_ini_enc = driver.find_element(By.NAME, "dataEncerramento").get_attribute('value')
            data_ini_ok = data_ini_enc[:10]
            hora_ini = data_ini_enc[11:]
            data_end_enc = driver.find_element(By.NAME, "unidadeEncerramentoDtUltimaAlteracao").get_attribute('value')
            data_end_ok = data_end_enc[:10]
            hora_end = data_end_enc[11:]
            linha = (i + 1, situacao, num_os, user_enc, data_ini_ok, hora_ini, data_end_ok, hora_end)
            escritor.writerow(linha)
        elif situacao == "Pendente":
            linha = (i + 1, situacao, num_os, "-", "-", "-", "-", "-")
            escritor.writerow(linha)
        elif num_os == '0':
            linha = (i + 1, "-", "-", "-", "-", "-", "-", "-")
            escritor.writerow(linha)
            pass
