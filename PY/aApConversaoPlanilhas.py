from db_arquivos import *
from db_funcoes import *
import pandas as pd
import time, csv
from datetime import date, timedelta

df1 = pd.read_csv('C:\\CSV\\atualizacao.csv')
df1 = df1.fillna(0).map(remover_acentos)
df2 = pd.read_csv(relatorioQgis)
df2 = df2.fillna(0)

data_base = date(1899, 12, 31)

relatorioGsan = relatorioGsan1

header = ['ALTERAR', 'ORDEM1', 'ORDEM2', 'LOCAL', 'SETOR', 'QUADRA', 'LOTE', 'SUBLOTE', 'TESTADA', 'SEQUENCIA', 'ROTA', 'MATRICULA', 'COD_LOG', 'BAIRRO', 'CEP_GSAN', 'NUMERO', 'COMPLEMENTO', 'NOME', 'CPF', 'CNPJ', 'V_CPF', 'V_CNPJ', 'COD_CLIENTE', 'EMAIL', 'RG', 'DATA_EXP', 'SEXO', 'MAE', 'DATA_NASC','TIPO_CLIENTE', 'TIPO_HAB', 'RES', 'COM', 'MUN', 'EST', 'FED', 'DDD', 'TELEFONE', 'CX', 'CY']

with open(relatorioGsan, mode="w", newline="") as relatorioGsan:
    writer = csv.writer(relatorioGsan)
    writer.writerow(header)

    for i in df1.index:      
        ordem = i+1     
        matricula_raw = df1['MATRÍCULA DO IMÓVEL'][i]
        # Converte matrícula, ignorando se for 0 ou inválido
        try:
            matricula = int(matricula_raw) if matricula_raw != 0 else None
        except:
            matricula = None
        localidade = str(df1['LOCALIDADE'][i])
        localidade = localidade[:3]
        setor = str(df1['SETOR'][i])
        rota = str(df1['ROTA'][i])
        numVisita = str(df1['Nº DA VISITA'][i])
        numImovel = str(df1['NÚMERO DO IMÓVEL'][i])
        econRes = int(df1['CATEGORIA x ECONOMIAS [RESIDENCIAL]'][i])
        econCom = int(df1['CATEGORIA x ECONOMIAS [COMERCIAL]'][i])
        econMun = int(df1['CATEGORIA x ECONOMIAS [PUBLICO MUN.]'][i])
        econEst = int(df1['CATEGORIA x ECONOMIAS [PUBLICO EST.]'][i])
        econFed = int(df1['CATEGORIA x ECONOMIAS [PUBLICO FED.]'][i])
        econInd = int(df1['CATEGORIA x ECONOMIAS [INDUSTRIAL]'][i])
        cnpj = int(df1['CNPJ'][i])
        nomeCliente = str(df1['NOME COMPLETO'][i])
        cpf = int(df1['CPF'][i])    
        dataExp = str(df1['DATA DE EXPEDIÇÃO'][i])
        # if dataExp != 0:
        #     dataExp = data_base + timedelta(days=dataExp)
        #     dataExp = dataExp.strftime("%d/%m/%Y")
        nomeMae = str(df1['NOME DA MÃE'][i])
        dataNasc = str(df1['DATA DE NASCIMENTO'][i])    
        # if dataNasc != 0:
        #     dataNasc = data_base + timedelta(days=dataNasc)    
        #     dataNasc = dataNasc.strftime("%d/%m/%Y")
        rgCliente = str(df1['RG'][i])
        emailCliente = str(df1['E-MAIL'][i])
        telefone = str(df1['TELEFONE DE CONTATO COM DDD'][i])
        ddd = telefone[:2].replace('.0','')
        telefone = telefone[2:].replace('.0','')
        
        # Inicializa valores padrão do QGIS - SEMPRE LIMPA A CADA LINHA
        seq_id_qgis = ''
        quadra_qgis = ''
        latitude = ''
        longitude = ''
        encontrou = False
        
        # Procura correspondência no df2 (relatorioQgis)
        # Só busca se matrícula for válida (não None e não 0)
        if matricula and matricula != 0:
            for j in df2.index:
                imv_id = int(df2['imv_id'][j])
                # Pula imv_id zerado ou inválido
                if imv_id == 0 or imv_id is None:
                    continue
                if matricula == imv_id:
                    lat_temp = df2['latitude'][j]
                    lon_temp = df2['longitude'][j]
                    
                    # Só atribui se as coordenadas não forem 0
                    if lat_temp != 0 and lon_temp != 0:
                        seq_id_qgis = int(df2['seq_id'][j])
                        quadra_qgis = int(df2['quadra'][j])
                        latitude = str(lat_temp)
                        longitude = str(lon_temp)
                        encontrou = True
                        print(f"✅ {ordem}: Mat {matricula} = imv_id {imv_id} | quadra {quadra_qgis}, seq {seq_id_qgis} | lat {latitude}, long {longitude}")
                        break  # PARA no primeiro match válido
                    
        if not encontrou:
            print(f"❌ {ordem}: Matrícula {matricula} NÃO encontrada ou sem coordenadas válidas")
        
        # Escreve a linha no relatório (usa matrícula original mesmo se None)
        matricula_output = matricula if matricula else ''
        row = ordem, matricula_output, localidade, setor, quadra_qgis, rota, seq_id_qgis, numVisita, numImovel, econRes, econCom, econMun, econEst, econFed, cnpj, nomeCliente, cpf, dataExp, nomeMae, dataNasc, rgCliente, emailCliente, ddd, telefone, latitude, longitude
        writer.writerow(row)
            


