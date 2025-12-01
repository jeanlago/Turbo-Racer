import os
import pygame
import random
from config import DIR_PROJETO

os.environ["SDL_AUDIODRIVER"] = "directsound"

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
        self.audio_disponivel = False  # Flag para indicar se o áudio está disponível
        
        # Tentar inicializar o mixer do pygame
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_disponivel = True
        except pygame.error:
            try:
                pygame.mixer.init()
                self.audio_disponivel = True
            except pygame.error as e:
                print(f"AVISO: Dispositivo de áudio não encontrado. O jogo continuará sem som. ({e})")
                self.audio_disponivel = False
                self.musica_habilitada = False
        
        # Só configurar volume se o áudio estiver disponível
        if self.audio_disponivel:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except pygame.error:
                self.audio_disponivel = False
                self.musica_habilitada = False
        
        self.carregar_musicas()
    
    def carregar_musicas(self):
        """Carrega todas as músicas da pasta assets/sounds/music"""
        pasta_musicas = os.path.join(DIR_PROJETO, "assets", "sounds", "music")
        
        if os.path.exists(pasta_musicas):
            for arquivo in os.listdir(pasta_musicas):
                if arquivo.endswith(('.ogg', '.mp3', '.wav')):
                    caminho_completo = os.path.join(pasta_musicas, arquivo)
                    nome_musica = os.path.splitext(arquivo)[0]
                    self.musicas.append({
                        'caminho': caminho_completo,
                        'nome': nome_musica
                    })
        
        if not self.musicas:
            print("Nenhuma música encontrada na pasta assets/sounds/music")
    
    def tocar_musica(self, indice=None):
        """Toca uma música específica ou a próxima na lista"""
        if not self.audio_disponivel or not self.musicas or not self.musica_habilitada:
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
                self.musica_habilitada = False
                self.musica_tocando = False
                self.audio_disponivel = False
                return False
        return False
    
    def parar_musica(self):
        """Para a música atual"""
        if self.audio_disponivel:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
        self.musica_tocando = False
        self.nome_musica_atual = ""
    
    def pausar_musica(self):
        """Pausa a música atual"""
        if self.audio_disponivel and self.musica_tocando:
            try:
                pygame.mixer.music.pause()
            except pygame.error:
                pass
    
    def despausar_musica(self):
        """Despausa a música atual"""
        if self.audio_disponivel and self.musica_tocando:
            try:
                pygame.mixer.music.unpause()
            except pygame.error:
                pass
    
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
        if self.audio_disponivel:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except pygame.error:
                pass
    
    def verificar_fim_musica(self):
        """Verifica se a música terminou e toca a próxima"""
        if self.audio_disponivel and self.musica_tocando:
            try:
                if not pygame.mixer.music.get_busy():
                    self.proxima_musica()
            except pygame.error:
                self.musica_tocando = False
    
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

gerenciador_musica = GerenciadorMusica()
