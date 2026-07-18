from db_arquivos import relatorioPlan
from db_funcoes2 import remover_acentos
import pandas as pd
import csv
#from datetime import date, timedelta

def deduzir_sexo(nome):
    """Deduz o sexo baseado no nome"""
    if not nome or nome == '0' or nome == 'nan':
        return '01 - MASCULINO'
    
    nome_limpo = nome.strip().upper()
    primeiro_nome = nome_limpo.split()[0] if nome_limpo else ''
    
    # Nomes masculinos comuns terminados em 'a'
    masculinos_excecao = ['LUCA', 'JOSHUA', 'GARCIA', 'COSTA', 'SILVA', 'SOUSA', 'SOUZA']
    
    # Se for exceção masculina
    if primeiro_nome in masculinos_excecao:
        return '01 - MASCULINO'
    
    # Se termina com 'a', provavelmente é feminino
    if primeiro_nome.endswith('A'):
        return '02 - FEMININO'
    
    # Padrão: masculino
    return '01 - MASCULINO'

df = pd.read_csv('C:\\CSV\\atualizacao.csv')
df = df.fillna(0).map(remover_acentos)
df2 = pd.read_csv('C:\\CSV\\qgis.csv')

relatorioPlan = relatorioPlan

header = ['ALTERAR', 'ORDEM1', 'ORDEM2', 'LOCAL', 'SETOR', 'QUADRA', 'LOTE', 'SUBLOTE', 'TESTADA', 'SEQUENCIA', 'ROTA', 'MATRICULA', 'COD_LOG', 'BAIRRO', 'CEP_GSAN', 'NUMERO', 'COMPLEMENTO', 'NOME', 'CPF', 'CNPJ', 'V_CPF', 'V_CNPJ', 'COD_CLIENTE', 'EMAIL', 'RG', 'DATA_EXP', 'SEXO', 'MAE', 'DATA_NASC','TIPO_CLIENTE', 'TIPO_HAB', 'RES', 'COM', 'PUB', 'MUN', 'EST', 'FED', 'IND', 'PEQ', 'POP', 'AREA', 'DDD', 'TELEFONE', 'CX', 'CY']

with open(relatorioPlan, mode="w", newline="") as relatorioPlan:
    writer = csv.writer(relatorioPlan)
    writer.writerow(header)

    for i in df.index:
        ordem = i+1
        matricula_raw = df['MATRÍCULA DO IMÓVEL'][i]        
        try:
            matricula = int(matricula_raw) if matricula_raw != 0 else None
        except:
            matricula = None
        localidade = str(df['LOCALIDADE'][i])
        localidade = localidade[:3]
        setor = str(df['SETOR'][i])
        rota = str(df['ROTA'][i]).replace('.0','')
        numVisita = str(df['Nº DA VISITA'][i]).replace('.0','')
        numImovel = str(df['NÚMERO DO IMÓVEL'][i]).replace('.0','')

        econRes = int(df['CATEGORIA x ECONOMIAS [RESIDENCIAL]'][i])
        econCom = int(df['CATEGORIA x ECONOMIAS [COMERCIAL]'][i])
        econMun = int(df['CATEGORIA x ECONOMIAS [PUBLICO MUN.]'][i])
        econEst = int(df['CATEGORIA x ECONOMIAS [PUBLICO EST.]'][i])
        econFed = int(df['CATEGORIA x ECONOMIAS [PUBLICO FED.]'][i])
        econInd = int(df['CATEGORIA x ECONOMIAS [INDUSTRIAL]'][i])
        cnpj = int(df['CNPJ'][i])
        if cnpj > 0: 
            vcnpj = 1
            tipoCliente = '200 - COMERCIAL'
        else:
            vcnpj = 0
            tipoCliente = '100 - RESIDENCIA'
        nomeCliente = str(df['NOME COMPLETO'][i])
        cpf = int(df['CPF'][i])   
        if cpf > 0: 
            vcpf = 1
        else:
            vcpf = 0
        ocorCad = str(df['OCORRENCIA DE CADASTRO'][i])
        if ocorCad == 'Terreno vazio':
            tipoHab =  0
        else:
            tipoHab =  1
        
        # Formatar datas para DD/MM/YYYY
        dataExp = str(df['DATA DE EXPEDIÇÃO'][i])
        if dataExp != '0' and dataExp != 'nan':
            try:
                data_obj = pd.to_datetime(dataExp, errors='coerce')
                ano = data_obj.year
                # Se ano for maior que 2026, subtrai 100
                if ano > 2026:
                    data_obj = data_obj.replace(year=ano - 100)
                dataExp = data_obj.strftime('%d/%m/%Y')
            except:
                pass
        
        dataNasc = str(df['DATA DE NASCIMENTO'][i])
        if dataNasc != '0' and dataNasc != 'nan':
            try:
                data_obj = pd.to_datetime(dataNasc, errors='coerce')
                ano = data_obj.year
                # Se ano for maior que 2008, subtrai 100 (nascimentos devem ser antes de 2008)
                if ano > 2008:
                    data_obj = data_obj.replace(year=ano - 100)
                dataNasc = data_obj.strftime('%d/%m/%Y')
            except:
                pass
        
        nomeMae = str(df['NOME DA MÃE'][i])
        rgCliente = str(df['RG'][i]).replace('.0','')
        emailCliente = str(df['E-MAIL'][i])
        telefone = str(df['TELEFONE DE CONTATO COM DDD'][i])
        ddd = telefone[:2].replace('0.','0')
        telefone = telefone[2:].replace('.0','')
        if econRes + econCom + econMun + econEst + econFed + econInd == 0:
            econRes = 1
        
        # Calcular PUB, PEQ, IND, POP
        econPub = 1 if (econMun > 0 or econEst > 0 or econFed > 0) else 0
        econPeq = 0
        econPop = 0
        area = 40
        bairro = 'CENTRO'
        sexo = deduzir_sexo(nomeCliente)

        quadra = 0
        latitude = 0
        longitude = 0
        encontrou = False
        
        for j in df2.index:
            # Tenta encontrar pela matrícula
            if matricula is not None and not encontrou:
                imv_id = df2['imv_id'][j]
                try:
                    imv_id = int(imv_id) if imv_id != 0 else None
                except:
                    imv_id = None
                if imv_id == matricula:
                    latitude = str(df2['latitude'][j])
                    longitude = str(df2['longitude'][j])
                    quadra = str(df2['quadra'][j])
                    encontrou = True
                    break
            
            # Se não achou pela matrícula, tenta por rota e sequencia
            if not encontrou:
                rot_id = str(df2['rot_id'][j]).replace('.0','')
                seq_id = str(df2['seq_id'][j]).replace('.0','')
                if rot_id == rota and seq_id == numVisita:
                    latitude = str(df2['latitude'][j])
                    longitude = str(df2['longitude'][j])
                    quadra = str(df2['quadra'][j])
                    encontrou = True
                    break
            
        # Garantir que matrícula seja 0 se for None
        if matricula is None:
            matricula = 0

        row = 1, ordem, ordem, localidade, setor, quadra, numVisita, 0, 0, numVisita, rota, matricula, 0, bairro, 0, numImovel, 0, nomeCliente, cpf, cnpj, vcpf, vcnpj, 0, emailCliente, rgCliente, dataExp, sexo, nomeMae, dataNasc, tipoCliente, tipoHab, econRes, econCom, econPub, econMun, econEst, econFed, econInd, econPeq, econPop, area, ddd, telefone, latitude, longitude
        writer.writerow(row)
        