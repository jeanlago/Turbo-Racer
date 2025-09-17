import os
import pygame
import random
from config import DIR_PROJETO

# Forçar uso de driver de áudio real
os.environ["SDL_AUDIODRIVER"] = "directsound"  # Windows

class GerenciadorMusica:
    def __init__(self):
        self.musicas = []
        self.musica_atual = 0
        self.volume = 1.0
        self.musica_habilitada = True
        self.musica_no_menu = True
        self.musica_no_jogo = True
        self.musica_tocando = False
        self.nome_musica_atual = ""
        
        # Configurar mixer de áudio primeiro
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error:
            # Tentar com configurações mais simples
            pygame.mixer.init()
        
        pygame.mixer.music.set_volume(self.volume)
        
        # Carregar músicas da pasta
        self.carregar_musicas()
    
    def carregar_musicas(self):
        """Carrega todas as músicas da pasta assets/sounds/music"""
        pasta_musicas = os.path.join(DIR_PROJETO, "assets", "sounds", "music")
        
        if os.path.exists(pasta_musicas):
            for arquivo in os.listdir(pasta_musicas):
                if arquivo.endswith(('.ogg', '.mp3', '.wav')):
                    caminho_completo = os.path.join(pasta_musicas, arquivo)
                    nome_musica = os.path.splitext(arquivo)[0]
                    
                    # Adicionar música sem testar (será testada quando tocar)
                    self.musicas.append({
                        'caminho': caminho_completo,
                        'nome': nome_musica
                    })
        
        # Se não houver músicas, criar uma lista vazia
        if not self.musicas:
            print("Nenhuma música encontrada na pasta assets/sounds/music")
    
    def tocar_musica(self, indice=None):
        """Toca uma música específica ou a próxima na lista"""
        if not self.musicas or not self.musica_habilitada:
            return False
        
        if indice is None:
            indice = self.musica_atual
        else:
            self.musica_atual = indice
        
        if 0 <= indice < len(self.musicas):
            try:
                pygame.mixer.music.load(self.musicas[indice]['caminho'])
                pygame.mixer.music.play()
                self.musica_tocando = True
                self.nome_musica_atual = self.musicas[indice]['nome']
                return True
            except pygame.error as e:
                print(f"Erro ao tocar música {self.musicas[indice]['nome']}: {e}")
                # Se houver erro, desabilitar música para evitar loop
                self.musica_habilitada = False
                self.musica_tocando = False
                return False
        return False
    
    def parar_musica(self):
        """Para a música atual"""
        pygame.mixer.music.stop()
        self.musica_tocando = False
        self.nome_musica_atual = ""
    
    def pausar_musica(self):
        """Pausa a música atual"""
        if self.musica_tocando:
            pygame.mixer.music.pause()
    
    def despausar_musica(self):
        """Despausa a música atual"""
        if self.musica_tocando:
            pygame.mixer.music.unpause()
    
    def proxima_musica(self):
        """Vai para a próxima música"""
        if self.musicas:
            self.musica_atual = (self.musica_atual + 1) % len(self.musicas)
            self.tocar_musica()
    
    def musica_anterior(self):
        """Vai para a música anterior"""
        if self.musicas:
            self.musica_atual = (self.musica_atual - 1) % len(self.musicas)
            self.tocar_musica()
    
    def musica_aleatoria(self):
        """Toca uma música aleatória"""
        if self.musicas:
            self.musica_atual = random.randint(0, len(self.musicas) - 1)
            self.tocar_musica()
    
    def definir_volume(self, volume):
        """Define o volume da música (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def verificar_fim_musica(self):
        """Verifica se a música terminou e toca a próxima"""
        if not pygame.mixer.music.get_busy() and self.musica_tocando:
            self.proxima_musica()
    
    def obter_nome_musica_atual(self):
        """Retorna o nome da música atual"""
        return self.nome_musica_atual
    
    def obter_lista_musicas(self):
        """Retorna a lista de músicas disponíveis"""
        return [musica['nome'] for musica in self.musicas]
    
    def obter_indice_musica_atual(self):
        """Retorna o índice da música atual"""
        return self.musica_atual
    
    def obter_total_musicas(self):
        """Retorna o total de músicas"""
        return len(self.musicas)

# Instância global do gerenciador de música
gerenciador_musica = GerenciadorMusica()
