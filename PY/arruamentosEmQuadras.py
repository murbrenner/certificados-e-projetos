#NOME: Arruamentos em Quadras

#DESCRIÇÃO: Converte trechos de arruamento da camada 'ARRUAMENTO_MA' em polígonos de quadras, tratando fechamento de linhas e correções de geometria para gerar a camada de quadras no projeto.

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
    corrigida = processing.run("qgis:fixgeometries", {
        'INPUT': tmp_layer,
        'OUTPUT': 'memory:ARRUAMENTO_CORRIGIDO'
    })

    # polygoniza o resultado
    resultado = processing.run("qgis:polygonize", {
        'INPUT': corrigida['OUTPUT'],
        'KEEP_FIELDS': True,
        'OUTPUT': 'memory:QUADRAS_ARRUAMENTO'
    })

    # adiciona ao projeto
    QgsProject.instance().addMapLayer(resultado['OUTPUT'])

    print("✅ Processo concluído: linhas selecionadas corrigidas e convertidas em polígonos!")
