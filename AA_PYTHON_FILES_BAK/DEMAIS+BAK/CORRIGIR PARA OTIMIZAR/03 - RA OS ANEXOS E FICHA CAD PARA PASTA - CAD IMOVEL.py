from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import shutil
from arquivos import elaboration
from login import murilo, driver

df = pd.read_csv(elaboration)
murilo()

for i in df.index:

    # CRIA A PASTA DE DESTINO PARA O ARQUIVO BASEADA NO NUMERO INSERIDO NA COLUNA -RA- DA PLANILHA CSV
    caminho = r"C:\Users\Murilo\Desktop\CADASTRAMENTO DE IMOVEL\{}".format(str(df['RA'][i]))
    if not os.path.exists(caminho):
        os.makedirs(caminho)

    # DIZ QUAL É A PASTA DE ORIGEM PRA ELE PEGAR OS ARQUIVOS
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    # SETA A PASTA DE DESTINO PARA A COPIA DO ARQUIVO
    destination_path = caminho

    osdoc = (str(df['OS'][i]))
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroOS").send_keys("{}".format(osdoc), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.XPATH, "//input[@value='Imprimir']").click()
    print(osdoc)
    time.sleep(1)

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\O.S.PDF")
    latest_file = "C:\\Users\\Murilo\\Downloads\\O.S.PDF"

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    shutil.move(latest_file, destination_path)

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "Submit").click()
    print((str(df['RA'][i])))

    #DEPOIS DE ABRIR A R.A ELE CLICA NA GUI ANEXOS E DESCANSA POR 1 SEGUNDO PRA PODER DAR TEMPO DO GSAN ABRIR
    driver.find_element(By.PARTIAL_LINK_TEXT, 'Anexos').click()
    time.sleep(1)
    numero = 1
    contador = 0

    # DIZ QUAL É A PASTA DE ORIGEM PRA ELE PEGAR OS ARQUIVOS
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    # SETA A PASTA DE DESTINO PARA A COPIA DO ARQUIVO
    destination_path = caminho

    #CLICA EM IMPRIMIR PARA IMPRIMIR A R.A E COPIA PARA A PASTA COM O NUMERO DA R.A
    driver.find_element(By.NAME, "ButtonImprimir").click()
    driver.find_element(By.NAME, "botao").click()
    time.sleep(1)

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\R.A.PDF")
    latest_file = "C:\\Users\\Murilo\\Downloads\\R.A.PDF"

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    shutil.move(latest_file, destination_path)

    fichacad = "C:\\Users\\Murilo\\Desktop\\UTEIS\\FICHA CADASTRAL - REV.6.pdf"
    shutil.copy(fichacad, destination_path)

    #COMEÇA A BAIXAR ATÉ 10 ANEXOS
    while numero <= 10:
        try:
            anexo = driver.find_element(By.CSS_SELECTOR, '#layerShowAnexos > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td > div > table > tbody > tr:nth-child({}) > td:nth-child(1) > a > img'.format(numero))
            anexo.click()
            time.sleep(1)
            numero += 1
            contador += 1
            print("ANEXO {} BAIXADO".format(contador), end=' ')

            # PEGA O ARQUIVO MAIS RECENTE
            list_of_files = os.listdir(downloads_path)
            full_path = [os.path.join(downloads_path, file) for file in list_of_files]
            latest_file = max(full_path, key=os.path.getmtime)

            # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
            shutil.copy(latest_file, destination_path)

            print("E COPIADO")

        except NoSuchElementException:
            break