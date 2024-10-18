from datetime import date
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import shutil
import subprocess
import time
import pyautogui
import pandas as pd
import pygetwindow as gw
import keyboard
import os
from login import murilo, driver
from clearkeys import clear_all_keys_pressed

today = date.today()
today = today.strftime("%d/%m/%Y")
#today = "10/08/2023"
print(today)

murilo()

driver.get(
    "http://gsan.caema.ma.gov.br:8080/gsan/exibirElaborarOrdemServicoRoteiroCriteriosAction.do?menu=sim&filtro=0&dataRoteiro={}".format(
        today))
driver.find_element(By.XPATH, "//option[@value='613']").click()
driver.find_element(By.XPATH, "//option[@value='890']").click()
#driver.find_element(By.XPATH, "//option[@value='9125']").click()
driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
driver.find_element(By.XPATH, "//option[@value='{}']".format('230')).click()
driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
total = int(driver.find_element(By.NAME, "selecionadas").get_attribute('value'))
contador = 1
num = 1

while num < total:
    driver.get(
        "http://gsan.caema.ma.gov.br:8080/gsan/exibirElaborarOrdemServicoRoteiroCriteriosAction.do?menu=sim&filtro=0&dataRoteiro={}".format(
            today))
    driver.find_element(By.XPATH, "//option[@value='613']").click()
    driver.find_element(By.XPATH, "//option[@value='890']").click()
    #driver.find_element(By.XPATH, "//option[@value='9125']").click()
    driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
    driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()
    driver.find_element(By.XPATH, "//option[@value='{}']".format('230')).click()
    driver.find_element(By.XPATH, "//input[@value='  >  ']").click()

    oos = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[1]/input".format(num)).get_attribute('value')
    driver.find_element(By.XPATH, "//input[@value='{}']".format(oos)).click()
    rra = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[7]/div/a".format(num)).text

    #CRIA A PASTA DE DESTINO PARA O ARQUIVO BASEADA NO NUMERO INSERIDO NA COLUNA -RA- DA PLANILHA CSV
    caminho = r"C:\Users\Murilo\Desktop\LEVANTAMENTOS DE DADOS\{}".format(oos)
    if not os.path.exists(caminho):
        os.makedirs(caminho)
    else:
        pass

    #DIZ QUAL É A PASTA DE ORIGEM PRA ELE PEGAR OS ARQUIVOS
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    # SETA A PASTA DE DESTINO PARA A COPIA DO ARQUIVO
    destination_path = caminho

    #rra = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td/div/table/tbody/tr[{}]/td[7]/div/a".format(num)).text
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys("{}".format(rra), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.XPATH, "//*[@id='layerHideLocal']/table/tbody/tr/td/span/a/b").click()
    inscricaosearch = driver.find_element(By.NAME, "inscricaoImovel").get_attribute('value')
    localidade = driver.find_element(By.NAME, "idLocalidade").get_attribute('value')
    setor = driver.find_element(By.NAME, "idSetorComercial").get_attribute('value')
    rota = driver.find_element(By.NAME, "rota").get_attribute('value')


    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroOS").send_keys("{}".format(oos), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    driver.find_element(By.XPATH, "//input[@value='Imprimir']").click()

    time.sleep(0.5)

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    try:
        os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\O.S.PDF")
    except:
        os.replace(latest_file, "C:\\Users\\Murilo\\Downloads\\O.S.PDF")

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    try:
        shutil.move("C:\\Users\\Murilo\\Downloads\\O.S.PDF", destination_path)
    except:
        pass

    driver.get(
        "http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelOutrosCriteriosConsumidoresInscricao.do?menu=sim&gerarRelatorio=RelatorioCadastroConsumidoresInscricao&limpar=S")
    driver.find_element(By.NAME, "localidadeOrigemID").send_keys((localidade), Keys.ENTER)
    driver.find_element(By.NAME, "setorComercialOrigemCD").send_keys((setor), Keys.ENTER)
    driver.find_element(By.NAME, "cdRotaInicial").send_keys((rota), Keys.ENTER)
    driver.find_element(By.XPATH, "//option[@value='rota']").click()
    driver.find_element(By.NAME, "concluir").click()
    driver.find_element(By.NAME, "botao").click()
    time.sleep(0.5)

    # PEGA O ARQUIVO MAIS RECENTE
    list_of_files = os.listdir(downloads_path)
    full_path = [os.path.join(downloads_path, file) for file in list_of_files]
    latest_file = max(full_path, key=os.path.getmtime)

    try:
        os.renames(latest_file, "C:\\Users\\Murilo\\Downloads\\LISTAGEM.PDF")
    except:
        os.replace(latest_file, "C:\\Users\\Murilo\\Downloads\\LISTAGEM.PDF")

    # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
    try:
        shutil.move("C:\\Users\\Murilo\\Downloads\\LISTAGEM.PDF", destination_path)
    except:
        pass

    txtfile = "C:\\Users\\Murilo\\Downloads\\{}.txt".format(inscricaosearch)
    with open(txtfile, 'w') as file:
        file.write(inscricaosearch)
        file.close()
        try:
            shutil.move(txtfile, destination_path)
        except:
            pass
    file_path = "C:\\Users\\Murilo\\Downloads\\FIND.csv".format(inscricaosearch)
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['INSCRICAO', 'LOCALIDADE', 'SETOR', 'ROTA'])
        writer.writerow([inscricaosearch, localidade, setor, rota])
        csv_file.close()
        try:
            shutil.move(file_path, destination_path)
        except:
            pass

        lugar = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\LISTAGEM PRINT.pdf".format(str(oos))
        delpdf = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\LISTAGEM.pdf".format(oos)
        print(lugar, end=',')
        print((oos), end=',')
        subprocess.run(['start', '', "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\LISTAGEM.pdf".format(
            str(oos))], shell=True)
        time.sleep(2)
        janela = gw.getWindowsWithTitle('LISTAGEM.PDF - Foxit PDF Reader')[0]
        janela.activate()
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        filename2 = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\FIND.csv".format(oos)
        df2 = pd.read_csv(filename2)
        find = (str(df2['INSCRICAO'][0]))
        print(find)
        pyautogui.typewrite(find)
        time.sleep(0.5)
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'p')
        time.sleep(1.5)
        pyautogui.typewrite('Microsoft Print to PDF')
        time.sleep(0.5)
        pyautogui.keyDown('alt')
        pyautogui.keyDown('o')
        time.sleep(0.5)
        pyautogui.keyUp('alt')
        pyautogui.keyUp('o')
        time.sleep(0.5)
        pyautogui.keyDown('up')
        pyautogui.keyUp('up')
        time.sleep(0.5)
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
        time.sleep(0.35)
        pyautogui.typewrite(lugar)
        time.sleep(0.5)
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
        time.sleep(0.5)
        pyautogui.keyDown('alt')
        pyautogui.keyDown('S')
        pyautogui.keyUp('alt')
        pyautogui.keyUp('S')
        clear_all_keys_pressed()

        time.sleep(1)

        subprocess.run(["tskill", "Foxitpdfreader"])
        time.sleep(1)
        os.remove(delpdf)

        findlocal = (str(df2['LOCALIDADE'][0]))
        findsetor = (str(df2['SETOR'][0]))
        findrota = (str(df2['ROTA'][0]))

        if findlocal == '111':
            loc2 = 'CENTRO'
        elif findlocal == '122':
            loc2 = 'VINHAIS'
        elif findlocal == '133':
            loc2 = 'COHAB'
        elif findlocal == '145':
            loc2 = 'CIDADE OPERÁRIA'
        elif findlocal == '151':
            loc2 = 'ANJO DA GUARDA'
        elif findlocal == '183':
            print('GRUPO ALSAN 183 NAO TEM MAPA')
            pass
        else:
            print('ERRO')

        print(findlocal, findsetor, findrota, sep=',', end=',')

        pastamap = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\".format(oos)

        try:
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}.dwg".format(findlocal, loc2,
                                                                                            findsetor,
                                                                                            findrota)
            shutil.copy(file3, pastamap)
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}A.dwg".format(findlocal, loc2,
                                                                                                findsetor,
                                                                                                findrota)
            shutil.copy(file3, pastamap)
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}B.dwg".format(findlocal, loc2,
                                                                                                findsetor,
                                                                                                findrota)
            shutil.copy(file3, pastamap)
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}AB.dwg".format(findlocal, loc2,
                                                                                                findsetor,
                                                                                                findrota)
            shutil.copy(file3, pastamap)
        except:
            try:
                file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}.dwg".format(findlocal, loc2,
                                                                                                    findsetor,
                                                                                                    findrota)
                shutil.copy(file3, pastamap)
                file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}A.dwg".format(findlocal, loc2,
                                                                                                    findsetor,
                                                                                                    findrota)
                shutil.copy(file3, pastamap)
                file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}B.dwg".format(findlocal, loc2,
                                                                                                    findsetor,
                                                                                                    findrota)
                shutil.copy(file3, pastamap)
                file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}AB.dwg".format(findlocal, loc2,
                                                                                                    findsetor,
                                                                                                    findrota)
                shutil.copy(file3, pastamap)

            except:
                try:
                    file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA00{}.dwg".format(findlocal,
                                                                                                        loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                    shutil.copy(file3, pastamap)
                    file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}A.dwg".format(findlocal,
                                                                                                        loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                    shutil.copy(file3, pastamap)
                    file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}B.dwg".format(findlocal,
                                                                                                        loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                    shutil.copy(file3, pastamap)
                    file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA 0{}AB.dwg".format(findlocal,
                                                                                                        loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                    shutil.copy(file3, pastamap)

                except:
                    try:
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}.dwg".format(findlocal,
                                                                                                        loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                        shutil.copy(file3, pastamap)
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}A.dwg".format(findlocal,
                                                                                                            loc2,
                                                                                                            findsetor,
                                                                                                            findrota)
                        shutil.copy(file3, pastamap)
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}B.dwg".format(findlocal,
                                                                                                            loc2,
                                                                                                            findsetor,
                                                                                                            findrota)
                        shutil.copy(file3, pastamap)
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}AB.dwg".format(findlocal,
                                                                                                            loc2,
                                                                                                            findsetor,
                                                                                                            findrota)
                        shutil.copy(file3, pastamap)

                    except:
                        try:
                            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}.dwg".format(
                                findlocal,
                                loc2,
                                findsetor,
                                findrota)
                            shutil.copy(file3, pastamap)
                            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}A.dwg".format(
                                findlocal,
                                loc2,
                                findsetor,
                                findrota)
                            shutil.copy(file3, pastamap)
                            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}B.dwg".format(
                                findlocal,
                                loc2,
                                findsetor,
                                findrota)
                            shutil.copy(file3, pastamap)
                            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}AB.dwg".format(
                                findlocal,
                                loc2,
                                findsetor,
                                findrota)
                            shutil.copy(file3, pastamap)

                        except:
                            pass

            print(contador, rra, oos, "OK")
            num += 1
            contador += 1

            os.remove(filename2)