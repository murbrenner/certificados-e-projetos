from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from arquivos import prog_fisc

#
# def proximo_dia_da_semana(dia_alvo):
#     hoje = datetime.now()
#     dias_ate_dia_alvo = (dia_alvo - hoje.weekday() + 7) % 7
#     data_alvo = hoje + relativedelta(days=dias_ate_dia_alvo)
#     return data_alvo

df = pd.read_csv(prog_fisc)

for i in df.index:
    hoje = datetime.now()
    tomorrow = datetime.now() + timedelta(days=1)
    if str(df['DIA'][i]) == 'segunda':
        dia_num = 0
    elif str(df['DIA'][i]) == 'terça':
        dia_num = 1
    elif str(df['DIA'][i]) == 'quarta':
        dia_num = 2
    elif str(df['DIA'][i]) == 'quinta':
        dia_num = 3
    elif str(df['DIA'][i]) == 'sexta':
       dia_num = 4

    dias_ate_dia_alvo = (dia_num - tomorrow.weekday() + 7) % 7
    data = hoje + relativedelta(days=dias_ate_dia_alvo)



#
#
# # Exemplo de uso para cada dia da semana
# dias_da_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
#
# for dia in dias_da_semana:
#     data_proximo_dia = proximo_dia_da_semana(dias_da_semana.index(dia))
#     print(f"Para hoje ({datetime.now().strftime('%d/%m/%Y')}), próxima {dia} será em: {data_proximo_dia.strftime('%d/%m/%Y')}")