#NOME: Inserir Dados nas Camadas Apartir da Rota

#DESCRIÇÃO: Insere dados, geometrias ou atributos nas camadas de destino conforme a rotina do script. Camadas envolvidas: 'ARRUAMENTO_MA', 'FIM_PNT', 'IMÓVEL', 'INICIO_PNT', 'OVERLEY'.

#PRÉ-REQUISITO: Carregar as camadas 'ARRUAMENTO_MA', 'FIM_PNT', 'IMÓVEL', 'INICIO_PNT', 'OVERLEY' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject

layerOverlay = QgsProject.instance().mapLayersByName("OVERLEY")[0]
layerImovel = QgsProject.instance().mapLayersByName("IMÓVEL")[0]
layerInicioPnt = QgsProject.instance().mapLayersByName("INICIO_PNT")[0]
layerFimPnt = QgsProject.instance().mapLayersByName("FIM_PNT")[0]
layerRotas = QgsProject.instance().mapLayersByName("ROTAS DE LEITURA")[0]
layerQuadras = QgsProject.instance().mapLayersByName("QUADRAS")[0]
layerArruamento = QgsProject.instance().mapLayersByName("ARRUAMENTO_MA")[0]

layerOverlay.startEditing()
layerImovel.startEditing()
layerInicioPnt.startEditing()
layerFimPnt.startEditing()
layerRotas.startEditing()
layerQuadras.startEditing()
layerArruamento.startEditing()

upd_local, ok = QInputDialog.getText(None, 'Inserir LOCALIDADE', 'Digite o número da LOCALIDADE:')
upd_local = int(upd_local)

upd_setor, ok = QInputDialog.getText(None, 'Inserir SETOR', 'Digite o número do SETOR:')
upd_setor = int(upd_setor)

upd_gerencia, ok = QInputDialog.getText(None, 'Inserir GERÊNCIA', 'Digite a GERÊNCIA:')
upd_gerencia = str(upd_gerencia)

upd_municipio, ok = QInputDialog.getText(None, 'Inserir MUNICÍPIO', 'Digite o MUNICÍPIO:')
upd_municipio = str(upd_municipio)

for rota in layerRotas.selectedFeatures():      
    layerRotas.selectByIds([rota.id()])        
    layerQuadras.removeSelection()

    processing.run("native:selectbylocation", {
        'INPUT':'IMÓVEL',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })    
    
    processing.run("native:selectbylocation", {
        'INPUT':'ARRUAMENTO_MA',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })
    
    processing.run("native:selectbylocation", {
        'INPUT':'QUADRAS',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })
    
    processing.run("native:selectbylocation", {
        'INPUT':'OVERLEY',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })
    
    processing.run("native:selectbylocation", {
        'INPUT':'INICIO_PNT',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })
    
    processing.run("native:selectbylocation", {
        'INPUT':'FIM_PNT',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('ROTAS DE LEITURA',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })         
            
    #upd_rota, ok = QInputDialog.getText(None, 'Inserir ROTA', 'Digite o número da ROTA:')
    upd_rota = rota['rota'] #int(upd_rota)

    print("ATUALIZANDO ROTA ->", upd_rota)

    rota['rota'] = upd_rota
    rota['setor'] = upd_setor  
    rota['gerencia'] = upd_gerencia
    rota['localidade'] = upd_local
    layerRotas.updateFeature(rota)     

    # Prepara expressões de latitude e longitude
    expr_lat = QgsExpression('$y')
    expr_lon = QgsExpression('$x')

    # Contexto da expressão
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layerImovel))

    for imovel in layerImovel.selectedFeatures():    
        imovel['rot_id'] = upd_rota 
        imovel['Setor'] = upd_setor
        imovel['gerencia'] = upd_gerencia
        imovel['visita_campo'] = imovel['seq_id']
        imovel['localidade'] = upd_local
        
        context.setFeature(imovel)
        lat = expr_lat.evaluate(context)
        lon = expr_lon.evaluate(context)
        imovel.setAttribute('latitude', lat)
        imovel.setAttribute('longitude', lon)

        layerImovel.selectByIds([imovel.id()])
        processing.run("native:selectbylocation", {
        'INPUT':'QUADRAS',
        'PREDICATE':[0],
        'INTERSECT':QgsProcessingFeatureSourceDefinition('IMÓVEL',
        selectedFeaturesOnly=True, 
        featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
        'METHOD':0
        })

        for quadra in layerQuadras.selectedFeatures():
            imovel['quadra'] = quadra['quadra']
            break

        layerImovel.updateFeature(imovel)


    for arruamento in layerArruamento.selectedFeatures():    
        arruamento['cd_setor'] = upd_setor 
        arruamento['nm_mun'] = upd_municipio
        arruamento['localidade'] = upd_local
        layerArruamento.updateFeature(arruamento)            

    for quadra in layerQuadras.selectedFeatures():
        quadra['rota'] = upd_rota 
        quadra['setor'] = upd_setor    
        quadra['gerencia'] = upd_gerencia
        quadra['localidade'] = upd_local
        layerQuadras.updateFeature(quadra)              

    for overlay in layerOverlay.selectedFeatures():      
        overlay['rota'] = upd_rota
        overlay['localidade '] = upd_local
        overlay['setor'] = upd_setor  
        overlay['gerencia '] = upd_gerencia  
        overlay['municipio'] = upd_municipio     
        layerOverlay.updateFeature(overlay)              
        
    for iniciopnt in layerInicioPnt.selectedFeatures():
        iniciopnt['Rota'] = upd_rota 
        iniciopnt['Setor'] = upd_setor     
        iniciopnt['Gerencia'] = upd_gerencia
        iniciopnt['localidade'] = upd_local
        layerInicioPnt.updateFeature(iniciopnt)             

    for fimpnt in layerFimPnt.selectedFeatures():    
        fimpnt['Rota '] = upd_rota 
        fimpnt['Setor'] = upd_setor   
        fimpnt['Gerencia'] = upd_gerencia
        fimpnt['localidade'] = upd_local
        layerFimPnt.updateFeature(fimpnt)           
        

        
#DESCOBRIR NOME CORRETO DOS ATRIBUTOS
# fields = layerOverlay.fields()
    # for field in fields:
    #     print(repr(field.name()))
