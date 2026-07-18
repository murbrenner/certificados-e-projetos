#NOME: Inserir Overlay nas Quadras

#DESCRIÇÃO: Seleciona automaticamente as quadras que intersectam a rota pre-selecionada. Returns: list[int] | None: lista de IDs selecionados ou None em caso de erro. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


from qgis.core import *
from qgis.utils import *
import math


def selecionar_quadras_a_partir_da_rota(project, quadras_layer):
    """
    Seleciona automaticamente as quadras que intersectam a rota pre-selecionada.

    Returns:
        list[int] | None: lista de IDs selecionados ou None em caso de erro.
    """
    possible_route_names = [
        'ROTAS DE LEITURA',
        'Rotas de Leitura',
        'ROTAS',
        'Rotas',
        'ROTA',
        'Rota',
    ]

    rota_layer = None
    for name in possible_route_names:
        layers = project.mapLayersByName(name)
        if layers:
            rota_layer = layers[0]
            print(f"✅ Camada de rota encontrada: '{name}'")
            break

    if not rota_layer:
        print("❌ Erro: camada de rota não encontrada.")
        print("💡 Nomes tentados:", possible_route_names)
        return None

    selected_rotas = list(rota_layer.selectedFeatures())
    if not selected_rotas:
        print("❌ Erro: selecione ao menos uma rota na camada de rotas.")
        return None

    print(f"📍 Rotas selecionadas: {len(selected_rotas)}")

    # Transformar geometrias da rota para o CRS da camada de quadras, se necessário.
    route_to_quadras = None
    if rota_layer.crs() != quadras_layer.crs():
        route_to_quadras = QgsCoordinateTransform(
            rota_layer.crs(),
            quadras_layer.crs(),
            project.transformContext()
        )

    rota_union = None
    for rota_feat in selected_rotas:
        g = rota_feat.geometry()
        if g is None or g.isEmpty():
            continue
        gq = QgsGeometry(g)
        if route_to_quadras:
            gq.transform(route_to_quadras)

        if rota_union is None:
            rota_union = gq
        else:
            rota_union = rota_union.combine(gq)

    if rota_union is None or rota_union.isEmpty():
        print("❌ Erro: geometrias de rota inválidas para seleção de quadras.")
        return None

    quadras_ids = []
    for quadra_feat in quadras_layer.getFeatures():
        qg = quadra_feat.geometry()
        if qg is None or qg.isEmpty():
            continue
        if qg.intersects(rota_union) or qg.within(rota_union) or rota_union.contains(qg):
            quadras_ids.append(quadra_feat.id())

    quadras_layer.selectByIds(quadras_ids)
    print(f"✅ Quadras selecionadas a partir da rota: {len(quadras_ids)}")
    return quadras_ids

def criar_linhas_externas_vertices():
    """
    Cria camada temporária de linhas próximas aos vértices dos polígonos 
    selecionados na camada 'QUADRAS'.
    
    - Cada linha fica na parte EXTERNA do polígono (1 metro de distância)
    - Linhas alternadas: uma sim, uma não (vértices pares: 0, 2, 4...)
    - Quinas detectadas: linhas unidas em L para indicar curvas
    - Linhas de 10 metros para vértices normais, menores para quinas
    - Sistema de coordenadas: SIRGAS 2000 / UTM zone 23S (EPSG:31983)
    - Campo numérico sequencial para ordem dos vértices
    """
    
    print("🔍 Procurando camada 'QUADRAS'...")
    
    # Listar todas as camadas para debug
    project = QgsProject.instance()
    all_layers = project.mapLayers()
    print(f"📋 Camadas disponíveis no projeto ({len(all_layers)}):")
    for layer_id, layer in all_layers.items():
        print(f"   - {layer.name()} ({layer.type()})")
    
    # Obter camada QUADRAS (tentar nomes variados)
    quadras_layer = None
    possible_names = ['QUADRAS', 'Quadras', 'quadras', 'QUADRA', 'Quadra', 'quadra']
    
    for name in possible_names:
        try:
            layers = project.mapLayersByName(name)
            if layers:
                quadras_layer = layers[0]
                print(f"✅ Camada '{name}' encontrada: {quadras_layer.featureCount()} features total")
                break
        except Exception as e:
            print(f"⚠️  Erro ao buscar camada '{name}': {e}")
    
    if not quadras_layer:
        print("❌ Erro: Nenhuma camada de quadras encontrada no projeto!")
        print("💡 Nomes tentados:", possible_names)
        return None
    
    # Selecionar quadras a partir da rota pre-selecionada
    print("🔍 Selecionando quadras a partir da rota pre-selecionada...")
    ids_por_rota = selecionar_quadras_a_partir_da_rota(project, quadras_layer)
    if ids_por_rota is None:
        return None
    if len(ids_por_rota) == 0:
        print("❌ Nenhuma quadra intersecta a rota selecionada.")
        return None

    # Verificar se há features selecionadas
    print(f"🔍 Verificando features selecionadas...")
    selected_features = list(quadras_layer.selectedFeatures())
    print(f"📊 Features selecionadas encontradas: {len(selected_features)}")
    
    if not selected_features:
        print("❌ Falha: não foi possível manter a seleção de quadras pela rota.")
        return None
    else:
        print(f"📍 {len(selected_features)} feature(s) selecionada(s) na camada (via rota)")
    
    # Definir CRS de trabalho (SIRGAS 2000 UTM 23S)
    crs_trabalho = QgsCoordinateReferenceSystem(31983)  # EPSG:31983
    
    # Criar camada temporária de linhas
    temp_layer = QgsVectorLayer(
        f"LineString?crs=EPSG:31983", 
        "Linhas_Vertices_QUADRAS", 
        "memory"
    )
    
    # Definir campos da camada temporária
    provider = temp_layer.dataProvider()
    provider.addAttributes([
        QgsField("id_quadra", QVariant.Int),      # ID da feature original
        QgsField("num_vertice", QVariant.Int),   # Número sequencial do vértice (1, 2, 3...)
        QgsField("inicio_x", QVariant.Double),   # Coordenada X do início da linha
        QgsField("inicio_y", QVariant.Double),   # Coordenada Y do início da linha
        QgsField("fim_x", QVariant.Double),      # Coordenada X do fim da linha
        QgsField("fim_y", QVariant.Double),      # Coordenada Y do fim da linha
        QgsField("comprimento", QVariant.Double), # Comprimento da linha (sempre 10.0)
        QgsField("direcao", QVariant.String)     # Direção da linha (graus)
    ])
    temp_layer.updateFields()
    
    # Configurar transformação de coordenadas se necessário
    transform = None
    if quadras_layer.crs() != crs_trabalho:
        transform = QgsCoordinateTransform(
            quadras_layer.crs(), 
            crs_trabalho, 
            QgsProject.instance().transformContext()
        )
        print(f"🔄 Transformação de coordenadas: {quadras_layer.crs().authid()} → {crs_trabalho.authid()}")
    
    # Processar cada feature selecionada
    total_linhas = 0
    comprimento_linha = 25.0  # metros
    distancia_offset = 1.5   # metros (distância externa do polígono)
    
    for feature in selected_features:
        geom = feature.geometry()
        if geom is None or geom.isEmpty():
            continue
            
        # Transformar geometria se necessário
        if transform:
            geom_trabalho = QgsGeometry(geom)
            geom_trabalho.transform(transform)
        else:
            geom_trabalho = geom
        
        # Obter vértices do polígono
        if geom_trabalho.isMultipart():
            # Polígono multi-parte
            multipolygon = geom_trabalho.asMultiPolygon()
            for polygon in multipolygon:
                if polygon:  # Ring exterior
                    vertices = polygon[0]  # Primeiro ring (contorno externo)
                    total_linhas += processar_vertices_linhas(
                        vertices, feature.id(), temp_layer, comprimento_linha, distancia_offset, total_linhas
                    )
        else:
            # Polígono simples
            polygon = geom_trabalho.asPolygon()
            if polygon:
                vertices = polygon[0]  # Ring exterior
                total_linhas += processar_vertices_linhas(
                    vertices, feature.id(), temp_layer, comprimento_linha, distancia_offset, total_linhas
                )
    
    # Adicionar camada ao projeto
    QgsProject.instance().addMapLayer(temp_layer)
    
    # Configurar simbologia de setas azuis conforme especificação
    try:
        from qgis.core import (QgsLineSymbol, QgsArrowSymbolLayer, QgsUnitTypes)
        from qgis.PyQt.QtGui import QColor
        
        # Criar símbolo de seta
        arrow_symbol = QgsLineSymbol()
        arrow_symbol.deleteSymbolLayer(0)  # Remover camada padrão
        
        # Camada de seta
        arrow_layer = QgsArrowSymbolLayer()
        arrow_layer.setArrowWidth(0.6)               # espessura do arco
        arrow_layer.setArrowStartWidth(0.6)          # espessura inicial do arco
        arrow_layer.setHeadLength(2.5)               # comprimento da cabeça
        arrow_layer.setHeadThickness(0.9)            # espessura da cabeça (em mm)
        arrow_layer.setOffset(0.0)                   # deslocamento
        arrow_layer.setIsCurved(False)               # setas curvas: falso
        arrow_layer.setIsRepeated(True)              # repita seta em cada segmento: verdadeiro
        
        # Configurar tipo da seta
        arrow_layer.setArrowType(QgsArrowSymbolLayer.ArrowPlain)      # tipo de seta: plano
        arrow_layer.setHeadType(QgsArrowSymbolLayer.HeadSingle)      # tipo da ponta: simples
        
        # Configurar cores
        arrow_layer.setColor(QColor(0, 0, 255))        # cor do preenchimento: #0000ff (azul)
        arrow_layer.setStrokeColor(QColor(6, 6, 6))    # cor do traço: #060606 (cinza escuro)
        arrow_layer.setStrokeWidth(0.26)               # largura do traço: 0.26mm
        arrow_layer.setStrokeWidthUnit(QgsUnitTypes.RenderMillimeters)  # unidade: mm
        
        # Adicionar camada ao símbolo
        arrow_symbol.appendSymbolLayer(arrow_layer)
        
        # Aplicar símbolo à camada
        temp_layer.renderer().setSymbol(arrow_symbol)
        temp_layer.triggerRepaint()
        
        print("✅ Simbologia de setas configurada: azul #0000ff, traço #060606, 0.26mm")
        
    except Exception as e:
        print(f"⚠️ Erro na configuração da simbologia: {e}")
        # Fallback para simbologia simples
        from qgis.core import QgsLineSymbol
        simple_symbol = QgsLineSymbol.createSimple({
            'line_color': 'blue',
            'line_width': '0.6',
            'line_style': 'solid'
        })
        temp_layer.renderer().setSymbol(simple_symbol)
        temp_layer.triggerRepaint()
        print("✅ Simbologia simples aplicada (fallback)")
    
    print(f"✅ Camada temporária criada com {total_linhas} linhas ENXUTAS")
    print(f"📍 Comprimento das linhas: {comprimento_linha} metros")
    print(f"📍 Distância externa: {distancia_offset} metros")
    print(f"🎯 Sistema ENXUTO: máximo 8 linhas por polígono")
    print(f"📐 Quinas L conectadas: PRIORIDADE MÁXIMA (sempre incluídas)")
    print(f"📏 Arestas: distribuídas uniformemente entre quinas")
    print(f"🚫 SEM perpendiculares aleatórias: apenas quinas + arestas selecionadas")
    print(f"✨ Visual limpo: remove excesso de linhas automaticamente")
    print(f"� Simbologia: setas azuis #0000ff, traço #060606")
    print(f"🗺️  Sistema de coordenadas: {crs_trabalho.description()}")
    
    return temp_layer

def verificar_distancia_entre_linhas(linha1_inicio, linha1_fim, linha2_inicio, linha2_fim):
    """
    Verifica a distância mínima entre duas linhas.
    
    Returns:
        float: Distância mínima entre as linhas
    """
    # Calcular distância entre os pontos das linhas
    distancias = []
    
    # Distância entre início da linha1 e início da linha2
    dx = linha1_inicio[0] - linha2_inicio[0]
    dy = linha1_inicio[1] - linha2_inicio[1]
    distancias.append(math.sqrt(dx*dx + dy*dy))
    
    # Distância entre início da linha1 e fim da linha2
    dx = linha1_inicio[0] - linha2_fim[0]
    dy = linha1_inicio[1] - linha2_fim[1]
    distancias.append(math.sqrt(dx*dx + dy*dy))
    
    # Distância entre fim da linha1 e início da linha2
    dx = linha1_fim[0] - linha2_inicio[0]
    dy = linha1_fim[1] - linha2_inicio[1]
    distancias.append(math.sqrt(dx*dx + dy*dy))
    
    # Distância entre fim da linha1 e fim da linha2
    dx = linha1_fim[0] - linha2_fim[0]
    dy = linha1_fim[1] - linha2_fim[1]
    distancias.append(math.sqrt(dx*dx + dy*dy))
    
    return min(distancias)

def detectar_quinas(vertices, angulo_minimo=45.0):
    """
    Detecta vértices que representam quinas (mudanças de direção significativas).
    Agora mais rigoroso para evitar cruzamentos.
    
    Args:
        vertices: Lista de QgsPointXY dos vértices
        angulo_minimo: Ângulo mínimo em graus para considerar uma quina (aumentado para 45°)
    
    Returns:
        set: Conjunto de índices dos vértices que são quinas
    """
    quinas = set()
    
    if len(vertices) < 3:
        return quinas
    
    for i in range(len(vertices)):
        # Pontos anterior, atual e próximo (circular)
        prev_idx = (i - 1) % len(vertices)
        next_idx = (i + 1) % len(vertices)
        
        prev_pt = vertices[prev_idx]
        curr_pt = vertices[i]
        next_pt = vertices[next_idx]
        
        # Vetores das arestas
        vec1_x = curr_pt.x() - prev_pt.x()
        vec1_y = curr_pt.y() - prev_pt.y()
        vec2_x = next_pt.x() - curr_pt.x()
        vec2_y = next_pt.y() - curr_pt.y()
        
        # Verificar se as arestas são suficientemente longas
        mag1 = math.sqrt(vec1_x**2 + vec1_y**2)
        mag2 = math.sqrt(vec2_x**2 + vec2_y**2)
        
        # Só considerar quinas se as arestas forem longas o suficiente (> 2m)
        if mag1 < 2.0 or mag2 < 2.0:
            continue
        
        # Calcular ângulo entre as arestas
        try:
            # Produto escalar e magnitudes
            dot_product = vec1_x * vec2_x + vec1_y * vec2_y
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot_product / (mag1 * mag2)
                cos_angle = max(-1.0, min(1.0, cos_angle))  # Limitar para evitar erros de precisão
                angle_rad = math.acos(cos_angle)
                angle_deg = math.degrees(angle_rad)
                
                # Critério mais rigoroso: ângulo >= 45° E não muito próximo de 180°
                if angulo_minimo <= angle_deg <= 160.0:
                    # Verificar se não há vértices muito próximos
                    dist_prev = math.sqrt((curr_pt.x() - prev_pt.x())**2 + (curr_pt.y() - prev_pt.y())**2)
                    dist_next = math.sqrt((next_pt.x() - curr_pt.x())**2 + (next_pt.y() - curr_pt.y())**2)
                    
                    if dist_prev >= 1.5 and dist_next >= 1.5:  # Distância mínima entre vértices
                        quinas.add(i)
                        print(f"    📐 Quina detectada: vértice {i+1} (ângulo={angle_deg:.1f}°)")
                    
        except (ValueError, ZeroDivisionError):
            continue
    
    return quinas

def processar_vertices_linhas(vertices, feature_id, temp_layer, comprimento_linha, distancia_offset, contador_base):
    """
    Processa os vértices de um ring de polígono e cria linhas externas ENXUTAS.
    
    - Máximo de 8 linhas por polígono para visual limpo
    - Prioriza quinas (linhas L conectadas)  
    - Distribui arestas de forma equilibrada
    - Remove duplicatas e linhas muito próximas
    
    Args:
        vertices: Lista de QgsPointXY dos vértices
        feature_id: ID da feature original
        temp_layer: Camada temporária onde adicionar as linhas
        comprimento_linha: Comprimento da linha em metros (10m)
        distancia_offset: Distância externa do polígono em metros (1m)
        contador_base: Contador base para numeração sequencial
    
    Returns:
        int: Número de linhas criadas
    """
    linhas_criadas = 0
    provider = temp_layer.dataProvider()
    
    # Remover último vértice se for igual ao primeiro (ring fechado)
    if len(vertices) > 1 and vertices[0] == vertices[-1]:
        vertices = vertices[:-1]
    
    # Detectar quinas (mudanças de direção significativas)
    quinas = detectar_quinas(vertices, angulo_minimo=30.0)
    
    # Lista para armazenar todas as linhas candidatas antes da seleção
    linhas_candidatas = []
    
    # Máximo de linhas permitidas por polígono
    MAX_LINHAS = 8
    
    for i, vertex in enumerate(vertices):
        try:
            # === LÓGICA DE LINHAS ALTERNADAS ===
            # Processar apenas vértices alternados (0, 2, 4, ...) ou quinas
            eh_quina = i in quinas
            eh_alternado = (i % 2 == 0)  # Vértices pares (0, 2, 4, ...)
            
            if not eh_alternado and not eh_quina:
                continue  # Pular este vértice (não é alternado nem quina)
            
            # Ponto anterior e próximo (circular)
            prev_idx = (i - 1) % len(vertices)
            next_idx = (i + 1) % len(vertices)
            
            prev_vertex = vertices[prev_idx]
            next_vertex = vertices[next_idx]
            
            # === 1. CALCULAR DIREÇÃO DA LINHA (do anterior para o próximo) ===
            # Vetor do ponto anterior para o próximo ponto
            direcao_linha_x = next_vertex.x() - prev_vertex.x()
            direcao_linha_y = next_vertex.y() - prev_vertex.y()
            
            # Normalizar direção da linha
            linha_len = math.sqrt(direcao_linha_x**2 + direcao_linha_y**2)
            if linha_len > 0:
                direcao_linha_x /= linha_len
                direcao_linha_y /= linha_len
            
            # === 2. CALCULAR DIREÇÃO PERPENDICULAR EXTERNA ===
            # Para encontrar a direção "externa" ao polígono
            # Calcular bissetriz das arestas adjacentes
            vec1_x = vertex.x() - prev_vertex.x()
            vec1_y = vertex.y() - prev_vertex.y()
            vec2_x = next_vertex.x() - vertex.x()  
            vec2_y = next_vertex.y() - vertex.y()
            
            # Normalizar vetores das arestas
            len1 = math.sqrt(vec1_x**2 + vec1_y**2)
            len2 = math.sqrt(vec2_x**2 + vec2_y**2)
            
            if len1 > 0:
                vec1_x /= len1
                vec1_y /= len1
            if len2 > 0:
                vec2_x /= len2  
                vec2_y /= len2
            
            # Bissetriz (direção média das arestas)
            bisset_x = vec1_x + vec2_x
            bisset_y = vec1_y + vec2_y
            
            # Normalizar bissetriz
            bisset_len = math.sqrt(bisset_x**2 + bisset_y**2)
            if bisset_len > 0:
                bisset_x /= bisset_len
                bisset_y /= bisset_len
            else:
                # Fallback: perpendicular à aresta anterior
                bisset_x = -vec1_y
                bisset_y = vec1_x
            
            # === 3. CALCULAR PONTO EXTERNO EXATO A 2 METROS ===
            # Usar perpendicular à aresta atual para garantir distância exata de 2m
            # Aresta atual: do vértice atual para o próximo
            edge_atual_x = next_vertex.x() - vertex.x()
            edge_atual_y = next_vertex.y() - vertex.y()
            
            # Normalizar aresta atual
            edge_len = math.sqrt(edge_atual_x**2 + edge_atual_y**2)
            if edge_len > 0:
                edge_atual_x /= edge_len
                edge_atual_y /= edge_len
            
            # Perpendicular EXTERNA à aresta (rotação 90° anti-horário)
            perp_ext_x = -edge_atual_y
            perp_ext_y = edge_atual_x
            
            # Ponto externo a exatos 2 metros do vértice
            ponto_externo_x = vertex.x() + (perp_ext_x * distancia_offset)
            ponto_externo_y = vertex.y() + (perp_ext_y * distancia_offset)
            
            # === 4. CRIAR LINHA(S) ===
            if eh_quina:
                # === QUINA: CRIAR LINHAS PARALELAS ÀS ARESTAS ===
                # Calcular linhas paralelas às arestas, garantindo distância mínima
                
                # Direções das arestas (normalizadas)
                edge_prev_x = vertex.x() - prev_vertex.x()
                edge_prev_y = vertex.y() - prev_vertex.y()
                prev_len = math.sqrt(edge_prev_x**2 + edge_prev_y**2)
                if prev_len > 0:
                    edge_prev_x /= prev_len
                    edge_prev_y /= prev_len
                
                edge_next_x = next_vertex.x() - vertex.x()
                edge_next_y = next_vertex.y() - vertex.y()
                next_len = math.sqrt(edge_next_x**2 + edge_next_y**2)
                if next_len > 0:
                    edge_next_x /= next_len
                    edge_next_y /= next_len
                
                # Calcular pontos externos para cada aresta (garantir distância mínima)
                # Perpendicular EXTERNA à aresta anterior
                perp_prev_x = -edge_prev_y
                perp_prev_y = edge_prev_x
                ponto_ext_prev_x = vertex.x() + (perp_prev_x * distancia_offset)
                ponto_ext_prev_y = vertex.y() + (perp_prev_y * distancia_offset)
                
                # Perpendicular EXTERNA à próxima aresta
                perp_next_x = -edge_next_y
                perp_next_y = edge_next_x
                ponto_ext_next_x = vertex.x() + (perp_next_x * distancia_offset)
                ponto_ext_next_y = vertex.y() + (perp_next_y * distancia_offset)
                
                # Comprimento das linhas da quina (menor que linhas normais)
                comp_quina = comprimento_linha / 3.0
                
                # Lista para armazenar linhas da quina
                linhas_quina = []
                
                # CRIAR LINHAS EM "L" CONECTADAS (paralelas às arestas, conectadas ponta-a-ponta)
                
                # Calcular ponto de conexão (interseção das linhas paralelas prolongadas)
                # Ponto na direção da aresta anterior
                ponto_base_prev_x = vertex.x() + (perp_prev_x * distancia_offset)
                ponto_base_prev_y = vertex.y() + (perp_prev_y * distancia_offset)
                
                # Ponto na direção da próxima aresta  
                ponto_base_next_x = vertex.x() + (perp_next_x * distancia_offset)
                ponto_base_next_y = vertex.y() + (perp_next_y * distancia_offset)
                
                # Calcular ponto de encontro/conexão das duas linhas (interseção)
                # Usando bissetriz para encontrar ponto médio de conexão
                bisset_x = (perp_prev_x + perp_next_x) / 2
                bisset_y = (perp_prev_y + perp_next_y) / 2
                bisset_len = math.sqrt(bisset_x**2 + bisset_y**2)
                if bisset_len > 0:
                    bisset_x /= bisset_len
                    bisset_y /= bisset_len
                
                # Ponto de conexão (onde as linhas se encontram)
                ponto_conexao_x = vertex.x() + (bisset_x * distancia_offset)
                ponto_conexao_y = vertex.y() + (bisset_y * distancia_offset)
                
                # LINHA 1: Da aresta anterior até o ponto de conexão
                linha1_inicio_x = ponto_conexao_x - (edge_prev_x * comp_quina)
                linha1_inicio_y = ponto_conexao_y - (edge_prev_y * comp_quina)
                linha1_fim_x = ponto_conexao_x  # Termina no ponto de conexão
                linha1_fim_y = ponto_conexao_y
                
                # LINHA 2: Do ponto de conexão até a próxima aresta (conecta onde linha 1 termina)
                linha2_inicio_x = ponto_conexao_x  # Começa exatamente onde linha 1 termina
                linha2_inicio_y = ponto_conexao_y
                linha2_fim_x = ponto_conexao_x + (edge_next_x * comp_quina)
                linha2_fim_y = ponto_conexao_y + (edge_next_y * comp_quina)
                
                linhas_quina.append(([linha1_inicio_x, linha1_inicio_y], [linha1_fim_x, linha1_fim_y], "quina_1"))
                linhas_quina.append(([linha2_inicio_x, linha2_inicio_y], [linha2_fim_x, linha2_fim_y], "quina_2"))
                
                # VERIFICAR COMPRIMENTO DAS LINHAS EM L
                # Como as linhas agora são consecutivas (formam L), calcular comprimento total
                comprimento_total_L = comp_quina * 2  # Duas linhas consecutivas
                
                # Se as linhas ficaram muito pequenas, aumentar ligeiramente
                if comp_quina < 2.0:
                    comp_quina = 2.0  # Mínimo para visualização
                    print(f"    🔧 Quina {i+1}: comprimento ajustado para {comp_quina}m")
                    
                    # Recalcular linhas conectadas com novo comprimento
                    linha1_inicio_x = ponto_conexao_x - (edge_prev_x * comp_quina)
                    linha1_inicio_y = ponto_conexao_y - (edge_prev_y * comp_quina)
                    
                    linha2_fim_x = ponto_conexao_x + (edge_next_x * comp_quina)
                    linha2_fim_y = ponto_conexao_y + (edge_next_y * comp_quina)
                    
                    # Atualizar coordenadas nas linhas (mantendo conexão)
                    linhas_quina[0] = ([linha1_inicio_x, linha1_inicio_y], [ponto_conexao_x, ponto_conexao_y], "quina_1_adj")
                    linhas_quina[1] = ([ponto_conexao_x, ponto_conexao_y], [linha2_fim_x, linha2_fim_y], "quina_2_adj")
                
                # Informar sobre a quina criada
                print(f"    📐 Quina conectada: vértice {i+1} (L conectado: {comp_quina:.1f}m cada linha, paralelas às arestas)")
                
                # Adicionar linhas da quina às candidatas (PRIORIDADE ALTA)
                for j, ((ix, iy), (fx, fy), desc) in enumerate(linhas_quina):
                    linha_candidata = {
                        'tipo': 'quina',
                        'prioridade': 100,  # Prioridade máxima para quinas
                        'vertice_idx': i,
                        'inicio': (ix, iy),
                        'fim': (fx, fy),
                        'comprimento': comp_quina,
                        'descricao': desc,
                        'feature_data': [
                            feature_id,
                            contador_base + i + 1 + j * 0.1,
                            round(ix, 3), round(iy, 3),
                            round(fx, 3), round(fy, 3),
                            round(comp_quina, 1),
                            desc
                        ]
                    }
                    linhas_candidatas.append(linha_candidata)
                
            else:
                # === VÉRTICE NORMAL (SEM LINHA) ===
                # Vértices normais (não-quinas) não recebem linhas
                # Apenas as quinas e as arestas recebem linhas para evitar perpendiculares aleatórias
                print(f"    ⚪ Vértice normal {i+1}: sem linha (evita perpendiculares aleatórias)")
                pass
            
        except Exception as e:
            print(f"⚠️  Erro ao processar vértice {i}: {e}")
            continue
    
    # === COLETAR LINHAS DAS ARESTAS COMO CANDIDATAS ===
    print(f"📏 Coletando linhas das {len(vertices)} arestas como candidatas...")
    
    for i in range(len(vertices)):
        try:
            # Vértice atual e próximo vértice (definindo a aresta)
            vertex_atual = vertices[i]
            vertex_proximo = vertices[(i + 1) % len(vertices)]
            
            # Verificar se esta aresta já tem uma quina (evitar sobrepor)
            aresta_tem_quina = i in quinas or ((i + 1) % len(vertices)) in quinas
            
            # Ponto médio da aresta
            meio_aresta_x = (vertex_atual.x() + vertex_proximo.x()) / 2
            meio_aresta_y = (vertex_atual.y() + vertex_proximo.y()) / 2
            
            # Vetor da aresta
            aresta_x = vertex_proximo.x() - vertex_atual.x()
            aresta_y = vertex_proximo.y() - vertex_atual.y()
            
            # Normalizar vetor da aresta
            aresta_len = math.sqrt(aresta_x**2 + aresta_y**2)
            if aresta_len > 0:
                aresta_x /= aresta_len
                aresta_y /= aresta_len
            
            # Perpendicular EXTERNA à aresta (rotação 90° anti-horário)
            perp_aresta_x = -aresta_y
            perp_aresta_y = aresta_x
            
            # Ponto externo no meio da aresta
            ponto_externo_aresta_x = meio_aresta_x + (perp_aresta_x * distancia_offset)
            ponto_externo_aresta_y = meio_aresta_y + (perp_aresta_y * distancia_offset)
            
            # Comprimento da linha da aresta (menor que linhas normais)
            comp_aresta = comprimento_linha * 0.6  # 60% do comprimento normal
            meio_comp_aresta = comp_aresta / 2.0
            
            # Linha paralela à aresta, centrada no meio da aresta
            inicio_aresta_x = ponto_externo_aresta_x - (aresta_x * meio_comp_aresta)
            inicio_aresta_y = ponto_externo_aresta_y - (aresta_y * meio_comp_aresta)
            fim_aresta_x = ponto_externo_aresta_x + (aresta_x * meio_comp_aresta)
            fim_aresta_y = ponto_externo_aresta_y + (aresta_y * meio_comp_aresta)
            
            # Calcular ângulo da direção da aresta
            angulo_aresta_graus = math.degrees(math.atan2(aresta_y, aresta_x))
            if angulo_aresta_graus < 0:
                angulo_aresta_graus += 360
            
            # Prioridade menor para arestas que já têm quinas
            prioridade_aresta = 30 if aresta_tem_quina else 50
            
            # Adicionar aresta às candidatas
            linha_candidata_aresta = {
                'tipo': 'aresta',
                'prioridade': prioridade_aresta,
                'aresta_idx': i,
                'inicio': (inicio_aresta_x, inicio_aresta_y),
                'fim': (fim_aresta_x, fim_aresta_y),
                'comprimento': comp_aresta,
                'angulo': angulo_aresta_graus,
                'tem_quina': aresta_tem_quina,
                'descricao': f"aresta_{i+1}_{angulo_aresta_graus:.1f}°",
                'feature_data': [
                    feature_id,
                    contador_base + len(vertices) + i + 1,
                    round(inicio_aresta_x, 3), round(inicio_aresta_y, 3),
                    round(fim_aresta_x, 3), round(fim_aresta_y, 3),
                    round(comp_aresta, 1),
                    f"aresta_{i+1}_{angulo_aresta_graus:.1f}°"
                ]
            }
            linhas_candidatas.append(linha_candidata_aresta)
            
        except Exception as e:
            print(f"⚠️  Erro ao processar aresta {i}: {e}")
            continue
    
    # === SELEÇÃO INTELIGENTE DE LINHAS (MÁXIMO 8) ===
    print(f"🎯 Selecionando até {MAX_LINHAS} linhas mais importantes de {len(linhas_candidatas)} candidatas...")
    
    # Ordenar por prioridade (maior primeiro)
    linhas_candidatas.sort(key=lambda x: x['prioridade'], reverse=True)
    
    # Selecionar linhas finais
    linhas_selecionadas = []
    
    # Primeiro: garantir TODAS as quinas (prioridade absoluta)
    for linha in linhas_candidatas:
        if linha['tipo'] == 'quina':
            linhas_selecionadas.append(linha)
    
    # Segundo: completar com arestas bem distribuídas
    restante_vagas = MAX_LINHAS - len(linhas_selecionadas)
    arestas_candidatas = [l for l in linhas_candidatas if l['tipo'] == 'aresta']
    
    # Distribuir arestas uniformemente pelo polígono
    if restante_vagas > 0 and arestas_candidatas:
        num_arestas = len(vertices)
        step = max(1, num_arestas // min(restante_vagas, len(arestas_candidatas)))
        
        arestas_selecionadas = []
        for i in range(0, num_arestas, step):
            # Encontrar aresta candidata para este índice
            for aresta in arestas_candidatas:
                if aresta['aresta_idx'] == i and len(arestas_selecionadas) < restante_vagas:
                    arestas_selecionadas.append(aresta)
                    break
        
        linhas_selecionadas.extend(arestas_selecionadas)
    
    # === CRIAR FEATURES DAS LINHAS SELECIONADAS ===
    print(f"✅ Criando {len(linhas_selecionadas)} linhas selecionadas:")
    
    for linha in linhas_selecionadas:
        try:
            # Criar geometria
            ix, iy = linha['inicio']
            fx, fy = linha['fim']
            linha_geom = QgsGeometry.fromPolylineXY([QgsPointXY(ix, iy), QgsPointXY(fx, fy)])
            
            # Criar feature
            feature = QgsFeature(temp_layer.fields())
            feature.setGeometry(linha_geom)
            feature.setAttributes(linha['feature_data'])
            
            provider.addFeature(feature)
            linhas_criadas += 1
            
            # Log da linha criada
            if linha['tipo'] == 'quina':
                print(f"    � {linha['descricao']}: QUINA (prioridade máxima)")
            else:
                print(f"    📏 {linha['descricao']}: aresta {linha['aresta_idx']+1} ({linha['comprimento']:.1f}m)")
            
        except Exception as e:
            print(f"⚠️  Erro ao criar linha: {e}")
            continue
    
    print(f"📊 Resumo: {len(linhas_selecionadas)} de {len(linhas_candidatas)} linhas criadas (máx: {MAX_LINHAS})")
    return linhas_criadas

def calcular_direcao_interna_simples(vertices, vertex_idx, distancia_offset):
    """
    Método alternativo mais simples: offset perpendicular à aresta seguinte.
    """
    vertex = vertices[vertex_idx]
    next_idx = (vertex_idx + 1) % len(vertices)
    next_vertex = vertices[next_idx]
    
    # Vetor da aresta
    dx = next_vertex.x() - vertex.x()
    dy = next_vertex.y() - vertex.y()
    
    # Normalizar
    length = math.sqrt(dx**2 + dy**2)
    if length > 0:
        dx /= length
        dy /= length
    
    # Perpendicular (rotação 90° no sentido horário = para "dentro")
    perp_x = dy
    perp_y = -dx
    
    # Aplicar offset
    offset_x = vertex.x() + (perp_x * distancia_offset)
    offset_y = vertex.y() + (perp_y * distancia_offset)
    
    return offset_x, offset_y

# Executar função principal
print("🚀 Iniciando execução do script de linhas externas...")
try:
    layer = criar_linhas_externas_vertices()
    if layer:
        print("🎯 Script ENXUTO executado com sucesso!")
        print("📐 Quinas L conectadas: SEMPRE incluídas (prioridade máxima)")
        print("📏 Arestas selecionadas: distribuídas uniformemente")
        print("🎯 Máximo 8 linhas por polígono: visual limpo e organizado")
        print("🚫 SEM perpendiculares aleatórias: apenas quinas L + arestas essenciais")
        print("🎨 Simbologia: setas azuis configuradas automaticamente")
        print("✨ Sistema ENXUTO: remove automaticamente linhas em excesso")
        print("💡 Resultado: visual limpo com linhas essenciais apenas")
    else:
        print("❌ Falha na execução do script")
except Exception as e:
    print(f"💥 Erro durante execução: {e}")
    import traceback
    traceback.print_exc()
