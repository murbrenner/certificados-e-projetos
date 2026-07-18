import os
import subprocess
import sys
import shutil
import time

print("=" * 60)
print("  COMPILADOR SmartSync Cadastral - SUBSTITUIR")
print("=" * 60)

# Caminho do executável antigo
exe_antigo = os.path.join(os.path.dirname(__file__), 'dist', 'SmartSync Cadastral.exe')
exe_backup = os.path.join(os.path.dirname(__file__), 'dist', 'SmartSync Cadastral_OLD.exe')

# Fazer backup se existir
if os.path.exists(exe_antigo):
    print(f"\n⚠️  Executável anterior detectado")
    print(f"   Tentando criar backup...")
    try:
        if os.path.exists(exe_backup):
            os.remove(exe_backup)
        shutil.move(exe_antigo, exe_backup)
        print(f"✓ Backup criado: SmartSync Cadastral_OLD.exe")
    except Exception as e:
        print(f"⚠️  Não foi possível mover o arquivo: {e}")
        print(f"   O arquivo pode estar em uso. Fechando processos...")
        
        # Tentar fechar processos relacionados
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'SmartSync Cadastral.exe'], 
                         capture_output=True, text=True)
            print("✓ Processo finalizado")
            time.sleep(2)
            
            # Tentar novamente
            if os.path.exists(exe_backup):
                os.remove(exe_backup)
            shutil.move(exe_antigo, exe_backup)
            print(f"✓ Backup criado: SmartSync Cadastral_OLD.exe")
        except Exception as e2:
            print(f"⚠️  Ainda não foi possível mover: {e2}")
            print(f"   Compilando com novo nome temporário...")

# Executar o script de compilação normal
print("\n" + "=" * 60)
print("  INICIANDO COMPILAÇÃO")
print("=" * 60 + "\n")

compilador = os.path.join(os.path.dirname(__file__), 'compilar_smartsync.py')
result = subprocess.run([sys.executable, compilador])

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("  ✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    # Se houver backup, perguntar se quer deletar
    if os.path.exists(exe_backup):
        print(f"\n📁 Backup disponível: SmartSync Cadastral_OLD.exe")
        print(f"   Você pode deletá-lo manualmente se desejar.")
else:
    print("\n" + "=" * 60)
    print("  ❌ ERRO NA COMPILAÇÃO")
    print("=" * 60)
    
    # Restaurar backup se houver erro
    if os.path.exists(exe_backup) and not os.path.exists(exe_antigo):
        try:
            shutil.move(exe_backup, exe_antigo)
            print(f"✓ Backup restaurado")
        except:
            pass

input("\nPressione ENTER para sair...")
