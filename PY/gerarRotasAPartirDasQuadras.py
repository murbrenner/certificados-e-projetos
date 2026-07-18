#NOME: Gerar Rotas Apartir das Quadras

#DESCRIÇÃO: Executa a rotina 'Gerar Rotas Apartir das Quadras', gerando dados/camadas de saida a partir das informacoes do projeto. Camadas envolvidas: 'QUADRAS', 'ROTAS DE LEITURA'. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Carregar as camadas 'QUADRAS', 'ROTAS DE LEITURA' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest, QgsVectorLayer, QgsField
from qgis.PyQt.QtCore import QVariant
import processing

# camadas de entrada
layerQuadras = QgsProject.instance().mapLayersByName("QUADRAS")[0]
layerRotas = QgsProject.instance().mapLayersByName("ROTAS DE LEITURA")[0]

# Gera buffer apenas das quadras selecionadas (distância inicial 13)
buffer_result = processing.run("native:buffer", {
    'INPUT': QgsProcessingFeatureSourceDefinition(
        'QUADRAS',
        selectedFeaturesOnly=True,
        featureLimit=-1,
        geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
    ),
    'DISTANCE': 13,
    'SEGMENTS': 1,
    'END_CAP_STYLE': 2,
    'JOIN_STYLE': 1,
    'MITER_LIMIT': 2,
    'DISSOLVE': True,
    'SEPARATE_DISJOINT': False,
    'OUTPUT': 'TEMPORARY_OUTPUT'
})

buffer_layer = buffer_result['OUTPUT']

rota, ok = QInputDialog.getText(None, 'Inserir ROTA', 'Digite o número da ROTA:')

# cria uma camada temporária em memória para armazenar o buffer final
mem_uri = 'Polygon?crs={}'.format(buffer_layer.crs().authid())
tmp_layer = QgsVectorLayer(mem_uri, f'ROTA-{rota}', 'memory')
pr = tmp_layer.dataProvider()
pr.addAttributes([QgsField('rota', QVariant.Int)])
tmp_layer.updateFields()

# pede rota uma vez (aplica a todas as feições geradas)
from qgis.PyQt.QtWidgets import QInputDialog
#rota, ok = QInputDialog.getText(None, 'Inserir ROTA', 'Digite o número da ROTA:')
if not ok:
    print('Operação cancelada pelo usuário')
else:
    try:
        rota = int(rota)
    except Exception:
        print('Valor de rota inválido; abortando')
        rota = None

    if rota is not None:
        # Para cada feição do buffer original, faz buffer com distance -9 (encolher) e depois buffer final 4
        for feat in buffer_layer.getFeatures():
            geom = feat.geometry()

            # buffer negativo (distance -9) - operar diretamente na geometria (evita chamada desnecessária ao processing)
            geom_buf1 = geom.buffer(-12, 1)
            # se o buffer1 for vazio, pula
            if geom_buf1.isEmpty():
                print('Buffer -9 eliminou a geometria, pulando')
                continue

            # aplica buffer final de 4
            geom_final = geom_buf1.buffer(3, 1)
            if geom_final.isEmpty():
                print('Buffer final resultou em geometria vazia, pulando')
                continue

            # cria nova feição na camada temporária
            from qgis.core import QgsFeature
            new_feat = QgsFeature(tmp_layer.fields())
            new_feat.setGeometry(geom_final)
            new_feat['rota'] = rota
            pr.addFeatures([new_feat])

        tmp_layer.updateExtents()

        # agora tmp_layer contém os buffers finais (distância efetiva: 13 -> -9 -> +4)
        # o usuário pediu para não inserir em layerRotas; caso queira, poderemos copiar as feições de tmp_layer para layerRotas depois.
        QgsProject.instance().addMapLayer(tmp_layer)
