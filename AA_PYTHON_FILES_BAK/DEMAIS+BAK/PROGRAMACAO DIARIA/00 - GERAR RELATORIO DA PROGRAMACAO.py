from selenium.webdriver.common.by import By
import pandas as pd
from arquivos import relatorio_prog, elab_date, teste
from login import murilo, driver
from datetime import date
import csv
import LOCALIZACAO as local

df = pd.read_csv(relatorio_prog)
df2 = pd.read_csv(elab_date)
murilo()

cabeçalho = ['#', 'FISCAL', 'RA', 'OS', 'TIPO SERVICO', 'DATA', 'STATUS SERV', 'STATUS GSAN']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)

    for d in df2.index:
        today = str(df2['DATA'][d])
        for f in df.index:
            try:
                driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
                driver.find_element(By.XPATH, "//*[@id='layerHide{}']/table/tbody/tr/td[1]/table/tbody/tr/td[2]/a/b".format(str(df['FISCAL'][f]))).click()
            except:
                try:
                    no_prog = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                    print(no_prog)
                    break
                except:
                    pass
            n = 3
            try:
                while n < 100:
                    reg_atend = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[7]/div/a".format(str(df['FISCAL'][f]), n)).text
                    ord_serv = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[8]/div/a".format(str(df['FISCAL'][f]), n)).text
                    tipo_serv = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[9]/div".format(str(df['FISCAL'][f]), n)).text
                    status_serv = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[6]/div".format(str(df['FISCAL'][f]), n)).text
                    if tipo_serv == '613':
                        tipo_serv = 'LEV. DADOS'
                    elif tipo_serv == '890':
                        tipo_serv = 'LEV. DADOS'
                    elif tipo_serv == '9125':
                        tipo_serv = 'CAD. IMOVEL'
                    if tipo_serv == '603':
                        tipo_serv = 'VERIF. COND. FIS. HD'
                    if status_serv == 'Pen':
                        status_serv = 'EM CAMPO'
                        status_gsan = 'PENDENTE'
                    elif status_serv == 'Enc':
                        status_serv = 'DEVOLVIDA'
                        status_gsan = 'ENCERRADA'
                    count = n - 2
                    linha = count, str(df['FISCAL'][f]), reg_atend, ord_serv, tipo_serv, today, status_serv, status_gsan
                    n = n + 1
                    escritor.writerow(linha)
            except:
                pass

local