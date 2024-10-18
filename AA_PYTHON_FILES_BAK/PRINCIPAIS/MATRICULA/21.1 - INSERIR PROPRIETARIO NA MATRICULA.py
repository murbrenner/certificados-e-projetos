import time, os, glob, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, murilo2
from arquivos import inserir_imovel, elaboration

df = pd.read_csv(inserir_imovel)
murilo2()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")
    driver.find_element(By.NAME, 'matriculaFiltro').send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    time.sleep(0.5)
    driver.find_element(By.ID, "3").click()
    time.sleep(0.2)
    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass
    id_cliente = str(df['COD_CLIENTE'][i])
     
    
    try:
        tipo_cliente = driver.find_element(By.XPATH,"//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[5]/div").text
        if tipo_cliente == "USUARIO":
            date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[6]").text
    except:
        pass

    driver.find_element(By.NAME, 'idCliente').send_keys(id_cliente, Keys.ENTER)
    driver.find_element(By.NAME, "tipoClienteImovel").send_keys("01 - PROPRIETARIO")
    driver.find_element(By.NAME, "dataInicioClienteImovelRelacao").clear()
    driver.find_element(By.NAME, "dataInicioClienteImovelRelacao").send_keys(date_inicio_rel)

    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
    try:
        time.sleep(0.2)
        driver.find_element(By.XPATH, "//input[@value='Sim']").click()        
        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
        msg_ok = driver.find_element(By.XPATH,
                                        "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(i + 1, msg_ok)
    except:
        msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(i + 1, msg_err)


    



    # user_cod = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[3]/div").text

    
    # try:
    #     tipo_cliente = driver.find_element(By.XPATH,"//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[5]/div").text
    #     if tipo_cliente == "USUARIO":
    #         date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[6]").text
    # except:
    #     pass
    # j = 1
    # while j < 4:
    #     try:
    #         tipo_cliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[5]/div".format(j)).text
    #         if tipo_cliente == "PROPRIETARIO":
    #             date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[6]".format(j)).text
    #             driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/div/input".format(j)).click()
    #     except:
    #         break
    # j = j + 1
    # time.sleep(0.2)
    # driver.find_element(By.XPATH, "//input[@value='Remover']").click()
    # alert = driver.switch_to.alert
    # alert = alert.accept()
    # time.sleep(1)
    # janela = driver.window_handles[0]
    # popup = driver.window_handles[1]
    # driver.switch_to.window(popup)
    # date_inicio_rel = date_inicio_rel.replace('/', '')
    # #data_fim = str(df['DATA'][i]).replace('/', '')
    # driver.find_element(By.NAME, 'dataTerminoRelacao').clear()
    # driver.find_element(By.NAME, 'dataTerminoRelacao').send_keys(date_inicio_rel)
    # driver.find_element(By.NAME, 'idMotivo').send_keys('ATUALIZ. CADASTRAL')
    # driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    # try:
    #     time.sleep(0.2)
    #     msg_err0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span")
    #     print(msg_err0.text)
    #     msg_er1 = bool(msg_err0)
    #     driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
    #     driver.close()
    #     time.sleep(0.5)
    #     driver.switch_to.window(janela)
    #     driver.find_element(By.XPATH, "//input[@value='Cancelar']").click()
    # except:
    #     time.sleep(0.2)
    #     driver.switch_to.window(janela)
    #     janela = driver.window_handles[0]
    #     driver.switch_to.window(janela)
    #     driver.find_element(By.NAME, "idCliente").send_keys(str(df['COD_CLIENTE'][i]), Keys.ENTER)
    #     driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
    #     driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
    #     try:
    #         time.sleep(0.2)
    #         driver.find_element(By.XPATH, "//input[@value='Sim']").click()
    #         time.sleep(11111)
    #         #driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
    #         msg_ok = driver.find_element(By.XPATH,
    #                                         "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
    #         print(i + 1, msg_ok)
    #     except:
    #         msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
    #         print(i + 1, msg_err)