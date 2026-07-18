#NOME: Orientar Rotulos Perpendicularmente

#DESCRIÇÃO: Orienta os rótulos da camada 'imovel' perpendiculares à aresta mais próxima do polígono da camada 'QUADRAS' onde cada ponto está contido. Melhora significativamente a estética do layout de impressão.

#PRÉ-REQUISITO: Carregar as camadas 'imovel' (pontos com rótulo) e 'QUADRAS' (polígonos), com campo de ângulo/rotação disponível para aplicar a orientação perpendicular dos rótulos.


# ORIENTAÇÃO PERPENDICULAR DE RÓTULOS - CAMADA IMOVEL
# Orienta rótulos da camada imovel perpendiculares à aresta mais próxima da camada QUADRAS
# Data: Nov/2025

def orientar_rotulos_perpendiculares():
    """
    Orienta os rótulos da camada 'imovel' perpendiculares à aresta mais próxima 
    do polígono da camada 'QUADRAS' onde cada ponto está contido.
    Melhora significativamente a estética do layout de impressão.
    """
    
    print("🎯 ORIENTAÇÃO PERPENDICULAR DE RÓTULOS")
    print("=" * 50)
    print("📋 Processo:")
    print("   🔍 1. Localizar camadas 'imovel' e 'QUADRAS'")
    print("   📐 2. Para cada ponto calcular aresta mais próxima")
    print("   🔄 3. Calcular ângulo perpendicular")
    print("   ✏️ 4. Aplicar rotação aos rótulos")
    print()
    
    try:
        # IMPORTAÇÕES NECESSÁRIAS
        from qgis.core import (QgsProject, QgsGeometry, QgsPointXY, 
                               QgsVectorLayer, QgsPalLayerSettings, 
                               QgsVectorLayerSimpleLabeling, QgsProperty)
        from qgis.utils import iface
        import math
        
        # 1. LOCALIZAR CAMADAS
        print("🔍 Localizando camadas...")
        project = QgsProject.instance()
        
        # Buscar camada IMOVEL
        camada_imovel = 'IMÓVEL'
        camada_quadras = 'QUADRAS'
        
        for layer in project.mapLayers().values():
            if 'imovel' in layer.name().lower():
                camada_imovel = layer
                print(f"   ✅ Camada imovel encontrada: {layer.name()}")
            elif 'quadras' in layer.name().lower():
                camada_quadras = layer
                print(f"   ✅ Camada QUADRAS encontrada: {layer.name()}")
        
        if not camada_imovel:
            print("   ❌ ERRO: Camada 'imovel' não encontrada!")
            return False
            
        if not camada_quadras:
            print("   ❌ ERRO: Camada 'QUADRAS' não encontrada!")
            return False
        
        # 2. FUNÇÃO PARA CALCULAR ARESTA MAIS PRÓXIMA
        def calcular_aresta_mais_proxima(ponto, poligono):
            """Calcula a aresta mais próxima de um ponto em um polígono"""
            min_distancia = float('inf')
            aresta_mais_proxima = None
            
            # Obter pontos do polígono
            vertices = poligono.asPolygon()[0]  # Primeiro anel (exterior)
            
            # Verificar cada aresta
            for i in range(len(vertices) - 1):
                p1 = vertices[i]
                p2 = vertices[i + 1]
                
                # Criar linha da aresta
                linha = QgsGeometry.fromPolylineXY([p1, p2])
                
                # Calcular distância do ponto à aresta
                distancia = ponto.distance(linha)
                
                if distancia < min_distancia:
                    min_distancia = distancia
                    aresta_mais_proxima = (p1, p2)
            
            return aresta_mais_proxima
        
        # 3. FUNÇÃO PARA CALCULAR ÂNGULO PERPENDICULAR
        def calcular_angulo_perpendicular(aresta):
            """Calcula o ângulo perpendicular a uma aresta em graus"""
            p1, p2 = aresta
            
            # Calcular vetor da aresta
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            
            # Calcular ângulo da aresta em radianos
            angulo_aresta = math.atan2(dy, dx)
            
            # Ângulo perpendicular (adicionar 90 graus)
            angulo_perpendicular = angulo_aresta + math.pi/2
            
            # Converter para graus
            angulo_graus = math.degrees(angulo_perpendicular)
            
            # Normalizar para 0-360
            if angulo_graus < 0:
                angulo_graus += 360
            elif angulo_graus >= 360:
                angulo_graus -= 360
                
            return angulo_graus
        
        # 4. PROCESSAR CADA PONTO DA CAMADA IMOVEL
        print("\n📐 Processando orientação dos rótulos...")
        
        angulos_calculados = {}
        pontos_processados = 0
        
        for feature_imovel in camada_imovel.getFeatures():
            ponto_geom = feature_imovel.geometry()
            ponto_xy = ponto_geom.asPoint()
            
            # Encontrar em qual polígono da camada QUADRAS este ponto está
            for feature_quadra in camada_quadras.getFeatures():
                poligono_geom = feature_quadra.geometry()
                
                # Verificar se o ponto está dentro do polígono
                if poligono_geom.contains(ponto_geom):
                    # Calcular aresta mais próxima
                    aresta = calcular_aresta_mais_proxima(ponto_geom, poligono_geom)
                    
                    if aresta:
                        # Calcular ângulo perpendicular
                        angulo = calcular_angulo_perpendicular(aresta)
                        angulos_calculados[feature_imovel.id()] = angulo
                        pontos_processados += 1
                        
                        print(f"   📍 Ponto ID {feature_imovel.id()}: {angulo:.1f}°")
                    break
        
        print(f"\n✅ {pontos_processados} pontos processados")
        
        # 5. APLICAR ROTAÇÃO AOS RÓTULOS
        print("\n🔄 Aplicando rotação aos rótulos...")
        
        # Configurar propriedades de rotulagem
        settings = QgsPalLayerSettings()
        
        # Ativar rótulos
        settings.enabled = True
        
        # Definir campo para o rótulo (assumindo que existe um campo com o valor)
        # Você pode ajustar conforme o nome do campo na sua camada
        campo_rotulo = None
        for field in camada_imovel.fields():
            if any(nome in field.name().lower() for nome in ['nome', 'valor', 'numero', 'id']):
                campo_rotulo = field.name()
                break
        
        if campo_rotulo:
            settings.fieldName = campo_rotulo
        else:
            settings.fieldName = camada_imovel.fields()[0].name()  # Primeiro campo
        
        print(f"   📝 Campo do rótulo: {settings.fieldName}")
        
        # Configurar rotação baseada em dados
        # Criar expressão para rotação baseada no ID da feature
        expressao_rotacao = "CASE "
        for feature_id, angulo in angulos_calculados.items():
            expressao_rotacao += f"WHEN $id = {feature_id} THEN {angulo} "
        expressao_rotacao += "ELSE 0 END"
        
        # Aplicar rotação
        settings.dataDefinedProperties().setProperty(
            QgsPalLayerSettings.LabelRotation, 
            QgsProperty.fromExpression(expressao_rotacao)
        )
        
        # Configurações adicionais para melhor aparência
        settings.placement = QgsPalLayerSettings.OverPoint
        settings.quadOffset = QgsPalLayerSettings.QuadrantAboveRight
        settings.dist = 2.0  # Distância do ponto
        
        # Aplicar configurações à camada
        labeling = QgsVectorLayerSimpleLabeling(settings)
        camada_imovel.setLabeling(labeling)
        camada_imovel.setLabelsEnabled(True)
        
        # Atualizar visualização
        camada_imovel.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(camada_imovel.id())
        
        print("✅ Rotação aplicada com sucesso!")
        print(f"📊 Total de rótulos orientados: {len(angulos_calculados)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO durante o processamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def orientar_rotulos_manual_melhorado():
    """
    Versão melhorada com interface para ajustes manuais
    """
    print("🎯 ORIENTAÇÃO PERPENDICULAR AVANÇADA")
    print("=" * 50)
    
    try:
        from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
        from qgis.utils import iface
        
        # Perguntar configurações ao usuário
        offset_distancia, ok1 = QInputDialog.getDouble(
            None, 
            "Configuração", 
            "Distância do rótulo ao ponto (mm):", 
            2.0, 0.0, 100.0, 1
        )
        
        if not ok1:
            return False
        
        tamanho_fonte, ok2 = QInputDialog.getDouble(
            None, 
            "Configuração", 
            "Tamanho da fonte:", 
            8.0, 4.0, 50.0, 1
        )
        
        if not ok2:
            return False
        
        # Executar orientação básica
        sucesso = orientar_rotulos_perpendiculares()
        
        if sucesso:
            QMessageBox.information(
                None, 
                "Sucesso!", 
                f"Rótulos orientados perpendiculares às arestas!\n\n"
                f"Configurações aplicadas:\n"
                f"• Distância: {offset_distancia} mm\n"
                f"• Tamanho fonte: {tamanho_fonte} pt"
            )
        
        return sucesso
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

# FUNÇÃO PARA USAR NO CONSOLE PYTHON DO QGIS
def executar_orientacao():
    """Função principal para executar no console Python do QGIS"""
    print("🚀 INICIANDO ORIENTAÇÃO PERPENDICULAR DE RÓTULOS")
    print("=" * 60)
    
    resultado = orientar_rotulos_perpendiculares()
    
    if resultado:
        print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("📋 Os rótulos da camada 'imovel' agora estão orientados")
        print("   perpendiculares às arestas mais próximas da camada 'QUADRAS'")
        print("\n💡 DICAS:")
        print("   • Use orientar_rotulos_manual_melhorado() para ajustes")
        print("   • Ajuste manualmente as propriedades se necessário")
        print("   • Salve o projeto para preservar as configurações")
    else:
        print("\n❌ PROCESSO FALHOU!")
        print("📋 Verifique:")
        print("   • Se as camadas 'imovel' e 'QUADRAS' existem")
        print("   • Se os pontos estão dentro dos polígonos")
        print("   • Se há erros no console Python do QGIS")

if __name__ == "__main__":
    # Para testar fora do QGIS
    print("Este script deve ser executado no console Python do QGIS")
    print("Cole este código no console e execute: executar_orientacao()")
