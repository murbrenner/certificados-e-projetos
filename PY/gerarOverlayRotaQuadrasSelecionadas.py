#NOME: Gerar Overlay Rota Quadras Selecionadas

#DESCRIÇÃO: Gera overlay de rota a partir de poligono selecionado em ROTAS DE LEITURA. Fluxo implementado: 1) Parte da rota selecionada na camada ROTAS DE LEITURA. 2) Seleciona por localizacao as camadas: IMOVEL, INICIO_PNT, FIM_PNT, QUADRAS e ARRUAMENTO_MA. 3) Cria PR_OVERLAY com vertices das quadras selecionadas e campo sequenci. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# -*- coding: utf-8 -*-
"""
Gera overlay de rota a partir de poligono selecionado em ROTAS DE LEITURA.

Fluxo implementado:
1) Parte da rota selecionada na camada ROTAS DE LEITURA.
2) Seleciona por localizacao as camadas: IMOVEL, INICIO_PNT, FIM_PNT, QUADRAS e ARRUAMENTO_MA.
3) Cria PR_OVERLAY com vertices das quadras selecionadas e campo sequencia_alfa.
4) Mantem os calculos de trajeto para suporte ao processamento metrico (sem criar linhas de overlay).
5) Atualiza seq_id em modo metrico.
6) Atualiza seq_id na camada IMOVEL respeitando obrigatoriamente a ordem dos pontos da camada (seq_id),
   usando INICIO_PNT selecionado como referencia inicial quando disponivel.
7) Nao faz commit (edicao aberta).

Observacoes:
- Script para executar dentro do Console Python do QGIS (QGIS 3.x).
- Assume campo seq_id existente na camada IMOVEL.
- Distancia para seq_id calculada em geodesia WGS84 (evita inflacao de metragem).
- Offset e desenho continuam em CRS metrico para manter deslocamento fixo em metros.
"""

import math
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QMessageBox


OFFSET_VERTICE_M = 8.0
MAX_LINHAS_POR_QUADRA = 9
ANGULO_90_TOLERANCIA_GRAUS = 15.0
COMPRIMENTO_LINHA_LOCAL_M = 12.0


# -----------------------------
# Helpers gerais
# -----------------------------

def get_layer_by_candidates(names):
    for name in names:
        layers = QgsProject.instance().mapLayersByName(name)
        if layers:
            return layers[0]
    return None


def remove_layer_if_exists(name):
    project = QgsProject.instance()
    for lyr in list(project.mapLayers().values()):
        if lyr.name() == name:
            project.removeMapLayer(lyr.id())


def alpha_label(index_zero_based):
    # 0 -> A, 25 -> Z, 26 -> AA, 27 -> AB...
    n = int(index_zero_based) + 1
    out = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def to_float_safe(value, default=float("inf")):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def distance_xy(p1, p2):
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    return math.hypot(dx, dy)


def interpolate_point(p1, p2, t):
    return QgsPointXY(
        p1.x() + (p2.x() - p1.x()) * t,
        p1.y() + (p2.y() - p1.y()) * t,
    )


def split_segment_max_len(p1, p2, max_len=15.0):
    """
    Divide p1->p2 em subsegmentos conectados, cada um com comprimento <= max_len.
    """
    total = distance_xy(p1, p2)
    if total <= 0:
        return []

    if total <= max_len:
        return [(p1, p2)]

    pieces = int(math.ceil(total / max_len))
    out = []
    prev = p1
    for i in range(1, pieces + 1):
        t = float(i) / float(pieces)
        cur = interpolate_point(p1, p2, t)
        out.append((prev, cur))
        prev = cur
    return out


def pick_metric_crs(reference_layer):
    """
    Escolhe um CRS metrico para calculos de distancia e offset.
    Prioridade:
    1) CRS da camada de referencia, se em metros.
    2) CRS do projeto, se em metros.
    3) EPSG:31983 (fallback comum no seu fluxo).
    """
    lyr_crs = reference_layer.crs()
    if lyr_crs.mapUnits() == QgsUnitTypes.DistanceMeters:
        return lyr_crs

    proj_crs = QgsProject.instance().crs()
    if proj_crs.mapUnits() == QgsUnitTypes.DistanceMeters:
        return proj_crs

    return QgsCoordinateReferenceSystem("EPSG:31983")


def make_transform(src_crs, dst_crs):
    return QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())


def transform_geometry(geom, xform):
    g = QgsGeometry(geom)
    g.transform(xform)
    return g


def transform_point(pt, xform):
    return xform.transform(pt)


def angle_deg(v1x, v1y, v2x, v2y):
    n1 = math.hypot(v1x, v1y)
    n2 = math.hypot(v2x, v2y)
    if n1 == 0 or n2 == 0:
        return 0.0
    c = (v1x * v2x + v1y * v2y) / (n1 * n2)
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def extract_point_safe(geom):
    if geom is None or geom.isEmpty():
        return None
    try:
        return geom.asPoint()
    except Exception:
        pass
    try:
        mp = geom.asMultiPoint()
        if mp:
            return mp[0]
    except Exception:
        pass
    return None


def merged_selected_route_geom_metric(route_layer, metric_crs):
    selected = list(route_layer.selectedFeatures())
    if not selected:
        return None

    x_route_to_m = make_transform(route_layer.crs(), metric_crs)
    merged = None
    for feat in selected:
        g = feat.geometry()
        if g is None or g.isEmpty():
            continue
        gm = transform_geometry(g, x_route_to_m)
        if merged is None:
            merged = gm
        else:
            merged = merged.combine(gm)
    return merged


def select_layer_by_route_geom(layer, route_geom_metric, metric_crs):
    if layer is None or route_geom_metric is None:
        return []

    x_to_m = make_transform(layer.crs(), metric_crs)
    selected_ids = []

    for feat in layer.getFeatures():
        g = feat.geometry()
        if g is None or g.isEmpty():
            continue
        gm = transform_geometry(g, x_to_m)
        if route_geom_metric.intersects(gm) or route_geom_metric.contains(gm) or gm.within(route_geom_metric):
            selected_ids.append(feat.id())

    layer.selectByIds(selected_ids)
    return selected_ids


# -----------------------------
# Geometria de vertices / ancoras
# -----------------------------

def outward_offset_point(prev_pt, curr_pt, next_pt, polygon_geom, offset_m=2.5):
    """
    Calcula um ponto deslocado para fora no vertice atual.
    Escolhe o lado externo testando contains() no poligono.
    """
    # Vetores das arestas adjacentes
    e1x = curr_pt.x() - prev_pt.x()
    e1y = curr_pt.y() - prev_pt.y()
    e2x = next_pt.x() - curr_pt.x()
    e2y = next_pt.y() - curr_pt.y()

    def norm(x, y):
        l = math.hypot(x, y)
        if l == 0:
            return (0.0, 0.0)
        return (x / l, y / l)

    # Normais "esquerda" das arestas
    e1x, e1y = norm(e1x, e1y)
    e2x, e2y = norm(e2x, e2y)
    n1x, n1y = -e1y, e1x
    n2x, n2y = -e2y, e2x

    # Direcao media das normais
    bx, by = n1x + n2x, n1y + n2y
    bl = math.hypot(bx, by)
    if bl == 0:
        # fallback
        bx, by = n1x, n1y
        bl = math.hypot(bx, by)
        if bl == 0:
            bx, by = 1.0, 0.0
            bl = 1.0
    bx, by = bx / bl, by / bl

    c1 = QgsPointXY(curr_pt.x() + bx * offset_m, curr_pt.y() + by * offset_m)
    c2 = QgsPointXY(curr_pt.x() - bx * offset_m, curr_pt.y() - by * offset_m)

    g1 = QgsGeometry.fromPointXY(c1)
    g2 = QgsGeometry.fromPointXY(c2)

    inside1 = polygon_geom.contains(g1)
    inside2 = polygon_geom.contains(g2)

    # Queremos fora da quadra
    if inside1 and not inside2:
        return c2
    if inside2 and not inside1:
        return c1

    # Caso ambiguo, escolhe o que estiver mais distante do centroide
    centroid = polygon_geom.centroid().asPoint()
    d1 = distance_xy(centroid, c1)
    d2 = distance_xy(centroid, c2)
    return c1 if d1 >= d2 else c2


def nearest_vertex_key(point_metric, candidate_keys, vertex_info):
    best_k = None
    best_d = float("inf")
    for k in candidate_keys:
        d = distance_xy(point_metric, vertex_info[k]["raw"])
        if d < best_d:
            best_d = d
            best_k = k
    return best_k, best_d


def build_vertex_collections(selected_quadras, x_q_to_m, offset_m=8.0):
    vertex_info = {}      # key -> {raw, offset, quadra_id, ring_id, idx}
    ring_to_keys = {}     # ring_id -> [keys em ordem]
    quadra_to_keys = {}   # quadra_id -> [keys]
    quadra_geoms = []     # [(quadra_id, geom_metric)]

    for qf in selected_quadras:
        g = qf.geometry()
        if g is None or g.isEmpty():
            continue

        gm = transform_geometry(g, x_q_to_m)
        qid = qf.id()
        quadra_geoms.append((qid, gm))
        quadra_to_keys.setdefault(qid, [])

        if gm.isMultipart():
            polygons = gm.asMultiPolygon()
        else:
            polygons = [gm.asPolygon()]

        for part_idx, poly in enumerate(polygons):
            if not poly or not poly[0]:
                continue

            part_geom = QgsGeometry.fromPolygonXY(poly)
            outer = poly[0]
            if len(outer) > 1 and outer[0] == outer[-1]:
                outer = outer[:-1]

            if len(outer) < 3:
                continue

            ring_id = f"{qid}_{part_idx}"
            ring_to_keys[ring_id] = []

            for vidx in range(len(outer)):
                prev_pt = outer[(vidx - 1) % len(outer)]
                cur_pt = outer[vidx]
                next_pt = outer[(vidx + 1) % len(outer)]

                offset_pt = outward_offset_point(prev_pt, cur_pt, next_pt, part_geom, offset_m=offset_m)

                key = (qid, part_idx, vidx)
                vertex_info[key] = {
                    "raw": QgsPointXY(cur_pt.x(), cur_pt.y()),
                    "offset": QgsPointXY(offset_pt.x(), offset_pt.y()),
                    "quadra_id": qid,
                    "ring_id": ring_id,
                    "idx": vidx,
                }
                ring_to_keys[ring_id].append(key)
                quadra_to_keys[qid].append(key)

    return vertex_info, ring_to_keys, quadra_to_keys, quadra_geoms


def vertex_angle_on_ring_deg(key, vertex_info, ring_to_keys):
    ring_id = vertex_info[key]["ring_id"]
    ring_keys = ring_to_keys.get(ring_id, [])
    if len(ring_keys) < 3:
        return 180.0

    idx = vertex_info[key]["idx"]
    n = len(ring_keys)
    k_prev = ring_keys[(idx - 1) % n]
    k_next = ring_keys[(idx + 1) % n]

    p_prev = vertex_info[k_prev]["raw"]
    p_cur = vertex_info[key]["raw"]
    p_next = vertex_info[k_next]["raw"]

    v1x = p_prev.x() - p_cur.x()
    v1y = p_prev.y() - p_cur.y()
    v2x = p_next.x() - p_cur.x()
    v2y = p_next.y() - p_cur.y()

    return angle_deg(v1x, v1y, v2x, v2y)


def add_split_line_features(overlay_layer, overlay_provider, order_ref, p1, p2, seg_type):
    parts = split_segment_max_len(p1, p2, max_len=15.0)
    for s1, s2 in parts:
        feat = QgsFeature(overlay_layer.fields())
        feat.setGeometry(QgsGeometry.fromPolylineXY([s1, s2]))
        feat.setAttributes([order_ref[0], seg_type])
        overlay_provider.addFeature(feat)
        order_ref[0] += 1


def add_directional_vertex_line(
    overlay_layer,
    overlay_provider,
    order_ref,
    key,
    target_point,
    vertex_info,
    ring_to_keys,
    length_m=12.0,
):
    """
    Cria uma linha local no vertice deslocado para fora, orientada para o proximo alvo.
    Comprimento maximo 15 m.
    """
    center = vertex_info[key]["offset"]

    vx = target_point.x() - center.x()
    vy = target_point.y() - center.y()
    norm = math.hypot(vx, vy)

    if norm == 0:
        ring_id = vertex_info[key]["ring_id"]
        ring_keys = ring_to_keys.get(ring_id, [])
        if len(ring_keys) >= 2:
            idx = vertex_info[key]["idx"]
            n = len(ring_keys)
            k_prev = ring_keys[(idx - 1) % n]
            k_next = ring_keys[(idx + 1) % n]
            p_prev = vertex_info[k_prev]["raw"]
            p_next = vertex_info[k_next]["raw"]
            vx = p_next.x() - p_prev.x()
            vy = p_next.y() - p_prev.y()
            norm = math.hypot(vx, vy)

    if norm == 0:
        vx, vy, norm = 1.0, 0.0, 1.0

    ux, uy = vx / norm, vy / norm
    seg_len = min(15.0, max(4.0, float(length_m)))

    # Levemente assimetrica para reforcar direcao de avancar.
    a = QgsPointXY(center.x() - ux * seg_len * 0.25, center.y() - uy * seg_len * 0.25)
    b = QgsPointXY(center.x() + ux * seg_len * 0.75, center.y() + uy * seg_len * 0.75)

    add_split_line_features(overlay_layer, overlay_provider, order_ref, a, b, "vertice_dir")


def add_u_turn_marker(overlay_layer, overlay_provider, order_ref, center, forward_unit, width=3.0, depth=4.0):
    """
    Desenha um pequeno U conectado para indicar meia-volta.
    """
    fx, fy = forward_unit
    fn = math.hypot(fx, fy)
    if fn == 0:
        return
    fx, fy = fx / fn, fy / fn
    nx, ny = -fy, fx

    p1 = QgsPointXY(center.x() + nx * width, center.y() + ny * width)
    p2 = QgsPointXY(center.x() - fx * depth, center.y() - fy * depth)
    p3 = QgsPointXY(center.x() - nx * width, center.y() - ny * width)

    add_split_line_features(overlay_layer, overlay_provider, order_ref, p1, p2, "u_local")
    add_split_line_features(overlay_layer, overlay_provider, order_ref, p2, p3, "u_local")


def build_wgs84_distance_engine():
    da = QgsDistanceArea()
    wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    da.setSourceCrs(wgs84, QgsProject.instance().transformContext())
    da.setEllipsoid("WGS84")
    try:
        da.setEllipsoidalMode(True)
    except Exception:
        try:
            da.setEllipsoidal(True)
        except Exception:
            pass
    return da, wgs84


def geodesic_distance_metric_points(p1_metric, p2_metric, x_metric_to_wgs84, dist_engine):
    p1w = transform_point(p1_metric, x_metric_to_wgs84)
    p2w = transform_point(p2_metric, x_metric_to_wgs84)
    d = dist_engine.measureLine(p1w, p2w)
    if d is None:
        return 0.0
    return float(d)


# -----------------------------
# Script principal
# -----------------------------

def main():
    layer_rotas = get_layer_by_candidates(["ROTAS DE LEITURA"])
    layer_imovel = get_layer_by_candidates(["IMÓVEL", "IMOVEL"])
    layer_inicio = get_layer_by_candidates(["INICIO_PNT"])
    layer_fim = get_layer_by_candidates(["FIM_PNT"])
    layer_quadras = get_layer_by_candidates(["QUADRAS"])
    layer_arruamento = get_layer_by_candidates(["ARRUAMENTO_MA"])

    if (
        layer_rotas is None
        or layer_imovel is None
        or layer_inicio is None
        or layer_fim is None
        or layer_quadras is None
        or layer_arruamento is None
    ):
        QMessageBox.critical(
            None,
            "Erro",
            (
                "Camadas obrigatorias nao encontradas.\n"
                "Necessarias: ROTAS DE LEITURA, IMÓVEL/IMOVEL, INICIO_PNT, FIM_PNT, QUADRAS, ARRUAMENTO_MA."
            ),
        )
        return

    selected_rotas = list(layer_rotas.selectedFeatures())
    if not selected_rotas:
        QMessageBox.warning(None, "Aviso", "Selecione ao menos um poligono na camada ROTAS DE LEITURA.")
        return

    if layer_imovel.fields().indexFromName("seq_id") < 0:
        QMessageBox.critical(None, "Erro", "Campo seq_id nao encontrado na camada IMOVEL.")
        return

    # Guardar INICIO preselecionado para priorizar no ponto inicial
    inicio_pre_ids = set(layer_inicio.selectedFeatureIds())

    # CRS metrico para calculos
    metric_crs = pick_metric_crs(layer_rotas)
    print("CRS metrico usado:", metric_crs.authid())

    route_geom_metric = merged_selected_route_geom_metric(layer_rotas, metric_crs)
    if route_geom_metric is None or route_geom_metric.isEmpty():
        QMessageBox.critical(None, "Erro", "Nao foi possivel montar a geometria da rota selecionada.")
        return

    # Selecoes obrigatorias a partir da rota
    sel_imovel = select_layer_by_route_geom(layer_imovel, route_geom_metric, metric_crs)
    sel_inicio = select_layer_by_route_geom(layer_inicio, route_geom_metric, metric_crs)
    sel_fim = select_layer_by_route_geom(layer_fim, route_geom_metric, metric_crs)
    sel_quadras = select_layer_by_route_geom(layer_quadras, route_geom_metric, metric_crs)
    sel_arruamento = select_layer_by_route_geom(layer_arruamento, route_geom_metric, metric_crs)

    print("Selecao por rota concluida:")
    print("- IMOVEL:", len(sel_imovel))
    print("- INICIO_PNT:", len(sel_inicio))
    print("- FIM_PNT:", len(sel_fim))
    print("- QUADRAS:", len(sel_quadras))
    print("- ARRUAMENTO_MA:", len(sel_arruamento))

    selected_quadras = list(layer_quadras.selectedFeatures())
    if not selected_quadras:
        QMessageBox.warning(None, "Aviso", "Nenhuma quadra foi selecionada dentro da rota.")
        return

    x_q_to_m = make_transform(layer_quadras.crs(), metric_crs)
    x_i_to_m = make_transform(layer_imovel.crs(), metric_crs)
    x_inicio_to_m = make_transform(layer_inicio.crs(), metric_crs)

    selected_imoveis = list(layer_imovel.selectedFeatures())
    if len(selected_imoveis) < 2:
        QMessageBox.warning(None, "Aviso", "Foram encontrados menos de 2 IMOVEIS dentro da rota.")
        return

    imovel_points = {}
    for imv in selected_imoveis:
        pt = extract_point_safe(imv.geometry())
        if pt is None:
            continue
        imovel_points[imv.id()] = transform_point(pt, x_i_to_m)

    def seq_key(feat):
        return to_float_safe(feat["seq_id"])

    ordered_imoveis = sorted(selected_imoveis, key=seq_key)
    ordered_imoveis = [f for f in ordered_imoveis if f.id() in imovel_points]
    if len(ordered_imoveis) < 2:
        QMessageBox.warning(None, "Aviso", "Nao foi possivel ordenar IMOVEIS validos para roteamento.")
        return

    # -----------------------------
    # Extrair vertices das quadras e calcular offset externo 8m
    # -----------------------------
    vertex_info, ring_to_keys, quadra_to_keys, quadra_geoms_metric = build_vertex_collections(
        selected_quadras,
        x_q_to_m,
        offset_m=OFFSET_VERTICE_M,
    )

    if not vertex_info:
        QMessageBox.critical(None, "Erro", "Nao foi possivel extrair vertices das quadras selecionadas.")
        return

    # -----------------------------
    # Obter ponto inicial (INICIO_PNT)
    # -----------------------------
    inicio_selected = list(layer_inicio.selectedFeatures())
    inicio_priority = [f for f in inicio_selected if f.id() in inicio_pre_ids]
    inicio_pool = inicio_priority if inicio_priority else inicio_selected

    start_point = None
    if inicio_pool:
        first_imv_pt = imovel_points[ordered_imoveis[0].id()]
        best = None
        best_d = float("inf")
        for feat in inicio_pool:
            p = extract_point_safe(feat.geometry())
            if p is None:
                continue
            pm = transform_point(p, x_inicio_to_m)
            d = distance_xy(pm, first_imv_pt)
            if d < best_d:
                best_d = d
                best = pm
        start_point = best

    if start_point is None:
        # fallback: inicia no primeiro IMOVEL
        start_point = imovel_points[ordered_imoveis[0].id()]
        print("Aviso: nenhum INICIO_PNT valido selecionado; inicio assumido no primeiro IMOVEL da ordem.")

    # -----------------------------
    # Mapear ancora por ordem obrigatoria do IMOVEL (seq_id)
    # -----------------------------
    quadra_centroids = [(qid, qg.centroid().asPoint()) for qid, qg in quadra_geoms_metric]

    anchors = []
    for imv in ordered_imoveis:
        fid = imv.id()
        pt_m = imovel_points[fid]
        g_pt_m = QgsGeometry.fromPointXY(pt_m)

        # Descobrir quadra contendo o ponto
        containing_quadra = None
        for qid, qgeom in quadra_geoms_metric:
            if qgeom.contains(g_pt_m) or qgeom.intersects(g_pt_m):
                containing_quadra = qid
                break

        if containing_quadra is None:
            # fallback por centroide mais proximo
            best_qid = None
            best_d = float("inf")
            for qid, c in quadra_centroids:
                d = distance_xy(pt_m, c)
                if d < best_d:
                    best_d = d
                    best_qid = qid
            containing_quadra = best_qid

        candidate_keys = quadra_to_keys.get(containing_quadra, [])
        if not candidate_keys:
            continue

        best_key, _ = nearest_vertex_key(pt_m, candidate_keys, vertex_info)
        if best_key is None:
            continue

        anchors.append(
            {
                "fid": fid,
                "seq": to_float_safe(imv["seq_id"], default=0.0),
                "pt": pt_m,
                "quadra_id": containing_quadra,
                "vertex_key": best_key,
            }
        )

    if len(anchors) < 2:
        QMessageBox.warning(None, "Aviso", "Nao foi possivel criar ancoras suficientes para gerar a rota.")
        return

    # -----------------------------
    # Criacao de linhas OVERLAY removida por solicitacao.
    # Mantemos apenas a ordem de vertices visitados para o PR_OVERLAY.
    # -----------------------------
    visited_vertex_order = []
    seen_vertex_keys = set()
    for a in anchors:
        k = a["vertex_key"]
        if k not in seen_vertex_keys:
            seen_vertex_keys.add(k)
            visited_vertex_order.append(k)

    # -----------------------------
    # 3) Criar PR_OVERLAY com todos os vertices e sequencia_alfa
    # -----------------------------
    pr_name = "PR_OVERLAY"
    remove_layer_if_exists(pr_name)

    pr_layer = QgsVectorLayer(
        f"Point?crs={metric_crs.authid()}",
        pr_name,
        "memory",
    )
    pr_provider = pr_layer.dataProvider()
    pr_provider.addAttributes([QgsField("sequencia_alfa", QVariant.String)])
    pr_layer.updateFields()

    visited_unique = []
    seen = set()
    for k in visited_vertex_order:
        if k not in seen:
            seen.add(k)
            visited_unique.append(k)

    all_keys_sorted = sorted(vertex_info.keys(), key=lambda k: (k[0], k[1], k[2]))
    final_order = list(visited_unique)
    for k in all_keys_sorted:
        if k not in seen:
            final_order.append(k)

    key_to_alpha = {}
    for idx, k in enumerate(final_order):
        key_to_alpha[k] = alpha_label(idx)

    pr_features = []
    for k in final_order:
        feat = QgsFeature(pr_layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(vertex_info[k]["raw"]))
        feat.setAttributes([key_to_alpha[k]])
        pr_features.append(feat)

    pr_provider.addFeatures(pr_features)
    pr_layer.updateExtents()
    QgsProject.instance().addMapLayer(pr_layer)

    # -----------------------------
    # 6/7) Atualizar seq_id no IMOVEL (sem commit)
    # Ordem obrigatoria dos IMOVEIS por seq_id
    # Distancias geodesicas WGS84 (evita inflacao)
    # -----------------------------
    seq_idx = layer_imovel.fields().indexFromName("seq_id")

    dist_engine, wgs84_crs = build_wgs84_distance_engine()
    x_m_to_wgs = make_transform(metric_crs, wgs84_crs)

    seq_updates = {}
    cumulative = 0.0

    # Distancia inicial: INICIO_PNT -> primeiro IMOVEL da ordem
    first_anchor = anchors[0]
    cumulative += geodesic_distance_metric_points(start_point, first_anchor["pt"], x_m_to_wgs, dist_engine)
    seq_updates[first_anchor["fid"]] = int(round(cumulative))

    for i in range(1, len(anchors)):
        prev_a = anchors[i - 1]
        curr_a = anchors[i]

        k_prev = prev_a["vertex_key"]
        k_curr = curr_a["vertex_key"]

        # Base obrigatoria: distancia entre IMOVEIS na ordem seq_id.
        direct_step = geodesic_distance_metric_points(prev_a["pt"], curr_a["pt"], x_m_to_wgs, dist_engine)

        # Em troca de quadra, considera caminho por vertices, mas com teto anti-exagero.
        if prev_a["quadra_id"] != curr_a["quadra_id"]:
            via_vertices = (
                geodesic_distance_metric_points(prev_a["pt"], vertex_info[k_prev]["raw"], x_m_to_wgs, dist_engine)
                + geodesic_distance_metric_points(vertex_info[k_prev]["raw"], vertex_info[k_curr]["raw"], x_m_to_wgs, dist_engine)
                + geodesic_distance_metric_points(vertex_info[k_curr]["raw"], curr_a["pt"], x_m_to_wgs, dist_engine)
            )
            step = max(direct_step, min(via_vertices, direct_step * 1.35))
        else:
            step = direct_step

        cumulative += step
        seq_updates[curr_a["fid"]] = int(round(cumulative))

    if seq_idx >= 0:
        if not layer_imovel.isEditable():
            layer_imovel.startEditing()

        for fid, value in seq_updates.items():
            layer_imovel.changeAttributeValue(fid, seq_idx, int(value))

    # Resultado final
    print("Concluido.")
    print(f"- Rotas selecionadas: {len(selected_rotas)}")
    print(f"- Quadras usadas: {len(selected_quadras)}")
    print(f"- Imoveis selecionados: {len(ordered_imoveis)}")
    print(f"- INICIO_PNT selecionados: {len(sel_inicio)}")
    print(f"- FIM_PNT selecionados: {len(sel_fim)}")
    print(f"- ARRUAMENTO_MA selecionados: {len(sel_arruamento)}")
    print(f"- Pontos PR_OVERLAY: {len(final_order)}")
    print(f"- seq_id atualizado (sem commit) em {len(seq_updates)} imoveis")

    QMessageBox.information(
        None,
        "Concluido",
        (
            "Script executado com sucesso.\n"
            "Selecoes realizadas a partir de ROTAS DE LEITURA.\n"
            f"Camada de pontos: {pr_name}\n"
            "Criacao de linhas de overlay: desativada.\n"
            "IMOVEL atualizado em modo de edicao, sem commit."
        ),
    )


main()
