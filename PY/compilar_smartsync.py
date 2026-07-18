import os
import subprocess
import sys

print("=" * 60)
print("  COMPILADOR SmartSync Cadastral")
print("=" * 60)

# Verificar se PyInstaller está instalado
try:
    import PyInstaller
    print("✓ PyInstaller encontrado")
except ImportError:
    print("✗ PyInstaller não encontrado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller instalado com sucesso")

# Verificar se Pillow está instalado (para criar o ícone)
try:
    import PIL
    print("✓ Pillow encontrado")
except ImportError:
    print("✗ Pillow não encontrado. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    print("✓ Pillow instalado com sucesso")

# Criar o ícone
print("\n" + "=" * 60)
print("  CRIANDO ÍCONE")
print("=" * 60)
icon_script = os.path.join(os.path.dirname(__file__), 'criar_icone.py')
subprocess.run([sys.executable, icon_script])

# Caminho do ícone
icon_path = os.path.join(os.path.dirname(__file__), 'smartsync_icon.ico')

# Verificar se o ícone foi criado
if not os.path.exists(icon_path):
    print("\n✗ Erro: Ícone não foi criado. Compilando sem ícone...")
    icon_param = ""
else:
    print(f"\n✓ Ícone encontrado: {icon_path}")
    icon_param = f'--icon="{icon_path}"'

# Verificar se CEP.csv existe
cep_path = os.path.join(os.path.dirname(__file__), 'CEP.csv')
if os.path.exists(cep_path):
    print(f"✓ Base CEP encontrada: {cep_path}")
    cep_param = f'--add-data "{cep_path}{os.pathsep}."'
else:
    print("⚠️ Aviso: CEP.csv não encontrado. Aplicativo funcionará sem base de municípios.")
    cep_param = ""

# Compilar com PyInstaller
print("\n" + "=" * 60)
print("  COMPILANDO APLICATIVO")
print("=" * 60)

script_path = os.path.join(os.path.dirname(__file__), 'aaaPlanilhas_GUI.py')
output_dir = os.path.join(os.path.dirname(__file__), 'dist')

# Preparar comando base
command = [
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--name=SmartSync Cadastral',
    f'--icon={icon_path}',
    f'--add-data={icon_path};.',  # Incluir o ícone no executável
    '--clean'
]

# Adicionar CEP.csv se existir
if cep_param:
    command.append(f'--add-data={cep_path};.')

command.append(script_path)

print(f"\nExecutando compilação...\n")
result = subprocess.run(command)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("  ✓ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    exe_path = os.path.join(output_dir, 'SmartSync Cadastral.exe')
    print(f"\n  Executável criado em:")
    print(f"  {exe_path}")
    print("\n" + "=" * 60)
else:
    print("\n" + "=" * 60)
    print("  ✗ ERRO NA COMPILAÇÃO")
    print("=" * 60)
    sys.exit(1)
