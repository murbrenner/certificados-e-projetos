#NOME: Buffer Zero

#DESCRIÇÃO: Executa a rotina 'Buffer Zero', aplicando operacoes de buffer e ajustes geometricos conforme os parametros definidos. Camadas envolvidas: 'QUADRAS_ARRUAMENTO'. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Carregar a camada 'QUADRAS_ARRUAMENTO' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


import processing
from qgis.core import QgsProject, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest

layer = QgsProject.instance().mapLayersByName('QUADRAS_ARRUAMENTO')
if not layer:
    print("Camada 'QUADRAS_ARRUAMENTO' não encontrada no projeto.")
else:
    layer = layer[0]
    if layer.selectedFeatureCount() == 0:
        print("Nenhuma feição selecionada em 'QUADRAS_ARRUAMENTO'. Selecione antes de executar.")
    else:
        print('Executando buffer 0 nas feições selecionadas...')
        buffer_result = processing.run('native:buffer', {
            'INPUT': QgsProcessingFeatureSourceDefinition(
                'QUADRAS_ARRUAMENTO',
                selectedFeaturesOnly=True,
                featureLimit=-1,
                geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
            ),
            'DISTANCE': 0.0,
            'SEGMENTS': 1,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'DISSOLVE': True,
            'SEPARATE_DISJOINT': True,
            'OUTPUT': 'memory:BUFFER_ZERO'
        })

        buffer_layer = buffer_result['OUTPUT']

        print('Corrigindo geometrias (fixgeometries)...')
        fix_result = processing.run('qgis:fixgeometries', {
            'INPUT': buffer_layer,
            'OUTPUT': 'memory:BUFFER_ZERO_FIXED'
        })

        final_layer = fix_result['OUTPUT']
        QgsProject.instance().addMapLayer(final_layer)

        print(f"Concluído: camada 'BUFFER_ZERO_FIXED' adicionada com {final_layer.featureCount()} feições.")
