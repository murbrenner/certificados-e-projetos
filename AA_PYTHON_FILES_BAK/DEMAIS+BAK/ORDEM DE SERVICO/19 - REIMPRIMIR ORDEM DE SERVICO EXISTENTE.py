import time
from selenium.webdriver.common.by import By
import pandas as pd
import os
import shutil
from login import driver, murilo
from arquivos import elaboration, teste

df = pd.read_csv(teste)
murilo()

#caminho = os.mkdir(r"C:\Users\Murilo\Desktop\O.S REP")
caminho = r"C:\Users\Murilo\Desktop\CAD IMOVEL"
if os.path.exists(caminho):
    pass
else:
    os.mkdir(caminho)

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][0]))
driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()

for i in df.index:
    #driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroOSParametro").send_keys(str(df['OS'][i]))
    #driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]))
    driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
    driver.find_element(By.PARTIAL_LINK_TEXT,"Dados do Local da Ocorrência").click()
    #mat = driver.find_element(By.NAME, "matriculaImovel").get_attribute("value")
    rra = driver.find_element(By.NAME, "numeroRA").get_attribute("value")
    driver.find_element(By.NAME, "btnImprimir").click()
    time.sleep(0.3)
    j = i + 1
    print(j, 'mat', str(df['OS'][i]), rra)

    time.sleep(0.3)

    # DIZ QUAL É A PASTA DE ORIGEM PRA ELE PEGAR OS ARQUIVOS
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    # SETA A PASTA DE DESTINO PARA A COPIA DO ARQUIVO
    destination_path = caminho

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    try:
        os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\{}_{}.pdf".format(j, str(df['OS'][i])))
    except:
        os.replace(latest_file, "C:\\Users\\Murilo\\Downloads\\{}_{}.pdf".format(j, str(df['OS'][i])))

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    shutil.move("C:\\Users\\Murilo\\Downloads\\{}_{}.pdf".format(j, str(df['OS'][i])), destination_path)

