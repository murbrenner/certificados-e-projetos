#NOME: Alinhar Pontos nas Quadras da Rota

#DESCRIÇÃO: Executa em sequência: (1) Buffer Alinhamento — seleciona quadras a partir da(s) rota(s) pré-selecionada(s) em 'ROTAS DE LEITURA' e gera a camada 'BUFFER_ALINHAMENTO'; (2) Alinhar Pontos — alinha pontos selecionados da camada informada pelo operador às bordas do buffer gerado.

#PRÉ-REQUISITO: Carregar as camadas 'ROTAS DE LEITURA' e 'QUADRAS' no projeto QGIS; selecionar ao menos uma rota em 'ROTAS DE LEITURA'; selecionar previamente os pontos que serão processados na camada de pontos.


import processing
from qgis.core import (
    QgsProject,
    QgsProcessingFeatureSourceDefinition,
    QgsFeatureRequest,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsPointXY,
    QgsDistanceArea,
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
)
from qgis.PyQt.QtGui import QColor, QFont


def _choose_point_layer_modern():
    point_layers = []
    for lyr in QgsProject.instance().mapLayers().values():
        if isinstance(lyr, QgsVectorLayer) and lyr.geometryType() == QgsWkbTypes.PointGeometry:
            point_layers.append(lyr)

    point_layers = sorted(point_layers, key=lambda l: l.name().lower())
    if not point_layers:
        return None

    dlg = QDialog()
    dlg.setWindowTitle("Selecionar Camada de Pontos")
    dlg.setFixedWidth(460)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)

    title = QLabel("Escolha a camada de pontos")
    title_font = QFont("Segoe UI", 11)
    title_font.setBold(True)
    title.setFont(title_font)
    layout.addWidget(title)

    subtitle = QLabel("Apenas camadas de ponto disponíveis no projeto.")
    subtitle.setStyleSheet("color: #7a8aaa; font-size: 10px;")
    layout.addWidget(subtitle)

    combo = QComboBox()
    combo.setFixedHeight(36)
    combo.setFont(QFont("Segoe UI", 10))
    for lyr in point_layers:
        combo.addItem(lyr.name(), lyr.name())
    layout.addWidget(combo)

    buttons = QHBoxLayout()
    buttons.addStretch()

    btn_cancel = QPushButton("Cancelar")
    btn_cancel.setFixedHeight(34)
    btn_cancel.setMinimumWidth(120)
    btn_cancel.clicked.connect(dlg.reject)

    btn_ok = QPushButton("Prosseguir")
    btn_ok.setFixedHeight(34)
    btn_ok.setMinimumWidth(120)
    btn_ok.clicked.connect(dlg.accept)

    buttons.addWidget(btn_cancel)
    buttons.addWidget(btn_ok)
    layout.addLayout(buttons)

    dlg.setStyleSheet("""
QDialog {
    background: #f4f7fb;
    color: #1a2440;
    font-family: "Segoe UI", "Arial", sans-serif;
}
QLabel { color: #1a2440; }
QComboBox {
    background: #ffffff;
    border: 1.5px solid #d0daf0;
    border-radius: 8px;
    padding: 0 10px;
    color: #1a2440;
    font-size: 10px;
}
QComboBox:focus { border-color: #0b57d0; }
QPushButton {
    background: #eef2fb;
    color: #2a4080;
    border: 1px solid #d0daf0;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 10px;
    font-weight: 600;
}
QPushButton:hover { background: #dde6f8; }
""")

    if dlg.exec() != QDialog.Accepted:
        return ""

    return combo.currentData()


# ─── PARTE 1: Buffer Alinhamento ──────────────────────────────────────────────

quadras_layers = QgsProject.instance().mapLayersByName('QUADRAS')
rotas_layers = QgsProject.instance().mapLayersByName('ROTAS DE LEITURA')

if not quadras_layers:
    print("Camada 'QUADRAS' não encontrada no projeto.")
elif not rotas_layers:
    print("Camada 'ROTAS DE LEITURA' não encontrada no projeto.")
else:
    quadras = quadras_layers[0]
    rotas = rotas_layers[0]

    if rotas.selectedFeatureCount() == 0:
        print("Nenhuma rota selecionada em 'ROTAS DE LEITURA'. Selecione ao menos uma rota antes de executar.")
    else:
        print("Montando geometria da(s) rota(s) selecionada(s)...")

        geoms_rota = []
        transform = None
        if rotas.crs() != quadras.crs():
            transform = QgsCoordinateTransform(
                rotas.crs(),
                quadras.crs(),
                QgsProject.instance()
            )

        for feat in rotas.selectedFeatures():
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            geom_rota = QgsGeometry(geom)
            if transform is not None:
                try:
                    geom_rota.transform(transform)
                except Exception as e:
                    print(f"Aviso: não foi possível transformar uma rota para o CRS de QUADRAS ({e}).")
                    continue

            geoms_rota.append(geom_rota)

        if not geoms_rota:
            print("Nenhuma geometria válida encontrada nas rotas selecionadas.")
        else:
            mascara_rota = QgsGeometry.unaryUnion(geoms_rota)
            if not mascara_rota or mascara_rota.isEmpty():
                print("Falha ao criar máscara espacial a partir das rotas selecionadas.")
            else:
                print("Selecionando quadras dentro/intersectando a(s) rota(s) selecionada(s)...")

                ids_quadras = []
                request = QgsFeatureRequest().setFilterRect(mascara_rota.boundingBox())
                for feat in quadras.getFeatures(request):
                    geom_q = feat.geometry()
                    if geom_q and not geom_q.isEmpty() and geom_q.intersects(mascara_rota):
                        ids_quadras.append(feat.id())

                quadras.selectByIds(ids_quadras)

                if not ids_quadras:
                    print("Nenhuma quadra encontrada dentro/intersectando as rotas selecionadas.")
                else:
                    print(f"{len(ids_quadras)} quadra(s) selecionada(s).")
                    print('Executando buffer nas quadras selecionadas pela rota...')

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

                    buffer_layer = buffer_result['OUTPUT']

                    print('Corrigindo geometrias (fixgeometries)...')
                    fix_result = processing.run('qgis:fixgeometries', {
                        'INPUT': buffer_layer,
                        'OUTPUT': 'memory:BUFFER_ALINHAMENTO'
                    })

                    final_layer = fix_result['OUTPUT']
                    QgsProject.instance().addMapLayer(final_layer)

                    print(f"Concluído parte 1: camada 'BUFFER_ALINHAMENTO' adicionada com {final_layer.featureCount()} feições.")


                    # ─── PARTE 2: Alinhar Pontos no Buffer Alinhamento ────────────────────────

                    crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

                    camPontos = _choose_point_layer_modern()

                    if not camPontos:
                        print("Operação cancelada pelo usuário.")
                    else:
                        layers_pontos = QgsProject.instance().mapLayersByName(camPontos)
                        if not layers_pontos:
                            print(f"Camada '{camPontos}' não encontrada.")
                        else:
                            pontos_layer = layers_pontos[0]
                            poligonos_layer = final_layer  # BUFFER_ALINHAMENTO criado na parte 1

                            # Criar nova camada para pontos ajustados
                            nova_layer = QgsVectorLayer("Point?crs=EPSG:4326", "PONTOS_ALINHADOS", "memory")
                            nova_layer_provider = nova_layer.dataProvider()
                            nova_layer_provider.addAttributes(pontos_layer.fields())
                            nova_layer.updateFields()

                            # Configurar calculadora de distância
                            distance_area = QgsDistanceArea()
                            distance_area.setEllipsoid('WGS84')
                            distancia_minima_m = 1.0
                            pontos_aceitos = []

                            # Filtrar pontos usando as quadras selecionadas como máscara (polígonos, não linha da rota)
                            geoms_quadras_mask = []
                            transform_quadras_para_pontos = None
                            if quadras.crs() != pontos_layer.crs():
                                transform_quadras_para_pontos = QgsCoordinateTransform(
                                    quadras.crs(),
                                    pontos_layer.crs(),
                                    QgsProject.instance()
                                )

                            for feat_quadra in quadras.selectedFeatures():
                                geom_q = feat_quadra.geometry()
                                if not geom_q or geom_q.isEmpty():
                                    continue
                                geom_q2 = QgsGeometry(geom_q)
                                if transform_quadras_para_pontos is not None:
                                    try:
                                        geom_q2.transform(transform_quadras_para_pontos)
                                    except Exception as e:
                                        print(f"Aviso: falha ao transformar quadra para CRS da camada de pontos ({e}).")
                                        continue
                                geoms_quadras_mask.append(geom_q2)

                            if not geoms_quadras_mask:
                                print("Nenhuma quadra válida para usar como máscara de pontos.")
                            else:
                                mascara_quadras = QgsGeometry.unaryUnion(geoms_quadras_mask)
                                req_pts = QgsFeatureRequest().setFilterRect(mascara_quadras.boundingBox())
                                pontos_filtrados_rota = []
                                for fpt in pontos_layer.getFeatures(req_pts):
                                    gpt = fpt.geometry()
                                    if gpt and not gpt.isEmpty() and gpt.intersects(mascara_quadras):
                                        pontos_filtrados_rota.append(fpt)

                                if not pontos_filtrados_rota:
                                    print(f"Nenhum ponto da camada '{camPontos}' foi encontrado na rota selecionada.")
                                else:
                                    print(f"Pontos da camada '{camPontos}' dentro da rota: {len(pontos_filtrados_rota)}")
                                    for ponto in pontos_filtrados_rota:
                                        geom_ponto = ponto.geometry()
                                        if geom_ponto.isEmpty():
                                            continue

                                        # Transformar para WGS84 se necessário
                                        if pontos_layer.crs() != crs_wgs84:
                                            xform = QgsCoordinateTransform(pontos_layer.crs(), crs_wgs84, QgsProject.instance())
                                            geom_ponto.transform(xform)

                                        ponto_xy = geom_ponto.asPoint()
                                        menor_distancia = float('inf')
                                        ponto_mais_proximo = None

                                        for poligono in poligonos_layer.getFeatures():
                                            geom_poligono = poligono.geometry()
                                            if geom_poligono.isEmpty():
                                                continue

                                            # Transformar polígono para WGS84 se necessário
                                            if poligonos_layer.crs() != crs_wgs84:
                                                xform = QgsCoordinateTransform(poligonos_layer.crs(), crs_wgs84, QgsProject.instance())
                                                geom_poligono.transform(xform)

                                            # Verificar se a geometria é MultiPolygon
                                            if geom_poligono.isMultipart():
                                                poligonos = geom_poligono.asMultiPolygon()
                                            else:
                                                poligonos = [geom_poligono.asPolygon()]

                                            for poly in poligonos:
                                                if not poly:
                                                    continue

                                                arestas = []
                                                vertices = poly[0]  # anel exterior
                                                for i in range(len(vertices) - 1):
                                                    aresta = QgsGeometry.fromPolylineXY([vertices[i], vertices[i + 1]])
                                                    arestas.append(aresta)

                                                for aresta in arestas:
                                                    ponto_proximo = aresta.nearestPoint(geom_ponto)
                                                    distancia = distance_area.measureLine(ponto_xy, ponto_proximo.asPoint())

                                                    if distancia < menor_distancia:
                                                        menor_distancia = distancia
                                                        ponto_mais_proximo = ponto_proximo

                                        # Adicionar ponto ajustado à nova camada
                                        if ponto_mais_proximo:
                                            pt_novo = ponto_mais_proximo.asPoint()
                                            respeita_distancia = True
                                            for pt_existente in pontos_aceitos:
                                                if distance_area.measureLine(pt_novo, pt_existente) < distancia_minima_m:
                                                    respeita_distancia = False
                                                    break

                                            if respeita_distancia:
                                                novo_ponto = QgsFeature()
                                                novo_ponto.setGeometry(ponto_mais_proximo)
                                                novo_ponto.setAttributes(ponto.attributes())
                                                nova_layer_provider.addFeature(novo_ponto)
                                                pontos_aceitos.append(pt_novo)

                                    # Configurar estilo e adicionar ao projeto
                                    nova_layer.renderer().symbol().setColor(QColor(0, 255, 0))  # Verde
                                    nova_layer.renderer().symbol().setSize(5)
                                    QgsProject.instance().addMapLayer(nova_layer)

                                    print("Processo concluído! Pontos ajustados às arestas em WGS84.")
