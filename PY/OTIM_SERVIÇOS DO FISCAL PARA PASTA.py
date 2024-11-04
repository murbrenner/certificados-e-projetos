import time
import os
import shutil
from datetime import date, timedelta
from selenium.webdriver.common.by import By
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, down_path
from db_fiscais import num_nomes, num_nomes_joined

from pypdf import PdfWriter


data = date.today() + timedelta(days=1)
data_dash = data.strftime("%d-%m-%Y")
data = data.strftime("%d/%m/%Y")
df = pd.read_csv(elaboration)
login()

pasta_fiscal = "C:\\Users\\ocmvc45555\\Desktop\\SERVICO {}".format(data_dash)
os.makedirs(pasta_fiscal)

for i in num_nomes:   

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirAcompanharRoteiroProgramacaoOrdemServicoAction.do?menu=sim&filtro=0&dataRoteiro={}".format(data))
    
    try:
        driver.find_element(By.LINK_TEXT, "{}".format(num_nomes[i])).click()
        num_os = driver.find_element(By.XPATH, "//a[@title='Consultar Dados da Ordem de Serviço']").get_attribute('text')
        num_os = num_os.strip()        
        driver.find_element(By.LINK_TEXT, 'Todos').click()
        driver.find_element(By.XPATH, "//input[@value='Imprimir OS']").click()        

        time.sleep(2)       

        list_of_files = os.listdir(down_path)
        full_path = [os.path.join(down_path, file) for file in list_of_files]
        latest_file = max(full_path, key=os.path.getmtime)

        try:
            os.renames(latest_file, "C:\\Users\\ocmvc45555\\Downloads\\OS_{}.pdf".format(num_nomes[i]))
        except:
            os.replace(latest_file, "C:\\Users\\ocmvc45555\\Downloads\\OS_{}.pdf".format(num_nomes[i]))

        # COPIA O ARQUIVO MAIS RECENTE DA PASTA DOWNLOADS PARA A PASTA COM O NUMERO DA R.A
        shutil.move("C:\\Users\\ocmvc45555\\Downloads\\OS_{}.pdf".format(num_nomes[i]), pasta_fiscal)
    except:
        pass
    
        

    pdfs = "C:\\Users\\ocmvc45555\\Desktop\\SERVICO {}\\OS_*.pdf".format(data_dash)

    merger = PdfWriter()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("result.pdf")
    merger.close()

    
