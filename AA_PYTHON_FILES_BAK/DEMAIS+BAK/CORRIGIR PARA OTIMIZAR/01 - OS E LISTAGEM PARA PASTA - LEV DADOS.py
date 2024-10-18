import datetime
import csv
import shutil
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

today = datetime.date.today()
dia = today.day

for i in df.index:
    # driver.get(
    #     "http://gsan.caema.ma.gov.br:8080/gsan/exibirCalendarioElaboracaoAcompanhamentoRoteiroActionElaborar.do?elaboracao=true&menu=sim")
    # driver.find_element(By.PARTIAL_LINK_TEXT, "{}".format(dia)).click()
    # driver.find_element(By.XPATH, "//option[@value='890']").click()
    # driver.find_element(By.XPATH, "//option[@value='613']").click()
    # driver.find_element(By.XPATH,"//input[@value='  >  ']").click()
    # driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()

    # CRIA A PASTA DE DESTINO PARA O ARQUIVO BASEADA NO NUMERO INSERIDO NA COLUNA -RA- DA PLANILHA CSV
    caminho = r"C:\Users\Murilo\Desktop\LEVANTAMENTOS DE DADOS\{}".format(str(df['OS'][i]))
    if not os.path.exists(caminho):
        os.makedirs(caminho)

    # DIZ QUAL É A PASTA DE ORIGEM PRA ELE PEGAR OS ARQUIVOS
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    # SETA A PASTA DE DESTINO PARA A COPIA DO ARQUIVO
    destination_path = caminho

    errea = (str(df['RA'][i]))
    # try:
    #     driver.find_element(By.PARTIAL_LINK_TEXT, "{}".format(errea))
    # except:
    #     pass
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys("{}".format(errea), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.XPATH, "//*[@id='layerHideLocal']/table/tbody/tr/td/span/a/b").click()
    inscricaosearch = driver.find_element(By.NAME, "inscricaoImovel").get_attribute('value')
    localidade = driver.find_element(By.NAME, "idLocalidade").get_attribute('value')
    setor = driver.find_element(By.NAME, "idSetorComercial").get_attribute('value')
    rota = driver.find_element(By.NAME, "rota").get_attribute('value')

    osdoc = (str(df['OS'][i]))
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroOS").send_keys("{}".format(osdoc), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.NAME, "btnImprimir").click()
    j = i + 1
    print(j, errea, osdoc)
    time.sleep(1)

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\O.S.PDF")

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    shutil.move("C:\\Users\\Murilo\\Downloads\\O.S.PDF", destination_path)

    driver.get(
        "http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelOutrosCriteriosConsumidoresInscricao.do?menu=sim&gerarRelatorio=RelatorioCadastroConsumidoresInscricao&limpar=S")
    driver.find_element(By.NAME, "localidadeOrigemID").send_keys((localidade), Keys.ENTER)
    driver.find_element(By.NAME, "setorComercialOrigemCD").send_keys((setor), Keys.ENTER)
    driver.find_element(By.NAME, "cdRotaInicial").send_keys((rota), Keys.ENTER)
    driver.find_element(By.XPATH, "//option[@value='rota']").click()
    driver.find_element(By.NAME, "concluir").click()
    driver.find_element(By.NAME, "botao").click()
    time.sleep(1)

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\LISTAGEM.PDF")

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    shutil.move("C:\\Users\\Murilo\\Downloads\\LISTAGEM.PDF", destination_path)

    txtfile = "C:\\Users\\Murilo\\Downloads\\{}.txt".format(inscricaosearch)
    with open(txtfile, 'w') as file:
        file.write(inscricaosearch)
        file.close()
        shutil.move(txtfile, destination_path)

    file_path = "C:\\Users\\Murilo\\Downloads\\FIND.csv".format(inscricaosearch)
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['INSCRICAO', 'LOCALIDADE', 'SETOR', 'ROTA',])
        writer.writerow([inscricaosearch, localidade, setor, rota])
        csv_file.close()

        shutil.move(file_path, destination_path)
