# src/core/tempo_jogo.py
"""
Sistema de Tempo do Jogo
Gerencia o ciclo dia/noite baseado em tempo real
1 minuto real = 1 hora do jogo
"""

import os
import json
import time
from typing import Tuple
from config import DIR_PROJETO, definir_estado_dia_noite, obter_estado_dia_noite

CAMINHO_TEMPO = os.path.join(DIR_PROJETO, "data", "tempo_jogo.json")

class GerenciadorTempoJogo:
    """Gerencia o tempo do jogo e ciclo dia/noite"""
    
    # 1 minuto real = 1 hora do jogo
    SEGUNDOS_POR_HORA_JOGO = 60.0  # 60 segundos reais = 1 hora do jogo
    
    def __init__(self):
        # Hora do jogo (0-23)
        self.hora_jogo = 12  # Começa ao meio-dia (12:00)
        
        # Timestamp da última atualização
        self.ultima_atualizacao_timestamp = time.time()
        
        # Carregar tempo salvo
        self.carregar()
        
        # Atualizar estado dia/noite inicial
        self._atualizar_estado_dia_noite()
    
    def atualizar(self, dt: float = None):
        """Atualiza o tempo do jogo baseado no tempo real decorrido
        
        Args:
            dt: Delta time em segundos. Se None, calcula automaticamente
        """
        if dt is None:
            # Calcular delta time desde última atualização
            agora = time.time()
            dt = agora - self.ultima_atualizacao_timestamp
            self.ultima_atualizacao_timestamp = agora
        
        # Converter tempo real para horas do jogo
        horas_decorridas = dt / self.SEGUNDOS_POR_HORA_JOGO
        
        # Avançar hora do jogo
        self.hora_jogo += horas_decorridas
        
        # Manter no ciclo de 24 horas
        while self.hora_jogo >= 24.0:
            self.hora_jogo -= 24.0
        while self.hora_jogo < 0.0:
            self.hora_jogo += 24.0
        
        # Atualizar estado dia/noite
        self._atualizar_estado_dia_noite()
    
    def _atualizar_estado_dia_noite(self):
        """Atualiza o estado dia/noite baseado na hora do jogo"""
        # Considerar dia de 6:00 às 18:00 (6h às 18h)
        # Noite de 18:00 às 6:00 (18h às 6h)
        if 6.0 <= self.hora_jogo < 18.0:
            estado = "dia"
        else:
            estado = "noite"
        
        # Só atualizar se mudou
        if obter_estado_dia_noite() != estado:
            definir_estado_dia_noite(estado)
    
    def avancar_horas(self, horas: float):
        """Avança o tempo do jogo em horas
        
        Args:
            horas: Quantidade de horas para avançar
        """
        self.hora_jogo += horas
        
        # Manter no ciclo de 24 horas
        while self.hora_jogo >= 24.0:
            self.hora_jogo -= 24.0
        while self.hora_jogo < 0.0:
            self.hora_jogo += 24.0
        
        # Atualizar estado dia/noite
        self._atualizar_estado_dia_noite()
    
    def obter_hora_formatada(self) -> str:
        """Retorna a hora do jogo formatada (HH:MM)
        
        Returns:
            String com hora formatada (ex: "14:30")
        """
        horas = int(self.hora_jogo)
        minutos = int((self.hora_jogo - horas) * 60)
        return f"{horas:02d}:{minutos:02d}"
    
    def obter_periodo_dia(self) -> str:
        """Retorna o período do dia
        
        Returns:
            "manhã", "tarde", "noite" ou "madrugada"
        """
        hora = int(self.hora_jogo)
        
        if 5 <= hora < 12:
            return "manhã"
        elif 12 <= hora < 18:
            return "tarde"
        elif 18 <= hora < 24:
            return "noite"
        else:  # 0 <= hora < 5
            return "madrugada"
    
    def eh_dia(self) -> bool:
        """Retorna True se for dia, False se for noite"""
        return obter_estado_dia_noite() == "dia"
    
    def eh_noite(self) -> bool:
        """Retorna True se for noite, False se for dia"""
        return obter_estado_dia_noite() == "noite"
    
    def carregar(self):
        """Carrega o tempo do jogo do arquivo"""
        if os.path.exists(CAMINHO_TEMPO):
            try:
                with open(CAMINHO_TEMPO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.hora_jogo = data.get("hora_jogo", 12.0)
                    # Limitar entre 0 e 24
                    self.hora_jogo = max(0.0, min(24.0, self.hora_jogo))
            except Exception as e:
                print(f"Erro ao carregar tempo do jogo: {e}")
                self.hora_jogo = 12.0
        
        # Atualizar timestamp
        self.ultima_atualizacao_timestamp = time.time()
    
    def salvar(self):
        """Salva o tempo do jogo no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_TEMPO), exist_ok=True)
            data = {
                "hora_jogo": self.hora_jogo
            }
            with open(CAMINHO_TEMPO, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar tempo do jogo: {e}")

# Instância global
gerenciador_tempo = GerenciadorTempoJogo()

