from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import shutil
from login import murilo, driver
from arquivos import elaboration

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    caminho = r"C:\Users\Murilo\Desktop\CADASTRAMENTO DE IMOVEL\{}".format(str(df['RA'][i]))
    if not os.path.exists(caminho):
        os.makedirs(caminho)

    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

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
    if os.path.exists(latest_file):
        os.replace(latest_file, latest_file)

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    shutil.move(latest_file, destination_path)
    if os.path.exists(destination_path):
        os.replace(destination_path, destination_path)

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
    if os.path.exists(destination_path):
        os.replace(destination_path, destination_path)

    fichacad = "C:\\Users\\Murilo\\Desktop\\UTEIS\\FICHA CADASTRAL - REV.6.pdf"
    shutil.copy(fichacad, destination_path)


    while numero <= 10:
        print(numero)
        anexo = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[7]/td/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr[{}]/td[1]/a/img'.format(numero))
        anexo.click()
        time.sleep(1)

        contador += 1
        try:
            print("ANEXO {} BAIXADO".format(contador), end=' ')

            # PEGA O ARQUIVO MAIS RECENTE
            list_of_files = os.listdir(downloads_path)
            full_path = [os.path.join(downloads_path, file) for file in list_of_files]
            latest_file = max(full_path, key=os.path.getmtime)

            # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
            shutil.copy(latest_file, destination_path)
            if os.path.exists(destination_path):
                os.replace(destination_path, destination_path)

            print("E COPIADO")
            numero += 1

        except:
            pass


