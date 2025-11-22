"""
Script para criar executável do Turbo Racer usando PyInstaller
Execute: python build.py
"""
import os
import sys
import shutil
import subprocess

def main():
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado!")
    except ImportError:
        print("PyInstaller não está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Caminhos
    base_dir = os.path.abspath(os.path.dirname(__file__))
    src_dir = os.path.join(base_dir, "src")
    main_script = os.path.join(src_dir, "main.py")
    
    # Verificar se o script principal existe
    if not os.path.exists(main_script):
        print(f"ERRO: Arquivo {main_script} não encontrado!")
        return
    
    # Verificar se assets e data existem
    assets_dir = os.path.join(base_dir, "assets")
    data_dir = os.path.join(base_dir, "data")
    
    if not os.path.exists(assets_dir):
        print(f"ERRO: Pasta assets não encontrada: {assets_dir}")
        return
    
    if not os.path.exists(data_dir):
        print(f"ERRO: Pasta data não encontrada: {data_dir}")
        return
    
    # Limpar builds anteriores (com tratamento de erros de permissão)
    print("Limpando builds anteriores...")
    
    def remover_pasta_segura(caminho):
        """Tenta remover uma pasta, ignorando erros de permissão"""
        if not os.path.exists(caminho):
            return True
        try:
            # Tentar remover com onerror para lidar com arquivos bloqueados
            def handle_remove_readonly(func, path, exc):
                import stat
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(caminho, onerror=handle_remove_readonly)
            return True
        except PermissionError:
            print(f"  ⚠ Não foi possível remover {caminho} (arquivos em uso)")
            print(f"     O PyInstaller tentará limpar automaticamente com --clean")
            return False
        except Exception as e:
            print(f"  ⚠ Erro ao remover {caminho}: {e}")
            print(f"     Continuando mesmo assim...")
            return False
    
    for folder in ["build", "dist"]:
        folder_path = os.path.join(base_dir, folder)
        if remover_pasta_segura(folder_path):
            print(f"  ✓ Removido: {folder}")
    
    # Limpar __pycache__ recursivamente
    import glob
    for pycache in glob.glob(os.path.join(base_dir, "**", "__pycache__"), recursive=True):
        try:
            shutil.rmtree(pycache)
        except:
            pass  # Ignorar erros em __pycache__
    
    # Limpar arquivo .spec se existir (ignorar erros)
    spec_file = os.path.join(base_dir, "TurboRacer.spec")
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
        except:
            pass  # Ignorar se não conseguir remover
    
    print("\nGerando executável com PyInstaller...")
    print("Isso pode levar alguns minutos...\n")
    
    # Tentar remover a pasta build mais agressivamente antes de executar
    build_path = os.path.join(base_dir, "build")
    build_bloqueada = False
    
    if os.path.exists(build_path):
        print("Tentando remover pasta build bloqueada...")
        import time
        import stat
        
        def remover_arquivo_forcado(caminho):
            """Tenta remover um arquivo mesmo se estiver bloqueado"""
            try:
                if os.path.exists(caminho):
                    os.chmod(caminho, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    os.remove(caminho)
                return True
            except:
                return False
        
        def remover_pasta_forcado(caminho):
            """Tenta remover uma pasta recursivamente, forçando permissões"""
            try:
                if not os.path.exists(caminho):
                    return True
                
                # Primeiro, tentar remover todos os arquivos
                for root, dirs, files in os.walk(caminho, topdown=False):
                    for f in files:
                        file_path = os.path.join(root, f)
                        remover_arquivo_forcado(file_path)
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        try:
                            os.chmod(dir_path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                            os.rmdir(dir_path)
                        except:
                            pass
                
                # Depois tentar remover a pasta raiz
                try:
                    os.chmod(caminho, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    os.rmdir(caminho)
                except:
                    shutil.rmtree(caminho, ignore_errors=True)
                
                return not os.path.exists(caminho)
            except:
                return False
        
        for tentativa in range(3):
            time.sleep(0.5)
            if remover_pasta_forcado(build_path):
                print("  ✓ Pasta build removida com sucesso")
                build_bloqueada = False
                break
            else:
                build_bloqueada = True
        
        if build_bloqueada:
            print("  ⚠ Pasta build ainda existe (arquivos bloqueados)")
            print("     Continuando sem --clean para evitar erros...")
    
    # Comando PyInstaller (sem --clean se a pasta build estiver bloqueada)
    usar_clean = not build_bloqueada
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=TurboRacer",
        "--onefile",  # Um único arquivo executável
        "--windowed",  # Sem console
    ]
    
    # Adicionar --clean apenas se a pasta build não existir
    if usar_clean:
        cmd.append("--clean")
    
    # Adicionar os parâmetros restantes
    cmd.append("--noconfirm")
    cmd.append(f"--add-data={assets_dir}{os.pathsep}assets")
    cmd.append(f"--add-data={data_dir}{os.pathsep}data")
    cmd.append("--hidden-import=pygame")
    cmd.append("--hidden-import=config")
    cmd.append("--hidden-import=core.checkpoint_manager")
    cmd.append("--hidden-import=core.carro_fisica")
    cmd.append("--hidden-import=core.corrida")
    cmd.append("--hidden-import=core.camera")
    cmd.append("--hidden-import=core.ia")
    cmd.append("--hidden-import=core.musica")
    cmd.append("--hidden-import=core.hud")
    cmd.append("--hidden-import=core.game_modes")
    cmd.append("--hidden-import=core.drift_scoring")
    cmd.append("--hidden-import=core.progresso")
    cmd.append("--hidden-import=core.menu")
    cmd.append("--hidden-import=core.i18n")
    cmd.append("--hidden-import=core.pista_tiles")
    cmd.append("--hidden-import=core.laps_grip")
    cmd.append("--hidden-import=core.skidmarks")
    cmd.append("--hidden-import=core.particulas")
    cmd.append("--hidden-import=core.popup_musica")
    cmd.append(main_script)
    
    try:
        subprocess.check_call(cmd)
        
        print("\n" + "="*60)
        print("✓ Executável criado com sucesso!")
        print("="*60)
        exe_path = os.path.join(base_dir, "dist", "TurboRacer.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✓ Arquivo: {exe_path}")
            print(f"✓ Tamanho: {size_mb:.1f} MB")
            print("\n📦 O executável está pronto para ser enviado!")
            print("   Você pode enviar apenas o arquivo TurboRacer.exe pelo WhatsApp.")
            print("   O executável contém todos os assets necessários.")
        else:
            print("\n⚠ Executável não encontrado no local esperado.")
            print("   Verifique a pasta 'dist' para encontrar o arquivo.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO ao gerar executável: {e}")
        print("\nTente executar manualmente:")
        print("  pyinstaller --name=TurboRacer --onefile --windowed src/main.py")
        return
    
    # Limpar arquivos temporários (opcional)
    print("\n💡 Dica: Você pode remover a pasta 'build' para economizar espaço.")
    print("   A pasta 'dist' contém o executável final.")

if __name__ == "__main__":
    main()
