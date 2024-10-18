import pandas as pd
from arquivos import elaboration, teste
import re, csv

df = pd.read_csv(elaboration)

cabeçalho = ['#', 'CPF', 'DIGITO', 'ESTADO']

with open(teste, mode="w", newline="") as teste:
    escritor = csv.writer(teste)
    escritor.writerow(cabeçalho)
    def pontuarCpf(cpf):
        return re.sub(r'(\d{3})(\d{3})(\d{3})(\d{2})', r'\1.\2.\3-\4', cpf)

    for i in df.index:
        linha = str(df['CPF'][i])
        if len(linha) == 11:
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        if len(linha) == 10:
            linha = '0' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        elif len(linha) == 9:
            linha = '00' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        elif len(linha) == 8:
            linha = '000' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        elif len(linha) == 7:
            linha = '0000' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        elif len(linha) == 6:
            linha = '00000' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        elif len(linha) == 5:
            linha = '000000' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        elif len(linha) == 4:
            linha = '0000000' + linha
            linha = pontuarCpf(linha)
            if linha[10] == '3':
                estado = 'MA'
            else:
                estado = 'OUTRO'

        line = (i+1, str(linha), linha[10], estado)
        escritor.writerow(line)




