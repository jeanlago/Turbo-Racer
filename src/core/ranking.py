# src/core/ranking.py
import json
import os
from config import DIR_PROJETO

CAMINHO_RANKING = os.path.join(DIR_PROJETO, "data", "ranking.json")

NOMES_RANKING = [
    "T-Rex_King",
    "Akira_Drift",
    "NightStalker",
    "ApexPredator",
    "The_Baron$$",
    "Camber_Queen",
    "Sly_Fox_GT",
    "Boost_Leak",
    "RoadRat",
    "JOGADOR"
]

class GerenciadorRanking:
    """Gerencia o ranking de pilotos (Top 10)"""
    
    def __init__(self):
        from core.progresso import gerenciador_progresso
        self.gerenciador_progresso = gerenciador_progresso
        self.carregar()
        self._inicializar_ranking_se_necessario()
    
    @property
    def ranking(self):
        """Retorna o ranking do progresso.json"""
        return self.gerenciador_progresso.ranking_pilotos
    
    @ranking.setter
    def ranking(self, value):
        """Define o ranking no progresso.json"""
        self.gerenciador_progresso.ranking_pilotos = value
        self.gerenciador_progresso.salvar()
    
    @property
    def posicao_jogador(self):
        """Retorna a posição do jogador do progresso.json"""
        return self.gerenciador_progresso.ranking_posicao_jogador
    
    @posicao_jogador.setter
    def posicao_jogador(self, value):
        """Define a posição do jogador no progresso.json"""
        self.gerenciador_progresso.ranking_posicao_jogador = value
        self.gerenciador_progresso.salvar()
    
    def carregar(self):
        """Carrega o ranking do progresso.json"""
        pass
    
    def salvar(self):
        """Salva o ranking no progresso.json"""
        self.gerenciador_progresso.salvar()
    
    def _inicializar_ranking_se_necessario(self):
        """Inicializa o ranking com os nomes padrão se estiver vazio"""
        if not self.ranking:
            ranking_novo = []
            nome_jogador = self.gerenciador_progresso.nome_jogador
            for i, nome in enumerate(NOMES_RANKING, start=1):
                nome_final = nome_jogador if nome == "JOGADOR" else nome
                ranking_novo.append({
                    'nome': nome_final,
                    'posicao': i,
                    'vitorias': 0,
                    'derrotas': 0,
                    'e_jogador': (nome == "JOGADOR")
                })
            self.gerenciador_progresso.ranking_pilotos = ranking_novo
            self.gerenciador_progresso.ranking_posicao_jogador = 10
            self.salvar()
        else:
            nome_jogador = self.gerenciador_progresso.nome_jogador
            for piloto in self.ranking:
                if piloto.get('e_jogador', False) or piloto['nome'] == "JOGADOR" or piloto['nome'] == nome_jogador:
                    piloto['nome'] = nome_jogador
                    piloto['e_jogador'] = True
                    self.salvar()
                    break
    
    def obter_ranking(self):
        """Retorna o ranking completo (lista ordenada por posição)"""
        return sorted(self.ranking, key=lambda x: x['posicao'])
    
    def obter_posicao_jogador(self):
        """Retorna a posição atual do jogador no ranking"""
        return self.posicao_jogador
    
    def obter_piloto_por_posicao(self, posicao):
        """Retorna o piloto na posição especificada (1-10)"""
        for piloto in self.ranking:
            if piloto['posicao'] == posicao:
                return piloto
        return None
    
    def registrar_vitoria_jogador(self):
        """Registra uma vitória do jogador e atualiza o ranking"""
        # Encontrar o piloto do jogador
        ranking_atual = self.ranking.copy()
        jogador = None
        for piloto in ranking_atual:
            nome_jogador = self.gerenciador_progresso.nome_jogador
            if piloto.get('e_jogador', False) or piloto['nome'] == "JOGADOR" or piloto['nome'] == nome_jogador:
                jogador = piloto
                break
        
        if not jogador:
            return False
        
        # Incrementar vitórias
        jogador['vitorias'] = jogador.get('vitorias', 0) + 1
        
        # Atualizar no progresso
        self.gerenciador_progresso.ranking_pilotos = ranking_atual
        
        # Se o jogador está em 10º lugar e venceu, pode subir de posição
        if self.posicao_jogador == 10:
            # Verificar se pode desafiar o 9º lugar
            # Por enquanto, apenas incrementar vitórias
            # A lógica de subir de posição será implementada depois
            pass
        
        self.salvar()
        return True
    
    def registrar_derrota_jogador(self):
        """Registra uma derrota do jogador"""
        # Encontrar o piloto do jogador
        ranking_atual = self.ranking.copy()
        jogador = None
        for piloto in ranking_atual:
            nome_jogador = self.gerenciador_progresso.nome_jogador
            if piloto.get('e_jogador', False) or piloto['nome'] == "JOGADOR" or piloto['nome'] == nome_jogador:
                jogador = piloto
                break
        
        if not jogador:
            return False
        
        # Incrementar derrotas
        jogador['derrotas'] = jogador.get('derrotas', 0) + 1
        
        # Atualizar no progresso
        self.gerenciador_progresso.ranking_pilotos = ranking_atual
        
        self.salvar()
        return True
    
    def desafiar_piloto(self, posicao_desafiada):
        """
        Permite ao jogador desafiar um piloto em uma posição específica
        Retorna True se o desafio foi bem-sucedido (jogador venceu)
        """
        if posicao_desafiada < 1 or posicao_desafiada > 10:
            return False
        
        # O jogador só pode desafiar pilotos acima dele
        if posicao_desafiada >= self.posicao_jogador:
            return False
        
        # Encontrar o piloto desafiado
        piloto_desafiado = self.obter_piloto_por_posicao(posicao_desafiada)
        if not piloto_desafiado:
            return False
        
        # Encontrar o jogador
        jogador = None
        for piloto in self.ranking:
            nome_jogador = self.gerenciador_progresso.nome_jogador
            if piloto.get('e_jogador', False) or piloto['nome'] == "JOGADOR" or piloto['nome'] == nome_jogador:
                jogador = piloto
                break
        
        if not jogador:
            return False
        
        # Por enquanto, apenas retornar True se o desafio foi aceito
        # A lógica de vitória/derrota será implementada na corrida
        return True
    
    def subir_posicao(self):
        """
        Move o jogador para cima no ranking (após vencer um desafio)
        """
        if self.posicao_jogador <= 1:
            return False  # Já está no topo
        
        # Encontrar o jogador e o piloto acima dele
        ranking_atual = self.ranking.copy()
        jogador = None
        piloto_acima = None
        
        for piloto in ranking_atual:
            nome_jogador = self.gerenciador_progresso.nome_jogador
            if piloto.get('e_jogador', False) or piloto['nome'] == "JOGADOR" or piloto['nome'] == nome_jogador:
                jogador = piloto
            elif piloto['posicao'] == self.posicao_jogador - 1:
                piloto_acima = piloto
        
        if not jogador or not piloto_acima:
            return False
        
        # Trocar posições
        posicao_jogador_antiga = jogador['posicao']
        posicao_acima_antiga = piloto_acima['posicao']
        
        jogador['posicao'] = posicao_acima_antiga
        piloto_acima['posicao'] = posicao_jogador_antiga
        
        self.gerenciador_progresso.ranking_pilotos = ranking_atual
        self.posicao_jogador = posicao_acima_antiga
        
        self.salvar()
        return True
    
    def descer_posicao(self):
        """
        Move o jogador para baixo no ranking (após perder um desafio)
        """
        if self.posicao_jogador >= 10:
            return False  # Já está no último lugar
        
        # Encontrar o jogador e o piloto abaixo dele
        ranking_atual = self.ranking.copy()
        jogador = None
        piloto_abaixo = None
        
        for piloto in ranking_atual:
            nome_jogador = self.gerenciador_progresso.nome_jogador
            if piloto.get('e_jogador', False) or piloto['nome'] == "JOGADOR" or piloto['nome'] == nome_jogador:
                jogador = piloto
            elif piloto['posicao'] == self.posicao_jogador + 1:
                piloto_abaixo = piloto
        
        if not jogador or not piloto_abaixo:
            return False
        
        # Trocar posições
        posicao_jogador_antiga = jogador['posicao']
        posicao_abaixo_antiga = piloto_abaixo['posicao']
        
        jogador['posicao'] = posicao_abaixo_antiga
        piloto_abaixo['posicao'] = posicao_jogador_antiga
        
        self.gerenciador_progresso.ranking_pilotos = ranking_atual
        self.posicao_jogador = posicao_abaixo_antiga
        
        self.salvar()
        return True

# Instância global
gerenciador_ranking = GerenciadorRanking()



