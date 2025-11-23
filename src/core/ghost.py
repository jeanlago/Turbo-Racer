# src/core/ghost.py
"""
Sistema de Ghost Car - Grava e reproduz a trajetória do melhor tempo
"""
import json
import os
import math
from config import DIR_PROJETO

CAMINHO_GHOSTS = os.path.join(DIR_PROJETO, "data", "ghosts.json")

class GhostRecorder:
    """Grava a trajetória de um carro durante a corrida"""
    
    def __init__(self, intervalo_gravacao=0.05):
        """
        intervalo_gravacao: Intervalo em segundos entre cada frame gravado (padrão: 0.05s = 20 FPS)
        """
        self.intervalo_gravacao = intervalo_gravacao
        self.tempo_acumulado = 0.0
        self.frames = []  # Lista de (tempo, x, y, angulo)
        self.gravando = False
    
    def iniciar_gravacao(self):
        """Inicia a gravação do ghost"""
        self.tempo_acumulado = 0.0
        self.frames = []
        self.gravando = True
    
    def parar_gravacao(self):
        """Para a gravação do ghost"""
        self.gravando = False
    
    def atualizar(self, dt, carro):
        """
        Atualiza a gravação com a posição atual do carro
        
        Args:
            dt: Delta time desde a última atualização
            carro: Objeto do carro a ser gravado
        """
        if not self.gravando:
            return
        
        self.tempo_acumulado += dt
        
        # Gravar apenas se passou o intervalo mínimo
        if len(self.frames) == 0 or (self.tempo_acumulado - self.frames[-1][0]) >= self.intervalo_gravacao:
            # Obter posição e ângulo do carro
            x = carro.x
            y = carro.y
            
            # Obter ângulo do carro (em graus)
            if hasattr(carro, 'angulo'):
                angulo = carro.angulo
            elif hasattr(carro, '_angulo'):
                angulo = carro._angulo
            else:
                # Calcular ângulo baseado na velocidade
                if hasattr(carro, 'vx') and hasattr(carro, 'vy'):
                    vx, vy = carro.vx, carro.vy
                    if abs(vx) > 0.01 or abs(vy) > 0.01:
                        angulo = math.degrees(math.atan2(-vx, vy))
                    else:
                        angulo = 0.0
                else:
                    angulo = 0.0
            
            # Adicionar frame
            self.frames.append((self.tempo_acumulado, float(x), float(y), float(angulo)))
    
    def obter_dados(self):
        """Retorna os dados gravados como uma lista de frames"""
        return self.frames.copy()
    
    def limpar(self):
        """Limpa os dados gravados"""
        self.frames = []
        self.tempo_acumulado = 0.0
        self.gravando = False


class GhostPlayer:
    """Reproduz a trajetória gravada de um ghost"""
    
    def __init__(self, frames):
        """
        Args:
            frames: Lista de frames gravados [(tempo, x, y, angulo), ...]
        """
        self.frames = frames
        self.tempo_atual = 0.0
        self.indice_atual = 0
        self.ativo = False
        self.x = 0.0
        self.y = 0.0
        self.angulo = 0.0
    
    def iniciar(self):
        """Inicia a reprodução do ghost"""
        self.tempo_atual = 0.0
        self.indice_atual = 0
        self.ativo = True
        if self.frames:
            self.x, self.y, self.angulo = self.frames[0][1], self.frames[0][2], self.frames[0][3]
    
    def parar(self):
        """Para a reprodução do ghost"""
        self.ativo = False
    
    def atualizar(self, dt):
        """
        Atualiza a posição do ghost baseado no tempo
        
        Args:
            dt: Delta time desde a última atualização
        """
        if not self.ativo or not self.frames:
            return
        
        self.tempo_atual += dt
        
        # Encontrar os dois frames entre os quais estamos
        while self.indice_atual < len(self.frames) - 1:
            tempo_frame_atual = self.frames[self.indice_atual][0]
            tempo_frame_proximo = self.frames[self.indice_atual + 1][0]
            
            if tempo_frame_atual <= self.tempo_atual < tempo_frame_proximo:
                # Interpolar entre os dois frames
                t1, x1, y1, a1 = self.frames[self.indice_atual]
                t2, x2, y2, a2 = self.frames[self.indice_atual + 1]
                
                if t2 > t1:
                    alpha = (self.tempo_atual - t1) / (t2 - t1)
                    self.x = x1 + (x2 - x1) * alpha
                    self.y = y1 + (y2 - y1) * alpha
                    
                    # Interpolar ângulo (lidar com wrap-around de 360 graus)
                    da = a2 - a1
                    if da > 180:
                        da -= 360
                    elif da < -180:
                        da += 360
                    self.angulo = a1 + da * alpha
                    if self.angulo < 0:
                        self.angulo += 360
                    elif self.angulo >= 360:
                        self.angulo -= 360
                else:
                    # Sem interpolação se tempos iguais
                    self.x, self.y, self.angulo = x1, y1, a1
                break
            elif self.tempo_atual >= tempo_frame_proximo:
                # Avançar para o próximo frame
                self.indice_atual += 1
            else:
                break
        
        # Se passou do último frame, usar o último frame
        if self.indice_atual >= len(self.frames) - 1:
            if self.frames:
                self.x, self.y, self.angulo = self.frames[-1][1], self.frames[-1][2], self.frames[-1][3]
    
    def esta_ativo(self):
        """Retorna True se o ghost está sendo reproduzido"""
        return self.ativo and len(self.frames) > 0


class GerenciadorGhosts:
    """Gerencia salvamento e carregamento de ghosts"""
    
    def __init__(self):
        self.ghosts = {}  # {numero_pista: frames}
        self.carregar()
    
    def carregar(self):
        """Carrega os ghosts salvos do arquivo"""
        if os.path.exists(CAMINHO_GHOSTS):
            try:
                with open(CAMINHO_GHOSTS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Converter chaves para string para consistência
                    self.ghosts = {str(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Erro ao carregar ghosts: {e}")
                self.ghosts = {}
        else:
            self.ghosts = {}
    
    def salvar(self):
        """Salva os ghosts no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_GHOSTS), exist_ok=True)
            with open(CAMINHO_GHOSTS, 'w', encoding='utf-8') as f:
                json.dump(self.ghosts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar ghosts: {e}")
    
    def salvar_ghost(self, numero_pista, frames):
        """
        Salva um ghost para uma pista
        
        Args:
            numero_pista: Número da pista
            frames: Lista de frames gravados
        """
        pista_key = str(numero_pista)
        self.ghosts[pista_key] = frames
        self.salvar()
        print(f"Ghost salvo para pista {pista_key} ({len(frames)} frames)")
    
    def obter_ghost(self, numero_pista):
        """
        Obtém o ghost de uma pista
        
        Args:
            numero_pista: Número da pista
            
        Returns:
            Lista de frames ou None se não houver ghost
        """
        pista_key = str(numero_pista)
        return self.ghosts.get(pista_key, None)
    
    def tem_ghost(self, numero_pista):
        """Verifica se existe um ghost para uma pista"""
        pista_key = str(numero_pista)
        return pista_key in self.ghosts and len(self.ghosts[pista_key]) > 0


# Instância global
gerenciador_ghosts = GerenciadorGhosts()

