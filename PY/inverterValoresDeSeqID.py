#NOME: Inverter Valores de Seq ID

#DESCRIÇÃO: Executa a rotina 'Inverter Valores de Seq ID', invertendo sentido, ordem ou valores conforme a configuracao do script. Camadas envolvidas: 'IMÓVEL'.

#PRÉ-REQUISITO: Carregar a camada 'IMÓVEL' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject

layers = QgsProject.instance().mapLayersByName('IMÓVEL')
if not layers:
	raise Exception("Camada 'IMÓVEL' não encontrada no projeto")

layer = layers[0]

selected = list(layer.selectedFeatures())
if not selected:
	print('Nenhuma feição selecionada na camada IMÓVEL. Nada a fazer.')
else:
	# verifica existência do campo
	field_idx = layer.fields().indexOf('seq_id')
	if field_idx == -1:
		raise Exception("Campo 'seq_id' não encontrado na camada IMÓVEL")

	if not layer.isEditable():
		layer.startEditing()

	# função helper para ordenar valores de seq_id (tratando None/strings)
	def _seq_value(feat):
		v = feat['seq_id']
		try:
			# manter tipo numérico quando possível
			return float(v)
		except Exception:
			# valores inválidos vão para o final
			return float('inf')

	# separar feições com e sem valor válido
	with_val = [f for f in selected if f['seq_id'] is not None]
	without_val = [f for f in selected if f['seq_id'] is None]

	if not with_val:
		print('Nenhuma feição com seq_id definido. Nada a inverter.')
	else:
		# ordenar as feições com valor por seq_id asc
		feats_asc = sorted(with_val, key=_seq_value)
		values_asc = [f['seq_id'] for f in feats_asc]

		# atribuir os valores invertidos apenas entre essas feições
		for i, feat_desc in enumerate(reversed(feats_asc)):
			new_value = values_asc[i]
			layer.changeAttributeValue(feat_desc.id(), field_idx, new_value)

		print(f'{len(with_val)} feições com seq_id invertidas; {len(without_val)} sem seq_id mantidas.')
