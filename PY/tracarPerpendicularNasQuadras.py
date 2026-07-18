#NOME: Traçar Perpendicular nas Quadras

#DESCRIÇÃO: Para cada ponto da camada 'IMÓVEL' (ou apenas os selecionados), encontra a aresta mais próxima da camada 'QUADRAS', traça uma linha perpendicular (aresta→ponto→interior) e cria uma camada de etiquetas com o 'seq_id' posicionado na metade interior da linha, com ângulo paralelo à aresta da quadra.

#PRÉ-REQUISITO: Carregar as camadas 'IMÓVEL' (pontos) e 'QUADRAS' (polígonos) no projeto QGIS.


from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling,
    QgsProperty,
    QgsTextFormat,
    QgsTextBufferSettings,
    QgsCoordinateTransform,
    Qgis,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMessageBox
import math


# ─────────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def _pe_da_perpendicular(px, py, ax, ay, bx, by):
    """Retorna o pé da perpendicular do ponto P(px,py) no segmento AB,
    limitado aos extremos do segmento (clamp)."""
    dx, dy = bx - ax, by - ay
    comprimento_sq = dx * dx + dy * dy
    if comprimento_sq == 0:
        return ax, ay
    t = ((px - ax) * dx + (py - ay) * dy) / comprimento_sq
    t = max(0.0, min(1.0, t))
    return ax + t * dx, ay + t * dy


def _segmentos_do_poligono(geom):
    """Retorna todos os segmentos (ax, ay, bx, by) do contorno de um polígono
    (suporta Polygon e MultiPolygon)."""
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


def _aresta_mais_proxima(px, py, candidatos_quadras):
    """Dentre todos os segmentos das quadras candidatas, retorna
    (fx, fy, ax, ay, bx, by) — pé da perpendicular mais próximo do ponto P
    junto com os extremos da aresta correspondente."""
    menor_dist = math.inf
    resultado = None

    for feat in candidatos_quadras:
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue
        for ax, ay, bx, by in _segmentos_do_poligono(geom):
            fx, fy = _pe_da_perpendicular(px, py, ax, ay, bx, by)
            dist = math.hypot(px - fx, py - fy)
            if dist < menor_dist:
                menor_dist = dist
                resultado = (fx, fy, ax, ay, bx, by)

    return resultado


# ─────────────────────────────────────────────
#  SCRIPT PRINCIPAL
# ─────────────────────────────────────────────

def executar():
    projeto = QgsProject.instance()

    # Busca as camadas pelo nome
    imovel_layers = projeto.mapLayersByName('IMÓVEL')
    quadras_layers = projeto.mapLayersByName('QUADRAS')

    if not imovel_layers:
        QMessageBox.critical(None, "Erro", "Camada 'IMÓVEL' não encontrada no projeto.")
        return
    if not quadras_layers:
        QMessageBox.critical(None, "Erro", "Camada 'QUADRAS' não encontrada no projeto.")
        return

    imovel_layer = imovel_layers[0]
    quadras_layer = quadras_layers[0]

    # ── Filtro obrigatório por ROTA DE LEITURA selecionada ──
    rotas_layers = projeto.mapLayersByName('ROTAS DE LEITURA')
    if not rotas_layers:
        QMessageBox.critical(None, "Erro", "Camada 'ROTAS DE LEITURA' não encontrada no projeto.")
        return

    rota_layer = rotas_layers[0]
    feats_rota = list(rota_layer.selectedFeatures())
    if not feats_rota:
        QMessageBox.critical(None, "Erro", "Nenhuma feição selecionada na camada 'ROTAS DE LEITURA'.\nSelecione uma rota e execute novamente.")
        return

    # Une todas as rotas selecionadas em uma única geometria
    geom_rota = feats_rota[0].geometry()
    for fr in feats_rota[1:]:
        geom_rota = geom_rota.combine(fr.geometry())

    # CRS das camadas
    crs_projeto = projeto.crs()           # EPSG:31983
    crs_rota = rota_layer.crs()           # EPSG:31983
    crs_imovel = imovel_layer.crs()       # WGS 84 (EPSG:4326)

    # Garante que geom_rota está em EPSG:31983 (projeto)
    if crs_rota != crs_projeto:
        geom_rota.transform(QgsCoordinateTransform(crs_rota, crs_projeto, projeto))

    # Transforma geom_rota para o CRS da camada IMÓVEL (WGS84)
    # para que o setFilterRect e o intersects usem o mesmo sistema de coordenadas da camada
    geom_rota_imovel = QgsGeometry(geom_rota)
    if crs_projeto != crs_imovel:
        geom_rota_imovel.transform(QgsCoordinateTransform(crs_projeto, crs_imovel, projeto))

    # Filtra imóveis que intersectam o polígono da rota (tudo em WGS84 aqui)
    bbox_imovel = geom_rota_imovel.boundingBox()
    request_imovel = QgsFeatureRequest().setFilterRect(bbox_imovel)
    pontos = []
    for f in imovel_layer.getFeatures(request_imovel):
        g = f.geometry()
        if g is None or g.isEmpty():
            continue
        if geom_rota_imovel.intersects(g):
            pontos.append(f)

    origem = f"{len(pontos)} imóvel(is) dentro da rota selecionada"
    if not pontos:
        QMessageBox.information(None, "Aviso", "Nenhum imóvel encontrado dentro da rota selecionada.")
        return

    # Transformação: CRS do imóvel (WGS84) → CRS do projeto (EPSG:31983)
    xform_imovel = QgsCoordinateTransform(crs_imovel, crs_projeto, projeto)

    # Índice espacial das QUADRAS para busca eficiente (já em EPSG:31983)
    # Se QUADRAS estiver em CRS diferente, transforma antes de indexar
    crs_quadras = quadras_layer.crs()
    xform_quadras = QgsCoordinateTransform(crs_quadras, crs_projeto, projeto) if crs_quadras != crs_projeto else None

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

    # Cria a camada temporária de linhas (CRS do projeto: EPSG:31983 - SIRGAS 2000 / UTM 23S)
    crs_str = crs_projeto.authid()
    camada_temp = QgsVectorLayer(f'LineString?crs={crs_str}', 'PERPENDICULARES', 'memory')
    provider = camada_temp.dataProvider()

    # Cria a camada temporária de etiquetas (pontos com seq_id + ângulo)
    camada_etiq = QgsVectorLayer(f'Point?crs={crs_str}', 'ETIQUETAS_IMOVEL', 'memory')
    prov_etiq = camada_etiq.dataProvider()
    prov_etiq.addAttributes([
        QgsField('seq_id', QVariant.String),
        QgsField('rotation', QVariant.Double),
        QgsField('label_x', QVariant.Double),
        QgsField('label_y', QVariant.Double),
    ])
    camada_etiq.updateFields()

    feats_linha = []
    feats_etiq = []
    sem_quadra = 0

    for ponto_feat in pontos:
        geom_ponto = ponto_feat.geometry()
        if geom_ponto is None or geom_ponto.isEmpty():
            continue

        # Transforma o ponto de WGS84 para EPSG:31983 (mesma CRS das QUADRAS e da saída)
        geom_proj = QgsGeometry(geom_ponto)
        geom_proj.transform(xform_imovel)
        pt = geom_proj.asPoint()
        px, py = pt.x(), pt.y()

        # Busca as N quadras mais próximas pelo bounding box (index)
        # Começa com 5 vizinhos; se nenhuma aresta for encontrada, expande
        ids_vizinhos = idx_quadras.nearestNeighbor(QgsPointXY(px, py), 5)
        candidatos = [todas_quadras[fid] for fid in ids_vizinhos if fid in todas_quadras]

        resultado = _aresta_mais_proxima(px, py, candidatos)

        if resultado is None:
            # Fallback: tenta com todas as quadras
            resultado = _aresta_mais_proxima(px, py, todas_quadras.values())

        if resultado is None:
            sem_quadra += 1
            continue

        fx, fy, ax, ay, bx, by = resultado

        # Linha: pé na aresta (fx,fy) → ponto (px,py) → continuação pra dentro
        # O ponto fica no meio — o vetor pé→ponto é espelhado além do ponto.
        # Ponto final = reflexo do pé em relação ao ponto = (2*px - fx, 2*py - fy)
        ex = 2 * px - fx
        ey = 2 * py - fy

        linha_geom = QgsGeometry.fromPolylineXY([
            QgsPointXY(fx, fy),
            QgsPointXY(px, py),
            QgsPointXY(ex, ey),
        ])
        feat_linha = QgsFeature()
        feat_linha.setGeometry(linha_geom)
        feats_linha.append(feat_linha)

        # ── Etiqueta: posição no meio da metade interior (ponto → extremo interno)
        lx = (px + ex) / 2.0
        ly = (py + ey) / 2.0

        # Ângulo da perpendicular no sentido aresta → interior (pé → ponto).
        # O vetor (dx_perp, dy_perp) aponta SEMPRE para dentro do polígono.
        dx_perp = px - fx
        dy_perp = py - fy

        # Ângulo geográfico da linha em coordenadas padrão (CCW a partir de Leste).
        angulo_bruto = math.degrees(math.atan2(dy_perp, dx_perp))

        # QGIS rotaciona no sentido horário. Para o baseline do texto ficar
        # PARALELO à linha (aresta→ponto→etiqueta), basta negar o ângulo:
        #   baseline_math = -R_qgis  →  R_qgis = -angulo_bruto
        angulo = -angulo_bruto

        # Normaliza para (-180, 180] — sem restrição a [-90, 90] para manter
        # o padrão horário: aresta → ponto → etiqueta, independente da orientação.
        angulo = ((angulo + 180.0) % 360.0) - 180.0

        # seq_id do imóvel (usa string vazia se o campo não existir)
        try:
            seq_val = str(ponto_feat['seq_id'])
        except Exception:
            seq_val = str(ponto_feat.id())

        feat_etiq = QgsFeature(camada_etiq.fields())
        # Ponto coincide com o imóvel (px,py).
        # label_x/label_y = meio da metade interior (ponto → extremo interno),
        # onde o centro do texto será ancorado diretamente sobre a linha.
        feat_etiq.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(px, py)))
        feat_etiq.setAttributes([seq_val, angulo, lx, ly])  # label_x/label_y = meio da metade interior
        feats_etiq.append(feat_etiq)

    provider.addFeatures(feats_linha)
    camada_temp.updateExtents()
    projeto.addMapLayer(camada_temp)

    # ── Configura etiquetas na camada de etiquetas ──
    prov_etiq.addFeatures(feats_etiq)
    camada_etiq.updateExtents()

    pal = QgsPalLayerSettings()
    pal.fieldName = 'seq_id'
    pal.enabled = True

    # Compatibilidade com QGIS >= 3.30 (Qgis.LabelPlacement) e versões anteriores
    try:
        pal.placement = Qgis.LabelPlacement.OverPoint
    except AttributeError:
        pal.placement = QgsPalLayerSettings.OverPoint

    # Rotação data-definida pelo campo 'rotation'
    dd = pal.dataDefinedProperties()
    dd.setProperty(QgsPalLayerSettings.LabelRotation, QgsProperty.fromField('rotation'))
    # Ancora a etiqueta em (ex,ey) = extremo interior da linha, sempre após o ponto
    dd.setProperty(QgsPalLayerSettings.PositionX, QgsProperty.fromField('label_x'))
    dd.setProperty(QgsPalLayerSettings.PositionY, QgsProperty.fromField('label_y'))
    pal.setDataDefinedProperties(dd)

    # Texto branco com buffer (halo) azul
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

    msg = f"Concluído! {len(feats_linha)} perpendicular(es) e {len(feats_etiq)} etiqueta(s) criada(s) a partir de {origem}."
    if sem_quadra:
        msg += f"\n{sem_quadra} ponto(s) ignorado(s) por não encontrar quadra próxima."

    QMessageBox.information(None, "Perpendiculares — Concluído", msg)


executar()
