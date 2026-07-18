import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import csv
from pathlib import Path
import threading
import os
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import time
import zipfile
import urllib.request
import platform
import subprocess
import shutil
import json
import ssl

def remover_acentos(texto):
    """Remove acentos de uma string"""
    if not isinstance(texto, str):
        return texto
    
    acentos = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C'
    }
    
    for acento, sem_acento in acentos.items():
        texto = texto.replace(acento, sem_acento)
    return texto

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

def cpf_ok(cpf):
    """Formata CPF com zeros à esquerda"""
    ncpf = len(cpf)
    while ncpf < 11:
        cpf = "0" + cpf
        ncpf = ncpf + 1
    return cpf

def rg_ok(rg):
    """Formata RG com zeros à esquerda"""
    nrg = len(rg)
    while nrg < 13:
        rg = "0" + rg
        nrg = nrg + 1
    return rg

class PlanilhasApp:
    def __init__(self, root, initial_theme='light'):
        self.root = root
        self.window_width = 1366
        self.window_height = 768
        self.root.title("SmartSync Workspace")
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.minsize(self.window_width, self.window_height)
        self.root.maxsize(self.window_width, self.window_height)
        self.root.resizable(False, False)
        self.center_window()

        self.current_theme = 'aurora'

        # URL base dinâmica do GSAN (compartilhada por todas as abas)
        self.gsan_base_url_var = tk.StringVar(value='http://g1.caema.ma.gov.br/gsan/')

        self.workspace_definitions = [
            {
                'key': 'online',
                'title': 'Converter Online',
                'description': 'CSV da planilha online para QGIS',
                'icon': '🌐',
                'summary': 'Transforme a extração online em um arquivo limpo para mapeamento.',
                'chips': ['Entrada CSV', 'Saída QGIS', 'Fluxo rápido'],
                'steps': ['Selecionar entrada e saída', 'Aplicar filtros opcionais', 'Executar a conversão']
            },
            {
                'key': 'converter',
                'title': 'Converter Base',
                'description': 'Cruzar e padronizar planilhas',
                'icon': '🧭',
                'summary': 'Cruze a base Google com o CSV do QGIS e gere a saída cadastral.',
                'chips': ['CEP', 'Padronização', 'Relatório'],
                'steps': ['Escolher os CSVs', 'Definir município e filtros', 'Gerar o relatório final']
            },
            {
                'key': 'consultar',
                'title': 'Consultar Cliente',
                'description': 'Pesquisa automatizada no GSAN',
                'icon': '🔎',
                'summary': 'Automatize a busca de códigos de cliente diretamente no GSAN.',
                'chips': ['GSAN', 'Consulta', 'Headless'],
                'steps': ['Informar login', 'Selecionar planilha convertida', 'Iniciar a consulta']
            },
            {
                'key': 'criar',
                'title': 'Criar Cliente',
                'description': 'Gerar novo código de cliente',
                'icon': '👤',
                'summary': 'Crie clientes em lote com acompanhamento do processamento.',
                'chips': ['Cadastro', 'Lote', 'Monitorado'],
                'steps': ['Configurar acesso', 'Escolher arquivos', 'Executar a criação']
            },
            {
                'key': 'rotas',
                'title': 'Criar Rotas',
                'description': 'Cadastrar rotas em lote',
                'icon': '🛣️',
                'summary': 'Cadastre sequências de rota com parâmetros operacionais centralizados.',
                'chips': ['Roteiro', 'Lote', 'Operação'],
                'steps': ['Definir login', 'Ajustar parâmetros', 'Criar rotas']
            },
            {
                'key': 'quadras',
                'title': 'Criar Quadras',
                'description': 'Cadastrar quadras em lote',
                'icon': '🏘️',
                'summary': 'Mantenha a criação de quadras em um fluxo simples e consistente.',
                'chips': ['Quadras', 'GSAN', 'Produtivo'],
                'steps': ['Informar credenciais', 'Selecionar base', 'Executar o cadastro']
            },
            {
                'key': 'matriculas',
                'title': 'Criar Matrículas',
                'description': 'Automação de matrículas',
                'icon': '📋',
                'summary': 'Automatize matrículas com o mesmo padrão visual dos demais módulos.',
                'chips': ['Matrículas', 'Saída CSV', 'Assistido'],
                'steps': ['Configurar login', 'Selecionar entrada e saída', 'Rodar a automação']
            },
            {
                'key': 'alterar_roteirizacao',
                'title': 'Alterar Roteiro',
                'description': 'Atualizar roteirização',
                'icon': '🧩',
                'summary': 'Atualize roteirizações em lote com feedback claro durante o processo.',
                'chips': ['Roteirização', 'Lote', 'Controle'],
                'steps': ['Escolher arquivos', 'Informar login', 'Aplicar alterações']
            },
            {
                'key': 'atualizar_endereco',
                'title': 'Atualizar Endereço',
                'description': 'Atualizar endereço em lote',
                'icon': '📍',
                'summary': 'Centralize a revisão de endereços em uma experiência mais limpa.',
                'chips': ['Endereço', 'GSAN', 'Revisão'],
                'steps': ['Selecionar base', 'Configurar acesso', 'Atualizar endereços']
            },
            {
                'key': 'alterar_cliente',
                'title': 'Alterar Cliente',
                'description': 'Trocar cliente da matrícula',
                'icon': '🔁',
                'summary': 'Altere o cliente vinculado à matrícula com rastreabilidade na saída.',
                'chips': ['Cliente', 'Matrícula', 'Saída CSV'],
                'steps': ['Escolher entrada e saída', 'Preencher login', 'Executar a troca']
            },
        ]
        self.workspace_meta = {item['key']: item for item in self.workspace_definitions}
        
        # Definir caminho base para recursos
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(__file__)
        
        # Definir ícone da janela (barra de tarefas e título)
        try:
            icon_path = os.path.join(self.base_path, 'smartsync_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                # Para Windows - garantir ícone na barra de tarefas
                self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o ícone: {e}")
            pass
        
        # Estilo moderno
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.apply_theme('aurora')
        
        self.root.configure(bg=self.bg_color)
        
        # Frame principal com padding
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Frame do cabeçalho
        header_frame = tk.Frame(
            main_frame,
            bg=self.header_bg,
            highlightthickness=1,
            highlightbackground=self.border_color,
            bd=0
        )
        header_frame.pack(fill=tk.X, pady=(0, 16))

        title_frame = tk.Frame(header_frame, bg=self.header_bg)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=24, pady=22)

        badge_label = tk.Label(
            title_frame,
            text="SINGLE TAB WORKSPACE",
            font=('Segoe UI', 9, 'bold'),
            bg=self.accent_soft,
            fg=self.accent_color,
            padx=12,
            pady=4
        )
        badge_label.pack(anchor=tk.W, pady=(0, 8))
        
        title_label = ttk.Label(title_frame, text="SmartSync Cadastral", 
                                style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            title_frame,
            text="Interface repaginada em guia única, com navegação lateral contínua e visual moderno inspirado em Gemini/KDE.",
            font=('Segoe UI', 10),
            bg=self.header_bg,
            fg=self.muted_text
        )
        subtitle.pack(anchor=tk.W, pady=(4, 10))

        meta_frame = tk.Frame(title_frame, bg=self.header_bg)
        meta_frame.pack(anchor=tk.W)

        for meta_text in ("1366x768 fixo", "1 guia ativa", "layout em cartões"):
            tk.Label(
                meta_frame,
                text=meta_text,
                font=('Segoe UI', 8, 'bold'),
                bg=self.tab_active_bg,
                fg=self.text_color,
                padx=12,
                pady=4
            ).pack(side=tk.LEFT, padx=(0, 8))

        summary_frame = tk.Frame(header_frame, bg=self.header_bg)
        summary_frame.pack(side=tk.RIGHT, padx=24, pady=22)

        stats_frame = tk.Frame(summary_frame, bg=self.header_bg)
        stats_frame.pack(anchor=tk.E, pady=(0, 12))

        for value, label in (
            (str(len(self.workspace_definitions)), "módulos"),
            ("1", "guia"),
            ("Pronto", "para VS Code"),
        ):
            stat_card = tk.Frame(
                stats_frame,
                bg=self.hero_bg,
                highlightthickness=1,
                highlightbackground=self.border_color,
                bd=0
            )
            stat_card.pack(side=tk.LEFT, padx=(10, 0))
            tk.Label(
                stat_card,
                text=value,
                font=('Segoe UI', 11, 'bold'),
                bg=self.hero_bg,
                fg=self.text_color
            ).pack(padx=14, pady=(10, 2))
            tk.Label(
                stat_card,
                text=label,
                font=('Segoe UI', 8),
                bg=self.hero_bg,
                fg=self.muted_text
            ).pack(padx=14, pady=(0, 10))

        config_btn_frame = tk.Frame(summary_frame, bg=self.header_bg)
        config_btn_frame.pack(anchor=tk.E)

        self.config_driver_btn = tk.Button(
            config_btn_frame,
            text="Configurar WebDriver",
            font=('Segoe UI', 10, 'bold'),
            width=22,
            height=1,
            bg=self.accent_color,
            fg='white',
            relief=tk.FLAT,
            activebackground=self.hover_color,
            activeforeground='white',
            bd=0,
            padx=14,
            pady=10,
            cursor='hand2',
            command=self.open_driver_config
        )
        self.config_driver_btn.pack()
        
        tk.Label(
            config_btn_frame,
            text="Drivers, navegador padrão e download automático",
            font=('Segoe UI', 8),
            bg=self.header_bg,
            fg=self.muted_text
        ).pack(pady=(6, 0))
        
        # ===== CRIAR NOTEBOOK (GUIA UNICA) =====
        self.notebook = ttk.Notebook(main_frame, style='Smart.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.workspace_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.workspace_tab, text="Workspace SmartSync")

        self.page_frames = {}
        self.page_buttons = {}
        self.build_workspace_shell()
        
        # Construir interface de cada aba
        self.build_online_tab()
        self.build_converter_tab()
        self.build_consultar_tab()
        self.build_criar_tab()
        self.build_rotas_tab()
        self.build_quadras_tab()
        self.build_matriculas_tab()
        self.build_alterar_roteirizacao_tab()
        self.build_atualizar_endereco_tab()
        self.build_alterar_cliente_tab()
        self.show_workspace_page('online')
        
        self.processing = False
        self.total_records = 0
        self.municipios_data = {}
        self.selected_cep_id = None
        
        # Variáveis para conversão online
        self.online_running = False
        
        # Variáveis para consulta de clientes
        self.driver = None
        self.consulta_running = False
        self.driver_path = None  # Caminho do driver do navegador
        
        # Variáveis de configuração do WebDriver
        self.driver_type_var = tk.StringVar(value='Edge')  # Edge por padrão
        self.driver_manual_path_var = tk.StringVar()
        
        # Variáveis para criar código de cliente
        self.criar_running = False
        
        # Variáveis para criar rotas
        self.rotas_running = False
        
        # Variáveis para criar quadras
        self.quadras_running = False
        
        # Variáveis para criar matrículas
        self.matriculas_running = False

        # Variáveis para alteração de matrícula
        self.alterar_roteirizacao_running = False
        self.atualizar_endereco_running = False
        self.alterar_cliente_running = False
        
        # Carregar base de municípios
        self.load_municipios_database()
        
        # Verificar drivers na inicialização
        self.check_drivers_on_startup()

    def center_window(self):
        """Centraliza a janela principal na tela."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max((screen_width - self.window_width) // 2, 0)
        y = max((screen_height - self.window_height) // 2, 0)
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def build_workspace_shell(self):
        """Cria a casca da guia única com navegação lateral e páginas internas."""
        shell = tk.Frame(self.workspace_tab, bg=self.bg_color)
        shell.pack(fill=tk.BOTH, expand=True)

        nav_panel = tk.Frame(
            shell,
            bg=self.panel_bg,
            width=250,
            highlightthickness=1,
            highlightbackground=self.border_color,
            bd=0
        )
        nav_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        nav_panel.pack_propagate(False)

        content_panel = tk.Frame(shell, bg=self.bg_color)
        content_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            nav_panel,
            text="Modulos",
            font=('Segoe UI', 16, 'bold'),
            bg=self.panel_bg,
            fg=self.text_color
        ).pack(anchor=tk.W, padx=18, pady=(18, 4))

        tk.Label(
            nav_panel,
            text="Tudo continua em um unico arquivo Python,\nmas agora em uma interface mais atual.",
            font=('Segoe UI', 9),
            justify=tk.LEFT,
            bg=self.panel_bg,
            fg=self.muted_text
        ).pack(anchor=tk.W, padx=18, pady=(0, 14))

        definitions = [
            ('online', 'Converter Online', 'CSV da planilha online para QGIS'),
            ('converter', 'Converter Base', 'Cruzar e padronizar planilhas'),
            ('consultar', 'Consultar Cliente', 'Pesquisa automatizada no GSAN'),
            ('criar', 'Criar Cliente', 'Gerar novo codigo de cliente'),
            ('rotas', 'Criar Rotas', 'Cadastrar rotas em lote'),
            ('quadras', 'Criar Quadras', 'Cadastrar quadras em lote'),
            ('matriculas', 'Criar Matriculas', 'Automacao de matriculas'),
            ('alterar_roteirizacao', 'Alterar Roteiro', 'Atualizar roteirizacao'),
            ('atualizar_endereco', 'Atualizar Endereco', 'Atualizar endereco em lote'),
            ('alterar_cliente', 'Alterar Cliente', 'Trocar cliente da matricula'),
        ]

        frame_attrs = {
            'online': 'tab_online',
            'converter': 'tab_converter',
            'consultar': 'tab_consultar',
            'criar': 'tab_criar',
            'rotas': 'tab_rotas',
            'quadras': 'tab_quadras',
            'matriculas': 'tab_matriculas',
            'alterar_roteirizacao': 'tab_alterar_roteirizacao',
            'atualizar_endereco': 'tab_atualizar_endereco',
            'alterar_cliente': 'tab_alterar_cliente',
        }

        for key, title, description in definitions:
            button = tk.Button(
                nav_panel,
                text=f"{title}\n{description}",
                font=('Segoe UI', 9, 'bold'),
                justify=tk.LEFT,
                anchor='w',
                wraplength=190,
                bg=self.panel_bg,
                fg=self.muted_text,
                activebackground=self.tab_active_bg,
                activeforeground=self.text_color,
                relief=tk.FLAT,
                bd=0,
                padx=14,
                pady=10,
                cursor='hand2',
                command=lambda page_key=key: self.show_workspace_page(page_key)
            )
            button.pack(fill=tk.X, padx=12, pady=4)
            self.page_buttons[key] = button

            page_frame = tk.Frame(content_panel, bg=self.bg_color)
            page_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.page_frames[key] = page_frame
            setattr(self, frame_attrs[key], page_frame)

        tk.Label(
            nav_panel,
            text="Dica: use a lateral para alternar modulos sem abrir novas guias.",
            font=('Segoe UI', 8),
            justify=tk.LEFT,
            wraplength=190,
            bg=self.panel_bg,
            fg=self.muted_text
        ).pack(side=tk.BOTTOM, anchor=tk.W, padx=18, pady=18)

    def show_workspace_page(self, page_key):
        """Exibe a página selecionada dentro da guia única."""
        target_page = self.page_frames.get(page_key)
        if not target_page:
            return

        target_page.tkraise()

        for key, button in self.page_buttons.items():
            if key == page_key:
                button.configure(bg=self.tab_active_bg, fg=self.text_color)
            else:
                button.configure(bg=self.panel_bg, fg=self.muted_text)
    
    def check_drivers_on_startup(self):
        """Verifica e tenta baixar drivers na inicialização"""
        drivers_dir = os.path.join(os.path.dirname(__file__), 'drivers')
        os.makedirs(drivers_dir, exist_ok=True)
        
        # Verificar drivers inclusos no executável (base_path para PyInstaller)
        # Tentar buscar na estrutura do GSAN_APP_DEV primeiro
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        gsan_drivers_dir = os.path.join(project_root, 'GSAN_APP_DEV', 'drivers_inclusos')
        included_drivers_dir = os.path.join(self.base_path, 'drivers_inclusos')
        
        # Verificar se existe algum driver (prioridade: inclusos GSAN -> inclusos local -> locais)
        edge_driver = None
        chrome_driver = None
        gecko_driver = None
        
        # Verificar geckodriver (prioridade máxima - firefox/)
        if os.path.exists(os.path.join(gsan_drivers_dir, 'firefox', 'geckodriver.exe')):
            gecko_driver = os.path.join(gsan_drivers_dir, 'firefox', 'geckodriver.exe')
        elif os.path.exists(os.path.join(included_drivers_dir, 'firefox', 'geckodriver.exe')):
            gecko_driver = os.path.join(included_drivers_dir, 'firefox', 'geckodriver.exe')
        elif os.path.exists(os.path.join(included_drivers_dir, 'geckodriver.exe')):
            gecko_driver = os.path.join(included_drivers_dir, 'geckodriver.exe')
        elif os.path.exists(os.path.join(drivers_dir, 'geckodriver.exe')):
            gecko_driver = os.path.join(drivers_dir, 'geckodriver.exe')
        
        # Verificar chromedriver (chrome/)
        if os.path.exists(os.path.join(gsan_drivers_dir, 'chrome', 'chromedriver.exe')):
            chrome_driver = os.path.join(gsan_drivers_dir, 'chrome', 'chromedriver.exe')
        elif os.path.exists(os.path.join(included_drivers_dir, 'chrome', 'chromedriver.exe')):
            chrome_driver = os.path.join(included_drivers_dir, 'chrome', 'chromedriver.exe')
        elif os.path.exists(os.path.join(included_drivers_dir, 'chromedriver.exe')):
            chrome_driver = os.path.join(included_drivers_dir, 'chromedriver.exe')
        elif os.path.exists(os.path.join(drivers_dir, 'chromedriver.exe')):
            chrome_driver = os.path.join(drivers_dir, 'chromedriver.exe')
        
        # Verificar edgedriver
        if os.path.exists(os.path.join(gsan_drivers_dir, 'msedgedriver.exe')):
            edge_driver = os.path.join(gsan_drivers_dir, 'msedgedriver.exe')
        elif os.path.exists(os.path.join(included_drivers_dir, 'msedgedriver.exe')):
            edge_driver = os.path.join(included_drivers_dir, 'msedgedriver.exe')
        elif os.path.exists(os.path.join(drivers_dir, 'msedgedriver.exe')):
            edge_driver = os.path.join(drivers_dir, 'msedgedriver.exe')
        
        # Definir driver padrão (priorizar geckodriver se disponível)
        if gecko_driver:
            self.driver_path = gecko_driver
            self.driver_type_var.set('Firefox')
            print(f"✅ GeckoDriver encontrado: {gecko_driver}")
        elif edge_driver:
            self.driver_path = edge_driver
            self.driver_type_var.set('Edge')
            print(f"✅ EdgeDriver encontrado: {edge_driver}")
        elif chrome_driver:
            self.driver_path = chrome_driver
            self.driver_type_var.set('Chrome')
            print(f"✅ ChromeDriver encontrado: {chrome_driver}")
        else:
            print("⚠️ Nenhum driver encontrado. Use o botão de configuração para baixar.")
    
    def build_online_tab(self):
        """Constrói a interface da aba de conversão de planilha online"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_online)
        
        # ===== SEÇÃO ARQUIVOS =====
        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        
        # Planilha Online (entrada)
        self.online_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha Online (CSV):", self.online_input_path, 
                              self.browse_online_input, "(arquivo CSV da planilha online)")
        
        # Planilha de Saída
        self.online_output_path = tk.StringVar()
        self.create_file_input(files_section, "Arquivo de Saída:", self.online_output_path, 
                              self.browse_online_output, "(arquivo CSV simplificado para QGIS)")
        
        # ===== SEÇÃO FILTROS =====
        filters_section = self.create_section(tab_frame, "🔍 FILTROS OPCIONAIS")
        
        # Container para filtros
        filters_container = tk.Frame(filters_section, bg=self.section_bg)
        filters_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Filtro Localidade
        loc_frame = tk.Frame(filters_container, bg=self.section_bg)
        loc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(loc_frame, text="Localidade:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.online_localidade_var = tk.StringVar()
        loc_entry = ttk.Entry(loc_frame, textvariable=self.online_localidade_var, width=15)
        loc_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(loc_frame, text="(ex: 001)", style='Hint.TLabel').pack(side=tk.LEFT)
        
        # Filtro Rota
        rota_frame = tk.Frame(filters_container, bg=self.section_bg)
        rota_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rota_frame, text="Rota:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.online_rota_var = tk.StringVar()
        rota_entry = ttk.Entry(rota_frame, textvariable=self.online_rota_var, width=15)
        rota_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(rota_frame, text="(ex: 123)", style='Hint.TLabel').pack(side=tk.LEFT)
        
        # ===== INFORMAÇÕES =====
        info_section = self.create_section(tab_frame, "ℹ️ INFORMAÇÕES")
        
        info_container = tk.Frame(info_section, bg=self.section_bg)
        info_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        info_text = (
            "Esta ferramenta converte a planilha online para o formato QGIS:\n\n"
            "📍 Separa coordenadas em latitude e longitude\n"
            "🏷️ Extrai: MATRÍCULA DO IMÓVEL → imv_id\n"
            "🛣️ Extrai: ROTA → rot_id\n"
            "🔢 Extrai: Nº DA VISITA → seq_id\n"
            "📌 Extrai: LOCALIDADE (apenas número) → localidade\n"
            "🏘️ Extrai: SETOR → Setor\n\n"
            "✅ Saída: [latitude,longitude,imv_id,rot_id,seq_id,localidade,Setor]"
        )
        
        ttk.Label(info_container, text=info_text, 
                 style='Hint.TLabel', justify=tk.LEFT).pack(anchor=tk.W, pady=5)
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.online_progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                              style='Custom.Horizontal.TProgressbar',
                                              maximum=100, value=0)
        self.online_progress.pack(fill=tk.X)
        
        # Label de status
        self.online_status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                            style='Status.TLabel')
        self.online_status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Converter
        self.online_btn = self.create_modern_button(button_frame, "▶ Converter", 
                                                    self.iniciar_online, '#28a745', '#218838')
        self.online_btn.pack(fill=tk.X, pady=4)
        
        # Botão Cancelar
        self.cancel_online_btn = self.create_modern_button(button_frame, "⏹ Cancelar", 
                                                           self.cancelar_online, '#dc3545', '#c82333')
        self.cancel_online_btn.pack(fill=tk.X, pady=4)
    
    def browse_online_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha Online",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.online_input_path.set(filename)
    
    def browse_online_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar Planilha Convertida",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.online_output_path.set(filename)
    
    def iniciar_online(self):
        """Inicia a conversão da planilha online"""
        # Validações
        if not self.online_input_path.get():
            messagebox.showerror("Erro", "Selecione a planilha online!")
            return
        
        if not self.online_output_path.get():
            messagebox.showerror("Erro", "Selecione o arquivo de saída!")
            return
        
        # Executar conversão em thread separada
        self.online_running = True
        thread = threading.Thread(target=self.process_online_conversion)
        thread.daemon = True
        thread.start()
    
    def cancelar_online(self):
        """Cancela a conversão online"""
        if self.online_running:
            self.online_running = False
            self.root.after(0, lambda: self.online_status_label.config(text="Cancelado pelo usuário"))
    
    def process_online_conversion(self):
        """Processa a conversão da planilha online para formato QGIS"""
        try:
            self.root.after(0, lambda: self.online_status_label.config(text="Carregando planilha..."))
            self.root.after(0, lambda: self.online_progress.config(value=10))
            
            def disable_btn():
                self.online_btn['state'] = 'disabled'
            self.root.after(0, disable_btn)
            
            # Carregar planilha
            df = pd.read_csv(self.online_input_path.get())
            
            self.root.after(0, lambda: self.online_progress.config(value=30))
            
            # Aplicar filtros se fornecidos
            localidade = self.online_localidade_var.get().strip()
            rota = self.online_rota_var.get().strip()
            
            if localidade:
                # Filtrar por localidade (pode estar como número ou texto)
                df = df[df['LOCALIDADE'].astype(str).str.contains(localidade, case=False, na=False)]
                self.root.after(0, lambda: self.online_status_label.config(
                    text=f"Filtrado por localidade: {localidade}"))
            
            if rota:
                # Filtrar por rota
                df = df[df['ROTA'].astype(str).str.contains(rota, case=False, na=False)]
                self.root.after(0, lambda: self.online_status_label.config(
                    text=f"Filtrado por rota: {rota}"))
            
            if df.empty:
                raise ValueError("Nenhum registro encontrado com os filtros aplicados!")
            
            # Verificar se existe aba "coordenadas" ou colunas necessárias
            required_cols = ['MATRÍCULA DO IMÓVEL', 'ROTA', 'Nº DA VISITA', 'LOCALIDADE', 'SETOR']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Colunas faltando na planilha: {', '.join(missing_cols)}")
            
            # Verificar coluna de coordenadas
            coord_col = None
            for possible_name in ['coordenadas', 'Coordenadas', 'COORDENADAS', 'coords', 'Coords']:
                if possible_name in df.columns:
                    coord_col = possible_name
                    break
            
            if not coord_col:
                raise ValueError("Coluna de coordenadas não encontrada! Procure por 'coordenadas', 'Coordenadas' ou similar.")
            
            self.root.after(0, lambda: self.online_status_label.config(text="Processando dados..."))
            self.root.after(0, lambda: self.online_progress.config(value=50))
            
            # Criar DataFrame de saída
            output_data = []
            
            total = len(df)
            for idx, row in df.iterrows():
                if not self.online_running:
                    break
                
                # Separar coordenadas (formato: "latitude,longitude" ou "latitude, longitude")
                coords_str = str(row[coord_col]).strip()
                
                # Tentar separar as coordenadas
                if ',' in coords_str:
                    parts = coords_str.split(',')
                    if len(parts) >= 2:
                        latitude = parts[0].strip()
                        longitude = parts[1].strip()
                    else:
                        latitude = '0'
                        longitude = '0'
                else:
                    latitude = '0'
                    longitude = '0'
                
                # Extrair imv_id (MATRÍCULA DO IMÓVEL)
                imv_id_raw = row['MATRÍCULA DO IMÓVEL']
                if pd.isna(imv_id_raw) or str(imv_id_raw).strip() in ['', 'nan', 'NaN', 'None']:
                    imv_id = ''
                else:
                    # Remover .0 se for float
                    try:
                        imv_id_num = float(imv_id_raw)
                        if imv_id_num.is_integer():
                            imv_id = str(int(imv_id_num))
                        else:
                            imv_id = str(imv_id_raw).strip()
                    except:
                        imv_id = str(imv_id_raw).strip()
                
                # Extrair rot_id (ROTA)
                rot_id_raw = row['ROTA']
                if pd.isna(rot_id_raw) or str(rot_id_raw).strip() in ['', 'nan', 'NaN', 'None']:
                    rot_id = ''
                else:
                    try:
                        rot_id_num = float(rot_id_raw)
                        if rot_id_num.is_integer():
                            rot_id = str(int(rot_id_num))
                        else:
                            rot_id = str(rot_id_raw).strip()
                    except:
                        rot_id = str(rot_id_raw).strip()
                
                # Extrair seq_id (Nº DA VISITA)
                seq_id_raw = row['Nº DA VISITA']
                if pd.isna(seq_id_raw) or str(seq_id_raw).strip() in ['', 'nan', 'NaN', 'None']:
                    seq_id = ''
                else:
                    try:
                        seq_id_num = float(seq_id_raw)
                        if seq_id_num.is_integer():
                            seq_id = str(int(seq_id_num))
                        else:
                            seq_id = str(seq_id_raw).strip()
                    except:
                        seq_id = str(seq_id_raw).strip()
                
                # Extrair localidade (apenas número)
                localidade_raw = str(row['LOCALIDADE']).strip()
                # Extrair apenas números da localidade
                localidade_match = re.search(r'\d+', localidade_raw)
                localidade = localidade_match.group() if localidade_match else '0'
                
                # Extrair Setor
                setor = str(row['SETOR']).strip()
                
                output_data.append({
                    'latitude': latitude,
                    'longitude': longitude,
                    'imv_id': imv_id,
                    'rot_id': rot_id,
                    'seq_id': seq_id,
                    'localidade': localidade,
                    'Setor': setor
                })
                
                # Atualizar progresso
                progress = 50 + int((idx / total) * 40)
                self.root.after(0, lambda p=progress: self.online_progress.config(value=p))
            
            if not self.online_running:
                self.root.after(0, lambda: self.online_status_label.config(text="Cancelado pelo usuário"))
                return
            
            # Criar DataFrame de saída
            df_output = pd.DataFrame(output_data)
            
            self.root.after(0, lambda: self.online_status_label.config(text="Salvando arquivo..."))
            self.root.after(0, lambda: self.online_progress.config(value=90))
            
            # Salvar arquivo
            df_output.to_csv(self.online_output_path.get(), index=False)
            
            self.root.after(0, lambda: self.online_progress.config(value=100))
            self.root.after(0, lambda: self.online_status_label.config(
                text=f"✅ Conversão concluída! {len(df_output)} registros processados"))
            
            messagebox.showinfo("Sucesso", 
                              f"Planilha convertida com sucesso!\n\n"
                              f"Registros processados: {len(df_output)}\n"
                              f"Arquivo salvo em:\n{self.online_output_path.get()}")
            
        except Exception as e:
            self.root.after(0, lambda: self.online_status_label.config(text=f"❌ Erro: {str(e)}"))
            messagebox.showerror("Erro", f"Erro ao converter planilha:\n{str(e)}")
        
        finally:
            def enable_btn():
                self.online_btn['state'] = 'normal'
            self.root.after(0, enable_btn)
            self.online_running = False
    
    def build_converter_tab(self):
        """Constrói a interface da aba de conversão"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_converter)
        
        # ===== SEÇÃO ARQUIVOS =====
        files_section = self.create_section(tab_frame, "📁 ARQUIVOS DE ENTRADA/SAÍDA")
        
        # Planilha Google
        self.df1_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha Google:", self.df1_path, 
                              self.browse_df1, "(arquivo CSV da planilha)")
        
        # Planilha CSV QGIS
        self.df2_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha CSV QGIS:", self.df2_path, 
                              self.browse_df2, "(arquivo CSV do QGIS)")
        
        # Relatório de Saída
        self.output_path = tk.StringVar()
        self.create_file_input(files_section, "Relatório de Saída:", self.output_path, 
                              self.browse_output, "(onde salvar o resultado)")
        
        # ===== SEÇÃO MUNICÍPIO =====
        municipio_section = self.create_section(tab_frame, "🏙️ MUNICÍPIO E CEP")
        
        # Container para município
        mun_container = tk.Frame(municipio_section, bg=self.section_bg)
        mun_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Frame do município
        mun_frame = tk.Frame(mun_container, bg=self.section_bg)
        mun_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mun_frame, text="Município:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        
        self.municipio_var = tk.StringVar()
        self.municipio_combo = ttk.Combobox(mun_frame, textvariable=self.municipio_var, 
                                           width=30, state='readonly')
        self.municipio_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.municipio_combo.bind('<<ComboboxSelected>>', self.on_municipio_selected)
        
        # Botão atualizar base
        btn_update = ttk.Button(mun_frame, text="🔄", command=self.update_cep_database, width=3)
        btn_update.pack(side=tk.LEFT, padx=(5, 0))
        
        # Label de status do CEP selecionado
        self.cep_status_label = ttk.Label(mun_container, text="", style='Hint.TLabel')
        self.cep_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # ===== SEÇÃO FILTROS =====
        filters_section = self.create_section(tab_frame, "🔍 FILTROS OPCIONAIS")
        
        # Container para filtros
        filters_container = tk.Frame(filters_section, bg=self.section_bg)
        filters_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Filtro Localidade
        loc_frame = tk.Frame(filters_container, bg=self.section_bg)
        loc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(loc_frame, text="Localidade:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.localidade_var = tk.StringVar()
        loc_entry = ttk.Entry(loc_frame, textvariable=self.localidade_var, width=15)
        loc_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(loc_frame, text="(ex: 001)", style='Hint.TLabel').pack(side=tk.LEFT)
        
        # Filtro Rota
        rota_frame = tk.Frame(filters_container, bg=self.section_bg)
        rota_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rota_frame, text="Rota:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rota_var = tk.StringVar()
        rota_entry = ttk.Entry(rota_frame, textvariable=self.rota_var, width=15)
        rota_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(rota_frame, text="(ex: 123)", style='Hint.TLabel').pack(side=tk.LEFT)
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                       style='Custom.Horizontal.TProgressbar',
                                       maximum=100, value=0)
        self.progress.pack(fill=tk.X)
        
        # Label de status
        self.status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                      style='Status.TLabel')
        self.status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Converter
        self.convert_btn = self.create_modern_button(button_frame, "Converter", 
                                                     self.convert, self.accent_color, 
                                                     self.hover_color)
        self.convert_btn.pack(fill=tk.X, pady=4)
        
        # Botão Cancelar
        self.cancel_btn = self.create_modern_button(button_frame, "Cancelar", 
                                                    self.cancel, '#6c757d', '#5a6268')
        self.cancel_btn.pack(fill=tk.X, pady=4)
    
    def build_consultar_tab(self):
        """Constrói a interface da aba de consulta de clientes"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_consultar)

        self.add_gsan_url_field(tab_frame)
        
        # ===== SEÇÃO CONFIGURAÇÕES =====
        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Usuário
        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.gsan_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.gsan_user_var, width=30).pack(side=tk.LEFT)
        
        # Senha
        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.gsan_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.gsan_senha_var, show='*', width=30).pack(side=tk.LEFT)
        
        # ===== SEÇÃO ARQUIVOS =====
        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        
        # Planilha de entrada (já convertida)
        self.consulta_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha Convertida:", self.consulta_input_path, 
                              self.browse_consulta_input, "(arquivo CSV gerado na aba anterior)")
        
        # Planilha de saída
        self.consulta_output_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha de Saída:", self.consulta_output_path, 
                              self.browse_consulta_output, "(arquivo CSV com códigos de cliente)")
        
        # ===== OPÇÕES =====
        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", 
                       variable=self.headless_var).pack(anchor=tk.W, pady=5)
        
        ttk.Label(options_container, text="⚡ Modo invisível é mais rápido e não abre o navegador", 
                 style='Hint.TLabel').pack(anchor=tk.W)
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.consulta_progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                                style='Custom.Horizontal.TProgressbar',
                                                maximum=100, value=0)
        self.consulta_progress.pack(fill=tk.X)
        
        # Label de status
        self.consulta_status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                              style='Status.TLabel')
        self.consulta_status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Iniciar Consulta
        self.consulta_btn = self.create_modern_button(button_frame, "▶ Iniciar Consulta", 
                                                      self.iniciar_consulta, '#28a745', '#218838')
        self.consulta_btn.pack(fill=tk.X, pady=4)
        
        # Botão Parar
        self.parar_consulta_btn = self.create_modern_button(button_frame, "⏹ Parar", 
                                                            self.parar_consulta, '#dc3545', '#c82333')
        self.parar_consulta_btn.pack(fill=tk.X, pady=4)
    
    def build_criar_tab(self):
        """Constrói a interface da aba de criar código de cliente"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_criar)

        self.add_gsan_url_field(tab_frame)
        
        # ===== SEÇÃO CONFIGURAÇÕES =====
        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Usuário
        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.criar_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.criar_user_var, width=30).pack(side=tk.LEFT)
        
        # Senha
        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.criar_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.criar_senha_var, show='*', width=30).pack(side=tk.LEFT)
        
        # ===== SEÇÃO ARQUIVOS =====
        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        
        # Planilha de entrada (planilha convertida)
        self.criar_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha Convertida:", self.criar_input_path, 
                              self.browse_criar_input, "(arquivo CSV com dados completos)")
        
        # Planilha de saída
        self.criar_output_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha de Saída:", self.criar_output_path, 
                              self.browse_criar_output, "(arquivo CSV com códigos criados)")
        
        # ===== OPÇÕES =====
        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        self.criar_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", 
                       variable=self.criar_headless_var).pack(anchor=tk.W, pady=5)
        
        ttk.Label(options_container, 
                 text="⚠️ Recomendado deixar visível para acompanhar a criação de clientes", 
                 style='Hint.TLabel').pack(anchor=tk.W)
        
        ttk.Label(options_container, 
                 text="💡 Apenas registros com ALTERAR=1 e COD_CLIENTE=0 serão processados", 
                 style='Hint.TLabel').pack(anchor=tk.W, pady=(5,0))
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.criar_progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                             style='Custom.Horizontal.TProgressbar',
                                             maximum=100, value=0)
        self.criar_progress.pack(fill=tk.X)
        
        # Label de status
        self.criar_status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                           style='Status.TLabel')
        self.criar_status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Iniciar Criação
        self.criar_btn = self.create_modern_button(button_frame, "▶ Criar Clientes", 
                                                   self.iniciar_criar, '#28a745', '#218838')
        self.criar_btn.pack(fill=tk.X, pady=4)
        
        # Botão Parar
        self.parar_criar_btn = self.create_modern_button(button_frame, "⏹ Parar", 
                                                         self.parar_criar, '#dc3545', '#c82333')
        self.parar_criar_btn.pack(fill=tk.X, pady=4)
    
    def build_rotas_tab(self):
        """Constrói a interface da aba de criar rotas"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_rotas)

        self.add_gsan_url_field(tab_frame)
        
        # ===== SEÇÃO CONFIGURAÇÕES =====
        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Usuário
        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.rotas_user_var, width=30).pack(side=tk.LEFT)
        
        # Senha
        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.rotas_senha_var, show='*', width=30).pack(side=tk.LEFT)
        
        # ===== SEÇÃO PARÂMETROS DA ROTA =====
        params_section = self.create_section(tab_frame, "🔢 PARÂMETROS DA ROTA")
        
        params_container = tk.Frame(params_section, bg=self.section_bg)
        params_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Localidade
        loc_frame = tk.Frame(params_container, bg=self.section_bg)
        loc_frame.pack(fill=tk.X, pady=3)
        ttk.Label(loc_frame, text="Localidade:", style='Section.TLabel', 
                 width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_localidade_var = tk.StringVar(value='301')
        ttk.Entry(loc_frame, textvariable=self.rotas_localidade_var, width=15).pack(side=tk.LEFT)
        
        # Setor Comercial
        setor_frame = tk.Frame(params_container, bg=self.section_bg)
        setor_frame.pack(fill=tk.X, pady=3)
        ttk.Label(setor_frame, text="Setor Comercial:", style='Section.TLabel', 
                 width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_setor_var = tk.StringVar(value='300')
        ttk.Entry(setor_frame, textvariable=self.rotas_setor_var, width=15).pack(side=tk.LEFT)
        
        # Rota Inicial
        rota_ini_frame = tk.Frame(params_container, bg=self.section_bg)
        rota_ini_frame.pack(fill=tk.X, pady=3)
        ttk.Label(rota_ini_frame, text="Rota Inicial:", style='Section.TLabel', 
                 width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_inicial_var = tk.StringVar(value='1')
        ttk.Entry(rota_ini_frame, textvariable=self.rotas_inicial_var, width=15).pack(side=tk.LEFT)
        
        # Rota Final
        rota_fim_frame = tk.Frame(params_container, bg=self.section_bg)
        rota_fim_frame.pack(fill=tk.X, pady=3)
        ttk.Label(rota_fim_frame, text="Rota Final:", style='Section.TLabel', 
                 width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_final_var = tk.StringVar(value='1')
        ttk.Entry(rota_fim_frame, textvariable=self.rotas_final_var, width=15).pack(side=tk.LEFT)
        
        # Leiturista ID
        leit_frame = tk.Frame(params_container, bg=self.section_bg)
        leit_frame.pack(fill=tk.X, pady=3)
        ttk.Label(leit_frame, text="ID Leiturista:", style='Section.TLabel', 
                 width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_leiturista_var = tk.StringVar(value='1')
        ttk.Entry(leit_frame, textvariable=self.rotas_leiturista_var, width=15).pack(side=tk.LEFT)

        # ===== SEÇÃO PARÂMETROS OPERACIONAIS =====
        op_section = self.create_section(tab_frame, "⚙️ PARAMETROS OPERACIONAIS")
        op_container = tk.Frame(op_section, bg=self.section_bg)
        op_container.pack(fill=tk.X, padx=15, pady=(5, 10))

        faturamento_frame = tk.Frame(op_container, bg=self.section_bg)
        faturamento_frame.pack(fill=tk.X, pady=3)
        ttk.Label(faturamento_frame, text="Grupo Faturamento:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_faturamento_var = tk.StringVar(value='150')
        ttk.Entry(faturamento_frame, textvariable=self.rotas_faturamento_var, width=18).pack(side=tk.LEFT)

        cobranca_frame = tk.Frame(op_container, bg=self.section_bg)
        cobranca_frame.pack(fill=tk.X, pady=3)
        ttk.Label(cobranca_frame, text="Grupo Cobranca:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_cobranca_var = tk.StringVar(value='150')
        ttk.Entry(cobranca_frame, textvariable=self.rotas_cobranca_var, width=18).pack(side=tk.LEFT)

        leitura_frame = tk.Frame(op_container, bg=self.section_bg)
        leitura_frame.pack(fill=tk.X, pady=3)
        ttk.Label(leitura_frame, text="Tipo de Leitura:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_leitura_tipo_var = tk.StringVar(value='MICROCOLETOR')
        ttk.Entry(leitura_frame, textvariable=self.rotas_leitura_tipo_var, width=28).pack(side=tk.LEFT)

        empresa_leit_frame = tk.Frame(op_container, bg=self.section_bg)
        empresa_leit_frame.pack(fill=tk.X, pady=3)
        ttk.Label(empresa_leit_frame, text="Empresa Leitura:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_empresa_leitura_var = tk.StringVar(value='CAEMA')
        ttk.Entry(empresa_leit_frame, textvariable=self.rotas_empresa_leitura_var, width=28).pack(side=tk.LEFT)

        empresa_cob_frame = tk.Frame(op_container, bg=self.section_bg)
        empresa_cob_frame.pack(fill=tk.X, pady=3)
        ttk.Label(empresa_cob_frame, text="Empresa Cobranca:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_empresa_cobranca_var = tk.StringVar(value='CAEMA')
        ttk.Entry(empresa_cob_frame, textvariable=self.rotas_empresa_cobranca_var, width=28).pack(side=tk.LEFT)

        empresa_ent_frame = tk.Frame(op_container, bg=self.section_bg)
        empresa_ent_frame.pack(fill=tk.X, pady=3)
        ttk.Label(empresa_ent_frame, text="Empresa Entrega:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.rotas_empresa_entrega_var = tk.StringVar(value='CAEMA')
        ttk.Entry(empresa_ent_frame, textvariable=self.rotas_empresa_entrega_var, width=28).pack(side=tk.LEFT)

        # Indicadores equivalentes ao script criarRotas.py
        self.rotas_fiscalizar_cortado_var = tk.StringVar(value='2')
        self.rotas_fiscalizar_suprimido_var = tk.StringVar(value='2')
        self.rotas_armazenar_coord_var = tk.StringVar(value='1')
        self.rotas_gerar_falsa_faixa_var = tk.StringVar(value='2')
        self.rotas_gerar_fiscalizacao_var = tk.StringVar(value='2')

        indicadores_frame = tk.Frame(op_container, bg=self.section_bg)
        indicadores_frame.pack(fill=tk.X, pady=(6, 2))
        ttk.Label(indicadores_frame, text="Indic. Cortado:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(indicadores_frame, textvariable=self.rotas_fiscalizar_cortado_var, width=6).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(indicadores_frame, text="Suprimido:", style='Section.TLabel').pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(indicadores_frame, textvariable=self.rotas_fiscalizar_suprimido_var, width=6).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(indicadores_frame, text="Coord:", style='Section.TLabel').pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(indicadores_frame, textvariable=self.rotas_armazenar_coord_var, width=6).pack(side=tk.LEFT)

        indicadores2_frame = tk.Frame(op_container, bg=self.section_bg)
        indicadores2_frame.pack(fill=tk.X, pady=(3, 2))
        ttk.Label(indicadores2_frame, text="Falsa Faixa:", style='Section.TLabel', width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(indicadores2_frame, textvariable=self.rotas_gerar_falsa_faixa_var, width=6).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(indicadores2_frame, text="Fiscalizacao:", style='Section.TLabel').pack(side=tk.LEFT, padx=(0, 6))
        ttk.Entry(indicadores2_frame, textvariable=self.rotas_gerar_fiscalizacao_var, width=6).pack(side=tk.LEFT)

        ttk.Label(op_container, text="Padrao do script: 2,2,1,2,2", style='Hint.TLabel').pack(anchor=tk.W, pady=(3, 0))
        
        ttk.Label(params_container, 
                 text="💡 As rotas serão criadas de [Rota Inicial] até [Rota Final]", 
                 style='Hint.TLabel').pack(anchor=tk.W, pady=(10,0))
        
        # ===== OPÇÕES =====
        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        self.rotas_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", 
                       variable=self.rotas_headless_var).pack(anchor=tk.W, pady=5)
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.rotas_progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                             style='Custom.Horizontal.TProgressbar',
                                             maximum=100, value=0)
        self.rotas_progress.pack(fill=tk.X)
        
        # Label de status
        self.rotas_status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                           style='Status.TLabel')
        self.rotas_status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Criar Rotas
        self.rotas_btn = self.create_modern_button(button_frame, "▶ Criar Rotas", 
                                                   self.iniciar_rotas, '#28a745', '#218838')
        self.rotas_btn.pack(fill=tk.X, pady=4)
        
        # Botão Parar
        self.parar_rotas_btn = self.create_modern_button(button_frame, "⏹ Parar", 
                                                         self.parar_rotas, '#dc3545', '#c82333')
        self.parar_rotas_btn.pack(fill=tk.X, pady=4)
    
    def build_quadras_tab(self):
        """Constrói a interface da aba de criar quadras"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_quadras)

        self.add_gsan_url_field(tab_frame)
        
        # ===== SEÇÃO CONFIGURAÇÕES =====
        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Usuário
        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.quadras_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.quadras_user_var, width=30).pack(side=tk.LEFT)
        
        # Senha
        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.quadras_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.quadras_senha_var, show='*', width=30).pack(side=tk.LEFT)
        
        # ===== SEÇÃO ARQUIVOS =====
        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        
        # Planilha de entrada
        self.quadras_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha Convertida:", self.quadras_input_path, 
                              self.browse_quadras_input, "(arquivo CSV com dados das quadras)")
        
        ttk.Label(files_section, 
                 text="💡 Serão criadas apenas quadras únicas (sem duplicatas)", 
                 style='Hint.TLabel', background=self.section_bg).pack(anchor=tk.W, padx=15, pady=(0,10))
        
        # ===== PARÂMETROS =====
        params_section = self.create_section(tab_frame, "🔧 PARÂMETROS")
        
        params_container = tk.Frame(params_section, bg=self.section_bg)
        params_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Código do Bairro
        bairro_frame = tk.Frame(params_container, bg=self.section_bg)
        bairro_frame.pack(fill=tk.X, pady=5)
        ttk.Label(bairro_frame, text="Código do Bairro:", style='Section.TLabel', 
                 width=20, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.quadras_bairro_var = tk.StringVar(value='50')
        ttk.Entry(bairro_frame, textvariable=self.quadras_bairro_var, width=15).pack(side=tk.LEFT)
        
        self.quadras_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(params_container, text="Executar em modo invisível (headless)", 
                       variable=self.quadras_headless_var).pack(anchor=tk.W, pady=5)
        
        ttk.Label(params_container, 
                 text="✅ Processará automaticamente quadras únicas (QUADRA, ROTA, LOCAL, SETOR)", 
                 style='Hint.TLabel').pack(anchor=tk.W, pady=(5,0))
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.quadras_progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                               style='Custom.Horizontal.TProgressbar',
                                               maximum=100, value=0)
        self.quadras_progress.pack(fill=tk.X)
        
        # Label de status
        self.quadras_status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                             style='Status.TLabel')
        self.quadras_status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Criar Quadras
        self.quadras_btn = self.create_modern_button(button_frame, "▶ Criar Quadras", 
                                                     self.iniciar_quadras, '#28a745', '#218838')
        self.quadras_btn.pack(fill=tk.X, pady=4)
        
        # Botão Parar
        self.parar_quadras_btn = self.create_modern_button(button_frame, "⏹ Parar", 
                                                           self.parar_quadras, '#dc3545', '#c82333')
        self.parar_quadras_btn.pack(fill=tk.X, pady=4)
    
    def build_matriculas_tab(self):
        """Constrói a interface da aba de criar matrículas"""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_matriculas)

        self.add_gsan_url_field(tab_frame)
        
        # ===== SEÇÃO CONFIGURAÇÕES =====
        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Usuário
        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.matriculas_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.matriculas_user_var, width=30).pack(side=tk.LEFT)
        
        # Senha
        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', 
                 width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.matriculas_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.matriculas_senha_var, show='*', width=30).pack(side=tk.LEFT)
        
        # ===== SEÇÃO ARQUIVOS =====
        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        
        # Planilha de entrada
        self.matriculas_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha Convertida:", self.matriculas_input_path, 
                              self.browse_matriculas_input, "(arquivo CSV com dados dos imóveis)")
        
        # Planilha de saída
        self.matriculas_output_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha de Saída:", self.matriculas_output_path, 
                              self.browse_matriculas_output, "(arquivo CSV com matrículas criadas)")
        
        # ===== OPÇÕES =====
        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        self.matriculas_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", 
                       variable=self.matriculas_headless_var).pack(anchor=tk.W, pady=5)
        
        ttk.Label(options_container, 
                 text="💡 Apenas registros com MATRICULA=0 serão processados", 
                 style='Hint.TLabel').pack(anchor=tk.W)
        
        ttk.Label(options_container, 
                 text="✅ As matrículas criadas serão inseridas na coluna MATRICULA", 
                 style='Hint.TLabel').pack(anchor=tk.W, pady=(5,0))
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.matriculas_progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                                  style='Custom.Horizontal.TProgressbar',
                                                  maximum=100, value=0)
        self.matriculas_progress.pack(fill=tk.X)
        
        # Label de status
        self.matriculas_status_label = ttk.Label(tab_frame, text="Aguardando...", 
                                                style='Status.TLabel')
        self.matriculas_status_label.pack(pady=(5, 15))
        
        # ===== BOTÕES =====
        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        
        # Botão Criar Matrículas
        self.matriculas_btn = self.create_modern_button(button_frame, "▶ Criar Matrículas", 
                                                        self.iniciar_matriculas, '#28a745', '#218838')
        self.matriculas_btn.pack(fill=tk.X, pady=4)
        
        # Botão Parar
        self.parar_matriculas_btn = self.create_modern_button(button_frame, "⏹ Parar", 
                                                              self.parar_matriculas, '#dc3545', '#c82333')
        self.parar_matriculas_btn.pack(fill=tk.X, pady=4)
    
    def create_section(self, parent, title):
        """Cria uma seção visual com título e fundo"""
        section = tk.Frame(parent, bg=self.section_bg, relief=tk.SOLID, bd=1, highlightthickness=1, highlightbackground=self.border_color)
        section.pack(fill=tk.X, pady=(0, 10))

        top_border = tk.Frame(section, bg=self.accent_color, height=3)
        top_border.pack(fill=tk.X)
        
        # Título da seção
        title_label = ttk.Label(section, text=title, style='Section.TLabel')
        title_label.pack(anchor=tk.W, padx=12, pady=(6, 4))
        
        return section

    def create_scrollable_tab(self, parent_tab):
        """Cria layout com conteúdo rolável à esquerda e ações fixas à direita."""
        outer = tk.Frame(parent_tab, bg=self.bg_color)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = tk.Frame(outer, bg=self.bg_color)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(
            outer,
            bg='#dbeafe',
            relief=tk.SOLID,
            bd=1,
            highlightthickness=1,
            highlightbackground=self.border_color,
            width=230
        )
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right.pack_propagate(False)

        right_title = tk.Label(
            right,
            text="ACOES",
            font=('Segoe UI', 10, 'bold'),
            bg='#dbeafe',
            fg=self.accent_color
        )
        right_title.pack(anchor=tk.W, padx=10, pady=(8, 6))

        canvas = tk.Canvas(left, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient='vertical', command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.bg_color)

        window_id = canvas.create_window((0, 0), window=scrollable, anchor='nw')

        def on_frame_configure(_event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        def on_canvas_configure(event):
            target_width = max(640, min(event.width - 8, 880))
            canvas.itemconfigure(window_id, width=target_width)

        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-event.delta / 120), 'units')

        def on_mousewheel_linux_up(_event):
            canvas.yview_scroll(-1, 'units')

        def on_mousewheel_linux_down(_event):
            canvas.yview_scroll(1, 'units')

        def bind_mousewheel(_event):
            canvas.bind_all('<MouseWheel>', on_mousewheel)
            canvas.bind_all('<Button-4>', on_mousewheel_linux_up)
            canvas.bind_all('<Button-5>', on_mousewheel_linux_down)

        def unbind_mousewheel(_event):
            canvas.unbind_all('<MouseWheel>')
            canvas.unbind_all('<Button-4>')
            canvas.unbind_all('<Button-5>')

        scrollable.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.bind('<Enter>', bind_mousewheel)
        canvas.bind('<Leave>', unbind_mousewheel)
        scrollable.bind('<Enter>', bind_mousewheel)
        scrollable.bind('<Leave>', unbind_mousewheel)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return scrollable, right

    def get_theme_palette(self, theme_name):
        """Retorna a paleta de cores do tema selecionado."""
        return {
            'bg_color': '#eef4ff',
            'section_bg': '#ffffff',
            'accent_color': '#2563eb',
            'hover_color': '#1d4ed8',
            'text_color': '#1f2937',
            'muted_text': '#475569',
            'border': '#bfd0f2',
            'input_bg': '#ffffff',
            'input_fg': '#1f2937',
            'tab_active': '#dbeafe'
        }

    def apply_theme(self, theme_name='light'):
        """Aplica tema visual global claro."""
        palette = self.get_theme_palette('light')
        self.current_theme = 'light'

        self.bg_color = palette['bg_color']
        self.section_bg = palette['section_bg']
        self.accent_color = palette['accent_color']
        self.hover_color = palette['hover_color']
        self.text_color = palette['text_color']
        self.muted_text = palette['muted_text']
        self.border_color = palette['border']
        self.input_bg = palette['input_bg']
        self.input_fg = palette['input_fg']
        self.tab_active_bg = palette['tab_active']

        self.style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground=self.accent_color, background=self.bg_color)
        self.style.configure('Section.TLabel', font=('Segoe UI', 10, 'bold'), foreground=self.accent_color, background=self.section_bg)
        self.style.configure('Hint.TLabel', font=('Segoe UI', 8), foreground=self.muted_text, background=self.section_bg)
        self.style.configure('Status.TLabel', font=('Segoe UI', 9), foreground=self.muted_text, background=self.bg_color)

        self.style.configure('Custom.Horizontal.TProgressbar', troughcolor=self.border_color, background=self.accent_color, borderwidth=0, thickness=20)

        # Notebook com abas horizontais padronizadas
        self.style.configure('Smart.TNotebook', background=self.bg_color, borderwidth=0, tabposition='n')
        self.style.configure('Smart.TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=(10, 8), width=14, background=self.section_bg, foreground=self.muted_text)
        self.style.map(
            'Smart.TNotebook.Tab',
            background=[('selected', self.tab_active_bg), ('active', self.tab_active_bg)],
            foreground=[('selected', self.accent_color), ('active', self.accent_color)]
        )

        self.style.configure('TEntry', fieldbackground=self.input_bg, foreground=self.input_fg)
        self.style.configure('TCombobox', fieldbackground=self.input_bg, foreground=self.input_fg)
        self.style.map('TCombobox', fieldbackground=[('readonly', self.input_bg)], foreground=[('readonly', self.input_fg)])
        self.style.configure('TCheckbutton', background=self.section_bg, foreground=self.text_color)
        self.style.configure('TButton', background=self.section_bg, foreground=self.text_color)
        self.style.configure('Primary.TButton', font=('Segoe UI', 9, 'bold'))

        self.root.configure(bg=self.bg_color)

    def toggle_theme(self):
        """Tema fixo claro."""
        return

    def get_gsan_base_url(self):
        """Normaliza a URL base do GSAN informada pelo usuário."""
        base_url = self.gsan_base_url_var.get().strip()
        if not base_url:
            base_url = 'http://g1.caema.ma.gov.br/gsan/'

        if not re.match(r'^https?://', base_url, re.IGNORECASE):
            base_url = f'http://{base_url}'

        if not base_url.endswith('/'):
            base_url += '/'

        if 'gsan/' not in base_url.lower():
            base_url += 'gsan/'

        return base_url

    def gsan_url(self, path=''):
        """Monta a URL final do GSAN para as telas automatizadas."""
        base_url = self.get_gsan_base_url()
        if not path:
            return base_url
        return f"{base_url}{path.lstrip('/')}"

    def add_gsan_url_field(self, parent):
        """Adiciona campo de URL base GSAN em uma aba."""
        url_section = self.create_section(parent, "🌐 SERVIDOR GSAN")
        url_container = tk.Frame(url_section, bg=self.section_bg)
        url_container.pack(fill=tk.X, padx=15, pady=(5, 10))

        url_row = tk.Frame(url_container, bg=self.section_bg)
        url_row.pack(fill=tk.X, pady=2)

        ttk.Label(url_row, text="URL Base:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(url_row, textvariable=self.gsan_base_url_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(
            url_container,
            text="Ex.: gsan.caema.ma.gov.br:8080/gsan/ ou g1.caema.ma.gov.br/gsan/",
            style='Hint.TLabel'
        ).pack(anchor=tk.W, pady=(4, 0))
    
    def create_file_input(self, parent, label_text, var, command, hint=""):
        """Cria um campo de seleção de arquivo"""
        container = tk.Frame(parent, bg=self.section_bg)
        container.pack(fill=tk.X, padx=12, pady=4)
        
        # Label
        label = ttk.Label(container, text=label_text, style='Section.TLabel')
        label.pack(anchor=tk.W)
        
        # Frame para input e botão
        input_frame = tk.Frame(container, bg=self.section_bg)
        input_frame.pack(fill=tk.X, pady=(2, 0))
        
        # Entry
        entry = ttk.Entry(input_frame, textvariable=var, width=44)
        entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão
        btn = ttk.Button(input_frame, text="...", command=command, width=4)
        btn.pack(side=tk.LEFT)
        
        # Hint
        if hint:
            hint_label = ttk.Label(container, text=hint, style='Hint.TLabel')
            hint_label.pack(anchor=tk.W, pady=(2, 5))
    
    def create_modern_button(self, parent, text, command, bg_color, hover_color):
        """Cria um botão moderno com efeitos"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 9, 'bold'),
            width=18,
            height=1,
            bg=bg_color,
            fg='white',
            activebackground=hover_color,
            activeforeground='white',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            padx=10,
            pady=7
        )
        return btn
    
    def browse_df1(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha Google",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.df1_path.set(filename)
    
    def browse_df2(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha CSV QGIS",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.df2_path.set(filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar Relatório Como",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def cancel(self):
        if self.processing:
            self.processing = False
            self.status_label.config(text="Cancelado pelo usuário")
        else:
            self.root.quit()
    
    def convert(self):
        # Validações
        if not self.df1_path.get():
            messagebox.showerror("Erro", "Selecione a Planilha Google!")
            return
        
        if not self.df2_path.get():
            messagebox.showerror("Erro", "Selecione a Planilha CSV QGIS!")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Erro", "Selecione o local para salvar o relatório!")
            return
        
        # Executar conversão em thread separada
        self.processing = True
        thread = threading.Thread(target=self.process_conversion)
        thread.daemon = True
        thread.start()
    
    def process_conversion(self):
        try:
            self.root.after(0, self.progress.start)
            self.root.after(0, lambda: self.status_label.config(text="Carregando planilhas..."))
            self.root.after(0, lambda: self.convert_btn.config(state='disabled'))
            
            # Carregar dados
            self.root.after(0, lambda: self.progress.config(value=10))
            df = pd.read_csv(self.df1_path.get())
            df = df.fillna(0).map(remover_acentos)
            
            self.root.after(0, lambda: self.progress.config(value=20))
            
            # Aplicar filtros se fornecidos
            localidade = self.localidade_var.get().strip()
            rota = self.rota_var.get().strip()
            
            if localidade:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Filtrando por localidade: {localidade}..."))
                df['LOCALIDADE'] = df['LOCALIDADE'].astype(str)
                df = df[df['LOCALIDADE'].str[:3] == localidade.zfill(3)]
            
            if rota:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Filtrando por rota: {rota}..."))
                df['ROTA'] = df['ROTA'].astype(str).str.replace('.0', '')
                df = df[df['ROTA'] == rota]
            
            if df.empty:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Aviso", "Nenhum registro encontrado com os filtros especificados!"))
                self.root.after(0, lambda: self.progress.config(value=0))
                self.root.after(0, lambda: self.convert_btn.pack(side=tk.LEFT, padx=5))
                self.root.after(0, lambda: self.status_label.config(text="Aguardando..."))
                self.processing = False
                return
            
            self.root.after(0, lambda: self.progress.config(value=30))
            df2 = pd.read_csv(self.df2_path.get())
            
            self.total_records = len(df)
            self.root.after(0, lambda: self.status_label.config(
                text=f"Processando {self.total_records} registros..."))
            
            # Preparar saída
            header = ['ALTERAR', 'ORDEM1', 'ORDEM2', 'LOCAL', 'SETOR', 'QUADRA', 'LOTE', 
                     'SUBLOTE', 'TESTADA', 'SEQUENCIA', 'ROTA', 'MATRICULA', 'COD_LOG', 
                     'BAIRRO', 'CEP_GSAN', 'NUMERO', 'COMPLEMENTO', 'NOME', 'CPF', 'CNPJ', 
                     'V_CPF', 'V_CNPJ', 'COD_CLIENTE', 'EMAIL', 'RG', 'DATA_EXP', 'SEXO', 
                     'MAE', 'DATA_NASC','TIPO_CLIENTE', 'TIPO_HAB', 'RES', 'COM', 'PUB', 
                     'MUN', 'EST', 'FED', 'IND', 'PEQ', 'POP', 'AREA', 'DDD', 'TELEFONE', 
                     'CX', 'CY']
            
            with open(self.output_path.get(), mode="w", newline="", encoding='utf-8') as output_file:
                writer = csv.writer(output_file)
                writer.writerow(header)
                
                ordem_saida = 0  # Contador de ordem para a saída
                
                for i in df.index:
                    if not self.processing:
                        break
                    
                    ordem_saida += 1  # Incrementa ordem na saída
                    matricula_raw = df['MATRÍCULA DO IMÓVEL'][i]        
                    try:
                        matricula = int(matricula_raw) if matricula_raw != 0 else None
                    except:
                        matricula = None
                    
                    # Definir COD_CLIENTE baseado na matrícula
                    if matricula is not None and matricula != 0:
                        cod_cliente = 1
                    else:
                        cod_cliente = 0
                    
                    localidade_val = str(df['LOCALIDADE'][i])
                    localidade_val = localidade_val[:3]
                    setor = str(df['SETOR'][i])
                    rota_val = str(df['ROTA'][i]).replace('.0','')
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
                    # Se não tiver nome, usar texto padrão
                    if nomeCliente == '0' or nomeCliente == 'nan' or not nomeCliente.strip():
                        nomeCliente = 'CADASTRAR NOME NA CAEMA'
                    
                    cpf = int(df['CPF'][i])   
                    vcpf = 1  # Sempre 1 para todos
                    
                    ocorCad = str(df['OCORRENCIA DE CADASTRO'][i])
                    if ocorCad == 'Terreno vazio':
                        tipoHab = 0
                    else:
                        tipoHab = 1
                    
                    # Formatar datas para DD/MM/YYYY
                    dataExp = str(df['DATA DE EXPEDIÇÃO'][i])
                    if dataExp != '0' and dataExp != 'nan':
                        try:
                            data_obj = pd.to_datetime(dataExp, errors='coerce')
                            ano = data_obj.year
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
                            if ano > 2008:
                                data_obj = data_obj.replace(year=ano - 100)
                            dataNasc = data_obj.strftime('%d/%m/%Y')
                        except:
                            pass
                    
                    nomeMae = str(df['NOME DA MÃE'][i])
                    rgCliente = str(df['RG'][i]).replace('.0','')
                    emailCliente = str(df['E-MAIL'][i])
                    telefone = str(df['TELEFONE DE CONTATO COM DDD'][i])
                    
                    # Definir CEP_GSAN baseado no município selecionado
                    cep_gsan = self.selected_cep_id if self.selected_cep_id else 0
                    cod_log = 0  # COD_LOG sempre 0
                    
                    # Processar telefone - se não tiver, usar 0
                    if telefone == '0' or telefone == 'nan' or not telefone.strip():
                        ddd = '0'
                        telefone = '0'
                    else:
                        ddd = telefone[:2].replace('0.','0')
                        telefone = telefone[2:].replace('.0','')
                        # Se telefone ficar vazio após processamento, usar 0
                        if not telefone or telefone == 'nan':
                            telefone = '0'
                        if not ddd or ddd == 'nan':
                            ddd = '0'
                    
                    if econRes + econCom + econMun + econEst + econFed + econInd == 0:
                        econRes = 1
                    
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
                        
                        if not encontrou:
                            rot_id = str(df2['rot_id'][j]).replace('.0','')
                            seq_id = str(df2['seq_id'][j]).replace('.0','')
                            if rot_id == rota_val and seq_id == numVisita:
                                latitude = str(df2['latitude'][j])
                                longitude = str(df2['longitude'][j])
                                quadra = str(df2['quadra'][j])
                                encontrou = True
                                break
                    
                    if matricula is None:
                        matricula = 0

                    row = (1, ordem_saida, ordem_saida, localidade_val, setor, quadra, numVisita, 0, 0, 
                          numVisita, rota_val, matricula, cod_log, bairro, cep_gsan, numImovel, 0, 
                          nomeCliente, cpf, cnpj, vcpf, vcnpj, cod_cliente, emailCliente, rgCliente, 
                          dataExp, sexo, nomeMae, dataNasc, tipoCliente, tipoHab, econRes, 
                          econCom, econPub, econMun, econEst, econFed, econInd, econPeq, 
                          econPop, area, ddd, telefone, longitude, latitude)
                    writer.writerow(row)
                    
                    # Atualizar progresso (30% a 90%)
                    if i % 5 == 0:
                        progress_value = 30 + int((i / len(df)) * 60)
                        progress_text = f"Processando: {i+1}/{len(df)} registros"
                        self.root.after(0, lambda p=progress_value: self.progress.config(value=p))
                        self.root.after(0, lambda t=progress_text: self.status_label.config(text=t))
            
            if self.processing:
                self.root.after(0, lambda: self.progress.config(value=100, mode='determinate'))
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso", 
                    f"Conversão concluída!\n{len(df)} registros processados.\n\nArquivo salvo em:\n{self.output_path.get()}"))
                self.root.after(0, lambda: self.status_label.config(
                    text=f"✓ Concluído! {len(df)} registros processados."))
            
        except Exception as e:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante conversão:\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="✗ Erro na conversão"))
            self.root.after(0, lambda: self.progress.config(value=0))
        
        finally:
            self.processing = False
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.convert_btn.pack(side=tk.LEFT, padx=5))
    
    def load_municipios_database(self):
        """Carrega a base de municípios do arquivo CEP.csv"""
        try:
            # Buscar arquivo CEP.csv (incluído no executável)
            cep_file = os.path.join(self.base_path, 'CEP.csv')
            
            if not os.path.exists(cep_file):
                self.cep_status_label.config(text="⚠️ Arquivo CEP.csv não encontrado")
                return
            
            # Carregar dados (usando separador correto)
            df_cep = pd.read_csv(cep_file, sep=';', encoding='utf-8')
            
            # Agrupar por município
            self.municipios_data = {}
            for _, row in df_cep.iterrows():
                municipio = str(row['cep_nmmunicipio']).strip()
                cep_id = int(row['cep_id'])
                cep_cdcep = str(row['cep_cdcep']).strip()
                
                if municipio not in self.municipios_data:
                    self.municipios_data[municipio] = []
                
                self.municipios_data[municipio].append({
                    'cep_id': cep_id,
                    'cep_cdcep': cep_cdcep
                })
            
            # Preencher combobox com municípios ordenados
            municipios = sorted(self.municipios_data.keys())
            self.municipio_combo['values'] = municipios
            
            self.cep_status_label.config(
                text=f"✓ Base carregada: {len(municipios)} municípios, {len(df_cep)} CEPs"
            )
            
        except Exception as e:
            self.cep_status_label.config(text=f"✗ Erro ao carregar base: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar base de CEPs:\n{str(e)}")
    
    def on_municipio_selected(self, event=None):
        """Quando um município é selecionado"""
        municipio = self.municipio_var.get()
        
        if not municipio or municipio not in self.municipios_data:
            self.selected_cep_id = None
            self.cep_status_label.config(text="")
            return
        
        ceps = self.municipios_data[municipio]
        
        if len(ceps) == 1:
            # Apenas um CEP, selecionar automaticamente
            self.selected_cep_id = ceps[0]['cep_id']
            self.cep_status_label.config(
                text=f"✓ CEP: {ceps[0]['cep_cdcep']} | CEP_GSAN: {self.selected_cep_id}"
            )
        else:
            # Múltiplos CEPs, perguntar ao usuário
            cep_options = [f"{c['cep_cdcep']} (ID: {c['cep_id']})" for c in ceps]
            
            # Criar diálogo customizado
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Selecione o CEP - {municipio}")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Centralizar
            dialog.geometry("+%d+%d" % (
                self.root.winfo_rootx() + 90,
                self.root.winfo_rooty() + 200
            ))
            
            tk.Label(dialog, text=f"Município: {municipio}", 
                    font=('Segoe UI', 10, 'bold')).pack(pady=10)
            tk.Label(dialog, text="Selecione o CEP:").pack(pady=5)
            
            listbox = tk.Listbox(dialog, width=50, height=10)
            listbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
            
            for opt in cep_options:
                listbox.insert(tk.END, opt)
            
            listbox.select_set(0)
            
            selected_index = [0]
            
            def on_select():
                if listbox.curselection():
                    selected_index[0] = listbox.curselection()[0]
                    self.selected_cep_id = ceps[selected_index[0]]['cep_id']
                    self.cep_status_label.config(
                        text=f"✓ CEP: {ceps[selected_index[0]]['cep_cdcep']} | COD_LOG: {self.selected_cep_id}"
                    )
                dialog.destroy()
            
            def on_cancel():
                self.selected_cep_id = None
                self.municipio_var.set("")
                self.cep_status_label.config(text="")
                dialog.destroy()
            
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(pady=10)
            
            ttk.Button(btn_frame, text="Confirmar", command=on_select).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=5)
            
            listbox.bind('<Double-Button-1>', lambda e: on_select())
    
    def update_cep_database(self):
        """Atualiza a base de CEPs"""
        filename = filedialog.askopenfilename(
            title="Selecione o novo arquivo CEP.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # Validar arquivo
            df_test = pd.read_csv(filename)
            required_cols = ['cep_id', 'cep_cdcep', 'cep_nmmunicipio']
            
            if not all(col in df_test.columns for col in required_cols):
                messagebox.showerror(
                    "Erro", 
                    f"Arquivo inválido!\n\nColunas necessárias: {', '.join(required_cols)}"
                )
                return
            
            # Copiar para pasta do app
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(__file__)
            
            dest_file = os.path.join(base_path, 'CEP.csv')
            
            # Fazer backup do anterior
            if os.path.exists(dest_file):
                backup_file = os.path.join(base_path, 'CEP_backup.csv')
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(dest_file, backup_file)
            
            # Copiar novo arquivo
            import shutil
            shutil.copy2(filename, dest_file)
            
            # Recarregar
            self.load_municipios_database()
            
            messagebox.showinfo(
                "Sucesso",
                f"Base de CEPs atualizada com sucesso!\n\n{len(df_test)} registros carregados."
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar base:\n{str(e)}")
    
    # ===== MÉTODOS DA ABA DE CONSULTA =====
    
    def open_driver_config(self):
        """Abre janela de configuração do WebDriver"""
        # Criar janela de diálogo
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar WebDriver")
        config_window.geometry("500x350")
        config_window.resizable(False, False)
        config_window.configure(bg=self.bg_color)
        
        # Centralizar janela
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(config_window, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="🌐 Configuração do WebDriver", 
                 font=('Segoe UI', 14, 'bold'), 
                 foreground='#0078d4',
                 background=self.bg_color).pack(pady=(0, 20))
        
        # Frame de conteúdo
        content_frame = tk.Frame(main_frame, bg=self.section_bg, relief=tk.FLAT, bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        inner_frame = tk.Frame(content_frame, bg=self.section_bg)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Seleção de navegador
        nav_frame = tk.Frame(inner_frame, bg=self.section_bg)
        nav_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(nav_frame, text="Navegador:", 
                 font=('Segoe UI', 10, 'bold'),
                 background=self.section_bg).pack(anchor=tk.W, pady=(0, 5))
        
        nav_select_frame = tk.Frame(nav_frame, bg=self.section_bg)
        nav_select_frame.pack(fill=tk.X)
        
        driver_combo = ttk.Combobox(nav_select_frame, textvariable=self.driver_type_var, 
                                    width=18, state='readonly', font=('Segoe UI', 10))
        driver_combo['values'] = ('Chrome', 'Edge', 'Firefox')
        driver_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão download
        btn_download = tk.Button(
            nav_select_frame,
            text="⬇️ Baixar Driver",
            font=('Segoe UI', 9),
            bg='#0078d4',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=lambda: self.download_driver_from_dialog(config_window)
        )
        btn_download.pack(side=tk.LEFT)
        
        # Separador
        ttk.Separator(inner_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Caminho manual
        manual_frame = tk.Frame(inner_frame, bg=self.section_bg)
        manual_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(manual_frame, text="Caminho Manual (opcional):", 
                 font=('Segoe UI', 10, 'bold'),
                 background=self.section_bg).pack(anchor=tk.W, pady=(0, 5))
        
        path_frame = tk.Frame(manual_frame, bg=self.section_bg)
        path_frame.pack(fill=tk.X)
        
        path_entry = ttk.Entry(path_frame, textvariable=self.driver_manual_path_var, 
                              font=('Segoe UI', 9), width=35)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_browse = tk.Button(
            path_frame,
            text="📂",
            font=('Segoe UI', 10),
            width=3,
            bg='#f0f0f0',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.browse_driver_exe
        )
        btn_browse.pack(side=tk.LEFT)
        
        # Dica
        ttk.Label(manual_frame, 
                 text="💡 Deixe vazio para usar o driver baixado automaticamente",
                 font=('Segoe UI', 8),
                 foreground='#666666',
                 background=self.section_bg).pack(anchor=tk.W, pady=(5, 0))
        
        # Status
        self.dialog_status_label = ttk.Label(inner_frame, text="", 
                                            font=('Segoe UI', 9),
                                            foreground='#0078d4',
                                            background=self.section_bg)
        self.dialog_status_label.pack(pady=(10, 0))
        
        # Botão fechar
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        btn_close = tk.Button(
            btn_frame,
            text="✓ Fechar",
            font=('Segoe UI', 10, 'bold'),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=8,
            command=config_window.destroy
        )
        btn_close.pack()
        
        # Verificar driver atual
        current_driver = self.driver_manual_path_var.get()
        if current_driver:
            self.dialog_status_label.config(text=f"✅ Driver configurado: {os.path.basename(current_driver)}")
        elif self.driver_path and os.path.exists(self.driver_path):
            self.dialog_status_label.config(text=f"✅ Driver baixado: {os.path.basename(self.driver_path)}")
    
    def download_driver_from_dialog(self, dialog_window):
        """Baixa o driver a partir da janela de diálogo"""
        self.dialog_status_label.config(text="⏳ Baixando driver...")
        dialog_window.update()
        
        driver_type = self.driver_type_var.get()
        drivers_dir = os.path.join(os.path.dirname(__file__), 'drivers')
        os.makedirs(drivers_dir, exist_ok=True)
        
        try:
            if driver_type == 'Chrome':
                driver_exe = self._download_chromedriver(drivers_dir)
            elif driver_type == 'Edge':
                driver_exe = self._download_edgedriver(drivers_dir)
            elif driver_type == 'Firefox':
                driver_exe = self._download_geckodriver(drivers_dir)
            else:
                raise Exception("Driver não suportado")
            
            if driver_exe and os.path.exists(driver_exe):
                self.driver_path = driver_exe
                self.dialog_status_label.config(text=f"✅ {driver_type}Driver baixado com sucesso!")
                messagebox.showinfo("Sucesso", f"{driver_type}Driver baixado e configurado!", parent=dialog_window)
            else:
                raise Exception("Falha ao baixar o driver")
                
        except Exception as e:
            self.dialog_status_label.config(text=f"❌ Erro ao baixar")
            messagebox.showerror("Erro", f"Erro ao baixar driver:\n{str(e)}\n\nUse a opção de caminho manual.", 
                               parent=dialog_window)
    
    def browse_driver_exe(self):
        """Permite ao usuário selecionar manualmente o executável do driver"""
        filename = filedialog.askopenfilename(
            title="Selecione o executável do driver",
            filetypes=[("Executables", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.driver_manual_path_var.set(filename)
            # Atualizar status se a janela de diálogo estiver aberta
            if hasattr(self, 'dialog_status_label'):
                self.dialog_status_label.config(text=f"✅ Driver manual: {os.path.basename(filename)}")
    
    def _download_file_with_ssl(self, url, dest_path):
        """Baixa um arquivo ignorando verificação SSL"""
        import ssl
        
        # Criar contexto SSL que ignora verificação
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Baixar o arquivo
        with urllib.request.urlopen(url, context=ssl_context, timeout=30) as response:
            with open(dest_path, 'wb') as out_file:
                out_file.write(response.read())
    
    def _download_chromedriver(self, drivers_dir):
        """Baixa o ChromeDriver"""
        try:
            driver_path = os.path.join(drivers_dir, 'chromedriver.exe')
            
            # Verificar se já existe
            if os.path.exists(driver_path):
                return driver_path
            
            # Obter versão do Chrome instalado
            try:
                chrome_version = subprocess.check_output(
                    r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                    shell=True, stderr=subprocess.DEVNULL
                ).decode('utf-8')
                chrome_version = chrome_version.split()[-1].split('.')[0]
            except:
                # Usar versão padrão recente
                chrome_version = "120"
            
            # URLs alternativas do ChromeDriver
            urls_to_try = [
                f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}.0.6099.109/win64/chromedriver-win64.zip",
                "https://chromedriver.storage.googleapis.com/120.0.6099.109/chromedriver_win32.zip",
                "https://chromedriver.storage.googleapis.com/119.0.6045.105/chromedriver_win32.zip",
                "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip",
            ]
            
            zip_path = os.path.join(drivers_dir, 'chromedriver.zip')
            
            for download_url in urls_to_try:
                try:
                    self._download_file_with_ssl(download_url, zip_path)
                    break
                except Exception as e:
                    continue
            else:
                raise Exception("Não foi possível baixar o ChromeDriver de nenhuma fonte")
            
            # Extrair o arquivo
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('chromedriver.exe'):
                        # Extrair apenas o executável
                        zip_ref.extract(file, drivers_dir)
                        # Mover para o diretório raiz se estiver em subpasta
                        extracted_path = os.path.join(drivers_dir, file)
                        if extracted_path != driver_path:
                            os.makedirs(os.path.dirname(driver_path), exist_ok=True)
                            if os.path.exists(driver_path):
                                os.remove(driver_path)
                            os.rename(extracted_path, driver_path)
                        break
            
            # Remover arquivo zip
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            # Limpar subpastas criadas pela extração
            try:
                for item in os.listdir(drivers_dir):
                    item_path = os.path.join(drivers_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
            except:
                pass
            
            return driver_path
        except Exception as e:
            raise Exception(f"Erro ao baixar ChromeDriver: {str(e)}")
    
    def _download_edgedriver(self, drivers_dir):
        """Baixa o EdgeDriver"""
        try:
            driver_path = os.path.join(drivers_dir, 'msedgedriver.exe')
            
            # Verificar se já existe
            if os.path.exists(driver_path):
                return driver_path
            
            # Obter versão do Edge instalado
            try:
                edge_version = subprocess.check_output(
                    r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon" /v version',
                    shell=True, stderr=subprocess.DEVNULL
                ).decode('utf-8')
                edge_version = edge_version.split()[-1].strip()
            except:
                # Usar versão padrão recente
                edge_version = "120.0.2210.91"
            
            # URLs alternativas do EdgeDriver
            urls_to_try = [
                f"https://msedgedriver.azureedge.net/{edge_version}/edgedriver_win64.zip",
                "https://msedgedriver.azureedge.net/120.0.2210.91/edgedriver_win64.zip",
                "https://msedgedriver.azureedge.net/119.0.2151.97/edgedriver_win64.zip",
            ]
            
            zip_path = os.path.join(drivers_dir, 'edgedriver.zip')
            
            for download_url in urls_to_try:
                try:
                    self._download_file_with_ssl(download_url, zip_path)
                    break
                except Exception as e:
                    continue
            else:
                raise Exception("Não foi possível baixar o EdgeDriver de nenhuma fonte. Tente usar o caminho manual.")
            
            # Extrair o arquivo
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('msedgedriver.exe'):
                        zip_ref.extract(file, drivers_dir)
                        extracted_path = os.path.join(drivers_dir, file)
                        if extracted_path != driver_path:
                            if os.path.exists(driver_path):
                                os.remove(driver_path)
                            os.rename(extracted_path, driver_path)
                        break
            
            # Remover arquivo zip
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            return driver_path
        except Exception as e:
            raise Exception(f"Erro ao baixar EdgeDriver: {str(e)}")
    
    def _download_geckodriver(self, drivers_dir):
        """Baixa o GeckoDriver (Firefox) - verifica inclusos primeiro"""
        try:
            driver_path = os.path.join(drivers_dir, 'geckodriver.exe')
            
            # 1. Verificar se já existe na pasta local
            if os.path.exists(driver_path):
                return driver_path
            
            # 2. Verificar se existe na pasta de drivers inclusos (para executável)
            included_driver_path = os.path.join(self.base_path, 'drivers', 'geckodriver.exe')
            if os.path.exists(included_driver_path):
                # Copiar para pasta local para uso
                try:
                    import shutil
                    shutil.copy2(included_driver_path, driver_path)
                    return driver_path
                except:
                    # Se não conseguir copiar, usar direto o incluído
                    return included_driver_path
            
            # 3. Tentar baixar da internet
            # URL do GeckoDriver (última versão conhecida)
            urls_to_try = [
                "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-win64.zip",
                "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-win64.zip",
            ]
            
            zip_path = os.path.join(drivers_dir, 'geckodriver.zip')
            
            for url in urls_to_try:
                try:
                    self._download_file_with_ssl(url, zip_path)
                    break
                except:
                    continue
            else:
                raise Exception("Não foi possível baixar o GeckoDriver de nenhuma fonte")
            
            # Extrair o arquivo
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(drivers_dir)
            
            # Remover o arquivo zip
            os.remove(zip_path)
            
            return driver_path
        except Exception as e:
            raise Exception(f"Erro ao obter GeckoDriver: {str(e)}")
    
    def browse_consulta_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha Convertida",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.consulta_input_path.set(filename)
    
    def browse_consulta_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar Planilha com Códigos",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.consulta_output_path.set(filename)
    
    def create_webdriver(self, headless=True):
        """Cria e retorna um webdriver baseado nas configurações do usuário"""
        driver_type = self.driver_type_var.get()
        manual_path = self.driver_manual_path_var.get()
        
        # Inicializar o driver apropriado
        if driver_type == 'Chrome':
            chrome_options = ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            if manual_path:
                service = ChromeService(executable_path=manual_path)
                return webdriver.Chrome(service=service, options=chrome_options)
            else:
                return webdriver.Chrome(options=chrome_options)
                
        elif driver_type == 'Firefox':
            firefox_options = FirefoxOptions()
            if headless:
                firefox_options.add_argument('--headless')
            
            if manual_path:
                service = FirefoxService(executable_path=manual_path)
                return webdriver.Firefox(service=service, options=firefox_options)
            else:
                return webdriver.Firefox(options=firefox_options)
                
        else:  # Edge (padrão)
            edge_options = EdgeOptions()
            if headless:
                edge_options.add_argument('--headless')
                edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            
            if manual_path:
                service = EdgeService(executable_path=manual_path)
                return webdriver.Edge(service=service, options=edge_options)
            else:
                return webdriver.Edge(options=edge_options)
    
    def iniciar_consulta(self):
        """Inicia a consulta de clientes no GSAN"""
        # Validações
        if not self.consulta_input_path.get():
            messagebox.showerror("Erro", "Selecione a planilha de entrada!")
            return
        
        if not self.consulta_output_path.get():
            messagebox.showerror("Erro", "Selecione o local para salvar o resultado!")
            return
        
        if not self.gsan_user_var.get() or not self.gsan_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return
        
        # Executar consulta em thread separada
        self.consulta_running = True
        thread = threading.Thread(target=self.process_consulta)
        thread.daemon = True
        thread.start()
    
    def parar_consulta(self):
        """Para a consulta de clientes"""
        if self.consulta_running:
            self.consulta_running = False
            self.root.after(0, lambda: self.consulta_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def process_consulta(self):
        """Processa a consulta de clientes no GSAN"""
        try:
            self.root.after(0, lambda: self.consulta_status_label.config(text="Inicializando navegador..."))
            self.root.after(0, lambda: self.consulta_progress.config(value=0))
            
            # Criar driver usando o método auxiliar
            self.driver = self.create_webdriver(headless=self.headless_var.get())
            
            # Fazer login
            self.root.after(0, lambda: self.consulta_status_label.config(text="Fazendo login no GSAN..."))
            self.driver.get(self.gsan_url())
            time.sleep(1)
            
            self.driver.find_element(By.NAME, 'login').send_keys(self.gsan_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.gsan_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)
            
            # Carregar planilha
            self.root.after(0, lambda: self.consulta_status_label.config(text="Carregando planilha..."))
            df = pd.read_csv(self.consulta_input_path.get())
            
            total = len(df)
            self.root.after(0, lambda: self.consulta_status_label.config(
                text=f"Consultando {total} registros..."))
            
            # Processar cada linha
            for i in df.index:
                if not self.consulta_running:
                    break
                
                try:
                    # Ir para página de consulta
                    self.driver.get(self.gsan_url("exibirFiltrarClienteAction.do?menu=sim"))
                    time.sleep(0.3)
                    
                    # Pegar CPF/CNPJ
                    cpf = str(df['CPF'][i]) if 'CPF' in df.columns else ''
                    v_cpf = int(df['V_CPF'][i]) if 'V_CPF' in df.columns else 0
                    
                    codigo_encontrado = 0
                    
                    if v_cpf == 1 and cpf and cpf not in ['0', 'nan', '00000000000']:
                        # Formatar CPF
                        cpf_formatado = cpf_ok(cpf)
                        
                        # Inserir CPF e buscar
                        self.driver.find_element(By.NAME, "cpfClienteFiltro").send_keys(cpf_formatado)
                        time.sleep(0.15)
                        self.driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                        time.sleep(0.3)
                        
                        # Verificar se tem popup de erro
                        try:
                            popup = self.driver.switch_to.alert
                            popup.accept()
                        except:
                            # Sem popup, tentar pegar código
                            try:
                                time.sleep(0.3)
                                codigo_encontrado = self.driver.find_element(
                                    By.XPATH, 
                                    "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[1]/td[2]"
                                ).text
                                # Atualizar COD_CLIENTE na linha
                                df.at[i, 'COD_CLIENTE'] = codigo_encontrado
                            except:
                                pass
                    
                    # Atualizar progresso
                    progress = int((i + 1) / total * 100)
                    status_text = f"Consultando: {i+1}/{total} | Último código: {codigo_encontrado}"
                    self.root.after(0, lambda p=progress: self.consulta_progress.config(value=p))
                    self.root.after(0, lambda t=status_text: self.consulta_status_label.config(text=t))
                    
                except Exception as e:
                    print(f"Erro no registro {i}: {e}")
                    continue
            
            # Salvar resultado
            if self.consulta_running:
                self.root.after(0, lambda: self.consulta_status_label.config(text="Salvando resultado..."))
                df.to_csv(self.consulta_output_path.get(), index=False)
                
                self.root.after(0, lambda: self.consulta_progress.config(value=100))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Consulta concluída!\n{total} registros processados.\n\nArquivo salvo em:\n{self.consulta_output_path.get()}"
                ))
                self.root.after(0, lambda: self.consulta_status_label.config(
                    text=f"✓ Concluído! {total} registros consultados."))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante consulta:\n{str(e)}"))
            self.root.after(0, lambda: self.consulta_status_label.config(text="✗ Erro na consulta"))
        
        finally:
            self.consulta_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    # ===== MÉTODOS DA ABA DE CRIAR CÓDIGO DE CLIENTE =====
    
    def browse_criar_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha Convertida",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.criar_input_path.set(filename)
    
    def browse_criar_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar Planilha com Códigos Criados",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.criar_output_path.set(filename)
    
    def iniciar_criar(self):
        """Inicia a criação de códigos de cliente no GSAN"""
        # Validações
        if not self.criar_input_path.get():
            messagebox.showerror("Erro", "Selecione a planilha de entrada!")
            return
        
        if not self.criar_output_path.get():
            messagebox.showerror("Erro", "Selecione o local para salvar o resultado!")
            return
        
        if not self.criar_user_var.get() or not self.criar_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return
        
        # Executar criação em thread separada
        self.criar_running = True
        thread = threading.Thread(target=self.process_criar)
        thread.daemon = True
        thread.start()
    
    def parar_criar(self):
        """Para a criação de códigos de cliente"""
        if self.criar_running:
            self.criar_running = False
            self.root.after(0, lambda: self.criar_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def process_criar(self):
        """Processa a criação de códigos de cliente no GSAN"""
        try:
            self.root.after(0, lambda: self.criar_status_label.config(text="Inicializando navegador..."))
            self.root.after(0, lambda: self.criar_progress.config(value=0))
            
            # Criar arquivo de log
            log_dir = os.path.dirname(self.criar_output_path.get())
            log_filename = os.path.splitext(os.path.basename(self.criar_output_path.get()))[0] + "_log_clientes.txt"
            log_path = os.path.join(log_dir, log_filename)
            
            with open(log_path, 'w', encoding='utf-8') as log_file:
                log_file.write(f"=== LOG DE CRIAÇÃO DE CLIENTES ===\n")
                log_file.write(f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                log_file.write(f"Arquivo: {self.criar_input_path.get()}\n")
                log_file.write(f"="*50 + "\n\n")
            
            # Criar driver usando o método auxiliar
            self.driver = self.create_webdriver(headless=self.criar_headless_var.get())
            
            # Fazer login
            self.root.after(0, lambda: self.criar_status_label.config(text="Fazendo login no GSAN..."))
            self.driver.get(self.gsan_url())
            time.sleep(1)
            
            self.driver.find_element(By.NAME, 'login').send_keys(self.criar_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.criar_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)
            
            # Carregar planilha
            self.root.after(0, lambda: self.criar_status_label.config(text="Carregando planilha..."))
            df = pd.read_csv(self.criar_input_path.get())
            
            # Filtrar apenas registros que precisam ser processados
            # Aceitar ALTERAR=1 e COD_CLIENTE como 0 (int), '0' (string), vazio ou NaN
            df_filtrado = df[
                ((df['ALTERAR'] == 1) | (df['ALTERAR'] == '1')) & 
                ((df['COD_CLIENTE'] == 0) | (df['COD_CLIENTE'] == '0') | 
                 (df['COD_CLIENTE'].astype(str).str.strip() == '0') |
                 (df['COD_CLIENTE'].isna()))
            ]
            total = len(df_filtrado)
            
            if total == 0:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Aviso",
                    "Nenhum registro precisa ser processado!\n\nVerifique se há registros com ALTERAR=1 e COD_CLIENTE=0"
                ))
                return
            
            self.root.after(0, lambda: self.criar_status_label.config(
                text=f"Criando {total} clientes..."))
            
            # Criar lista para armazenar códigos criados
            codigos_criados = []
            
            # Processar cada linha
            for idx, (i, row) in enumerate(df_filtrado.iterrows()):
                if not self.criar_running:
                    break
                
                try:
                    # Ir para página de inserir cliente
                    self.driver.get(self.gsan_url("exibirInserirClienteAction.do?menu=sim"))
                    time.sleep(0.3)
                    
                    # Pegar dados do cliente
                    nome = str(row['NOME']) if 'NOME' in row else ''
                    cpf_val = str(row['CPF']) if 'CPF' in row else ''
                    cnpj_val = str(row['CNPJ']) if 'CNPJ' in row else ''
                    v_cpf = int(row['V_CPF']) if 'V_CPF' in row else 0
                    v_cnpj = int(row['V_CNPJ']) if 'V_CNPJ' in row else 0
                    tipo_pessoa = str(row['TIPO_CLIENTE']) if 'TIPO_CLIENTE' in row else ''
                    email = str(row['EMAIL']) if 'EMAIL' in row else '0'
                    rg = str(row['RG']) if 'RG' in row else '0'
                    data_exp = str(row['DATA_EXP']) if 'DATA_EXP' in row else '0'
                    data_nasc = str(row['DATA_NASC']) if 'DATA_NASC' in row else '0'
                    sexo = str(row['SEXO']) if 'SEXO' in row else ''
                    mae = str(row['MAE']) if 'MAE' in row else '0'
                    cod_log = str(row['COD_LOG']) if 'COD_LOG' in row else ''
                    bairro = str(row['BAIRRO']) if 'BAIRRO' in row else ''
                    numero = str(row['NUMERO']) if 'NUMERO' in row else ''
                    complemento = str(row['COMPLEMENTO']) if 'COMPLEMENTO' in row else '0'
                    ddd = str(row['DDD']) if 'DDD' in row else '0'
                    telefone = str(row['TELEFONE']) if 'TELEFONE' in row else '0'
                    cep_gsan = int(row['CEP_GSAN']) if 'CEP_GSAN' in row else 0
                    
                    codigo_criado = 0
                    
                    # Processar Pessoa Física
                    if v_cpf == 1:
                        cpf_formatado = cpf_ok(cpf_val)
                        
                        # Preencher dados básicos
                        self.driver.find_element(By.NAME, "nome").send_keys(nome)
                        self.driver.find_element(By.XPATH, "//input[@name='indicadorPessoaFisicaJuridica' and @value='1']").click()
                        
                        if email != '0':
                            self.driver.find_element(By.NAME, "email").send_keys(email)
                        
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "tipoPessoa").send_keys(tipo_pessoa)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.3)
                        
                        # CPF
                        if cpf_formatado == '00000000000':
                            cpf_formatado = ''
                        self.driver.find_element(By.NAME, "cpf").send_keys(cpf_formatado, Keys.ENTER)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='1']").click()
                        time.sleep(0.2)
                        
                        # RG e data
                        if data_exp != '0' and rg != '0':
                            rg_formatado = rg[:13] if len(rg) > 13 else rg.zfill(13)
                            self.driver.find_element(By.NAME, "rg").send_keys(rg_formatado)
                            self.driver.find_element(By.NAME, "dataEmissao").send_keys(data_exp)
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "idOrgaoExpedidor").send_keys('SSP')
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "idUnidadeFederacao").send_keys('MA')
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "dataNascimento").send_keys(data_nasc)
                        
                        self.driver.find_element(By.NAME, "idPessoaSexo").send_keys(sexo)
                        if mae != '0':
                            self.driver.find_element(By.NAME, "nomeMae").send_keys(mae)
                        
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.7)
                        
                    # Processar Pessoa Jurídica
                    elif v_cnpj == 1:
                        cnpj_formatado = cnpj_val[:14] if len(cnpj_val) > 14 else cnpj_val.zfill(14)
                        
                        self.driver.find_element(By.NAME, "nome").send_keys(nome)
                        self.driver.find_element(By.XPATH, "//input[@name='indicadorPessoaFisicaJuridica' and @value='2']").click()
                        time.sleep(0.2)
                        
                        if email != '0':
                            self.driver.find_element(By.NAME, "email").send_keys(email)
                        
                        self.driver.find_element(By.NAME, "tipoPessoa").send_keys(tipo_pessoa)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.2)
                        
                        if cnpj_formatado == '00000000000000':
                            cnpj_formatado = ''
                        
                        self.driver.find_element(By.NAME, "cnpj").send_keys(cnpj_formatado, Keys.ENTER)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='1']").click()
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "idRamoAtividade").send_keys(tipo_pessoa)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.6)
                    
                    # Adicionar endereço
                    self.driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                    time.sleep(0.2)
                    janela_principal = self.driver.window_handles[0]
                    janela_endereco = self.driver.window_handles[1]
                    self.driver.switch_to.window(janela_endereco)
                    time.sleep(0.2)
                    
                    self.driver.find_element(By.NAME, "tipo").send_keys('01 - RESIDENCIAL')
                    time.sleep(0.2)
                    self.driver.find_element(By.NAME, "logradouro").send_keys(cod_log, Keys.ENTER)
                    time.sleep(0.2)
                    self.driver.find_element(By.XPATH, f"//input[@value='{cep_gsan}']").click()
                    time.sleep(0.2)
                    self.driver.find_element(By.NAME, "bairro").send_keys(bairro)
                    time.sleep(0.2)
                    self.driver.find_element(By.NAME, "numero").send_keys(numero)
                    time.sleep(0.2)
                    
                    if complemento != '0':
                        self.driver.find_element(By.NAME, "complemento").send_keys(complemento)
                    
                    time.sleep(0.2)
                    self.driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                    time.sleep(0.2)
                    self.driver.close()
                    self.driver.switch_to.window(janela_principal)
                    time.sleep(0.2)
                    self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                    
                    # Adicionar telefone
                    if ddd != '0' and telefone != '0':
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "idTipoTelefone").send_keys('03 - CELULAR')
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "idMunicipio").send_keys('1', Keys.ENTER)
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "ddd").clear()
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "ddd").send_keys(ddd)
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "telefone").send_keys(telefone)
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "contato").send_keys(nome)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                        time.sleep(0.4)
                    
                    # Concluir
                    time.sleep(0.5)
                    self.driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                    time.sleep(0.3)
                    
                    # Capturar código criado
                    try:
                        msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                        # Extrair código da mensagem (formato: "Cliente inserido com sucesso. Código: 12345678")
                        codigo_criado = msg_ok[18:26].strip() if len(msg_ok) > 26 else '0'
                        
                        # Atualizar COD_CLIENTE na linha original
                        df.at[i, 'COD_CLIENTE'] = codigo_criado
                        codigos_criados.append((i, codigo_criado, msg_ok))
                        
                        # Salvar no log imediatamente
                        with open(log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"✓ SUCESSO | Linha {i} | Cliente: {codigo_criado} | Nome: {nome}\n")
                        
                    except Exception as e:
                        codigos_criados.append((i, '0', 'Erro ao capturar código'))
                        # Salvar erro no log
                        with open(log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"✗ ERRO | Linha {i} | Falha ao capturar código: {str(e)}\n")
                    
                    # Atualizar progresso
                    progress = int((idx + 1) / total * 100)
                    status_text = f"Criando: {idx+1}/{total} | Último código: {codigo_criado}"
                    self.root.after(0, lambda p=progress: self.criar_progress.config(value=p))
                    self.root.after(0, lambda t=status_text: self.criar_status_label.config(text=t))
                    
                except Exception as e:
                    print(f"Erro no registro {i}: {e}")
                    codigos_criados.append((i, '0', f'Erro: {str(e)}'))
                    # Salvar erro no log
                    with open(log_path, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"✗ ERRO CRÍTICO | Linha {i} | {str(e)}\n")
                    continue
            
            # Salvar resultado
            if self.criar_running:
                self.root.after(0, lambda: self.criar_status_label.config(text="Salvando resultado..."))
                df.to_csv(self.criar_output_path.get(), index=False)
                
                # Contar quantos foram criados com sucesso
                sucesso = sum(1 for _, cod, _ in codigos_criados if cod != '0')
                
                # Finalizar log
                with open(log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"\n" + "="*50 + "\n")
                    log_file.write(f"RESUMO FINAL:\n")
                    log_file.write(f"Total processado: {total}\n")
                    log_file.write(f"Sucessos: {sucesso}\n")
                    log_file.write(f"Erros: {total - sucesso}\n")
                    log_file.write(f"Data/Hora Final: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                
                self.root.after(0, lambda: self.criar_progress.config(value=100))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Criação concluída!\n{sucesso}/{total} clientes criados com sucesso.\n\nArquivo salvo em:\n{self.criar_output_path.get()}\n\nLog salvo em:\n{log_path}"
                ))
                self.root.after(0, lambda: self.criar_status_label.config(
                    text=f"✓ Concluído! {sucesso}/{total} clientes criados."))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante criação:\n{str(e)}"))
            self.root.after(0, lambda: self.criar_status_label.config(text="✗ Erro na criação"))
        
        finally:
            self.criar_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    # ===== MÉTODOS DA ABA DE CRIAR ROTAS =====
    
    def iniciar_rotas(self):
        """Inicia a criação de rotas no GSAN"""
        # Validações
        if not self.rotas_user_var.get() or not self.rotas_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return

        if (not self.rotas_faturamento_var.get().strip() or
            not self.rotas_cobranca_var.get().strip() or
            not self.rotas_leitura_tipo_var.get().strip() or
            not self.rotas_empresa_leitura_var.get().strip() or
            not self.rotas_empresa_cobranca_var.get().strip() or
            not self.rotas_empresa_entrega_var.get().strip()):
            messagebox.showerror("Erro", "Preencha os parâmetros operacionais de rota!")
            return
        
        try:
            rota_ini = int(self.rotas_inicial_var.get())
            rota_fim = int(self.rotas_final_var.get())
            if rota_ini > rota_fim:
                messagebox.showerror("Erro", "Rota inicial deve ser menor ou igual à rota final!")
                return
        except:
            messagebox.showerror("Erro", "Valores de rota devem ser numéricos!")
            return
        
        # Executar criação em thread separada
        self.rotas_running = True
        thread = threading.Thread(target=self.process_rotas)
        thread.daemon = True
        thread.start()
    
    def parar_rotas(self):
        """Para a criação de rotas"""
        if self.rotas_running:
            self.rotas_running = False
            self.root.after(0, lambda: self.rotas_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def process_rotas(self):
        """Processa a criação de rotas no GSAN"""
        try:
            self.root.after(0, lambda: self.rotas_status_label.config(text="Inicializando navegador..."))
            self.root.after(0, lambda: self.rotas_progress.config(value=0))
            
            # Criar driver usando o método auxiliar
            self.driver = self.create_webdriver(headless=self.rotas_headless_var.get())
            
            # Fazer login
            self.root.after(0, lambda: self.rotas_status_label.config(text="Fazendo login no GSAN..."))
            self.driver.get(self.gsan_url())
            time.sleep(1)
            
            self.driver.find_element(By.NAME, 'login').send_keys(self.rotas_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.rotas_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)
            
            # Pegar parâmetros
            localidade = self.rotas_localidade_var.get()
            setor = self.rotas_setor_var.get()
            rota_inicial = int(self.rotas_inicial_var.get())
            rota_final = int(self.rotas_final_var.get())
            leiturista = self.rotas_leiturista_var.get()
            faturamento_grupo = self.rotas_faturamento_var.get().strip()
            cobranca_grupo = self.rotas_cobranca_var.get().strip()
            leitura_tipo = self.rotas_leitura_tipo_var.get().strip()
            empresa_leitura = self.rotas_empresa_leitura_var.get().strip()
            empresa_cobranca = self.rotas_empresa_cobranca_var.get().strip()
            empresa_entrega = self.rotas_empresa_entrega_var.get().strip()
            ind_fiscalizar_cortado = self.rotas_fiscalizar_cortado_var.get().strip() or '2'
            ind_fiscalizar_suprimido = self.rotas_fiscalizar_suprimido_var.get().strip() or '2'
            ind_armazenar_coord = self.rotas_armazenar_coord_var.get().strip() or '1'
            ind_gerar_falsa_faixa = self.rotas_gerar_falsa_faixa_var.get().strip() or '2'
            ind_gerar_fiscalizacao = self.rotas_gerar_fiscalizacao_var.get().strip() or '2'
            
            total_rotas = rota_final - rota_inicial + 1
            self.root.after(0, lambda: self.rotas_status_label.config(
                text=f"Criando {total_rotas} rotas..."))
            
            rotas_criadas = []
            
            for rota in range(rota_inicial, rota_final + 1):
                if not self.rotas_running:
                    break
                
                try:
                    self.driver.get(self.gsan_url("exibirInserirRotaAction.do?menu=sim"))
                    time.sleep(0.5)
                    
                    self.driver.find_element(By.NAME, "idLocalidade").send_keys(localidade, Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "codigoSetorComercial").send_keys(setor, Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "idLeiturista").send_keys(leiturista, Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "codigoRota").clear()
                    self.driver.find_element(By.NAME, "codigoRota").send_keys(str(rota))
                    time.sleep(0.5)
                    
                    self.driver.find_element(By.NAME, "faturamentoGrupo").send_keys(faturamento_grupo)
                    self.driver.find_element(By.NAME, "cobrancaGrupo").send_keys(cobranca_grupo)
                    self.driver.find_element(By.NAME, "leituraTipo").send_keys(leitura_tipo)
                    self.driver.find_element(By.NAME, "empresaLeituristica").send_keys(empresa_leitura)
                    self.driver.find_element(By.NAME, "empresaCobranca").send_keys(empresa_cobranca)
                    self.driver.find_element(By.NAME, "empresaEntregaContas").send_keys(empresa_entrega)
                    self.driver.find_element(By.XPATH, f"//input[@name='indicadorFiscalizarCortado' and @value='{ind_fiscalizar_cortado}']").click()
                    self.driver.find_element(By.XPATH, f"//input[@name='indicadorFiscalizarSuprimido' and @value='{ind_fiscalizar_suprimido}']").click()
                    self.driver.find_element(By.XPATH, f"//input[@name='indicadorArmazenarCoordenadas' and @value='{ind_armazenar_coord}']").click()
                    self.driver.find_element(By.XPATH, f"//input[@name='indicadorGerarFalsaFaixa' and @value='{ind_gerar_falsa_faixa}']").click()
                    self.driver.find_element(By.XPATH, f"//input[@name='indicadorGerarFiscalizacao' and @value='{ind_gerar_fiscalizacao}']").click()
                    self.driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                    
                    time.sleep(0.5)
                    
                    try:
                        msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                        rotas_criadas.append((rota, msg_ok))
                    except:
                        msg_er = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        rotas_criadas.append((rota, msg_er))
                    
                    # Atualizar progresso
                    progress = int(((rota - rota_inicial + 1) / total_rotas) * 100)
                    status_text = f"Criando rotas: {rota - rota_inicial + 1}/{total_rotas} | Rota: {rota}"
                    self.root.after(0, lambda p=progress: self.rotas_progress.config(value=p))
                    self.root.after(0, lambda t=status_text: self.rotas_status_label.config(text=t))
                    
                except Exception as e:
                    print(f"Erro na rota {rota}: {e}")
                    rotas_criadas.append((rota, f'Erro: {str(e)}'))
                    continue
            
            if self.rotas_running:
                sucesso = len([r for r in rotas_criadas if 'sucesso' in r[1].lower()])
                
                self.root.after(0, lambda: self.rotas_progress.config(value=100))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Criação de rotas concluída!\n{sucesso}/{total_rotas} rotas criadas com sucesso."
                ))
                self.root.after(0, lambda: self.rotas_status_label.config(
                    text=f"✓ Concluído! {sucesso}/{total_rotas} rotas criadas."))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante criação de rotas:\n{str(e)}"))
            self.root.after(0, lambda: self.rotas_status_label.config(text="✗ Erro na criação"))
        
        finally:
            self.rotas_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    # ===== MÉTODOS DA ABA DE CRIAR QUADRAS =====
    
    def browse_quadras_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha Convertida",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.quadras_input_path.set(filename)
    
    def iniciar_quadras(self):
        """Inicia a criação de quadras no GSAN"""
        # Validações
        if not self.quadras_input_path.get():
            messagebox.showerror("Erro", "Selecione a planilha de entrada!")
            return
        
        if not self.quadras_user_var.get() or not self.quadras_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return
        
        # Executar criação em thread separada
        self.quadras_running = True
        thread = threading.Thread(target=self.process_quadras)
        thread.daemon = True
        thread.start()
    
    def parar_quadras(self):
        """Para a criação de quadras"""
        if self.quadras_running:
            self.quadras_running = False
            self.root.after(0, lambda: self.quadras_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def process_quadras(self):
        """Processa a criação de quadras no GSAN"""
        try:
            self.root.after(0, lambda: self.quadras_status_label.config(text="Inicializando navegador..."))
            self.root.after(0, lambda: self.quadras_progress.config(value=0))
            
            # Criar driver usando o método auxiliar
            self.driver = self.create_webdriver(headless=self.quadras_headless_var.get())
            
            # Fazer login
            self.root.after(0, lambda: self.quadras_status_label.config(text="Fazendo login no GSAN..."))
            self.driver.get(self.gsan_url())
            time.sleep(1)
            
            self.driver.find_element(By.NAME, 'login').send_keys(self.quadras_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.quadras_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)
            
            # Carregar planilha
            self.root.after(0, lambda: self.quadras_status_label.config(text="Carregando planilha..."))
            df = pd.read_csv(self.quadras_input_path.get())
            
            # Criar tabela dinâmica com quadras únicas
            self.root.after(0, lambda: self.quadras_status_label.config(text="Processando quadras únicas..."))
            df_unique = df[['LOCAL', 'SETOR', 'QUADRA', 'ROTA']].drop_duplicates()
            
            total = len(df_unique)
            cod_bairro = self.quadras_bairro_var.get()
            
            self.root.after(0, lambda: self.quadras_status_label.config(
                text=f"Criando {total} quadras únicas..."))
            
            # Lista para contabilizar resultados
            quadras_criadas = []
            
            # Processar cada linha única
            for idx, row in df_unique.iterrows():
                if not self.quadras_running:
                    break
                
                try:
                    self.driver.get(self.gsan_url("exibirInserirQuadraAction.do?menu=sim"))
                    
                    local = int(row['LOCAL'])
                    setor = int(row['SETOR'])
                    quadra = int(row['QUADRA'])
                    rota = int(row['ROTA'])
                    
                    self.driver.find_element(By.NAME, "localidadeID").send_keys(str(local), Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "setorComercialCD").send_keys(str(setor), Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "quadraNM").clear()
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "quadraNM").send_keys(str(quadra))
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "codigoRota").send_keys(str(rota), Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "bairroID").send_keys(cod_bairro, Keys.ENTER)
                    time.sleep(0.5)
                    
                    self.driver.find_element(By.XPATH, "//input[@name='indicadorIncrementoLote' and @value='2']").click()
                    self.driver.find_element(By.NAME, "areaTipoID").send_keys('URBANA')
                    time.sleep(0.2)
                    self.driver.find_element(By.NAME, "perfilQuadra").send_keys('NORMAL')
                    time.sleep(0.2)
                    self.driver.find_element(By.XPATH, "//input[@name='indicadorRedeAguaAux' and @value='3']").click()
                    self.driver.find_element(By.XPATH, "//input[@name='indicadorRedeEsgotoAux' and @value='1']").click()
                    
                    self.driver.find_element(By.NAME, "distritoOperacionalID").send_keys(str(local), Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "setorCensitarioID").send_keys('1', Keys.ENTER)
                    time.sleep(0.5)
                    self.driver.find_element(By.NAME, "zeisID").send_keys('ZEIS 1')
                    
                    self.driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                    time.sleep(0.3)
                    
                    try:
                        msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                        quadras_criadas.append((quadra, True, msg_ok))
                    except:
                        msg_er = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        quadras_criadas.append((quadra, False, msg_er))
                    
                    # Atualizar progresso
                    current = len(quadras_criadas)
                    progress = int((current / total) * 100)
                    status_text = f"Criando quadras: {current}/{total} | Quadra: {quadra}"
                    self.root.after(0, lambda p=progress: self.quadras_progress.config(value=p))
                    self.root.after(0, lambda t=status_text: self.quadras_status_label.config(text=t))
                    
                except Exception as e:
                    print(f"Erro na quadra {quadra}: {e}")
                    quadras_criadas.append((quadra, False, f'Erro: {str(e)}'))
                    continue
            
            # Finalizar
            if self.quadras_running:
                sucesso = sum(1 for _, ok, _ in quadras_criadas if ok)
                
                self.root.after(0, lambda: self.quadras_progress.config(value=100))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Criação de quadras concluída!\n{sucesso}/{total} quadras únicas criadas com sucesso."
                ))
                self.root.after(0, lambda: self.quadras_status_label.config(
                    text=f"✓ Concluído! {sucesso}/{total} quadras criadas."))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante criação de quadras:\n{str(e)}"))
            self.root.after(0, lambda: self.quadras_status_label.config(text="✗ Erro na criação"))
        
        finally:
            self.quadras_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    # ===== MÉTODOS DA ABA DE CRIAR MATRÍCULAS =====
    
    def browse_matriculas_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a Planilha Convertida",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.matriculas_input_path.set(filename)
    
    def browse_matriculas_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar Planilha com Matrículas",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.matriculas_output_path.set(filename)
    
    def iniciar_matriculas(self):
        """Inicia a criação de matrículas no GSAN"""
        # Validações
        if not self.matriculas_input_path.get():
            messagebox.showerror("Erro", "Selecione a planilha de entrada!")
            return
        
        if not self.matriculas_output_path.get():
            messagebox.showerror("Erro", "Selecione o local para salvar o resultado!")
            return
        
        if not self.matriculas_user_var.get() or not self.matriculas_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return
        
        # Executar criação em thread separada
        self.matriculas_running = True
        thread = threading.Thread(target=self.process_matriculas)
        thread.daemon = True
        thread.start()
    
    def parar_matriculas(self):
        """Para a criação de matrículas"""
        if self.matriculas_running:
            self.matriculas_running = False
            self.root.after(0, lambda: self.matriculas_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def process_matriculas(self):
        """Processa a criação de matrículas no GSAN"""
        try:
            self.root.after(0, lambda: self.matriculas_status_label.config(text="Inicializando navegador..."))
            self.root.after(0, lambda: self.matriculas_progress.config(value=0))
            
            # Criar arquivo de log
            log_dir = os.path.dirname(self.matriculas_output_path.get())
            log_filename = os.path.splitext(os.path.basename(self.matriculas_output_path.get()))[0] + "_log_matriculas.txt"
            log_path = os.path.join(log_dir, log_filename)
            
            with open(log_path, 'w', encoding='utf-8') as log_file:
                log_file.write(f"=== LOG DE CRIAÇÃO DE MATRÍCULAS ===\n")
                log_file.write(f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                log_file.write(f"Arquivo: {self.matriculas_input_path.get()}\n")
                log_file.write(f"="*50 + "\n\n")
            
            # Criar driver usando o método auxiliar
            self.driver = self.create_webdriver(headless=self.matriculas_headless_var.get())
            
            # Fazer login
            self.root.after(0, lambda: self.matriculas_status_label.config(text="Fazendo login no GSAN..."))
            self.driver.get(self.gsan_url())
            time.sleep(1)
            
            self.driver.find_element(By.NAME, 'login').send_keys(self.matriculas_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.matriculas_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)
            
            # Carregar planilha
            self.root.after(0, lambda: self.matriculas_status_label.config(text="Carregando planilha..."))
            df = pd.read_csv(self.matriculas_input_path.get())
            
            total = len(df)
            
            self.root.after(0, lambda: self.matriculas_status_label.config(
                text=f"Processando {total} registros..."))
            
            # Processar cada linha
            matriculas_criadas = []
            contador = 0
            
            for i in df.index:
                if not self.matriculas_running:
                    break
                
                contador = i + 1
                local = int(df['LOCAL'][i])
                setor = int(df['SETOR'][i])
                quadra = int(df['QUADRA'][i])
                lote = int(df['LOTE'][i])
                sublote = int(df['SUBLOTE'][i])
                sequencia = int(df['LOTE'][i])
                id_cliente = str(df['COD_CLIENTE'][i])
                matricula = int(df['MATRICULA'][i])
                tipo_hab = str(df['TIPO_HAB'][i])
                complemento = str(df['COMPLEMENTO'][i])
                cx = str(df['CX'][i])
                cy = str(df['CY'][i])
                cep_gsan = int(df['CEP_GSAN'][i])
                
                if matricula == 0:
                    try:
                        self.driver.get(self.gsan_url("exibirInserirImovelAction.do?menu=sim"))
                        self.driver.find_element(By.NAME, "idLocalidade").clear()
                        self.driver.find_element(By.NAME, "idLocalidade").send_keys(str(local))
                        self.driver.find_element(By.NAME, "idSetorComercial").clear()
                        self.driver.find_element(By.NAME, "idSetorComercial").send_keys(str(setor))
                        self.driver.find_element(By.NAME, "idQuadra").clear()
                        self.driver.find_element(By.NAME, "idQuadra").send_keys(str(quadra), Keys.ENTER)
                        time.sleep(0.3)
                        self.driver.find_element(By.NAME, "lote").clear()
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "lote").send_keys(str(lote))
                        self.driver.find_element(By.NAME, "subLote").clear()
                        self.driver.find_element(By.NAME, "subLote").send_keys(str(sublote))
                        self.driver.find_element(By.NAME, "sequencialRota").clear()
                        self.driver.find_element(By.NAME, "sequencialRota").send_keys(str(sequencia))
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.3)
                        
                        try:
                            self.driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                        except:
                            pass
                        
                        time.sleep(0.5)
                        self.driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                        time.sleep(0.3)
                        janela_principal = self.driver.window_handles[0]
                        janela_endereco = self.driver.window_handles[1]
                        self.driver.switch_to.window(janela_endereco)
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "logradouro").send_keys(str(df['COD_LOG'][i]), Keys.ENTER)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, f"//input[@value='{cep_gsan}']").click()
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
                        if complemento != '0':
                            self.driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))
                        
                        self.driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                        time.sleep(0.2)
                        self.driver.switch_to.window(janela_principal)
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.4)
                        self.driver.find_element(By.NAME, "idCliente").send_keys(str(df['COD_CLIENTE'][i]), Keys.ENTER)
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.2)
                        
                        categoria_res = int(df['RES'][i])
                        categoria_com = int(df['COM'][i])
                        categoria_pub = int(df['PUB'][i])
                        categoria_pub_mun = int(df['MUN'][i])
                        categoria_pub_est = int(df['EST'][i])
                        categoria_pub_fed = int(df['FED'][i])
                        categoria_com_peq = int(df['PEQ'][i])
                        categoria_ind = int(df['IND'][i])
                        time.sleep(0.2)
                        
                        if categoria_res >= 1:                
                            self.driver.find_element(By.XPATH, "//select[@name='idCategoria']").send_keys('')
                            self.driver.find_element(By.XPATH, "//option[@value='1']").click()                
                            time.sleep(0.4)
                            self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0') 
                            time.sleep(0.2)    
                            self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0')                
                            time.sleep(0.4)
                            self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_res)
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "botaoAdicionar").click()                
                        if categoria_pub >= 1:
                            if categoria_pub_mun >= 1:
                                self.driver.find_element(By.XPATH, "//select[@name='idCategoria']").send_keys('')
                                self.driver.find_element(By.XPATH, "//option[@value='4']").click()                
                                time.sleep(0.4)
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0') 
                                time.sleep(0.2)    
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0')
                                time.sleep(0.4)
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0')
                                time.sleep(0.4)
                                self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                                time.sleep(0.2)
                                self.driver.find_element(By.NAME, "botaoAdicionar").click()
                                time.sleep(0.2)
                        if categoria_pub >= 1:
                            if categoria_pub_est >= 1:
                                self.driver.find_element(By.XPATH, "//select[@name='idCategoria']").send_keys('')
                                self.driver.find_element(By.XPATH, "//option[@value='4']").click()                
                                time.sleep(0.4)
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0') 
                                time.sleep(0.2)    
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0')
                                time.sleep(0.4)                    
                                self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                                time.sleep(0.2)
                                self.driver.find_element(By.NAME, "botaoAdicionar").click()
                                time.sleep(0.2)

                        if categoria_pub >= 1:
                            if categoria_pub_fed >= 1:
                                self.driver.find_element(By.XPATH, "//select[@name='idCategoria']").send_keys('')
                                self.driver.find_element(By.XPATH, "//option[@value='4']").click()                
                                time.sleep(0.4)
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0') 
                                time.sleep(0.2)    
                                self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0')
                                time.sleep(0.4)  
                                self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_pub)
                                time.sleep(0.2)
                                self.driver.find_element(By.NAME, "botaoAdicionar").click()
                                time.sleep(0.2)
                        if categoria_com >= 1:
                            self.driver.find_element(By.XPATH, "//select[@name='idCategoria']").send_keys('')
                            self.driver.find_element(By.XPATH, "//option[@value='2']").click()                
                            time.sleep(0.4)
                            self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0') 
                            time.sleep(0.2)                    
                            self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com)
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "botaoAdicionar").click()  
                            time.sleep(0.2)          
                        if categoria_com_peq >= 1:
                            self.driver.find_element(By.XPATH, "//select[@name='idCategoria']").send_keys('')
                            self.driver.find_element(By.XPATH, "//option[@value='2']").click()                
                            time.sleep(0.4)
                            self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0') 
                            time.sleep(0.2)    
                            self.driver.find_element(By.XPATH, "//select[@name='idSubCategoria']").send_keys('0')
                            time.sleep(0.2) 
                            self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_com_peq)
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "botaoAdicionar").click()
                        if categoria_ind >= 1:
                            self.driver.find_element(By.NAME, "idCategoria").send_keys('03 - INDUSTRIAL')
                            time.sleep(0.4)
                            self.driver.find_element(By.NAME, "idSubCategoria").send_keys('03 - INDUSTRIAL')
                            time.sleep(0.4)
                            self.driver.find_element(By.NAME, "quantidadeEconomia").send_keys(categoria_ind)
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "botaoAdicionar").click()
                            time.sleep(0.2)
                        
                        time.sleep(0.5)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.3)
                        
                        self.driver.find_element(By.NAME, "areaConstruida").send_keys(str(df['AREA'][i]), '00')
                        time.sleep(0.2)
                        self.driver.find_element(By.NAME, "pavimentoCalcada").send_keys('02 - CIMENTO')
                        self.driver.find_element(By.NAME, "pavimentoRua").send_keys('02 - ASFALTO')
                        self.driver.find_element(By.NAME, "fonteAbastecimento").send_keys('01 - CAEMA')
                        self.driver.find_element(By.NAME, "situacaoLigacaoAgua").send_keys('02 - FACTIVEL')
                        self.driver.find_element(By.NAME, "situacaoLigacaoEsgoto").send_keys('01 - POTENCIAL')
                        self.driver.find_element(By.NAME, "perfilImovel").send_keys('05 - NORMAL')
                        self.driver.find_element(By.NAME, "tipoDespejo").send_keys('01 - RESIDENCIAL')
                        
                        time.sleep(0.2)
                        
                        if tipo_hab == '0':
                            self.driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('04 - TERRENO')
                            self.driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('09 - OUTROS')
                            self.driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('09 - OUTROS')
                            self.driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('09 - OUTROS')
                        elif tipo_hab == '1':
                            self.driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('01 - HABITADO')
                            self.driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('01 - PROPRIO')
                            self.driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('03 - ALVENARIA')
                            self.driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('02 - TELHA CERAMICA')
                        elif tipo_hab == '2':
                            self.driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('05 - CONSTRUCAO')
                            self.driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('01 - PROPRIO')
                            self.driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('03 - ALVENARIA')
                            self.driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('02 - TELHA CERAMICA')
                        
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Avançar']").click()
                        time.sleep(0.2)
                        
                        if cx != "0":
                            self.driver.find_element(By.NAME, "cordenadasUtmX").send_keys(cx)
                            self.driver.find_element(By.NAME, "cordenadasUtmY").send_keys(cy)
                        
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                        time.sleep(0.2)
                        
                        msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                        
                        # Salvar no log imediatamente
                        with open(log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"✓ Linha {i+1} | {msg_ok}\n")
                        
                        # Extrair matrícula e atualizar DataFrame
                        import re
                        match = re.search(r'Matrícula:\s*(\d+)', msg_ok)
                        if match:
                            matricula_criada = match.group(1)
                            df.at[i, 'MATRICULA'] = int(matricula_criada)
                            matriculas_criadas.append((i+1, matricula_criada, msg_ok))
                        else:
                            matriculas_criadas.append((i+1, '0', msg_ok))
                        
                    except Exception as e:
                        msg_er = f"Erro: {str(e)}"
                        with open(log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"✗ Linha {i+1} | {msg_er}\n")
                        matriculas_criadas.append((i+1, '0', msg_er))
                        
                else:
                    try:
                        msg_er = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        with open(log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"⊘ Linha {i+1} | {msg_er}\n")
                        matriculas_criadas.append((i+1, str(matricula), msg_er))
                    except:
                        msg_er = f"JA POSSUI MATRICULA [{matricula}]"
                        with open(log_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"⊘ Linha {i+1} | {msg_er}\n")
                        matriculas_criadas.append((i+1, str(matricula), msg_er))
                
                # Atualizar progresso
                progress = int((contador / total) * 100)
                status_text = f"Processando: {contador}/{total} | Última linha: {i+1}"
                self.root.after(0, lambda p=progress: self.matriculas_progress.config(value=p))
                self.root.after(0, lambda t=status_text: self.matriculas_status_label.config(text=t))
            
            
            # Salvar resultado
            if self.matriculas_running:
                self.root.after(0, lambda: self.matriculas_status_label.config(text="Salvando resultado..."))
                
                # Garantir que as matrículas atualizadas sejam salvas no arquivo
                df.to_csv(self.matriculas_output_path.get(), index=False, encoding='utf-8-sig')
                
                sucesso = sum(1 for _, mat, _ in matriculas_criadas if mat != '0' and 'POSSUI MATRICULA' not in str(_))
                
                # Finalizar log
                with open(log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"\n" + "="*50 + "\n")
                    log_file.write(f"RESUMO FINAL:\n")
                    log_file.write(f"Total processado: {total}\n")
                    log_file.write(f"Sucessos: {sucesso}\n")
                    log_file.write(f"Data/Hora Final: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                
                self.root.after(0, lambda: self.matriculas_progress.config(value=100))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Processamento concluído!\n{sucesso}/{total} matrículas criadas com sucesso.\n\nArquivo salvo em:\n{self.matriculas_output_path.get()}\n\nLog salvo em:\n{log_path}"
                ))
                self.root.after(0, lambda: self.matriculas_status_label.config(
                    text=f"✓ Concluído! {sucesso}/{total} matrículas criadas."))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante criação de matrículas:\n{str(e)}"))
            self.root.after(0, lambda: self.matriculas_status_label.config(text="✗ Erro na criação"))
        
        finally:
            self.matriculas_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    # ===== MÉTODOS DA ABA ALTERAR ROTEIRIZAÇÃO =====

    def build_alterar_roteirizacao_tab(self):
        """Constrói a interface da aba de alterar roteirização da matrícula."""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_alterar_roteirizacao)

        self.add_gsan_url_field(tab_frame)

        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))

        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.alterar_roteirizacao_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.alterar_roteirizacao_user_var, width=30).pack(side=tk.LEFT)

        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.alterar_roteirizacao_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.alterar_roteirizacao_senha_var, show='*', width=30).pack(side=tk.LEFT)

        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        self.alterar_roteirizacao_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha de Entrada:", self.alterar_roteirizacao_input_path,
                               self.browse_alterar_roteirizacao_input, "(CSV com MATRICULA, ALTERAR, LOCAL, SETOR, QUADRA, LOTE)")

        self.alterar_roteirizacao_output_path = tk.StringVar()
        self.create_file_input(files_section, "Relatório de Saída:", self.alterar_roteirizacao_output_path,
                               self.browse_alterar_roteirizacao_output, "(CSV com resultado por matrícula)")

        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        self.alterar_roteirizacao_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", variable=self.alterar_roteirizacao_headless_var).pack(anchor=tk.W, pady=5)

        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        self.alterar_roteirizacao_progress = ttk.Progressbar(progress_frame, mode='determinate', style='Custom.Horizontal.TProgressbar', maximum=100, value=0)
        self.alterar_roteirizacao_progress.pack(fill=tk.X)

        self.alterar_roteirizacao_status_label = ttk.Label(tab_frame, text="Aguardando...", style='Status.TLabel')
        self.alterar_roteirizacao_status_label.pack(pady=(5, 15))

        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        self.alterar_roteirizacao_btn = self.create_modern_button(button_frame, "▶ Alterar Roteirização", self.iniciar_alterar_roteirizacao, '#28a745', '#218838')
        self.alterar_roteirizacao_btn.pack(fill=tk.X, pady=4)
        self.parar_alterar_roteirizacao_btn = self.create_modern_button(button_frame, "⏹ Parar", self.parar_alterar_roteirizacao, '#dc3545', '#c82333')
        self.parar_alterar_roteirizacao_btn.pack(fill=tk.X, pady=4)

    def browse_alterar_roteirizacao_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a planilha de entrada",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.alterar_roteirizacao_input_path.set(filename)

    def browse_alterar_roteirizacao_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.alterar_roteirizacao_output_path.set(filename)

    def iniciar_alterar_roteirizacao(self):
        if not self.alterar_roteirizacao_input_path.get() or not self.alterar_roteirizacao_output_path.get():
            messagebox.showerror("Erro", "Selecione entrada e saída!")
            return
        if not self.alterar_roteirizacao_user_var.get() or not self.alterar_roteirizacao_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return

        self.alterar_roteirizacao_running = True
        thread = threading.Thread(target=self.process_alterar_roteirizacao)
        thread.daemon = True
        thread.start()

    def parar_alterar_roteirizacao(self):
        if self.alterar_roteirizacao_running:
            self.alterar_roteirizacao_running = False
            self.root.after(0, lambda: self.alterar_roteirizacao_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    def process_alterar_roteirizacao(self):
        try:
            self.root.after(0, lambda: self.alterar_roteirizacao_progress.config(value=0))
            self.root.after(0, lambda: self.alterar_roteirizacao_status_label.config(text="Inicializando navegador..."))

            self.driver = self.create_webdriver(headless=self.alterar_roteirizacao_headless_var.get())
            self.driver.get(self.gsan_url())
            time.sleep(1)
            self.driver.find_element(By.NAME, 'login').send_keys(self.alterar_roteirizacao_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.alterar_roteirizacao_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)

            df = pd.read_csv(self.alterar_roteirizacao_input_path.get())
            total = len(df)
            rows = []

            for idx, row in df.iterrows():
                if not self.alterar_roteirizacao_running:
                    break

                matricula = int(float(row.get('MATRICULA', 0))) if str(row.get('MATRICULA', '0')).strip() not in ['', 'nan'] else 0
                alterar = int(float(row.get('ALTERAR', 0))) if str(row.get('ALTERAR', '0')).strip() not in ['', 'nan'] else 0

                if alterar != 1 or matricula == 0:
                    rows.append([idx + 1, matricula, 'NÃO ALTERAR'])
                    continue

                try:
                    local = int(float(row.get('LOCAL', 0)))
                    setor = int(float(row.get('SETOR', 0)))
                    quadra = int(float(row.get('QUADRA', 0)))
                    lote = int(float(row.get('LOTE', 0)))
                    sublote = int(float(row.get('SUBLOTE', 0))) if str(row.get('SUBLOTE', '0')).strip() not in ['', 'nan'] else 0
                    sequencia = int(float(row.get('SEQUENCIA', lote))) if str(row.get('SEQUENCIA', '')).strip() not in ['', 'nan'] else lote
                    cx = str(row.get('CX', '0'))
                    cy = str(row.get('CY', '0'))

                    self.driver.get(self.gsan_url("exibirFiltrarImovelAction.do?menu=sim"))
                    self.driver.find_element(By.NAME, "matriculaFiltro").send_keys(str(matricula))
                    self.driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                    time.sleep(0.4)

                    try:
                        msg = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        rows.append([idx + 1, matricula, msg])
                    except:
                        self.driver.find_element(By.NAME, "idLocalidade").clear()
                        self.driver.find_element(By.NAME, "idLocalidade").send_keys(str(local))
                        self.driver.find_element(By.NAME, "idSetorComercial").clear()
                        self.driver.find_element(By.NAME, "idSetorComercial").send_keys(str(setor))
                        self.driver.find_element(By.NAME, "idQuadra").clear()
                        self.driver.find_element(By.NAME, "idQuadra").send_keys(str(quadra), Keys.ENTER)
                        time.sleep(0.3)
                        self.driver.find_element(By.NAME, "lote").clear()
                        self.driver.find_element(By.NAME, "lote").send_keys(str(lote))
                        self.driver.find_element(By.NAME, "subLote").clear()
                        self.driver.find_element(By.NAME, "subLote").send_keys(str(sublote))
                        self.driver.find_element(By.NAME, "sequencialRota").clear()
                        self.driver.find_element(By.NAME, "sequencialRota").send_keys(str(sequencia))
                        self.driver.find_element(By.ID, "5").click()
                        time.sleep(0.3)

                        if cx != '0' and cy != '0':
                            self.driver.find_element(By.ID, "6").click()
                            time.sleep(0.2)
                            self.driver.find_element(By.NAME, "cordenadasUtmX").clear()
                            self.driver.find_element(By.NAME, "cordenadasUtmX").send_keys(cx)
                            self.driver.find_element(By.NAME, "cordenadasUtmY").clear()
                            self.driver.find_element(By.NAME, "cordenadasUtmY").send_keys(cy)

                        self.driver.find_element(By.XPATH, "//*[@value='Concluir']").click()
                        time.sleep(0.3)
                        try:
                            self.driver.find_element(By.XPATH, "//*[@value='Sim']").click()
                        except:
                            pass

                        try:
                            msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                            rows.append([idx + 1, matricula, msg_ok])
                        except:
                            msg_er = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                            rows.append([idx + 1, matricula, msg_er])

                except Exception as e:
                    rows.append([idx + 1, matricula, f'Erro: {str(e)}'])

                progress = int(((idx + 1) / total) * 100)
                self.root.after(0, lambda p=progress: self.alterar_roteirizacao_progress.config(value=p))
                self.root.after(0, lambda: self.alterar_roteirizacao_status_label.config(text=f"Processando: {idx+1}/{total}"))

            pd.DataFrame(rows, columns=['#', 'MATRICULA', 'MENSAGEM']).to_csv(self.alterar_roteirizacao_output_path.get(), index=False, encoding='utf-8-sig')
            self.root.after(0, lambda: self.alterar_roteirizacao_progress.config(value=100))
            self.root.after(0, lambda: self.alterar_roteirizacao_status_label.config(text="✓ Concluído"))
            self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Rotierização concluída!\n\nArquivo: {self.alterar_roteirizacao_output_path.get()}"))

        except Exception as e:
            self.root.after(0, lambda: self.alterar_roteirizacao_status_label.config(text="✗ Erro"))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na alteração de roteirização:\n{str(e)}"))
        finally:
            self.alterar_roteirizacao_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    # ===== MÉTODOS DA ABA ATUALIZAR ENDEREÇO =====

    def build_atualizar_endereco_tab(self):
        """Constrói a interface da aba de atualizar endereço da matrícula."""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_atualizar_endereco)

        self.add_gsan_url_field(tab_frame)

        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))

        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.atualizar_endereco_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.atualizar_endereco_user_var, width=30).pack(side=tk.LEFT)

        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.atualizar_endereco_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.atualizar_endereco_senha_var, show='*', width=30).pack(side=tk.LEFT)

        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        self.atualizar_endereco_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha de Entrada:", self.atualizar_endereco_input_path,
                               self.browse_atualizar_endereco_input, "(CSV com MATRICULA, CEP_GSAN, COD_LOG, BAIRRO, NUMERO)")

        self.atualizar_endereco_output_path = tk.StringVar()
        self.create_file_input(files_section, "Relatório de Saída:", self.atualizar_endereco_output_path,
                               self.browse_atualizar_endereco_output, "(CSV com resultado por matrícula)")

        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        self.atualizar_endereco_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", variable=self.atualizar_endereco_headless_var).pack(anchor=tk.W, pady=5)

        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        self.atualizar_endereco_progress = ttk.Progressbar(progress_frame, mode='determinate', style='Custom.Horizontal.TProgressbar', maximum=100, value=0)
        self.atualizar_endereco_progress.pack(fill=tk.X)

        self.atualizar_endereco_status_label = ttk.Label(tab_frame, text="Aguardando...", style='Status.TLabel')
        self.atualizar_endereco_status_label.pack(pady=(5, 15))

        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        self.atualizar_endereco_btn = self.create_modern_button(button_frame, "▶ Atualizar Endereço", self.iniciar_atualizar_endereco, '#28a745', '#218838')
        self.atualizar_endereco_btn.pack(fill=tk.X, pady=4)
        self.parar_atualizar_endereco_btn = self.create_modern_button(button_frame, "⏹ Parar", self.parar_atualizar_endereco, '#dc3545', '#c82333')
        self.parar_atualizar_endereco_btn.pack(fill=tk.X, pady=4)

    def browse_atualizar_endereco_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a planilha de entrada",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.atualizar_endereco_input_path.set(filename)

    def browse_atualizar_endereco_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.atualizar_endereco_output_path.set(filename)

    def iniciar_atualizar_endereco(self):
        if not self.atualizar_endereco_input_path.get() or not self.atualizar_endereco_output_path.get():
            messagebox.showerror("Erro", "Selecione entrada e saída!")
            return
        if not self.atualizar_endereco_user_var.get() or not self.atualizar_endereco_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return

        self.atualizar_endereco_running = True
        thread = threading.Thread(target=self.process_atualizar_endereco)
        thread.daemon = True
        thread.start()

    def parar_atualizar_endereco(self):
        if self.atualizar_endereco_running:
            self.atualizar_endereco_running = False
            self.root.after(0, lambda: self.atualizar_endereco_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    def process_atualizar_endereco(self):
        try:
            self.root.after(0, lambda: self.atualizar_endereco_progress.config(value=0))
            self.driver = self.create_webdriver(headless=self.atualizar_endereco_headless_var.get())
            self.driver.get(self.gsan_url())
            time.sleep(1)
            self.driver.find_element(By.NAME, 'login').send_keys(self.atualizar_endereco_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.atualizar_endereco_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)

            df = pd.read_csv(self.atualizar_endereco_input_path.get())
            total = len(df)
            rows = []

            for idx, row in df.iterrows():
                if not self.atualizar_endereco_running:
                    break

                matricula = str(row.get('MATRICULA', '0')).strip()
                alterar = int(float(row.get('ALTERAR', 0))) if str(row.get('ALTERAR', '0')).strip() not in ['', 'nan'] else 0
                if alterar != 1 or matricula in ['0', '']:
                    rows.append([idx + 1, matricula, 'NÃO ALTERAR'])
                    continue

                try:
                    cep_gsan = int(float(row.get('CEP_GSAN', 0)))
                    cod_log = str(row.get('COD_LOG', '0')).strip()
                    bairro = str(row.get('BAIRRO', '')).strip()
                    numero = str(row.get('NUMERO', '')).strip()
                    complemento = str(row.get('COMPLEMENTO', '0')).strip()

                    self.driver.get(self.gsan_url("exibirFiltrarImovelAction.do?menu=sim"))
                    time.sleep(0.3)
                    self.driver.find_element(By.NAME, "matriculaFiltro").send_keys(matricula)
                    self.driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                    time.sleep(0.5)

                    try:
                        msg_err = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        rows.append([idx + 1, matricula, msg_err])
                    except:
                        self.driver.find_element(By.ID, "2").click()
                        time.sleep(0.3)
                        try:
                            self.driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                        except:
                            pass

                        try:
                            self.driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[5]/tbody/tr[2]/td/div/table/tbody/tr/td[1]/a/img").click()
                            alert = self.driver.switch_to.alert
                            alert.accept()
                        except:
                            pass

                        self.driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                        time.sleep(0.3)
                        janela_principal = self.driver.window_handles[0]
                        janela_popup = self.driver.window_handles[1]
                        self.driver.switch_to.window(janela_popup)
                        self.driver.find_element(By.NAME, "logradouro").send_keys(cod_log, Keys.ENTER)
                        time.sleep(0.3)
                        self.driver.find_element(By.XPATH, f"//input[@name='cepSelecionado' and @value='{cep_gsan}']").click()
                        self.driver.find_element(By.NAME, "bairro").send_keys(bairro)
                        self.driver.find_element(By.NAME, "numero").send_keys(numero)
                        if complemento and complemento != '0':
                            self.driver.find_element(By.NAME, "complemento").send_keys(complemento)
                        self.driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
                        time.sleep(0.3)
                        self.driver.switch_to.window(janela_principal)
                        self.driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                        time.sleep(0.3)

                        try:
                            msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                            rows.append([idx + 1, matricula, msg_ok])
                        except:
                            msg_er = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                            rows.append([idx + 1, matricula, msg_er])

                except Exception as e:
                    rows.append([idx + 1, matricula, f'Erro: {str(e)}'])

                progress = int(((idx + 1) / total) * 100)
                self.root.after(0, lambda p=progress: self.atualizar_endereco_progress.config(value=p))
                self.root.after(0, lambda: self.atualizar_endereco_status_label.config(text=f"Processando: {idx+1}/{total}"))

            pd.DataFrame(rows, columns=['#', 'MATRICULA', 'MENSAGEM']).to_csv(self.atualizar_endereco_output_path.get(), index=False, encoding='utf-8-sig')
            self.root.after(0, lambda: self.atualizar_endereco_progress.config(value=100))
            self.root.after(0, lambda: self.atualizar_endereco_status_label.config(text="✓ Concluído"))
            self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Atualização de endereço concluída!\n\nArquivo: {self.atualizar_endereco_output_path.get()}"))

        except Exception as e:
            self.root.after(0, lambda: self.atualizar_endereco_status_label.config(text="✗ Erro"))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na atualização de endereço:\n{str(e)}"))
        finally:
            self.atualizar_endereco_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    # ===== MÉTODOS DA ABA ALTERAR CLIENTE DA MATRÍCULA =====

    def build_alterar_cliente_tab(self):
        """Constrói a interface da aba de alterar cliente da matrícula."""
        tab_frame, action_panel = self.create_scrollable_tab(self.tab_alterar_cliente)

        self.add_gsan_url_field(tab_frame)

        config_section = self.create_section(tab_frame, "⚙️ CONFIGURAÇÕES DE LOGIN")
        config_container = tk.Frame(config_section, bg=self.section_bg)
        config_container.pack(fill=tk.X, padx=15, pady=(5, 10))

        user_frame = tk.Frame(config_container, bg=self.section_bg)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuário GSAN:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.alterar_cliente_user_var = tk.StringVar(value=os.environ.get('USR', ''))
        ttk.Entry(user_frame, textvariable=self.alterar_cliente_user_var, width=30).pack(side=tk.LEFT)

        senha_frame = tk.Frame(config_container, bg=self.section_bg)
        senha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(senha_frame, text="Senha GSAN:", style='Section.TLabel', width=15, anchor='w').pack(side=tk.LEFT, padx=(0, 10))
        self.alterar_cliente_senha_var = tk.StringVar(value=os.environ.get('PWD', ''))
        ttk.Entry(senha_frame, textvariable=self.alterar_cliente_senha_var, show='*', width=30).pack(side=tk.LEFT)

        files_section = self.create_section(tab_frame, "📁 ARQUIVOS")
        self.alterar_cliente_input_path = tk.StringVar()
        self.create_file_input(files_section, "Planilha de Entrada:", self.alterar_cliente_input_path,
                               self.browse_alterar_cliente_input, "(CSV com MATRICULA, ALTERAR, COD_CLIENTE)")

        self.alterar_cliente_output_path = tk.StringVar()
        self.create_file_input(files_section, "Relatório de Saída:", self.alterar_cliente_output_path,
                               self.browse_alterar_cliente_output, "(CSV com resultado por matrícula)")

        options_section = self.create_section(tab_frame, "🔧 OPÇÕES")
        options_container = tk.Frame(options_section, bg=self.section_bg)
        options_container.pack(fill=tk.X, padx=15, pady=(5, 10))
        self.alterar_cliente_headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_container, text="Executar em modo invisível (headless)", variable=self.alterar_cliente_headless_var).pack(anchor=tk.W, pady=5)

        progress_frame = tk.Frame(tab_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        self.alterar_cliente_progress = ttk.Progressbar(progress_frame, mode='determinate', style='Custom.Horizontal.TProgressbar', maximum=100, value=0)
        self.alterar_cliente_progress.pack(fill=tk.X)

        self.alterar_cliente_status_label = ttk.Label(tab_frame, text="Aguardando...", style='Status.TLabel')
        self.alterar_cliente_status_label.pack(pady=(5, 15))

        button_frame = tk.Frame(action_panel, bg='#dbeafe')
        button_frame.pack(fill=tk.X, padx=8, pady=(4, 0))
        self.alterar_cliente_btn = self.create_modern_button(button_frame, "▶ Alterar Cliente", self.iniciar_alterar_cliente, '#28a745', '#218838')
        self.alterar_cliente_btn.pack(fill=tk.X, pady=4)
        self.parar_alterar_cliente_btn = self.create_modern_button(button_frame, "⏹ Parar", self.parar_alterar_cliente, '#dc3545', '#c82333')
        self.parar_alterar_cliente_btn.pack(fill=tk.X, pady=4)

    def browse_alterar_cliente_input(self):
        filename = filedialog.askopenfilename(
            title="Selecione a planilha de entrada",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.alterar_cliente_input_path.set(filename)

    def browse_alterar_cliente_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.alterar_cliente_output_path.set(filename)

    def iniciar_alterar_cliente(self):
        if not self.alterar_cliente_input_path.get() or not self.alterar_cliente_output_path.get():
            messagebox.showerror("Erro", "Selecione entrada e saída!")
            return
        if not self.alterar_cliente_user_var.get() or not self.alterar_cliente_senha_var.get():
            messagebox.showerror("Erro", "Informe usuário e senha do GSAN!")
            return

        self.alterar_cliente_running = True
        thread = threading.Thread(target=self.process_alterar_cliente)
        thread.daemon = True
        thread.start()

    def parar_alterar_cliente(self):
        if self.alterar_cliente_running:
            self.alterar_cliente_running = False
            self.root.after(0, lambda: self.alterar_cliente_status_label.config(text="Parando..."))
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

    def process_alterar_cliente(self):
        try:
            self.root.after(0, lambda: self.alterar_cliente_progress.config(value=0))
            self.driver = self.create_webdriver(headless=self.alterar_cliente_headless_var.get())
            self.driver.get(self.gsan_url())
            time.sleep(1)
            self.driver.find_element(By.NAME, 'login').send_keys(self.alterar_cliente_user_var.get())
            self.driver.find_element(By.NAME, 'senha').send_keys(self.alterar_cliente_senha_var.get())
            self.driver.find_element(By.NAME, 'buttonLogin').click()
            time.sleep(1)

            df = pd.read_csv(self.alterar_cliente_input_path.get())
            total = len(df)
            rows = []

            for idx, row in df.iterrows():
                if not self.alterar_cliente_running:
                    break

                matricula = int(float(row.get('MATRICULA', 0))) if str(row.get('MATRICULA', '0')).strip() not in ['', 'nan'] else 0
                alterar = int(float(row.get('ALTERAR', 0))) if str(row.get('ALTERAR', '0')).strip() not in ['', 'nan'] else 0
                codigo = int(float(row.get('COD_CLIENTE', 0))) if str(row.get('COD_CLIENTE', '0')).strip() not in ['', 'nan'] else 0

                if alterar != 1 or matricula == 0 or codigo == 0:
                    rows.append([idx + 1, matricula, 'NÃO ALTERAR'])
                    continue

                try:
                    self.driver.get(self.gsan_url("exibirFiltrarImovelAction.do?menu=sim"))
                    self.driver.find_element(By.NAME, 'matriculaFiltro').send_keys(str(matricula))
                    self.driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                    time.sleep(0.5)

                    try:
                        msg_err = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                        rows.append([idx + 1, matricula, msg_err])
                    except:
                        self.driver.find_element(By.ID, "3").click()
                        time.sleep(0.3)
                        try:
                            self.driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                        except:
                            pass

                        self.driver.find_element(By.NAME, "idCliente").clear()
                        self.driver.find_element(By.NAME, "idCliente").send_keys(str(codigo), Keys.ENTER)
                        time.sleep(0.4)
                        self.driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
                        time.sleep(0.2)
                        self.driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
                        time.sleep(0.3)
                        try:
                            self.driver.find_element(By.XPATH, "//input[@value='Sim']").click()
                            time.sleep(0.2)
                        except:
                            pass
                        self.driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                        time.sleep(0.4)

                        try:
                            msg_ok = self.driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                            rows.append([idx + 1, matricula, msg_ok])
                        except:
                            msg_er = self.driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                            rows.append([idx + 1, matricula, msg_er])

                except Exception as e:
                    rows.append([idx + 1, matricula, f'Erro: {str(e)}'])

                progress = int(((idx + 1) / total) * 100)
                self.root.after(0, lambda p=progress: self.alterar_cliente_progress.config(value=p))
                self.root.after(0, lambda: self.alterar_cliente_status_label.config(text=f"Processando: {idx+1}/{total}"))

            pd.DataFrame(rows, columns=['#', 'MATRICULA', 'MENSAGEM']).to_csv(self.alterar_cliente_output_path.get(), index=False, encoding='utf-8-sig')
            self.root.after(0, lambda: self.alterar_cliente_progress.config(value=100))
            self.root.after(0, lambda: self.alterar_cliente_status_label.config(text="✓ Concluído"))
            self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Alteração de cliente concluída!\n\nArquivo: {self.alterar_cliente_output_path.get()}"))

        except Exception as e:
            self.root.after(0, lambda: self.alterar_cliente_status_label.config(text="✗ Erro"))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na alteração de cliente:\n{str(e)}"))
        finally:
            self.alterar_cliente_running = False
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

def main():
    # Criar splash screen
    splash = tk.Tk()
    splash.withdraw()  # Esconde a janela principal temporariamente
    
    # Criar toplevel para splash
    splash_window = tk.Toplevel(splash)
    splash_window.overrideredirect(True)  # Remove bordas
    
    # Centralizar splash
    window_width = 400
    window_height = 200
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    splash_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Garantir que a splash apareça na frente imediatamente
    splash_window.lift()
    splash_window.attributes('-topmost', True)
    splash_window.focus_force()
    
    # Configurar splash com gradiente azul
    splash_frame = tk.Frame(splash_window, bg='#0078d4', bd=0)
    splash_frame.pack(fill=tk.BOTH, expand=True)
    
    # Ícone/Logo (usando texto grande)
    logo_label = tk.Label(splash_frame, text="⚡", font=('Segoe UI', 60), 
                         bg='#0078d4', fg='white')
    logo_label.pack(pady=(30, 10))
    
    # Nome do app
    title_label = tk.Label(splash_frame, text="SmartSync Cadastral", 
                          font=('Segoe UI', 18, 'bold'), bg='#0078d4', fg='white')
    title_label.pack(pady=(0, 5))
    
    # Subtítulo
    subtitle_label = tk.Label(splash_frame, text="Carregando aplicativo...", 
                             font=('Segoe UI', 10), bg='#0078d4', fg='#e0e0e0')
    subtitle_label.pack(pady=(0, 20))
    
    # Barra de progresso indeterminada
    progress = ttk.Progressbar(splash_frame, mode='indeterminate', length=300)
    progress.pack(pady=(0, 20))
    progress.start(10)
    
    # Forçar atualização imediata da splash
    splash_window.update_idletasks()
    splash_window.update()
    
    # Função para destruir splash e mostrar app principal
    def show_main_app():
        splash_window.destroy()
        splash.destroy()
        
        # Criar janela principal
        root = tk.Tk()
        app = PlanilhasApp(root)
        root.mainloop()
    
    # Aguardar apenas 600ms para mostrar app principal (mais rápido)
    splash_window.after(600, show_main_app)
    splash.mainloop()

if __name__ == "__main__":
    main()
