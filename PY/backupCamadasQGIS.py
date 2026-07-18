#NOME: Backup de Camadas do QGIS

#DESCRIÇÃO: Abre uma janela interativa (tema escuro) para selecionar as camadas do projeto e exportá-las como shapefiles + projeto QGZ na área de trabalho, dentro de uma pasta nomeada BACKUP_QGIS_(DATA).

#PRÉ-REQUISITO: Ter um projeto QGIS aberto com ao menos uma camada carregada e permissão de escrita na área de trabalho.


import os
import glob
import shutil
import re
import unicodedata
from datetime import datetime

from qgis.core import (
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsRasterLayer,
)
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QListWidget, QListWidgetItem,
    QProgressBar, QFrame,
    QApplication, QMessageBox,
)
from qgis.PyQt.QtCore import Qt
from qgis.utils import iface


# ─────────────────────────────────────────────────────────────────────────────
#  Estilo – Tema Escuro
# ─────────────────────────────────────────────────────────────────────────────
STYLE = """
QDialog {
    background-color: #12131f;
    color: #dde1f0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QLabel#lblTitulo {
    color: #79b8ff;
    font-size: 18px;
    font-weight: bold;
    padding-bottom: 2px;
}
QLabel#lblSub {
    color: #6a74a0;
    font-size: 12px;
}
QLabel#lblDestino {
    color: #79cfff;
    font-size: 12px;
    font-weight: bold;
}
QLabel#lblStatus {
    font-size: 12px;
    padding: 5px 8px;
    border-radius: 6px;
}

QFrame#separador {
    background-color: #252840;
    max-height: 1px;
    border: none;
}
QFrame#cardDestino {
    background-color: #1a1d30;
    border: 1px solid #252840;
    border-radius: 10px;
}

QListWidget {
    background-color: #1a1d30;
    color: #dde1f0;
    border: 1px solid #252840;
    border-radius: 8px;
    padding: 6px 4px;
    outline: 0;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 5px;
    margin: 1px 3px;
}
QListWidget::item:hover  { background-color: #22284a; }
QListWidget::item:selected { background-color: #22284a; }

QScrollBar:vertical {
    background: #1a1d30;
    width: 7px;
    margin: 2px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #354070;
    border-radius: 3px;
    min-height: 18px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }

QPushButton#btnSalvar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a7dda, stop:1 #5ba3ff);
    color: #ffffff;
    border: none;
    border-radius: 9px;
    padding: 10px 32px;
    font-size: 14px;
    font-weight: bold;
    min-height: 42px;
    min-width: 180px;
}
QPushButton#btnSalvar:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4a8dea, stop:1 #6eb3ff);
}
QPushButton#btnSalvar:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2a6dca, stop:1 #4a93ef);
}
QPushButton#btnSalvar:disabled {
    background: #1e2240;
    color: #3a4468;
}

QPushButton#btnMini {
    background-color: #1e2240;
    color: #8a94c0;
    border: 1px solid #2e3460;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 12px;
    min-height: 28px;
}
QPushButton#btnMini:hover {
    background-color: #2a3060;
    color: #c0cae0;
}

QPushButton#btnFechar {
    background-color: transparent;
    color: #6a74a0;
    border: 1px solid #2e3460;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 12px;
    min-height: 28px;
}
QPushButton#btnFechar:hover {
    background-color: #2a1f35;
    color: #c07ab0;
    border-color: #6a4080;
}

QProgressBar {
    background-color: #1a1d30;
    border: 1px solid #252840;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: #ffffff;
    font-size: 10px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a7dda, stop:1 #7eb8ff);
    border-radius: 5px;
}
"""

# Ícone por tipo de geometria vetorial
_GEOM_ICON = {0: "◉", 1: "╌", 2: "▬", 3: "◈"}

PRIORITY_LAYER_NAMES = [
    "IMÓVEL",
    "OVERLEY",
    "INICIO_PNT",
    "FIM_PNT",
    "QUADRAS",
    "ARRUAMENTO_MA",
    "ROTAS DE LEITURA",
    "MUNICIPIOS",
    "GOOGLE HYBRID",
]


def _normalizar_nome(nome):
    nome = unicodedata.normalize('NFKD', nome)
    nome = ''.join(c for c in nome if not unicodedata.combining(c))
    nome = nome.upper().strip()
    nome = re.sub(r'\s+', ' ', nome)
    return nome


PRIORITY_LAYER_NAMES_NORM = [_normalizar_nome(n) for n in PRIORITY_LAYER_NAMES]


# ─────────────────────────────────────────────────────────────────────────────
#  Diálogo principal
# ─────────────────────────────────────────────────────────────────────────────
class BackupDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup de Camadas QGIS")
        self.setMinimumSize(530, 600)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
        )
        self.setStyleSheet(STYLE)

        data_hoje = datetime.now().strftime("%d-%m-%Y")
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.pasta_destino = os.path.join(desktop, f"BACKUP_QGIS_({data_hoje})")
        self.ultimo_log_path = None

        self._build_ui()
        self._populate_layers()

    # ── Construção da interface ───────────────────────────────────────────────
    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(22, 18, 22, 18)

        # Título
        lbl_titulo = QLabel("Backup de Camadas QGIS")
        lbl_titulo.setObjectName("lblTitulo")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_titulo)

        lbl_sub = QLabel("Selecione as camadas que deseja salvar no backup")
        lbl_sub.setObjectName("lblSub")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl_sub)

        # Separador
        sep = QFrame()
        sep.setObjectName("separador")
        sep.setFrameShape(QFrame.HLine)
        lay.addWidget(sep)

        # Barra de seleção rápida
        row_sel = QHBoxLayout()
        row_sel.setSpacing(6)

        btn_tudo = QPushButton("Selecionar Tudo")
        btn_tudo.setObjectName("btnMini")
        btn_tudo.setCursor(Qt.PointingHandCursor)
        btn_tudo.clicked.connect(self._select_all)
        row_sel.addWidget(btn_tudo)

        btn_nada = QPushButton("Desmarcar Tudo")
        btn_nada.setObjectName("btnMini")
        btn_nada.setCursor(Qt.PointingHandCursor)
        btn_nada.clicked.connect(self._deselect_all)
        row_sel.addWidget(btn_nada)

        row_sel.addStretch()

        self.lbl_contagem = QLabel("0/0 selecionadas")
        self.lbl_contagem.setObjectName("lblSub")
        row_sel.addWidget(self.lbl_contagem)

        lay.addLayout(row_sel)

        # Lista de camadas
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(250)
        self.list_widget.itemChanged.connect(self._atualizar_contagem)
        lay.addWidget(self.list_widget)

        # Card com caminho destino
        card = QFrame()
        card.setObjectName("cardDestino")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(14, 10, 14, 10)
        card_lay.setSpacing(3)

        lbl_dest_head = QLabel("📁  Pasta de destino:")
        lbl_dest_head.setObjectName("lblSub")
        card_lay.addWidget(lbl_dest_head)

        lbl_dest = QLabel(self.pasta_destino)
        lbl_dest.setObjectName("lblDestino")
        lbl_dest.setWordWrap(True)
        card_lay.addWidget(lbl_dest)

        lay.addWidget(card)

        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        lay.addWidget(self.progress)

        # Status
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("lblStatus")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setVisible(False)
        lay.addWidget(self.lbl_status)

        # Botões de ação
        row_btn = QHBoxLayout()
        row_btn.setSpacing(10)

        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.setObjectName("btnFechar")
        self.btn_fechar.setCursor(Qt.PointingHandCursor)
        self.btn_fechar.clicked.connect(self.reject)
        row_btn.addWidget(self.btn_fechar)

        self.btn_abrir_log = QPushButton("Abrir Log")
        self.btn_abrir_log.setObjectName("btnMini")
        self.btn_abrir_log.setCursor(Qt.PointingHandCursor)
        self.btn_abrir_log.setEnabled(False)
        self.btn_abrir_log.clicked.connect(self._abrir_log)
        row_btn.addWidget(self.btn_abrir_log)

        row_btn.addStretch()

        self.btn_salvar = QPushButton("💾  Salvar Backup")
        self.btn_salvar.setObjectName("btnSalvar")
        self.btn_salvar.setCursor(Qt.PointingHandCursor)
        self.btn_salvar.clicked.connect(self._executar_backup)
        row_btn.addWidget(self.btn_salvar)

        lay.addLayout(row_btn)

    # ── Preenchimento da lista ────────────────────────────────────────────────
    def _populate_layers(self):
        project = QgsProject.instance()
        layers = list(project.mapLayers().values())

        def sort_key(layer):
            nome_norm = _normalizar_nome(layer.name())
            if nome_norm in PRIORITY_LAYER_NAMES_NORM:
                return (0, PRIORITY_LAYER_NAMES_NORM.index(nome_norm), layer.name().lower())
            return (1, 999, layer.name().lower())

        layers.sort(key=sort_key)

        for layer in layers:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, layer.id())

            if isinstance(layer, QgsVectorLayer):
                icon = _GEOM_ICON.get(layer.geometryType(), "◈")
                tipo = "Vetor"
            elif isinstance(layer, QgsRasterLayer):
                icon = "🖼"
                tipo = "Raster"
            else:
                icon = "◈"
                tipo = "Outro"

            item.setText(f"  {icon}   {layer.name()}   —   {tipo}")
            if _normalizar_nome(layer.name()) in PRIORITY_LAYER_NAMES_NORM:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        self._atualizar_contagem()

    def _atualizar_contagem(self):
        checked = sum(
            1 for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        )
        total = self.list_widget.count()
        self.lbl_contagem.setText(f"{checked}/{total} selecionadas")

    def _select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Checked)

    def _deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Unchecked)

    def _ids_selecionados(self):
        return [
            self.list_widget.item(i).data(Qt.UserRole)
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]

    # ── Execução do backup ────────────────────────────────────────────────────
    def _set_status(self, msg, cor="#dde1f0"):
        self.lbl_status.setText(msg)
        self.lbl_status.setStyleSheet(
            f"color: {cor}; font-size: 12px; padding: 5px 8px; border-radius: 6px;"
        )
        self.lbl_status.setVisible(True)
        QApplication.processEvents()

    def _reabilitar(self):
        self.btn_salvar.setEnabled(True)
        self.btn_fechar.setEnabled(True)

    def _abrir_log(self):
        if not self.ultimo_log_path or not os.path.exists(self.ultimo_log_path):
            self._set_status("⚠️  Log ainda não disponível.", "#f7c56e")
            return
        try:
            os.startfile(self.ultimo_log_path)
        except Exception as e:
            self._set_status(f"❌  Não foi possível abrir o log: {e}", "#f07070")

    def _nome_arquivo_limpo(self, nome):
        nome_limpo = re.sub(r'[^\w\-.]+', '_', nome.strip(), flags=re.UNICODE)
        nome_limpo = re.sub(r'_+', '_', nome_limpo).strip('._')
        return nome_limpo or 'camada'

    def _nome_tabela_limpo(self, nome):
        base = self._nome_arquivo_limpo(nome).lower()
        if not base or not base[0].isalpha():
            base = f"layer_{base}"
        return base[:55]

    def _copiar_raster_completo(self, fonte, nome_base):
        """Copia raster e arquivos auxiliares (tfw, prj, ovr, aux.xml etc.)."""
        pasta_fonte = os.path.dirname(fonte)
        raiz_fonte = os.path.splitext(os.path.basename(fonte))[0]
        ext_fonte = os.path.splitext(fonte)[1]

        destino_principal = os.path.join(self.pasta_destino, f"{nome_base}{ext_fonte}")
        shutil.copy2(fonte, destino_principal)

        padrao = os.path.join(pasta_fonte, f"{raiz_fonte}.*")
        for arq in glob.glob(padrao):
            if os.path.abspath(arq) == os.path.abspath(fonte):
                continue
            ext_aux = os.path.splitext(arq)[1]
            if not ext_aux:
                continue
            destino_aux = os.path.join(self.pasta_destino, f"{nome_base}{ext_aux}")
            try:
                shutil.copy2(arq, destino_aux)
            except Exception:
                pass

        return destino_principal

    def _salvar_vetor_gpkg(self, layer, gpkg_path, tabela):
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "GPKG"
        opts.layerName = tabela
        opts.fileEncoding = "UTF-8"

        # Compatibilidade entre versões do QGIS para sobrescrever camadas no GPKG.
        if os.path.exists(gpkg_path):
            if hasattr(QgsVectorFileWriter, 'CreateOrOverwriteLayer'):
                opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
            elif hasattr(QgsVectorFileWriter, 'CreateOrOverwriteFile'):
                opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile
        else:
            if hasattr(QgsVectorFileWriter, 'CreateOrOverwriteFile'):
                opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

        res = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            gpkg_path,
            QgsProject.instance().transformContext(),
            opts,
        )
        return res

    def _salvar_vetor_shp(self, layer, shp_path):
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "ESRI Shapefile"
        opts.fileEncoding = "UTF-8"
        if hasattr(QgsVectorFileWriter, 'CreateOrOverwriteFile'):
            opts.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

        res = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            shp_path,
            QgsProject.instance().transformContext(),
            opts,
        )
        return res

    def _escrever_log_backup(self, linhas):
        log_path = os.path.join(self.pasta_destino, "LOG_BACKUP_QGIS.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(linhas))
        return log_path

    def _executar_backup(self):
        ids = self._ids_selecionados()
        if not ids:
            self._set_status("⚠️  Nenhuma camada selecionada.", "#f7c56e")
            return

        self.btn_salvar.setEnabled(False)
        self.btn_fechar.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(ids))
        self.progress.setValue(0)
        self._set_status("Preparando backup…", "#79b8ff")

        # Criar pasta destino
        try:
            os.makedirs(self.pasta_destino, exist_ok=True)
        except Exception as e:
            self._set_status(f"❌  Erro ao criar pasta: {e}", "#f07070")
            self._reabilitar()
            return

        project = QgsProject.instance()
        camadas_salvas = []   # lista de dicts para montar o QGZ mantendo estilo/ordem
        avisos = []
        erros = []
        log_linhas = []

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        gpkg_path = os.path.join(self.pasta_destino, "BACKUP_COMPLETO.gpkg")
        log_linhas.append("=" * 70)
        log_linhas.append("BACKUP QGIS - LOG DETALHADO")
        log_linhas.append("=" * 70)
        log_linhas.append(f"Data/Hora: {data_hora}")
        log_linhas.append(f"Destino: {self.pasta_destino}")
        log_linhas.append(f"Arquivo completo (vetor): {gpkg_path}")
        log_linhas.append("")

        for idx, layer_id in enumerate(ids, start=1):
            layer = project.mapLayer(layer_id)
            if not layer:
                erros.append(f"[ID {layer_id}] camada não encontrada")
                self.progress.setValue(idx)
                continue

            self._set_status(f"Salvando:  {layer.name()} …", "#79b8ff")

            nome_arq = self._nome_arquivo_limpo(layer.name())
            nome_tabela = self._nome_tabela_limpo(layer.name())

            log_linhas.append(f"[Camada] {layer.name()}")

            if isinstance(layer, QgsVectorLayer):
                # 1) Salvamento principal sem perda de informação: GPKG
                res_gpkg = self._salvar_vetor_gpkg(layer, gpkg_path, nome_tabela)

                if res_gpkg[0] != QgsVectorFileWriter.NoError:
                    msg = f"{layer.name()}: falha ao salvar completo no GPKG ({res_gpkg[1]})"
                    erros.append(msg)
                    log_linhas.append(f"  - ERRO GPKG: {res_gpkg[1]}")
                    log_linhas.append("")
                    self.progress.setValue(idx)
                    QApplication.processEvents()
                    continue

                caminho_gpkg_layer = f"{gpkg_path}|layername={nome_tabela}"
                camadas_salvas.append({
                    "nome": layer.name(),
                    "caminho": caminho_gpkg_layer,
                    "tipo": "vetor",
                    "orig_layer_id": layer.id(),
                })
                log_linhas.append(f"  - OK GPKG: {nome_tabela}")

                # 2) SHP é exportado como compatibilidade. Se falhar, não perde dados.
                caminho_shp = os.path.join(self.pasta_destino, f"{nome_arq}.shp")
                res_shp = self._salvar_vetor_shp(layer, caminho_shp)
                if res_shp[0] == QgsVectorFileWriter.NoError:
                    log_linhas.append(f"  - OK SHP: {os.path.basename(caminho_shp)}")
                else:
                    aviso = (
                        f"{layer.name()}: SHP falhou ({res_shp[1]}). "
                        f"Camada preservada no GPKG."
                    )
                    avisos.append(aviso)
                    log_linhas.append(f"  - AVISO SHP: {res_shp[1]}")

            elif isinstance(layer, QgsRasterLayer):
                fonte = layer.source()
                if "|" in fonte:
                    fonte = fonte.split("|")[0]
                if os.path.isfile(fonte):
                    try:
                        caminho = self._copiar_raster_completo(fonte, nome_arq)
                        camadas_salvas.append({
                            "nome": layer.name(),
                            "caminho": caminho,
                            "tipo": "raster",
                            "orig_layer_id": layer.id(),
                            "provider": "gdal",
                        })
                        log_linhas.append(f"  - OK Raster: {os.path.basename(caminho)}")
                    except Exception as e:
                        msg = f"{layer.name()}: falha ao copiar raster ({e})"
                        erros.append(msg)
                        log_linhas.append(f"  - ERRO Raster: {e}")
                else:
                    # Raster remoto (XYZ/WMS etc.): mantém fonte original no QGZ.
                    camadas_salvas.append({
                        "nome": layer.name(),
                        "caminho": layer.source(),
                        "tipo": "raster_remoto",
                        "orig_layer_id": layer.id(),
                        "provider": layer.providerType() or "wms",
                    })
                    avisos.append(
                        f"{layer.name()}: camada remota mantida por referência (não copiada para disco)."
                    )
                    log_linhas.append("  - AVISO Raster remoto: fonte mantida por referência")

            else:
                avisos.append(f"{layer.name()}: tipo não suportado, camada ignorada")
                log_linhas.append("  - AVISO: tipo de camada não suportado")

            log_linhas.append("")

            self.progress.setValue(idx)
            QApplication.processEvents()

        # Gerar arquivo QGZ
        qgz_ok = False
        qgz_msg = "não gerado"
        if camadas_salvas:
            self._set_status("Gerando projeto QGZ…", "#79b8ff")
            QApplication.processEvents()
            qgz_ok, qgz_msg = self._gerar_qgz(camadas_salvas)
            if not qgz_ok:
                erros.append(f"Falha ao gerar QGZ: {qgz_msg}")

        # Resultado final
        n_ok = len(camadas_salvas)
        n_warn = len(avisos)
        n_err = len(erros)

        log_linhas.append("=" * 70)
        log_linhas.append("RESUMO")
        log_linhas.append(f"Salvas: {n_ok}")
        log_linhas.append(f"Avisos: {n_warn}")
        log_linhas.append(f"Erros: {n_err}")
        if camadas_salvas:
            log_linhas.append(f"QGZ: {'OK' if qgz_ok else f'ERRO ({qgz_msg})'}")
        else:
            log_linhas.append("QGZ: não gerado (nenhuma camada salva)")
        if avisos:
            log_linhas.append("")
            log_linhas.append("AVISOS:")
            for w in avisos:
                log_linhas.append(f"- {w}")
        if erros:
            log_linhas.append("")
            log_linhas.append("ERROS:")
            for e in erros:
                log_linhas.append(f"- {e}")

        log_path = self._escrever_log_backup(log_linhas)
        self.ultimo_log_path = log_path
        self.btn_abrir_log.setEnabled(True)

        if n_err == 0 and n_warn == 0:
            self._set_status(
                f"✅  {n_ok} camada(s) salva(s) com sucesso!",
                "#7de099",
            )
        elif n_err == 0:
            self._set_status(
                f"✅  {n_ok} salva(s) / {n_warn} aviso(s). Sem perda no GPKG.",
                "#7de099",
            )
        else:
            self._set_status(
                f"⚠️  {n_ok} salva(s) / {n_warn} aviso(s) / {n_err} erro(s).",
                "#f7c56e",
            )

        self._reabilitar()

        # Janela com detalhes para não ficar sem explicação do erro.
        msg = QMessageBox(self)
        msg.setWindowTitle("Resultado do Backup")
        msg.setIcon(QMessageBox.Information if n_err == 0 else QMessageBox.Warning)
        msg.setStyleSheet("QLabel{color:#ffffff;} QMessageBox{background:#12131f;}")
        msg.setText(
            f"Salvas: {n_ok}\nAvisos: {n_warn}\nErros: {n_err}\n\n"
            f"Log detalhado:\n{log_path}"
        )

        detalhes = []
        if avisos:
            detalhes.append("AVISOS:")
            detalhes.extend(f"- {w}" for w in avisos)
            detalhes.append("")
        if erros:
            detalhes.append("ERROS:")
            detalhes.extend(f"- {e}" for e in erros)
        if not detalhes:
            detalhes = ["Backup concluído sem avisos e sem erros."]

        msg.setDetailedText("\n".join(detalhes))
        msg.exec_()

        # Abrir pasta no Explorer
        try:
            os.startfile(self.pasta_destino)
        except Exception:
            pass

    # ── Geração do projeto QGZ ────────────────────────────────────────────────
    def _gerar_qgz(self, camadas_salvas):
        """Clona o projeto atual para preservar propriedades e troca fontes das camadas salvas."""
        data_hoje = datetime.now().strftime("%d-%m-%Y")
        qgz_path = os.path.join(
            self.pasta_destino,
            f"BACKUP_QGIS_({data_hoje}).qgz",
        )
        template_path = os.path.join(self.pasta_destino, "_template_projeto_original.qgz")

        try:
            projeto_atual = QgsProject.instance()
            if not projeto_atual.write(template_path):
                return False, "não foi possível criar cópia base do projeto atual"

            novo_projeto = QgsProject()
            if not novo_projeto.read(template_path):
                return False, "não foi possível abrir cópia base do projeto"

            adicionadas = 0
            falhas = []
            selected_ids = [item.get("orig_layer_id") for item in camadas_salvas if item.get("orig_layer_id")]
            selected_set = set(selected_ids)

            # Remove do projeto clonado tudo que não foi selecionado.
            for layer_id in list(novo_projeto.mapLayers().keys()):
                if layer_id not in selected_set:
                    novo_projeto.removeMapLayer(layer_id)

            for item in camadas_salvas:
                nome = item["nome"]
                caminho = item["caminho"]
                tipo = item.get("tipo", "vetor")
                orig_layer_id = item.get("orig_layer_id")
                layer_existente = novo_projeto.mapLayer(orig_layer_id) if orig_layer_id else None
                if not layer_existente:
                    falhas.append(f"{nome} -> camada não encontrada no projeto clonado")
                    continue

                provider = item.get("provider", layer_existente.providerType())
                if tipo == "vetor":
                    provider = "ogr"
                elif tipo == "raster":
                    provider = "gdal"

                layer_existente.setName(nome)
                layer_existente.setDataSource(caminho, nome, provider)

                if not layer_existente.isValid():
                    falhas.append(f"{nome} -> fonte inválida após setDataSource")
                    continue

                adicionadas += 1

            # Reordena no painel exatamente na ordem selecionada.
            root = novo_projeto.layerTreeRoot()
            for idx, layer_id in enumerate(selected_ids):
                node = root.findLayer(layer_id)
                if node:
                    parent = node.parent() or root
                    clone = node.clone()
                    parent.removeChildNode(node)
                    root.insertChildNode(idx, clone)

            if adicionadas == 0:
                return False, "nenhuma camada válida para incluir no projeto"

            ok = novo_projeto.write(qgz_path)
            del novo_projeto

            if not ok:
                return False, "QGIS não conseguiu gravar o arquivo .qgz"

            if not os.path.exists(qgz_path):
                return False, "arquivo .qgz não foi criado em disco"

            if falhas:
                return True, f"gerado com {len(falhas)} camada(s) ignorada(s)"

            return True, "ok"
        except Exception as e:
            return False, str(e)
        finally:
            try:
                if os.path.exists(template_path):
                    os.remove(template_path)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
#  Ponto de entrada
# ─────────────────────────────────────────────────────────────────────────────
dialog = BackupDialog(iface.mainWindow())
dialog.exec_()
