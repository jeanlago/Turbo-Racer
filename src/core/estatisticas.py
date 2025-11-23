# src/core/estatisticas.py
"""
Sistema de Estatísticas Detalhadas
"""
import json
import os
from config import DIR_PROJETO

CAMINHO_ESTATISTICAS = os.path.join(DIR_PROJETO, "data", "estatisticas.json")

class GerenciadorEstatisticas:
    """Gerencia estatísticas detalhadas do jogador"""
    
    def __init__(self):
        self.estatisticas_gerais = {
            "tempo_total_jogado": 0.0,  # em segundos
            "distancia_total": 0.0,  # em pixels (convertido para km depois)
            "corridas_completas": 0,
            "corridas_vencidas": 0,
            "voltas_completas": 0,
            "colisoes_totais": 0,
            "drifts_totais": 0,
            "turbo_usado": 0,
            "recordes_estabelecidos": 0,
            "trofeus_ganhos": 0
        }
        
        self.estatisticas_por_pista = {}  # {numero_pista: {estatisticas}}
        self.carregar()
    
    def carregar(self):
        """Carrega as estatísticas do arquivo"""
        if os.path.exists(CAMINHO_ESTATISTICAS):
            try:
                with open(CAMINHO_ESTATISTICAS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.estatisticas_gerais = data.get('estatisticas_gerais', self.estatisticas_gerais)
                    self.estatisticas_por_pista = data.get('estatisticas_por_pista', {})
            except Exception as e:
                print(f"Erro ao carregar estatísticas: {e}")
                self.estatisticas_gerais = {
                    "tempo_total_jogado": 0.0,
                    "distancia_total": 0.0,
                    "corridas_completas": 0,
                    "corridas_vencidas": 0,
                    "voltas_completas": 0,
                    "colisoes_totais": 0,
                    "drifts_totais": 0,
                    "turbo_usado": 0,
                    "recordes_estabelecidos": 0,
                    "trofeus_ganhos": 0
                }
                self.estatisticas_por_pista = {}
    
    def salvar(self):
        """Salva as estatísticas no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_ESTATISTICAS), exist_ok=True)
            data = {
                'estatisticas_gerais': self.estatisticas_gerais,
                'estatisticas_por_pista': self.estatisticas_por_pista
            }
            with open(CAMINHO_ESTATISTICAS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar estatísticas: {e}")
    
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
        # Não salvar a cada frame para melhorar performance
        if not hasattr(self, '_tempo_pendente'):
            self._tempo_pendente = 0.0
        self._tempo_pendente += segundos
        # Salvar apenas a cada 5 segundos
        if self._tempo_pendente >= 5.0:
            self.salvar()
            self._tempo_pendente = 0.0
    
    def registrar_distancia(self, distancia_pixels):
        """Registra distância percorrida (em pixels)"""
        self.estatisticas_gerais["distancia_total"] += distancia_pixels
        # Não salvar a cada frame para melhorar performance
        if not hasattr(self, '_ultimo_salvamento_distancia'):
            self._ultimo_salvamento_distancia = 0
        self._ultimo_salvamento_distancia += distancia_pixels
        # Salvar apenas a cada 1000 pixels para reduzir I/O
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
        # Não salvar a cada volta para melhorar performance
        if not hasattr(self, '_voltas_pendentes'):
            self._voltas_pendentes = 0
        self._voltas_pendentes += 1
        # Salvar apenas a cada 5 voltas
        if self._voltas_pendentes >= 5:
            self.salvar()
            self._voltas_pendentes = 0
    
    def registrar_colisao(self, numero_pista=None):
        """Registra uma colisão"""
        self.estatisticas_gerais["colisoes_totais"] += 1
        if numero_pista is not None:
            stats_pista = self._obter_estatisticas_pista(numero_pista)
            stats_pista["colisoes"] += 1
        # Não salvar a cada colisão para melhorar performance
        if not hasattr(self, '_colisoes_pendentes'):
            self._colisoes_pendentes = 0
        self._colisoes_pendentes += 1
        # Salvar apenas a cada 10 colisões
        if self._colisoes_pendentes >= 10:
            self.salvar()
            self._colisoes_pendentes = 0
    
    def registrar_drift(self):
        """Registra uso de drift"""
        self.estatisticas_gerais["drifts_totais"] += 1
        # Não salvar a cada drift para melhorar performance
        if not hasattr(self, '_drifts_pendentes'):
            self._drifts_pendentes = 0
        self._drifts_pendentes += 1
        # Salvar apenas a cada 10 drifts
        if self._drifts_pendentes >= 10:
            self.salvar()
            self._drifts_pendentes = 0
    
    def registrar_turbo(self):
        """Registra uso de turbo"""
        self.estatisticas_gerais["turbo_usado"] += 1
        # Não salvar a cada turbo para melhorar performance
        if not hasattr(self, '_turbos_pendentes'):
            self._turbos_pendentes = 0
        self._turbos_pendentes += 1
        # Salvar apenas a cada 10 turbos
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
        self.salvar()  # Salvar imediatamente para troféus (evento importante)
    
    def finalizar_sessao(self):
        """Salva todas as estatísticas pendentes"""
        # Forçar salvamento de todas as estatísticas pendentes
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

