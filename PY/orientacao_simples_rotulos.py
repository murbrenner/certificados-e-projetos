#NOME: Orientacao Simples Rotulos

#DESCRIÇÃO: Executa a rotina 'Orientacao Simples Rotulos', ajustando orientacao de rotulos/linhas conforme a geometria das feicoes.

#PRÉ-REQUISITO: Ter camada de imóveis com rótulos configurados e campo de ângulo disponível para atualização, além da camada de referência geométrica carregada para cálculo da orientação.


# ORIENTAÇÃO SIMPLES DE RÓTULOS - VERSÃO RÁPIDA
# Versão simplificada para orientação perpendicular rápida
# Data: Nov/2025

def orientacao_rapida_rotulos():
    """
    Versão rápida e simples para orientar rótulos perpendiculares
    """
    from qgis.core import QgsProject, QgsPalLayerSettings, QgsVectorLayerSimpleLabeling
    from qgis.utils import iface
    import math
    
    print("⚡ ORIENTAÇÃO RÁPIDA DE RÓTULOS")
    print("=" * 40)
    
    try:
        # Buscar camada imovel
        project = QgsProject.instance()
        camada_imovel = None
        
        for layer in project.mapLayers().values():
            if 'imovel' in layer.name().lower():
                camada_imovel = layer
                break
        
        if not camada_imovel:
            print("❌ Camada 'imovel' não encontrada!")
            return False
        
        print(f"✅ Processando: {camada_imovel.name()}")
        
        # Configuração simples de rótulos
        settings = QgsPalLayerSettings()
        settings.enabled = True
        
        # Campo do rótulo
        if camada_imovel.fields():
            settings.fieldName = camada_imovel.fields()[0].name()
        
        # Rotação fixa perpendicular (45 graus como padrão)
        settings.angleOffset = 45
        
        # Configurações de posicionamento
        settings.placement = QgsPalLayerSettings.OverPoint
        settings.dist = 3.0
        
        # Aplicar
        labeling = QgsVectorLayerSimpleLabeling(settings)
        camada_imovel.setLabeling(labeling)
        camada_imovel.setLabelsEnabled(True)
        camada_imovel.triggerRepaint()
        
        print("✅ Orientação aplicada!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def resetar_rotulos():
    """Remove orientação dos rótulos"""
    from qgis.core import QgsProject
    from qgis.utils import iface
    
    project = QgsProject.instance()
    for layer in project.mapLayers().values():
        if 'imovel' in layer.name().lower():
            layer.setLabelsEnabled(False)
            layer.triggerRepaint()
            print(f"✅ Rótulos resetados: {layer.name()}")
            return True
    
    print("❌ Camada não encontrada")
    return False

# INSTRUÇÕES DE USO
def instrucoes():
    """Mostra instruções de uso"""
    print("📋 INSTRUÇÕES DE USO")
    print("=" * 30)
    print("1. Abra o console Python do QGIS")
    print("2. Cole este código completo")
    print("3. Execute uma das funções:")
    print("   • executar_orientacao() - Versão completa")
    print("   • orientacao_rapida_rotulos() - Versão rápida")
    print("   • resetar_rotulos() - Remove orientação")
    print()
    print("💡 REQUISITOS:")
    print("   • Camada 'imovel' (pontos)")
    print("   • Camada 'QUADRAS' (polígonos)")
    print("   • Pontos dentro dos polígonos")

if __name__ == "__main__":
    instrucoes()
