import pandas as pd
import csv
from db_arquivos import *

df1 = pd.read_csv('C:\\CSV\\ESP1.csv')
df2 = pd.read_csv('C:\\CSV\\ESP2.csv')

relatorioGsan = relatorioGsan5

header = ['MATRICULA PLAN1', 'ROTA PLAN1', 'MAT_QGIS', 'ROTA_QGIS', 'STATUS']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df1.index:
        mat1 = str(df1['matricula'][i])
        rot1 = str(df1['rota'][i])
        for j in df2.index:
            mat2 = str(df2['imv_id'][j])
            rot2 = str(df2['rot_id'][j])

            if mat1 == mat2:            
                if rot1 == rot2:
                    #print(mat1, rot1, mat2, rot2, 'OK')
                    linha = mat1, rot1, mat2, rot2, 'OK'
                    writer.writerow(linha)
                else:
                    #print(mat1, rot1, mat2, rot2, 'DIVERGENTE')
                    linha = mat1, rot1, mat2, rot2, 'DIVERGENTE'
                    writer.writerow(linha)

