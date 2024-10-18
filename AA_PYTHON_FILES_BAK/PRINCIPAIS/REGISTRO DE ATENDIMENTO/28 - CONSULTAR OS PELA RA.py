import time
from selenium.webdriver.common.by import By
import pandas as pd
from login import murilo2, driver
from arquivos import elaboration, teste

df = pd.read_csv(elaboration)
murilo2()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    j = 1
    while j < 5:

        try:
            tipo_os = driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[3]/div/font".format(i)).text
            if tipo_os == "CADASTRAMENTO DE IMOVEL":
                driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/font").click()
            num_ra = driver.find_element(By.NAME, "numeroRA").get_attribute('value')
            sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
            sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
            unid_atual = driver.find_element(By.NAME, "unidadeAtualDescricao").get_attribute('value')
            driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
            matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
            oos = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
            print(i + 1, num_ra, str(oos), "OS:", sit_os, "RA:", sit_ra, unid_atual)
            i = i + 1
        except:
            try:
                tipo_os = driver.find_element(By.XPATH,"/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[3]/div/font".format(i)).text
                if tipo_os == "CADASTRAMENTO DE IMOVEL":
                    driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[2]/div/font".format(i)).click()
                    num_ra = driver.find_element(By.NAME, "numeroRA").get_attribute('value')
                    sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
                    sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
                    unid_atual = driver.find_element(By.NAME, "unidadeAtualDescricao").get_attribute('value')
                    driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
                    matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
                    oos = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
                    print(i + 1, num_ra, str(oos), "OS:", sit_os, "RA:", sit_ra, unid_atual)
                    i = i + 1

            except:
                num_ra = driver.find_element(By.NAME, "numeroRA").get_attribute('value')
                sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
                sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
                unid_atual = driver.find_element(By.NAME, "unidadeAtualDescricao").get_attribute('value')
                driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
                matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
                oos = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
                print(i + 1, num_ra, str(oos), "OS:", sit_os, "RA:", sit_ra, unid_atual)





        j = j + 1

    #print(i + 1, num_ra, str(oos), "OS:", sit_os, "RA:", sit_ra, unid_atual)


        #     if tipo_os == 'CADASTRAMENTO DE IMOVEL':
        #         driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[3]/td/table/tbody/tr[{}]/td[2]/div/a/font".format(j)).click()
        #         time.sleep(0.1)
        #     sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        #     sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
        #     unid_atual = driver.find_element(By.NAME, "unidadeAtualDescricao").get_attribute('value')
        #     driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        #     matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
        #     oos = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
        #
        # except:
        #
        #     time.sleep(11111)
        #
        #     pass
        #
        # sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
        # sit_ra = driver.find_element(By.NAME, "situacaoRA").get_attribute('value')
        # unid_atual = driver.find_element(By.NAME, "unidadeAtualDescricao").get_attribute('value')
        # driver.find_element(By.LINK_TEXT, "Dados do Local da Ocorrência").click()
        # matricula = driver.find_element(By.NAME, "matriculaImovel").get_attribute('value')
        # oos = driver.find_element(By.NAME, "numeroOSPesquisada").get_attribute('value')
        # print(i + 1, str(df['RA'][i]), str(oos), "OS:", sit_os, "RA:", sit_ra, unid_atual)
        # j = j + 1