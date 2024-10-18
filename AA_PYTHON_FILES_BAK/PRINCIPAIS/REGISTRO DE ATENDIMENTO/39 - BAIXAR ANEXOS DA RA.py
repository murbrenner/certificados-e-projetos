from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import shutil
from login import murilo, driver, murilo2
from arquivos import elaboration, down_path

df = pd.read_csv(elaboration)
murilo()

for i in df.index:
    caminho = "Z:\\CCRFG - 2024\\ANEXOS RAs\\{}".format(str(df['RA'][i]))
    if not os.path.exists(caminho):
        os.makedirs(caminho)

    destination_path = caminho
    numero = 1
    contador = 0
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "Submit").click()
    print((str(df['RA'][i])))
    j = 1
    while j <= 10:
        try:
            anexo = driver.find_element(By.XPATH, '//*[@id="layerShowAnexos"]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr/td[1]/a/img')
            anexo.click()
            time.sleep(1)
            cont_anexo += 1           
        except: 
            try:
                anexo = driver.find_element(By.XPATH, '//*[@id="layerShowAnexos"]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr[{}]/td[1]/a/img'.format(j))
                anexo.click()
                time.sleep(1)
            except:
                cont_anexo = 0
                pass
            cont_anexo = 0           
            pass

        print(j)
        anexo = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[7]/td/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/div/table/tbody/tr[{}]/td[1]/a/img'.format(j))
        anexo.click()
        time.sleep(1)

        cont_anexo += 1
        try:
            print("ANEXO {} BAIXADO".format(cont_anexo), end=' ')

            # PEGA O ARQUIVO MAIS RECENTE
            list_of_files = os.listdir(down_path)
            full_path = [os.path.join(down_path, file) for file in list_of_files]
            latest_file = max(full_path, key=os.path.getmtime)

            # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
            shutil.copy(latest_file, destination_path)
            if os.path.exists(destination_path):
                os.replace(destination_path, destination_path)

            print("E COPIADO")
            numero += 1
        
        except:
            pass