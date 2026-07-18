#NOME: Inserir Sequencia do CSV

#DESCRIÇÃO: Insere dados, geometrias ou atributos nas camadas de destino conforme a rotina do script. Inclui leitura e/ou exportacao de dados em CSV. Camadas envolvidas: 'IMÓVEL'.

#PRÉ-REQUISITO: Carregar a camada 'IMÓVEL' no projeto QGIS; selecionar previamente as feicoes que serao processadas; garantir arquivo CSV valido e no layout esperado.


from qgis.core import QgsProject, QgsExpression, QgsFeatureRequest
import pandas as pd

database = "C:\\CSV\\151.csv"
db = pd.read_csv(database)

layerImovel = QgsProject.instance().mapLayersByName("IMÓVEL")[0]
layerImovel.startEditing()

for i in db.index:
    sequencia = str(db['SEQUENCIA'][i]).strip()
    rota = str(db['ROTA'][i]).strip()
    matricula = str(db['MATRICULA'][i]).strip()    
    for imovel in layerImovel.selectedFeatures():  
        seq_id = str(imovel['seq_id']).strip()
        rot_id = str(imovel['rot_id']).strip()
        imv_id = str(imovel['imv_id']).strip()        
        if imv_id == matricula:
            if rot_id == rota:
                imovel.setAttribute('seq_id', sequencia)  # Aqui atualiza de fato o atributo
                layerImovel.updateFeature(imovel)         # Salva a mudança na camada
                print(sequencia, matricula, rota, "/", seq_id, imovel['imv_id'], imovel['rot_id'])
