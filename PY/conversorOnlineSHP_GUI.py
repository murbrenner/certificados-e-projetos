#NOME: Assistente de Atualização Cadastral

#DESCRIÇÃO: Ferramenta para converter e organizar dados do cadastro entre Google, QGIS e GSAN, gerando CSV e SHP prontos para atualização cadastral.

#PRÉ-REQUISITO: GOOGLE > QGIS: CSV da planilha online com coordenadas e campos básicos (ROTA, Nº DA VISITA, LOCALIDADE, SETOR, MATRÍCULA) e QGIS aberto para criar/carregar SHP; GERAR CSV: camadas IMÓVEL, QUADRAS, OVERLEY/OVERLAY, ROTAS DE LEITURA e Ruas_MA ou ARRUAMENTO_MA carregadas, com rotas previamente selecionadas; QGIS > GSAN: CSV Google (dados cadastrais) + CSV QGIS (seq_id, rot_id, coordenadas etc.) e arquivo CEP.csv disponível para escolher município/CEP e preencher CEP_GSAN.


import csv
import math
import os
import re
import time
import unicodedata
from urllib.parse import quote

import pandas as pd
import processing
from qgis.PyQt.QtCore import Qt, QVariant, QSettings, QStandardPaths
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QListView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    Qgis,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsProcessingFeatureSourceDefinition,
    QgsProject,
    QgsProperty,
    QgsSpatialIndex,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes,
)


def avisar(texto, nivel=Qgis.Info, duracao=6):
    if "iface" in globals() and iface is not None:
        iface.messageBar().pushMessage("Conversor", texto, level=nivel, duration=duracao)
    else:
        print(texto)


def remover_acentos(texto):
    if not isinstance(texto, str):
        return texto
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def deduzir_sexo(nome):
    if not nome or str(nome).strip() in ["", "0", "nan", "None"]:
        return "01 - MASCULINO"
    primeiro_nome = str(nome).strip().upper().split()[0]
    masculinos_excecao = ["LUCA", "JOSHUA", "GARCIA", "COSTA", "SILVA", "SOUSA", "SOUZA"]
    if primeiro_nome in masculinos_excecao:
        return "01 - MASCULINO"
    if primeiro_nome.endswith("A"):
        return "02 - FEMININO"
    return "01 - MASCULINO"


def int_seguro(valor, padrao=0):
    try:
        if pd.isna(valor):
            return padrao
        return int(float(str(valor).strip()))
    except Exception:
        return padrao


def str_num_sem_decimal(valor):
    if pd.isna(valor):
        return "0"
    txt = str(valor).strip()
    if txt.endswith(".0"):
        return txt[:-2]
    return txt


def detectar_xy(headers):
    normalizados = {h.strip().lower(): h for h in headers}
    candidatos = [
        ("x", "y"),
        ("lon", "lat"),
        ("lng", "lat"),
        ("longitude", "latitude"),
        ("long", "lat"),
        ("coord_x", "coord_y"),
        ("easting", "northing"),
    ]
    for x_key, y_key in candidatos:
        if x_key in normalizados and y_key in normalizados:
            return normalizados[x_key], normalizados[y_key]
    return None, None


def normalizar_localidade(valor):
    try:
        return int(float(str(valor).replace(",", ".")))
    except (TypeError, ValueError):
        return 0


def aplicar_estilo_rotulo(camada, campo_rotulo):
    simbolo = QgsMarkerSymbol.createSimple(
        {
            "name": "circle",
            "color": "127,255,0",
            "outline_color": "40,90,40",
            "outline_width": "0.2",
            "size": "2.8",
        }
    )
    camada.renderer().setSymbol(simbolo)

    if campo_rotulo:
        conf_rotulo = QgsPalLayerSettings()
        conf_rotulo.enabled = True
        conf_rotulo.fieldName = campo_rotulo
        formato = QgsTextFormat()
        formato.setSize(9)
        formato.setColor(QColor("white"))
        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(1.2)
        buffer.setColor(QColor("blue"))
        formato.setBuffer(buffer)
        conf_rotulo.setFormat(formato)
        camada.setLabelsEnabled(True)
        camada.setLabeling(QgsVectorLayerSimpleLabeling(conf_rotulo))
    else:
        camada.setLabelsEnabled(False)

    camada.triggerRepaint()


def salvar_shp(camada, caminho_saida):
    opcoes = QgsVectorFileWriter.SaveVectorOptions()
    opcoes.driverName = "ESRI Shapefile"
    opcoes.fileEncoding = "UTF-8"
    opcoes.layerName = os.path.splitext(os.path.basename(caminho_saida))[0]
    erro, msg_erro, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
        camada,
        caminho_saida,
        QgsProject.instance().transformContext(),
        opcoes,
    )
    return erro, msg_erro


class ConversorOnlineSHPDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assistente de Atualização Cadastral")
        self.setFixedSize(880, 660)
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setStyleSheet(
            """
            QDialog { background-color: #f7f9fc; }
            QTabWidget::pane { border: 1px solid #d8dee9; border-radius: 4px; background: #ffffff; top: -1px; }
            QTabBar::tab { background: #e8edf5; color: #1f2937; width: 130px; height: 30px; margin-right: 3px; border: 1px solid #d8dee9; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #2563eb; color: #ffffff; font-weight: 600; border-color: #1d4ed8; }
            QTabBar::tab:!selected { margin-top: 2px; }
            QLabel { color: #1f2937; }
            QLineEdit, QComboBox { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 5px; }
            QPushButton { background: #2563eb; color: #ffffff; border: none; border-radius: 6px; padding: 6px 10px; }
            QPushButton:hover { background: #1d4ed8; }
            QProgressBar { border: 1px solid #cbd5e1; border-radius: 6px; text-align: center; background: #f1f5f9; }
            QProgressBar::chunk { background-color: #22c55e; border-radius: 5px; }
            """
        )
        self.alinhar_running = False
        self.conversor2_running = False
        self.inserir_dados_running = False
        self.perpendicular_running = False
        self.pdf_running = False
        self._pdf_namespace = None
        self.municipios_data = {}
        self.selected_cep_id = None
        self.tabs = QTabWidget(self)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setElideMode(Qt.ElideRight)
        self._montar_ui()

    def _montar_ui(self):
        root = QVBoxLayout(self)
        root.addWidget(self.tabs)
        self._montar_tab_online_shp()
        self._montar_tab_alinhar_pontos()
        self._montar_tab_gerar_csv()
        self._montar_tab_converter_base()
        self._montar_tab_inserir_dados()
        self._montar_tab_perpendicular()
        self._montar_tab_gerar_pdf()

    def _criar_row_arquivo(self, line_edit, callback):
        linha = QHBoxLayout()
        linha.addWidget(line_edit)
        btn = QPushButton("...")
        btn.setFixedWidth(40)
        btn.clicked.connect(callback)
        linha.addWidget(btn)
        w = QWidget()
        w.setLayout(linha)
        return w

    def _montar_tab_online_shp(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.input_csv = QLineEdit()
        self.localidade = QLineEdit()
        self.rota = QLineEdit()
        self.status = QLabel("Aguardando...")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        form.addRow(
            "Planilha Online (CSV):",
            self._criar_row_arquivo(self.input_csv, self.selecionar_csv_online),
        )
        form.addRow("Localidade (opcional):", self.localidade)
        form.addRow("Rota (opcional):", self.rota)

        info = QLabel(
            "Saída automática em segundo plano:\n"
            "- CSV convertido na mesma pasta do CSV\n"
            "- SHP em SHP\\ na mesma pasta\n"
            "- SHP carregado em edição com estilo"
        )
        info.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_converter = QPushButton("Converter")
        btn_fechar = QPushButton("Fechar")
        btn_converter.clicked.connect(self.executar_online_para_shp)
        btn_fechar.clicked.connect(self.close)
        botoes.addWidget(btn_converter)
        botoes.addWidget(btn_fechar)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "GOOGLE > QGIS")

    def _montar_tab_converter_base(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.conv_google_csv = QLineEdit()
        self.conv_qgis_csv = QLineEdit()
        self.conv_output_csv = QLineEdit()
        self.conv_localidade = QLineEdit()
        self.conv_rota = QLineEdit()
        self.conv_status = QLabel("Aguardando...")
        self.conv_progress = QProgressBar()
        self.conv_progress.setRange(0, 100)
        self.conv_progress.setValue(0)

        form.addRow(
            "Planilha Google:",
            self._criar_row_arquivo(self.conv_google_csv, self.selecionar_google_csv),
        )
        form.addRow(
            "Planilha CSV QGIS:",
            self._criar_row_arquivo(self.conv_qgis_csv, self.selecionar_qgis_csv),
        )
        form.addRow(
            "Relatório de Saída:",
            self._criar_row_arquivo(self.conv_output_csv, self.selecionar_output_csv),
        )
        self.conv_municipio_combo = QComboBox()
        self.conv_cep_combo = QComboBox()
        self.conv_municipio_combo.setView(QListView())
        self.conv_cep_combo.setView(QListView())
        popup_style = (
            "QListView { background: #ffffff; color: #1f2937; border: 1px solid #cbd5e1; "
            "selection-background-color: #2563eb; selection-color: #ffffff; outline: 0; }"
            "QListView::item:hover { background: #2563eb; color: #ffffff; }"
            "QListView::item:selected { background: #2563eb; color: #ffffff; }"
        )
        self.conv_municipio_combo.view().setStyleSheet(popup_style)
        self.conv_cep_combo.view().setStyleSheet(popup_style)
        self.conv_municipio_combo.currentIndexChanged.connect(self.on_municipio_changed)
        self.conv_cep_combo.currentIndexChanged.connect(self.on_cep_changed)
        form.addRow("Município:", self.conv_municipio_combo)
        form.addRow("CEP:", self.conv_cep_combo)
        form.addRow("Localidade (opcional):", self.conv_localidade)
        form.addRow("Rota (opcional):", self.conv_rota)

        info = QLabel(
            "Guia 2 (app antigo): cruza Planilha Google + CSV QGIS\n"
            "e gera relatório cadastral de saída."
        )
        info.setWordWrap(True)
        self.conv_cep_status = QLabel("")
        self.conv_cep_status.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_converter = QPushButton("Converter")
        btn_cancelar = QPushButton("Cancelar")
        btn_converter.clicked.connect(self.executar_converter_base)
        btn_cancelar.clicked.connect(self.cancelar_converter_base)
        botoes.addWidget(btn_converter)
        botoes.addWidget(btn_cancelar)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addWidget(self.conv_cep_status)
        layout.addWidget(self.conv_progress)
        layout.addWidget(self.conv_status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "QGIS > GSAN")
        self.carregar_base_ceps()

    def _montar_tab_inserir_dados(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.ins_localidade = QLineEdit()
        self.ins_setor = QLineEdit()
        self.ins_gerencia = QLineEdit()
        self.ins_municipio = QLineEdit()
        self.ins_status = QLabel("Aguardando...")
        self.ins_progress = QProgressBar()
        self.ins_progress.setRange(0, 100)
        self.ins_progress.setValue(0)

        form.addRow("Localidade:", self.ins_localidade)
        form.addRow("Setor:", self.ins_setor)
        form.addRow("Gerência:", self.ins_gerencia)
        form.addRow("Município:", self.ins_municipio)

        info = QLabel(
            "Insere dados nas camadas a partir das rotas selecionadas,\n"
            "substituindo as janelas de entrada por estes campos."
        )
        info.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_executar = QPushButton("Executar")
        btn_cancelar = QPushButton("Cancelar")
        btn_executar.clicked.connect(self.executar_inserir_dados)
        btn_cancelar.clicked.connect(self.cancelar_inserir_dados)
        botoes.addWidget(btn_executar)
        botoes.addWidget(btn_cancelar)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addWidget(self.ins_progress)
        layout.addWidget(self.ins_status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "INSERIR DADOS")

    def _montar_tab_alinhar_pontos(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.alinhar_pontos_combo = QComboBox()
        self.alinhar_pontos_combo.setView(QListView())
        popup_style = (
            "QListView { background: #ffffff; color: #1f2937; border: 1px solid #cbd5e1; "
            "selection-background-color: #2563eb; selection-color: #ffffff; outline: 0; }"
            "QListView::item:hover { background: #2563eb; color: #ffffff; }"
            "QListView::item:selected { background: #2563eb; color: #ffffff; }"
        )
        self.alinhar_pontos_combo.view().setStyleSheet(popup_style)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.setFixedWidth(70)
        btn_atualizar.clicked.connect(self._atualizar_combo_pontos_alinhar)

        linha_combo = QHBoxLayout()
        linha_combo.addWidget(self.alinhar_pontos_combo)
        linha_combo.addWidget(btn_atualizar)
        linha_combo_widget = QWidget()
        linha_combo_widget.setLayout(linha_combo)

        self.alinhar_status = QLabel("Aguardando...")
        self.alinhar_progress = QProgressBar()
        self.alinhar_progress.setRange(0, 100)
        self.alinhar_progress.setValue(0)

        form.addRow("Camada de pontos:", linha_combo_widget)

        info = QLabel(
            "Alinha os pontos selecionados às bordas das quadras da rota selecionada,\n"
            "atualiza o campo 'seq_id' com a métrica (metros) e ajusta o ponto inicial\n"
            "pela distância até o vértice mais próximo. Ao final, pergunta se deseja\n"
            "copiar para IMÓVEL. Camadas necessárias: ROTAS DE LEITURA (com rota\n"
            "selecionada) e QUADRAS."
        )
        info.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_exec = QPushButton("Alinhar e Calcular Métrica")
        btn_cancel = QPushButton("Cancelar")
        btn_exec.clicked.connect(self.executar_alinhar_pontos)
        btn_cancel.clicked.connect(self.cancelar_alinhar_pontos)
        botoes.addWidget(btn_exec)
        botoes.addWidget(btn_cancel)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addWidget(self.alinhar_progress)
        layout.addWidget(self.alinhar_status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "ALINHAR PONTOS")
        self._atualizar_combo_pontos_alinhar()

    def _montar_tab_gerar_csv(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.gerar_csv_output = QLineEdit()
        self.gerar_csv_status = QLabel("Aguardando...")
        self.gerar_csv_progress = QProgressBar()
        self.gerar_csv_progress.setRange(0, 100)
        self.gerar_csv_progress.setValue(0)

        form.addRow(
            "Arquivo de Saída:",
            self._criar_row_arquivo(self.gerar_csv_output, self.selecionar_gerar_csv_output),
        )

        info = QLabel(
            "Usa as rotas selecionadas no QGIS para gerar CSV com logradouro\n"
            "a partir das camadas do projeto."
        )
        info.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_gerar = QPushButton("Gerar CSV")
        btn_fechar = QPushButton("Cancelar")
        btn_gerar.clicked.connect(self.executar_gerar_csv)
        btn_fechar.clicked.connect(self.cancelar_gerar_csv)
        botoes.addWidget(btn_gerar)
        botoes.addWidget(btn_fechar)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addWidget(self.gerar_csv_progress)
        layout.addWidget(self.gerar_csv_status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "GERAR CSV")

    def _montar_tab_perpendicular(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.perp_status = QLabel("Aguardando...")
        self.perp_progress = QProgressBar()
        self.perp_progress.setRange(0, 100)
        self.perp_progress.setValue(0)

        info = QLabel(
            "Executa o traçado perpendicular nas quadras usando as rotas selecionadas.\n"
            "Camadas necessárias: IMÓVEL, QUADRAS e ROTAS DE LEITURA."
        )
        info.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_exec = QPushButton("Traçar Perpendicular")
        btn_cancel = QPushButton("Cancelar")
        btn_exec.clicked.connect(self.executar_perpendicular)
        btn_cancel.clicked.connect(self.cancelar_perpendicular)
        botoes.addWidget(btn_exec)
        botoes.addWidget(btn_cancel)

        layout.addWidget(info)
        layout.addWidget(self.perp_progress)
        layout.addWidget(self.perp_status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "PERPENDICULAR")

    def _montar_tab_gerar_pdf(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()

        self.pdf_qpt_retrato = QLineEdit()
        self.pdf_qpt_paisagem = QLineEdit()
        self.pdf_pasta_qpt = QLineEdit()
        self.pdf_pasta_pdf = QLineEdit()
        self.pdf_localidade = QComboBox()
        self.pdf_setor = QComboBox()
        self.pdf_municipio = QComboBox()
        self.pdf_localidade.setEditable(True)
        self.pdf_setor.setEditable(True)
        self.pdf_municipio.setEditable(True)
        self.pdf_localidade.setView(QListView())
        self.pdf_setor.setView(QListView())
        self.pdf_municipio.setView(QListView())
        self.pdf_elaborado = QComboBox()
        self.pdf_elaborado.setEditable(False)
        self.pdf_elaborado.addItems(["", "GLEISON", "LUANA", "JULYANNE", "MURILO"])
        self.pdf_elaborado.setView(QListView())
        self.pdf_data = QLineEdit()
        self.pdf_exibir_imovel = QCheckBox("Exibir etiqueta de imóvel no mapa")
        self.pdf_exibir_imovel.setChecked(True)
        self.pdf_status = QLabel("Aguardando...")
        self.pdf_progress = QProgressBar()
        self.pdf_progress.setRange(0, 100)
        self.pdf_progress.setValue(0)
        self.pdf_localidades_csv_path = (
            r"\\10.39.192.3\OCRCC\PYTHON\AUTOMAÇÃO QGIS\CSV\localidades.csv"
        )
        self.pdf_logo_fixo_path = r"\\10.39.192.3\ocrcc\PYTHON\AUTOMAÇÃO QGIS\caemaLogo.png"
        self.pdf_localidades_data = []
        popup_style = (
            "QListView { background: #ffffff; color: #1f2937; border: 1px solid #cbd5e1; "
            "selection-background-color: #2563eb; selection-color: #ffffff; outline: 0; }"
            "QListView::item:hover { background: #2563eb; color: #ffffff; }"
            "QListView::item:selected { background: #2563eb; color: #ffffff; }"
        )
        self.pdf_localidade.view().setStyleSheet(popup_style)
        self.pdf_setor.view().setStyleSheet(popup_style)
        self.pdf_municipio.view().setStyleSheet(popup_style)
        self.pdf_elaborado.view().setStyleSheet(popup_style)

        form.addRow(
            "QPT retrato (opcional):",
            self._criar_row_arquivo(self.pdf_qpt_retrato, self.selecionar_pdf_qpt_retrato),
        )
        form.addRow(
            "QPT paisagem (opcional):",
            self._criar_row_arquivo(self.pdf_qpt_paisagem, self.selecionar_pdf_qpt_paisagem),
        )
        form.addRow(
            "Saída QPT:",
            self._criar_row_arquivo(self.pdf_pasta_qpt, self.selecionar_pdf_pasta_qpt),
        )
        form.addRow(
            "Saída PDF:",
            self._criar_row_arquivo(self.pdf_pasta_pdf, self.selecionar_pdf_pasta_pdf),
        )
        form.addRow("Município:", self.pdf_municipio)
        form.addRow("Localidade:", self.pdf_localidade)
        form.addRow("Setor:", self.pdf_setor)
        form.addRow("Elaborado por:", self.pdf_elaborado)
        form.addRow("Data (dd/mm/aaaa):", self.pdf_data)
        form.addRow("", self.pdf_exibir_imovel)

        info = QLabel(
            "Gera PDF das rotas selecionadas usando os templates QPT.\n"
            "Sem abrir janelas de parâmetros durante a execução."
        )
        info.setWordWrap(True)

        botoes = QHBoxLayout()
        btn_exec = QPushButton("Gerar PDF")
        btn_cancel = QPushButton("Cancelar")
        btn_exec.clicked.connect(self.executar_gerar_pdf)
        btn_cancel.clicked.connect(self.cancelar_gerar_pdf)
        botoes.addWidget(btn_exec)
        botoes.addWidget(btn_cancel)

        layout.addLayout(form)
        layout.addWidget(info)
        layout.addWidget(self.pdf_progress)
        layout.addWidget(self.pdf_status)
        layout.addStretch(1)
        layout.addLayout(botoes)
        self.tabs.addTab(tab, "GERAR PDF")
        self.pdf_localidade.currentTextChanged.connect(self._on_pdf_localidade_changed)
        self.pdf_setor.currentTextChanged.connect(self._on_pdf_setor_changed)
        self.pdf_municipio.currentTextChanged.connect(self._on_pdf_municipio_changed)
        self._preencher_defaults_pdf()

    def _normalizar_txt_pdf(self, valor):
        return remover_acentos(str(valor or "")).strip().upper()

    def _split_setores_pdf(self, setor_raw):
        return [s.strip() for s in str(setor_raw or "").split(",") if s.strip()]

    def _normalizar_nome_pasta_pdf(self, valor, fallback):
        nome = str(valor or "").strip()
        nome = remover_acentos(nome)
        nome = re.sub(r'[<>:"/\\|?*]', "_", nome)
        nome = re.sub(r"\s+", " ", nome).strip()
        return nome or fallback

    def _carregar_localidades_csv_pdf(self):
        self.pdf_localidades_data = []
        caminho = self.pdf_localidades_csv_path
        if not os.path.exists(caminho):
            self._set_status_pdf(f"CSV de localidades não encontrado: {caminho}", 0)
            return

        def _num_localidade(valor):
            txt = str(valor or "").strip()
            m = re.search(r"\d+", txt)
            if m:
                return str_num_sem_decimal(m.group(0))
            return txt

        def _get_val(row_norm, candidatos):
            for c in candidatos:
                if c in row_norm and str(row_norm.get(c, "")).strip():
                    return str(row_norm.get(c, "")).strip()
            return ""

        localidade_cands_num = [
            "LOCALIDADE",
            "COD_LOCALIDADE",
            "CD_LOCALIDADE",
            "ID_LOCALIDADE",
            "NUMERO_LOCALIDADE",
            "N_LOCALIDADE",
            "LOCAL",
        ]
        setor_cands = ["SETOR", "SETORES", "SETOR_DE_LEITURA", "NUMERO_DO_SETOR"]
        municipio_cands = [
            "NOME_LOCALIDADE",
            "NOME_DA_LOCALIDADE",
            "MUNICIPIO",
            "MUNICIPIO_NOME",
            "NOME_DO_MUNICIPIO",
        ]
        gerencia_cands = ["GERENCIA", "GERATRIZ", "GERENCIA_OPERACIONAL"]

        try:
            for encoding in ("utf-8-sig", "latin-1"):
                try:
                    with open(caminho, "r", encoding=encoding, newline="") as f:
                        amostra = f.read(4096)
                        f.seek(0)
                        try:
                            dialect = csv.Sniffer().sniff(amostra, delimiters=";,\t|")
                            reader = csv.DictReader(f, dialect=dialect)
                        except Exception:
                            reader = csv.DictReader(f, delimiter=";")

                        for row in reader:
                            if not row:
                                continue
                            row_norm = {}
                            for k, v in row.items():
                                k_norm = self._normalizar_txt_pdf(k).replace(" ", "_")
                                row_norm[k_norm] = str(v or "").strip()

                            localidade = _get_val(row_norm, localidade_cands_num)
                            # Garante que Localidade priorize o código numérico da coluna LOCALIDADE.
                            if localidade and not str_num_sem_decimal(localidade).isdigit():
                                for k, v in row_norm.items():
                                    if "LOCALIDADE" in k and str_num_sem_decimal(v).isdigit():
                                        localidade = v
                                        break

                            setor = _get_val(row_norm, setor_cands)
                            municipio = _get_val(row_norm, municipio_cands)
                            gerencia = _get_val(row_norm, gerencia_cands)

                            localidade = _num_localidade(localidade)
                            if localidade or setor or municipio:
                                self.pdf_localidades_data.append(
                                    {
                                        "localidade": localidade,
                                        "setor": setor,
                                        "municipio": municipio,
                                        "gerencia": gerencia,
                                        "setores_lista": self._split_setores_pdf(setor),
                                    }
                                )
                    if self.pdf_localidades_data:
                        return
                except Exception:
                    continue
        except Exception as e:
            self._set_status_pdf(f"Falha ao ler localidades.csv: {str(e)}", 0)

        if self.pdf_localidades_data:
            return

        try:
            ns = self._carregar_namespace_pdf()
            ler_localidades = ns.get("_ler_localidades_csv")
            dados = ler_localidades(caminho) if callable(ler_localidades) else []
            for rec in dados:
                localidade_bruta = str(rec.get("LOCALIDADE", "")).strip()
                localidade = _num_localidade(localidade_bruta)
                setor = str(rec.get("SETOR", "")).strip()
                municipio = (
                    str(rec.get("NOME LOCALIDADE", "")).strip()
                    or str(rec.get("NOME_LOCALIDADE", "")).strip()
                    or str(rec.get("MUNICIPIO", "")).strip()
                )
                gerencia = str(rec.get("GERENCIA", "")).strip()
                if localidade or setor or municipio:
                    self.pdf_localidades_data.append(
                        {
                            "localidade": localidade,
                            "setor": setor,
                            "municipio": municipio,
                            "gerencia": gerencia,
                            "setores_lista": self._split_setores_pdf(setor),
                        }
                    )
        except Exception:
            pass

    def _preencher_combo_pdf(self, combo, valores, valor_atual=""):
        combo.blockSignals(True)
        combo.clear()
        if valores:
            combo.setEditable(False)
            combo.addItems(valores)
            if valor_atual and valor_atual in valores:
                combo.setCurrentText(valor_atual)
            else:
                combo.setCurrentIndex(0)
        else:
            combo.setEditable(True)
            combo.setCurrentText(valor_atual)
        combo.blockSignals(False)

    def _registros_por_municipio_pdf(self, municipio):
        mun_norm = self._normalizar_txt_pdf(municipio)
        return [
            r
            for r in self.pdf_localidades_data
            if self._normalizar_txt_pdf(r.get("municipio", "")) == mun_norm
        ]

    def _registros_por_municipio_localidade_pdf(self, municipio, localidade):
        mun_norm = self._normalizar_txt_pdf(municipio)
        loc_norm = self._normalizar_txt_pdf(localidade)
        return [
            r
            for r in self.pdf_localidades_data
            if self._normalizar_txt_pdf(r.get("municipio", "")) == mun_norm
            and self._normalizar_txt_pdf(r.get("localidade", "")) == loc_norm
        ]

    def _on_pdf_localidade_changed(self, _=None):
        municipio = self.pdf_municipio.currentText().strip()
        localidade = self.pdf_localidade.currentText().strip()
        registros = self._registros_por_municipio_localidade_pdf(municipio, localidade)
        setores = sorted(
            {
                s
                for r in registros
                for s in (r.get("setores_lista") or [])
                if s
            }
        )
        atual_setor = self.pdf_setor.currentText().strip()
        self._preencher_combo_pdf(self.pdf_setor, setores, atual_setor)
        self._atualizar_pastas_pdf_por_campos()

    def _on_pdf_setor_changed(self, _=None):
        self._atualizar_pastas_pdf_por_campos()

    def _on_pdf_municipio_changed(self, _=None):
        municipio = self.pdf_municipio.currentText().strip()
        registros = self._registros_por_municipio_pdf(municipio)
        localidades = sorted(
            {r.get("localidade", "").strip() for r in registros if r.get("localidade", "").strip()}
        )
        atual_localidade = self.pdf_localidade.currentText().strip()
        self._preencher_combo_pdf(self.pdf_localidade, localidades, atual_localidade)
        self._on_pdf_localidade_changed()

    def _obter_rota_nome_saida(self, feat_rota=None, ns=None):
        rota_raw = ""
        if feat_rota is not None and ns and callable(ns.get("_guess_rota_label")):
            rota_raw = str(ns["_guess_rota_label"](feat_rota)).strip()
        if not rota_raw:
            layer_rotas = self._obter_camada_por_nomes(["ROTAS DE LEITURA"])
            if layer_rotas and layer_rotas.selectedFeatureCount() > 0:
                f = next(layer_rotas.getSelectedFeatures(), None)
                if f is not None:
                    rota_raw = str(self._get_attr_se_existe(layer_rotas, f, ["rota", "Rota", "rot_id"], "")).strip()
        rota_norm = str_num_sem_decimal(rota_raw).strip()
        if rota_norm.isdigit():
            return f"ROTA {int(rota_norm):02d}"
        if rota_norm:
            return "ROTA " + self._normalizar_nome_pasta_pdf(rota_norm, "SEM_ROTA")
        return "ROTA 01"

    def _atualizar_pastas_pdf_por_campos(self, _=None):
        projeto = QgsProject.instance()
        base = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        if not base:
            base = projeto.homePath() or os.path.expanduser("~")

        municipio_txt = self.pdf_municipio.currentText().strip()
        if not municipio_txt:
            self.pdf_pasta_qpt.setText("")
            self.pdf_pasta_pdf.setText("")
            return

        localidade_txt = self.pdf_localidade.currentText().strip()
        setor_txt = self.pdf_setor.currentText().strip()
        regs = self._registros_por_municipio_localidade_pdf(municipio_txt, localidade_txt)
        if setor_txt:
            setor_norm = self._normalizar_txt_pdf(setor_txt)
            regs = [
                r
                for r in regs
                if any(
                    self._normalizar_txt_pdf(s) == setor_norm
                    for s in (r.get("setores_lista") or [])
                )
            ]
        if not regs:
            regs = self._registros_por_municipio_pdf(municipio_txt)
        gerencia_txt = regs[0].get("gerencia", "").strip() if regs else ""
        gerencia = self._normalizar_nome_pasta_pdf(gerencia_txt, "SEM_GERENCIA")
        municipio = self._normalizar_nome_pasta_pdf(municipio_txt, "SEM_MUNICIPIO")
        pasta_base = os.path.join(base, gerencia, municipio)
        rota_nome = self._obter_rota_nome_saida()
        self.pdf_pasta_qpt.setText(os.path.join(pasta_base, "QPT", f"{rota_nome}.qpt"))
        self.pdf_pasta_pdf.setText(os.path.join(pasta_base, "PDF", f"{rota_nome}.pdf"))

    def _preencher_defaults_pdf(self):
        self.pdf_data.setText(time.strftime("%d/%m/%Y"))
        self.pdf_elaborado.setCurrentIndex(0)

        try:
            ns = self._carregar_namespace_pdf()
            resolver_template = ns.get("_resolver_template_qpt_padrao")
            pasta_modelos = ns.get("PASTA_MODELOS_QPT_PADRAO", "")
            modelo_retrato = ns.get("NOME_MODELO_QPT_RETRATO", "")
            modelo_paisagem = ns.get("NOME_MODELO_QPT_PAISAGEM", "")
            if callable(resolver_template):
                qpt_retrato_padrao = resolver_template(pasta_modelos, modelo_retrato)
                qpt_paisagem_padrao = resolver_template(pasta_modelos, modelo_paisagem)
                if qpt_retrato_padrao and not self.pdf_qpt_retrato.text().strip():
                    self.pdf_qpt_retrato.setText(qpt_retrato_padrao)
                if qpt_paisagem_padrao and not self.pdf_qpt_paisagem.text().strip():
                    self.pdf_qpt_paisagem.setText(qpt_paisagem_padrao)

            self._carregar_localidades_csv_pdf()
            municipios = sorted(
                {
                    r.get("municipio", "").strip()
                    for r in self.pdf_localidades_data
                    if r.get("municipio", "").strip()
                }
            )
            self._preencher_combo_pdf(self.pdf_municipio, municipios, "")
            self._on_pdf_municipio_changed()
        except Exception as e:
            self._set_status_pdf(f"Pré-preenchimento parcial: {str(e)}", 0)

    def selecionar_csv_online(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Planilha Online", "", "CSV (*.csv);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.input_csv.setText(caminho)

    def selecionar_google_csv(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Planilha Google", "", "CSV (*.csv);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.conv_google_csv.setText(caminho)

    def selecionar_qgis_csv(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecione a Planilha CSV QGIS", "", "CSV (*.csv);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.conv_qgis_csv.setText(caminho)

    def selecionar_output_csv(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório", "", "CSV (*.csv);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.conv_output_csv.setText(caminho)

    def selecionar_gerar_csv_output(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        caminho_padrao = os.path.join(downloads, "relatorio.csv")
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório CSV", caminho_padrao, "CSV (*.csv);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.gerar_csv_output.setText(caminho)

    def selecionar_pdf_qpt_retrato(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecione QPT retrato", "", "QPT (*.qpt);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.pdf_qpt_retrato.setText(caminho)

    def selecionar_pdf_qpt_paisagem(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecione QPT paisagem", "", "QPT (*.qpt);;Todos os arquivos (*.*)"
        )
        if caminho:
            self.pdf_qpt_paisagem.setText(caminho)

    def selecionar_pdf_pasta_qpt(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Selecione saída QPT", self.pdf_pasta_qpt.text().strip(), "QPT (*.qpt)"
        )
        if caminho:
            if not caminho.lower().endswith(".qpt"):
                caminho += ".qpt"
            self.pdf_pasta_qpt.setText(caminho)

    def selecionar_pdf_pasta_pdf(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Selecione saída PDF", self.pdf_pasta_pdf.text().strip(), "PDF (*.pdf)"
        )
        if caminho:
            if not caminho.lower().endswith(".pdf"):
                caminho += ".pdf"
            self.pdf_pasta_pdf.setText(caminho)

    def selecionar_pdf_logo(self):
        # Mantido apenas por compatibilidade; logo é fixo e não exposto na interface.
        pass

    def _set_status(self, texto, progresso=None):
        self.status.setText(texto)
        if progresso is not None:
            self.progress.setValue(progresso)
        QApplication.processEvents()

    def _set_status_conv2(self, texto, progresso=None):
        self.conv_status.setText(texto)
        if progresso is not None:
            self.conv_progress.setValue(progresso)
        QApplication.processEvents()

    def _set_status_inserir_dados(self, texto, progresso=None):
        self.ins_status.setText(texto)
        if progresso is not None:
            self.ins_progress.setValue(progresso)
        QApplication.processEvents()

    def _set_status_gerar_csv(self, texto, progresso=None):
        self.gerar_csv_status.setText(texto)
        if progresso is not None:
            self.gerar_csv_progress.setValue(progresso)
        QApplication.processEvents()

    def _set_status_perpendicular(self, texto, progresso=None):
        self.perp_status.setText(texto)
        if progresso is not None:
            self.perp_progress.setValue(progresso)
        QApplication.processEvents()

    def _set_status_pdf(self, texto, progresso=None):
        self.pdf_status.setText(texto)
        if progresso is not None:
            self.pdf_progress.setValue(progresso)
        QApplication.processEvents()

    def _montar_nome_base_saida(self, localidade_filtro, rota_filtro, fallback):
        localidade = re.sub(r"\s+", "", localidade_filtro or "")
        rota = re.sub(r"\s+", "", rota_filtro or "")
        if localidade and rota:
            return f"G{localidade}-R{rota}"
        return fallback

    def _obter_camada_por_nomes(self, nomes):
        for nome in nomes:
            camadas = QgsProject.instance().mapLayersByName(nome)
            if camadas:
                return camadas[0]
        return None

    def _obter_nome_campo(self, camada, candidatos):
        if camada is None:
            return None
        nomes = camada.fields().names()
        for cand in candidatos:
            if cand in nomes:
                return cand
        normalizados = {n.strip().lower(): n for n in nomes}
        for cand in candidatos:
            achado = normalizados.get(cand.strip().lower())
            if achado:
                return achado
        return None

    def _set_attr_se_existe(self, camada, feicao, candidatos, valor):
        nome = self._obter_nome_campo(camada, candidatos)
        if nome:
            feicao[nome] = valor

    def _get_attr_se_existe(self, camada, feicao, candidatos, padrao=None):
        nome = self._obter_nome_campo(camada, candidatos)
        if nome:
            return feicao[nome]
        return padrao

    def localizar_arquivo_cep(self):
        arquivo_atual = globals().get("__file__")
        candidatos = []

        if arquivo_atual:
            base_dir = os.path.dirname(os.path.abspath(arquivo_atual))
            root_dir = os.path.dirname(os.path.dirname(base_dir))
            candidatos.extend(
                [
                    os.path.join(base_dir, "CEP.csv"),
                    os.path.join(root_dir, "AUTOMAÇÃO GSAN", "PY", "CEP.csv"),
                ]
            )

        cwd = os.getcwd()
        candidatos.extend(
            [
                os.path.join(cwd, "CEP.csv"),
                os.path.join(cwd, "AUTOMAÇÃO GSAN", "PY", "CEP.csv"),
                "\\\\10.39.192.3\\ocrcc\\PYTHON\\AUTOMAÇÃO QGIS\\CSV\\CEP.csv",
            ]
        )

        for letra in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            raiz = f"{letra}:\\"
            if os.path.exists(raiz):
                candidatos.append(os.path.join(raiz, "Meu Drive", "PYTHON", "AUTOMAÇÃO GSAN", "PY", "CEP.csv"))

        for caminho in candidatos:
            if os.path.exists(caminho):
                return caminho
        return None

    def carregar_base_ceps(self):
        self.conv_municipio_combo.clear()
        self.conv_cep_combo.clear()
        self.municipios_data = {}
        self.selected_cep_id = None

        cep_path = self.localizar_arquivo_cep()
        if not cep_path:
            self.conv_cep_status.setText("CEP.csv não encontrado.")
            return

        required_cols = {"cep_id", "cep_cdcep", "cep_nmmunicipio"}
        try:
            df_cep = pd.read_csv(cep_path, sep=";", encoding="utf-8")
            if not required_cols.issubset(df_cep.columns):
                df_cep = pd.read_csv(cep_path, encoding="utf-8")
            if not required_cols.issubset(df_cep.columns):
                raise ValueError("CEP.csv sem colunas obrigatórias.")

            for _, row in df_cep.iterrows():
                municipio = str(row["cep_nmmunicipio"]).strip()
                if not municipio:
                    continue
                self.municipios_data.setdefault(municipio, []).append(
                    {
                        "cep_id": int_seguro(row["cep_id"], 0),
                        "cep_cdcep": str(row["cep_cdcep"]).strip(),
                    }
                )

            municipios = sorted(self.municipios_data.keys())
            self.conv_municipio_combo.addItem("")
            self.conv_municipio_combo.addItems(municipios)
            self.conv_cep_status.setText(f"Base CEP carregada: {len(municipios)} municípios.")
        except Exception as e:
            self.conv_cep_status.setText(f"Erro ao carregar CEP.csv: {str(e)}")

    def on_municipio_changed(self, *_args):
        municipio = self.conv_municipio_combo.currentText().strip()
        self.conv_cep_combo.clear()
        self.selected_cep_id = None
        if not municipio or municipio not in self.municipios_data:
            self.conv_cep_status.setText("")
            return

        ceps = self.municipios_data[municipio]
        self.conv_cep_combo.addItem("")
        for item in ceps:
            self.conv_cep_combo.addItem(
                f"{item['cep_cdcep']} (ID: {item['cep_id']})",
                item["cep_id"],
            )

        if len(ceps) == 1:
            self.conv_cep_combo.setCurrentIndex(1)
        else:
            self.conv_cep_status.setText(f"{len(ceps)} CEPs disponíveis para {municipio}.")

    def on_cep_changed(self, *_args):
        cep_id = self.conv_cep_combo.currentData()
        texto = self.conv_cep_combo.currentText().strip()
        if cep_id in [None, ""]:
            self.selected_cep_id = None
            return
        self.selected_cep_id = int_seguro(cep_id, 0)
        self.conv_cep_status.setText(f"CEP selecionado: {texto}")

    def executar_online_para_shp(self):
        csv_entrada = self.input_csv.text().strip()
        if not csv_entrada:
            QMessageBox.critical(self, "Erro", "Selecione a planilha online (CSV).")
            return
        if not os.path.exists(csv_entrada):
            QMessageBox.critical(self, "Erro", "Arquivo de entrada não encontrado.")
            return

        try:
            self._set_status("Carregando planilha...", 10)
            df = pd.read_csv(csv_entrada)
            localidade_filtro = self.localidade.text().strip()
            rota_filtro = self.rota.text().strip()

            if localidade_filtro:
                filtro = localidade_filtro.lower()
                serie = df["LOCALIDADE"].astype(str).str.lower()
                df = df[serie.str.contains(filtro, regex=False, na=False)]
                self._set_status(f"Filtro localidade aplicado: {localidade_filtro}", 20)
            if rota_filtro:
                filtro = rota_filtro.lower()
                serie = df["ROTA"].astype(str).str.lower()
                df = df[serie.str.contains(filtro, regex=False, na=False)]
                self._set_status(f"Filtro rota aplicado: {rota_filtro}", 30)
            if df.empty:
                raise ValueError("Nenhum registro encontrado com os filtros aplicados.")

            required_cols = ["MATRÍCULA DO IMÓVEL", "ROTA", "Nº DA VISITA", "LOCALIDADE", "SETOR"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError("Colunas faltando na planilha: " + ", ".join(missing_cols))

            coord_col = None
            for possible_name in ["coordenadas", "Coordenadas", "COORDENADAS", "coords", "Coords"]:
                if possible_name in df.columns:
                    coord_col = possible_name
                    break
            if not coord_col:
                raise ValueError("Coluna de coordenadas não encontrada.")

            output_data = []
            total = len(df)
            self._set_status("Processando linhas...", 40)
            for idx, (_, row) in enumerate(df.iterrows(), start=1):
                coords_str = str(row[coord_col]).strip()
                latitude = "0"
                longitude = "0"
                if "," in coords_str:
                    parts = coords_str.split(",")
                    if len(parts) >= 2:
                        latitude = parts[0].strip()
                        longitude = parts[1].strip()

                imv_id = str_num_sem_decimal(row["MATRÍCULA DO IMÓVEL"])
                rot_id = str_num_sem_decimal(row["ROTA"])
                seq_id = str_num_sem_decimal(row["Nº DA VISITA"])
                localidade_raw = str(row["LOCALIDADE"]).strip()
                localidade_match = re.search(r"\d+", localidade_raw)
                localidade = localidade_match.group() if localidade_match else "0"

                output_data.append(
                    {
                        "latitude": latitude,
                        "longitude": longitude,
                        "imv_id": "" if imv_id in ["0", "nan"] else imv_id,
                        "rot_id": "" if rot_id in ["0", "nan"] else rot_id,
                        "seq_id": "" if seq_id in ["0", "nan"] else seq_id,
                        "localidade": localidade,
                        "Setor": str(row["SETOR"]).strip(),
                    }
                )
                self._set_status(f"Processando linhas... {idx}/{total}", 40 + int((idx / total) * 35))

            df_output = pd.DataFrame(output_data)
            pasta_origem = os.path.dirname(csv_entrada)
            nome_base_entrada = os.path.splitext(os.path.basename(csv_entrada))[0]
            nome_base_saida = self._montar_nome_base_saida(localidade_filtro, rota_filtro, nome_base_entrada)
            csv_saida = os.path.join(pasta_origem, f"{nome_base_saida}.csv")
            df_output.to_csv(csv_saida, index=False, quoting=csv.QUOTE_MINIMAL)
            self._set_status("CSV convertido salvo.", 80)

            with open(csv_saida, "r", encoding="utf-8-sig", newline="") as f:
                headers = next(csv.reader(f), [])
            if not headers:
                raise ValueError("Não foi possível ler o cabeçalho do CSV convertido.")

            x_field, y_field = detectar_xy(headers)
            if not x_field or not y_field:
                raise ValueError("Não foi possível detectar campos X/Y automaticamente.")

            pasta_shp = os.path.join(pasta_origem, "SHP")
            os.makedirs(pasta_shp, exist_ok=True)
            shp_path = os.path.join(pasta_shp, f"{nome_base_saida}.shp")
            if os.path.exists(shp_path):
                resp = QMessageBox.question(
                    self,
                    "Sobrescrever SHP",
                    f"O arquivo já existe:\n{shp_path}\n\nDeseja sobrescrever?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if resp != QMessageBox.Yes:
                    self._set_status("Cancelado: SHP existente não foi sobrescrito.", 0)
                    return

            uri = (
                f"file:///{csv_saida.replace(os.sep, '/')}"
                f"?delimiter=,&detectTypes=yes&xField={quote(x_field)}&yField={quote(y_field)}"
                f"&crs=EPSG:{quote('4326')}&geomType=point&decimalPoint=."
            )
            camada_csv = QgsVectorLayer(uri, f"{nome_base_saida}_tmp_csv", "delimitedtext")
            if not camada_csv.isValid():
                raise ValueError("Falha ao carregar CSV convertido como camada temporária.")

            QgsProject.instance().addMapLayer(camada_csv)
            campo_rotulo = "seq_id" if camada_csv.fields().indexOf("seq_id") >= 0 else None
            aplicar_estilo_rotulo(camada_csv, campo_rotulo)
            erro, msg_erro = salvar_shp(camada_csv, shp_path)
            QgsProject.instance().removeMapLayer(camada_csv.id())
            if erro != QgsVectorFileWriter.NoError:
                raise ValueError(f"Erro ao salvar SHP: {msg_erro}")

            camada_shp = QgsVectorLayer(shp_path, nome_base_saida, "ogr")
            if not camada_shp.isValid():
                raise ValueError("SHP foi salvo, mas falhou ao carregar no QGIS.")
            QgsProject.instance().addMapLayer(camada_shp)
            aplicar_estilo_rotulo(camada_shp, campo_rotulo)
            if not camada_shp.startEditing():
                avisar("SHP carregado, mas não foi possível entrar em modo de edição.", Qgis.Warning)
            if "iface" in globals() and iface is not None:
                iface.setActiveLayer(camada_shp)
                iface.mapCanvas().refresh()

            self._set_status(f"Concluído! {len(df_output)} linhas processadas.", 100)
            QMessageBox.information(
                self,
                "Sucesso",
                "Processamento concluído!\n\n"
                f"Linhas processadas: {len(df_output)}\nCSV: {csv_saida}\nSHP: {shp_path}",
            )
        except Exception as e:
            self._set_status(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro ao processar:\n{str(e)}")

    def cancelar_gerar_csv(self):
        self._set_status_gerar_csv("Cancelado pelo usuário.", 0)

    def executar_gerar_csv(self):
        arquivo_saida = self.gerar_csv_output.text().strip()
        if not arquivo_saida:
            QMessageBox.critical(self, "Erro", "Selecione o arquivo de saída.")
            return

        layer_imovel = self._obter_camada_por_nomes(["IMÓVEL", "IMOVEL"])
        layer_quadras = self._obter_camada_por_nomes(["QUADRAS"])
        layer_overlay = self._obter_camada_por_nomes(["OVERLEY", "OVERLAY"])
        layer_rotas = self._obter_camada_por_nomes(["ROTAS DE LEITURA"])
        camada_ruas = self._obter_camada_por_nomes(["Ruas_MA", "ARRUAMENTO_MA"])

        faltantes = []
        if layer_imovel is None:
            faltantes.append("IMÓVEL")
        if layer_quadras is None:
            faltantes.append("QUADRAS")
        if layer_overlay is None:
            faltantes.append("OVERLEY/OVERLAY")
        if layer_rotas is None:
            faltantes.append("ROTAS DE LEITURA")
        if camada_ruas is None:
            faltantes.append("Ruas_MA/ARRUAMENTO_MA")
        if faltantes:
            QMessageBox.critical(
                self,
                "Erro",
                "Camadas não encontradas no projeto:\n- " + "\n- ".join(faltantes),
            )
            return

        rotas_preselecionadas = layer_rotas.selectedFeatures()
        if not rotas_preselecionadas:
            QMessageBox.critical(self, "Erro", "Selecione pelo menos uma rota em 'ROTAS DE LEITURA'.")
            return

        try:
            self._set_status_gerar_csv("Preparando camadas...", 5)
            indice_ruas = QgsSpatialIndex(camada_ruas.getFeatures())
            medidor = QgsDistanceArea()
            medidor.setEllipsoid("WGS84")
            ruas_dict = {f.id(): f for f in camada_ruas.getFeatures()}
            total_rotas = len(rotas_preselecionadas)
            linhas_processadas = 0

            cabecalho = [
                "localidade",
                "Setor",
                "quadra",
                "seq_id",
                "rot_id",
                "imv_id",
                "latitude",
                "longitude",
                "alterar",
                "logradouro",
                "cod_log",
            ]

            with open(arquivo_saida, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(cabecalho)
                linhas_csv = []

                for idx_rota, rota in enumerate(rotas_preselecionadas, start=1):
                    self._set_status_gerar_csv(
                        f"Processando rota {idx_rota}/{total_rotas}...", 10 + int((idx_rota / total_rotas) * 70)
                    )
                    layer_rotas.selectByIds([rota.id()])
                    layer_quadras.removeSelection()
                    layer_overlay.removeSelection()

                    processing.run(
                        "native:selectbylocation",
                        {
                            "INPUT": layer_quadras,
                            "PREDICATE": [0, 1, 5, 6, 7],
                            "INTERSECT": QgsProcessingFeatureSourceDefinition(layer_rotas.id(), True, rota.id()),
                            "METHOD": 0,
                        },
                    )

                    processing.run(
                        "native:selectbylocation",
                        {
                            "INPUT": layer_overlay,
                            "PREDICATE": [0, 1, 5, 6, 7],
                            "INTERSECT": QgsProcessingFeatureSourceDefinition(layer_rotas.id(), True, rota.id()),
                            "METHOD": 0,
                        },
                    )

                    localidade = 0
                    for overlay in layer_overlay.selectedFeatures():
                        campos_overlay = overlay.fields().names()
                        if "localidade " in campos_overlay:
                            localidade = normalizar_localidade(overlay["localidade "])
                        elif "localidade" in campos_overlay:
                            localidade = normalizar_localidade(overlay["localidade"])
                        break

                    for quadra in layer_quadras.selectedFeatures():
                        layer_quadras.selectByIds([quadra.id()])
                        layer_imovel.removeSelection()

                        processing.run(
                            "native:selectbylocation",
                            {
                                "INPUT": layer_imovel,
                                "PREDICATE": [0, 1, 4, 5, 6, 7],
                                "INTERSECT": QgsProcessingFeatureSourceDefinition(
                                    layer_quadras.id(), True, quadra.id()
                                ),
                                "METHOD": 0,
                            },
                        )

                        for imovel in layer_imovel.selectedFeatures():
                            ponto = imovel.geometry().asPoint()
                            proximas_ids = indice_ruas.nearestNeighbor(ponto, 5)
                            menor_dist = float("inf")
                            nome_rua = ""

                            for rua_id in proximas_ids:
                                rua = ruas_dict.get(rua_id)
                                if rua is None:
                                    continue
                                ponto_mais_proximo = rua.geometry().nearestPoint(imovel.geometry()).asPoint()
                                dist = medidor.measureLine(ponto, ponto_mais_proximo)
                                if dist < menor_dist:
                                    menor_dist = dist
                                    nome_rua = str(rua["name"]) if "name" in rua.fields().names() else ""

                            imv_id_valor = imovel["imv_id"]
                            if pd.isna(imv_id_valor) or str(imv_id_valor).strip().lower() in [
                                "",
                                "null",
                                "none",
                                "nan",
                            ]:
                                imv_id_valor = 0

                            linhas_csv.append(
                                (
                                    localidade,
                                    quadra["setor"],
                                    quadra["quadra"],
                                    imovel["seq_id"],
                                    imovel["rot_id"],
                                    imv_id_valor,
                                    imovel["latitude"],
                                    imovel["longitude"],
                                    "1",
                                    nome_rua,
                                    "",
                                )
                            )

                def chave_seq_id(linha):
                    try:
                        return float(str(linha[3]).replace(",", "."))
                    except Exception:
                        return float("inf")

                linhas_csv.sort(key=chave_seq_id)
                for linha in linhas_csv:
                    writer.writerow(linha)
                linhas_processadas = len(linhas_csv)

            self._set_status_gerar_csv(f"Concluído! {linhas_processadas} linhas geradas.", 100)
            QMessageBox.information(
                self,
                "Sucesso",
                f"CSV gerado com sucesso!\n\nLinhas processadas: {linhas_processadas}\nArquivo: {arquivo_saida}",
            )
        except Exception as e:
            self._set_status_gerar_csv(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro ao gerar CSV:\n{str(e)}")

    def cancelar_inserir_dados(self):
        self.inserir_dados_running = False
        self._set_status_inserir_dados("Cancelado pelo usuário.", 0)

    def executar_inserir_dados(self):
        try:
            upd_local = int(self.ins_localidade.text().strip())
            upd_setor = int(self.ins_setor.text().strip())
        except Exception:
            QMessageBox.critical(self, "Erro", "Localidade e Setor devem ser numéricos.")
            return

        upd_gerencia = self.ins_gerencia.text().strip()
        upd_municipio = self.ins_municipio.text().strip()
        if not upd_gerencia or not upd_municipio:
            QMessageBox.critical(self, "Erro", "Preencha Gerência e Município.")
            return

        layer_overlay = self._obter_camada_por_nomes(["OVERLEY", "OVERLAY"])
        layer_imovel = self._obter_camada_por_nomes(["IMÓVEL", "IMOVEL"])
        layer_inicio = self._obter_camada_por_nomes(["INICIO_PNT"])
        layer_fim = self._obter_camada_por_nomes(["FIM_PNT"])
        layer_rotas = self._obter_camada_por_nomes(["ROTAS DE LEITURA"])
        layer_quadras = self._obter_camada_por_nomes(["QUADRAS"])
        layer_arruamento = self._obter_camada_por_nomes(["ARRUAMENTO_MA"])

        faltantes = []
        if layer_overlay is None:
            faltantes.append("OVERLEY/OVERLAY")
        if layer_imovel is None:
            faltantes.append("IMÓVEL")
        if layer_inicio is None:
            faltantes.append("INICIO_PNT")
        if layer_fim is None:
            faltantes.append("FIM_PNT")
        if layer_rotas is None:
            faltantes.append("ROTAS DE LEITURA")
        if layer_quadras is None:
            faltantes.append("QUADRAS")
        if layer_arruamento is None:
            faltantes.append("ARRUAMENTO_MA")
        if faltantes:
            QMessageBox.critical(
                self,
                "Erro",
                "Camadas não encontradas no projeto:\n- " + "\n- ".join(faltantes),
            )
            return

        rotas_sel = layer_rotas.selectedFeatures()
        if not rotas_sel:
            QMessageBox.critical(self, "Erro", "Selecione pelo menos uma rota em 'ROTAS DE LEITURA'.")
            return

        for lyr in [layer_overlay, layer_imovel, layer_inicio, layer_fim, layer_rotas, layer_quadras, layer_arruamento]:
            if not lyr.isEditable():
                lyr.startEditing()

        self.inserir_dados_running = True
        total = len(rotas_sel)
        try:
            for idx, rota in enumerate(rotas_sel, start=1):
                if not self.inserir_dados_running:
                    break

                self._set_status_inserir_dados(f"Processando rota {idx}/{total}...", int((idx / total) * 90))
                layer_rotas.selectByIds([rota.id()])
                layer_quadras.removeSelection()
                layer_overlay.removeSelection()
                layer_imovel.removeSelection()
                layer_arruamento.removeSelection()
                layer_inicio.removeSelection()
                layer_fim.removeSelection()

                for destino in [layer_imovel, layer_arruamento, layer_quadras, layer_overlay, layer_inicio, layer_fim]:
                    processing.run(
                        "native:selectbylocation",
                        {
                            "INPUT": destino,
                            "PREDICATE": [0],
                            "INTERSECT": QgsProcessingFeatureSourceDefinition(layer_rotas.id(), True, rota.id()),
                            "METHOD": 0,
                        },
                    )

                upd_rota = self._get_attr_se_existe(layer_rotas, rota, ["rota", "Rota"], None)
                if upd_rota is None:
                    raise ValueError("Campo de rota não encontrado na camada ROTAS DE LEITURA.")

                self._set_attr_se_existe(layer_rotas, rota, ["rota", "Rota"], upd_rota)
                self._set_attr_se_existe(layer_rotas, rota, ["setor", "Setor"], upd_setor)
                self._set_attr_se_existe(layer_rotas, rota, ["gerencia", "Gerencia"], upd_gerencia)
                self._set_attr_se_existe(layer_rotas, rota, ["localidade", "localidade "], upd_local)
                layer_rotas.updateFeature(rota)

                for imovel in layer_imovel.selectedFeatures():
                    self._set_attr_se_existe(layer_imovel, imovel, ["rot_id"], upd_rota)
                    self._set_attr_se_existe(layer_imovel, imovel, ["Setor", "setor"], upd_setor)
                    self._set_attr_se_existe(layer_imovel, imovel, ["gerencia", "Gerencia"], upd_gerencia)
                    seq_val = self._get_attr_se_existe(layer_imovel, imovel, ["seq_id"], None)
                    if seq_val is not None:
                        self._set_attr_se_existe(layer_imovel, imovel, ["visita_campo"], seq_val)
                    self._set_attr_se_existe(layer_imovel, imovel, ["localidade", "localidade "], upd_local)

                    geom = imovel.geometry()
                    if geom and not geom.isEmpty():
                        if geom.isMultipart():
                            p = geom.asMultiPoint()[0] if geom.asMultiPoint() else geom.centroid().asPoint()
                        else:
                            try:
                                p = geom.asPoint()
                            except Exception:
                                p = geom.centroid().asPoint()
                        self._set_attr_se_existe(layer_imovel, imovel, ["latitude"], p.y())
                        self._set_attr_se_existe(layer_imovel, imovel, ["longitude"], p.x())

                    layer_imovel.selectByIds([imovel.id()])
                    processing.run(
                        "native:selectbylocation",
                        {
                            "INPUT": layer_quadras,
                            "PREDICATE": [0],
                            "INTERSECT": QgsProcessingFeatureSourceDefinition(layer_imovel.id(), True, imovel.id()),
                            "METHOD": 0,
                        },
                    )
                    for quadra in layer_quadras.selectedFeatures():
                        quadra_val = self._get_attr_se_existe(layer_quadras, quadra, ["quadra"], None)
                        if quadra_val is not None:
                            self._set_attr_se_existe(layer_imovel, imovel, ["quadra"], quadra_val)
                        break
                    layer_imovel.updateFeature(imovel)

                for arruamento in layer_arruamento.selectedFeatures():
                    self._set_attr_se_existe(layer_arruamento, arruamento, ["cd_setor"], upd_setor)
                    self._set_attr_se_existe(layer_arruamento, arruamento, ["nm_mun"], upd_municipio)
                    self._set_attr_se_existe(layer_arruamento, arruamento, ["localidade", "localidade "], upd_local)
                    layer_arruamento.updateFeature(arruamento)

                for quadra in layer_quadras.selectedFeatures():
                    self._set_attr_se_existe(layer_quadras, quadra, ["rota", "Rota"], upd_rota)
                    self._set_attr_se_existe(layer_quadras, quadra, ["setor", "Setor"], upd_setor)
                    self._set_attr_se_existe(layer_quadras, quadra, ["gerencia", "Gerencia"], upd_gerencia)
                    self._set_attr_se_existe(layer_quadras, quadra, ["localidade", "localidade "], upd_local)
                    layer_quadras.updateFeature(quadra)

                for overlay in layer_overlay.selectedFeatures():
                    self._set_attr_se_existe(layer_overlay, overlay, ["rota", "Rota"], upd_rota)
                    self._set_attr_se_existe(layer_overlay, overlay, ["localidade ", "localidade"], upd_local)
                    self._set_attr_se_existe(layer_overlay, overlay, ["setor", "Setor"], upd_setor)
                    self._set_attr_se_existe(layer_overlay, overlay, ["gerencia ", "gerencia", "Gerencia"], upd_gerencia)
                    self._set_attr_se_existe(layer_overlay, overlay, ["municipio", "Município"], upd_municipio)
                    layer_overlay.updateFeature(overlay)

                for inicio in layer_inicio.selectedFeatures():
                    self._set_attr_se_existe(layer_inicio, inicio, ["Rota", "rota"], upd_rota)
                    self._set_attr_se_existe(layer_inicio, inicio, ["Setor", "setor"], upd_setor)
                    self._set_attr_se_existe(layer_inicio, inicio, ["Gerencia", "gerencia"], upd_gerencia)
                    self._set_attr_se_existe(layer_inicio, inicio, ["localidade", "localidade "], upd_local)
                    layer_inicio.updateFeature(inicio)

                for fim in layer_fim.selectedFeatures():
                    self._set_attr_se_existe(layer_fim, fim, ["Rota ", "Rota", "rota"], upd_rota)
                    self._set_attr_se_existe(layer_fim, fim, ["Setor", "setor"], upd_setor)
                    self._set_attr_se_existe(layer_fim, fim, ["Gerencia", "gerencia"], upd_gerencia)
                    self._set_attr_se_existe(layer_fim, fim, ["localidade", "localidade "], upd_local)
                    layer_fim.updateFeature(fim)

            self._set_status_inserir_dados("Concluído!", 100)
            QMessageBox.information(self, "Sucesso", "Dados inseridos nas camadas com sucesso.")
        except Exception as e:
            self._set_status_inserir_dados(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro ao inserir dados:\n{str(e)}")
        finally:
            self.inserir_dados_running = False

    def cancelar_converter_base(self):
        self.conversor2_running = False
        self._set_status_conv2("Cancelado pelo usuário.", 0)

    def executar_converter_base(self):
        arquivo_google = self.conv_google_csv.text().strip()
        arquivo_qgis = self.conv_qgis_csv.text().strip()
        arquivo_saida = self.conv_output_csv.text().strip()
        if not arquivo_google or not os.path.exists(arquivo_google):
            QMessageBox.critical(self, "Erro", "Selecione a Planilha Google.")
            return
        if not arquivo_qgis or not os.path.exists(arquivo_qgis):
            QMessageBox.critical(self, "Erro", "Selecione a Planilha CSV QGIS.")
            return
        if not arquivo_saida:
            QMessageBox.critical(self, "Erro", "Selecione o Relatório de Saída.")
            return
        if self.selected_cep_id is None:
            QMessageBox.critical(self, "Erro", "Selecione o município e o CEP.")
            return

        self.conversor2_running = True
        try:
            self._set_status_conv2("Carregando planilhas...", 10)
            df = pd.read_csv(arquivo_google)
            df = df.fillna(0).map(remover_acentos)
            df2 = pd.read_csv(arquivo_qgis)

            localidade = self.conv_localidade.text().strip()
            rota = self.conv_rota.text().strip()
            if localidade:
                df["LOCALIDADE"] = df["LOCALIDADE"].astype(str)
                df = df[df["LOCALIDADE"].str[:3] == localidade.zfill(3)]
            if rota:
                df["ROTA"] = df["ROTA"].astype(str).str.replace(".0", "", regex=False)
                df = df[df["ROTA"] == rota]
            if df.empty:
                raise ValueError("Nenhum registro encontrado com os filtros especificados.")

            # Alinha a ordem da planilha online com a ordem crescente de seq_id do QGIS por rota.
            df["__rota_sort"] = df["ROTA"].apply(str_num_sem_decimal)
            df["__visita_sort"] = pd.to_numeric(df["Nº DA VISITA"], errors="coerce").fillna(0)
            df = df.sort_values(by=["__rota_sort", "__visita_sort"], kind="stable").reset_index(drop=True)

            df2_ord = df2.copy()
            df2_ord["__rot_id_norm"] = df2_ord["rot_id"].apply(str_num_sem_decimal)
            df2_ord["__seq_id_norm"] = df2_ord["seq_id"].apply(str_num_sem_decimal)
            df2_ord["__seq_id_num"] = pd.to_numeric(df2_ord["__seq_id_norm"], errors="coerce").fillna(0)
            seq_por_rota = {}
            for rota_id, grupo in df2_ord.groupby("__rot_id_norm", dropna=False):
                seq_por_rota[rota_id] = (
                    grupo.sort_values("__seq_id_num", kind="stable")["__seq_id_norm"].tolist()
                )
            contador_seq_por_rota = {}

            self._set_status_conv2(f"Processando {len(df)} registros...", 25)
            header = [
                "ALTERAR", "ORDEM1", "ORDEM2", "LOCAL", "SETOR", "QUADRA", "LOTE", "SUBLOTE",
                "TESTADA", "SEQUENCIA", "ROTA", "MATRICULA", "COD_LOG", "BAIRRO", "CEP_GSAN",
                "NUMERO", "COMPLEMENTO", "NOME", "CPF", "CNPJ", "V_CPF", "V_CNPJ", "COD_CLIENTE",
                "EMAIL", "RG", "DATA_EXP", "SEXO", "MAE", "DATA_NASC", "TIPO_CLIENTE", "TIPO_HAB",
                "RES", "COM", "PUB", "MUN", "EST", "FED", "IND", "PEQ", "POP", "AREA", "DDD",
                "TELEFONE", "CX", "CY",
            ]

            with open(arquivo_saida, "w", newline="", encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow(header)
                total = len(df)

                for idx, (_, row) in enumerate(df.iterrows(), start=1):
                    if not self.conversor2_running:
                        break

                    matricula = int_seguro(row.get("MATRÍCULA DO IMÓVEL"), 0)
                    localidade_val = str(row.get("LOCALIDADE", "0"))[:3]
                    setor = str(row.get("SETOR", "0"))
                    rota_val = str_num_sem_decimal(row.get("ROTA", "0"))
                    num_visita = str_num_sem_decimal(row.get("Nº DA VISITA", "0"))
                    num_imovel = str_num_sem_decimal(row.get("NÚMERO DO IMÓVEL", "0"))
                    sequencias_rota = seq_por_rota.get(rota_val, [])
                    posicao_rota = contador_seq_por_rota.get(rota_val, 0)
                    if posicao_rota < len(sequencias_rota):
                        seq_saida = sequencias_rota[posicao_rota]
                        contador_seq_por_rota[rota_val] = posicao_rota + 1
                    else:
                        seq_saida = num_visita

                    econ_res = int_seguro(row.get("CATEGORIA x ECONOMIAS [RESIDENCIAL]"), 0)
                    econ_com = int_seguro(row.get("CATEGORIA x ECONOMIAS [COMERCIAL]"), 0)
                    econ_mun = int_seguro(row.get("CATEGORIA x ECONOMIAS [PUBLICO MUN.]"), 0)
                    econ_est = int_seguro(row.get("CATEGORIA x ECONOMIAS [PUBLICO EST.]"), 0)
                    econ_fed = int_seguro(row.get("CATEGORIA x ECONOMIAS [PUBLICO FED.]"), 0)
                    econ_ind = int_seguro(row.get("CATEGORIA x ECONOMIAS [INDUSTRIAL]"), 0)
                    if econ_res + econ_com + econ_mun + econ_est + econ_fed + econ_ind == 0:
                        econ_res = 1

                    cnpj = int_seguro(row.get("CNPJ"), 0)
                    v_cnpj = 1 if cnpj > 0 else 0
                    tipo_cliente = "200 - COMERCIAL" if cnpj > 0 else "100 - RESIDENCIA"

                    nome = str(row.get("NOME COMPLETO", "")).strip()
                    if not nome or nome in ["0", "nan"]:
                        nome = "CADASTRAR NOME NA CAEMA"
                    cpf = int_seguro(row.get("CPF"), 0)
                    if matricula:
                        matricula_saida = matricula
                    else:
                        matricula_saida = 1 if cpf == 0 else 0
                    cod_cliente = 1 if cpf == 0 else 0
                    v_cpf = 1
                    tipo_hab = 0 if str(row.get("OCORRENCIA DE CADASTRO", "")).strip() == "Terreno vazio" else 1

                    data_exp = str(row.get("DATA DE EXPEDIÇÃO", "0"))
                    data_nasc = str(row.get("DATA DE NASCIMENTO", "0"))
                    nome_mae = str(row.get("NOME DA MÃE", ""))
                    rg = str_num_sem_decimal(row.get("RG", "0"))
                    if rg in ["", "0", "nan", "None"]:
                        data_exp = "0"
                    email = str(row.get("E-MAIL", ""))
                    telefone_raw = str(row.get("TELEFONE DE CONTATO COM DDD", "0"))
                    if telefone_raw in ["", "0", "nan"]:
                        ddd = "0"
                        telefone = "0"
                    else:
                        ddd = telefone_raw[:2].replace("0.", "0")
                        telefone = telefone_raw[2:].replace(".0", "")
                        if not ddd:
                            ddd = "0"
                        if not telefone:
                            telefone = "0"

                    econ_pub = 1 if (econ_mun > 0 or econ_est > 0 or econ_fed > 0) else 0
                    bairro = "CENTRO"
                    sexo = deduzir_sexo(nome)

                    quadra = 0
                    cod_log_saida = 0
                    latitude = 0
                    longitude = 0
                    encontrou = False

                    for _, row2 in df2.iterrows():
                        if matricula and not encontrou:
                            imv_id = int_seguro(row2.get("imv_id"), 0)
                            if imv_id == matricula:
                                latitude = row2.get("latitude", 0)
                                longitude = row2.get("longitude", 0)
                                quadra = str_num_sem_decimal(row2.get("quadra", 0))
                                cod_log_saida = str_num_sem_decimal(
                                    row2.get("cod_log", row2.get("COD_LOG", 0))
                                )
                                encontrou = True
                                break
                        if not encontrou:
                            rot_id = str_num_sem_decimal(row2.get("rot_id", "0"))
                            seq_id = str_num_sem_decimal(row2.get("seq_id", "0"))
                            if rot_id == rota_val and seq_id == seq_saida:
                                latitude = row2.get("latitude", 0)
                                longitude = row2.get("longitude", 0)
                                quadra = str_num_sem_decimal(row2.get("quadra", 0))
                                cod_log_saida = str_num_sem_decimal(
                                    row2.get("cod_log", row2.get("COD_LOG", 0))
                                )
                                encontrou = True
                                break

                    writer.writerow(
                        (
                            1, idx, idx, localidade_val, setor, quadra, seq_saida, 0, 0, seq_saida,
                            rota_val, matricula_saida, cod_log_saida, bairro, self.selected_cep_id, num_imovel, 0, nome, cpf, cnpj, v_cpf,
                            v_cnpj, cod_cliente, email, rg, data_exp, sexo, nome_mae, data_nasc,
                            tipo_cliente, tipo_hab, econ_res, econ_com, econ_pub, econ_mun, econ_est,
                            econ_fed, econ_ind, 0, 0, 40, ddd, telefone, longitude, latitude,
                        )
                    )

                    if idx % 5 == 0 or idx == total:
                        self._set_status_conv2(
                            f"Processando: {idx}/{total} registros",
                            25 + int((idx / total) * 75),
                        )

            if self.conversor2_running:
                self._set_status_conv2(f"Concluído! {len(df)} registros processados.", 100)
                QMessageBox.information(
                    self,
                    "Sucesso",
                    f"Conversão concluída!\n\nRegistros processados: {len(df)}\nArquivo: {arquivo_saida}",
                )
        except Exception as e:
            self._set_status_conv2(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro durante conversão:\n{str(e)}")
        finally:
            self.conversor2_running = False

    def cancelar_perpendicular(self):
        self.perpendicular_running = False
        self._set_status_perpendicular("Cancelado pelo usuário.", 0)

    def _pe_da_perpendicular(self, px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        comprimento_sq = dx * dx + dy * dy
        if comprimento_sq == 0:
            return ax, ay
        t = ((px - ax) * dx + (py - ay) * dy) / comprimento_sq
        t = max(0.0, min(1.0, t))
        return ax + t * dx, ay + t * dy

    def _segmentos_do_poligono(self, geom):
        segmentos = []
        if geom.isMultipart():
            poligonos = geom.asMultiPolygon()
        else:
            poligonos = [geom.asPolygon()]
        for poligono in poligonos:
            for anel in poligono:
                for i in range(len(anel) - 1):
                    ax, ay = anel[i].x(), anel[i].y()
                    bx, by = anel[i + 1].x(), anel[i + 1].y()
                    segmentos.append((ax, ay, bx, by))
        return segmentos

    def _aresta_mais_proxima(self, px, py, candidatos_quadras):
        menor_dist = math.inf
        resultado = None
        for feat in candidatos_quadras:
            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                continue
            for ax, ay, bx, by in self._segmentos_do_poligono(geom):
                fx, fy = self._pe_da_perpendicular(px, py, ax, ay, bx, by)
                dist = math.hypot(px - fx, py - fy)
                if dist < menor_dist:
                    menor_dist = dist
                    resultado = (fx, fy, ax, ay, bx, by)
        return resultado

    def executar_perpendicular(self):
        projeto = QgsProject.instance()
        imovel_layer = self._obter_camada_por_nomes(["IMÓVEL", "IMOVEL"])
        quadras_layer = self._obter_camada_por_nomes(["QUADRAS"])
        rota_layer = self._obter_camada_por_nomes(["ROTAS DE LEITURA"])

        faltantes = []
        if imovel_layer is None:
            faltantes.append("IMÓVEL")
        if quadras_layer is None:
            faltantes.append("QUADRAS")
        if rota_layer is None:
            faltantes.append("ROTAS DE LEITURA")
        if faltantes:
            QMessageBox.critical(
                self, "Erro", "Camadas não encontradas:\n- " + "\n- ".join(faltantes)
            )
            return

        feats_rota = list(rota_layer.selectedFeatures())
        if not feats_rota:
            QMessageBox.critical(
                self,
                "Erro",
                "Nenhuma feição selecionada na camada 'ROTAS DE LEITURA'.",
            )
            return

        self.perpendicular_running = True
        try:
            self._set_status_perpendicular("Preparando geometrias...", 5)
            geom_rota = feats_rota[0].geometry()
            for fr in feats_rota[1:]:
                geom_rota = geom_rota.combine(fr.geometry())

            crs_projeto = projeto.crs()
            crs_rota = rota_layer.crs()
            crs_imovel = imovel_layer.crs()
            if crs_rota != crs_projeto:
                geom_rota.transform(QgsCoordinateTransform(crs_rota, crs_projeto, projeto))

            geom_rota_imovel = QgsGeometry(geom_rota)
            if crs_projeto != crs_imovel:
                geom_rota_imovel.transform(
                    QgsCoordinateTransform(crs_projeto, crs_imovel, projeto)
                )

            bbox_imovel = geom_rota_imovel.boundingBox()
            request_imovel = QgsFeatureRequest().setFilterRect(bbox_imovel)
            pontos = []
            for f in imovel_layer.getFeatures(request_imovel):
                g = f.geometry()
                if g is None or g.isEmpty():
                    continue
                if geom_rota_imovel.intersects(g):
                    pontos.append(f)

            if not pontos:
                QMessageBox.information(
                    self, "Aviso", "Nenhum imóvel encontrado dentro da rota selecionada."
                )
                return

            xform_imovel = QgsCoordinateTransform(crs_imovel, crs_projeto, projeto)
            crs_quadras = quadras_layer.crs()
            xform_quadras = (
                QgsCoordinateTransform(crs_quadras, crs_projeto, projeto)
                if crs_quadras != crs_projeto
                else None
            )

            self._set_status_perpendicular("Indexando quadras...", 20)
            todas_quadras = {}
            for f in quadras_layer.getFeatures():
                if xform_quadras:
                    g = QgsGeometry(f.geometry())
                    g.transform(xform_quadras)
                    feat_proj = QgsFeature(f)
                    feat_proj.setGeometry(g)
                    todas_quadras[f.id()] = feat_proj
                else:
                    todas_quadras[f.id()] = f

            idx_quadras = QgsSpatialIndex()
            for f in todas_quadras.values():
                idx_quadras.addFeature(f)

            crs_str = crs_projeto.authid()
            camada_temp = QgsVectorLayer(f"LineString?crs={crs_str}", "PERPENDICULARES", "memory")
            provider = camada_temp.dataProvider()
            camada_etiq = QgsVectorLayer(f"Point?crs={crs_str}", "ETIQUETAS_IMOVEL", "memory")
            prov_etiq = camada_etiq.dataProvider()
            prov_etiq.addAttributes(
                [
                    QgsField("seq_id", QVariant.String),
                    QgsField("rotation", QVariant.Double),
                    QgsField("label_x", QVariant.Double),
                    QgsField("label_y", QVariant.Double),
                ]
            )
            camada_etiq.updateFields()

            feats_linha = []
            feats_etiq = []
            sem_quadra = 0
            total = len(pontos)

            for idx, ponto_feat in enumerate(pontos, start=1):
                if not self.perpendicular_running:
                    break

                geom_ponto = ponto_feat.geometry()
                if geom_ponto is None or geom_ponto.isEmpty():
                    continue

                geom_proj = QgsGeometry(geom_ponto)
                geom_proj.transform(xform_imovel)
                pt = geom_proj.asPoint()
                px, py = pt.x(), pt.y()

                ids_vizinhos = idx_quadras.nearestNeighbor(QgsPointXY(px, py), 5)
                candidatos = [todas_quadras[fid] for fid in ids_vizinhos if fid in todas_quadras]
                resultado = self._aresta_mais_proxima(px, py, candidatos)
                if resultado is None:
                    resultado = self._aresta_mais_proxima(px, py, todas_quadras.values())
                if resultado is None:
                    sem_quadra += 1
                    continue

                fx, fy, ax, ay, bx, by = resultado
                ex = 2 * px - fx
                ey = 2 * py - fy
                linha_geom = QgsGeometry.fromPolylineXY(
                    [QgsPointXY(fx, fy), QgsPointXY(px, py), QgsPointXY(ex, ey)]
                )
                feat_linha = QgsFeature()
                feat_linha.setGeometry(linha_geom)
                feats_linha.append(feat_linha)

                lx = (px + ex) / 2.0
                ly = (py + ey) / 2.0
                dx_perp = px - fx
                dy_perp = py - fy
                angulo_bruto = math.degrees(math.atan2(dy_perp, dx_perp))
                angulo = ((-angulo_bruto + 180.0) % 360.0) - 180.0
                try:
                    seq_val = str(ponto_feat["seq_id"])
                except Exception:
                    seq_val = str(ponto_feat.id())

                feat_etiq = QgsFeature(camada_etiq.fields())
                feat_etiq.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(px, py)))
                feat_etiq.setAttributes([seq_val, angulo, lx, ly])
                feats_etiq.append(feat_etiq)

                if idx % 30 == 0 or idx == total:
                    self._set_status_perpendicular(
                        f"Processando imóveis: {idx}/{total}", 20 + int((idx / total) * 75)
                    )

            provider.addFeatures(feats_linha)
            camada_temp.updateExtents()
            projeto.addMapLayer(camada_temp)

            prov_etiq.addFeatures(feats_etiq)
            camada_etiq.updateExtents()
            pal = QgsPalLayerSettings()
            pal.fieldName = "seq_id"
            pal.enabled = True
            try:
                pal.placement = Qgis.LabelPlacement.OverPoint
            except AttributeError:
                pal.placement = QgsPalLayerSettings.OverPoint
            dd = pal.dataDefinedProperties()
            dd.setProperty(QgsPalLayerSettings.LabelRotation, QgsProperty.fromField("rotation"))
            dd.setProperty(QgsPalLayerSettings.PositionX, QgsProperty.fromField("label_x"))
            dd.setProperty(QgsPalLayerSettings.PositionY, QgsProperty.fromField("label_y"))
            pal.setDataDefinedProperties(dd)

            buf = QgsTextBufferSettings()
            buf.setEnabled(True)
            buf.setColor(QColor(0, 0, 255))
            buf.setSize(1.0)
            fmt = QgsTextFormat()
            fmt.setColor(QColor(255, 255, 255))
            fmt.setBuffer(buf)
            pal.setFormat(fmt)
            camada_etiq.setLabeling(QgsVectorLayerSimpleLabeling(pal))
            camada_etiq.setLabelsEnabled(True)
            projeto.addMapLayer(camada_etiq)

            self._set_status_perpendicular("Concluído!", 100)
            origem = f"{len(pontos)} imóvel(is) dentro da rota selecionada"
            msg = (
                f"Concluído! {len(feats_linha)} perpendicular(es) e {len(feats_etiq)} etiqueta(s) "
                f"criada(s) a partir de {origem}."
            )
            if sem_quadra:
                msg += f"\n{sem_quadra} ponto(s) ignorado(s) por não encontrar quadra próxima."
            QMessageBox.information(self, "Perpendiculares — Concluído", msg)
        except Exception as e:
            self._set_status_perpendicular(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro ao traçar perpendiculares:\n{str(e)}")
        finally:
            self.perpendicular_running = False

    def cancelar_gerar_pdf(self):
        self.pdf_running = False
        self._set_status_pdf("Cancelado pelo usuário.", 0)

    def _carregar_namespace_pdf(self):
        if self._pdf_namespace is not None:
            return self._pdf_namespace

        caminhos_tentativa = []
        arquivo_atual = globals().get("__file__")
        if arquivo_atual:
            caminhos_tentativa.append(
                os.path.join(os.path.dirname(os.path.abspath(arquivo_atual)), "gerarPdfDaRotaSelecionada.py")
            )
        try:
            caminhos_tentativa.append(os.path.join(os.getcwd(), "gerarPdfDaRotaSelecionada.py"))
        except Exception:
            pass
        caminhos_tentativa.append(
            r"G:\Meu Drive\PYTHON\AUTOMAÇÃO QGIS\PY\gerarPdfDaRotaSelecionada.py"
        )
        caminhos_tentativa.append(
            r"\\10.39.192.3\ocrcc\PYTHON\AUTOMAÇÃO QGIS\PY\gerarPdfDaRotaSelecionada.py"
        )
        caminhos_tentativa.append(
            r"\\10.39.192.3\OCRCC\PYTHON\AUTOMAÇÃO QGIS\PY\gerarPdfDaRotaSelecionada.py"
        )

        caminho = next((p for p in caminhos_tentativa if p and os.path.exists(p)), None)
        if not caminho:
            raise FileNotFoundError("Script 'gerarPdfDaRotaSelecionada.py' não encontrado.")

        with open(caminho, "r", encoding="utf-8") as f:
            linhas = f.readlines()
        linhas_sem_auto = [ln for ln in linhas if ln.strip() != "_auto_run()"]
        namespace = {"__name__": "__pdf_embed__"}
        exec("".join(linhas_sem_auto), namespace)
        self._pdf_namespace = namespace
        return namespace

    def executar_gerar_pdf(self):
        qpt_retrato = self.pdf_qpt_retrato.text().strip()
        qpt_paisagem = self.pdf_qpt_paisagem.text().strip()
        saida_qpt = self.pdf_pasta_qpt.text().strip()
        saida_pdf = self.pdf_pasta_pdf.text().strip()
        logo_path = self.pdf_logo_fixo_path

        if not qpt_retrato and not qpt_paisagem:
            QMessageBox.critical(self, "Erro", "Informe ao menos um arquivo QPT (retrato ou paisagem).")
            return
        if qpt_retrato and not os.path.exists(qpt_retrato):
            QMessageBox.critical(self, "Erro", f"QPT retrato não encontrado:\n{qpt_retrato}")
            return
        if qpt_paisagem and not os.path.exists(qpt_paisagem):
            QMessageBox.critical(self, "Erro", f"QPT paisagem não encontrado:\n{qpt_paisagem}")
            return
        if not saida_qpt or not saida_pdf:
            QMessageBox.critical(self, "Erro", "Informe as pastas de saída de QPT e PDF.")
            return
        pasta_qpt = os.path.dirname(saida_qpt) if saida_qpt.lower().endswith(".qpt") else saida_qpt
        pasta_pdf = os.path.dirname(saida_pdf) if saida_pdf.lower().endswith(".pdf") else saida_pdf
        try:
            os.makedirs(pasta_qpt, exist_ok=True)
            os.makedirs(pasta_pdf, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível preparar as pastas de saída:\n{str(e)}")
            return

        self.pdf_running = True
        try:
            self._set_status_pdf("Carregando módulo de exportação...", 5)
            ns = self._carregar_namespace_pdf()
            projeto = QgsProject.instance()

            if not os.path.exists(logo_path):
                raise ValueError(f"Logo CAEMA não encontrado: {logo_path}")
            QSettings().setValue(ns["SETTINGS_KEY_LOGO_CAEMA"], logo_path)

            layer_rota = ns["_get_layer"](ns["NOME_CAMADA_ROTA"])
            if layer_rota is None:
                raise RuntimeError("Camada de rotas não encontrada.")
            rotas_selecionadas = list(layer_rota.selectedFeatures())
            if not rotas_selecionadas:
                raise RuntimeError("Selecione pelo menos uma rota em 'ROTAS DE LEITURA'.")

            layers_base = {
                "rota": layer_rota,
                "quadras": ns["_get_layer"](ns["NOME_CAMADA_QUADRAS"]),
                "arruamento": ns["_get_layer"](ns["NOME_CAMADA_ARRUAMENTO"]),
                "imovel": ns["_get_layer"](ns["NOME_CAMADA_IMOVEL"]),
                "overley": ns["_get_layer"](ns["NOME_CAMADA_OVERLEY"]),
                "inicio": ns["_get_layer"](ns["NOME_CAMADA_INICIO"]),
                "fim": ns["_get_layer"](ns["NOME_CAMADA_FIM"]),
            }

            config_exportacao = {
                "qpt_retrato": qpt_retrato,
                "qpt_paisagem": qpt_paisagem,
                "qpt_output_dir": pasta_qpt,
                "pdf_output_dir": pasta_pdf,
                "EXIBIR_IMOVEL_ETIQ": self.pdf_exibir_imovel.isChecked(),
                "LOCALIDADE": self.pdf_localidade.currentText().strip(),
                "SETOR": self.pdf_setor.currentText().strip(),
                "ROTA": "",
                "MUNICIPIO": self.pdf_municipio.currentText().strip(),
                "ELABORADO POR": self.pdf_elaborado.currentText().strip(),
                "DATA": self.pdf_data.text().strip() or time.strftime("%d/%m/%Y"),
            }

            erros = []
            total = len(rotas_selecionadas)
            for idx, feat_rota in enumerate(rotas_selecionadas, start=1):
                if not self.pdf_running:
                    break
                self._set_status_pdf(f"Exportando rota {idx}/{total}...", 10 + int((idx / total) * 85))
                try:
                    resultado = ns["_exportar_rota"](projeto, layers_base, feat_rota, config_exportacao)
                    rota_nome = self._obter_rota_nome_saida(feat_rota=feat_rota, ns=ns)
                    destino_qpt = os.path.join(pasta_qpt, f"{rota_nome}.qpt")
                    destino_pdf = os.path.join(pasta_pdf, f"{rota_nome}.pdf")
                    if resultado and isinstance(resultado, dict):
                        origem_qpt = resultado.get("qpt")
                        origem_pdf = resultado.get("pdf")
                        if origem_qpt and os.path.exists(origem_qpt):
                            if os.path.exists(destino_qpt):
                                os.remove(destino_qpt)
                            os.replace(origem_qpt, destino_qpt)
                        if origem_pdf and os.path.exists(origem_pdf):
                            if os.path.exists(destino_pdf):
                                os.remove(destino_pdf)
                            os.replace(origem_pdf, destino_pdf)
                except Exception as e:
                    erros.append(f"Rota {idx}: {str(e)}")

            if not self.pdf_running:
                self._set_status_pdf("Cancelado pelo usuário.", 0)
                return

            self._set_status_pdf("Concluído!", 100)
            if erros:
                QMessageBox.warning(
                    self,
                    "Concluído com avisos",
                    f"PDF gerado com {len(erros)} falha(s).\n\n" + "\n".join(erros[:10]),
                )
            else:
                QMessageBox.information(self, "Sucesso", "PDF(s) gerado(s) com sucesso.")
        except Exception as e:
            self._set_status_pdf(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF:\n{str(e)}")
        finally:
            self.pdf_running = False

    def cancelar_alinhar_pontos(self):
        self.alinhar_running = False
        self._set_status_alinhar("Cancelado pelo usuário.", 0)

    def _set_status_alinhar(self, texto, progresso=None):
        self.alinhar_status.setText(texto)
        if progresso is not None:
            self.alinhar_progress.setValue(progresso)
        QApplication.processEvents()

    def _listar_camadas_pontos_alinhar(self):
        camadas = [
            lyr
            for lyr in QgsProject.instance().mapLayers().values()
            if isinstance(lyr, QgsVectorLayer) and lyr.geometryType() == QgsWkbTypes.PointGeometry
        ]
        camadas.sort(key=lambda l: l.name().lower())
        return camadas

    def _atualizar_combo_pontos_alinhar(self):
        atual = self.alinhar_pontos_combo.currentText().strip()
        nomes = [lyr.name() for lyr in self._listar_camadas_pontos_alinhar()]
        self.alinhar_pontos_combo.blockSignals(True)
        self.alinhar_pontos_combo.clear()
        self.alinhar_pontos_combo.addItems(nomes)
        if atual in nomes:
            self.alinhar_pontos_combo.setCurrentText(atual)
        elif "IMÓVEL" in nomes:
            self.alinhar_pontos_combo.setCurrentText("IMÓVEL")
        elif "IMOVEL" in nomes:
            self.alinhar_pontos_combo.setCurrentText("IMOVEL")
        elif nomes:
            self.alinhar_pontos_combo.setCurrentIndex(0)
        self.alinhar_pontos_combo.blockSignals(False)

    def executar_alinhar_pontos(self):
        projeto = QgsProject.instance()
        quadras = self._obter_camada_por_nomes(["QUADRAS"])
        rotas = self._obter_camada_por_nomes(["ROTAS DE LEITURA"])

        faltantes = []
        if quadras is None:
            faltantes.append("QUADRAS")
        if rotas is None:
            faltantes.append("ROTAS DE LEITURA")
        if faltantes:
            QMessageBox.critical(
                self, "Erro", "Camadas não encontradas:\n- " + "\n- ".join(faltantes)
            )
            return

        if rotas.selectedFeatureCount() == 0:
            QMessageBox.critical(
                self,
                "Erro",
                "Nenhuma rota selecionada em 'ROTAS DE LEITURA'. Selecione ao menos uma rota antes de executar.",
            )
            return

        nome_pontos = self.alinhar_pontos_combo.currentText().strip()
        if not nome_pontos:
            QMessageBox.critical(self, "Erro", "Selecione a camada de pontos a alinhar.")
            return

        pontos_layers = projeto.mapLayersByName(nome_pontos)
        if not pontos_layers:
            QMessageBox.critical(self, "Erro", f"Camada de pontos '{nome_pontos}' não encontrada.")
            return
        pontos_layer = pontos_layers[0]

        self.alinhar_running = True
        buffer_layer = None
        try:
            self._set_status_alinhar("Montando geometria da(s) rota(s) selecionada(s)...", 5)

            geoms_rota = []
            transform = None
            if rotas.crs() != quadras.crs():
                transform = QgsCoordinateTransform(rotas.crs(), quadras.crs(), projeto)

            for feat in rotas.selectedFeatures():
                geom = feat.geometry()
                if not geom or geom.isEmpty():
                    continue
                geom_rota = QgsGeometry(geom)
                if transform is not None:
                    try:
                        geom_rota.transform(transform)
                    except Exception:
                        continue
                geoms_rota.append(geom_rota)

            if not geoms_rota:
                raise ValueError("Nenhuma geometria válida encontrada nas rotas selecionadas.")

            mascara_rota = QgsGeometry.unaryUnion(geoms_rota)
            if not mascara_rota or mascara_rota.isEmpty():
                raise ValueError("Falha ao criar máscara espacial a partir das rotas selecionadas.")

            self._set_status_alinhar("Selecionando quadras da rota...", 10)
            ids_quadras = []
            request = QgsFeatureRequest().setFilterRect(mascara_rota.boundingBox())
            for feat in quadras.getFeatures(request):
                geom_q = feat.geometry()
                if geom_q and not geom_q.isEmpty() and geom_q.intersects(mascara_rota):
                    ids_quadras.append(feat.id())
            quadras.selectByIds(ids_quadras)

            if not ids_quadras:
                raise ValueError("Nenhuma quadra encontrada dentro/intersectando as rotas selecionadas.")

            self._set_status_alinhar(f"{len(ids_quadras)} quadra(s) selecionada(s). Gerando buffer...", 20)
            buffer_result = processing.run('native:buffer', {
                'INPUT': QgsProcessingFeatureSourceDefinition(
                    quadras.source(),
                    selectedFeaturesOnly=True,
                    featureLimit=-1,
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
                ),
                'DISTANCE': -4.0,
                'SEGMENTS': 1,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': True,
                'SEPARATE_DISJOINT': True,
                'OUTPUT': 'memory:BUFFER1'
            })

            self._set_status_alinhar("Corrigindo geometrias do buffer...", 25)
            fix_result = processing.run('qgis:fixgeometries', {
                'INPUT': buffer_result['OUTPUT'],
                'OUTPUT': 'memory:BUFFER_ALINHAMENTO'
            })
            buffer_layer = fix_result['OUTPUT']
            projeto.addMapLayer(buffer_layer)
            poligonos_layer = buffer_layer

            crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

            self._set_status_alinhar("Filtrando pontos na área das quadras...", 35)
            geoms_quadras_mask = []
            transform_quadras_para_pontos = None
            if quadras.crs() != pontos_layer.crs():
                transform_quadras_para_pontos = QgsCoordinateTransform(
                    quadras.crs(), pontos_layer.crs(), projeto
                )
            for feat_quadra in quadras.selectedFeatures():
                geom_q = feat_quadra.geometry()
                if not geom_q or geom_q.isEmpty():
                    continue
                geom_q2 = QgsGeometry(geom_q)
                if transform_quadras_para_pontos is not None:
                    try:
                        geom_q2.transform(transform_quadras_para_pontos)
                    except Exception:
                        continue
                geoms_quadras_mask.append(geom_q2)

            if not geoms_quadras_mask:
                raise ValueError("Nenhuma quadra válida para usar como máscara de pontos.")

            mascara_quadras = QgsGeometry.unaryUnion(geoms_quadras_mask)
            req_pts = QgsFeatureRequest().setFilterRect(mascara_quadras.boundingBox())
            pontos_filtrados = []
            for fpt in pontos_layer.getFeatures(req_pts):
                gpt = fpt.geometry()
                if gpt and not gpt.isEmpty() and gpt.intersects(mascara_quadras):
                    pontos_filtrados.append(fpt)

            if not pontos_filtrados:
                raise ValueError(f"Nenhum ponto da camada '{nome_pontos}' foi encontrado na rota selecionada.")

            total_pts = len(pontos_filtrados)
            self._set_status_alinhar(f"Alinhando {total_pts} ponto(s) às bordas das quadras...", 40)

            nova_layer = QgsVectorLayer("Point?crs=EPSG:4326", "PONTOS_ALINHADOS", "memory")
            nova_prov = nova_layer.dataProvider()
            nova_prov.addAttributes(pontos_layer.fields())
            nova_layer.updateFields()

            distance_area = QgsDistanceArea()
            distance_area.setEllipsoid('WGS84')
            distancia_minima_m = 1.0
            pontos_aceitos = []

            for idx, ponto in enumerate(pontos_filtrados, start=1):
                if not self.alinhar_running:
                    break
                geom_ponto = QgsGeometry(ponto.geometry())
                if geom_ponto.isEmpty():
                    continue

                if pontos_layer.crs() != crs_wgs84:
                    xform = QgsCoordinateTransform(pontos_layer.crs(), crs_wgs84, projeto)
                    geom_ponto.transform(xform)

                ponto_xy = geom_ponto.asPoint()
                menor_distancia = float('inf')
                ponto_mais_proximo = None

                for poligono in poligonos_layer.getFeatures():
                    geom_poligono = QgsGeometry(poligono.geometry())
                    if geom_poligono.isEmpty():
                        continue
                    if poligonos_layer.crs() != crs_wgs84:
                        xform = QgsCoordinateTransform(poligonos_layer.crs(), crs_wgs84, projeto)
                        geom_poligono.transform(xform)

                    if geom_poligono.isMultipart():
                        poligonos = geom_poligono.asMultiPolygon()
                    else:
                        poligonos = [geom_poligono.asPolygon()]

                    for poly in poligonos:
                        if not poly:
                            continue
                        vertices = poly[0]
                        for i in range(len(vertices) - 1):
                            aresta = QgsGeometry.fromPolylineXY([vertices[i], vertices[i + 1]])
                            ponto_proximo = aresta.nearestPoint(geom_ponto)
                            distancia = distance_area.measureLine(ponto_xy, ponto_proximo.asPoint())
                            if distancia < menor_distancia:
                                menor_distancia = distancia
                                ponto_mais_proximo = ponto_proximo

                if ponto_mais_proximo:
                    pt_novo = ponto_mais_proximo.asPoint()
                    respeita_distancia = True
                    for pt_existente in pontos_aceitos:
                        if distance_area.measureLine(pt_novo, pt_existente) < distancia_minima_m:
                            respeita_distancia = False
                            break
                    if respeita_distancia:
                        novo_ponto = QgsFeature(nova_layer.fields())
                        novo_ponto.setGeometry(ponto_mais_proximo)
                        novo_ponto.setAttributes(ponto.attributes())
                        nova_prov.addFeature(novo_ponto)
                        pontos_aceitos.append(pt_novo)

                if idx % 20 == 0 or idx == total_pts:
                    self._set_status_alinhar(
                        f"Alinhando pontos: {idx}/{total_pts}", 40 + int((idx / total_pts) * 30)
                    )

            nova_layer.updateExtents()

            if not self.alinhar_running:
                self._set_status_alinhar("Cancelado pelo usuário.", 0)
                return

            if nova_layer.featureCount() == 0:
                raise ValueError("Nenhum ponto pôde ser alinhado às quadras selecionadas.")

            # Calcula a métrica (metros) e sobrescreve o próprio campo 'seq_id' na
            # camada final de pontos alinhados — sem criar cópia nem campo novo.
            self._set_status_alinhar("Calculando métrica e atualizando 'seq_id'...", 75)
            campo_seq = "seq_id"
            idx_seq = nova_layer.fields().indexFromName(campo_seq)
            if idx_seq < 0:
                raise ValueError(f"Campo '{campo_seq}' não encontrado na camada de pontos.")
            tipo_campo_seq = nova_layer.fields().field(idx_seq).type()

            def _valor_para_campo_seq(valor_num):
                if tipo_campo_seq == QVariant.String:
                    return str(valor_num)
                return valor_num

            feats_final = list(nova_layer.getFeatures())
            if len(feats_final) < 2:
                raise ValueError("São necessárias pelo menos 2 feições para calcular a métrica.")

            def _parse_seq(feat):
                try:
                    v = feat[campo_seq]
                    if v is None:
                        return float('inf')
                    return int(v)
                except Exception:
                    return float('inf')

            def _ponto_da_feicao(feat):
                geom = feat.geometry()
                if geom is None or geom.isEmpty():
                    return None
                if geom.type() != QgsWkbTypes.PointGeometry:
                    return None
                try:
                    return geom.asPoint()
                except Exception:
                    try:
                        mp = geom.asMultiPoint()
                        return mp[0] if mp else None
                    except Exception:
                        return None

            feats_ordenados = sorted(feats_final, key=_parse_seq)

            dist2 = QgsDistanceArea()
            try:
                dist2.setSourceCrs(nova_layer.crs(), projeto.transformContext())
            except Exception:
                dist2.setSourceCrs(nova_layer.crs(), None)
            try:
                dist2.setEllipsoid(projeto.ellipsoid())
            except Exception:
                dist2.setEllipsoid('WGS84')
            try:
                dist2.setEllipsoidalMode(True)
            except Exception:
                try:
                    dist2.setEllipsoidal(True)
                except Exception:
                    pass

            p_prev = _ponto_da_feicao(feats_ordenados[0])
            if p_prev is None:
                raise ValueError("A primeira feição (menor seq_id) não possui geometria válida.")

            resultados = {feats_ordenados[0].id(): 0}
            cumulative = 0
            for i in range(1, len(feats_ordenados)):
                p_cur = _ponto_da_feicao(feats_ordenados[i])
                if p_cur is None:
                    resultados[feats_ordenados[i].id()] = cumulative
                    continue
                try:
                    seg = dist2.measureLine(p_prev, p_cur)
                except Exception:
                    seg = 0.0
                if seg is None:
                    seg = 0.0
                cumulative += int(round(seg))
                resultados[feats_ordenados[i].id()] = cumulative
                p_prev = p_cur

            for fid, valor in resultados.items():
                nova_prov.changeAttributeValues({fid: {idx_seq: _valor_para_campo_seq(valor)}})

            # Passo final: o ponto de menor seq_id recebe a distância real até o
            # vértice mais próximo da camada QUADRAS, em vez do 0 padrão.
            self._set_status_alinhar("Calculando distância até o vértice mais próximo...", 88)
            ponto_inicial_feat = feats_ordenados[0]
            ponto_inicial_xy = _ponto_da_feicao(ponto_inicial_feat)

            vertices_quadras = []
            transform_quadras_para_pontos = None
            if quadras.crs() != nova_layer.crs():
                transform_quadras_para_pontos = QgsCoordinateTransform(
                    quadras.crs(), nova_layer.crs(), projeto
                )
            for feat_poly in quadras.selectedFeatures():
                geom_poly = feat_poly.geometry()
                if geom_poly is None or geom_poly.isEmpty():
                    continue
                geom_poly2 = QgsGeometry(geom_poly)
                if transform_quadras_para_pontos is not None:
                    try:
                        geom_poly2.transform(transform_quadras_para_pontos)
                    except Exception:
                        continue
                if geom_poly2.isMultipart():
                    aneis_poligonos = geom_poly2.asMultiPolygon()
                else:
                    aneis_poligonos = [geom_poly2.asPolygon()]
                for poly in aneis_poligonos:
                    if not poly:
                        continue
                    for anel in poly:
                        vertices_quadras.extend(anel)

            if vertices_quadras and ponto_inicial_xy is not None:
                menor_dist_vertice = float('inf')
                for v in vertices_quadras:
                    d = dist2.measureLine(ponto_inicial_xy, QgsPointXY(v.x(), v.y()))
                    if d < menor_dist_vertice:
                        menor_dist_vertice = d
                if menor_dist_vertice != float('inf'):
                    nova_prov.changeAttributeValues(
                        {
                            ponto_inicial_feat.id(): {
                                idx_seq: _valor_para_campo_seq(int(round(menor_dist_vertice)))
                            }
                        }
                    )

            nova_layer.updateExtents()

            # Remove a camada temporária de buffer/quadra: já cumpriu seu papel de
            # alinhamento e não deve permanecer no projeto ("alinhou, puft, excluiu!").
            self._set_status_alinhar("Removendo camada temporária de alinhamento...", 92)
            projeto.removeMapLayer(buffer_layer.id())
            buffer_layer = None

            renderer_origem = pontos_layer.renderer()
            if renderer_origem is not None:
                nova_layer.setRenderer(renderer_origem.clone())
            labeling_origem = pontos_layer.labeling()
            if labeling_origem is not None:
                nova_layer.setLabeling(labeling_origem.clone())
            nova_layer.setLabelsEnabled(pontos_layer.labelsEnabled())
            nova_layer.setOpacity(pontos_layer.opacity())
            projeto.addMapLayer(nova_layer)

            total_final = nova_layer.featureCount()
            self._set_status_alinhar(
                f"Concluído! {total_final} ponto(s) alinhado(s) e com métrica calculada.", 97
            )

            resposta = QMessageBox.question(
                self,
                "Copiar para IMÓVEL?",
                f"{total_final} ponto(s) alinhado(s) e calculado(s) em 'PONTOS_ALINHADOS'.\n\n"
                "Deseja copiar esses pontos para a camada 'IMÓVEL' agora?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if resposta == QMessageBox.Yes:
                layer_imovel = self._obter_camada_por_nomes(["IMÓVEL", "IMOVEL"])
                if layer_imovel is None:
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Camada 'IMÓVEL' não encontrada. Os pontos calculados permanecem em 'PONTOS_ALINHADOS'.",
                    )
                else:
                    if not layer_imovel.isEditable():
                        layer_imovel.startEditing()
                    campos_destino = layer_imovel.fields()
                    transform_final = None
                    if nova_layer.crs() != layer_imovel.crs():
                        transform_final = QgsCoordinateTransform(
                            nova_layer.crs(), layer_imovel.crs(), projeto
                        )
                    copiados = 0
                    for feat_origem in nova_layer.getFeatures():
                        geom_dest = QgsGeometry(feat_origem.geometry())
                        if transform_final is not None:
                            try:
                                geom_dest.transform(transform_final)
                            except Exception:
                                continue
                        novo_feat = QgsFeature(campos_destino)
                        novo_feat.setGeometry(geom_dest)
                        for campo in nova_layer.fields():
                            idx_dest = campos_destino.indexFromName(campo.name())
                            if idx_dest >= 0:
                                novo_feat.setAttribute(idx_dest, feat_origem[campo.name()])
                        layer_imovel.addFeature(novo_feat)
                        copiados += 1
                    layer_imovel.triggerRepaint()
                    self._set_status_alinhar(
                        f"Concluído! {copiados} ponto(s) copiado(s) para 'IMÓVEL' (edição pendente).", 100
                    )
                    QMessageBox.information(
                        self,
                        "Sucesso",
                        f"{copiados} ponto(s) copiado(s) para a camada 'IMÓVEL'.\n"
                        "Revise e salve (commit) as edições quando desejar.",
                    )
            else:
                self._set_status_alinhar(
                    f"Concluído! {total_final} ponto(s) calculados em 'PONTOS_ALINHADOS'.", 100
                )
                QMessageBox.information(
                    self,
                    "Concluído",
                    "Os pontos calculados permanecem na camada 'PONTOS_ALINHADOS'\n"
                    "para posicionamento manual posterior.",
                )
        except Exception as e:
            self._set_status_alinhar(f"Erro: {str(e)}", 0)
            QMessageBox.critical(self, "Erro", f"Erro ao alinhar pontos:\n{str(e)}")
        finally:
            if buffer_layer is not None:
                try:
                    projeto.removeMapLayer(buffer_layer.id())
                except Exception:
                    pass
            self.alinhar_running = False


def executar():
    global conversor_online_shp_dialog

    try:
        conversor_online_shp_dialog.close()
        conversor_online_shp_dialog.deleteLater()
    except Exception:
        pass

    conversor_online_shp_dialog = ConversorOnlineSHPDialog()
    conversor_online_shp_dialog.show()
    conversor_online_shp_dialog.raise_()
    conversor_online_shp_dialog.activateWindow()


executar()
