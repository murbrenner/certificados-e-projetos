import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration, teste

df = pd.read_csv(elaboration)
murilo()

cabeçalho = ['MATRICULA', 'FISCAL', 'CARGO', 'LOTACAO']
with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for i in df.index:
        driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim')
        driver.find_element(By.XPATH, "//*[@title='Pesquisar Usuário']").click()
        j_zero = driver.window_handles[0]
        janela_pesq = driver.window_handles[1]
        driver.switch_to.window(janela_pesq)
        driver.find_element(By.XPATH, "//*[@title='Pesquisar Funcionário']").click()
        driver.find_element(By.NAME, "id").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
        try:
            mat = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[4]/td/table/tbody/tr/td[1]").text.replace(' ', '')
            nome_fisc = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[4]/td/table/tbody/tr/td[2]").text
            cargo = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[4]/td/table/tbody/tr/td[3]").text.replace(' ', '')
            lotacao = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[4]/td/table/tbody/tr/td[4]").text
            linha = (mat, nome_fisc, cargo, lotacao)
            escritor.writerow(linha)
        except:
            linha_err = (mat, "NAO LOCALIZADO", "NAO LOCALIZADO", "NAO LOCALIZADO")
            escritor.writerow(linha_err)
            pass
        driver.close()
        driver.switch_to.window(j_zero)
