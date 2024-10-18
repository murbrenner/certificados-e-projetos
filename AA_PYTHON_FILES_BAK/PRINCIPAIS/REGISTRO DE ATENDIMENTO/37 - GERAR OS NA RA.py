from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, murilo2
from arquivos import elaboration, teste, abrir_ra
import csv, re, time

df = pd.read_csv(abrir_ra)
murilo2()

header = ['#', 'RA', 'OS']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:        
        os_plan = str(df['OS'][i])
        if os_plan == '0':
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRegistroAtendimentoAction.do?menu=sim")
            driver.find_element(By.NAME, "numeroRA").send_keys(str(df['RA'][i]))
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
            driver.find_element(By.XPATH, "//input[@value='Gerar O.S']").click()
            driver.find_element(By.NAME, "idServicoTipo").send_keys("INSTALACAO DE HIDROMETRO NO POCO")
            driver.find_element(By.XPATH, "//input[@value='Gerar']").click()
            time.sleep(0.2)
            txt = driver.find_element(By.CSS_SELECTOR, 'body > table:nth-child(5) > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > div > span').text
            num = re.findall(r'\d+', txt)
            num_ra = ' '.join(num).replace("'", '').replace('[', '').replace(']', '')
            num_ra = num_ra.replace(' ', ',')
            num_ra_ok = num_ra[0:7]
            num_os = num_ra[8:15]
            j = i + 1
            linha = j, str(df['RA'][i]), num_os
            escritor.writerow(linha)
        else:
            j = i + 1
            linha = j, str(df['RA'][i]), os_plan
            escritor.writerow(linha)