#NOME: Gerar Pdf da Rota Selecionada

#DESCRIÇÃO: gerarPdfDaRotaSelecionada.py Exporta PDFs e arquivos QPT para varias rotas selecionadas na camada 'ROTAS DE LEITURA'. O script abre uma unica janela para informar: - template QPT base - pasta de saida dos QPTs - pasta de saida dos PDFs - localidade, setor e municipio Para cada feicao selecionada, o valor da rota e lido. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# -*- coding: utf-8 -*-
"""
gerarPdfDaRotaSelecionada.py

Exporta PDFs e arquivos QPT para varias rotas selecionadas na camada
'ROTAS DE LEITURA'. O script abre uma unica janela para informar:
- template QPT base
- pasta de saida dos QPTs
- pasta de saida dos PDFs
- localidade, setor e municipio

Para cada feicao selecionada, o valor da rota e lido do atributo 'rota'
da camada de rotas, o layout e preenchido automaticamente e os arquivos
finais sao gerados nas pastas informadas.
"""

import math
import os
import shutil
import time
import unicodedata

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLineSymbol,
    QgsMapLayerStyle,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsPrintLayout,
    QgsProject,
    QgsProperty,
    QgsRectangle,
    QgsReadWriteContext,
    QgsSingleSymbolRenderer,
    QgsSpatialIndex,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QDateTime, QSettings, QStandardPaths, QVariant, Qt
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qgis.PyQt.QtXml import QDomDocument


NOME_CAMADA_ROTA = 'ROTAS DE LEITURA'
NOME_CAMADA_IMOVEL = 'IMÓVEL'
NOME_CAMADA_QUADRAS = 'QUADRAS'
NOME_CAMADA_OVERLEY = 'OVERLEY'
NOME_CAMADA_INICIO = 'INICIO_PNT'
NOME_CAMADA_FIM = 'FIM_PNT'
NOME_CAMADA_ARRUAMENTO = 'ARRUAMENTO_MA'
NOME_CAMADA_ETIQ = 'ETIQUETAS_IMOVEL'

MARGEM_ENQUADRAMENTO = 0.03
DESLOCAMENTO_IMOVEL_M = 2.0
SETTINGS_KEY_LOGO_CAEMA = 'smartsync/layout/logo_caema_path'
APLICAR_DESLOCAMENTO_IMOVEL = True
IMOVEL_POINT_SIZE = 0.55
SEQ_ID_SIZE_MIN = 2.60
SEQ_ID_SIZE_MAX = 4.20
SEQ_ID_DIST_MIN = 0.01
SEQ_ID_DIST_MAX = 0.05
SEQ_ID_BUFFER_SIZE = 0.24


def _get_layer(nome):
    layers = QgsProject.instance().mapLayersByName(nome)
    if not layers:
        raise RuntimeError(f"Camada '{nome}' nao encontrada no projeto.")
    return layers[0]


def _copiar_estilo(orig, dest):
    estilo = QgsMapLayerStyle()
    estilo.readFromLayer(orig)
    estilo.writeToLayer(dest)


def _aplicar_estilo_preto_branco(layer, papel='default'):
    geom_type = QgsWkbTypes.geometryType(layer.wkbType())

    if geom_type == QgsWkbTypes.PolygonGeometry:
        if papel == 'rota':
            symbol = QgsFillSymbol.createSimple({
                'color': '255,255,255,0',
                'outline_color': '0,0,0,255',
                'outline_width': '0.4',
            })
        else:
            symbol = QgsFillSymbol.createSimple({
                'color': '255,255,255,255',
                'outline_color': '0,0,0,255',
                'outline_width': '0.15',
            })
    elif geom_type == QgsWkbTypes.LineGeometry:
        largura = '0.18'
        if papel == 'overley':
            largura = '0.35'
        symbol = QgsLineSymbol.createSimple({
            'line_color': '0,0,0,255',
            'line_width': largura,
        })
    else:
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '0,0,0,255',
            'outline_color': '0,0,0,255',
            'size': '1.6',
        })

    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


def _new_memory_like(layer_origem, novo_nome):
    wkb = QgsWkbTypes.displayString(layer_origem.wkbType())
    crs_authid = layer_origem.crs().authid()
    uri = f"{wkb}?crs={crs_authid}"
    nova = QgsVectorLayer(uri, novo_nome, 'memory')
    prov = nova.dataProvider()
    prov.addAttributes(layer_origem.fields())
    nova.updateFields()
    return nova


def _clip_features_to_polygon(layer_origem, geom_rota, nome_saida, crs_rota=None):
    layer_out = _new_memory_like(layer_origem, nome_saida)
    prov = layer_out.dataProvider()
    geom_recorte = QgsGeometry(geom_rota)

    if crs_rota and crs_rota.isValid() and layer_origem.crs().isValid() and crs_rota != layer_origem.crs():
        try:
            xform = QgsCoordinateTransform(
                crs_rota,
                layer_origem.crs(),
                QgsProject.instance().transformContext(),
            )
        except Exception:
            xform = QgsCoordinateTransform(crs_rota, layer_origem.crs(), QgsProject.instance())
        geom_recorte.transform(xform)

    try:
        geom_recorte = geom_recorte.makeValid()
    except Exception:
        pass

    geom_type = QgsWkbTypes.geometryType(layer_origem.wkbType())
    novos = []
    for feat in layer_origem.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue

        try:
            intersecta = (
                geom_recorte.intersects(geom)
                or geom_recorte.contains(geom)
                or geom_recorte.touches(geom)
                or geom.within(geom_recorte)
            )
        except Exception:
            intersecta = False
        if not intersecta:
            continue

        if geom_type == QgsWkbTypes.PointGeometry:
            clip = QgsGeometry(geom)
        else:
            try:
                clip = geom.intersection(geom_recorte)
            except Exception:
                try:
                    clip = geom.makeValid().intersection(geom_recorte.makeValid())
                except Exception:
                    clip = None
        if clip is None or clip.isEmpty():
            continue

        novo_feat = QgsFeature(layer_out.fields())
        novo_feat.setAttributes(feat.attributes())
        novo_feat.setGeometry(clip)
        novos.append(novo_feat)

    if novos:
        prov.addFeatures(novos)
    layer_out.updateExtents()
    _copiar_estilo(layer_origem, layer_out)
    return layer_out


def _build_route_layer(layer_rota, feat_rota, nome_saida):
    out = _new_memory_like(layer_rota, nome_saida)
    prov = out.dataProvider()
    nf = QgsFeature(out.fields())
    nf.setAttributes(feat_rota.attributes())
    nf.setGeometry(QgsGeometry(feat_rota.geometry()))
    prov.addFeatures([nf])
    out.updateExtents()
    _copiar_estilo(layer_rota, out)
    return out


def _guess_rota_label(feat):
    candidatos = ('rota', 'ROTA', 'rot_id', 'ROT_ID', 'id', 'ID')
    campos = feat.fields().names()
    for campo in candidatos:
        if campo in campos:
            try:
                valor = feat[campo]
                if valor is not None and str(valor).strip() != '':
                    return str(valor)
            except Exception:
                pass
    return str(feat.id())


def _find_existing_field_name(layer, candidatos):
    nomes = layer.fields().names()
    nomes_lower = {n.lower(): n for n in nomes}
    for cand in candidatos:
        if cand in nomes:
            return cand
        achado = nomes_lower.get(cand.lower())
        if achado:
            return achado
    return None


def _normalizar_campo_txt(txt):
    if txt is None:
        return ''
    s = str(txt).strip().upper()
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')
    s = s.replace('_', ' ')
    return ' '.join(s.split())


def _point_xy_from_geom(geom):
    if geom is None or geom.isEmpty():
        return None
    wt = geom.wkbType()
    if QgsWkbTypes.isMultiType(wt):
        pts = geom.asMultiPoint()
        return pts[0] if pts else None
    return geom.asPoint()


def _iter_polygon_segments(layer):
    for feat in layer.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue
        wt = geom.wkbType()
        partes = geom.asMultiPolygon() if QgsWkbTypes.isMultiType(wt) else [geom.asPolygon()]
        for parte in partes:
            if not parte:
                continue
            poly_geom = QgsGeometry.fromPolygonXY(parte)
            for anel in parte:
                if len(anel) < 2:
                    continue
                for i in range(len(anel) - 1):
                    p1 = anel[i]
                    p2 = anel[i + 1]
                    if p1.x() == p2.x() and p1.y() == p2.y():
                        continue
                    yield p1, p2, poly_geom


def _angulo_perpendicular_para_ponto(p1, p2, pt):
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    seg_len2 = dx * dx + dy * dy
    if seg_len2 == 0:
        return 0.0

    t = ((pt.x() - p1.x()) * dx + (pt.y() - p1.y()) * dy) / float(seg_len2)
    t = max(0.0, min(1.0, t))
    proj_x = p1.x() + t * dx
    proj_y = p1.y() + t * dy

    nx = -dy
    ny = dx
    vx = pt.x() - proj_x
    vy = pt.y() - proj_y
    if (vx * nx + vy * ny) < 0:
        nx = -nx
        ny = -ny

    return math.degrees(math.atan2(ny, nx)) % 360.0


def _normal_interna_e_deslocamento(p1, p2, pt, poly_geom, dist_m):
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    seg_len = math.hypot(dx, dy)
    if seg_len == 0:
        return None, 0.0

    nx = -dy / seg_len
    ny = dx / seg_len
    cand1 = QgsGeometry.fromPointXY(QgsPointXY(pt.x() + nx * dist_m, pt.y() + ny * dist_m))
    cand2 = QgsGeometry.fromPointXY(QgsPointXY(pt.x() - nx * dist_m, pt.y() - ny * dist_m))
    inside1 = poly_geom.contains(cand1) if poly_geom is not None else False
    inside2 = poly_geom.contains(cand2) if poly_geom is not None else False

    if inside1 and not inside2:
        escolhido = QgsPointXY(cand1.asPoint())
        ang = math.degrees(math.atan2(ny, nx)) % 360.0
    elif inside2 and not inside1:
        escolhido = QgsPointXY(cand2.asPoint())
        ang = math.degrees(math.atan2(-ny, -nx)) % 360.0
    elif inside1 and inside2:
        escolhido = QgsPointXY(cand1.asPoint())
        ang = math.degrees(math.atan2(ny, nx)) % 360.0
    else:
        ang = _angulo_perpendicular_para_ponto(p1, p2, pt)
        ang_rad = math.radians(ang)
        escolhido = QgsPointXY(pt.x() + math.cos(ang_rad) * dist_m, pt.y() + math.sin(ang_rad) * dist_m)

    return escolhido, ang


def _distancia_ponto_segmento(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / float(dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def _segmentos_da_geometria_poligono(geom):
    if geom is None or geom.isEmpty():
        return []

    wt = geom.wkbType()
    partes = geom.asMultiPolygon() if QgsWkbTypes.isMultiType(wt) else [geom.asPolygon()]
    segmentos = []

    for parte in partes:
        if not parte:
            continue
        for anel in parte:
            if len(anel) < 2:
                continue
            for i in range(len(anel) - 1):
                p1 = anel[i]
                p2 = anel[i + 1]
                if p1.x() == p2.x() and p1.y() == p2.y():
                    continue
                segmentos.append((p1, p2))

    return segmentos


def _normalizar_angulo_legivel(ang):
    ang = ang % 360.0
    # Evita rótulos de cabeça para baixo.
    if 90.0 < ang <= 270.0:
        ang = (ang + 180.0) % 360.0
    return ang


def _angulo_perpendicular_pelo_segmento(p1, p2, pt_xy):
    if p1 is None or p2 is None or pt_xy is None:
        return None

    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    if dx == 0 and dy == 0:
        return None

    ang_seg = math.degrees(math.atan2(dy, dx)) % 360.0
    ang_perp_a = (ang_seg + 90.0) % 360.0
    ang_perp_b = (ang_seg + 270.0) % 360.0

    seg_len2 = dx * dx + dy * dy
    t = ((pt_xy.x() - p1.x()) * dx + (pt_xy.y() - p1.y()) * dy) / float(seg_len2)
    t = max(0.0, min(1.0, t))
    proj_x = p1.x() + t * dx
    proj_y = p1.y() + t * dy
    pt_proj = QgsPointXY(proj_x, proj_y)

    vx = pt_xy.x() - pt_proj.x()
    vy = pt_xy.y() - pt_proj.y()
    nx = math.cos(math.radians(ang_perp_a))
    ny = math.sin(math.radians(ang_perp_a))
    ang_final = ang_perp_a if (vx * nx + vy * ny) >= 0 else ang_perp_b

    return _normalizar_angulo_legivel(ang_final)


def _configurar_camada_etiquetas_imovel(camada):
    """Configura a camada ETIQUETAS_IMOVEL para uso no layout PDF:
    tamanho fixo 5pt, posição pela campos label_x/label_y, rotação pelo campo rotation."""
    pal = QgsPalLayerSettings()
    pal.fieldName = 'seq_id'
    pal.enabled = True

    try:
        pal.placement = QgsPalLayerSettings.Placement.OverPoint
    except AttributeError:
        pal.placement = QgsPalLayerSettings.OverPoint

    try:
        pal.displayAll = True
    except Exception:
        pass

    dd = pal.dataDefinedProperties()
    dd.setProperty(QgsPalLayerSettings.LabelRotation, QgsProperty.fromField('rotation'))
    dd.setProperty(QgsPalLayerSettings.PositionX, QgsProperty.fromField('label_x'))
    dd.setProperty(QgsPalLayerSettings.PositionY, QgsProperty.fromField('label_y'))
    try:
        dd.setProperty(QgsPalLayerSettings.Pinned, QgsProperty.fromExpression('true'))
    except Exception:
        pass
    pal.setDataDefinedProperties(dd)

    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setColor(QColor(255, 255, 255))
    buf.setSize(SEQ_ID_BUFFER_SIZE)

    fmt = QgsTextFormat()
    fmt.setFont(QFont('Arial', 4))
    fmt.setColor(QColor(0, 0, 0))
    fmt.setSize(5.0)
    fmt.setSizeUnit(QgsUnitTypes.RenderPoints)
    fmt.setBuffer(buf)
    pal.setFormat(fmt)

    # Ponto invisível — apenas o rótulo interessa no PDF
    symbol_invis = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': '0,0,0,0',
        'outline_color': '0,0,0,0',
        'size': '0',
    })
    camada.setRenderer(QgsSingleSymbolRenderer(symbol_invis))

    camada.setLabeling(QgsVectorLayerSimpleLabeling(pal))
    camada.setLabelsEnabled(True)
    camada.triggerRepaint()


def _configurar_rotulos_quadras(tmp_quadras):
    campo = _find_existing_field_name(tmp_quadras, ('quadra', 'QUADRA', 'Quadra'))
    if not campo:
        print('Campo quadra nao encontrado em QUADRAS; rotulos nao foram aplicados.')
        return

    settings = QgsPalLayerSettings()
    settings.enabled = True
    settings.fieldName = campo
    try:
        settings.placement = QgsPalLayerSettings.Placement.OverPoint
    except Exception:
        try:
            settings.placement = QgsPalLayerSettings.OverPoint
        except Exception:
            pass
    settings.priority = 8
    try:
        settings.displayAll = True
    except Exception:
        try:
            settings.setDisplayAll(True)
        except Exception:
            pass

    text_format = QgsTextFormat()
    fonte_quadras = QFont('Arial', 7)
    fonte_quadras.setBold(True)
    text_format.setFont(fonte_quadras)
    text_format.setSize(7)
    text_format.setColor(QColor(0, 0, 0))

    buffer = QgsTextBufferSettings()
    buffer.setEnabled(False)
    text_format.setBuffer(buffer)
    settings.setFormat(text_format)

    tmp_quadras.setLabelsEnabled(True)
    tmp_quadras.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    tmp_quadras.triggerRepaint()


def _criar_camada_rotulo_quadras(tmp_quadras, nome_saida):
    """Cria uma camada de pontos (centroides) para forcar rotulos de todas as quadras."""
    campo = _find_existing_field_name(tmp_quadras, ('quadra', 'QUADRA', 'Quadra'))
    if not campo:
        return None

    uri = f"Point?crs={tmp_quadras.crs().authid()}"
    camada = QgsVectorLayer(uri, nome_saida, 'memory')
    prov = camada.dataProvider()
    prov.addAttributes([QgsField(campo, tmp_quadras.fields().field(campo).type())])
    camada.updateFields()

    novos = []
    for feat in tmp_quadras.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue
        try:
            pt = geom.pointOnSurface()
            if pt is None or pt.isEmpty():
                pt = geom.centroid()
        except Exception:
            pt = geom.centroid()
        if pt is None or pt.isEmpty():
            continue

        nf = QgsFeature(camada.fields())
        try:
            nf.setAttribute(campo, feat[campo])
        except Exception:
            nf.setAttribute(campo, '')
        nf.setGeometry(pt)
        novos.append(nf)

    if novos:
        prov.addFeatures(novos)
    camada.updateExtents()

    simbolo_invisivel = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'size': '0.1',
        'color': '0,0,0,0',
        'outline_color': '0,0,0,0',
    })
    camada.setRenderer(QgsSingleSymbolRenderer(simbolo_invisivel))

    settings = QgsPalLayerSettings()
    settings.enabled = True
    settings.fieldName = campo
    try:
        settings.placement = QgsPalLayerSettings.Placement.OverPoint
    except Exception:
        try:
            settings.placement = QgsPalLayerSettings.OverPoint
        except Exception:
            pass
    settings.priority = 10
    try:
        settings.displayAll = True
    except Exception:
        try:
            settings.setDisplayAll(True)
        except Exception:
            pass
    try:
        settings.obstacle = False
    except Exception:
        pass

    text_format = QgsTextFormat()
    fonte = QFont('Arial', 7)
    fonte.setBold(True)
    text_format.setFont(fonte)
    text_format.setSize(7)
    text_format.setColor(QColor(0, 0, 0))

    buffer = QgsTextBufferSettings()
    buffer.setEnabled(False)
    text_format.setBuffer(buffer)
    settings.setFormat(text_format)

    camada.setLabelsEnabled(True)
    camada.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    camada.triggerRepaint()
    return camada


def _configurar_rotulos_arruamento(tmp_arruamento):
    campo = _find_existing_field_name(
        tmp_arruamento,
        ('nm_logradouro', 'NM_LOGRADOURO', 'nome_logradouro', 'NOME_LOGRADOURO'),
    )
    if not campo:
        print('Campo nm_logradouro nao encontrado em ARRUAMENTO_MA; rotulos nao foram aplicados.')
        return

    settings = QgsPalLayerSettings()
    settings.enabled = True
    settings.fieldName = campo
    try:
        settings.placement = QgsPalLayerSettings.Placement.Line
    except Exception:
        try:
            settings.placement = QgsPalLayerSettings.Line
        except Exception:
            settings.placement = 3
    settings.priority = 7

    text_format = QgsTextFormat()
    text_format.setFont(QFont('Arial', 4))
    text_format.setSize(1.5)
    text_format.setColor(QColor(0, 0, 0))
    try:
        text_format.setOpacity(1.0)
    except Exception:
        pass

    buffer = QgsTextBufferSettings()
    buffer.setEnabled(False)
    buffer.setSize(0.0)
    buffer.setColor(QColor(0, 0, 0, 0))
    text_format.setBuffer(buffer)

    # Em algumas versões, halo cinza pode vir de sombra/fundo/máscara.
    try:
        sombra = text_format.shadow()
        sombra.setEnabled(False)
        text_format.setShadow(sombra)
    except Exception:
        pass
    try:
        fundo = text_format.background()
        fundo.setEnabled(False)
        text_format.setBackground(fundo)
    except Exception:
        pass
    try:
        mascara = text_format.mask()
        mascara.setEnabled(False)
        text_format.setMask(mascara)
    except Exception:
        pass

    settings.setFormat(text_format)

    tmp_arruamento.setLabelsEnabled(False)
    tmp_arruamento.setLabeling(None)
    tmp_arruamento.setLabelsEnabled(True)
    tmp_arruamento.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    tmp_arruamento.triggerRepaint()


def _calcular_dados_rotulos_imovel(tmp_imovel, tmp_quadras):
    """Calcula ângulos e parâmetros de rótulos para cada imóvel.
    Retorna lista de dicionários com informações de cada imóvel."""
    
    campo_seq = _find_existing_field_name(tmp_imovel, ('seq_id', 'SEQ_ID', 'seqid', 'SEQID'))
    if not campo_seq:
        print('Campo seq_id nao encontrado em IMÓVEL; retornando lista vazia.')
        return []

    quadras_por_id = {f.id(): f for f in tmp_quadras.getFeatures()}
    indice_quadras = None
    if quadras_por_id:
        indice_quadras = QgsSpatialIndex()
        for feat_q in quadras_por_id.values():
            indice_quadras.addFeature(feat_q)
    def _obter_quadra_referencia(pt_xy):
        if indice_quadras is None:
            return None

        eps = 1e-9
        rect = QgsRectangle(pt_xy.x() - eps, pt_xy.y() - eps, pt_xy.x() + eps, pt_xy.y() + eps)
        candidatos_bbox = indice_quadras.intersects(rect)
        candidatos = list(candidatos_bbox) if candidatos_bbox else []
        if not candidatos:
            candidatos = indice_quadras.nearestNeighbor(pt_xy, 10)
        if not candidatos:
            return None

        melhor_feat = None
        melhor_dist = float('inf')
        pt_geom = QgsGeometry.fromPointXY(pt_xy)

        for fid in candidatos:
            feat_q = quadras_por_id.get(fid)
            if feat_q is None:
                continue
            geom_q = feat_q.geometry()
            if geom_q is None or geom_q.isEmpty():
                continue
            try:
                if geom_q.contains(pt_geom) or geom_q.touches(pt_geom):
                    return feat_q
            except Exception:
                pass

            try:
                dist = geom_q.distance(pt_geom)
            except Exception:
                dist = float('inf')

            if dist < melhor_dist:
                melhor_dist = dist
                melhor_feat = feat_q

        return melhor_feat

    def _segmento_mais_proximo_da_quadra(geom_q, pt_xy):
        segmentos = _segmentos_da_geometria_poligono(geom_q)
        if not segmentos:
            return None
        melhor = None
        melhor_dist = float('inf')
        for p1, p2 in segmentos:
            d = _distancia_ponto_segmento(pt_xy.x(), pt_xy.y(), p1.x(), p1.y(), p2.x(), p2.y())
            if d < melhor_dist:
                melhor_dist = d
                melhor = (p1, p2)
        return melhor

    imoveis_por_id = {f.id(): f for f in tmp_imovel.getFeatures()}
    indice_imoveis = QgsSpatialIndex()
    for feat_i in imoveis_por_id.values():
        indice_imoveis.addFeature(feat_i)

    dist_vizinho = {}
    for feat in imoveis_por_id.values():
        pt = _point_xy_from_geom(feat.geometry())
        if pt is None:
            continue
        candidatos = indice_imoveis.nearestNeighbor(pt, 3)
        menor = None
        for fid in candidatos:
            if fid == feat.id():
                continue
            viz = imoveis_por_id.get(fid)
            if viz is None:
                continue
            pt_viz = _point_xy_from_geom(viz.geometry())
            if pt_viz is None:
                continue
            d = math.hypot(pt.x() - pt_viz.x(), pt.y() - pt_viz.y())
            if menor is None or d < menor:
                menor = d
        dist_vizinho[feat.id()] = menor if menor is not None else 0.0

    valores_dist = sorted([d for d in dist_vizinho.values() if d > 0])
    if valores_dist:
        idx20 = int((len(valores_dist) - 1) * 0.20)
        idx80 = int((len(valores_dist) - 1) * 0.80)
        p20 = valores_dist[idx20]
        p80 = valores_dist[idx80]
        if p80 <= p20:
            p80 = p20 + 1e-9
    else:
        p20 = 0.0
        p80 = 1.0

    base_por_id = {}
    dist_borda = {}
    for feat in imoveis_por_id.values():
        pt = _point_xy_from_geom(feat.geometry())
        if pt is None:
            continue

        melhor_ang = 0.0
        menor_dist_borda = 0.0
        if APLICAR_DESLOCAMENTO_IMOVEL:
            quadra_ref = _obter_quadra_referencia(pt)
            if quadra_ref is not None:
                seg = _segmento_mais_proximo_da_quadra(quadra_ref.geometry(), pt)
                if seg is not None:
                    menor_dist_borda = _distancia_ponto_segmento(pt.x(), pt.y(), seg[0].x(), seg[0].y(), seg[1].x(), seg[1].y())
                    ang_quadra = _angulo_perpendicular_pelo_segmento(seg[0], seg[1], pt)
                    if ang_quadra is not None:
                        melhor_ang = ang_quadra
                        # DEBUG: Mostrar segmento e ângulo antes da normalização
                        print(f"[DEBUG CALC] FID={feat.id()}, seg=({seg[0].x():.2f},{seg[0].y():.2f})-({seg[1].x():.2f},{seg[1].y():.2f}), ang_bruto={ang_quadra:.2f}°")

        angulo_final = _normalizar_angulo_legivel(melhor_ang)
        base_por_id[feat.id()] = angulo_final
        print(f"[DEBUG CALC] FID={feat.id()}, ang_normalizado={angulo_final:.2f}°")
        dist_borda[feat.id()] = menor_dist_borda

    valores_borda = sorted([d for d in dist_borda.values() if d > 0])
    if valores_borda:
        idx20_b = int((len(valores_borda) - 1) * 0.20)
        idx80_b = int((len(valores_borda) - 1) * 0.80)
        p20_b = valores_borda[idx20_b]
        p80_b = valores_borda[idx80_b]
        if p80_b <= p20_b:
            p80_b = p20_b + 1e-9
    else:
        p20_b = 0.0
        p80_b = 1.0

    def _escala_dinamica(d_viz, d_borda):
        if d_viz <= 0:
            f_v = 0.0
        else:
            f_v = (d_viz - p20) / float(p80 - p20)
            f_v = max(0.0, min(1.0, f_v))

        if d_borda <= 0:
            f_b = 0.0
        else:
            f_b = (d_borda - p20_b) / float(p80_b - p20_b)
            f_b = max(0.0, min(1.0, f_b))

        # Otimiza tamanho usando espaço local e distância da borda da quadra.
        f = min(f_v, f_b)
        f = math.sqrt(f)
        tamanho = SEQ_ID_SIZE_MIN + (SEQ_ID_SIZE_MAX - SEQ_ID_SIZE_MIN) * f

        # Distância curta mantém seq_id ao lado do ponto e ajuda a ficar dentro da quadra.
        f_dist = min(f_v, f_b)
        distancia = SEQ_ID_DIST_MIN + (SEQ_ID_DIST_MAX - SEQ_ID_DIST_MIN) * f_dist
        return tamanho, distancia

    # Preparar lista de dados para retornar
    dados_imoveis = []
    for feat in imoveis_por_id.values():
        pt = _point_xy_from_geom(feat.geometry())
        if pt is None:
            continue
        
        fid = feat.id()
        angulo = base_por_id.get(fid, 0.0)
        tamanho_lbl, dist_lbl = _escala_dinamica(dist_vizinho.get(fid, 0.0), dist_borda.get(fid, 0.0))
        
        seq_id_valor = feat[campo_seq] if campo_seq else ''
        
        # DEBUG: Imprimir ângulo calculado para cada imóvel
        print(f"[DEBUG] Imovel seq_id={seq_id_valor}, angulo={angulo:.2f}°, tamanho={tamanho_lbl:.2f}, dist={dist_lbl:.3f}")
        
        dados_imoveis.append({
            'geometry': QgsGeometry(feat.geometry()),
            'seq_id': seq_id_valor,
            'angulo': angulo,
            'tamanho': tamanho_lbl,
            'distancia': dist_lbl,
            'attributes': feat.attributes(),
            'fields': tmp_imovel.fields(),
        })
    
    return dados_imoveis


def _criar_camadas_individuais_imovel(dados_imoveis, crs, nome_base):
    """Cria uma camada temporária para cada imóvel com configuração individual de rótulo.
    Isso garante que cada seq_id fique perpendicular à aresta da quadra correspondente."""
    
    camadas_individuais = []
    
    for idx, dados in enumerate(dados_imoveis):
        # Criar camada temporária para este imóvel específico
        uri = f"Point?crs={crs.authid()}"
        nome_camada = f"{nome_base}_IMOVEL_{idx}"
        camada = QgsVectorLayer(uri, nome_camada, 'memory')
        prov = camada.dataProvider()
        
        # Adicionar campos: seq_id, angulo_rotulo, tamanho_rotulo, dist_rotulo
        prov.addAttributes([
            QgsField('seq_id', QVariant.String),
            QgsField('angulo_rotulo', QVariant.Double),
            QgsField('tamanho_rotulo', QVariant.Double),
            QgsField('dist_rotulo', QVariant.Double),
        ])
        camada.updateFields()
        
        # Criar feature com geometria e todos os atributos
        feat = QgsFeature(camada.fields())
        feat.setGeometry(dados['geometry'])
        feat.setAttribute('seq_id', str(dados['seq_id']))
        feat.setAttribute('angulo_rotulo', float(dados['angulo']))
        feat.setAttribute('tamanho_rotulo', float(dados['tamanho']))
        feat.setAttribute('dist_rotulo', float(dados['distancia']))
        prov.addFeatures([feat])
        camada.updateExtents()
        
        # Aplicar símbolo de ponto preto
        symbol_pt = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '0,0,0,255',
            'outline_color': '0,0,0,255',
            'outline_width': '0.30',
            'size': str(IMOVEL_POINT_SIZE),
        })
        camada.setRenderer(QgsSingleSymbolRenderer(symbol_pt))
        
        try:
            camada.setScaleBasedVisibility(False)
        except Exception:
            pass
        try:
            camada.setOpacity(1.0)
        except Exception:
            pass
        
        # Configurar rótulo com rotação data-defined usando campo angulo_rotulo
        settings = QgsPalLayerSettings()
        settings.enabled = True
        settings.fieldName = 'seq_id'
        
        try:
            settings.upsidedownLabels = QgsPalLayerSettings.UpsideDownLabels.UpsideDownLabelsUpright
        except Exception:
            try:
                settings.upsidedownLabels = QgsPalLayerSettings.Upright
            except Exception:
                pass
        
        try:
            settings.placement = QgsPalLayerSettings.Placement.OffsetFromPoint
        except Exception:
            try:
                settings.placement = QgsPalLayerSettings.OffsetFromPoint
            except Exception:
                try:
                    settings.placement = QgsPalLayerSettings.Placement.AroundPoint
                except Exception:
                    try:
                        settings.placement = QgsPalLayerSettings.AroundPoint
                    except Exception:
                        pass
        
        try:
            settings.quadOffset = QgsPalLayerSettings.QuadrantRight
        except Exception:
            try:
                settings.quadOffset = QgsPalLayerSettings.Right
            except Exception:
                pass
        
        settings.priority = 10
        
        try:
            settings.displayAll = True
        except Exception:
            try:
                settings.setDisplayAll(True)
            except Exception:
                pass
        
        # Configurar formato do texto
        text_format = QgsTextFormat()
        text_format.setFont(QFont('Arial', 4))
        text_format.setSize(float(dados['tamanho']))
        text_format.setColor(QColor(0, 0, 0))
        
        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(SEQ_ID_BUFFER_SIZE)
        buffer.setColor(QColor(255, 255, 255))
        text_format.setBuffer(buffer)
        settings.setFormat(text_format)
        
        # Aplicar rotação, tamanho e distância DIRETAMENTE (não via data-defined)
        # Como cada camada tem apenas 1 feição, não precisa de data-defined
        settings.angleOffset = float(dados['angulo'])
        settings.dist = float(dados['distancia'])
        
        print(f"[DEBUG] Camada {nome_camada}: seq_id={dados['seq_id']}, angulo_aplicado={dados['angulo']:.2f}°, tamanho={dados['tamanho']:.2f}, dist={dados['distancia']:.3f}")
        
        camada.setLabelsEnabled(True)
        camada.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        camada.triggerRepaint()
        
        camadas_individuais.append(camada)
    
    return camadas_individuais


def _configurar_rotulos_imovel(tmp_imovel, tmp_quadras):
    """Função legada mantida para compatibilidade (não usada na nova abordagem)."""
    symbol_pt = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': '0,0,0,255',
        'outline_color': '0,0,0,255',
        'outline_width': '0.30',
        'size': str(IMOVEL_POINT_SIZE),
    })
    tmp_imovel.setRenderer(QgsSingleSymbolRenderer(symbol_pt))
    try:
        tmp_imovel.setScaleBasedVisibility(False)
    except Exception:
        pass
    try:
        tmp_imovel.setOpacity(1.0)
    except Exception:
        pass

    campo_seq = _find_existing_field_name(tmp_imovel, ('seq_id', 'SEQ_ID', 'seqid', 'SEQID'))
    if not campo_seq:
        print('Campo seq_id nao encontrado em IMÓVEL; apenas os pontos foram exibidos.')
        tmp_imovel.triggerRepaint()
        return

    prov = tmp_imovel.dataProvider()
    novos_campos = []
    if 'label_rot' not in tmp_imovel.fields().names():
        novos_campos.append(QgsField('label_rot', QVariant.Double))
    if 'label_size' not in tmp_imovel.fields().names():
        novos_campos.append(QgsField('label_size', QVariant.Double))
    if 'label_dist' not in tmp_imovel.fields().names():
        novos_campos.append(QgsField('label_dist', QVariant.Double))
    if novos_campos:
        prov.addAttributes(novos_campos)
        tmp_imovel.updateFields()

    idx_rot = tmp_imovel.fields().indexFromName('label_rot')
    idx_size = tmp_imovel.fields().indexFromName('label_size')
    idx_dist = tmp_imovel.fields().indexFromName('label_dist')

    imoveis_por_id = {f.id(): f for f in tmp_imovel.getFeatures()}
    updates = {}
    for fid, feat in imoveis_por_id.items():
        updates[fid] = {
            idx_rot: 0.0,
            idx_size: SEQ_ID_SIZE_MIN,
            idx_dist: SEQ_ID_DIST_MIN,
        }

    if updates:
        tmp_imovel.startEditing()
        tmp_imovel.dataProvider().changeAttributeValues(updates)
        tmp_imovel.commitChanges()

    settings = QgsPalLayerSettings()
    settings.enabled = True
    settings.fieldName = campo_seq
    try:
        settings.upsidedownLabels = QgsPalLayerSettings.UpsideDownLabels.UpsideDownLabelsUpright
    except Exception:
        try:
            settings.upsidedownLabels = QgsPalLayerSettings.Upright
        except Exception:
            pass
    try:
        settings.placement = QgsPalLayerSettings.Placement.OffsetFromPoint
    except Exception:
        try:
            settings.placement = QgsPalLayerSettings.OffsetFromPoint
        except Exception:
            try:
                settings.placement = QgsPalLayerSettings.Placement.AroundPoint
            except Exception:
                try:
                    settings.placement = QgsPalLayerSettings.AroundPoint
                except Exception:
                    pass
    try:
        settings.quadOffset = QgsPalLayerSettings.QuadrantRight
    except Exception:
        try:
            settings.quadOffset = QgsPalLayerSettings.Right
        except Exception:
            pass
    settings.dist = SEQ_ID_DIST_MIN
    settings.priority = 10
    try:
        settings.displayAll = False
    except Exception:
        pass

    text_format = QgsTextFormat()
    text_format.setFont(QFont('Arial', 4))
    text_format.setSize(SEQ_ID_SIZE_MIN)
    text_format.setColor(QColor(0, 0, 0))

    buffer = QgsTextBufferSettings()
    buffer.setEnabled(True)
    buffer.setSize(SEQ_ID_BUFFER_SIZE)
    buffer.setColor(QColor(255, 255, 255))
    text_format.setBuffer(buffer)
    settings.setFormat(text_format)

    tmp_imovel.setLabelsEnabled(True)
    tmp_imovel.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    tmp_imovel.triggerRepaint()



def _aplicar_textos_layout(layout, campos_layout):
    labels = [it for it in layout.items() if isinstance(it, QgsLayoutItemLabel)]
    if not labels:
        return

    labels.sort(key=lambda lb: lb.sceneBoundingRect().top())
    aliases = {
        'LOCAL': ['LOCAL', 'LOCAL DO SETOR', 'LOCALIDADE'],
        'DATA': ['DATA', 'DATA DO MAPA', 'DATA DE EMISSAO', 'DATA EMISSAO', 'DT'],
        'DESENHO': ['DESENHO', 'DESENHADO POR', 'DESENHADO_POR', 'ELABORADO POR', 'DESENHISTA'],
        'SETOR': ['SETOR', 'SETOR DE LEITURA', 'NUMERO DO SETOR'],
        'ROTA': ['ROTA', 'ROTA DE LEITURA', 'NUMERO DA ROTA'],
        'MUNICIPIO': ['MUNICIPIO', 'MUNICÍPIO', 'NOME DO MUNICIPIO'],
    }
    ordem_campos = [
        ('LOCAL', 'LOCAL'),
        ('SETOR', 'SETOR'),
        ('MUNICIPIO', 'MUNICÍPIO'),
        ('DESENHO', 'DESENHADO POR'),
        ('ROTA', 'ROTA'),
        ('DATA', 'DATA'),
    ]

    linhas_finais = []
    for chave, rotulo in ordem_campos:
        valor = (campos_layout.get(chave) or '').strip()
        if valor:
            linhas_finais.append(f'{rotulo}: {valor}')
    texto_completo = '\n'.join(linhas_finais)

    for lb in labels:
        txt_orig = lb.text() or ''
        if '\n' in txt_orig or _normalizar_campo_txt(txt_orig).startswith('LOCAL:'):
            lb.setText(texto_completo)
            layout.refresh()
            return

    usados = set()
    for chave, rotulo in ordem_campos:
        valor = (campos_layout.get(chave) or '').strip()
        if not valor:
            continue

        matched_lb = None
        matched_txt = None
        tokens_candidatos = set()
        for alias in aliases.get(chave, []):
            tokens_candidatos.add('{' + alias + '}')
            tokens_candidatos.add('{' + alias.replace(' ', '_') + '}')
            alias_norm = _normalizar_campo_txt(alias)
            tokens_candidatos.add('{' + alias_norm + '}')
            tokens_candidatos.add('{' + alias_norm.replace(' ', '_') + '}')

        for passo in range(4):
            for lb in labels:
                if id(lb) in usados:
                    continue
                txt = lb.text() or ''
                txt_norm = _normalizar_campo_txt(txt)

                if passo == 0:
                    novo = txt
                    for tok in tokens_candidatos:
                        if tok in novo:
                            novo = novo.replace(tok, valor)
                    if novo != txt:
                        matched_lb = lb
                        matched_txt = novo
                        break

                for alias in aliases.get(chave, []):
                    alias_norm = _normalizar_campo_txt(alias)
                    if passo == 1 and (txt_norm.startswith(alias_norm + ':') or txt_norm.startswith(alias_norm + ' :')):
                        matched_lb = lb
                        matched_txt = f'{rotulo}: {valor}'
                        break
                    if passo == 2 and txt_norm == alias_norm:
                        matched_lb = lb
                        matched_txt = f'{rotulo}: {valor}'
                        break
                    if passo == 3 and alias_norm in txt_norm and len(txt_norm) <= len(alias_norm) + 25:
                        matched_lb = lb
                        matched_txt = f'{rotulo}: {valor}'
                        break

                if matched_lb:
                    break
            if matched_lb:
                break

        if matched_lb:
            matched_lb.setText(matched_txt)
            usados.add(id(matched_lb))

    layout.refresh()


class BatchExportDialog(QDialog):
    def __init__(self, projeto, parent=None):
        super().__init__(parent)
        self.projeto = projeto
        self.setWindowTitle('Exportar rotas selecionadas')
        self.setMinimumWidth(560)
        self._build_ui()
        self._apply_style()
        self._preencher_defaults()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        titulo = QLabel('Exportação em lote de rotas')
        titulo.setObjectName('titulo')
        subtitulo = QLabel('Informe o template, as pastas de saída e os campos aplicados a todas as rotas selecionadas.')
        subtitulo.setWordWrap(True)
        subtitulo.setObjectName('subtitulo')
        root.addWidget(titulo)
        root.addWidget(subtitulo)

        linha = QFrame()
        linha.setFrameShape(QFrame.HLine)
        root.addWidget(linha)

        form_host = QWidget(self)
        form = QFormLayout(form_host)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setSpacing(10)

        self.input_qpt_retrato = self._build_path_field('Selecionar .qpt', self._pick_qpt_retrato)
        self.input_qpt_paisagem = self._build_path_field('Selecionar .qpt', self._pick_qpt_paisagem)
        self.input_pasta_qpt = self._build_path_field('Escolher pasta', self._pick_qpt_dir)
        self.input_pasta_pdf = self._build_path_field('Escolher pasta', self._pick_pdf_dir)
        self.input_localidade = QLineEdit()
        self.input_setor = QLineEdit()
        self.input_municipio = QLineEdit()

        form.addRow(self._make_form_label('Template QPT (Retrato):'), self.input_qpt_retrato['container'])
        form.addRow(self._make_form_label('Template QPT (Paisagem):'), self.input_qpt_paisagem['container'])
        form.addRow(self._make_form_label('Salvar QPTs em:'), self.input_pasta_qpt['container'])
        form.addRow(self._make_form_label('Salvar PDFs em:'), self.input_pasta_pdf['container'])
        form.addRow(self._make_form_label('Localidade:'), self.input_localidade)
        form.addRow(self._make_form_label('Setor:'), self.input_setor)
        form.addRow(self._make_form_label('Município:'), self.input_municipio)
        root.addWidget(form_host)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        ok_btn = botoes.button(QDialogButtonBox.Ok)
        ok_btn.setText('Executar')
        ok_btn.clicked.connect(self._validar)
        botoes.rejected.connect(self.reject)
        root.addWidget(botoes)

    def _build_path_field(self, button_text, callback):
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        inp = QLineEdit(container)
        btn = QPushButton(button_text, container)
        btn.clicked.connect(callback)
        layout.addWidget(inp, 1)
        layout.addWidget(btn)
        return {'container': container, 'input': inp, 'button': btn}

    def _make_form_label(self, texto):
        lb = QLabel(texto, self)
        lb.setStyleSheet('color: #ffffff; font-weight: 600;')
        return lb

    def _apply_style(self):
        self.setStyleSheet(
            """
            QDialog { background: #202124; }
            QWidget { color: #f5f6f7; }
            QDialog, QFormLayout, QWidget, QLabel { color: #f5f6f7; }
            QLabel#titulo { color: #ffffff; font-size: 16px; font-weight: 700; }
            QLabel#subtitulo { color: #c7c9cc; font-size: 11px; }
            QLineEdit {
                min-height: 34px;
                border: 1px solid #3f434a;
                border-radius: 8px;
                padding: 6px 10px;
                background: #2b2d31;
                color: #f5f6f7;
                selection-background-color: #2b7fff;
            }
            QLineEdit:focus { border: 1px solid #5aa2ff; }
            QPushButton {
                min-height: 34px;
                border: 0;
                border-radius: 8px;
                padding: 0 14px;
                background: #2b7fff;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover { background: #1f6ad4; }
            QPushButton:pressed { background: #1a59af; }
            QDialogButtonBox QPushButton { min-width: 110px; }
            QFrame { color: #3b3f45; }
            """
        )

    def _preencher_defaults(self):
        base = self.projeto.homePath() or os.path.expanduser('~')
        self.input_pasta_qpt['input'].setText(base)
        self.input_pasta_pdf['input'].setText(base)

    def _pick_qpt_retrato(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            'Selecione o arquivo de layout RETRATO (.qpt)',
            self.projeto.homePath() or os.path.expanduser('~'),
            'QGIS Layout Template (*.qpt)',
        )
        if caminho:
            self.input_qpt_retrato['input'].setText(caminho)
    
    def _pick_qpt_paisagem(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            'Selecione o arquivo de layout PAISAGEM (.qpt)',
            self.projeto.homePath() or os.path.expanduser('~'),
            'QGIS Layout Template (*.qpt)',
        )
        if caminho:
            self.input_qpt_paisagem['input'].setText(caminho)

    def _pick_qpt_dir(self):
        pasta = QFileDialog.getExistingDirectory(self, 'Escolha a pasta para salvar os QPTs', self.input_pasta_qpt['input'].text() or self.projeto.homePath() or os.path.expanduser('~'))
        if pasta:
            self.input_pasta_qpt['input'].setText(pasta)

    def _pick_pdf_dir(self):
        pasta = QFileDialog.getExistingDirectory(self, 'Escolha a pasta para salvar os PDFs', self.input_pasta_pdf['input'].text() or self.projeto.homePath() or os.path.expanduser('~'))
        if pasta:
            self.input_pasta_pdf['input'].setText(pasta)

    def _validar(self):
        qpt_retrato = self.input_qpt_retrato['input'].text().strip()
        qpt_paisagem = self.input_qpt_paisagem['input'].text().strip()
        pasta_qpt = self.input_pasta_qpt['input'].text().strip()
        pasta_pdf = self.input_pasta_pdf['input'].text().strip()
        
        # Pelo menos um template deve ser informado
        if not qpt_retrato and not qpt_paisagem:
            QMessageBox.warning(self, 'Validação', 'Selecione pelo menos um arquivo .qpt (retrato e/ou paisagem).')
            return
        
        if qpt_retrato and not os.path.exists(qpt_retrato):
            QMessageBox.warning(self, 'Validação', f'Arquivo QPT retrato não encontrado: {qpt_retrato}')
            return
        
        if qpt_paisagem and not os.path.exists(qpt_paisagem):
            QMessageBox.warning(self, 'Validação', f'Arquivo QPT paisagem não encontrado: {qpt_paisagem}')
            return
        
        if not pasta_qpt or not os.path.isdir(pasta_qpt):
            QMessageBox.warning(self, 'Validação', 'Informe uma pasta válida para os QPTs.')
            return
        if not pasta_pdf or not os.path.isdir(pasta_pdf):
            QMessageBox.warning(self, 'Validação', 'Informe uma pasta válida para os PDFs.')
            return
        self.accept()

    def values(self):
        return {
            'qpt_retrato': self.input_qpt_retrato['input'].text().strip(),
            'qpt_paisagem': self.input_qpt_paisagem['input'].text().strip(),
            'qpt_output_dir': self.input_pasta_qpt['input'].text().strip(),
            'pdf_output_dir': self.input_pasta_pdf['input'].text().strip(),
            'LOCAL': self.input_localidade.text().strip(),
            'SETOR': self.input_setor.text().strip(),
            'MUNICIPIO': self.input_municipio.text().strip(),
            'DATA': time.strftime('%d/%m/%Y'),
        }


def _unique_layout_name(layout_manager, base_name):
    existente = {lo.name() for lo in layout_manager.printLayouts()}
    if base_name not in existente:
        return base_name
    i = 2
    while True:
        nome = f'{base_name}_{i}'
        if nome not in existente:
            return nome
        i += 1


def _import_layout_from_qpt(projeto, qpt_path):
    if not os.path.exists(qpt_path):
        raise RuntimeError('Arquivo de layout .qpt nao encontrado.')

    dom = QDomDocument()
    with open(qpt_path, 'r', encoding='utf-8') as f:
        txt = f.read()
    if not dom.setContent(txt):
        raise RuntimeError('Nao foi possivel ler o conteudo do arquivo .qpt.')

    lm = projeto.layoutManager()
    nome_base = os.path.splitext(os.path.basename(qpt_path))[0] or 'Layout_Importado'
    nome_final = _unique_layout_name(lm, nome_base)

    layout = QgsPrintLayout(projeto)
    layout.initializeDefaults()
    layout.setName(nome_final)

    context = QgsReadWriteContext()
    _, ok = layout.loadFromTemplate(dom, context)
    if not ok:
        raise RuntimeError('Falha ao carregar template .qpt no layout.')

    layout.setName(nome_final)
    lm.addLayout(layout)
    return layout


def _salvar_layout_como_qpt_em(layout, destino):
    """Salva layout como QPT com compatibilidade entre versões do QGIS."""
    context = QgsReadWriteContext()
    context.setPathResolver(QgsProject.instance().pathResolver())

    # QGIS antigo/atual: preferir API do layout quando existir
    if hasattr(layout, 'saveAsTemplate'):
        resultado = layout.saveAsTemplate(destino, context)
        # Em algumas versões retorna bool, em outras pode retornar status numérico
        if isinstance(resultado, bool):
            if resultado:
                return
        else:
            if resultado in (None, 0):
                return

    # Algumas versões expõem exportToTemplate no exporter
    exporter = QgsLayoutExporter(layout)
    if hasattr(exporter, 'exportToTemplate'):
        resultado = exporter.exportToTemplate(destino, QgsLayoutExporter.LayoutExportSettings())
        if resultado == QgsLayoutExporter.Success:
            return

    # Fallback final: serialização XML manual
    doc = QDomDocument('qgis')
    root = doc.createElement('Layout')
    doc.appendChild(root)
    try:
        ok = layout.writeXml(root, doc, context)
    except TypeError:
        # Assinatura alternativa em versões diferentes
        ok = layout.writeXml(doc, context)

    if ok is False or doc.documentElement().isNull():
        raise RuntimeError(f'Falha ao salvar o layout como QPT em {destino}.')

    with open(destino, 'w', encoding='utf-8') as f:
        f.write(doc.toString(2))

    if not os.path.exists(destino) or os.path.getsize(destino) == 0:
        raise RuntimeError(f'QPT foi gerado vazio em {destino}.')


def _processar_eventos_ui():
    app = QApplication.instance()
    if app is not None:
        app.processEvents()


def _find_first_map_item(layout):
    mapas = [i for i in layout.items() if isinstance(i, QgsLayoutItemMap)]
    if not mapas:
        raise RuntimeError(f"Layout '{layout.name()}' nao possui item de mapa.")
    return mapas[0]


def _detectar_orientacao_melhor(geom_rota):
    """Detecta se a rota é melhor em retrato ou paisagem baseado no aspect ratio da bbox.
    
    Args:
        geom_rota: QgsGeometry da rota
    
    Returns:
        str: 'paisagem' se width > height, 'retrato' caso contrário
    """
    bbox = geom_rota.boundingBox()
    width = bbox.width()
    height = bbox.height()
    if width <= 0 or height <= 0:
        return 'paisagem'  # default
    aspect_ratio = width / height
    return 'paisagem' if aspect_ratio > 1.0 else 'retrato'


def _storage_dir_logo():
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not base:
        base = os.path.join(os.path.expanduser('~'), '.smartsync_qgis')
    pasta = os.path.join(base, 'assets')
    os.makedirs(pasta, exist_ok=True)
    return pasta


def _logo_salvo_valido():
    cfg = QSettings()
    p = cfg.value(SETTINGS_KEY_LOGO_CAEMA, '', type=str)
    return p if p and os.path.exists(p) else ''


def _escolher_e_salvar_logo_caema(projeto):
    origem, _ = QFileDialog.getOpenFileName(
        None,
        'Selecione o logo da CAEMA (sera salvo para uso automatico)',
        projeto.homePath() or os.path.expanduser('~'),
        'Imagens (*.png *.jpg *.jpeg *.bmp *.webp *.svg)',
    )
    if not origem:
        raise RuntimeError('Logo da CAEMA nao configurado. Selecione o logo ao menos uma vez para continuar.')

    ext = os.path.splitext(origem)[1].lower() or '.png'
    destino = os.path.join(_storage_dir_logo(), f'logo_caema{ext}')
    shutil.copy2(origem, destino)
    cfg = QSettings()
    cfg.setValue(SETTINGS_KEY_LOGO_CAEMA, destino)
    return destino


def _obter_logo_caema(projeto):
    logo = _logo_salvo_valido()
    return logo if logo else _escolher_e_salvar_logo_caema(projeto)


def _garantir_logo_caema_no_layout(layout, projeto):
    figuras = [it for it in layout.items() if isinstance(it, QgsLayoutItemPicture)]
    if not figuras:
        return
    figuras.sort(key=lambda it: (-it.sceneBoundingRect().bottom(), it.sceneBoundingRect().left()))
    item_logo = figuras[0]
    item_logo.setPicturePath(_obter_logo_caema(projeto))
    item_logo.refresh()
    layout.refresh()


def _expand_extent(extent, fator):
    dx = extent.width() * fator or 1.0
    dy = extent.height() * fator or 1.0
    extent.setXMinimum(extent.xMinimum() - dx)
    extent.setXMaximum(extent.xMaximum() + dx)
    extent.setYMinimum(extent.yMinimum() - dy)
    extent.setYMaximum(extent.yMaximum() + dy)
    return extent


def _slugify_texto(valor):
    txt = _normalizar_campo_txt(valor).replace(' ', '_')
    return ''.join(ch for ch in txt if ch.isalnum() or ch in ('_', '-')) or 'SEM_VALOR'


def _exportar_rota(projeto, layers_base, feat_rota, config_exportacao):
    layer_rota = layers_base['rota']
    geom_rota = feat_rota.geometry()
    if geom_rota is None or geom_rota.isEmpty():
        raise RuntimeError('Uma das rotas selecionadas nao possui geometria valida.')

    rota_label = _guess_rota_label(feat_rota)
    
    # Auto-detectar melhor orientação e carregar template apropriado
    orientacao = _detectar_orientacao_melhor(geom_rota)
    if orientacao == 'paisagem' and config_exportacao.get('qpt_paisagem'):
        qpt_path = config_exportacao['qpt_paisagem']
    elif orientacao == 'retrato' and config_exportacao.get('qpt_retrato'):
        qpt_path = config_exportacao['qpt_retrato']
    elif config_exportacao.get('qpt_paisagem'):
        qpt_path = config_exportacao['qpt_paisagem']
    elif config_exportacao.get('qpt_retrato'):
        qpt_path = config_exportacao['qpt_retrato']
    else:
        raise RuntimeError('Nenhum template QPT disponível para a rota.')
    
    layout = _import_layout_from_qpt(projeto, qpt_path)
    campos_layout = dict(config_exportacao)
    campos_layout['ROTA'] = rota_label
    _aplicar_textos_layout(layout, campos_layout)
    _garantir_logo_caema_no_layout(layout, projeto)
    _processar_eventos_ui()

    mapa_item = _find_first_map_item(layout)
    stamp = QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss_zzz')
    nome_base = f"tmp_rota_pdf_{_slugify_texto(rota_label)}_{stamp}"
    crs_rota = layer_rota.crs()

    tmp_rota = _build_route_layer(layer_rota, feat_rota, f'{nome_base}_ROTA')
    tmp_imovel = _clip_features_to_polygon(layers_base['imovel'], geom_rota, f'{nome_base}_IMOVEL', crs_rota)
    tmp_quadras = _clip_features_to_polygon(layers_base['quadras'], geom_rota, f'{nome_base}_QUADRAS', crs_rota)
    tmp_quadras_rotulo = _criar_camada_rotulo_quadras(tmp_quadras, f'{nome_base}_QUADRAS_ROT')
    tmp_overley = _clip_features_to_polygon(layers_base['overley'], geom_rota, f'{nome_base}_OVERLEY', crs_rota)
    tmp_inicio = _clip_features_to_polygon(layers_base['inicio'], geom_rota, f'{nome_base}_INICIO_PNT', crs_rota)
    tmp_fim = _clip_features_to_polygon(layers_base['fim'], geom_rota, f'{nome_base}_FIM_PNT', crs_rota)
    layer_arruamento = layers_base['arruamento']
    tmp_arruamento = _clip_features_to_polygon(layer_arruamento, geom_rota, f'{nome_base}_ARRUAMENTO', crs_rota) if layer_arruamento else None
    _processar_eventos_ui()

    _aplicar_estilo_preto_branco(tmp_quadras)
    _aplicar_estilo_preto_branco(tmp_imovel)
    _aplicar_estilo_preto_branco(tmp_inicio)
    _aplicar_estilo_preto_branco(tmp_fim)
    _aplicar_estilo_preto_branco(tmp_rota, papel='rota')
    if tmp_arruamento is not None:
        _aplicar_estilo_preto_branco(tmp_arruamento)

    # Usar camada ETIQUETAS_IMOVEL existente (gerada por tracarPerpendicularNasQuadras)
    etiq_source_layers = projeto.mapLayersByName(NOME_CAMADA_ETIQ)
    tmp_etiq = None
    camadas_imoveis_individuais = []
    if etiq_source_layers:
        tmp_etiq = _clip_features_to_polygon(
            etiq_source_layers[0], geom_rota, f'{nome_base}_ETIQ_IMOVEL', crs_rota
        )
        _configurar_camada_etiquetas_imovel(tmp_etiq)
    else:
        # Fallback: calcular e criar camadas individuais dinamicamente
        dados_imoveis = _calcular_dados_rotulos_imovel(tmp_imovel, tmp_quadras)
        camadas_imoveis_individuais = _criar_camadas_individuais_imovel(
            dados_imoveis,
            tmp_imovel.crs(),
            nome_base
        )
    
    if tmp_quadras_rotulo is None:
        _configurar_rotulos_quadras(tmp_quadras)
    else:
        # Evita duplicidade: rótulo da quadra fica apenas na camada dedicada de pontos.
        tmp_quadras.setLabelsEnabled(False)
        tmp_quadras.triggerRepaint()
    if tmp_arruamento is not None:
        _configurar_rotulos_arruamento(tmp_arruamento)

    projeto.addMapLayer(tmp_rota, False)
    # NÃO adicionar tmp_imovel ao projeto (será ocultada)
    projeto.addMapLayer(tmp_quadras, False)
    if tmp_quadras_rotulo is not None:
        projeto.addMapLayer(tmp_quadras_rotulo, False)
    projeto.addMapLayer(tmp_overley, False)
    projeto.addMapLayer(tmp_inicio, False)
    projeto.addMapLayer(tmp_fim, False)
    if tmp_arruamento is not None:
        projeto.addMapLayer(tmp_arruamento, False)

    # Adicionar camada de etiquetas ou camadas individuais de imóveis
    if tmp_etiq is not None:
        projeto.addMapLayer(tmp_etiq, False)
    else:
        for camada_imovel in camadas_imoveis_individuais:
            projeto.addMapLayer(camada_imovel, False)

    try:
        mapa_item.setKeepLayerSet(True)
        # IMOVEIS no topo de desenho para destacar pontos e rótulos seq_id.
        # Usar camadas individuais em vez de tmp_imovel
        camadas_layout = []
        if tmp_etiq is not None:
            camadas_layout.append(tmp_etiq)
        else:
            camadas_layout.extend(camadas_imoveis_individuais)
        camadas_layout.extend([tmp_quadras, tmp_inicio, tmp_fim])
        if tmp_quadras_rotulo is not None:
            camadas_layout.append(tmp_quadras_rotulo)
        if tmp_arruamento is not None:
            camadas_layout.append(tmp_arruamento)
        camadas_layout.append(tmp_overley)
        mapa_item.setLayers(camadas_layout)

        ext = _expand_extent(QgsGeometry(geom_rota).boundingBox(), MARGEM_ENQUADRAMENTO)
        if hasattr(mapa_item, 'zoomToExtent'):
            mapa_item.zoomToExtent(ext)
        else:
            mapa_item.setExtent(ext)
        mapa_item.refresh()

        nome_base_saida = f'Mapa_Rota_{_slugify_texto(rota_label)}'
        caminho_qpt = os.path.join(config_exportacao['qpt_output_dir'], nome_base_saida + '.qpt')
        caminho_pdf = os.path.join(config_exportacao['pdf_output_dir'], nome_base_saida + '.pdf')
        _salvar_layout_como_qpt_em(layout, caminho_qpt)
        _processar_eventos_ui()

        exporter = QgsLayoutExporter(layout)
        result = exporter.exportToPdf(caminho_pdf, QgsLayoutExporter.PdfExportSettings())
        if result != QgsLayoutExporter.Success:
            raise RuntimeError(f'Falha ao exportar o PDF da rota {rota_label}.')
        return {'rota': rota_label, 'pdf': caminho_pdf, 'qpt': caminho_qpt}
    finally:
        try:
            projeto.layoutManager().removeLayout(layout)
        except Exception:
            pass
        camadas_tmp = [tmp_rota, tmp_imovel, tmp_quadras, tmp_overley, tmp_inicio, tmp_fim]
        if tmp_quadras_rotulo is not None:
            camadas_tmp.append(tmp_quadras_rotulo)
        if tmp_arruamento is not None:
            camadas_tmp.append(tmp_arruamento)
        if tmp_etiq is not None:
            camadas_tmp.append(tmp_etiq)
        camadas_tmp.extend(camadas_imoveis_individuais)
        
        for lyr in camadas_tmp:
            try:
                projeto.removeMapLayer(lyr.id())
            except Exception:
                pass


def main():
    projeto = QgsProject.instance()
    layer_rota = _get_layer(NOME_CAMADA_ROTA)
    layer_imovel = _get_layer(NOME_CAMADA_IMOVEL)
    layer_quadras = _get_layer(NOME_CAMADA_QUADRAS)
    layer_overley = _get_layer(NOME_CAMADA_OVERLEY)
    layer_inicio = _get_layer(NOME_CAMADA_INICIO)
    layer_fim = _get_layer(NOME_CAMADA_FIM)
    try:
        layer_arruamento = _get_layer(NOME_CAMADA_ARRUAMENTO)
    except RuntimeError:
        layer_arruamento = None
        print(f"Camada '{NOME_CAMADA_ARRUAMENTO}' nao encontrada; arruamento sera omitido.")

    sel_rotas = list(layer_rota.selectedFeatures())
    if not sel_rotas:
        raise RuntimeError('Selecione uma ou mais rotas na camada de rotas antes de executar.')
    if QgsWkbTypes.geometryType(layer_rota.wkbType()) != QgsWkbTypes.PolygonGeometry:
        raise RuntimeError('A camada de rota precisa ser poligonal para usar recorte por rota.')

    dialog = BatchExportDialog(projeto)
    if dialog.exec_() != QDialog.Accepted:
        print('Operacao cancelada pelo usuario.')
        return

    config_exportacao = dialog.values()
    layers_base = {
        'rota': layer_rota,
        'imovel': layer_imovel,
        'quadras': layer_quadras,
        'overley': layer_overley,
        'inicio': layer_inicio,
        'fim': layer_fim,
        'arruamento': layer_arruamento,
    }

    resultados = []
    erros = []
    total = len(sel_rotas)
    progresso = QProgressDialog('Preparando exportação em lote...', 'Cancelar', 0, total, None)
    progresso.setWindowTitle('Exportação de Rotas')
    progresso.setWindowModality(Qt.ApplicationModal)
    progresso.setMinimumDuration(0)
    progresso.setValue(0)
    _processar_eventos_ui()

    for indice, feat_rota in enumerate(sel_rotas, 1):
        if progresso.wasCanceled():
            erros.append('Operação cancelada pelo usuário.')
            break
        rota_label = _guess_rota_label(feat_rota)
        progresso.setLabelText(f'[{indice}/{total}] Exportando rota {rota_label}...')
        progresso.setValue(indice - 1)
        _processar_eventos_ui()
        print(f'[{indice}/{total}] Exportando rota {rota_label}...')
        try:
            resultado = _exportar_rota(projeto, layers_base, feat_rota, config_exportacao)
            resultados.append(resultado)
            print(f"[{indice}/{total}] PDF: {resultado['pdf']}")
            print(f"[{indice}/{total}] QPT: {resultado['qpt']}")
        except Exception as exc:
            erros.append(f'Rota {rota_label}: {exc}')
            print(f'[{indice}/{total}] Erro na rota {rota_label}: {exc}')
        finally:
            progresso.setValue(indice)
            _processar_eventos_ui()

    progresso.close()

    if resultados and not erros:
        QMessageBox.information(
            None,
            'Exportação concluída',
            f'{len(resultados)} rota(s) exportada(s) com sucesso.\n\nPDFs: {config_exportacao["pdf_output_dir"]}\nQPTs: {config_exportacao["qpt_output_dir"]}',
        )
        return

    if resultados and erros:
        QMessageBox.warning(
            None,
            'Exportação concluída com ressalvas',
            f'{len(resultados)} rota(s) exportada(s) com sucesso e {len(erros)} falha(s).\n\n' + '\n'.join(erros[:10]),
        )
        return

    raise RuntimeError('Nenhuma rota foi exportada.\n' + '\n'.join(erros[:10]))


def _run_with_ui_feedback():
    try:
        print('Iniciando geracao de PDFs das rotas selecionadas...')
        main()
    except Exception as exc:
        msg = f'Erro: {exc}'
        print(msg)
        QMessageBox.critical(None, 'Erro na exportacao do PDF', msg)


def run():
    _run_with_ui_feedback()


def _auto_run():
    try:
        if __name__ in ('__main__', '__console__', 'builtins', '__builtin__'):
            _run_with_ui_feedback()
            return

        from qgis.utils import iface
        if iface is not None:
            _run_with_ui_feedback()
    except Exception:
        pass


_auto_run()
