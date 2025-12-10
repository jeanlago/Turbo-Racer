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
    
    SEGUNDOS_POR_HORA_JOGO = 60.0
    
    def __init__(self):
        from datetime import datetime, timedelta, date
        self.data_inicial = date(1990, 12, 5)
        self.hora_jogo = 12
        self.dia_jogo = 1
        
        self.ultima_atualizacao_timestamp = time.time()
        
        self.carregar()
        
        self._atualizar_estado_dia_noite()
    
    def atualizar(self, dt: float = None):
        """Atualiza o tempo do jogo baseado no tempo real decorrido
        
        Args:
            dt: Delta time em segundos. Se None, calcula automaticamente
        """
        if dt is None:
            agora = time.time()
            dt = agora - self.ultima_atualizacao_timestamp
            self.ultima_atualizacao_timestamp = agora
        
        horas_decorridas = dt / self.SEGUNDOS_POR_HORA_JOGO
        hora_anterior = self.hora_jogo
        
        self.hora_jogo += horas_decorridas
        
        dias_passados = 0
        while self.hora_jogo >= 24.0:
            self.hora_jogo -= 24.0
            dias_passados += 1
        while self.hora_jogo < 0.0:
            self.hora_jogo += 24.0
        
        if dias_passados > 0:
            self.dia_jogo += dias_passados
            print(f"[TEMPO] Passou meia-noite! Avançou {dias_passados} dia(s). Dia atual: {self.dia_jogo}, Data: {self.obter_data_formatada()}")
        
        self._atualizar_estado_dia_noite()
    
    def obter_dia_atual(self) -> int:
        """Retorna o dia atual do jogo
        
        Returns:
            Número do dia (começando em 1)
        """
        return self.dia_jogo
    
    def obter_data_atual(self):
        """Retorna a data atual do jogo como datetime.date
        
        Returns:
            datetime.date: Data atual do jogo
        """
        from datetime import timedelta
        return self.data_inicial + timedelta(days=self.dia_jogo - 1)
    
    def obter_data_formatada(self) -> str:
        """Retorna a data atual formatada como DD/MM/YYYY
        
        Returns:
            String com data formatada (ex: "05/12/1990")
        """
        data_atual = self.obter_data_atual()
        return data_atual.strftime("%d/%m/%Y")
    
    def _atualizar_estado_dia_noite(self):
        """Atualiza o estado dia/noite baseado na hora do jogo"""
        if 6.0 <= self.hora_jogo < 18.0:
            estado = "dia"
        else:
            estado = "noite"
        
        if obter_estado_dia_noite() != estado:
            definir_estado_dia_noite(estado)
    
    def avancar_horas(self, horas: float):
        """Avança o tempo do jogo em horas
        
        Args:
            horas: Quantidade de horas para avançar
        """
        self.hora_jogo += horas
        
        # Verificar se passou um dia (hora passou de 24 para 0)
        dias_passados = 0
        while self.hora_jogo >= 24.0:
            self.hora_jogo -= 24.0
            dias_passados += 1
        while self.hora_jogo < 0.0:
            self.hora_jogo += 24.0
        
        # Atualizar contador de dias
        if dias_passados > 0:
            self.dia_jogo += dias_passados
            print(f"[TEMPO] Avançou {dias_passados} dia(s). Dia atual: {self.dia_jogo}, Data: {self.obter_data_formatada()}")
        
        self._atualizar_estado_dia_noite()
    
    def obter_hora_atual(self) -> float:
        """Retorna a hora atual do jogo (0-24)
        
        Returns:
            Hora atual como float (ex: 18.5 = 18:30)
        """
        return self.hora_jogo
    
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
        """Carrega o tempo do jogo do progresso.json"""
        # Primeiro, tentar carregar do progresso.json (fonte principal)
        try:
            from core.progresso import gerenciador_progresso
            caminho_progresso = os.path.join(os.path.dirname(CAMINHO_TEMPO), 'progresso.json')
            caminho_progresso = os.path.normpath(caminho_progresso)
            
            if os.path.exists(caminho_progresso):
                with open(caminho_progresso, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'tempo_jogo' in data:
                        tempo_data = data.get('tempo_jogo', {})
                        self.hora_jogo = tempo_data.get('hora_jogo', 12.0)
                        self.dia_jogo = tempo_data.get('dia_jogo', 1)
                        self.ultima_atualizacao_timestamp = tempo_data.get('ultima_atualizacao_timestamp', time.time())
                        # Carregar data_inicial se disponível
                        if 'data_inicial' in tempo_data:
                            from datetime import datetime
                            data_str = tempo_data['data_inicial']
                            self.data_inicial = datetime.strptime(data_str, "%Y-%m-%d").date()
                        else:
                            from datetime import date
                            self.data_inicial = date(1990, 12, 5)
                        print(f"[TEMPO] Carregado do progresso.json: hora={self.hora_jogo:.2f}, dia={self.dia_jogo}, data={self.obter_data_formatada()}")
                        return  # Dados carregados do progresso.json, não precisa do arquivo antigo
        except Exception as e:
            print(f"[TEMPO] Erro ao carregar do progresso.json: {e}")
        
        # Fallback: valores padrão se não houver dados (começar em 05/12/1990)
        self.hora_jogo = 12.0
        self.dia_jogo = 1
        self.ultima_atualizacao_timestamp = time.time()
        # Data inicial: 05/12/1990
        from datetime import date
        self.data_inicial = date(1990, 12, 5)
    
    def salvar(self):
        """Salva o tempo do jogo (agora salvo no progresso.json)"""
        # Dados são salvos através do GerenciadorProgresso.salvar()
        # Este método existe para compatibilidade, mas não salva mais em arquivo separado
        try:
            from core.progresso import gerenciador_progresso
            gerenciador_progresso.salvar()  # Isso salvará tudo, incluindo tempo
        except Exception as e:
            print(f"Erro ao salvar tempo do jogo: {e}")

gerenciador_tempo = GerenciadorTempoJogo()

