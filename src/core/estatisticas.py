import json
import os
from config import DIR_PROJETO

CAMINHO_ESTATISTICAS = os.path.join(DIR_PROJETO, "data", "estatisticas.json")

class GerenciadorEstatisticas:
    """Gerencia estatísticas detalhadas do jogador"""
    
    def __init__(self):
        from core.progresso import gerenciador_progresso
        self.gerenciador_progresso = gerenciador_progresso
        self.carregar()
    
    @property
    def estatisticas_gerais(self):
        """Retorna as estatísticas gerais do progresso.json (referência direta para permitir modificações)"""
        return self.gerenciador_progresso.estatisticas_gerais
    
    @property
    def estatisticas_por_pista(self):
        """Retorna as estatísticas por pista do progresso.json (referência direta para permitir modificações)"""
        return self.gerenciador_progresso.estatisticas_por_pista
    
    def carregar(self):
        """Carrega as estatísticas do progresso.json"""
        pass
    
    def salvar(self):
        """Salva as estatísticas no progresso.json"""
        self.gerenciador_progresso.salvar()
    
    def _obter_estatisticas_pista(self, numero_pista):
        """Obtém ou cria as estatísticas de uma pista"""
        pista_key = str(numero_pista)
        if pista_key not in self.estatisticas_por_pista:
            self.estatisticas_por_pista[pista_key] = {
                "corridas_completas": 0,
                "corridas_vencidas": 0,
                "melhor_tempo": None,
                "melhor_posicao": None,
                "voltas_completas": 0,
                "colisoes": 0,
                "recordes_estabelecidos": 0
            }
        return self.estatisticas_por_pista[pista_key]
    
    def registrar_tempo_jogado(self, segundos):
        """Registra tempo total jogado"""
        self.estatisticas_gerais["tempo_total_jogado"] += segundos
        if not hasattr(self, '_tempo_pendente'):
            self._tempo_pendente = 0.0
        self._tempo_pendente += segundos
        if self._tempo_pendente >= 5.0:
            self.salvar()
            self._tempo_pendente = 0.0
    
    def registrar_distancia(self, distancia_pixels):
        """Registra distância percorrida (em pixels)"""
        self.estatisticas_gerais["distancia_total"] += distancia_pixels
        if not hasattr(self, '_ultimo_salvamento_distancia'):
            self._ultimo_salvamento_distancia = 0
        self._ultimo_salvamento_distancia += distancia_pixels
        if self._ultimo_salvamento_distancia >= 1000:
            self.salvar()
            self._ultimo_salvamento_distancia = 0
    
    def registrar_corrida_completa(self, numero_pista, posicao_final=None, tempo_final=None):
        """Registra uma corrida completa"""
        self.estatisticas_gerais["corridas_completas"] += 1
        stats_pista = self._obter_estatisticas_pista(numero_pista)
        stats_pista["corridas_completas"] += 1
        
        if posicao_final == 1:
            self.estatisticas_gerais["corridas_vencidas"] += 1
            stats_pista["corridas_vencidas"] += 1
        
        if posicao_final is not None:
            if stats_pista["melhor_posicao"] is None or posicao_final < stats_pista["melhor_posicao"]:
                stats_pista["melhor_posicao"] = posicao_final
        
        if tempo_final is not None:
            if stats_pista["melhor_tempo"] is None or tempo_final < stats_pista["melhor_tempo"]:
                stats_pista["melhor_tempo"] = tempo_final
        
        self.salvar()
    
    def registrar_volta(self, numero_pista=None):
        """Registra uma volta completa"""
        self.estatisticas_gerais["voltas_completas"] += 1
        if numero_pista is not None:
            stats_pista = self._obter_estatisticas_pista(numero_pista)
            stats_pista["voltas_completas"] += 1
        if not hasattr(self, '_voltas_pendentes'):
            self._voltas_pendentes = 0
        self._voltas_pendentes += 1
        if self._voltas_pendentes >= 5:
            self.salvar()
            self._voltas_pendentes = 0
    
    def registrar_colisao(self, numero_pista=None):
        """Registra uma colisão"""
        self.estatisticas_gerais["colisoes_totais"] += 1
        if numero_pista is not None:
            stats_pista = self._obter_estatisticas_pista(numero_pista)
            stats_pista["colisoes"] += 1
        if not hasattr(self, '_colisoes_pendentes'):
            self._colisoes_pendentes = 0
        self._colisoes_pendentes += 1
        if self._colisoes_pendentes >= 10:
            self.salvar()
            self._colisoes_pendentes = 0
    
    def registrar_drift(self):
        """Registra uso de drift"""
        self.estatisticas_gerais["drifts_totais"] += 1
        if not hasattr(self, '_drifts_pendentes'):
            self._drifts_pendentes = 0
        self._drifts_pendentes += 1
        if self._drifts_pendentes >= 10:
            self.salvar()
            self._drifts_pendentes = 0
    
    def registrar_turbo(self):
        """Registra uso de turbo"""
        self.estatisticas_gerais["turbo_usado"] += 1
        if not hasattr(self, '_turbos_pendentes'):
            self._turbos_pendentes = 0
        self._turbos_pendentes += 1
        if self._turbos_pendentes >= 10:
            self.salvar()
            self._turbos_pendentes = 0
    
    def registrar_recorde(self, numero_pista):
        """Registra um recorde estabelecido"""
        self.estatisticas_gerais["recordes_estabelecidos"] += 1
        stats_pista = self._obter_estatisticas_pista(numero_pista)
        stats_pista["recordes_estabelecidos"] += 1
        self.salvar()
    
    def registrar_trofeu(self):
        """Registra um troféu ganho"""
        self.estatisticas_gerais["trofeus_ganhos"] += 1
        self.salvar()
    
    def finalizar_sessao(self):
        """Salva todas as estatísticas pendentes"""
        if hasattr(self, '_ultimo_salvamento_distancia') and self._ultimo_salvamento_distancia > 0:
            self.salvar()
            self._ultimo_salvamento_distancia = 0
        if hasattr(self, '_drifts_pendentes') and self._drifts_pendentes > 0:
            self.salvar()
            self._drifts_pendentes = 0
        if hasattr(self, '_turbos_pendentes') and self._turbos_pendentes > 0:
            self.salvar()
            self._turbos_pendentes = 0
        if hasattr(self, '_tempo_pendente') and self._tempo_pendente > 0:
            self.salvar()
            self._tempo_pendente = 0.0
        if hasattr(self, '_voltas_pendentes') and self._voltas_pendentes > 0:
            self.salvar()
            self._voltas_pendentes = 0
        if hasattr(self, '_colisoes_pendentes') and self._colisoes_pendentes > 0:
            self.salvar()
            self._colisoes_pendentes = 0
    
    def obter_estatisticas_gerais(self):
        """Retorna as estatísticas gerais"""
        return self.estatisticas_gerais.copy()
    
    def obter_estatisticas_pista(self, numero_pista):
        """Retorna as estatísticas de uma pista específica"""
        pista_key = str(numero_pista)
        if pista_key in self.estatisticas_por_pista:
            return self.estatisticas_por_pista[pista_key].copy()
        return None
    
    def obter_todas_pistas(self):
        """Retorna todas as pistas com estatísticas"""
        return list(self.estatisticas_por_pista.keys())
    
    def formatar_tempo(self, segundos):
        """Formata segundos em formato legível"""
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        if horas > 0:
            return f"{horas}h {minutos}m {segs}s"
        elif minutos > 0:
            return f"{minutos}m {segs}s"
        else:
            return f"{segs}s"
    
    def formatar_distancia(self, pixels):
        """Formata distância em km"""
        km = pixels / 100000.0
        if km >= 1.0:
            return f"{km:.2f} km"
        else:
            metros = pixels / 100.0
            return f"{metros:.0f} m"

gerenciador_estatisticas = GerenciadorEstatisticas()

