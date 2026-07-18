#NOME: Inverter Sentido do Overlay

#DESCRIÇÃO: Executa a rotina 'Inverter Sentido do Overlay', invertendo sentido, ordem ou valores conforme a configuracao do script. Camadas envolvidas: 'OVERLEY'.

#PRÉ-REQUISITO: Carregar a camada 'OVERLEY' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject

layerOverlay = QgsProject.instance().mapLayersByName('OVERLEY')
if not layerOverlay:
	raise Exception("Camada 'OVERLEY' não encontrada no projeto")

layerOverlay = layerOverlay[0]

selected = list(layerOverlay.selectedFeatures())
if not selected:
	print('Nenhuma feição selecionada na camada OVERLEY. Nada a fazer.')
else:
	if not layerOverlay.isEditable():
		layerOverlay.startEditing()

	for feat in selected:
		geom = feat.geometry()
		if geom is None:
			continue
		
		if geom.isMultipart():
			parts = geom.asMultiPolyline()			
			new_parts = [list(reversed(p)) for p in parts]
			from qgis.core import QgsGeometry
			new_geom = QgsGeometry.fromMultiPolylineXY(new_parts)
		else:
			line = geom.asPolyline()
			if not line:				
				continue
			new_line = list(reversed(line))
			from qgis.core import QgsGeometry
			new_geom = QgsGeometry.fromPolylineXY(new_line)

		feat.setGeometry(new_geom)
		layerOverlay.updateFeature(feat)
