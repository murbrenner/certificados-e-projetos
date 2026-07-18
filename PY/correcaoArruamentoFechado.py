#NOME: Correcao Arruamento Fechado

#DESCRIÇÃO: Executa a rotina 'Correcao Arruamento Fechado', corrigindo topologia e geometrias com base nas validacoes do script. Camadas envolvidas: 'ARRUAMENTO_MA'. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Carregar a camada 'ARRUAMENTO_MA' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


import processing
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsFields
from qgis.PyQt.QtCore import QVariant

layerArruamento = QgsProject.instance().mapLayersByName("ARRUAMENTO_MA")[0]

# verifica seleção
selected_feats = list(layerArruamento.selectedFeatures())
if not selected_feats:
    print('Nenhuma feição selecionada em ARRUAMENTO_MA. Nada a processar.')
else:
    # coletar todos os pontos de extremidade (start/end) das geometrias selecionadas
    pts = []  # lista de tuplas (QgsPointXY, feat_id, idx_part, idx_point)
    from qgis.core import QgsGeometry, QgsPointXY, QgsFeature, QgsVectorLayer
    from math import hypot

    for f in selected_feats:
        geom = f.geometry()
        if geom is None:
            continue
        if geom.isMultipart():
            parts = geom.asMultiPolyline()
            for pi, part in enumerate(parts):
                if not part:
                    continue
                start = QgsPointXY(part[0])
                end = QgsPointXY(part[-1])
                pts.append((start, f.id(), pi, 0))
                pts.append((end, f.id(), pi, len(part)-1))
        else:
            line = geom.asPolyline()
            if not line:
                continue
            start = QgsPointXY(line[0])
            end = QgsPointXY(line[-1])
            pts.append((start, f.id(), 0, 0))
            pts.append((end, f.id(), 0, len(line)-1))

    # verificar pares próximos (n^2). Distância em unidades da camada (assumindo metros)
    max_dist = 2.0
    connectors = []
    n = len(pts)
    for i in range(n):
        p1, f1, part1, idx1 = pts[i]
        for j in range(i+1, n):
            p2, f2, part2, idx2 = pts[j]
            if f1 == f2 and part1 == part2 and idx1 == idx2:
                continue
            dx = p1.x() - p2.x()
            dy = p1.y() - p2.y()
            d = hypot(dx, dy)
            if d <= max_dist:
                connectors.append((p1, p2))

    if not connectors:
        print('Nenhum conector necessário (nenhuma ponta dentro de 2 m).')
    else:
        # criar camada de memória com os conectores
        uri = 'LineString?crs=' + layerArruamento.crs().authid()
        conn_layer = QgsVectorLayer(uri, 'ARRUAMENTO_CONECTORES', 'memory')
        prov = conn_layer.dataProvider()

        feats = []
        for p1, p2 in connectors:
            feat_conn = QgsFeature()
            feat_conn.setGeometry(QgsGeometry.fromPolylineXY([p1, p2]))
            feats.append(feat_conn)

        prov.addFeatures(feats)
        conn_layer.updateExtents()
        # não adicionamos a camada de conectores separadamente ao mapa para evitar confusão

        # criar nova camada de memória que conterá todas as linhas selecionadas
        # mais os conectores; preservamos a camada original intacta
        uri_new = 'LineString?crs=' + layerArruamento.crs().authid()
        new_layer = QgsVectorLayer(uri_new, 'ARRUAMENTO_CONECTADO', 'memory')
        prov_new = new_layer.dataProvider()

        # copiar estrutura de campos da camada original
        prov_new.addAttributes(layerArruamento.fields())
        new_layer.updateFields()

        feats_to_add = []
        # adicionar as feições selecionadas (originais) à nova camada, preservando atributos
        for f in selected_feats:
            nf = QgsFeature(new_layer.fields())
            nf.setGeometry(f.geometry())
            nf.setAttributes(f.attributes())
            feats_to_add.append(nf)

        # adicionar os conectores como novas feições (atributos vazios)
        empty_attrs = [None] * len(new_layer.fields())
        for p1, p2 in connectors:
            cf = QgsFeature(new_layer.fields())
            cf.setGeometry(QgsGeometry.fromPolylineXY([p1, p2]))
            cf.setAttributes(empty_attrs)
            feats_to_add.append(cf)

        prov_new.addFeatures(feats_to_add)
        new_layer.updateExtents()
        QgsProject.instance().addMapLayer(new_layer)
        print(f'Criadas {len(connectors)} conexões e gerada camada "ARRUAMENTO_CONECTADO" com {len(feats_to_add)} feições (originais + conectores)')
