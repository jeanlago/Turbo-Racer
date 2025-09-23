import pygame
import os

# InicIAlizar pygame
pygame.init()

# Configurar mixer
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    print("Mixer inicIAlizado com sucesso")
    print(f"Configuração do mixer: {pygame.mixer.get_init()}")
except pygame.error as e:
    print(f"Erro ao inicIAlizar mixer: {e}")
    pygame.mixer.init()
    print("Mixer inicIAlizado com configurações padrão")

# Verificar se há músicas
pasta_musicas = "assets/sounds/music"
if os.path.exists(pasta_musicas):
    musicas = [f for f in os.listdir(pasta_musicas) if f.endswith(('.ogg', '.mp3', '.wav'))]
    print(f"Encontradas {len(musicas)} músicas:")
    for musica in musicas:
        print(f"  - {musica}")
    
    if musicas:
        # Tentar tocar a primeira música
        primeira_musica = os.path.join(pasta_musicas, musicas[0])
        print(f"\nTentando tocar: {primeira_musica}")
        
        try:
            pygame.mixer.music.load(primeira_musica)
            print("Música carregada com sucesso")
            
            pygame.mixer.music.play()
            print("Música inicIAda")
            
            # Verificar se está tocando
            if pygame.mixer.music.get_busy():
                print("✓ Música está tocando!")
                print("Pressione ENTER para parar...")
                input()
                pygame.mixer.music.stop()
                print("Música parada")
            else:
                print("✗ Música não está tocando")
                
        except pygame.error as e:
            print(f"Erro ao tocar música: {e}")
    else:
        print("Nenhuma música encontrada")
else:
    print("Pasta de músicas não encontrada")

pygame.quit()
