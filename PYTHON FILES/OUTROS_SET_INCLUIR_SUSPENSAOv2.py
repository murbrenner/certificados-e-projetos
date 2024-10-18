from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import elaboration
from db_login import login, driver
import time

base = pd.read_csv(elaboration)
login()

def volumeInformado():
    driver.find_element(By.NAME, 'consumoFixoNaoMedido').send_keys(str(base['CONS_NAO_MEDIDO'][i-2]))    
    driver.find_element(By.NAME, 'consumoFixoMedido').send_keys(str(base['CONS_MEDIDO'][i-2]))
    driver.find_element(By.NAME, 'volumeFixoNaoMedido').send_keys(str(base['VOL_NAO_MEDIDO'][i-2]))
    driver.find_element(By.NAME, 'volumeFixoMedido').send_keys(str(base['VOL_MEDIDO'][i-2]))

i = 2
while i <= 10:
    driver.get('https://gsan.caema.ma.gov.br/gsan/exibirSituacaoEspecialFaturamentoInformarAction.do?menu=sim')
    matricula = str(base['MATRICULA'][i-2]).split('.')[0]
    driver.find_element(By.NAME, 'idImovel').send_keys(matricula, Keys.ENTER)
    time.sleep(0.1)
    #driver.find_element(By.NAME, 'idImovel').send_keys(str(base['MATRICULA'][i-2]), Keys.ENTER)
    driver.find_element(By.NAME, 'selecionar').click()
    valor = driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[28]/td[2]/input').get_attribute('value')

    if valor != '0':
        driver.find_element(By.NAME, 'retirar').click()
        driver.find_element(By.NAME, 'observacaoRetira').send_keys(str(base['OBS'][i-2]))
        driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr[1]/td[2]/input').click()
        popup = driver.switch_to.alert
        popup.accept()
        driver.get('http://gsan.caema.ma.gov.br:8080/gsan/exibirSituacaoEspecialFaturamentoInformarAction.do?menu=sim')
        driver.find_element(By.NAME, 'idImovel').send_keys(matricula, Keys.ENTER)
        driver.find_element(By.NAME, 'selecionar').click()
        driver.find_element(By.NAME, 'inserir').click()

        driver.find_element(By.NAME, 'idFaturamentoSituacaoTipo').send_keys(str(base['SITUACAO'][i-2]))
        time.sleep(11111)
        #volumeInformado()
        driver.find_element(By.NAME, 'idFaturamentoSituacaoMotivo').send_keys(str(base['MOTIVO'][i-2]))
        if base['REF_INICIAL'][i-2] <= 92024 :
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoInicial').send_keys('0'+str(base['REF_INICIAL'][i-2]))
        else:
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoInicial').send_keys(str(base['REF_INICIAL'][i-2]))
        if base['REF_FINAL'][i-2] <= 92024 :
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoFinal').send_keys('0'+str(base['REF_FINAL'][i-2]))
        else:
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoFinal').send_keys(str(base['REF_FINAL'][i-2]))
        driver.find_element(By.NAME, 'observacaoInforma').send_keys(str(base['OBS'][i-2]))
        #sleep(1000)
        driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr/td[2]/input').click()
        popup = driver.switch_to.alert
        popup.accept()
        print(i, str(base['MATRICULA'][i-2]), "RETIRADO E INSERIDO")
        i = i + 1

    else:
        driver.find_element(By.NAME, 'inserir').click()
        driver.find_element(By.NAME, 'idFaturamentoSituacaoTipo').send_keys(str(base['SITUACAO'][i-2]))
        #volumeInformado()
        driver.find_element(By.NAME, 'idFaturamentoSituacaoMotivo').send_keys(str(base['MOTIVO'][i-2]))

        if base['REF_INICIAL'][i-2] <= 92024 :
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoInicial').send_keys('0'+str(base['REF_INICIAL'][i-2]))
        else:
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoInicial').send_keys(str(base['REF_INICIAL'][i-2]))

        if base['REF_FINAL'][i-2] <= 92024 :
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoFinal').send_keys('0'+str(base['REF_FINAL'][i-2]))
        else:
            driver.find_element(By.NAME, 'mesAnoReferenciaFaturamentoFinal').send_keys(str(base['REF_FINAL'][i-2]))
        driver.find_element(By.NAME, 'observacaoInforma').send_keys(str(base['OBS'][i-2]))

        #sleep(1000)
        driver.find_element(By.XPATH, '/html/body/form/table[3]/tbody/tr/td[2]/table[6]/tbody/tr/td[2]/input').click()
        popup = driver.switch_to.alert
        popup.accept()
        print(i, str(base['MATRICULA'][i-2]), "APENAS INSERIDO")
        i = i + 1



