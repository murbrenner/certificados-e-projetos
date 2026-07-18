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
import csv

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPolygon,
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
from qgis.PyQt.QtCore import QDateTime, QSettings, QStandardPaths, QVariant, Qt, QPointF
from qgis.PyQt.QtGui import QColor, QFont, QPolygonF
from qgis.PyQt.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
NOME_CAMADA_ARRUAMENTO = 'Ruas_MA'
NOME_CAMADA_ETIQ = 'ETIQUETAS_IMOVEL'
PASTA_MODELOS_QPT_PADRAO = '\\\\10.39.192.3\\OCRCC\\QGIS\\'
NOME_MODELO_QPT_RETRATO = 'MODELO_RETRATO_A3'
NOME_MODELO_QPT_PAISAGEM = 'MODELO_PAISAGEM_A3'

MARGEM_ENQUADRAMENTO = 0.03
DESLOCAMENTO_IMOVEL_M = 2.0
SETTINGS_KEY_LOGO_CAEMA = 'smartsync/layout/logo_caema_path'
APLICAR_DESLOCAMENTO_IMOVEL = True
IMOVEL_POINT_SIZE = 0.55
SEQ_ID_SIZE_BASE = 4.60
SEQ_ID_SIZE_MIN = 2.60
SEQ_ID_SIZE_MAX = 4.20
SEQ_ID_DIST_MIN = 0.01
SEQ_ID_DIST_MAX = 0.05
SEQ_ID_BUFFER_SIZE = 0.0
ARRUAMENTO_CLEARANCE_QUADRA_M = 0.25
NOMES_ELABORADO_POR = [
    'ALANA',
    'ANA PAULA',
    'GILSON',
    'GLEISON',
    'JEDERSON',
    'JULYANNE',
    'LUANA',
    'MURILO',
    'SERRA',
    'OUTRO...',
]


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
        marker_props = {
            'name': 'circle',
            'size': '1.6',
        }
        if papel == 'fim':
            marker_props.update({
                'color': '255,255,255,255',
                'outline_color': '0,0,0,255',
                'outline_width': '0.30',
            })
        else:
            marker_props.update({
                'color': '0,0,0,255',
                'outline_color': '0,0,0,255',
                'outline_width': '0.30',
            })
        symbol = QgsMarkerSymbol.createSimple(marker_props)

    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


def _aplicar_estilo_quadras_invisivel(layer):
    symbol = QgsFillSymbol.createSimple({
        'color': '255,255,255,0',
        'outline_color': '255,255,255,0',
        'outline_width': '0',
    })
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.triggerRepaint()


def _aplicar_estilo_invisivel(layer):
    geom_type = QgsWkbTypes.geometryType(layer.wkbType())

    if geom_type == QgsWkbTypes.PolygonGeometry:
        symbol = QgsFillSymbol.createSimple({
            'color': '255,255,255,0',
            'outline_color': '255,255,255,0',
            'outline_width': '0',
        })
    elif geom_type == QgsWkbTypes.LineGeometry:
        symbol = QgsLineSymbol.createSimple({
            'line_color': '255,255,255,0',
            'line_width': '0',
        })
    else:
        symbol = QgsMarkerSymbol.createSimple({
            'name': 'circle',
            'color': '255,255,255,0',
            'outline_color': '255,255,255,0',
            'size': '0',
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


def _normalizar_nome_pasta(nome, fallback='SEM_MUNICIPIO'):
    txt = (nome or '').strip()
    if not txt:
        txt = fallback
    invalidos = '<>:"/\\|?*'
    return ''.join('_' if ch in invalidos else ch for ch in txt).strip(' .') or fallback


def _resolver_caminho_localidades_csv(projeto):
    caminho_fixo = r'Z:\PYTHON\AUTOMAÇÃO QGIS\CSV\localidades.csv'
    if os.path.exists(caminho_fixo):
        print(f'LOCALIDADES.csv encontrado em: {caminho_fixo}')
        return caminho_fixo

    def _candidatos_por_ancora(ancora):
        if not ancora:
            return []
        ancora = os.path.abspath(ancora)
        pasta = ancora if os.path.isdir(ancora) else os.path.dirname(ancora)
        lista = []

        # Caminho esperado: .../PY/../CSV/LOCALIDADES.csv
        lista.append(os.path.join(pasta, '..', 'CSV', 'LOCALIDADES.csv'))
        lista.append(os.path.join(pasta, '..', 'CSV', 'localidades.csv'))

        # Fallbacks comuns
        lista.append(os.path.join(pasta, '..', 'LOCALIDADES.csv'))
        lista.append(os.path.join(pasta, 'CSV', 'LOCALIDADES.csv'))
        lista.append(os.path.join(pasta, 'AUTOMAÇÃO QGIS', 'CSV', 'LOCALIDADES.csv'))
        lista.append(os.path.join(pasta, 'AUTOMACAO QGIS', 'CSV', 'LOCALIDADES.csv'))

        # Sobe até 4 níveis procurando CSV/LOCALIDADES.csv
        atual = pasta
        for _ in range(4):
            lista.append(os.path.join(atual, 'CSV', 'LOCALIDADES.csv'))
            lista.append(os.path.join(atual, 'CSV', 'localidades.csv'))
            lista.append(os.path.join(atual, 'LOCALIDADES.csv'))
            atual_pai = os.path.dirname(atual)
            if atual_pai == atual:
                break
            atual = atual_pai

        return lista

    candidatos = []
    vistos = set()

    # 1) Caminho real do arquivo quando disponível
    file_path = globals().get('__file__')
    for p in _candidatos_por_ancora(file_path):
        ap = os.path.abspath(p)
        if ap not in vistos:
            vistos.add(ap)
            candidatos.append(ap)

    # 2) Diretório atual do processo (útil no console do QGIS)
    for p in _candidatos_por_ancora(os.getcwd()):
        ap = os.path.abspath(p)
        if ap not in vistos:
            vistos.add(ap)
            candidatos.append(ap)

    # 3) HomePath do projeto
    home = projeto.homePath() if projeto is not None else ''
    for p in _candidatos_por_ancora(home):
        ap = os.path.abspath(p)
        if ap not in vistos:
            vistos.add(ap)
            candidatos.append(ap)

    for p in candidatos:
        if os.path.exists(p):
            print(f'LOCALIDADES.csv encontrado em: {p}')
            return p

    # Fallback: busca por nome em diretórios âncora (sem depender da estrutura exata).
    diretorios_ancora = []
    for ancora in (globals().get('__file__'), os.getcwd(), projeto.homePath() if projeto is not None else ''):
        if not ancora:
            continue
        pasta = ancora if os.path.isdir(ancora) else os.path.dirname(ancora)
        pasta = os.path.abspath(pasta)
        if pasta and pasta not in diretorios_ancora:
            diretorios_ancora.append(pasta)
        pai = os.path.dirname(pasta)
        if pai and pai != pasta and pai not in diretorios_ancora:
            diretorios_ancora.append(pai)

    alvos = {'localidades.csv', 'LOCALIDADES.csv'}
    for base in diretorios_ancora:
        try:
            for raiz, _, arquivos in os.walk(base):
                for nome_arq in arquivos:
                    if nome_arq in alvos or nome_arq.lower() == 'localidades.csv':
                        encontrado = os.path.join(raiz, nome_arq)
                        print(f'LOCALIDADES.csv encontrado por busca automática em: {encontrado}')
                        return encontrado
        except Exception:
            continue

    print('Aviso: LOCALIDADES.csv não encontrado nas pastas esperadas.')
    return ''


def _resolver_template_qpt_padrao(pasta_base, nome_base):
    if not pasta_base or not nome_base:
        return ''

    candidatos = [
        os.path.join(pasta_base, nome_base + '.qpt'),
        os.path.join(pasta_base, nome_base + '.QPT'),
        os.path.join(pasta_base, nome_base),
    ]
    for caminho in candidatos:
        if os.path.isfile(caminho):
            return caminho

    try:
        for nome_arquivo in os.listdir(pasta_base):
            nome_sem_ext, ext = os.path.splitext(nome_arquivo)
            if _normalizar_campo_txt(nome_sem_ext) == _normalizar_campo_txt(nome_base) and ext.lower() == '.qpt':
                caminho = os.path.join(pasta_base, nome_arquivo)
                if os.path.isfile(caminho):
                    return caminho
    except Exception:
        return ''

    return ''


def _ler_localidades_csv(caminho_csv):
    if not caminho_csv or not os.path.exists(caminho_csv):
        return []

    aliases = {
        'GERENCIA': ('GERÊNCIA', 'GERENCIA', 'GERATRIZ'),
        'LOCALIDADE': ('NOME LOCALIDADE', 'LOCALIDADE', 'LOCAL', 'LOCAL DO SETOR', 'NOME DA LOCALIDADE'),
        'SETOR': ('SETORES', 'SETOR', 'SETOR DE LEITURA', 'NUMERO DO SETOR'),
        'ROTA': ('ROTA', 'ROTA DE LEITURA', 'NUMERO DA ROTA'),
        'MUNICIPIO': ('MUNICIPIO', 'MUNICÍPIO', 'NOME DO MUNICIPIO', 'MUNÍCIPIO', 'NOME LOCALIDADE', 'NOME DA LOCALIDADE'),
    }

    for encoding in ('utf-8-sig', 'latin-1'):
        try:
            with open(caminho_csv, 'r', encoding=encoding, newline='') as f:
                amostra = f.read(4096)
                f.seek(0)

                try:
                    dialect = csv.Sniffer().sniff(amostra, delimiters=';,\t|')
                    delimitador = dialect.delimiter
                except Exception:
                    delimitador = ';'

                reader = csv.DictReader(f, delimiter=delimitador)
                if not reader.fieldnames:
                    continue

                fieldnames = [str(n).strip() for n in reader.fieldnames]
                fieldnames_norm = [_normalizar_campo_txt(n) for n in fieldnames]

                idx_map = {}
                for campo_saida, cands in aliases.items():
                    idx = None
                    for cand in cands:
                        cand_norm = _normalizar_campo_txt(cand)
                        if cand_norm in fieldnames_norm:
                            idx = fieldnames_norm.index(cand_norm)
                            break
                    idx_map[campo_saida] = idx

                dados = []
                for row in reader:
                    rec = {}
                    for campo_saida in aliases.keys():
                        idx = idx_map.get(campo_saida)
                        if idx is None or idx >= len(fieldnames):
                            rec[campo_saida] = ''
                        else:
                            key = fieldnames[idx]
                            val = row.get(key, '')
                            rec[campo_saida] = str(val).strip() if val is not None else ''

                    if rec.get('LOCALIDADE') or rec.get('SETOR') or rec.get('ROTA'):
                        dados.append(rec)

                if dados:
                    print(f'LOCALIDADES.csv carregado com {len(dados)} registro(s).')
                    return dados
        except Exception:
            continue

    print('Aviso: nao foi possivel ler LOCALIDADES.csv ou as colunas esperadas não foram encontradas.')
    return []


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


def _intersecao_raio_segmento(ox, oy, dx, dy, ax, ay, bx, by):
    rx, ry = dx, dy
    sx, sy = bx - ax, by - ay
    qpx, qpy = ax - ox, ay - oy

    den = (rx * sy) - (ry * sx)
    if abs(den) < 1e-12:
        return None

    t = ((qpx * sy) - (qpy * sx)) / den
    u = ((qpx * ry) - (qpy * rx)) / den
    if t < 0.0 or u < 0.0 or u > 1.0:
        return None

    return ox + t * rx, oy + t * ry, t


def _configurar_camada_etiquetas_imovel(camada, tmp_quadras=None, ext=None, mapa_item=None):
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
        pal.dist = 0.0
    except Exception:
        pass

    try:
        pal.displayAll = True
    except Exception:
        try:
            pal.setDisplayAll(True)
        except Exception:
            pass

    pal.priority = 10

    # Prioriza maior tamanho e desloca posição ao longo da aresta para evitar conflito.
    _ajustar_etiquetas_priorizando_tamanho(camada, tmp_quadras, ext, mapa_item)

    campo_rot = _find_existing_field_name(camada, ('rotation_pdf', 'ROTATION_PDF', 'rotation', 'ROTATION'))
    dd = pal.dataDefinedProperties()
    if campo_rot:
        dd.setProperty(QgsPalLayerSettings.LabelRotation, QgsProperty.fromField(campo_rot))
    dd.setProperty(QgsPalLayerSettings.PositionX, QgsProperty.fromField('label_x_pdf'))
    dd.setProperty(QgsPalLayerSettings.PositionY, QgsProperty.fromField('label_y_pdf'))
    dd.setProperty(QgsPalLayerSettings.Size, QgsProperty.fromField('label_size'))
    try:
        dd.setProperty(QgsPalLayerSettings.Pinned, QgsProperty.fromExpression('true'))
    except Exception:
        pass
    pal.setDataDefinedProperties(dd)

    buf = QgsTextBufferSettings()
    buf.setEnabled(False)
    buf.setSize(0.0)

    fmt = QgsTextFormat()
    fmt.setFont(QFont('Arial', 4))
    fmt.setColor(QColor(0, 0, 0))
    fmt.setSize(SEQ_ID_SIZE_BASE)
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


def _aplicar_tamanho_dinamico_etiquetas(camada):
    """Cria/atualiza campo label_size para reduzir tamanho quando houver conflito."""
    campo_x = _find_existing_field_name(camada, ('label_x', 'LABEL_X'))
    campo_y = _find_existing_field_name(camada, ('label_y', 'LABEL_Y'))
    if not campo_x or not campo_y:
        return

    prov = camada.dataProvider()
    if 'label_size' not in camada.fields().names():
        prov.addAttributes([QgsField('label_size', QVariant.Double)])
        camada.updateFields()
    idx_size = camada.fields().indexFromName('label_size')

    coords = {}
    for f in camada.getFeatures():
        try:
            coords[f.id()] = (float(f[campo_x]), float(f[campo_y]))
        except Exception:
            continue

    updates = {}
    fids = list(coords.keys())
    for fid in fids:
        x, y = coords[fid]
        menor = None
        for ofid in fids:
            if ofid == fid:
                continue
            ox, oy = coords[ofid]
            d = math.hypot(x - ox, y - oy)
            if menor is None or d < menor:
                menor = d

        if menor is None:
            tam = 5.0
        elif menor < 1.5:
            tam = 3.2
        elif menor < 2.5:
            tam = 4.0
        else:
            tam = 5.0
        updates[fid] = {idx_size: tam}

    if updates:
        camada.startEditing()
        camada.dataProvider().changeAttributeValues(updates)
        camada.commitChanges()


def _aabb_rotulada(cx, cy, ang_deg, largura, altura):
    ar = math.radians(ang_deg)
    c = abs(math.cos(ar))
    s = abs(math.sin(ar))
    hx = (largura * c + altura * s) * 0.5
    hy = (largura * s + altura * c) * 0.5
    return (cx - hx, cy - hy, cx + hx, cy + hy)


def _sobrepoe(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def _area_sobreposicao(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return ix * iy


def _ajustar_etiquetas_priorizando_tamanho(camada, tmp_quadras, ext, mapa_item):
    """Mantém maior tamanho possível; ajusta posição em conflitos sem alterar
    a distância da etiqueta à aresta (deslocamento paralelo à aresta)."""
    campo_seq = _find_existing_field_name(camada, ('seq_id', 'SEQ_ID', 'seqid', 'SEQID'))
    campo_x = _find_existing_field_name(camada, ('label_x', 'LABEL_X'))
    campo_y = _find_existing_field_name(camada, ('label_y', 'LABEL_Y'))
    campo_rot = _find_existing_field_name(camada, ('rotation', 'ROTATION'))
    if not campo_seq or not campo_x or not campo_y or not campo_rot:
        return

    prov = camada.dataProvider()
    novos_campos = []
    if 'label_x_pdf' not in camada.fields().names():
        novos_campos.append(QgsField('label_x_pdf', QVariant.Double))
    if 'label_y_pdf' not in camada.fields().names():
        novos_campos.append(QgsField('label_y_pdf', QVariant.Double))
    if 'label_size' not in camada.fields().names():
        novos_campos.append(QgsField('label_size', QVariant.Double))
    if novos_campos:
        prov.addAttributes(novos_campos)
        camada.updateFields()

    idx_x = camada.fields().indexFromName('label_x_pdf')
    idx_y = camada.fields().indexFromName('label_y_pdf')
    idx_s = camada.fields().indexFromName('label_size')

    mu_por_mm = 1.0
    try:
        if mapa_item is not None and ext is not None:
            largura_mm = float(mapa_item.rect().width())
            if largura_mm > 0 and ext.width() > 0:
                mu_por_mm = ext.width() / largura_mm
    except Exception:
        mu_por_mm = 1.0
    mm_por_pt = 0.352777778

    dados = []
    for f in camada.getFeatures():
        try:
            dados.append({
                'fid': f.id(),
                'seq': str(f[campo_seq]),
                'x': float(f[campo_x]),
                'y': float(f[campo_y]),
                'rot': float(f[campo_rot]),
            })
        except Exception:
            continue

    dados.sort(key=lambda d: d['y'], reverse=True)
    caixas = []
    updates = {}

    quadras_por_id = {}
    idx_quadras = None
    if tmp_quadras is not None:
        quadras_por_id = {f.id(): f for f in tmp_quadras.getFeatures()}
        if quadras_por_id:
            idx_quadras = QgsSpatialIndex()
            for fq in quadras_por_id.values():
                idx_quadras.addFeature(fq)

    def _obter_quadra_referencia(pt_xy):
        if idx_quadras is None:
            return None
        eps = 1e-9
        rect = QgsRectangle(pt_xy.x() - eps, pt_xy.y() - eps, pt_xy.x() + eps, pt_xy.y() + eps)
        candidatos = list(idx_quadras.intersects(rect))
        if not candidatos:
            candidatos = idx_quadras.nearestNeighbor(pt_xy, 10)
        melhor = None
        melhor_d = float('inf')
        pt_geom = QgsGeometry.fromPointXY(pt_xy)
        for fid in candidatos:
            fq = quadras_por_id.get(fid)
            if fq is None:
                continue
            gq = fq.geometry()
            if gq is None or gq.isEmpty():
                continue
            try:
                if gq.contains(pt_geom) or gq.touches(pt_geom):
                    return fq
            except Exception:
                pass
            try:
                d = gq.distance(pt_geom)
            except Exception:
                d = float('inf')
            if d < melhor_d:
                melhor_d = d
                melhor = fq
        return melhor

    for d in dados:
        base_x, base_y = d['x'], d['y']
        theta = math.radians(-d['rot'])
        vx_in, vy_in = math.cos(theta), math.sin(theta)
        # vetor paralelo à aresta (deslocamento que preserva distância à aresta)
        tx, ty = -math.sin(theta), math.cos(theta)

        # Reancora etiqueta a 3.0m da aresta para que o ponto possa ficar a 1.5m da aresta
        # e a 1.5m da etiqueta, alinhados na normal da aresta.
        quadra_ref = _obter_quadra_referencia(QgsPointXY(base_x, base_y))
        if quadra_ref is not None:
            gq = quadra_ref.geometry()
            melhor_inter = None
            for p1, p2 in _segmentos_da_geometria_poligono(gq):
                inter = _intersecao_raio_segmento(base_x, base_y, -vx_in, -vy_in, p1.x(), p1.y(), p2.x(), p2.y())
                if inter is None:
                    continue
                if melhor_inter is None or inter[2] < melhor_inter[2]:
                    melhor_inter = inter
            if melhor_inter is not None:
                ix, iy, _ = melhor_inter
                base_x = ix + vx_in * 3.0
                base_y = iy + vy_in * 3.0

        melhor = None
        menor_area = None
        tamanhos = [SEQ_ID_SIZE_BASE, 4.4, 4.2, 4.0, 3.8, 3.6]
        desloc_idx = [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]

        for tam in tamanhos:
            alt = tam * mm_por_pt * mu_por_mm
            lar = max(alt * 1.2, len(d['seq']) * tam * 0.56 * mm_por_pt * mu_por_mm)
            passo = max(alt * 0.9, 0.4)

            for k in desloc_idx:
                cx = base_x + tx * (passo * k)
                cy = base_y + ty * (passo * k)
                caixa = _aabb_rotulada(cx, cy, -d['rot'], lar, alt)

                if all(not _sobrepoe(caixa, c) for c in caixas):
                    melhor = (cx, cy, tam, caixa)
                    menor_area = 0.0
                    break

                area = 0.0
                for c in caixas:
                    area += _area_sobreposicao(caixa, c)
                if menor_area is None or area < menor_area:
                    menor_area = area
                    melhor = (cx, cy, tam, caixa)
            if menor_area == 0.0:
                break

        if melhor is None:
            continue

        cx, cy, tam, caixa = melhor
        updates[d['fid']] = {
            idx_x: cx,
            idx_y: cy,
            idx_s: tam,
        }
        caixas.append(caixa)

    if updates:
        camada.startEditing()
        camada.dataProvider().changeAttributeValues(updates)
        camada.commitChanges()


def _criar_camada_pontos_imovel_proximos(tmp_etiq, tmp_quadras, nome_saida):
    """Exibe pontos do IMÓVEL alinhados à etiqueta final.
    O ponto é derivado da âncora final da etiqueta e da rotação para eliminar
    qualquer desalinhamento visual entre ponto e texto."""
    camada = QgsVectorLayer(f"Point?crs={tmp_etiq.crs().authid()}", nome_saida, 'memory')
    prov = camada.dataProvider()
    prov.addAttributes([QgsField('seq_id', QVariant.String)])
    camada.updateFields()

    campo_seq = _find_existing_field_name(tmp_etiq, ('seq_id', 'SEQ_ID', 'seqid', 'SEQID'))
    campo_x = _find_existing_field_name(tmp_etiq, ('label_x_pdf', 'LABEL_X_PDF', 'label_x', 'LABEL_X'))
    campo_y = _find_existing_field_name(tmp_etiq, ('label_y_pdf', 'LABEL_Y_PDF', 'label_y', 'LABEL_Y'))
    campo_rot = _find_existing_field_name(tmp_etiq, ('rotation_pdf', 'ROTATION_PDF', 'rotation', 'ROTATION'))
    if not campo_x or not campo_y or not campo_rot:
        return camada

    novos = []
    for f in tmp_etiq.getFeatures():
        try:
            lx, ly = float(f[campo_x]), float(f[campo_y])
            rot = float(f[campo_rot])
        except Exception:
            continue

        theta = math.radians(-rot)
        vx_in, vy_in = math.cos(theta), math.sin(theta)

        # Mantém alinhamento perfeito com a etiqueta: ponto na mesma normal,
        # deslocado 1.5m em direção à aresta.
        px = lx - (vx_in * 1.5)
        py = ly - (vy_in * 1.5)

        nf = QgsFeature(camada.fields())
        nf.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(px, py)))
        if campo_seq:
            try:
                nf.setAttribute('seq_id', str(f[campo_seq]))
            except Exception:
                nf.setAttribute('seq_id', '')
        novos.append(nf)

    if novos:
        prov.addFeatures(novos)
    camada.updateExtents()

    symbol_pt = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': '0,0,0,255',
        'outline_color': '0,0,0,255',
        'outline_width': '0.30',
        'size': str(IMOVEL_POINT_SIZE),
    })
    camada.setRenderer(QgsSingleSymbolRenderer(symbol_pt))
    camada.setLabelsEnabled(False)
    camada.triggerRepaint()
    return camada


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
    fonte_quadras.setUnderline(True)
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
    fonte.setUnderline(True)
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


def _clip_arruamento_excluding_quadras(tmp_arruamento, tmp_quadras):
    """Remove trechos do arruamento dentro e muito próximos das quadras.
    Isso impede rótulos de rua sobre polígonos de quadra."""
    if tmp_arruamento is None:
        return None

    layer_out = _new_memory_like(tmp_arruamento, tmp_arruamento.name())
    prov = layer_out.dataProvider()

    idx_q = QgsSpatialIndex()
    quadras_geoms = {}
    for feat_q in tmp_quadras.getFeatures():
        g = feat_q.geometry()
        if g is None or g.isEmpty():
            continue
        idx_q.addFeature(feat_q)
        quadras_geoms[feat_q.id()] = g

    novos = []
    for feat in tmp_arruamento.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue

        candidatos = idx_q.intersects(geom.boundingBox())
        geom_result = QgsGeometry(geom)
        for fid in candidatos:
            gq = quadras_geoms.get(fid)
            if gq is None:
                continue
            try:
                if not geom_result.intersects(gq):
                    continue
            except Exception:
                continue

            # Usa buffer POSITIVO para criar uma faixa de segurança fora da quadra,
            # evitando que o rótulo de rua seja colocado por cima do polígono.
            try:
                gq_cut = gq.buffer(ARRUAMENTO_CLEARANCE_QUADRA_M, 8)
                if gq_cut is None or gq_cut.isEmpty():
                    gq_cut = gq
            except Exception:
                gq_cut = gq

            try:
                diff = geom_result.difference(gq_cut)
                geom_result = diff if (diff is not None and not diff.isEmpty()) else None
            except Exception:
                pass

            if geom_result is None or geom_result.isEmpty():
                break

        if geom_result is None or geom_result.isEmpty():
            continue

        nf = QgsFeature(layer_out.fields())
        nf.setAttributes(feat.attributes())
        nf.setGeometry(geom_result)
        novos.append(nf)

    if novos:
        prov.addFeatures(novos)
    layer_out.updateExtents()
    _copiar_estilo(tmp_arruamento, layer_out)
    return layer_out


def _configurar_rotulos_arruamento(tmp_arruamento):
    campo_tipo = _find_existing_field_name(tmp_arruamento, ('nm_tip_log', 'NM_TIP_LOG'))
    campo_nome = _find_existing_field_name(
        tmp_arruamento,
        (
            'nm_log',
            'NM_LOG',
            'name',
            'NAME',
            'nome',
            'NOME',
            'nm_logradouro',
            'NM_LOGRADOURO',
            'nome_logradouro',
            'NOME_LOGRADOURO',
            'logradouro',
            'LOGRADOURO',
            'ds_logradouro',
            'DS_LOGRADOURO',
        ),
    )
    if not campo_tipo and not campo_nome:
        print('Campo de nome da rua nao encontrado em Ruas_MA; rotulos nao foram aplicados.')
        return

    # Mantém as linhas visíveis (estilo já aplicado em _aplicar_estilo_preto_branco)
    # e configura apenas a rotulagem aqui.

    settings = QgsPalLayerSettings()
    settings.enabled = True
    if campo_tipo and campo_nome:
        settings.fieldName = (
            f"trim(regexp_replace(concat(coalesce(\"{campo_tipo}\", ''), ' ', coalesce(\"{campo_nome}\", '')), '\\s+', ' '))"
        )
        settings.isExpression = True
    elif campo_nome:
        settings.fieldName = campo_nome
        settings.isExpression = False
    else:
        settings.fieldName = campo_tipo
        settings.isExpression = False
    try:
        settings.placement = QgsPalLayerSettings.Placement.Line
    except Exception:
        try:
            settings.placement = QgsPalLayerSettings.Line
        except Exception:
            settings.placement = 3
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
    text_format.setFont(QFont('Arial', 6))
    text_format.setSize(6.0)
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


def _criar_camada_rotulo_arruamento_externo(tmp_arruamento, tmp_quadras, nome_saida):
    """Cria pontos de rótulo de rua somente fora das quadras."""
    if tmp_arruamento is None:
        return None

    campo_tipo = _find_existing_field_name(tmp_arruamento, ('nm_tip_log', 'NM_TIP_LOG'))
    campo_nome = _find_existing_field_name(
        tmp_arruamento,
        ('nm_log', 'NM_LOG', 'nm_logradouro', 'NM_LOGRADOURO', 'nome_logradouro', 'NOME_LOGRADOURO'),
    )
    if not campo_tipo and not campo_nome:
        return None

    camada = QgsVectorLayer(f"Point?crs={tmp_arruamento.crs().authid()}", nome_saida, 'memory')
    prov = camada.dataProvider()
    prov.addAttributes([
        QgsField('lbl_txt', QVariant.String),
        QgsField('lbl_x', QVariant.Double),
        QgsField('lbl_y', QVariant.Double),
    ])
    camada.updateFields()

    quadras_buf = []
    for fq in tmp_quadras.getFeatures():
        gq = fq.geometry()
        if gq is None or gq.isEmpty():
            continue
        try:
            gbuf = gq.buffer(ARRUAMENTO_CLEARANCE_QUADRA_M, 8)
            if gbuf is None or gbuf.isEmpty():
                gbuf = gq
        except Exception:
            gbuf = gq
        quadras_buf.append(gbuf)

    try:
        union_quadras_buf = QgsGeometry.unaryUnion(quadras_buf) if quadras_buf else None
    except Exception:
        union_quadras_buf = None

    def _ponto_rotulo_fora_quadra(geom_linha, union_quadras):
        if geom_linha is None or geom_linha.isEmpty():
            return None
        try:
            comp = geom_linha.length()
        except Exception:
            comp = 0.0
        if comp <= 0.0:
            return None

        fracoes = (0.50, 0.35, 0.65, 0.20, 0.80, 0.10, 0.90)
        for fr in fracoes:
            try:
                pt = geom_linha.interpolate(comp * fr)
            except Exception:
                pt = None
            if pt is None or pt.isEmpty():
                continue

            if union_quadras is None or union_quadras.isEmpty():
                return pt

            try:
                dentro = union_quadras.contains(pt) or union_quadras.intersects(pt)
            except Exception:
                dentro = False
            if not dentro:
                return pt

        return None

    novos = []
    for fa in tmp_arruamento.getFeatures():
        try:
            tipo = str(fa[campo_tipo]).strip() if campo_tipo else ''
        except Exception:
            tipo = ''
        try:
            nome = str(fa[campo_nome]).strip() if campo_nome else ''
        except Exception:
            nome = ''
        txt_rotulo = ' '.join(p for p in (tipo, nome) if p).strip()
        if not txt_rotulo:
            continue

        ga = fa.geometry()
        if ga is None or ga.isEmpty():
            continue

        pt_escolhido = _ponto_rotulo_fora_quadra(ga, union_quadras_buf)

        if pt_escolhido is None:
            continue
        if pt_escolhido.isEmpty():
            continue

        pt_xy = pt_escolhido.asPoint()

        nf = QgsFeature(camada.fields())
        nf.setGeometry(pt_escolhido)
        nf.setAttribute('lbl_txt', txt_rotulo)
        nf.setAttribute('lbl_x', float(pt_xy.x()))
        nf.setAttribute('lbl_y', float(pt_xy.y()))
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
    settings.fieldName = 'lbl_txt'
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
        pass

    try:
        dd = settings.dataDefinedProperties()
        dd.setProperty(QgsPalLayerSettings.Pinned, QgsProperty.fromExpression('true'))
        settings.setDataDefinedProperties(dd)
    except Exception:
        pass

    text_format = QgsTextFormat()
    fonte_rua = QFont('Arial', 6)
    fonte_rua.setBold(True)
    text_format.setFont(fonte_rua)
    text_format.setSize(4.2)
    text_format.setColor(QColor(0, 0, 0))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(0.35)
    buf.setColor(QColor(255, 255, 255))
    text_format.setBuffer(buf)
    settings.setFormat(text_format)

    camada.setLabelsEnabled(True)
    camada.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    camada.triggerRepaint()
    return camada


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
        buffer.setEnabled(False)
        buffer.setSize(0.0)
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
    buffer.setEnabled(False)
    buffer.setSize(0.0)
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
        'LOCALIDADE': ['LOCAL', 'LOCAL DO SETOR', 'LOCALIDADE', 'NOME LOCALIDADE'],
        'DATA': ['DATA', 'DATA DO MAPA', 'DATA DE EMISSAO', 'DATA EMISSAO', 'DT'],
        'ELABORADO POR': ['DESENHO', 'DESENHADO POR', 'DESENHADO_POR', 'ELABORADO POR', 'DESENHISTA'],
        'SETOR': ['SETOR', 'SETOR DE LEITURA', 'NUMERO DO SETOR'],
        'ROTA': ['ROTA', 'ROTA DE LEITURA', 'NUMERO DA ROTA'],
        'MUNICIPIO': ['MUNICIPIO', 'MUNICÍPIO', 'NOME DO MUNICIPIO', 'NOME LOCALIDADE'],
    }
    ordem_campos = [
        ('LOCALIDADE', 'LOCALIDADE'),
        ('SETOR', 'SETOR'),
        ('ROTA', 'ROTA'),
        ('MUNICIPIO', 'MUNICÍPIO'),
        ('ELABORADO POR', 'ELABORADO POR'),
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
        txt_norm = _normalizar_campo_txt(txt_orig)
        if '\n' in txt_orig or txt_norm.startswith('LOCAL:') or txt_norm.startswith('LOCALIDADE:'):
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
    def __init__(self, projeto, rotas_selecionadas=None, parent=None):
        super().__init__(parent)
        self.projeto = projeto
        self._rotas_selecionadas = list(rotas_selecionadas or [])
        self._dados_localidades = []
        self._base_area_trabalho = ''
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

        self.input_exibir_imovel_etiq = QCheckBox('Exibir IMÓVEL e ETIQUETAS_IMOVEL (quando existirem)')
        self.input_exibir_imovel_etiq.setChecked(True)

        self.input_qpt_retrato = self._build_path_field('Selecionar .qpt', self._pick_qpt_retrato)
        self.input_qpt_paisagem = self._build_path_field('Selecionar .qpt', self._pick_qpt_paisagem)
        self.input_pasta_qpt = self._build_path_field('Escolher pasta', self._pick_qpt_dir)
        self.input_pasta_pdf = self._build_path_field('Escolher pasta', self._pick_pdf_dir)
        self.input_localidade = QComboBox()
        self.input_localidade.setEditable(True)
        self.input_gerencia = QComboBox()
        self.input_gerencia.setEditable(True)
        self.input_setor = QComboBox()
        self.input_setor.setEditable(True)
        self.input_rota = QLineEdit()
        self.input_rota.setReadOnly(True)
        self.input_rota.setPlaceholderText("Preenchido a partir do atributo 'rota' da camada ROTAS DE LEITURA")
        self.input_rota.clear()
        self.input_municipio = QLineEdit()
        self.input_municipio.setReadOnly(True)
        self.input_elaborado_por = QComboBox()
        self.input_elaborado_por.addItems(NOMES_ELABORADO_POR)
        self.input_elaborado_outro = QLineEdit()
        self.input_elaborado_outro.setPlaceholderText('Digite o nome')
        self.input_elaborado_outro.setVisible(False)

        self.container_elaborado = QWidget(self)
        layout_elaborado = QHBoxLayout(self.container_elaborado)
        layout_elaborado.setContentsMargins(0, 0, 0, 0)
        layout_elaborado.setSpacing(8)
        layout_elaborado.addWidget(self.input_elaborado_por, 1)
        layout_elaborado.addWidget(self.input_elaborado_outro, 1)

        self.input_data = QLineEdit()
        self.input_data.setPlaceholderText('dd/mm/aaaa')

        form.addRow(self._make_form_label('Exibir camadas:'), self.input_exibir_imovel_etiq)
        form.addRow(self._make_form_label('Template QPT (Retrato):'), self.input_qpt_retrato['container'])
        form.addRow(self._make_form_label('Template QPT (Paisagem):'), self.input_qpt_paisagem['container'])
        self.label_localidade = self._make_form_label('Localidade:')
        form.addRow(self.label_localidade, self.input_localidade)
        
        self.container_gerencia = QWidget(self)
        layout_gerencia = QHBoxLayout(self.container_gerencia)
        layout_gerencia.setContentsMargins(0, 0, 0, 0)
        layout_gerencia.addWidget(self.input_gerencia)
        self.label_gerencia = self._make_form_label('Gerência:')
        form.addRow(self.label_gerencia, self.container_gerencia)
        self.label_gerencia.setVisible(False)
        self.container_gerencia.setVisible(False)
        
        form.addRow(self._make_form_label('Setor:'), self.input_setor)
        form.addRow(self._make_form_label('Rota:'), self.input_rota)
        form.addRow(self._make_form_label('Município:'), self.input_municipio)
        form.addRow(self._make_form_label('Elaborado por:'), self.container_elaborado)
        form.addRow(self._make_form_label('Data:'), self.input_data)
        form.addRow(self._make_form_label('Salvar QPTs em:'), self.input_pasta_qpt['container'])
        form.addRow(self._make_form_label('Salvar PDFs em:'), self.input_pasta_pdf['container'])
        root.addWidget(form_host)

        self.input_municipio.textChanged.connect(self._atualizar_pastas_saida_por_municipio)
        self.input_setor.currentTextChanged.connect(self._atualizar_pastas_saida_por_municipio)
        self.input_localidade.currentTextChanged.connect(self._atualizar_gerencias_por_localidade)
        self.input_gerencia.currentTextChanged.connect(self._atualizar_municipio_por_localidade_gerencia)
        self.input_gerencia.currentTextChanged.connect(self._atualizar_setores_por_localidade_gerencia)
        self.input_elaborado_por.currentTextChanged.connect(self._ao_mudar_elaborado_por)

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
        lb.setStyleSheet('color: #334155; font-weight: 600; background: transparent;')
        return lb

    def _apply_style(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #f5f7fb;
                color: #1f2937;
                font-family: "Segoe UI";
                font-size: 9pt;
            }
            QDialog { background: #f5f7fb; }
            QLabel { background: transparent; }
            QLabel#titulo { color: #0f172a; font-size: 16px; font-weight: 700; }
            QLabel#subtitulo { color: #526077; font-size: 11px; }
            QLineEdit {
                min-height: 34px;
                border: 1px solid #d1d9e6;
                border-radius: 8px;
                padding: 6px 10px;
                background: #ffffff;
                color: #1f2937;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
            }
            QLineEdit:focus { border: 1px solid #3b82f6; }
            QComboBox {
                min-height: 34px;
                border: 1px solid #d1d9e6;
                border-radius: 8px;
                padding: 4px 10px;
                background: #ffffff;
                color: #1f2937;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border-left: 1px solid #d1d9e6;
                background: #f8fafc;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
            QComboBox::drop-down:hover { background: #eef4ff; }
            QComboBox:focus { border: 1px solid #3b82f6; }
            QComboBox QAbstractItemView {
                background: #ffffff;
                color: #1f2937;
                border: 1px solid #d1d9e6;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #0078d7;
                color: #ffffff;
            }
            QPushButton {
                min-height: 34px;
                border: 1px solid #d1d9e6;
                border-radius: 8px;
                padding: 0 14px;
                background: #e9eef7;
                color: #1e3a5f;
                font-weight: 600;
            }
            QPushButton:hover { background: #dde7f5; }
            QPushButton:pressed { background: #d3def0; }
            QDialogButtonBox QPushButton { min-width: 110px; }
            QFrame { color: #dbe2ef; background: #dbe2ef; }
            """
        )

    def _preencher_defaults(self):
        self._base_area_trabalho = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        if not self._base_area_trabalho:
            self._base_area_trabalho = self.projeto.homePath() or os.path.expanduser('~')

        qpt_retrato_padrao = _resolver_template_qpt_padrao(PASTA_MODELOS_QPT_PADRAO, NOME_MODELO_QPT_RETRATO)
        qpt_paisagem_padrao = _resolver_template_qpt_padrao(PASTA_MODELOS_QPT_PADRAO, NOME_MODELO_QPT_PAISAGEM)
        if qpt_retrato_padrao and not self.input_qpt_retrato['input'].text().strip():
            self.input_qpt_retrato['input'].setText(qpt_retrato_padrao)
        if qpt_paisagem_padrao and not self.input_qpt_paisagem['input'].text().strip():
            self.input_qpt_paisagem['input'].setText(qpt_paisagem_padrao)

        self._atualizar_pastas_saida_por_municipio()
        self.input_data.setText(time.strftime('%d/%m/%Y'))
        self._preencher_rota_por_selecao()
        self._preencher_localidade_setor_por_planilha()

    def _preencher_rota_por_selecao(self):
        rotas = []
        for feat_rota in self._rotas_selecionadas:
            rota_label = str(_guess_rota_label(feat_rota)).strip()
            if rota_label and rota_label not in rotas:
                rotas.append(rota_label)

        self.input_rota.blockSignals(True)
        if rotas:
            self.input_rota.setText(', '.join(rotas))
            self.input_rota.setToolTip(', '.join(rotas))
        else:
            self.input_rota.clear()
            self.input_rota.setToolTip('')
        self.input_rota.blockSignals(False)

    def _preencher_municipio_por_localidade(self, gerencia_txt=''):
        localidade = _normalizar_campo_txt(self.input_localidade.currentText())
        gerencia = _normalizar_campo_txt(gerencia_txt)
        if not localidade:
            self.input_municipio.blockSignals(True)
            self.input_municipio.clear()
            self.input_municipio.blockSignals(False)
            self._atualizar_pastas_saida_por_municipio()
            return []

        matches = [
            r for r in self._dados_localidades
            if _normalizar_campo_txt(r.get('LOCALIDADE', '')) == localidade
            and (not gerencia or _normalizar_campo_txt(r.get('GERENCIA', '')) == gerencia)
        ]

        municipios = sorted(set(
            r.get('MUNICIPIO', '').strip()
            for r in matches
            if r.get('MUNICIPIO', '').strip()
        ))

        self.input_municipio.blockSignals(True)
        if len(municipios) == 1:
            self.input_municipio.setText(municipios[0])
        else:
            self.input_municipio.clear()
        self.input_municipio.blockSignals(False)
        self._atualizar_pastas_saida_por_municipio()
        return matches

    def _pick_qpt_retrato(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            'Selecione o arquivo de layout RETRATO (.qpt)',
            self.input_qpt_retrato['input'].text().strip() or PASTA_MODELOS_QPT_PADRAO or self.projeto.homePath() or os.path.expanduser('~'),
            'QGIS Layout Template (*.qpt)',
        )
        if caminho:
            self.input_qpt_retrato['input'].setText(caminho)
    
    def _pick_qpt_paisagem(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            'Selecione o arquivo de layout PAISAGEM (.qpt)',
            self.input_qpt_paisagem['input'].text().strip() or PASTA_MODELOS_QPT_PADRAO or self.projeto.homePath() or os.path.expanduser('~'),
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

    def _ao_mudar_elaborado_por(self, texto):
        eh_outro = _normalizar_campo_txt(texto) == 'OUTRO...'
        self.input_elaborado_outro.setVisible(eh_outro)
        if eh_outro:
            self.input_elaborado_outro.setFocus()

    def _atualizar_pastas_saida_por_municipio(self, *_):
        base = self._base_area_trabalho or self.projeto.homePath() or os.path.expanduser('~')
        municipio_txt = self.input_municipio.text().strip()
        if not municipio_txt:
            # Aguarda o preenchimento do município para montar os caminhos automáticos.
            self.input_pasta_qpt['input'].setText('')
            self.input_pasta_pdf['input'].setText('')
            return
        municipio = _normalizar_nome_pasta(municipio_txt, 'SEM_MUNICIPIO')
        pasta_base = os.path.join(base, municipio)
        setor_txt = self.input_setor.currentText().strip()
        if setor_txt:
            setor_nome = _normalizar_nome_pasta(f'SETOR {setor_txt}', 'SETOR_SEM_NUMERO')
            pasta_base = os.path.join(pasta_base, setor_nome)
        self.input_pasta_qpt['input'].setText(os.path.join(pasta_base, 'ARQUIVOS QPT'))
        self.input_pasta_pdf['input'].setText(os.path.join(pasta_base, 'ROTAS PDF'))

    def _dados_localidades_filtrados(self):
        if not self._dados_localidades:
            return []
        return list(self._dados_localidades)

    def _preencher_localidade_setor_por_planilha(self):
        caminho_csv = _resolver_caminho_localidades_csv(self.projeto)
        self._dados_localidades = _ler_localidades_csv(caminho_csv)
        if not self._dados_localidades:
            return

        self._atualizar_localidades_por_municipio()

    def _atualizar_localidades_por_municipio(self, *_):
        if not self._dados_localidades:
            return

        dados = self._dados_localidades_filtrados()
        localidades = sorted({r.get('LOCALIDADE', '').strip() for r in dados if r.get('LOCALIDADE', '').strip()})
        atual = self.input_localidade.currentText().strip()

        self.input_localidade.blockSignals(True)
        self.input_localidade.clear()
        if localidades:
            self.input_localidade.setEditable(False)
            self.input_localidade.addItems(localidades)
            if atual in localidades:
                self.input_localidade.setCurrentText(atual)
            else:
                self.input_localidade.setCurrentIndex(0)
        else:
            self.input_localidade.setEditable(True)
            self.input_localidade.setCurrentText(atual)
        self.input_localidade.blockSignals(False)

        # Propaga a cascata mesmo quando os sinais ficaram bloqueados durante o preenchimento.
        self._atualizar_gerencias_por_localidade()

    def _atualizar_gerencias_por_localidade(self, *_):
        """Quando usuário escolhe LOCALIDADE, preenche o combo de GERÊNCIA com as gerências disponíveis"""
        if not self._dados_localidades:
            return

        localidade = _normalizar_campo_txt(self.input_localidade.currentText())
        if not localidade:
            self.input_gerencia.blockSignals(True)
            self.input_gerencia.clear()
            self.input_gerencia.blockSignals(False)
            self.input_municipio.blockSignals(True)
            self.input_municipio.clear()
            self.input_municipio.blockSignals(False)
            self._preencher_rota_por_selecao()
            return

        matches = self._preencher_municipio_por_localidade()
        self._preencher_rota_por_selecao()
        
        # Extrai gerências únicas
        gerencias = sorted(set(
            r.get('GERENCIA', '').strip()
            for r in matches
            if r.get('GERENCIA', '').strip()
        ))

        self.input_gerencia.blockSignals(True)
        self.input_gerencia.clear()
        
        if len(gerencias) > 1:
            # Múltiplas gerências: mostrar combo com opções
            self.input_gerencia.setEditable(False)
            self.input_gerencia.addItems(gerencias)
        else:
            # Uma única gerência: preencher automaticamente
            self.input_gerencia.setEditable(True)
            if gerencias:
                self.input_gerencia.addItem(gerencias[0])
                self.input_gerencia.setCurrentText(gerencias[0])
        
        self.input_gerencia.blockSignals(False)

        # Mostrar ou ocultar completamente a gerência, incluindo o label.
        precisa_gerencia = len(gerencias) > 1
        self.label_gerencia.setVisible(precisa_gerencia)
        self.container_gerencia.setVisible(precisa_gerencia)
        
        # Ativa a cascata para município, setor e rota.
        if gerencias:
            self._atualizar_municipio_por_localidade_gerencia()
            self._atualizar_setores_por_localidade_gerencia()
        else:
            self.input_setor.blockSignals(True)
            self.input_setor.clear()
            self.input_setor.blockSignals(False)
            self._preencher_rota_por_selecao()

    def _atualizar_municipio_por_localidade_gerencia(self, *_):
        """Quando LOCALIDADE + GERÊNCIA são selecionadas, preenche MUNICÍPIO"""
        if not self._dados_localidades:
            return

        self._preencher_municipio_por_localidade(self.input_gerencia.currentText())

    def _atualizar_setores_por_localidade_gerencia(self, *_):
        """Quando LOCALIDADE + GERÊNCIA são selecionadas, preenche SETOR"""
        if not self._dados_localidades:
            return

        localidade = _normalizar_campo_txt(self.input_localidade.currentText())
        gerencia = _normalizar_campo_txt(self.input_gerencia.currentText())
        
        if not localidade or not gerencia:
            self.input_setor.blockSignals(True)
            self.input_setor.clear()
            self.input_setor.blockSignals(False)
            self._preencher_rota_por_selecao()
            self._atualizar_pastas_saida_por_municipio()
            return

        dados = self._dados_localidades_filtrados()
        # Filtra por localidade + gerência
        dados = [r for r in dados 
                 if _normalizar_campo_txt(r.get('LOCALIDADE', '')) == localidade
                 and _normalizar_campo_txt(r.get('GERENCIA', '')) == gerencia]

        # Divide setores pela vírgula e coleta todos os únicos
        setores = set()
        for r in dados:
            setor_str = r.get('SETOR', '').strip()
            if setor_str:
                for s in setor_str.split(','):
                    s_clean = s.strip()
                    if s_clean:
                        setores.add(s_clean)
        
        setores = sorted(setores)

        self.input_setor.blockSignals(True)
        self.input_setor.clear()
        self._preencher_rota_por_selecao()
        
        if len(setores) > 1:
            self.input_setor.setEditable(False)
            self.input_setor.addItems(setores)
        else:
            self.input_setor.setEditable(True)
            if setores:
                self.input_setor.addItem(setores[0])
                self.input_setor.setCurrentText(setores[0])
        
        self.input_setor.blockSignals(False)
        self._atualizar_pastas_saida_por_municipio()

    def _atualizar_municipio_por_localidade(self, *_):
        if not self._dados_localidades:
            return

        localidade = _normalizar_campo_txt(self.input_localidade.currentText())
        if not localidade:
            self.input_municipio.blockSignals(True)
            self.input_municipio.clear()
            self.input_municipio.blockSignals(False)
            return

        # Procura registros que correspondem à localidade selecionada
        matches = [
            r for r in self._dados_localidades
            if _normalizar_campo_txt(r.get('LOCALIDADE', '')) == localidade
        ]
        
        # Extrai nomes únicos de município
        municipios = sorted(set(
            r.get('MUNICIPIO', '').strip()
            for r in matches
            if r.get('MUNICIPIO', '').strip()
        ))

        # Preench o campo Município se houver exatamente um
        self.input_municipio.blockSignals(True)
        if len(municipios) == 1:
            self.input_municipio.setText(municipios[0])
        else:
            self.input_municipio.clear()
        self.input_municipio.blockSignals(False)
        self._atualizar_pastas_saida_por_municipio()

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

        if not pasta_qpt:
            QMessageBox.warning(self, 'Validação', 'Informe uma pasta válida para os QPTs.')
            return
        if not pasta_pdf:
            QMessageBox.warning(self, 'Validação', 'Informe uma pasta válida para os PDFs.')
            return

        try:
            os.makedirs(pasta_qpt, exist_ok=True)
            os.makedirs(pasta_pdf, exist_ok=True)
        except Exception as exc:
            QMessageBox.warning(self, 'Validação', f'Não foi possível criar as pastas de saída: {exc}')
            return

        if not os.path.isdir(pasta_qpt) or not os.path.isdir(pasta_pdf):
            QMessageBox.warning(self, 'Validação', 'Não foi possível validar as pastas de saída informadas.')
            return

        self.accept()

    def values(self):
        return {
            'qpt_retrato': self.input_qpt_retrato['input'].text().strip(),
            'qpt_paisagem': self.input_qpt_paisagem['input'].text().strip(),
            'qpt_output_dir': self.input_pasta_qpt['input'].text().strip(),
            'pdf_output_dir': self.input_pasta_pdf['input'].text().strip(),
            'EXIBIR_IMOVEL_ETIQ': self.input_exibir_imovel_etiq.isChecked(),
            'LOCALIDADE': self.input_localidade.currentText().strip(),
            'SETOR': self.input_setor.currentText().strip(),
            'ROTA': self.input_rota.text().strip(),
            'MUNICIPIO': self.input_municipio.text().strip(),
            'ELABORADO POR': (
                self.input_elaborado_outro.text().strip()
                if _normalizar_campo_txt(self.input_elaborado_por.currentText()) == 'OUTRO...'
                else self.input_elaborado_por.currentText().strip()
            ),
            'DATA': self.input_data.text().strip() or time.strftime('%d/%m/%Y'),
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

def _find_map_items(layout):
    mapas = [i for i in layout.items() if isinstance(i, QgsLayoutItemMap)]
    if not mapas:
        raise RuntimeError(f"Layout '{layout.name()}' nao possui item de mapa.")
    return mapas


def _anel_externo_principal(geom):
    if geom is None or geom.isEmpty():
        return []

    wt = geom.wkbType()
    partes = geom.asMultiPolygon() if QgsWkbTypes.isMultiType(wt) else [geom.asPolygon()]
    melhor_anel = []
    melhor_area = -1.0

    for parte in partes:
        if not parte:
            continue
        anel = parte[0]
        if len(anel) < 3:
            continue
        try:
            area = abs(QgsGeometry.fromPolygonXY([anel]).area())
        except Exception:
            area = 0.0
        if area > melhor_area:
            melhor_area = area
            melhor_anel = anel

    return melhor_anel


def _adicionar_item_poligono_rota(layout, mapa_item, geom_rota, item_id='ROTA_CLIP'):
    anel = _anel_externo_principal(geom_rota)
    if len(anel) < 3:
        return None

    try:
        transform_layout_para_mapa = mapa_item.layoutToMapCoordsTransform()
        transform_mapa_para_layout, ok = transform_layout_para_mapa.inverted()
        if not ok:
            return None
    except Exception:
        return None

    poligono = QPolygonF()
    for pt in anel:
        poligono.append(transform_mapa_para_layout.map(QPointF(pt.x(), pt.y())))

    if poligono.size() < 3:
        return None

    item = QgsLayoutItemPolygon(poligono, layout)
    try:
        item.setId(item_id)
    except Exception:
        pass

    simbolo = QgsFillSymbol.createSimple({
        'color': '255,255,255,0',
        'outline_color': '0,0,0,255',
        'outline_width': '0.20',
    })
    try:
        item.setSymbol(simbolo)
    except Exception:
        pass

    layout.addLayoutItem(item)
    try:
        item.attemptMove(item.pos())
    except Exception:
        pass
    item.refresh()
    return item


def _aplicar_clip_item_nos_mapas(mapa_itens, item_clip):
    if item_clip is None:
        return False

    aplicado = False
    for mi in mapa_itens:
        try:
            clip_settings = mi.itemClippingSettings()
        except Exception:
            continue

        try:
            clip_settings.setSourceItem(item_clip)
            clip_settings.setEnabled(True)
            clip_settings.setForceLabelsInsideClipPath(True)
            aplicado = True
        except Exception:
            continue

    return aplicado


def _configurar_mapas_layout(mapa_itens, camadas, ext, item_clip=None):
    for mi in mapa_itens:
        try:
            mi.setKeepLayerSet(True)
        except Exception:
            pass
        try:
            mi.setFollowVisibilityPreset(False)
        except Exception:
            pass
        try:
            mi.setLayers(camadas)
        except Exception:
            pass
        if hasattr(mi, 'zoomToExtent'):
            mi.zoomToExtent(ext)
        else:
            mi.setExtent(ext)
        if item_clip is not None:
            try:
                clip_settings = mi.itemClippingSettings()
                clip_settings.setSourceItem(item_clip)
                clip_settings.setEnabled(True)
                clip_settings.setForceLabelsInsideClipPath(True)
            except Exception:
                pass
        mi.refresh()

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
    # A rota do PDF deve sempre refletir a feicao atual da camada ROTAS DE LEITURA.
    campos_layout['ROTA'] = str(rota_label).strip()
    _aplicar_textos_layout(layout, campos_layout)
    _garantir_logo_caema_no_layout(layout, projeto)
    _processar_eventos_ui()

    mapa_item = _find_first_map_item(layout)
    mapa_itens = _find_map_items(layout)
    ext = _expand_extent(QgsGeometry(geom_rota).boundingBox(), MARGEM_ENQUADRAMENTO)
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
    tmp_arruamento_rotulo = None
    if tmp_arruamento is not None:
        tmp_arruamento_rotulo = _criar_camada_rotulo_arruamento_externo(
            tmp_arruamento,
            tmp_quadras,
            f'{nome_base}_ARRUAMENTO_ROT',
        )
        try:
            if tmp_arruamento_rotulo is not None and tmp_arruamento_rotulo.featureCount() == 0:
                tmp_arruamento_rotulo = None
        except Exception:
            pass
    _processar_eventos_ui()

    # Desativa recorte por item para evitar corte parcial da rota no PDF.
    item_poligono_rota = None
    clip_item_ativo = False

    # Exibir polígonos de quadra normalmente no mapa final.
    _aplicar_estilo_preto_branco(tmp_quadras)
    exibir_imovel_etiq = bool(config_exportacao.get('EXIBIR_IMOVEL_ETIQ', True))
    if exibir_imovel_etiq:
        _aplicar_estilo_preto_branco(tmp_imovel)
    _aplicar_estilo_preto_branco(tmp_inicio, papel='inicio')
    _aplicar_estilo_preto_branco(tmp_fim, papel='fim')
    _aplicar_estilo_preto_branco(tmp_rota, papel='rota')
    if tmp_arruamento is not None:
        _aplicar_estilo_invisivel(tmp_arruamento)

    # Usar camada ETIQUETAS_IMOVEL existente (gerada por tracarPerpendicularNasQuadras)
    etiq_source_layers = projeto.mapLayersByName(NOME_CAMADA_ETIQ)
    tmp_etiq = None
    tmp_imovel_pontos = None
    camadas_imoveis_individuais = []
    if exibir_imovel_etiq:
        if etiq_source_layers:
            tmp_etiq = _clip_features_to_polygon(
                etiq_source_layers[0], geom_rota, f'{nome_base}_ETIQ_IMOVEL', crs_rota
            )
            _configurar_camada_etiquetas_imovel(tmp_etiq, tmp_quadras, ext, mapa_item)
            tmp_imovel_pontos = _criar_camada_pontos_imovel_proximos(tmp_etiq, tmp_quadras, f'{nome_base}_IMOVEL_PONTOS')
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
        if tmp_arruamento_rotulo is not None:
            # Rótulo da rua será controlado por camada dedicada no topo para garantir visibilidade.
            tmp_arruamento.setLabelsEnabled(False)
            tmp_arruamento.triggerRepaint()
        else:
            # Fallback: se a camada de rótulo externo não gerar pontos, rotula a própria linha.
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
    if tmp_arruamento_rotulo is not None:
        projeto.addMapLayer(tmp_arruamento_rotulo, False)

    # Adicionar camada de etiquetas ou camadas individuais de imóveis
    if exibir_imovel_etiq:
        if tmp_etiq is not None:
            projeto.addMapLayer(tmp_etiq, False)
            if tmp_imovel_pontos is not None:
                projeto.addMapLayer(tmp_imovel_pontos, False)
        else:
            for camada_imovel in camadas_imoveis_individuais:
                projeto.addMapLayer(camada_imovel, False)

    try:
        # IMOVEIS no topo de desenho para destacar pontos e rótulos seq_id.
        # Usar camadas individuais em vez de tmp_imovel
        camadas_layout = []
        if exibir_imovel_etiq:
            if tmp_etiq is not None:
                if tmp_imovel_pontos is not None:
                    camadas_layout.append(tmp_imovel_pontos)
                camadas_layout.append(tmp_etiq)
            else:
                camadas_layout.extend(camadas_imoveis_individuais)
        camadas_layout.extend([tmp_quadras, tmp_inicio, tmp_fim])
        if tmp_quadras_rotulo is not None:
            camadas_layout.append(tmp_quadras_rotulo)
        if tmp_arruamento is not None and tmp_arruamento_rotulo is None:
            camadas_layout.append(tmp_arruamento)
        camadas_layout.append(tmp_overley)
        if tmp_arruamento_rotulo is not None:
            # Última camada para ficar à frente de tudo no layout.
            camadas_layout.append(tmp_arruamento_rotulo)

        _configurar_mapas_layout(mapa_itens, camadas_layout, ext, None)

        nome_base_saida = f'Mapa_Rota_{_slugify_texto(rota_label)}'
        caminho_qpt = os.path.join(config_exportacao['qpt_output_dir'], nome_base_saida + '.qpt')
        caminho_pdf = os.path.join(config_exportacao['pdf_output_dir'], nome_base_saida + '.pdf')

        exporter = QgsLayoutExporter(layout)
        result = exporter.exportToPdf(caminho_pdf, QgsLayoutExporter.PdfExportSettings())
        if result != QgsLayoutExporter.Success:
            raise RuntimeError(f'Falha ao exportar o PDF da rota {rota_label}.')

        camadas_qpt = [layers_base['rota'], layers_base['quadras'], layers_base['inicio'], layers_base['fim']]
        if layer_arruamento is not None:
            camadas_qpt.append(layer_arruamento)
        camadas_qpt.append(layers_base['overley'])
        if exibir_imovel_etiq:
            etiq_source_layers = projeto.mapLayersByName(NOME_CAMADA_ETIQ)
            if etiq_source_layers:
                camadas_qpt.insert(0, etiq_source_layers[0])
            else:
                camadas_qpt.insert(0, layers_base['imovel'])

        # QPT deve manter o enquadramento sem recorte por poligono da rota.
        _configurar_mapas_layout(mapa_itens, camadas_qpt, ext, None)
        _salvar_layout_como_qpt_em(layout, caminho_qpt)
        _processar_eventos_ui()

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
        if tmp_arruamento_rotulo is not None:
            camadas_tmp.append(tmp_arruamento_rotulo)
        if tmp_etiq is not None:
            camadas_tmp.append(tmp_etiq)
        if tmp_imovel_pontos is not None:
            camadas_tmp.append(tmp_imovel_pontos)
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
        # Fallback para projetos que ainda usam o nome alternativo.
        try:
            layer_arruamento = _get_layer('ARRUAMENTO_MA')
            print("Camada 'Ruas_MA' nao encontrada; usando fallback 'ARRUAMENTO_MA'.")
        except RuntimeError:
            layer_arruamento = None
            print("Camadas 'Ruas_MA' e 'ARRUAMENTO_MA' nao encontradas; arruamento sera omitido.")

    sel_rotas = list(layer_rota.selectedFeatures())
    if not sel_rotas:
        raise RuntimeError('Selecione uma ou mais rotas na camada de rotas antes de executar.')
    if QgsWkbTypes.geometryType(layer_rota.wkbType()) != QgsWkbTypes.PolygonGeometry:
        raise RuntimeError('A camada de rota precisa ser poligonal para usar recorte por rota.')

    dialog = BatchExportDialog(projeto, sel_rotas)
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
