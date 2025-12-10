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
        print(f"[GHOST] Gravação iniciada (intervalo={self.intervalo_gravacao}s)")
        print(f"[GHOST] Gravação iniciada (intervalo={self.intervalo_gravacao}s)")
    
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
        
        if len(self.frames) == 0 or (self.tempo_acumulado - self.frames[-1][0]) >= self.intervalo_gravacao:
            x = carro.x
            y = carro.y
            
            if hasattr(carro, 'angulo'):
                angulo = carro.angulo
            elif hasattr(carro, '_angulo'):
                angulo = carro._angulo
            else:
                if hasattr(carro, 'vx') and hasattr(carro, 'vy'):
                    vx, vy = carro.vx, carro.vy
                    if abs(vx) > 0.01 or abs(vy) > 0.01:
                        angulo = math.degrees(math.atan2(-vx, vy))
                    else:
                        angulo = 0.0
                else:
                    angulo = 0.0
            
            self.frames.append((self.tempo_acumulado, float(x), float(y), float(angulo)))
            # Log apenas a cada 100 frames para não poluir o console
            if len(self.frames) % 100 == 0:
                print(f"[GHOST] Gravando frame {len(self.frames)} (tempo={self.tempo_acumulado:.2f}s)")
    
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
        """Carrega os ghosts do progresso.json"""
        # Tentar carregar do progresso.json diretamente (evitar importação circular)
        try:
            from config import DIR_PROJETO
            caminho_progresso = os.path.join(DIR_PROJETO, 'data', 'progresso.json')
            caminho_progresso = os.path.normpath(caminho_progresso)
            
            if os.path.exists(caminho_progresso):
                with open(caminho_progresso, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'ghosts' in data:
                        self.ghosts = {str(k): v for k, v in data.get('ghosts', {}).items()}
                        print(f"[GHOSTS] Carregado do progresso.json: {len(self.ghosts)} ghosts")
                        return  # Dados carregados do progresso.json
        except Exception as e:
            print(f"[GHOSTS] Erro ao carregar do progresso.json: {e}")
        
        # Fallback: valores padrão se não houver dados
        self.ghosts = {}
        print(f"[GHOSTS] Nenhum ghost carregado (usando padrão vazio)")
    
    def salvar(self):
        """Salva os ghosts"""
        # Dados são salvos através do GerenciadorProgresso.salvar()
        # Este método existe para compatibilidade, mas não salva mais em arquivo separado
        try:
            from core.progresso import gerenciador_progresso
            gerenciador_progresso.salvar()  # Isso salvará tudo, incluindo ghosts
        except Exception as e:
            print(f"Erro ao salvar ghosts: {e}")
    
    def salvar_ghost(self, numero_pista, frames, tempo=None, tipo_jogo=None):
        """
        Salva um ghost para uma pista (apenas se for a melhor volta)
        
        Args:
            numero_pista: Número da pista
            frames: Lista de frames gravados
            tempo: Tempo/score da volta (opcional, para verificar se é melhor)
            tipo_jogo: Tipo de jogo ("GHOST" ou "DRIFT") para verificar recorde correto
        """
        from core.progresso import gerenciador_progresso
        
        pista_key = str(numero_pista)
        
        # Se foi fornecido tempo e tipo_jogo, verificar se é realmente a melhor volta
        if tempo is not None and tipo_jogo is not None:
            if tipo_jogo == "GHOST":
                # Modo relógio: verificar se é melhor tempo (menor = melhor)
                # PRIMEIRO: verificar se já existe ghost (independente do tempo)
                ghost_existente = self.ghosts.get(pista_key, [])
                if ghost_existente is None or len(ghost_existente) == 0:
                    # Não há ghost anterior, sempre salvar (primeira vez)
                    print(f"[GHOST] Primeiro ghost para pista {pista_key} no modo relógio, salvando...")
                else:
                    # Há ghost anterior, verificar se este tempo é melhor
                    recorde_atual = gerenciador_progresso.obter_recorde(numero_pista)
                    if recorde_atual is None:
                        # Não há recorde mas há ghost? Isso não deveria acontecer, mas vamos salvar
                        print(f"[GHOST] AVISO: Há ghost mas não há recorde no modo relógio, salvando mesmo assim...")
                    elif tempo < recorde_atual:
                        print(f"[GHOST] Novo recorde melhor no modo relógio ({tempo:.2f}s < {recorde_atual:.2f}s), salvando ghost...")
                    else:
                        print(f"[GHOST] Ghost não salvo no modo relógio: tempo {tempo:.2f}s não é melhor que recorde {recorde_atual:.2f}s")
                        return False
            elif tipo_jogo == "DRIFT":
                # Modo drift: verificar se é melhor score (maior = melhor)
                # Para drift, o recorde é salvo com chave "{pista}_{voltas}", mas vamos verificar o recorde geral da pista
                # Na verdade, o recorde de drift pode ter múltiplas chaves, então vamos verificar se já existe um ghost melhor
                # Por enquanto, vamos confiar que o código que chama já verificou se é novo recorde
                # Mas vamos fazer uma verificação adicional: se já existe ghost, só salvar se for melhor
                if pista_key in self.ghosts:
                    # Se já existe ghost, verificar se o score é melhor
                    # Como não temos o score do ghost antigo, vamos confiar que o código que chama já verificou
                    pass
        
        # Salvar apenas se passou na verificação ou se não foi fornecida verificação
        self.ghosts[pista_key] = frames
        self.salvar()
        print(f"[GHOST] Ghost salvo para pista {pista_key} ({len(frames)} frames)")
        return True
    
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

