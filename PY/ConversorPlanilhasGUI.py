import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import csv
from db_funcoes2 import remover_acentos
import os

class ConversorPlanilhasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CONVERSOR DE PLANILHAS PARA ATUALIZAÇÃO CADASTRAL")
        self.root.geometry("600x450")
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(False, False)
        
        # Variáveis para armazenar os caminhos
        self.planilha_recadastramento = tk.StringVar()
        self.planilha_qgis = tk.StringVar()
        self.arquivo_saida = tk.StringVar()
        self.rota_filtro = tk.StringVar()
        self.localidade_filtro = tk.StringVar()
        
        self.criar_interface()
    
    def criar_interface(self):
        # Título
        titulo = tk.Label(
            self.root,
            text="CONVERSOR DE PLANILHAS - RECADASTRAMENTO",
            font=("Arial", 14, "bold"),
            bg='#2b2b2b',
            fg='#ff6600'
        )
        titulo.pack(pady=20)
        
        # Frame principal
        frame_principal = tk.Frame(self.root, bg='#2b2b2b')
        frame_principal.pack(padx=30, pady=10, fill='both', expand=True)
        
        # PLANILHA ONLINE RECADASTRAMENTO
        self.criar_campo_arquivo(
            frame_principal,
            "PLANILHA ONLINE RECADASTRAMENTO",
            self.planilha_recadastramento,
            self.procurar_planilha_recadastramento,
            0
        )
        
        # PLANILHA QGIS
        self.criar_campo_arquivo(
            frame_principal,
            "PLANILHA QGIS",
            self.planilha_qgis,
            self.procurar_planilha_qgis,
            1
        )
        
        # FILTRO DE ROTA (integrado como campo com botão)
        self.criar_campo_rota(frame_principal, 2)
        
        # ARQUIVO DE SAÍDA
        self.criar_campo_arquivo(
            frame_principal,
            "ARQUIVO DE SAÍDA",
            self.arquivo_saida,
            self.procurar_arquivo_saida,
            3
        )
        
        # Frame para botões
        frame_botoes = tk.Frame(self.root, bg='#2b2b2b')
        frame_botoes.pack(pady=20)
        
        # Botão CONVERTER
        btn_converter = tk.Button(
            frame_botoes,
            text="CONVERTER",
            font=("Arial", 11, "bold"),
            bg='#404040',
            fg='white',
            activebackground='#1e90ff',
            activeforeground='white',
            bd=0,
            highlightthickness=2,
            highlightbackground='#1e90ff',
            highlightcolor='#1e90ff',
            width=15,
            height=2,
            command=self.converter
        )
        btn_converter.grid(row=0, column=0, padx=10)
        
        # Botão CANCELAR
        btn_cancelar = tk.Button(
            frame_botoes,
            text="CANCELAR",
            font=("Arial", 11, "bold"),
            bg='#404040',
            fg='white',
            activebackground='#ff6600',
            activeforeground='white',
            bd=0,
            highlightthickness=2,
            highlightbackground='#ff6600',
            highlightcolor='#ff6600',
            width=15,
            height=2,
            command=self.root.quit
        )
        btn_cancelar.grid(row=0, column=1, padx=10)
        
        # Configurar peso das colunas
        frame_principal.columnconfigure(0, weight=1)
    
    def criar_campo_arquivo(self, parent, label_text, variavel, comando, row):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Arial", 9, "bold"),
            bg='#2b2b2b',
            fg='white',
            anchor='w'
        )
        label.grid(row=row*2, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        entry = tk.Entry(
            parent,
            textvariable=variavel,
            font=("Arial", 9),
            bg='#404040',
            fg='white',
            state='readonly',
            readonlybackground='#404040',
            relief='flat'
        )
        entry.grid(row=row*2+1, column=0, sticky='ew', ipady=8)
        
        btn_procurar = tk.Button(
            parent,
            text="PROCURAR",
            font=("Arial", 9, "bold"),
            bg='#404040',
            fg='white',
            activebackground='#ffcc00',
            activeforeground='black',
            bd=0,
            highlightthickness=2,
            highlightbackground='#ffcc00',
            highlightcolor='#ffcc00',
            width=12,
            command=comando
        )
        btn_procurar.grid(row=row*2+1, column=1, padx=(10, 0), ipady=5)
    
    def criar_campo_rota(self, parent, row):
        # Frame para rota e localidade lado a lado
        frame_filtros = tk.Frame(parent, bg='#2b2b2b')
        frame_filtros.grid(row=row*2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        frame_filtros.columnconfigure(0, weight=1)
        frame_filtros.columnconfigure(1, weight=1)
        
        # Campo ROTA (esquerda)
        frame_rota = tk.Frame(frame_filtros, bg='#2b2b2b')
        frame_rota.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        label_rota = tk.Label(
            frame_rota,
            text="FILTRAR POR ROTA (deixe vazio para todas)",
            font=("Arial", 9, "bold"),
            bg='#2b2b2b',
            fg='white',
            anchor='w'
        )
        label_rota.pack(anchor='w', pady=(0, 5))
        
        entry_rota = tk.Entry(
            frame_rota,
            textvariable=self.rota_filtro,
            font=("Arial", 9),
            bg='#404040',
            fg='white',
            insertbackground='white',
            relief='flat'
        )
        entry_rota.pack(fill='x', ipady=8)
        
        # Campo LOCALIDADE (direita)
        frame_localidade = tk.Frame(frame_filtros, bg='#2b2b2b')
        frame_localidade.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        label_localidade = tk.Label(
            frame_localidade,
            text="FILTRAR POR LOCALIDADE (deixe vazio para todas)",
            font=("Arial", 9, "bold"),
            bg='#2b2b2b',
            fg='white',
            anchor='w'
        )
        label_localidade.pack(anchor='w', pady=(0, 5))
        
        entry_localidade = tk.Entry(
            frame_localidade,
            textvariable=self.localidade_filtro,
            font=("Arial", 9),
            bg='#404040',
            fg='white',
            insertbackground='white',
            relief='flat'
        )
        entry_localidade.pack(fill='x', ipady=8)
    
    def procurar_planilha_recadastramento(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha de Recadastramento",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.planilha_recadastramento.set(filename)
    
    def procurar_planilha_qgis(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha QGIS",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.planilha_qgis.set(filename)
    
    def procurar_arquivo_saida(self):
        filename = filedialog.asksaveasfilename(
            title="Selecione o Arquivo de Saída",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.arquivo_saida.set(filename)
    
    def converter(self):
        # Validar se os arquivos foram selecionados
        if not self.planilha_recadastramento.get():
            messagebox.showerror("Erro", "Selecione a Planilha de Recadastramento!")
            return
        
        if not self.planilha_qgis.get():
            messagebox.showerror("Erro", "Selecione a Planilha QGIS!")
            return
        
        if not self.arquivo_saida.get():
            messagebox.showerror("Erro", "Defina o Arquivo de Saída!")
            return
        
        try:
            # Carregar as planilhas
            df = pd.read_csv(self.planilha_recadastramento.get())
            df = df.fillna(0).map(remover_acentos)
            df2 = pd.read_csv(self.planilha_qgis.get())
            
            # Filtrar por rota se especificado
            rota_filtro = self.rota_filtro.get().strip()
            localidade_filtro = self.localidade_filtro.get().strip()
            
            if rota_filtro:
                df['ROTA_STR'] = df['ROTA'].astype(str).str.replace('.0', '')
                df = df[df['ROTA_STR'] == rota_filtro]
                
                if df.empty:
                    messagebox.showwarning(
                        "Aviso", 
                        f"Nenhum registro encontrado para a rota '{rota_filtro}'!"
                    )
                    return
            
            if localidade_filtro:
                df['LOCALIDADE_STR'] = df['LOCALIDADE'].astype(str)
                # Filtrar por localidade (primeiros 3 caracteres)
                df = df[df['LOCALIDADE_STR'].str[:3] == localidade_filtro[:3]]
                
                if df.empty:
                    messagebox.showwarning(
                        "Aviso", 
                        f"Nenhum registro encontrado para a localidade '{localidade_filtro}'!"
                    )
                    return
            
            # Header do arquivo de saída
            header = ['ALTERAR', 'ORDEM1', 'ORDEM2', 'LOCAL', 'SETOR', 'QUADRA', 'LOTE', 
                     'SUBLOTE', 'TESTADA', 'SEQUENCIA', 'ROTA', 'MATRICULA', 'COD_LOG', 
                     'BAIRRO', 'CEP_GSAN', 'NUMERO', 'COMPLEMENTO', 'NOME', 'CPF', 'CNPJ', 
                     'V_CPF', 'V_CNPJ', 'COD_CLIENTE', 'EMAIL', 'RG', 'DATA_EXP', 'SEXO', 
                     'MAE', 'DATA_NASC', 'TIPO_CLIENTE', 'TIPO_HAB', 'RES', 'COM', 'MUN', 
                     'EST', 'FED', 'DDD', 'TELEFONE', 'CX', 'CY']
            
            # Processar e escrever no arquivo
            with open(self.arquivo_saida.get(), mode="w", newline="", encoding='utf-8') as arquivo_saida:
                writer = csv.writer(arquivo_saida)
                writer.writerow(header)
                
                for idx, i in enumerate(df.index):
                    ordem = idx + 1
                    matricula_raw = df['MATRÍCULA DO IMÓVEL'][i]
                    
                    try:
                        matricula = int(matricula_raw) if matricula_raw != 0 else None
                    except:
                        matricula = None
                    
                    localidade = str(df['LOCALIDADE'][i])
                    localidade = localidade[:3]
                    setor = str(df['SETOR'][i])
                    rota = str(df['ROTA'][i]).replace('.0', '')
                    numVisita = str(df['Nº DA VISITA'][i]).replace('.0', '')
                    numImovel = str(df['NÚMERO DO IMÓVEL'][i]).replace('.0', '')
                    
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
                        tipoHab = 0
                    else:
                        tipoHab = 1
                    
                    dataExp = str(df['DATA DE EXPEDIÇÃO'][i])
                    nomeMae = str(df['NOME DA MÃE'][i])
                    dataNasc = str(df['DATA DE NASCIMENTO'][i])
                    rgCliente = str(df['RG'][i]).replace('.0', '')
                    emailCliente = str(df['E-MAIL'][i])
                    telefone = str(df['TELEFONE DE CONTATO COM DDD'][i])
                    ddd = telefone[:2].replace('0.', '0')
                    telefone = telefone[2:].replace('.0', '')
                    
                    if econRes + econCom + econMun + econEst + econFed + econInd == 0:
                        econRes = 1
                    
                    # Buscar dados do QGIS
                    quadra = 0
                    latitude = 0
                    longitude = 0
                    
                    if matricula:
                        for j in df2.index:
                            imv_id = str(df2['imv_id'][j])
                            if imv_id == str(matricula):
                                latitude = str(df2['latitude'][j])
                                longitude = str(df2['longitude'][j])
                                quadra = str(df2['quadra'][j])
                                break
                    
                    row = [1, ordem, ordem, localidade, setor, quadra, numVisita, 0, 0, 
                          numVisita, rota, matricula, 0, '', 0, numImovel, 0, nomeCliente, 
                          cpf, cnpj, vcpf, vcnpj, 0, emailCliente, rgCliente, dataExp, '', 
                          nomeMae, dataNasc, tipoCliente, tipoHab, econRes, econCom, econMun, 
                          econEst, econFed, ddd, telefone, latitude, longitude]
                    writer.writerow(row)
            
            messagebox.showinfo(
                "Sucesso", 
                f"Conversão concluída!\n\nArquivo gerado: {self.arquivo_saida.get()}\n"
                f"Total de registros: {len(df)}"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao converter planilhas:\n\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorPlanilhasApp(root)
    root.mainloop()
