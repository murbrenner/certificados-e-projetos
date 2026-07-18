import time
import csv
import pandas as pd
from db_login_playwright import inicializar_browser, login, fechar_browser, page as driver_page
from db_arquivos import *

relatorioGsan = relatorioGsan1

df = pd.read_csv(databaseCSV1)

# Inicializar browser e fazer login
page = inicializar_browser()
login()

header = ['MATRICULA', 'COORD. X', 'COORD. Y']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df.index:
        matricula = str(df['MATRICULA'][i])
        if matricula != "0":
            page.goto("http://gsan.caema.ma.gov.br:8080/gsan/exibirConsultarImovelAction.do?menu=sim")            
            page.locator('[id="1"]').click()
            matricula = str(df['MATRICULA'][i])
            page.locator('[name="idImovelDadosCadastrais"]').fill(matricula)
            page.locator('[name="idImovelDadosCadastrais"]').press("Enter")
            codif = page.locator('[name="matriculaImovelDadosCadastrais"]').input_value()
            coordx = page.locator('[name="coordenadaXDadosCadastrais"]').input_value()
            if coordx == '':
                coordx = '0'
            coordx = coordx.replace('.', ',')
            
            coordy = page.locator('[name="coordenadaYDadosCadastrais"]').input_value()
            if coordy == '':
                coordy = '0'
            coordy = coordy.replace('.', ',')
            
            linha = matricula, coordx, coordy
            writer.writerow(linha)
        elif matricula == "0":
            linha = '0', '0', '0'
            writer.writerow(linha)
            pass

# Fechar browser
fechar_browser()
