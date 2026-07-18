#NOME: Deletar Quadras Nulas

#DESCRIÇÃO: Remove da camada 'QUADRAS' as feições cujo atributo de identificação da quadra está nulo ou vazio, mantendo apenas registros válidos para continuidade do fluxo cadastral.

#PRÉ-REQUISITO: Carregar a camada 'QUADRAS' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject, QgsExpression, QgsFeatureRequest

layer = QgsProject.instance().mapLayersByName('QUADRAS')[0]

if layer and layer.selectedFeatureCount() > 0:
    layer.startEditing()

    # Expressão para pegar apenas as selecionadas com quadra IS NULL
    expr = QgsExpression('quadra IS NULL')
    request = QgsFeatureRequest(expr)

    # Filtra apenas dentro das selecionadas
    selected_ids = [f.id() for f in layer.selectedFeatures()]
    for f in layer.getFeatures(request):
        if f.id() in selected_ids:
            layer.deleteFeature(f.id())

    layer.commitChanges()
    #layer.triggerRepaint()
