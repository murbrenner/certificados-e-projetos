#NOME: Corrigir Topologia Rotas Leitura

#DESCRIÇÃO: Executa a rotina 'Corrigir Topologia Rotas Leitura', corrigindo topologia e geometrias com base nas validacoes do script. Camadas envolvidas: 'ROTAS DE LEITURA'.

#PRÉ-REQUISITO: Carregar a camada 'ROTAS DE LEITURA' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qgis.utils import iface


NOME_CAMADA = "ROTAS DE LEITURA"
TOLERANCIA_AREA = 1e-9


def obter_camada_poligono(nome_camada: str):
    camadas = QgsProject.instance().mapLayersByName(nome_camada)
    if not camadas:
        raise RuntimeError(f"Camada '{nome_camada}' não encontrada no projeto.")

    camada = camadas[0]
    if camada.geometryType() != QgsWkbTypes.PolygonGeometry:
        raise RuntimeError(f"A camada '{nome_camada}' não é do tipo polígono.")

    return camada


def normalizar_poligono(geometria: QgsGeometry):
    if geometria is None or geometria.isEmpty():
        return None

    geom = QgsGeometry(geometria)
    if not geom.isGeosValid():
        geom = geom.makeValid()

    if geom is None or geom.isEmpty():
        return None

    if QgsWkbTypes.geometryType(geom.wkbType()) != QgsWkbTypes.PolygonGeometry:
        geom = geom.convertToType(QgsWkbTypes.PolygonGeometry, True)

    if geom is None or geom.isEmpty():
        return None

    if not geom.isGeosValid():
        geom = geom.makeValid()

    if geom is None or geom.isEmpty():
        return None

    if QgsWkbTypes.geometryType(geom.wkbType()) != QgsWkbTypes.PolygonGeometry:
        return None

    return geom


def carregar_geometrias(camada, ids=None):
    geometrias = {}
    if ids is None:
        iterator = camada.selectedFeatures()
    else:
        requisicao = QgsFeatureRequest().setFilterFids(list(ids))
        iterator = camada.getFeatures(requisicao)

    for feicao in iterator:
        geom = normalizar_poligono(feicao.geometry())
        if geom is not None:
            geometrias[feicao.id()] = geom
    return geometrias


def criar_indice(geometrias: dict):
    indice = QgsSpatialIndex()
    for fid, geom in geometrias.items():
        feat = QgsFeature()
        feat.setId(fid)
        feat.setGeometry(geom)
        indice.addFeature(feat)
    return indice


def detectar_sobreposicoes(geometrias: dict, indice: QgsSpatialIndex, tolerancia_area: float):
    sobreposicoes = []
    ids = sorted(geometrias.keys())

    for fid_a in ids:
        geom_a = geometrias.get(fid_a)
        if geom_a is None or geom_a.isEmpty():
            continue

        candidatos = indice.intersects(geom_a.boundingBox())
        for fid_b in candidatos:
            if fid_b <= fid_a:
                continue

            geom_b = geometrias.get(fid_b)
            if geom_b is None or geom_b.isEmpty():
                continue

            if not geom_a.intersects(geom_b):
                continue

            inter = geom_a.intersection(geom_b)
            if inter.isEmpty():
                continue

            area_inter = inter.area()
            if area_inter > tolerancia_area:
                sobreposicoes.append((fid_a, fid_b, area_inter))

    return sobreposicoes


def corrigir_sobreposicoes(geometrias: dict, indice: QgsSpatialIndex, tolerancia_area: float):
    ids_alterados = set()
    ids_removidos = set()
    total_corrigidas = 0

    ids = sorted(geometrias.keys())

    for fid_a in ids:
        geom_a = geometrias.get(fid_a)
        if geom_a is None or geom_a.isEmpty():
            continue

        candidatos = indice.intersects(geom_a.boundingBox())
        for fid_b in candidatos:
            if fid_b <= fid_a:
                continue

            geom_b = geometrias.get(fid_b)
            if geom_b is None or geom_b.isEmpty():
                continue

            if not geom_a.intersects(geom_b):
                continue

            inter = geom_a.intersection(geom_b)
            if inter.isEmpty() or inter.area() <= tolerancia_area:
                continue

            geom_corrigida_b = normalizar_poligono(geom_b.difference(geom_a))

            if geom_corrigida_b is None or geom_corrigida_b.isEmpty():
                geometrias[fid_b] = None
                ids_removidos.add(fid_b)
            else:
                geometrias[fid_b] = geom_corrigida_b
                ids_alterados.add(fid_b)

            total_corrigidas += 1

    return total_corrigidas, ids_alterados, ids_removidos


def aplicar_alteracoes_na_camada(camada, geometrias: dict, ids_alterados: set, ids_removidos: set):
    if not camada.isEditable() and not camada.startEditing():
        raise RuntimeError("Não foi possível iniciar edição na camada.")

    for fid in ids_alterados:
        geom = geometrias.get(fid)
        if geom is None:
            continue
        if not camada.changeGeometry(fid, geom):
            raise RuntimeError(f"Falha ao atualizar geometria do fid {fid}.")

    for fid in ids_removidos:
        if not camada.deleteFeature(fid):
            raise RuntimeError(f"Falha ao remover feição do fid {fid}.")

    camada.triggerRepaint()


class JanelaCorrecaoTopologia(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ultimo_resultado = None
        self._montar_ui()

    def _montar_ui(self):
        self.setWindowTitle("Topologia - Rotas")
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFixedSize(330, 150)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #1f2937;
                color: #e5e7eb;
                font-size: 11px;
            }
            QFrame#card {
                border: 1px solid #374151;
                border-radius: 10px;
                background-color: #111827;
            }
            QPushButton {
                border: 1px solid #4b5563;
                border-radius: 8px;
                padding: 6px 10px;
                background-color: #374151;
                color: #f9fafb;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:pressed {
                background-color: #6b7280;
            }
            QLabel#status {
                color: #d1d5db;
            }
            """
        )

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(8, 8, 8, 8)

        card = QFrame()
        card.setObjectName("card")
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(10, 10, 10, 10)
        layout_card.setSpacing(8)

        titulo = QLabel("ROTAS DE LEITURA (seleção)")
        titulo.setStyleSheet("font-weight: 700;")

        self.lbl_status = QLabel("Selecione os polígonos e clique em Identificar.")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setWordWrap(True)

        botoes = QHBoxLayout()
        botoes.setSpacing(8)
        self.btn_identificar = QPushButton("Identificar")
        self.btn_corrigir = QPushButton("Corrigir")
        self.btn_corrigir.setEnabled(False)

        self.btn_identificar.clicked.connect(self.identificar)
        self.btn_corrigir.clicked.connect(self.corrigir)

        botoes.addWidget(self.btn_identificar)
        botoes.addWidget(self.btn_corrigir)

        layout_card.addWidget(titulo)
        layout_card.addLayout(botoes)
        layout_card.addWidget(self.lbl_status)
        layout_principal.addWidget(card)

    def _coletar_contexto(self):
        camada = obter_camada_poligono(NOME_CAMADA)
        ids_selecionados = camada.selectedFeatureIds()

        if not ids_selecionados:
            raise RuntimeError("Nenhuma feição selecionada na camada 'ROTAS DE LEITURA'.")

        geometrias = carregar_geometrias(camada, ids_selecionados)
        if not geometrias:
            raise RuntimeError("Nenhuma geometria válida encontrada na seleção.")

        return camada, ids_selecionados, geometrias

    def identificar(self):
        try:
            camada, ids_selecionados, geometrias = self._coletar_contexto()
            indice = criar_indice(geometrias)
            sobreposicoes = detectar_sobreposicoes(geometrias, indice, TOLERANCIA_AREA)

            self._ultimo_resultado = {
                "ids": list(ids_selecionados),
                "total_validas": len(geometrias),
                "sobreposicoes": sobreposicoes,
                "camada": camada,
            }

            if sobreposicoes:
                self.btn_corrigir.setEnabled(True)
                self.lbl_status.setText(
                    f"Encontradas {len(sobreposicoes)} sobreposições em {len(geometrias)} feições válidas."
                )
            else:
                self.btn_corrigir.setEnabled(False)
                self.lbl_status.setText("Sem sobreposições na seleção atual.")

            print(f"Feições selecionadas válidas: {len(geometrias)}")
            print(f"Sobreposições encontradas na seleção (antes): {len(sobreposicoes)}")

        except Exception as erro:
            self.btn_corrigir.setEnabled(False)
            self.lbl_status.setText(str(erro))
            print(f"Erro ao identificar: {erro}")

    def corrigir(self):
        try:
            if not self._ultimo_resultado:
                self.identificar()
                if not self._ultimo_resultado or not self._ultimo_resultado["sobreposicoes"]:
                    return

            camada = self._ultimo_resultado["camada"]
            ids_base = self._ultimo_resultado["ids"]

            geometrias = carregar_geometrias(camada, ids_base)
            indice = criar_indice(geometrias)

            total_corrigidas, ids_alterados, ids_removidos = corrigir_sobreposicoes(
                geometrias, indice, TOLERANCIA_AREA
            )
            aplicar_alteracoes_na_camada(camada, geometrias, ids_alterados, ids_removidos)

            geometrias_finais = carregar_geometrias(camada, ids_base)
            indice_final = criar_indice(geometrias_finais)
            sobreposicoes_depois = detectar_sobreposicoes(
                geometrias_finais, indice_final, TOLERANCIA_AREA
            )

            self.btn_corrigir.setEnabled(False)
            self.lbl_status.setText(
                f"Correção aplicada. Restantes: {len(sobreposicoes_depois)}. (sem commit)"
            )

            print(f"Correções aplicadas: {total_corrigidas}")
            print(f"Feições ajustadas: {len(ids_alterados)}")
            print(f"Feições removidas por sobreposição total: {len(ids_removidos)}")
            print(f"Sobreposições restantes na seleção (depois): {len(sobreposicoes_depois)}")
            print("Alterações aplicadas em modo de edição (sem commit automático).")
            print("Revise no QGIS e salve manualmente quando aprovar.")

        except Exception as erro:
            self.lbl_status.setText(str(erro))
            print(f"Erro ao corrigir: {erro}")


def abrir_janela():
    global JANELA_CORRECAO_TOPOLOGIA
    try:
        if JANELA_CORRECAO_TOPOLOGIA is not None:
            JANELA_CORRECAO_TOPOLOGIA.close()
    except NameError:
        pass

    parent = iface.mainWindow() if iface else None
    JANELA_CORRECAO_TOPOLOGIA = JanelaCorrecaoTopologia(parent)
    JANELA_CORRECAO_TOPOLOGIA.show()
    JANELA_CORRECAO_TOPOLOGIA.raise_()
    JANELA_CORRECAO_TOPOLOGIA.activateWindow()


abrir_janela()
