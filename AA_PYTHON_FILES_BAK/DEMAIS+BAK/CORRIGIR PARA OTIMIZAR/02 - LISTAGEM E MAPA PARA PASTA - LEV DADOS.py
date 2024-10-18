import os
import shutil
import subprocess
import time
import pyautogui
import pandas as pd
import pygetwindow as gw
import keyboard


filename = 'C:\\Users\\Murilo\\Desktop\\PROJETOS PYTHON\\CSV FILES\\ELABORATION.csv'
df = pd.read_csv(filename)

def clear_all_keys_pressed():
    # Define the list of keys to check
    keys_to_check = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                     "u", "v", "w", "x", "y", "z", "enter", "esc",
                     "space", "shift", "ctrl", "alt"]

    # Release each key if it is pressed
    for key in keys_to_check:
        if keyboard.is_pressed(key):
            pyautogui.keyUp(key)


def play():
    for i in df.index:
        num = 0
        lugar = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\LISTAGEM PRINT.pdf".format(str(df['OS'][i]))
        delpdf = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\LISTAGEM.pdf".format(str(df['OS'][i]))
        print(lugar, end=',')
        print((str(df['OS'][i])), end=',')
        subprocess.run(['start', '', "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\LISTAGEM.pdf".format(str(df['OS'][i]))], shell=True)
        time.sleep(2)
        janela = gw.getWindowsWithTitle('LISTAGEM.PDF - Foxit PDF Reader')[num]
        janela.activate()
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        filename2 = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\FIND.csv".format(str(df['OS'][i]))
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
        time.sleep(0.5)
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

        pastamap = "C:\\Users\\Murilo\\Desktop\\LEVANTAMENTOS DE DADOS\\{}\\".format(str(df['OS'][i]))

        try:
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}.dwg".format(findlocal, loc2, findsetor,
                                                                                            findrota)
            shutil.copy(file3, pastamap)
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}A.dwg".format(findlocal, loc2, findsetor,
                                                                                            findrota)
            shutil.copy(file3, pastamap)
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}B.dwg".format(findlocal, loc2, findsetor,
                                                                                            findrota)
            shutil.copy(file3, pastamap)
            file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA {}AB.dwg".format(findlocal, loc2, findsetor,
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
                    file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA00{}.dwg".format(findlocal, loc2,
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
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}.dwg".format(findlocal, loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                        shutil.copy(file3, pastamap)
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}A.dwg".format(findlocal, loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                        shutil.copy(file3, pastamap)
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}B.dwg".format(findlocal, loc2,
                                                                                                        findsetor,
                                                                                                        findrota)
                        shutil.copy(file3, pastamap)
                        file3 = "Z:\\MAPAS_CAPITAL\\LOC - {} - {}\\SETOR {}\\ROTAS\\ROTA0{}AB.dwg".format(findlocal, loc2,
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
                            pass



        os.remove(filename2)

play()
