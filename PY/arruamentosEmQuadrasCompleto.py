#NOME: Arruamentos em Quadras Completo

#DESCRIÇÃO: Executa o fluxo completo de geração de quadras a partir da camada 'ARRUAMENTO_MA', incluindo limpeza/correção das linhas, fechamento de contornos e criação dos polígonos finais.

#PRÉ-REQUISITO: Carregar a camada 'ARRUAMENTO_MA' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


import processing
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsFields, QgsPointXY, QgsGeometry
from qgis.PyQt.QtCore import QVariant

layerArruamento = QgsProject.instance().mapLayersByName("ARRUAMENTO_MA")[0]

# verifica seleção
selected_feats = list(layerArruamento.selectedFeatures())
if not selected_feats:
    print('Nenhuma feição selecionada em ARRUAMENTO_MA. Nada a processar.')
else:
    # cria uma camada temporária em memória contendo apenas as feições selecionadas
    crs = layerArruamento.crs().authid()
    tmp_uri = 'LineString?crs={}'.format(crs)
    tmp_layer = QgsVectorLayer(tmp_uri, 'arruamento_selected_tmp', 'memory')
    tmp_pr = tmp_layer.dataProvider()

    # copia campos
    tmp_pr.addAttributes(layerArruamento.fields())
    tmp_layer.updateFields()

    # cria e adiciona features selecionadas na camada temporária
    new_feats = []
    for f in selected_feats:
        nf = QgsFeature(tmp_layer.fields())
        nf.setGeometry(f.geometry())
        # copia atributos existentes (se houver)
        for i, field in enumerate(layerArruamento.fields()):
            try:
                nf.setAttribute(i, f[i])
            except Exception:
                pass
        new_feats.append(nf)

    tmp_pr.addFeatures(new_feats)
    tmp_layer.updateExtents()

    # aplica fixgeometries na camada temporária
    corrigida_res = processing.run("qgis:fixgeometries", {
        'INPUT': tmp_layer,
        'OUTPUT': 'memory:ARRUAMENTO_CORRIGIDO'
    })
    corrigida = corrigida_res['OUTPUT']

    # cria um spatial index para procurar a linha mais próxima
    from qgis.core import QgsSpatialIndex, QgsPointXY, QgsGeometry, QgsFeature
    index = QgsSpatialIndex()
    feats_by_id = {}
    for f in corrigida.getFeatures():
        index.insertFeature(f)
        feats_by_id[f.id()] = f

    # camada combinada (linhas corrigidas + conectores)
    crs = corrigida.crs().authid()
    combined_uri = 'LineString?crs={}'.format(crs)
    combined = QgsVectorLayer(combined_uri, 'arruamento_combined', 'memory')
    comb_pr = combined.dataProvider()
    # adiciona campos (opcional) - não estritamente necessário para polygonize
    comb_pr.addAttributes(corrigida.fields())
    combined.updateFields()

    # adiciona as feições corrigidas ao combined
    comb_feats = []
    for f in corrigida.getFeatures():
        nf = QgsFeature(combined.fields())
        nf.setGeometry(f.geometry())
        # copia atributos se existirem
        try:
            for i in range(len(corrigida.fields())):
                nf.setAttribute(i, f[i])
        except Exception:
            pass
        comb_feats.append(nf)

    # função auxiliar para extrair endpoints de uma geometria de linha
    def get_endpoints(geom):
        pts = []
        try:
            if geom.isMultipart():
                mparts = geom.asMultiPolyline()
                for part in mparts:
                    if len(part) >= 1:
                        pts.append(QgsPointXY(part[0]))
                        pts.append(QgsPointXY(part[-1]))
            else:
                part = geom.asPolyline()
                if len(part) >= 1:
                    pts.append(QgsPointXY(part[0]))
                    pts.append(QgsPointXY(part[-1]))
        except Exception:
            pass
        return pts

    # construir grafo de conectividade entre feições por endpoints (tolerância pequena)
    # e depois seguir cada componente para criar conectores finais de fechamento até 2 metros
    endpoints_list = []  # tuples (feat_id, pt_index, QgsPointXY)
    feat_endpoints = {}   # feat_id -> [QgsPointXY,...]
    small_tol = 0.001  # tolerância para considerar endpoints coincidentes (map units)
    closure_tol = 110.0  # tolerância para fechar polígonos com conector (map units)

    for f in corrigida.getFeatures():
        fid = f.id()
        geom = f.geometry()
        eps = get_endpoints(geom)
        feat_endpoints[fid] = eps
        for idx, p in enumerate(eps):
            endpoints_list.append((fid, idx, p))

    # construir adjacency: duas feições são adjacentes se algum endpoint estiver a <= small_tol
    neighbors = {fid: set() for fid in feat_endpoints.keys()}
    n = len(endpoints_list)
    for i in range(n):
        fid_i, idx_i, p_i = endpoints_list[i]
        for j in range(i+1, n):
            fid_j, idx_j, p_j = endpoints_list[j]
            if fid_i == fid_j:
                continue
            try:
                if p_i.distance(p_j) <= small_tol:
                    neighbors[fid_i].add(fid_j)
                    neighbors[fid_j].add(fid_i)
            except Exception:
                pass

    visited_feats = set()
    connectors = []
    created_connectors = 0
    components = 0

    # percorre cada feição selecionada e explora o componente conectado
    for start_f in feat_endpoints.keys():
        if start_f in visited_feats:
            continue
        # DFS para coletar feições do componente
        stack = [start_f]
        comp = set()
        while stack:
            cur = stack.pop()
            if cur in comp:
                continue
            comp.add(cur)
            for nb in neighbors.get(cur, []):
                if nb not in comp:
                    stack.append(nb)

        if not comp:
            continue
        components += 1
        visited_feats.update(comp)

        # coletar todos endpoints desse componente
        comp_points = []
        for fid in comp:
            for p in feat_endpoints.get(fid, []):
                comp_points.append((fid, p))

        # tentar fechar: para cada ponto do componente, buscar outro ponto do componente (não mesmo coordenada)
        # dentro de closure_tol e criar conector se necessário
        seen_conn = set()
        for fid_a, pt_a in comp_points:
            for fid_b, pt_b in comp_points:
                if fid_a == fid_b:
                    continue
                try:
                    if pt_a.distance(pt_b) <= closure_tol:
                        a = (round(pt_a.x(),3), round(pt_a.y(),3))
                        b = (round(pt_b.x(),3), round(pt_b.y(),3))
                        key = tuple(sorted([a,b]))
                        if key in seen_conn:
                            continue
                        seen_conn.add(key)
                        conn_geom = QgsGeometry.fromPolylineXY([pt_a, pt_b])
                        connectors.append(conn_geom)
                        created_connectors += 1
                except Exception:
                    pass

        # adiciona as feições do componente ao combined (já foram adicionadas globalmente antes, mas repetimos pra garantir)
        # (não removemos duplicatas, polygonize irá lidar com a topologia)
        # Nota: comb_feats já contém as feições originais

    # adiciona conectores como feições ao combined
    for cg in connectors:
        cf = QgsFeature(combined.fields())
        cf.setGeometry(cg)
        comb_feats.append(cf)

    # adiciona todas as feições ao combined layer
    comb_pr.addFeatures(comb_feats)
    combined.updateExtents()

    # polygoniza o combined (linhas corrigidas + conectores)
    resultado = processing.run("qgis:polygonize", {
        'INPUT': combined,
        'KEEP_FIELDS': True,
        'OUTPUT': 'memory:QUADRAS_ARRUAMENTO'
    })

    # adiciona ao projeto
    out_layer = resultado['OUTPUT']
    QgsProject.instance().addMapLayer(out_layer)

    # relatório final
    num_input_feats = len(selected_feats)
    num_components = components
    num_connectors = created_connectors
    num_polygons = out_layer.featureCount() if out_layer is not None else 0

    print(f"✅ Processo concluído: {num_input_feats} linhas de entrada, {num_components} componentes detectados, {num_connectors} conectores criados, {num_polygons} polígonos gerados.")
