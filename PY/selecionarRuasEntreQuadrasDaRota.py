# NOME: Selecionar Ruas Entre Quadras da Rota
# DESCRICAO:
# 1) Usa o poligono selecionado em 'ROTAS DE LEITURA'.
# 2) Seleciona as quadras de 'QUADRAS' dentro/intersectando a rota.
# 3) Filtra linhas da camada 'Ruas_MA' que passam entre bordas proximas de quadras,
#    privilegiando trechos aproximadamente no meio entre duas quadras.
# 4) Alinha/move as linhas aprovadas para o meio entre quadras na propria 'Ruas_MA'
#    em modo de edicao SEM COMMIT (permite cancelar/desfazer).
# 5) Cria camadas auxiliares em memoria: backup original e resultado alinhado.
#
# EXECUCAO:
# Rodar no Console Python do QGIS 3.x.

import math
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsSpatialIndex,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsWkbTypes,
)


# =============================
# CONFIGURACAO
# =============================
NOME_CAMADA_ROTAS = "ROTAS DE LEITURA"
NOME_CAMADA_QUADRAS = "QUADRAS"
NOME_CAMADA_RUAS = "Ruas_MA"
NOME_SAIDA = "RUAS_ALINHADAS_ENTRE_QUADRAS_ROTA"
NOME_BACKUP = "RUAS_BACKUP_PRE_ALINHAMENTO"

# Distancia maxima (m) de um ponto da rua para borda de quadra para considerar proximidade
MAX_DIST_BORDA_M = 35.0
# Diferenca maxima (m) entre distancia para as duas quadras mais proximas (simetria de meio de rua)
MAX_DIF_DISTS_M = 8.0
# Percentual minimo de amostras da linha que devem satisfazer o criterio entre quadras
MIN_PROP_AMOSTRAS = 0.35
# Tamanho do passo (m) para amostrar cada linha
PASSO_AMOSTRAGEM_M = 12.0
# Buffer da rota para limitar busca de linhas (m)
BUFFER_ROTA_M = 5.0
# Fator de deslocamento para o ponto alvo (1.0 = vai direto para o meio entre quadras)
FATOR_DESLOCAMENTO = 1.0


# =============================
# HELPERS
# =============================
def layer_by_name(name):
    layers = QgsProject.instance().mapLayersByName(name)
    return layers[0] if layers else None


def metric_crs_from_layer(layer):
    crs = layer.crs()
    if crs.mapUnits() == 0:  # meters
        return crs

    proj_crs = QgsProject.instance().crs()
    if proj_crs.mapUnits() == 0:
        return proj_crs

    # Fallback comum no seu ambiente
    return QgsCoordinateReferenceSystem("EPSG:31983")


def transform_geometry(geom, src_crs, dst_crs):
    if src_crs == dst_crs:
        return QgsGeometry(geom)
    xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
    out = QgsGeometry(geom)
    out.transform(xform)
    return out


def merged_selected_route_geom_metric(route_layer, m_crs):
    selected = list(route_layer.selectedFeatures())
    if not selected:
        return None

    merged = None
    for f in selected:
        g = f.geometry()
        if g is None or g.isEmpty():
            continue
        gm = transform_geometry(g, route_layer.crs(), m_crs)
        merged = gm if merged is None else merged.combine(gm)
    return merged


def geometry_to_line_parts(geom):
    parts = []
    if geom is None or geom.isEmpty():
        return parts

    wkb = geom.wkbType()
    if QgsWkbTypes.geometryType(wkb) != QgsWkbTypes.LineGeometry:
        return parts

    if QgsWkbTypes.isMultiType(wkb):
        for p in geom.asMultiPolyline():
            if len(p) >= 2:
                parts.append(p)
    else:
        p = geom.asPolyline()
        if len(p) >= 2:
            parts.append(p)
    return parts


def sample_points_along_line_metric(line_geom, step_m=10.0):
    points = []
    if line_geom is None or line_geom.isEmpty():
        return points

    total = line_geom.length()
    if total <= 0:
        return points

    # Garante pontos iniciais/finais
    points.append(line_geom.interpolate(0).asPoint())

    d = step_m
    while d < total:
        points.append(line_geom.interpolate(d).asPoint())
        d += step_m

    points.append(line_geom.interpolate(total).asPoint())
    return points


def midpoint(p1, p2):
    return QgsPointXY((p1.x() + p2.x()) * 0.5, (p1.y() + p2.y()) * 0.5)


def geometry_boundary_compatible(geom):
    if geom is None or geom.isEmpty():
        return None

    # QGIS mais novo
    try:
        b = geom.boundary()
        if b is not None and not b.isEmpty():
            return b
    except Exception:
        pass

    # Fallback para versoes sem boundary() exposto em QgsGeometry
    try:
        wkb = geom.wkbType()
        gtype = QgsWkbTypes.geometryType(wkb)

        if gtype == QgsWkbTypes.PolygonGeometry:
            line_parts = []

            if QgsWkbTypes.isMultiType(wkb):
                polygons = geom.asMultiPolygon()
            else:
                polygons = [geom.asPolygon()]

            for poly in polygons:
                for ring in poly:
                    if len(ring) >= 2:
                        line_parts.append([QgsPointXY(p) for p in ring])

            if not line_parts:
                return None
            if len(line_parts) == 1:
                return QgsGeometry.fromPolylineXY(line_parts[0])
            return QgsGeometry.fromMultiPolylineXY(line_parts)

        if gtype == QgsWkbTypes.LineGeometry:
            return QgsGeometry(geom)

    except Exception:
        return None

    return None


def nearest_two_quadras_distance_to_boundary(pt_geom, quadra_layer_m, quadra_index, feat_cache):
    # Busca mais candidatos para evitar colisao de centroides e geometrias irregulares
    nn_ids = quadra_index.nearestNeighbor(pt_geom.asPoint(), 8)

    pairs = []
    for fid in nn_ids:
        feat = feat_cache.get(fid)
        if feat is None:
            continue
        g = feat.geometry()
        if g is None or g.isEmpty():
            continue

        boundary = geometry_boundary_compatible(g)
        if boundary is None or boundary.isEmpty():
            continue
        dist = pt_geom.distance(boundary)
        pairs.append((fid, dist))

    pairs.sort(key=lambda x: x[1])
    if len(pairs) < 2:
        return None

    # Precisamos de duas quadras distintas
    a = pairs[0]
    b = None
    for p in pairs[1:]:
        if p[0] != a[0]:
            b = p
            break

    if b is None:
        return None

    return a, b


def nearest_midpoint_between_two_quadras(pt_geom, quadra_index, feat_cache):
    nn_ids = quadra_index.nearestNeighbor(pt_geom.asPoint(), 8)
    pairs = []

    for fid in nn_ids:
        feat = feat_cache.get(fid)
        if feat is None:
            continue

        g = feat.geometry()
        if g is None or g.isEmpty():
            continue

        boundary = geometry_boundary_compatible(g)
        if boundary is None or boundary.isEmpty():
            continue

        d = pt_geom.distance(boundary)
        pairs.append((fid, d, boundary))

    pairs.sort(key=lambda x: x[1])
    if len(pairs) < 2:
        return None

    first = pairs[0]
    second = None
    for p in pairs[1:]:
        if p[0] != first[0]:
            second = p
            break

    if second is None:
        return None

    g_pt_a = first[2].nearestPoint(pt_geom)
    g_pt_b = second[2].nearestPoint(pt_geom)
    if g_pt_a is None or g_pt_a.isEmpty() or g_pt_b is None or g_pt_b.isEmpty():
        return None

    pt_a = g_pt_a.asPoint()
    pt_b = g_pt_b.asPoint()
    target = midpoint(pt_a, pt_b)
    return first[1], second[1], target


def move_vertex_towards_target(orig_pt, target_pt, factor=1.0):
    f = max(0.0, min(1.0, float(factor)))
    nx = orig_pt.x() + (target_pt.x() - orig_pt.x()) * f
    ny = orig_pt.y() + (target_pt.y() - orig_pt.y()) * f
    return QgsPointXY(nx, ny)


def move_line_part_between_quadras(part_pts, quadra_index, feat_cache):
    if len(part_pts) < 2:
        return part_pts, 0, 0

    moved = []
    adjusted = 0
    tested = 0

    for pt in part_pts:
        pt_geom = QgsGeometry.fromPointXY(QgsPointXY(pt))
        info = nearest_midpoint_between_two_quadras(pt_geom, quadra_index, feat_cache)

        if info is None:
            moved.append(QgsPointXY(pt))
            continue

        d1, d2, target = info
        tested += 1

        if d1 <= MAX_DIST_BORDA_M and d2 <= MAX_DIST_BORDA_M and abs(d1 - d2) <= MAX_DIF_DISTS_M:
            moved.append(move_vertex_towards_target(QgsPointXY(pt), target, FATOR_DESLOCAMENTO))
            adjusted += 1
        else:
            moved.append(QgsPointXY(pt))

    return moved, adjusted, tested


def move_line_geometry_between_quadras(line_geom_m, quadra_index, feat_cache):
    if line_geom_m is None or line_geom_m.isEmpty():
        return None, 0, 0

    wkb = line_geom_m.wkbType()
    total_adjusted = 0
    total_tested = 0

    if QgsWkbTypes.isMultiType(wkb):
        parts = line_geom_m.asMultiPolyline()
        out_parts = []
        for part in parts:
            moved_pts, adjusted, tested = move_line_part_between_quadras(part, quadra_index, feat_cache)
            total_adjusted += adjusted
            total_tested += tested
            if len(moved_pts) >= 2:
                out_parts.append(moved_pts)
        if not out_parts:
            return None, total_adjusted, total_tested
        return QgsGeometry.fromMultiPolylineXY(out_parts), total_adjusted, total_tested

    part = line_geom_m.asPolyline()
    moved_pts, adjusted, tested = move_line_part_between_quadras(part, quadra_index, feat_cache)
    total_adjusted += adjusted
    total_tested += tested
    if len(moved_pts) < 2:
        return None, total_adjusted, total_tested
    return QgsGeometry.fromPolylineXY(moved_pts), total_adjusted, total_tested


# =============================
# MAIN
# =============================
rotas = layer_by_name(NOME_CAMADA_ROTAS)
quadras = layer_by_name(NOME_CAMADA_QUADRAS)
ruas = layer_by_name(NOME_CAMADA_RUAS)

if rotas is None or quadras is None or ruas is None:
    raise Exception(
        "Camadas obrigatorias nao encontradas. Necessarias: '{}' , '{}' , '{}'".format(
            NOME_CAMADA_ROTAS, NOME_CAMADA_QUADRAS, NOME_CAMADA_RUAS
        )
    )

m_crs = metric_crs_from_layer(quadras)

route_geom_m = merged_selected_route_geom_metric(rotas, m_crs)
if route_geom_m is None or route_geom_m.isEmpty():
    raise Exception("Selecione ao menos 1 poligono na camada 'ROTAS DE LEITURA'.")

route_geom_m = route_geom_m.makeValid()
route_buffer_m = route_geom_m.buffer(BUFFER_ROTA_M, 8)

# 1) Selecionar quadras na rota
quadra_ids = []
quadra_feats_m = []

for f in quadras.getFeatures():
    g = f.geometry()
    if g is None or g.isEmpty():
        continue

    gm = transform_geometry(g, quadras.crs(), m_crs)
    if route_geom_m.intersects(gm) or route_geom_m.contains(gm) or gm.within(route_geom_m):
        quadra_ids.append(f.id())
        nf = QgsFeature(f)
        nf.setGeometry(gm)
        quadra_feats_m.append(nf)

quadras.selectByIds(quadra_ids)

if not quadra_feats_m:
    raise Exception("Nenhuma quadra encontrada dentro da rota selecionada.")

# Preparar indice espacial das quadras em CRS metrico
quadra_layer_m = QgsVectorLayer("Polygon?crs={}".format(m_crs.authid()), "quadras_tmp_m", "memory")
quadra_pr = quadra_layer_m.dataProvider()
quadra_pr.addAttributes(quadras.fields())
quadra_layer_m.updateFields()
quadra_pr.addFeatures(quadra_feats_m)
quadra_layer_m.updateExtents()

quadra_index = QgsSpatialIndex(quadra_layer_m.getFeatures())
quadra_cache = {f.id(): f for f in quadra_layer_m.getFeatures()}

# 2) Filtrar ruas no meio entre quadras
selected_rua_ids = []
output_feats = []
updated_geoms = {}

for rua_feat in ruas.getFeatures():
    g = rua_feat.geometry()
    if g is None or g.isEmpty():
        continue

    gm = transform_geometry(g, ruas.crs(), m_crs)

    # limita para area da rota
    if not route_buffer_m.intersects(gm):
        continue

    # amostrar ao longo da linha e testar criterio de meio entre quadras
    pts = sample_points_along_line_metric(gm, PASSO_AMOSTRAGEM_M)
    if not pts:
        continue

    ok_count = 0
    test_count = 0

    for pt in pts:
        pt_geom = QgsGeometry.fromPointXY(pt)

        nearest_pair = nearest_two_quadras_distance_to_boundary(
            pt_geom, quadra_layer_m, quadra_index, quadra_cache
        )
        if nearest_pair is None:
            continue

        (qa, da), (qb, db) = nearest_pair
        test_count += 1

        # ponto deve estar proximo das duas bordas e com distancias semelhantes
        if da <= MAX_DIST_BORDA_M and db <= MAX_DIST_BORDA_M and abs(da - db) <= MAX_DIF_DISTS_M:
            ok_count += 1

    if test_count == 0:
        continue

    prop = float(ok_count) / float(test_count)
    if prop >= MIN_PROP_AMOSTRAS:
        moved_geom_m, adjusted_vertices, tested_vertices = move_line_geometry_between_quadras(
            gm, quadra_index, quadra_cache
        )

        if moved_geom_m is None or tested_vertices == 0:
            continue

        prop_vertices = float(adjusted_vertices) / float(tested_vertices)
        if prop_vertices < MIN_PROP_AMOSTRAS:
            continue

        moved_geom_src = transform_geometry(moved_geom_m, m_crs, ruas.crs())
        selected_rua_ids.append(rua_feat.id())
        updated_geoms[rua_feat.id()] = moved_geom_src

        nf = QgsFeature(rua_feat)
        nf.setGeometry(moved_geom_src)
        output_feats.append(nf)

ruas.selectByIds(selected_rua_ids)

# 3) Backup antes de alterar Ruas_MA (memoria)
for lyr in list(QgsProject.instance().mapLayers().values()):
    if lyr.name() == NOME_BACKUP:
        QgsProject.instance().removeMapLayer(lyr.id())

backup_uri = "{}?crs={}".format(QgsWkbTypes.displayString(ruas.wkbType()), ruas.crs().authid())
backup = QgsVectorLayer(backup_uri, NOME_BACKUP, "memory")
backup_pr = backup.dataProvider()
backup_pr.addAttributes(ruas.fields())
backup.updateFields()

backup_feats = []
if selected_rua_ids:
    selected_set = set(selected_rua_ids)
    for f in ruas.getFeatures():
        if f.id() in selected_set:
            bf = QgsFeature(backup.fields())
            bf.setGeometry(f.geometry())
            for i in range(len(ruas.fields())):
                bf.setAttribute(i, f[i])
            backup_feats.append(bf)

if backup_feats:
    backup_pr.addFeatures(backup_feats)
backup.updateExtents()
QgsProject.instance().addMapLayer(backup)

# 4) Aplicar alinhamento na propria camada Ruas_MA sem commit
if updated_geoms:
    if not ruas.isEditable():
        ok_edit = ruas.startEditing()
        if not ok_edit:
            raise Exception("Nao foi possivel iniciar edicao em 'Ruas_MA'.")

    for fid, new_geom in updated_geoms.items():
        ruas.changeGeometry(fid, new_geom)

# 5) Criar camada resultado (pre-visualizacao do alinhamento)
# Remove camada anterior homonima
for lyr in list(QgsProject.instance().mapLayers().values()):
    if lyr.name() == NOME_SAIDA:
        QgsProject.instance().removeMapLayer(lyr.id())

out_uri = "{}?crs={}".format(QgsWkbTypes.displayString(ruas.wkbType()), ruas.crs().authid())
out = QgsVectorLayer(out_uri, NOME_SAIDA, "memory")
out_pr = out.dataProvider()
out_pr.addAttributes(ruas.fields())
out.updateFields()

new_feats = []
for f in output_feats:
    nf = QgsFeature(out.fields())
    nf.setGeometry(f.geometry())
    for i in range(len(ruas.fields())):
        nf.setAttribute(i, f[i])
    new_feats.append(nf)

if new_feats:
    out_pr.addFeatures(new_feats)
out.updateExtents()
QgsProject.instance().addMapLayer(out)

print("✅ Concluido.")
print("Rota(s) selecionada(s): {}".format(len(rotas.selectedFeatureIds())))
print("Quadras selecionadas em '{}': {}".format(NOME_CAMADA_QUADRAS, len(quadra_ids)))
print("Ruas alinhadas em '{}': {}".format(NOME_CAMADA_RUAS, len(selected_rua_ids)))
print("Edicao de 'Ruas_MA' ficou ABERTA e SEM COMMIT (pode cancelar/rollback).")
print("Camada backup criada: '{}'".format(NOME_BACKUP))
print("Camada de saida criada: '{}'".format(NOME_SAIDA))
