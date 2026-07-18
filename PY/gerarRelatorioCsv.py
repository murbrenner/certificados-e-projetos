import glob
import importlib
import json
import os
import re
import shutil
import threading
import time
import tkinter as tk
import winreg
import ctypes
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk

from db_arquivos import downloads


RELATORIO_URL = (
    "http://gsan.caema.ma.gov.br:8080/gsan/"
    "exibirFiltrarImovelOutrosCriteriosConsumidoresInscricao.do"
    "?menu=sim&gerarRelatorio=RelatorioCadastroConsumidoresInscricao"
)
LOGIN_URL = "http://gsan.caema.ma.gov.br:8080/gsan/"
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".gsan_relatorio_csv")
DRIVER_DIR = os.path.join(APP_DATA_DIR, "drivers")
DRIVER_BIN = os.path.join(DRIVER_DIR, "chromedriver.exe")
PREFERENCIAS_ARQUIVO = os.path.join(APP_DATA_DIR, "preferencias.json")
TEMPO_MAX_DOWNLOAD_CSV = 45
APP_VERSAO = "1.6.1"
NOME_APP = "Quick Route CSV"
WINDOWS_APP_ID = "MuriloBrenner.QuickRouteCSV"

driver = None
webdriver = None
By = None
ChromeService = None
pd = None


def configurar_app_id_windows():
    if os.name != "nt":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_ID)
    except Exception:
        pass


def criar_icone_interno(master):
    icone = tk.PhotoImage(master=master, width=32, height=32)
    icone.put("#0d132a", to=(0, 0, 32, 32))
    icone.put("#1a2442", to=(2, 2, 30, 30))
    icone.put("#0e7ae6", to=(5, 5, 27, 11))
    icone.put("#2ea043", to=(5, 12, 16, 27))
    icone.put("#db8b23", to=(17, 12, 27, 27))
    icone.put("#ffffff", to=(8, 8, 11, 9))
    icone.put("#ffffff", to=(13, 8, 24, 9))
    icone.put("#ffffff", to=(8, 15, 14, 16))
    icone.put("#ffffff", to=(8, 18, 14, 19))
    return icone


def mostrar_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="#0d132a")

    largura, altura = 430, 250
    x = (splash.winfo_screenwidth() // 2) - (largura // 2)
    y = (splash.winfo_screenheight() // 2) - (altura // 2)
    splash.geometry(f"{largura}x{altura}+{x}+{y}")

    icone = criar_icone_interno(splash)
    splash.iconphoto(True, icone)
    splash._icone_ref = icone

    card = tk.Frame(splash, bg="#1a2442", bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=14, pady=14)

    tk.Label(card, text=NOME_APP, bg="#1a2442", fg="#ffffff", font=("Segoe UI Semibold", 20)).pack(pady=(30, 10))
    tk.Label(card, text=f"Versão {APP_VERSAO}", bg="#1a2442", fg="#b9c0d4", font=("Segoe UI", 10)).pack()
    tk.Label(card, text="Iniciando aplicação...", bg="#1a2442", fg="#d4af37", font=("Segoe UI", 10)).pack(pady=(10, 0))

    barra = ttk.Progressbar(card, mode="indeterminate", length=280)
    barra.pack(pady=(22, 0))
    barra.start(14)

    splash.update_idletasks()
    splash.after(1200, splash.destroy)
    splash.mainloop()


def _lazy_import_selenium():
    global webdriver, By, ChromeService
    if webdriver is None or By is None or ChromeService is None:
        from selenium import webdriver as selenium_webdriver
        from selenium.webdriver.common.by import By as selenium_by
        from selenium.webdriver.chrome.service import Service as selenium_chrome_service

        webdriver = selenium_webdriver
        By = selenium_by
        ChromeService = selenium_chrome_service


def _lazy_import_pandas():
    global pd
    if pd is None:
        import pandas as pandas

        pd = pandas


def windows_usa_tema_escuro():
    try:
        chave = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave) as key:
            valor, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(valor) == 0
    except Exception:
        return False


def carregar_preferencias():
    if not os.path.isfile(PREFERENCIAS_ARQUIVO):
        return {}
    try:
        with open(PREFERENCIAS_ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception:
        return {}


def salvar_preferencias(preferencias):
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    with open(PREFERENCIAS_ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(preferencias, arquivo, ensure_ascii=False, indent=2)


def obter_credenciais(usuario_digitado="", senha_digitada=""):
    usuario = str(usuario_digitado or "").strip()
    senha = str(senha_digitada or "").strip()

    if not usuario:
        usuario = os.environ.get("USR", "").strip()
    if not senha:
        senha = os.environ.get("PWD", "").strip()

    if not usuario or not senha:
        raise Exception("Informe login e senha do GSAN (ou defina USR/PWD no ambiente).")
    return usuario, senha


def garantir_driver_aberto():
    global driver
    _lazy_import_selenium()

    if driver is not None:
        try:
            _ = driver.title
            return driver
        except Exception:
            try:
                driver.quit()
            except Exception:
                pass
            driver = None

    os.makedirs(DRIVER_DIR, exist_ok=True)

    try:
        if os.path.exists(DRIVER_BIN):
            service = ChromeService(executable_path=DRIVER_BIN)
            driver = webdriver.Chrome(service=service)
        else:
            # Fallback para Selenium Manager quando não existe driver local.
            driver = webdriver.Chrome()
    except Exception as erro:
        raise Exception(
            "Falha ao iniciar o ChromeDriver. Use o botao 'Baixar driver offline' e tente novamente. "
            "Detalhes: {}".format(erro)
        )

    driver.implicitly_wait(10)
    return driver


def fechar_driver():
    global driver
    try:
        if driver is not None:
            driver.quit()
    except Exception:
        pass
    driver = None


def baixar_driver_offline():
    try:
        modulo_wdm = importlib.import_module("webdriver_manager.chrome")
        ChromeDriverManager = getattr(modulo_wdm, "ChromeDriverManager")
    except Exception as erro:
        raise Exception(
            "Pacote webdriver-manager não encontrado. Instale com: pip install webdriver-manager. "
            "Detalhes: {}".format(erro)
        )

    os.makedirs(DRIVER_DIR, exist_ok=True)
    caminho_baixado = ChromeDriverManager().install()

    if not os.path.isfile(caminho_baixado):
        raise Exception("Download do ChromeDriver falhou.")

    if os.path.abspath(caminho_baixado).lower() != os.path.abspath(DRIVER_BIN).lower():
        shutil.copy2(caminho_baixado, DRIVER_BIN)
    else:
        os.chmod(DRIVER_BIN, 0o755)

    return DRIVER_BIN


def login_gsan(usuario_digitado="", senha_digitada=""):
    usuario, senha = obter_credenciais(usuario_digitado, senha_digitada)
    drv = garantir_driver_aberto()
    drv.get(LOGIN_URL)
    drv.find_element(By.NAME, "login").send_keys(usuario)
    drv.find_element(By.NAME, "senha").send_keys(senha)
    drv.find_element(By.NAME, "buttonLogin").click()
    time.sleep(0.5)
    return drv


def extrair_sequencia(valor_coluna):
    texto = str(valor_coluna).strip()
    if not texto or texto.lower() == "nan":
        return ""

    match = re.search(r"^(?:\d+\.){3}(\d+)\.\d+", texto)
    if match:
        return match.group(1)

    partes = texto.split(".")
    if len(partes) >= 4:
        return partes[3].strip()
    return ""


def limpar_nome_arquivo(valor):
    texto = str(valor).strip().lower()
    texto = re.sub(r"\s+", "_", texto)
    texto = re.sub(r"[^a-z0-9_\-]", "", texto)
    return texto or "na"


def montar_codigo(prefixo, valor):
    numeros = re.findall(r"\d+", str(valor).strip())
    if numeros:
        return "{}{}".format(prefixo, "".join(numeros))

    texto = limpar_nome_arquivo(valor)
    if texto and texto != "na":
        return "{}{}".format(prefixo, texto.upper())

    return "{}000".format(prefixo)


def pasta_downloads_real():
    caminho = os.path.expandvars(downloads)
    caminho = os.path.expanduser(caminho)
    return os.path.abspath(caminho)


def esperar_csv_baixado(pasta_downloads, inicio_execucao, arquivos_existentes, timeout=120, drv=None):
    inicio_espera = time.time()
    while time.time() - inicio_espera <= timeout:
        if drv is not None:
            try:
                if drv.session_id is None:
                    raise Exception("Processo cancelado: navegador foi fechado.")
                if len(drv.window_handles) == 0:
                    raise Exception("Processo cancelado: navegador foi fechado.")
            except Exception:
                raise Exception("Processo cancelado: navegador foi fechado.")

        arquivos_csv = glob.glob(os.path.join(pasta_downloads, "*.csv"))
        novos_arquivos = [arq for arq in arquivos_csv if arq not in arquivos_existentes]

        if novos_arquivos:
            novos_arquivos.sort(key=os.path.getmtime, reverse=True)
            return novos_arquivos[0]

        recentes = [arq for arq in arquivos_csv if os.path.getmtime(arq) >= inicio_execucao]
        if recentes:
            recentes.sort(key=os.path.getmtime, reverse=True)
            return recentes[0]

        time.sleep(0.35)

    raise Exception("Timeout ao aguardar o download do CSV do GSAN.")


def gerar_relatorio(drv, local, setor, rota):
    pasta_dl = pasta_downloads_real()
    if not os.path.isdir(pasta_dl):
        raise Exception("Pasta de downloads nao encontrada: {}".format(pasta_dl))

    arquivos_antes = set(glob.glob(os.path.join(pasta_dl, "*.csv")))
    inicio_execucao = time.time()

    drv.get(RELATORIO_URL)
    drv.find_element(By.NAME, "localidadeOrigemID").send_keys(local)
    drv.find_element(By.NAME, "setorComercialOrigemCD").send_keys(setor)
    drv.find_element(By.NAME, "cdRotaInicial").send_keys(rota)
    drv.find_element(By.NAME, "ordenacaoRelatorio").send_keys("R")
    drv.find_element(By.NAME, "concluir").click()

    try:
        drv.find_element(By.XPATH, "//*[@id='demodiv']/table/tbody/tr[4]/td/span/input").click()
    except Exception:
        pass

    drv.find_element(By.XPATH, "//input[@value='Gerar']").click()

    return esperar_csv_baixado(
        pasta_dl,
        inicio_execucao,
        arquivos_antes,
        timeout=TEMPO_MAX_DOWNLOAD_CSV,
        drv=drv,
    )


def converter_csv_baixado(arquivo_baixado, rota, arquivo_saida):
    _lazy_import_pandas()

    try:
        df = pd.read_csv(arquivo_baixado, sep=";", header=None, dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(arquivo_baixado, sep=";", header=None, dtype=str, encoding="latin-1")

    if df.shape[1] < 7:
        raise Exception("CSV baixado sem a setima coluna esperada para MATRICULA.")

    rota_valor = str(rota).strip()

    saida = pd.DataFrame()
    saida["SEQUENCIA"] = df.iloc[:, 0].apply(extrair_sequencia)
    saida["MATRICULA"] = df.iloc[:, 6].fillna("").astype(str).str.strip()

    saida = saida[saida["SEQUENCIA"].astype(str).str.strip() != ""]
    saida.insert(0, "ROTA", [rota_valor] * len(saida))
    saida.to_csv(arquivo_saida, sep=",", index=False, encoding="utf-8")
    return len(saida)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(NOME_APP)
        self.geometry("680x860")
        self.maxsize(680, 860)
        self.minsize(680, 860)

        self.preferencias = carregar_preferencias()
        self.tema_escuro = windows_usa_tema_escuro()
        self._saida_manual = False
        self._processando = False

        self.local_var = tk.StringVar()
        self.setor_var = tk.StringVar()
        self.rota_var = tk.StringVar()
        self.usuario_gsan_var = tk.StringVar()
        self.senha_gsan_var = tk.StringVar()
        self.saida_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto para executar")
        self.validar_3_digitos_cmd = (self.register(self._validar_ate_3_digitos), "%P")
        self._icone_app = criar_icone_interno(self)
        self.iconphoto(True, self._icone_app)

        self._configurar_estilo_windows11()
        self._montar_ui()
        self._centralizar_janela(680, 860)
        self._restaurar_preferencias_ui()
        self._sugerir_saida_automatica()
        self.local_var.trace_add("write", self._ao_alterar_campos_nome)
        self.rota_var.trace_add("write", self._ao_alterar_campos_nome)
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def _centralizar_janela(self, largura, altura):
        self.update_idletasks()
        tela_largura = self.winfo_screenwidth()
        tela_altura = self.winfo_screenheight()
        pos_x = max(0, (tela_largura // 2) - (largura // 2))
        pos_y = max(0, (tela_altura // 2) - (altura // 2))
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def _configurar_estilo_windows11(self):
        if self.tema_escuro:
            self.cores = {
                "bg": "#0d132a",
                "card": "#1a2442",
                "card_soft": "#24335d",
                "text": "#f5f7ff",
                "title": "#ffffff",
                "hint": "#c8d0ea",
                "entry_bg": "#101a36",
                "entry_fg": "#f5f7ff",
                "log_bg": "#0b1024",
                "log_fg": "#d9e2ff",
                "accent": "#0e7ae6",
                "accent_active": "#0b66bf",
                "success": "#2ea043",
                "success_active": "#25873a",
                "warning": "#db8b23",
                "warning_active": "#c17716",
                "status": "#ffcc40",
            }
        else:
            self.cores = {
                "bg": "#f3f3f3",
                "card": "#ffffff",
                "card_soft": "#f6f7fb",
                "text": "#1f1f1f",
                "title": "#111111",
                "hint": "#5f5f5f",
                "entry_bg": "#ffffff",
                "entry_fg": "#1f1f1f",
                "log_bg": "#fbfbfb",
                "log_fg": "#1f1f1f",
                "accent": "#0f6cbd",
                "accent_active": "#115ea3",
                "success": "#2ea043",
                "success_active": "#25873a",
                "warning": "#db8b23",
                "warning_active": "#c17716",
                "status": "#9a6700",
            }

        self.configure(bg=self.cores["bg"])
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("vista")
        except tk.TclError:
            pass

        self.style.configure("W11.TLabel", background=self.cores["card"], foreground=self.cores["text"], font=("Segoe UI", 11))
        self.style.configure("W11Title.TLabel", background=self.cores["card"], foreground=self.cores["title"], font=("Segoe UI Semibold", 18))
        self.style.configure("W11Hint.TLabel", background=self.cores["card"], foreground=self.cores["hint"], font=("Segoe UI", 10))
        campo_hint_cor = "#b9c0d4" if self.tema_escuro else "#8f8f8f"
        self.style.configure("W11FieldHint.TLabel", background=self.cores["card"], foreground=campo_hint_cor, font=("Segoe UI", 9))
        self.style.configure("W11Status.TLabel", background=self.cores["card"], foreground=self.cores["status"], font=("Segoe UI Semibold", 10))
        self.style.configure("W11Footer.TLabel", background=self.cores["card"], foreground="#D4AF37", font=("Segoe UI Semibold", 10))
        self.style.configure("W11Card.TFrame", background=self.cores["card"])
        self.style.configure("W11SoftCard.TFrame", background=self.cores["card_soft"])
        self.style.configure(
            "W11.TEntry",
            font=("Segoe UI", 10),
            padding=6,
            fieldbackground=self.cores["entry_bg"],
            foreground=self.cores["entry_fg"],
            insertcolor=self.cores["entry_fg"],
        )
        self.style.map(
            "W11.TEntry",
            fieldbackground=[("!disabled", self.cores["entry_bg"])],
            foreground=[("!disabled", self.cores["entry_fg"])],
        )
        self.style.configure("W11.TButton", font=("Segoe UI Semibold", 10), padding=7)
        self.style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=7)
        self.style.configure("Success.TButton", font=("Segoe UI Semibold", 10), padding=7)
        self.style.configure("Warning.TButton", font=("Segoe UI Semibold", 10), padding=7)
        self.style.map("Accent.TButton", background=[("active", self.cores["accent_active"]), ("!disabled", self.cores["accent"])])
        self.style.map("Success.TButton", background=[("active", self.cores["success_active"]), ("!disabled", self.cores["success"])])
        self.style.map("Warning.TButton", background=[("active", self.cores["warning_active"]), ("!disabled", self.cores["warning"])])

    def _restaurar_preferencias_ui(self):
        self.local_var.set("")
        self.setor_var.set("")
        self.rota_var.set("")
        self.usuario_gsan_var.set(self.preferencias.get("usuario_gsan", ""))
        self.senha_gsan_var.set(self.preferencias.get("senha_gsan", ""))
        self.saida_var.set("")
        self._saida_manual = False

    def _coletar_preferencias(self):
        return {
            "local": self.local_var.get().strip(),
            "setor": self.setor_var.get().strip(),
            "rota": self.rota_var.get().strip(),
            "usuario_gsan": self.usuario_gsan_var.get().strip(),
            "senha_gsan": self.senha_gsan_var.get(),
            "saida": self.saida_var.get().strip() if self._saida_manual else "",
            "tema_escuro_detectado": self.tema_escuro,
            "ultima_execucao": datetime.now().isoformat(timespec="seconds"),
        }

    def _salvar_preferencias(self):
        try:
            salvar_preferencias(self._coletar_preferencias())
        except Exception:
            pass

    def _sugerir_saida_automatica(self):
        if self._saida_manual:
            return
        local = self.local_var.get().strip()
        rota = self.rota_var.get().strip()
        if not local or not rota:
            self.saida_var.set("")
            return
        codigo_local = "G{}".format(local.zfill(3))
        codigo_rota = "R{}".format(rota.zfill(3))
        pasta_padrao = pasta_downloads_real()
        if not os.path.isdir(pasta_padrao):
            pasta_padrao = os.path.expanduser("~")
        nome = "{}-{}.csv".format(codigo_local, codigo_rota)
        self.saida_var.set(os.path.join(pasta_padrao, nome))

    def _ao_alterar_rota(self, *_):
        self._sugerir_saida_automatica()

    def _ao_alterar_campos_nome(self, *_):
        self._sugerir_saida_automatica()

    def _validar_ate_3_digitos(self, novo_valor):
        if novo_valor == "":
            return True
        return novo_valor.isdigit() and len(novo_valor) <= 3

    def _ao_perder_foco_campos(self, _event=None):
        self._sugerir_saida_automatica()

    def _montar_ui(self):
        shell = tk.Frame(self, bg=self.cores["card_soft"], bd=1, relief="solid", highlightthickness=0)
        shell.pack(fill="both", expand=True, padx=14, pady=14)

        container = ttk.Frame(shell, style="W11Card.TFrame", padding=22)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        topo = ttk.Frame(container, style="W11Card.TFrame")
        topo.grid(row=0, column=0, sticky="ew")
        ttk.Label(topo, text="🧾 Gerador de Relatório GSAN", style="W11Title.TLabel").grid(row=0, column=0, sticky="w")
        self.btn_driver = tk.Button(
            topo,
            text="⬇ Baixar driver offline",
            command=self.baixar_driver,
            font=("Segoe UI Semibold", 10),
            bg=self.cores["success"],
            fg="#ffffff",
            activebackground=self.cores["success_active"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
        )
        self.btn_driver.grid(row=0, column=1, sticky="e")
        ttk.Label(
            topo,
            text="Preencha LOCAL, SETOR e ROTA para baixar e converter o CSV.",
            style="W11Hint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        topo.columnconfigure(0, weight=1)

        card_form = tk.Frame(container, bg=self.cores["card"], bd=1, relief="solid", highlightthickness=0)
        card_form.grid(row=1, column=0, sticky="ew", pady=(18, 14))
        form = ttk.Frame(card_form, style="W11Card.TFrame", padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="📍 LOCAL", style="W11.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        linha_local = tk.Frame(form, bg=self.cores["card"], highlightthickness=0, bd=0)
        linha_local.grid(row=0, column=1, sticky="w", padx=(14, 0))
        self.entry_local = tk.Entry(
            linha_local,
            textvariable=self.local_var,
            width=8,
            font=("Segoe UI", 10),
            bg=self.cores["entry_bg"],
            fg=self.cores["entry_fg"],
            insertbackground=self.cores["entry_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.cores["hint"],
            highlightcolor=self.cores["accent"],
            validate="key",
            validatecommand=self.validar_3_digitos_cmd,
            justify="center",
        )
        self.entry_local.grid(row=0, column=0, sticky="w", ipady=6)
        self.entry_local.bind("<FocusOut>", self._ao_perder_foco_campos)
        ttk.Label(linha_local, text="DIGITE A LOCALIDADE", style="W11FieldHint.TLabel").grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 1))

        ttk.Label(form, text="🏢 SETOR", style="W11.TLabel").grid(row=1, column=0, sticky="w", pady=(14, 6))
        linha_setor = tk.Frame(form, bg=self.cores["card"], highlightthickness=0, bd=0)
        linha_setor.grid(row=1, column=1, sticky="w", padx=(14, 0), pady=(14, 0))
        self.entry_setor = tk.Entry(
            linha_setor,
            textvariable=self.setor_var,
            width=8,
            font=("Segoe UI", 10),
            bg=self.cores["entry_bg"],
            fg=self.cores["entry_fg"],
            insertbackground=self.cores["entry_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.cores["hint"],
            highlightcolor=self.cores["accent"],
            validate="key",
            validatecommand=self.validar_3_digitos_cmd,
            justify="center",
        )
        self.entry_setor.grid(row=0, column=0, sticky="w", ipady=6)
        ttk.Label(linha_setor, text="DIGITE O SETOR", style="W11FieldHint.TLabel").grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 1))

        ttk.Label(form, text="🧭 ROTA", style="W11.TLabel").grid(row=2, column=0, sticky="w", pady=(14, 6))
        linha_rota = tk.Frame(form, bg=self.cores["card"], highlightthickness=0, bd=0)
        linha_rota.grid(row=2, column=1, sticky="w", padx=(14, 0), pady=(14, 0))
        self.entry_rota = tk.Entry(
            linha_rota,
            textvariable=self.rota_var,
            width=8,
            font=("Segoe UI", 10),
            bg=self.cores["entry_bg"],
            fg=self.cores["entry_fg"],
            insertbackground=self.cores["entry_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.cores["hint"],
            highlightcolor=self.cores["accent"],
            validate="key",
            validatecommand=self.validar_3_digitos_cmd,
            justify="center",
        )
        self.entry_rota.grid(row=0, column=0, sticky="w", ipady=6)
        self.entry_rota.bind("<FocusOut>", self._ao_perder_foco_campos)
        ttk.Label(linha_rota, text="DIGITE A ROTA DESEJADA", style="W11FieldHint.TLabel").grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 1))

        ttk.Label(form, text="📁 Arquivo de saída", style="W11.TLabel").grid(row=3, column=0, sticky="w", pady=(14, 6))
        self.entry_saida = tk.Entry(
            form,
            textvariable=self.saida_var,
            width=34,
            font=("Segoe UI", 10),
            bg=self.cores["entry_bg"],
            fg=self.cores["entry_fg"],
            insertbackground=self.cores["entry_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.cores["hint"],
            highlightcolor=self.cores["accent"],
        )
        self.entry_saida.grid(row=3, column=1, sticky="ew", padx=(14, 0), pady=(14, 0), ipady=6)

        self.btn_salvar_como = tk.Button(
            form,
            text="📂 Salvar como",
            command=self.escolher_saida,
            font=("Segoe UI Semibold", 10),
            bg=self.cores["warning"],
            fg="#ffffff",
            activebackground=self.cores["warning_active"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        )
        self.btn_salvar_como.grid(
            row=3,
            column=2,
            sticky="w",
            padx=(10, 0),
            pady=(14, 0),
        )

        form.columnconfigure(1, weight=0)
        form.columnconfigure(2, weight=1)

        barra = ttk.Frame(container, style="W11Card.TFrame")
        barra.grid(row=2, column=0, sticky="ew", pady=(6, 12))

        acoes = ttk.Frame(barra, style="W11Card.TFrame")
        acoes.grid(row=0, column=0, sticky="ew")
        acoes.columnconfigure(0, weight=1)
        acoes.columnconfigure(2, weight=1)

        grupo_acoes = tk.Frame(acoes, bg=self.cores["card"], highlightthickness=0, bd=0)
        grupo_acoes.grid(row=0, column=1)

        cred_bar = tk.Frame(grupo_acoes, bg=self.cores["card"], highlightthickness=0, bd=0)
        cred_bar.grid(row=0, column=0, sticky="w")

        ttk.Label(cred_bar, text="LOGIN GSAN", style="W11FieldHint.TLabel").grid(row=0, column=0, sticky="w")
        self.entry_usuario_gsan = tk.Entry(
            cred_bar,
            textvariable=self.usuario_gsan_var,
            width=14,
            font=("Segoe UI", 10),
            bg=self.cores["entry_bg"],
            fg=self.cores["entry_fg"],
            insertbackground=self.cores["entry_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.cores["hint"],
            highlightcolor=self.cores["accent"],
            justify="left",
        )
        self.entry_usuario_gsan.grid(row=1, column=0, sticky="w", pady=(2, 0), ipady=4)

        ttk.Label(cred_bar, text="SENHA GSAN", style="W11FieldHint.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.entry_senha_gsan = tk.Entry(
            cred_bar,
            textvariable=self.senha_gsan_var,
            width=14,
            show="•",
            font=("Segoe UI", 10),
            bg=self.cores["entry_bg"],
            fg=self.cores["entry_fg"],
            insertbackground=self.cores["entry_fg"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.cores["hint"],
            highlightcolor=self.cores["accent"],
            justify="left",
        )
        self.entry_senha_gsan.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(2, 0), ipady=4)

        self.btn_executar = tk.Button(
            grupo_acoes,
            text="▶ Executar",
            command=self.executar_fluxo,
            font=("Segoe UI Semibold", 12),
            bg=self.cores["accent"],
            fg="#ffffff",
            activebackground=self.cores["accent_active"],
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=26,
            pady=9,
            cursor="hand2",
        )
        self.btn_executar.grid(row=0, column=1, sticky="e", padx=(18, 0))

        self.status_label = ttk.Label(barra, textvariable=self.status_var, style="W11Status.TLabel")
        self.status_label.grid(row=1, column=0, pady=(25, 0))

        card_log = tk.Frame(container, bg=self.cores["card"], bd=1, relief="solid", highlightthickness=0)
        card_log.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        log_wrap = ttk.Frame(card_log, style="W11Card.TFrame", padding=10)
        log_wrap.pack(fill="both", expand=True)

        ttk.Label(log_wrap, text="Log de Execução", style="W11.TLabel").pack(anchor="w", pady=(0, 6))
        self.log_box = scrolledtext.ScrolledText(
            log_wrap,
            height=17,
            wrap="word",
            font=("Consolas", 9),
            bg=self.cores["log_bg"],
            fg=self.cores["log_fg"],
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
            insertbackground=self.cores["text"],
        )
        self.log_box.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="2026 - Desenvolvido por Murilo Brenner - Versão {}".format(APP_VERSAO),
            style="W11Footer.TLabel",
        ).grid(row=4, column=0, sticky="s", pady=(12, 2))

        barra.columnconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(3, weight=1)

        self.after(120, self._focar_campo_local)

    def _focar_campo_local(self):
        try:
            self.entry_local.focus_force()
            self.entry_local.icursor("end")
        except Exception:
            pass

    def _executar_na_ui(self, funcao, *args):
        self.after(0, lambda: funcao(*args))

    def _set_processando(self, processando, status=None):
        self._processando = processando
        estado = "disabled" if processando else "normal"
        self.btn_executar.config(state=estado)
        self.btn_driver.config(state=estado)
        self.btn_salvar_como.config(state=estado)
        self.entry_usuario_gsan.config(state=estado)
        self.entry_senha_gsan.config(state=estado)
        if status:
            self.status_var.set(status)

    def log(self, texto):
        self.log_box.insert("end", str(texto) + "\n")
        self.log_box.see("end")
        self.update_idletasks()

    def escolher_saida(self):
        caminho = filedialog.asksaveasfilename(
            title="Salvar CSV de saida",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if caminho:
            self._saida_manual = True
            self.saida_var.set(caminho)
            self._salvar_preferencias()

    def _baixar_driver_worker(self):
        try:
            caminho = baixar_driver_offline()
            self._executar_na_ui(self.log, "Driver salvo em: {}".format(caminho))
            self._executar_na_ui(self.status_var.set, "Driver offline pronto")
            self._executar_na_ui(messagebox.showinfo, "Driver", "Download concluido.\n\n{}".format(caminho))
        except Exception as erro:
            self._executar_na_ui(self.log, "ERRO ao baixar driver: {}".format(erro))
            self._executar_na_ui(self.status_var.set, "Falha no download do driver")
            self._executar_na_ui(messagebox.showerror, "Erro", str(erro))
        finally:
            self._executar_na_ui(self._set_processando, False)

    def baixar_driver(self):
        if self._processando:
            return

        self._set_processando(True, "Baixando driver offline...")
        self.log("Baixando ChromeDriver para uso offline...")
        thread = threading.Thread(target=self._baixar_driver_worker, daemon=True)
        thread.start()

    def _executar_fluxo_worker(self, local, setor, rota, saida, usuario_gsan, senha_gsan):
        try:
            self._executar_na_ui(self.log, "Iniciando login no GSAN...")
            drv = login_gsan(usuario_gsan, senha_gsan)
            self._executar_na_ui(self.log, "Login realizado.")

            self._executar_na_ui(
                self.log,
                "Gerando relatorio para LOCAL={}, SETOR={}, ROTA={}...".format(local, setor, rota),
            )
            arquivo_baixado = gerar_relatorio(drv, local, setor, rota)
            self._executar_na_ui(self.log, "Arquivo baixado: {}".format(arquivo_baixado))

            total_linhas = converter_csv_baixado(arquivo_baixado, rota, saida)
            self._executar_na_ui(self.log, "Arquivo final salvo em: {}".format(saida))
            self._executar_na_ui(self.log, "Total de linhas exportadas: {}".format(total_linhas))

            self._executar_na_ui(
                messagebox.showinfo,
                "Concluido",
                "Processo concluido com sucesso.\n\nArquivo: {}\nLinhas exportadas: {}".format(saida, total_linhas),
            )
            self._executar_na_ui(self.status_var.set, "Concluido com sucesso")
            self._salvar_preferencias()
        except Exception as erro:
            self._executar_na_ui(self.log, "ERRO: {}".format(erro))
            self._executar_na_ui(messagebox.showerror, "Erro", str(erro))
            self._executar_na_ui(self.status_var.set, "Erro na execucao")
        finally:
            fechar_driver()
            self._executar_na_ui(self._set_processando, False)

    def executar_fluxo(self):
        if self._processando:
            return

        if not self._saida_manual:
            self._sugerir_saida_automatica()

        local = self.local_var.get().strip()
        setor = self.setor_var.get().strip()
        rota = self.rota_var.get().strip()
        usuario_gsan = self.usuario_gsan_var.get().strip()
        senha_gsan = self.senha_gsan_var.get().strip()
        saida = self.saida_var.get().strip()

        if not local or not setor or not rota:
            messagebox.showwarning("Campos obrigatorios", "Informe LOCAL, SETOR e ROTA.")
            return
        if not saida:
            messagebox.showwarning("Saida", "Escolha onde salvar o arquivo de saida.")
            return
        if not usuario_gsan or not senha_gsan:
            messagebox.showwarning("Credenciais GSAN", "Informe LOGIN GSAN e SENHA GSAN.")
            return

        self._set_processando(True, "Executando processo...")
        self._salvar_preferencias()
        thread = threading.Thread(
            target=self._executar_fluxo_worker,
            args=(local, setor, rota, saida, usuario_gsan, senha_gsan),
            daemon=True,
        )
        thread.start()

    def ao_fechar(self):
        self._salvar_preferencias()
        fechar_driver()
        self.destroy()


if __name__ == "__main__":
    configurar_app_id_windows()
    mostrar_splash()
    app = App()
    app.mainloop()