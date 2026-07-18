import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import csv
import os
import sys

# Tentar importar biblioteca de detecção de gênero
try:
    import gender_guesser.detector as gender
    GENDER_DETECTOR = gender.Detector()
    HAS_GENDER_LIB = True
except ImportError:
    HAS_GENDER_LIB = False

# Importações locais
try:
    from db_arquivos import relatorioPlan as relatorioPlan_default
    from db_funcoes2 import remover_acentos
except ImportError:
    relatorioPlan_default = "relatorio_saida.csv"
    def remover_acentos(texto):
        """Função de fallback caso db_funcoes2 não esteja disponível"""
        if isinstance(texto, str):
            import unicodedata
            return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        return texto


class ConversorPlanilhas:
    def __init__(self, root):
        self.root = root
        self.root.title("CONVERSOR DE PLANILHAS PARA ATUALIZAÇÃO CADASTRAL")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Cores do tema
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.entry_bg = "#3c3c3c"
        self.entry_fg = "#ffffff"
        
        # Configurar cor de fundo da janela
        self.root.configure(bg=self.bg_color)
        
        # Variáveis para armazenar os caminhos dos arquivos
        self.planilha_online_var = tk.StringVar()
        self.planilha_qgis_var = tk.StringVar()
        self.arquivo_saida_var = tk.StringVar()
        self.rota_filtro_var = tk.StringVar()
        self.localidade_filtro_var = tk.StringVar()
        
        # Nomes masculinos brasileiros mais comuns (lista expandida)
        self.nomes_masculinos = {
            'JOAO', 'JOSE', 'ANTONIO', 'FRANCISCO', 'CARLOS', 'PAULO', 'PEDRO', 'LUCAS', 'LUIZ', 'MARCOS',
            'LUIS', 'GABRIEL', 'RAFAEL', 'DANIEL', 'MARCELO', 'BRUNO', 'RODRIGO', 'FELIPE', 'GUILHERME',
            'MATEUS', 'ANDRE', 'FERNANDO', 'FABIO', 'LEONARDO', 'GUSTAVO', 'DIEGO', 'RICARDO', 'THIAGO',
            'MAURICIO', 'EDUARDO', 'ROBERTO', 'SERGIO', 'ALEXANDRE', 'CESAR', 'HENRIQUE', 'VITOR', 'WAGNER',
            'ANDERSON', 'EDSON', 'WILSON', 'NELSON', 'MILTON', 'DAVI', 'SAMUEL', 'MIGUEL', 'ARTHUR', 'ENZO',
            'BERNARDO', 'HEITOR', 'CAIO', 'RENAN', 'RAFAEL', 'VINICIUS', 'FELLIPE', 'IGOR', 'MARIO', 'OTAVIO',
            'RAUL', 'THEO', 'ISAAC', 'LORENZO', 'BENICIO', 'LUAN', 'GIOVANNI', 'PIETRO', 'ANTHONY', 'NICOLAS',
            'MATHEUS', 'LEANDRO', 'ALEX', 'JOEL', 'JOAQUIM', 'MANUEL', 'SEBASTIAO', 'GERALDO', 'VALTER',
            'OSVALDO', 'AGNALDO', 'ALDO', 'MAURO', 'CLAUDIO', 'MARCIO', 'JULIO', 'ROGERIO', 'ADILSON',
            'AILTON', 'JEFFERSON', 'JAIR', 'JONAS', 'OSMAR', 'BENEDITO', 'DOMINGOS', 'PEDRO'
        }
        
        # Nomes femininos brasileiros mais comuns (lista expandida)
        self.nomes_femininos = {
            'MARIA', 'ANA', 'FRANCISCA', 'ANTONIA', 'ADRIANA', 'JULIANA', 'MARCIA', 'FERNANDA', 'PATRICIA',
            'ALINE', 'SANDRA', 'CAMILA', 'AMANDA', 'BRUNA', 'JESSICA', 'LETICIA', 'JULIA', 'BEATRIZ',
            'LARISSA', 'RENATA', 'VANESSA', 'CRISTINA', 'LUCIANA', 'CARLA', 'CLAUDIA', 'RITA', 'ROSA',
            'LUIZA', 'GABRIELA', 'ISABELA', 'RAQUEL', 'DEBORA', 'SIMONE', 'DANIELA', 'PAULA', 'TATIANA',
            'JOANA', 'ANDREIA', 'ELIANA', 'SILVIA', 'VERA', 'SONIA', 'ANDREA', 'ELENA', 'MONICA', 'APARECIDA',
            'LUCIA', 'ROSANGELA', 'MARIANA', 'CAROLINA', 'HELENA', 'VALENTINA', 'VITORIA', 'SOPHIA', 'ALICE',
            'MANUELA', 'LAURA', 'LUISA', 'CECILIA', 'YASMIN', 'MARINA', 'LIVIA', 'RAFAELA', 'BIANCA',
            'ISABELLE', 'LORENA', 'GIOVANNA', 'MELISSA', 'NICOLE', 'SARAH', 'AMANDA', 'BRENDA', 'CLARA',
            'EDUARDA', 'EMANUELLY', 'EVELYN', 'FABIANA', 'GISELE', 'INGRID', 'KARINA', 'LAIS', 'MIRIAM',
            'NATALIA', 'OLIVIA', 'PRISCILA', 'ROBERTA', 'SABRINA', 'TALITA', 'VIVIANE', 'TEREZA', 'CONCEICAO', 'IZABEL', 'EVA'
        }
        
        self.criar_widgets()
        
    def criar_widgets(self):
        # Título com linha cinza
        titulo_frame = tk.Frame(self.root, bg=self.bg_color)
        titulo_frame.pack(pady=(20, 0))
        
        titulo = tk.Label(titulo_frame, text="CONVERSOR DE PLANILHAS - RECADASTRAMENTO", 
                         font=("Arial", 14, "bold"),
                         bg=self.bg_color, fg="#ff6600")
        titulo.pack(padx=20)
        
        titulo_line = tk.Frame(self.root, bg="#666666", height=1)
        titulo_line.pack(fill="x", padx=20, pady=(5, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(self.root, bg=self.bg_color)
        frame_campos.pack(padx=20, pady=10)
        
        # PLANILHA ONLINE RECADASTRAMENTO
        label1 = tk.Label(frame_campos, text="PLANILHA ONLINE RECADASTRAMENTO", 
                         font=("Arial", 9, "bold"),
                         bg=self.bg_color, fg=self.fg_color)
        label1.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        entry1_container = tk.Frame(frame_campos, bg=self.bg_color)
        entry1_container.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        entry1 = tk.Entry(entry1_container, textvariable=self.planilha_online_var, width=50,
                         bg=self.entry_bg, fg=self.entry_fg, 
                         insertbackground=self.fg_color, relief="flat", bd=0,
                         highlightthickness=0)
        entry1.pack(ipady=5)
        
        entry1_line = tk.Frame(entry1_container, bg="#666666", height=2)
        entry1_line.pack(fill="x")
        
        btn1 = self.criar_botao_procurar(frame_campos, self.procurar_planilha_online)
        btn1.grid(row=1, column=1)
        
        # PLANILHA QGIS
        label2 = tk.Label(frame_campos, text="PLANILHA QGIS", 
                         font=("Arial", 9, "bold"),
                         bg=self.bg_color, fg=self.fg_color)
        label2.grid(row=2, column=0, sticky="w", pady=(15, 5))
        
        entry2_container = tk.Frame(frame_campos, bg=self.bg_color)
        entry2_container.grid(row=3, column=0, padx=(0, 10), sticky="ew")
        
        entry2 = tk.Entry(entry2_container, textvariable=self.planilha_qgis_var, width=50,
                         bg=self.entry_bg, fg=self.entry_fg,
                         insertbackground=self.fg_color, relief="flat", bd=0,
                         highlightthickness=0)
        entry2.pack(ipady=5)
        
        entry2_line = tk.Frame(entry2_container, bg="#666666", height=2)
        entry2_line.pack(fill="x")
        
        btn2 = self.criar_botao_procurar(frame_campos, self.procurar_planilha_qgis)
        btn2.grid(row=3, column=1)
        
        # Frame para filtros (ROTA e LOCALIDADE lado a lado)
        frame_filtros = tk.Frame(frame_campos, bg=self.bg_color)
        frame_filtros.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        frame_filtros.columnconfigure(0, weight=1)
        frame_filtros.columnconfigure(1, weight=1)
        
        # FILTRAR POR ROTA (esquerda)
        frame_rota = tk.Frame(frame_filtros, bg=self.bg_color)
        frame_rota.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        label_rota = tk.Label(frame_rota, text="ROTA (opcional)", 
                         font=("Arial", 8, "bold"),
                         bg=self.bg_color, fg=self.fg_color)
        label_rota.pack(anchor="w", pady=(0, 3))
        
        entry_rota_container = tk.Frame(frame_rota, bg=self.bg_color)
        entry_rota_container.pack(fill="x")
        
        entry_rota = tk.Entry(entry_rota_container, textvariable=self.rota_filtro_var,
                         bg=self.entry_bg, fg=self.entry_fg,
                         insertbackground=self.fg_color, relief="flat", bd=0,
                         highlightthickness=0, font=("Arial", 9))
        entry_rota.pack(fill="x", ipady=4)
        
        entry_rota_line = tk.Frame(entry_rota_container, bg="#666666", height=2)
        entry_rota_line.pack(fill="x")
        
        # FILTRAR POR LOCALIDADE (direita)
        frame_localidade = tk.Frame(frame_filtros, bg=self.bg_color)
        frame_localidade.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        label_localidade = tk.Label(frame_localidade, text="LOCALIDADE (opcional)", 
                         font=("Arial", 8, "bold"),
                         bg=self.bg_color, fg=self.fg_color)
        label_localidade.pack(anchor="w", pady=(0, 3))
        
        entry_localidade_container = tk.Frame(frame_localidade, bg=self.bg_color)
        entry_localidade_container.pack(fill="x")
        
        entry_localidade = tk.Entry(entry_localidade_container, textvariable=self.localidade_filtro_var,
                         bg=self.entry_bg, fg=self.entry_fg,
                         insertbackground=self.fg_color, relief="flat", bd=0,
                         highlightthickness=0, font=("Arial", 9))
        entry_localidade.pack(fill="x", ipady=4)
        
        entry_localidade_line = tk.Frame(entry_localidade_container, bg="#666666", height=2)
        entry_localidade_line.pack(fill="x")
        
        # ARQUIVO DE SAÍDA
        label3 = tk.Label(frame_campos, text="ARQUIVO DE SAÍDA", 
                         font=("Arial", 9, "bold"),
                         bg=self.bg_color, fg=self.fg_color)
        label3.grid(row=5, column=0, sticky="w", pady=(10, 5))
        
        entry3_container = tk.Frame(frame_campos, bg=self.bg_color)
        entry3_container.grid(row=6, column=0, padx=(0, 10), sticky="ew")
        
        entry3 = tk.Entry(entry3_container, textvariable=self.arquivo_saida_var, width=50,
                         bg=self.entry_bg, fg=self.entry_fg,
                         insertbackground=self.fg_color, relief="flat", bd=0,
                         highlightthickness=0)
        entry3.pack(ipady=5)
        
        entry3_line = tk.Frame(entry3_container, bg="#666666", height=2)
        entry3_line.pack(fill="x")
        
        btn3 = self.criar_botao_procurar(frame_campos, self.procurar_arquivo_saida)
        btn3.grid(row=6, column=1)
        
        # Frame para os botões de ação
        frame_botoes = tk.Frame(self.root, bg=self.bg_color)
        frame_botoes.pack(pady=20)
        
        # Botão Converter - com borda cinza e linha azul na base
        btn_converter_outer = tk.Frame(frame_botoes, bg="#666666", padx=2, pady=2)
        btn_converter_outer.grid(row=0, column=0, padx=20)
        
        btn_converter_container = tk.Frame(btn_converter_outer, bg=self.bg_color)
        btn_converter_container.pack()
        
        btn_converter = tk.Button(btn_converter_container, text="CONVERTER", 
                                  command=self.converter,
                                  width=15, height=2, font=("Arial", 10, "bold"),
                                  bg=self.bg_color, fg=self.fg_color,
                                  relief="flat", bd=0, cursor="hand2",
                                  activebackground="#3c3c3c", activeforeground=self.fg_color,
                                  highlightthickness=0)
        btn_converter.pack()
        
        linha_azul = tk.Frame(btn_converter_container, bg="#0078d4", height=3)
        linha_azul.pack(fill="x")
        
        # Botão Cancelar - com borda cinza e linha laranja na base
        btn_cancelar_outer = tk.Frame(frame_botoes, bg="#666666", padx=2, pady=2)
        btn_cancelar_outer.grid(row=0, column=1, padx=20)
        
        btn_cancelar_container = tk.Frame(btn_cancelar_outer, bg=self.bg_color)
        btn_cancelar_container.pack()
        
        btn_cancelar = tk.Button(btn_cancelar_container, text="CANCELAR", 
                                command=self.root.quit,
                                width=15, height=2, font=("Arial", 10, "bold"),
                                bg=self.bg_color, fg=self.fg_color,
                                relief="flat", bd=0, cursor="hand2",
                                activebackground="#3c3c3c", activeforeground=self.fg_color,
                                highlightthickness=0)
        btn_cancelar.pack()
        
        linha_laranja = tk.Frame(btn_cancelar_container, bg="#ff6600", height=3)
        linha_laranja.pack(fill="x")
    
    def criar_botao_procurar(self, parent, command):
        """Cria um botão PROCURAR com borda cinza e linha amarela na base"""
        outer = tk.Frame(parent, bg="#666666", padx=2, pady=2)
        
        container = tk.Frame(outer, bg=self.bg_color)
        container.pack()
        
        btn = tk.Button(container, text="PROCURAR", command=command,
                       width=12, height=1, font=("Arial", 9),
                       bg=self.bg_color, fg=self.fg_color,
                       relief="flat", bd=0, cursor="hand2",
                       activebackground="#3c3c3c", activeforeground=self.fg_color,
                       highlightthickness=0)
        btn.pack()
        
        linha_amarela = tk.Frame(container, bg="#ffd700", height=3)
        linha_amarela.pack(fill="x")
        
        return outer
    
    def procurar_planilha_online(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione a Planilha Online de Recadastramento",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if arquivo:
            self.planilha_online_var.set(arquivo)
            
    def procurar_planilha_qgis(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione a Planilha QGIS",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if arquivo:
            self.planilha_qgis_var.set(arquivo)
            
    def procurar_arquivo_saida(self):
        arquivo = filedialog.asksaveasfilename(
            title="Selecione o Arquivo de Saída",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if arquivo:
            self.arquivo_saida_var.set(arquivo)
    
    def detectar_sexo(self, nome):
        """Detecta o sexo baseado no nome do cliente usando múltiplas estratégias"""
        if not nome or nome == '0' or nome == 'nan':
            return '01 - MASCULINO'
        
        nome_upper = str(nome).upper().strip()
        palavras = nome_upper.split()
        
        if not palavras:
            return '01 - MASCULINO'
        
        primeiro_nome = palavras[0]
        
        # 1. Tentar biblioteca gender_guesser se disponível
        if HAS_GENDER_LIB:
            try:
                resultado = GENDER_DETECTOR.get_gender(primeiro_nome.lower())
                if resultado in ['female', 'mostly_female']:
                    return '02 - FEMININO'
                elif resultado in ['male', 'mostly_male']:
                    return '01 - MASCULINO'
            except:
                pass
        
        # 2. Verificar nas listas de nomes conhecidos
        if primeiro_nome in self.nomes_femininos:
            return '02 - FEMININO'
        
        if primeiro_nome in self.nomes_masculinos:
            return '01 - MASCULINO'
        
        # 3. Heurísticas baseadas em terminações comuns
        # Feminino: terminações típicas
        if primeiro_nome.endswith(('IA', 'INA', 'IANA', 'ANA', 'ELLA', 'ELLE', 'ETTE')):
            return '02 - FEMININO'
        
        # Nomes terminados em A (excluindo sobrenomes comuns)
        if primeiro_nome.endswith('A'):
            sobrenomes_exc = {'GARCIA', 'SILVA', 'COSTA', 'GAMA', 'LIMA', 'SOUZA', 'MIRANDA', 
                             'GUIMARAES', 'MOURA', 'VIANA', 'CUNHA', 'ROCHA', 'FARIA', 'MOTA'}
            if primeiro_nome not in sobrenomes_exc and len(primeiro_nome) > 3:
                return '02 - FEMININO'
        
        # Masculino: terminações típicas
        if primeiro_nome.endswith(('O', 'OR', 'OS', 'US', 'IS', 'EL', 'ON', 'AN')):
            return '01 - MASCULINO'
        
        # Padrão: masculino
        return '01 - MASCULINO'
    
    def converter(self):
        # Validar se os arquivos foram selecionados
        planilha_online = self.planilha_online_var.get()
        planilha_qgis = self.planilha_qgis_var.get()
        arquivo_saida = self.arquivo_saida_var.get()
        
        if not planilha_online:
            messagebox.showerror("Erro", "Por favor, selecione a Planilha Online de Recadastramento!")
            return
            
        if not planilha_qgis:
            messagebox.showerror("Erro", "Por favor, selecione a Planilha QGIS!")
            return
            
        if not arquivo_saida:
            messagebox.showerror("Erro", "Por favor, selecione o Arquivo de Saída!")
            return
        
        try:
            # Processar as planilhas
            self.processar_planilhas(planilha_online, planilha_qgis, arquivo_saida)
            messagebox.showinfo("Sucesso", f"Conversão concluída com sucesso!\n\nArquivo salvo em:\n{arquivo_saida}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar as planilhas:\n\n{str(e)}")
    
    def processar_planilhas(self, arquivo_online, arquivo_qgis, arquivo_saida):
        """Processa as planilhas e gera o arquivo de saída"""
        
        # Ler as planilhas
        df = pd.read_csv(arquivo_online)
        df = df.fillna(0).map(remover_acentos)
        df2 = pd.read_csv(arquivo_qgis)
        
        # Aplicar filtros se especificados
        rota_filtro = self.rota_filtro_var.get().strip()
        localidade_filtro = self.localidade_filtro_var.get().strip()
        
        if rota_filtro:
            df['ROTA_STR'] = df['ROTA'].astype(str).str.replace('.0', '')
            df = df[df['ROTA_STR'] == rota_filtro]
            
            if df.empty:
                raise ValueError(f"Nenhum registro encontrado para a rota '{rota_filtro}'!")
        
        if localidade_filtro:
            df['LOCALIDADE_STR'] = df['LOCALIDADE'].astype(str)
            df = df[df['LOCALIDADE_STR'].str[:3] == localidade_filtro[:3]]
            
            if df.empty:
                raise ValueError(f"Nenhum registro encontrado para a localidade '{localidade_filtro}'!")
        
        header = ['ALTERAR', 'ORDEM1', 'ORDEM2', 'LOCAL', 'SETOR', 'QUADRA', 'LOTE', 
                 'SUBLOTE', 'TESTADA', 'SEQUENCIA', 'ROTA', 'MATRICULA', 'COD_LOG', 
                 'BAIRRO', 'CEP_GSAN', 'NUMERO', 'COMPLEMENTO', 'NOME', 'CPF', 'CNPJ', 
                 'V_CPF', 'V_CNPJ', 'COD_CLIENTE', 'EMAIL', 'RG', 'DATA_EXP', 'SEXO', 
                 'MAE', 'DATA_NASC','TIPO_CLIENTE', 'TIPO_HAB', 'RES', 'COM', 'MUN', 
                 'EST', 'FED', 'DDD', 'TELEFONE', 'CX', 'CY']
        
        with open(arquivo_saida, mode="w", newline="", encoding="utf-8") as arquivo_relatorio:
            writer = csv.writer(arquivo_relatorio)
            writer.writerow(header)
            
            for i in df.index:
                
                ordem = i+1
                matricula_raw = df['MATRÍCULA DO IMÓVEL'][i]
                
                # Tratar matrícula NULL ou vazia
                try:
                    if pd.isna(matricula_raw) or matricula_raw == 0 or matricula_raw == '' or str(matricula_raw).strip() == '':
                        matricula = 0
                    else:
                        matricula = int(float(matricula_raw))
                except:
                    matricula = 0
                
                

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
                
                # Detectar sexo baseado no nome
                sexo = self.detectar_sexo(nomeCliente)
                
                cpf = int(df['CPF'][i])   
                if cpf > 0: 
                    vcpf = 1
                else:
                    vcpf = 1
                ocorCad = str(df['OCORRENCIA DE CADASTRO'][i])
                if ocorCad == 'Terreno vazio':
                    tipoHab =  0
                else:
                    tipoHab =  1
                dataExp = str(df['DATA DE EXPEDIÇÃO'][i])
                nomeMae = str(df['NOME DA MÃE'][i])
                dataNasc = str(df['DATA DE NASCIMENTO'][i])    
                rgCliente = str(df['RG'][i]).replace('.0','')
                emailCliente = str(df['E-MAIL'][i])
                telefone = str(df['TELEFONE DE CONTATO COM DDD'][i])
                if telefone == '0' or telefone == '':
                    ddd = '0'
                    telefone = '0'
                else:
                    telefone_str = str(telefone)
                    ddd = telefone_str[:2].replace('0.','0')
                    telefone = telefone_str[2:].replace('.0','')
                if econRes + econCom + econMun + econEst + econFed + econInd == 0:
                    econRes = 1
                
                # Definir código do cliente
                # Se tem matrícula mas não tem nome nem CPF, código = 1
                if matricula and matricula > 0:
                    nome_vazio = (not nomeCliente or nomeCliente == '0' or nomeCliente.strip() == '')
                    cpf_vazio = (cpf == 0)
                    if nome_vazio and cpf_vazio:
                        cod_cliente = 1
                    else:
                        cod_cliente = 0
                else:
                    cod_cliente = 0
                
                quadra = 0
                latitude = 0
                longitude = 0
                encontrado = False
                
                # Buscar dados do QGIS - primeiro por matrícula, depois por sequência
                if matricula and matricula > 0:
                    matricula_str = str(int(matricula)).strip()
                    for j in df2.index:
                        imv_id = str(df2['imv_id'][j]).strip()
                        # Remover .0 se existir
                        if '.0' in imv_id:
                            imv_id = imv_id.replace('.0', '')
                        
                        if imv_id == matricula_str:
                            latitude = str(df2['latitude'][j])
                            longitude = str(df2['longitude'][j])
                            quadra = str(df2['quadra'][j]).replace('.0', '')
                            encontrado = True
                            break
                
                # Se não encontrou por matrícula, busca por sequência
                if not encontrado:
                    numVisita_str = str(numVisita).strip()
                    for j in df2.index:
                        seq_id = str(df2['seq_id'][j]).strip().replace('.0', '')
                        
                        if seq_id == numVisita_str:
                            latitude = str(df2['latitude'][j])
                            longitude = str(df2['longitude'][j])
                            quadra = str(df2['quadra'][j]).replace('.0', '')
                            break
                
                row = [1, ordem, ordem, localidade, setor, quadra, numVisita, 0, 0, 
                      numVisita, rota, matricula, 0, '', 0, numImovel, 0, nomeCliente, 
                      cpf, cnpj, vcpf, vcnpj, cod_cliente, emailCliente, rgCliente, dataExp, sexo, 
                      nomeMae, dataNasc, tipoCliente, tipoHab, econRes, econCom, econMun, 
                      econEst, econFed, ddd, telefone, latitude, longitude]
                writer.writerow(row)


def main():
    root = tk.Tk()
    app = ConversorPlanilhas(root)
    root.mainloop()


if __name__ == "__main__":
    main()
