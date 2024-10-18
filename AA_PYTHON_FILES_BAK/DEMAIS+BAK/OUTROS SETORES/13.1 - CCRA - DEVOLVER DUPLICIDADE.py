import time
from selenium.common import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

filename = 'C:\\Users\\Murilo Brenner\\Downloads\\CREDITO - SEDUC.csv'
df = pd.read_csv(filename)

driver = webdriver.Chrome()

def end():
    pass

def login():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('LUIZD')
    driver.find_element(By.NAME, 'senha').send_keys('223906')
    driver.find_element(By.NAME, 'buttonLogin').click()
    begin()

def begin():
    for i in df.index:
        driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoDevolucaoValoresAction.do?menu=sim")
        driver.find_element(By.NAME, "idImovel").send_keys(str(df['MATRICULA'][i]), Keys.ENTER)
        print(str(df['MATRICULA'][i]), end=',')
        try:
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
        except NoSuchElementException:
            print("NEM FILTROU")
        try:
            driver.find_element(By.NAME, "idSelecionado").click()
            driver.find_element(By.XPATH, "//input[@value='Consultar']").click()
        except NoSuchElementException:
            print("SO FILTROU MAS NAO CLICOU NA BOLINHA", end=',')
            end()

        time.sleep(1)
        numero1 = 0
        contador = 0
        while numero1 <= 60:
            numero1 += 1
            try:
                data = driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[2]/font/a".format(numero1)).text
                if str(data) == "10/2022":
                    print("ACHOU TUDO DE OUTUBRO", end=',')
                    driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[{}]/td[1]/input".format(numero1)).click()
                    contador += 1
                else:
                    end()
            except NoSuchElementException:
                break

        while numero1 <= 60:
            numero1 += 1
            try:
                data0 = driver.find_element(By.XPATH, "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[2]/font/a".format(numero1)).text
                if str(data0) == "10/2022":
                    print("ACHOU TUDO DE OUTUBRO", end=',')
                    driver.find_element(By.XPATH,  "/html/body/div[1]/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/input".format(numero1)).click()
                    contador += 1
                else:
                    end()
            except NoSuchElementException:
                break

        numero2 = 0
        if contador != 0:
            print("OCT OK", end=',')
            while numero2 <= 60:
                numero2 += 1
                try:
                    data2 = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[9]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[2]/font/a".format(numero2)).text
                    if str(data2) == "11/2022":
                        print("CLICOU NOVEMBRO", end=',')
                        driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[9]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/input".format(numero2)).click()
                    else:
                        end()
                except NoSuchElementException:
                    break

            numero3 = 0
            while numero3 <= 60:
                numero3 += 1
                try:
                    data3 = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[9]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[2]/font/a".format(numero3)).text
                    if str(data3) == "12/2022":
                        print("CLICOU DEZEMBRO", end=',')
                        driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[9]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/input".format(numero3)).click()
                    else:
                        end()
                except NoSuchElementException:
                    break

            try:
                driver.find_element(By.XPATH, "//input[@value='Calcular']").click()
                print("CALCULOU E", end=',')
                driver.find_element(By.XPATH, "//input[@value='Transferir']").click()
                print("TRANSFERIU", end=',')
                driver.find_element(By.XPATH, "//input[@value='Sim']").click()
                print("ENCERROU R.A")
            except NoSuchElementException:
                end()
        else:
            print("NAO ACHOU ABSOLUTAMENTE NADA DE OUTUBRO")
            pass
    end()

login()

while True:
    pass