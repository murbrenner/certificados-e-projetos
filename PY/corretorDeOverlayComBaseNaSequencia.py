#NOME: Corretor de Overlay com Base na Sequencia

#DESCRIÇÃO: Corrige a geometria/ordenação do overlay com base na sequência dos imóveis e nas rotas de leitura, usando as camadas 'IMÓVEL' e 'ROTAS DE LEITURA' para ajustar o traçado final no projeto.

#PRÉ-REQUISITO: Carregar as camadas 'IMÓVEL', 'ROTAS DE LEITURA' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import (
    QgsProject, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer,
    QgsField, QgsLineSymbol, QgsArrowSymbolLayer, QgsCoordinateTransform, QgsSpatialIndex
)
from PyQt5.QtCore import QVariant
import math

layerRotas = QgsProject.instance().mapLayersByName("ROTAS DE LEITURA")[0]
layerImovel = QgsProject.instance().mapLayersByName('IMÓVEL')[0]


for rota in layerRotas.selectedFeatures():      
    layerRotas.selectByIds([rota.id()])     
    layerImovel.removeSelection()

    processing.run("native:selectbylocation", {
        'INPUT':'IMÓVEL',
        'PREDICATE':[0,4,5,6,7],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })
    

    def gerarSetasParalelasQuadrasRapido():
        print("🔄 Iniciando geração das setas de fluxo paralelas às quadras (otimizado)...")

        nome_cam_imovel = "IMÓVEL"
        nome_cam_quadras = "QUADRAS"
        campo_seq = "seq_id"
        tamanho_seta_m = 1
        deslocamento_lateral = 2  # metros

        layer_imovel = QgsProject.instance().mapLayersByName(nome_cam_imovel)[0]
        layer_quadras = QgsProject.instance().mapLayersByName(nome_cam_quadras)[0]

        crs_projeto = QgsProject.instance().crs()
        crs_layer = layer_imovel.crs()
        transform = QgsCoordinateTransform(crs_layer, crs_projeto, QgsProject.instance())

        # Spatial index para quadras
        index = QgsSpatialIndex(layer_quadras.getFeatures())

        feats = list(layer_imovel.selectedFeatures())
        if not feats:
            print("⚠ Nenhum ponto selecionado.")
            return
        feats.sort(key=lambda f: f[campo_seq])

        vl = QgsVectorLayer(f"LineString?crs={crs_projeto.authid()}", f"OVERLAY ROTA {rota['rota']}", "memory")
        pr = vl.dataProvider()
        pr.addAttributes([QgsField("seq", QVariant.Int)])
        vl.updateFields()

        for i in range(len(feats) - 1):
            p1 = transform.transform(feats[i].geometry().asPoint())
            p2 = transform.transform(feats[i+1].geometry().asPoint())

            # Buscar quadras próximas (dentro de 50m)
            nearby_ids = index.nearestNeighbor(p1, 5)  # pega até 5 quadras mais próximas
            vet_x, vet_y = 0, 0
            min_dist = float('inf')
            for fid in nearby_ids:
                quadra = layer_quadras.getFeature(fid)
                geom = quadra.geometry()
                if geom is None or geom.isEmpty():
                    continue
                # Segue mesma lógica de vetores para Polygon ou MultiPolygon
                polygons = geom.asMultiPolygon() if geom.isMultipart() else [geom.asPolygon()]
                for poly in polygons:
                    if not poly or len(poly[0]) < 2:
                        continue
                    pts = poly[0]
                    for idx in range(len(pts)-1):
                        a = pts[idx]
                        b = pts[idx+1]
                        dx_seg = b.x() - a.x()
                        dy_seg = b.y() - a.y()
                        seg_len = math.hypot(dx_seg, dy_seg)
                        if seg_len == 0:
                            continue
                        t = ((p1.x() - a.x())*dx_seg + (p1.y() - a.y())*dy_seg)/(seg_len**2)
                        t = max(0, min(1, t))
                        proj_x = a.x() + t*dx_seg
                        proj_y = a.y() + t*dy_seg
                        dist = math.hypot(p1.x()-proj_x, p1.y()-proj_y)
                        if dist < min_dist:
                            min_dist = dist
                            vet_x, vet_y = dx_seg, dy_seg

            dist = math.hypot(vet_x, vet_y)
            if dist == 0:
                continue

            nx = -vet_y / dist
            ny = vet_x / dist

            p1_desloc = QgsPointXY(p1.x() + nx * deslocamento_lateral,
                                p1.y() + ny * deslocamento_lateral)
            p2_desloc = QgsPointXY(p2.x() + nx * deslocamento_lateral,
                                p2.y() + ny * deslocamento_lateral)

            fet = QgsFeature(vl.fields())
            fet.setGeometry(QgsGeometry.fromPolylineXY([p1_desloc, p2_desloc]))
            fet.setAttribute("seq", feats[i][campo_seq])
            pr.addFeature(fet)

        symbol = QgsLineSymbol()
        arrow_layer = QgsArrowSymbolLayer()
        arrow_layer.setArrowWidth(tamanho_seta_m)
        arrow_layer.setHeadLength(4)
        arrow_layer.setHeadThickness(2)
        arrow_layer.setArrowType(0)
        symbol.changeSymbolLayer(0, arrow_layer)
        vl.renderer().setSymbol(symbol)

        QgsProject.instance().addMapLayer(vl)
        print("✅ Setas de fluxo paralelas geradas com sucesso!")
        

    gerarSetasParalelasQuadrasRapido()
