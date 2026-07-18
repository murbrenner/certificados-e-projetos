from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import elaboration, teste, inserir_imovel, abrir_ra
import csv

df = pd.read_csv(elaboration)

header = ['LATITUDE', 'LONGITUDE']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(header)

    for i in df.index:

        lat_long = str(df['wkt_geom'][i])               

        latitude = lat_long[0:20]
        longitude = lat_long[21:]

        latitude = latitude.strip()
        longitude = longitude.strip()
        

        # latitude = latitude * -1
        # longitude = longitude * -1    
    

                     

        # latitude.replace(',', ',')
        # longitude.replace(',', ',')

        # latitude.replace("'", "")
        # longitude.replace("'", "")

        # latitude.strip()
        # longitude.strip()

        # latitude = float(latitude)
        # longitude = float(longitude)

        # latitude.replace('-', '')
        # longitude.replace('-', '')

        print(latitude)
        print(longitude)

        linha = latitude, longitude
        escritor.writerow(linha)