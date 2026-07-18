from selenium.webdriver.common.by import By
from db_arquivos import *
from db_login import login, driver
import csv
from db_fiscais import num_nomes_joined, nomes_joined_corrigidos, nomes
from datetime import datetime, timedelta

today = datetime.today()
df = num_nomes_joined
login()

relatorioGsan = relatorioGsan1

header = ['FISCAL', 'RA', 'OS', 'TIPO SERVICO', 'DATA', 'STATUS SERV']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    escritor = csv.writer(relatorioGsan)
    escritor.writerow(header)

    # for d in df2.index:
    #     today = datetime.today()
    for f in df:
        try:
            today = datetime.today().strftime("%d/%m/%Y")
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
            driver.find_element(By.XPATH, "//*[@id='layerHide{}']/table/tbody/tr/td[1]/table/tbody/tr/td[2]/a/b".format(num_nomes_joined[f])).click()
        except:
            try:
                no_prog = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                print(no_prog)
                break
            except:
                pass
        n = 3
        try:
            while n < 30:
                reg_atend = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[7]/div/a".format(num_nomes_joined[f], n)).text
                ord_serv = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[8]/div/a".format(num_nomes_joined[f], n)).text
                tipo_serv = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[9]/div".format(num_nomes_joined[f], n)).text
                status_serv = driver.find_element(By.XPATH, "//*[@id='layerShow{}']/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[6]/div".format(num_nomes_joined[f], n)).text
                if tipo_serv == '613':
                    tipo_serv = 'LEVANTAMENTO DE DADOS PARA ATUALIZACAO CADASTRAL'
                elif tipo_serv == '890':
                    tipo_serv = 'LEVANT DE DADOS PARA ATUALIZ CADASTRAL'
                elif tipo_serv == '9125':
                    tipo_serv = 'CADASTRAMENTO DE IMOVEL'
                if tipo_serv == '603':
                    tipo_serv = 'VERIFICACAO DAS CONDICOES FISICAS DO HID'
                if status_serv == 'Pen':
                    status_serv = 'EM CAMPO'
                    status_gsan = 'PENDENTE'
                elif status_serv == 'Enc':
                    status_serv = 'DEVOLVIDA'
                    status_gsan = 'ENCERRADA'
                count = n - 2
                fisc_nome = num_nomes_joined[f]
                fiscal2 = nomes[fisc_nome]                
                linha = nomes[fisc_nome], reg_atend, ord_serv, tipo_serv, today, status_serv
                n = n + 1
                escritor.writerow(linha)
        except:
            pass