# src/core/status_jogador.py
"""
Sistema de Status do Jogador
Gerencia popularidade, fome, sono e tédio
"""

import os
import json
from typing import Dict, Tuple
from config import DIR_PROJETO

CAMINHO_STATUS = os.path.join(DIR_PROJETO, "data", "status_jogador.json")

class StatusJogador:
    """Gerencia os status do jogador"""
    
    def __init__(self):
        self.popularidade = 0.0  # Popularidade vai de 0 a 500
        self.fome = 100.0
        self.sono = 100.0
        self.tedio = 0.0
        
        self.ultima_atualizacao = 0.0
        
        self.taxa_fome = 0.5
        self.taxa_sono = 0.3
        self.taxa_tedio = 0.2
        
        self.carregar()
    
    def atualizar(self, dt: float):
        """Atualiza os status com base no tempo decorrido"""
        self.fome = max(0.0, self.fome - self.taxa_fome * dt)
        
        self.sono = max(0.0, self.sono - self.taxa_sono * dt)
        
        self.tedio = min(100.0, self.tedio + self.taxa_tedio * dt)
    
    def comer(self, quantidade: float = 50.0):
        """Aumenta fome ao comer na geladeira"""
        self.fome = min(100.0, self.fome + quantidade)
    
    def dormir(self, local: str = "cama", quantidade: float = None):
        """Aumenta sono ao dormir"""
        if quantidade is None:
            valores = {
                "cama": 100.0,
                "sofa": 50.0,
                "cafe": 30.0
            }
            quantidade = valores.get(local, 50.0)
        
        self.sono = min(100.0, self.sono + quantidade)
    
    def assistir_tv(self, quantidade: float = 50.0):
        """Reduz tédio ao assistir TV"""
        self.tedio = max(0.0, self.tedio - quantidade)
    
    def ganhar_popularidade(self, quantidade: float):
        """Aumenta popularidade (ao vencer corridas)"""
        self.popularidade = min(500.0, self.popularidade + quantidade)
        print(f"[STATUS] Popularidade aumentada: {self.popularidade:.1f}/500 (+{quantidade:.1f})")
    
    def perder_popularidade(self, quantidade: float):
        """Diminui popularidade (ao perder corridas)"""
        self.popularidade = max(0.0, self.popularidade - quantidade)
        print(f"[STATUS] Popularidade diminuída: {self.popularidade:.1f}/500 (-{quantidade:.1f})")
    
    def obter_multiplicador_dinheiro(self) -> float:
        """Retorna multiplicador de dinheiro baseado na popularidade (0-500)"""
        # Popularidade de 0-500 mapeada para multiplicador de 0.5 a 1.5
        return 0.5 + (self.popularidade / 500.0)
    
    def pode_fazer_upgrade(self) -> Tuple[bool, str]:
        """Verifica se pode fazer upgrade (verifica fome)"""
        if self.fome < 20.0:
            return False, "Estou com fome demais para isso agora..."
        return True, ""
    
    def pode_correr(self) -> Tuple[bool, str]:
        """Verifica se pode correr (verifica tédio)"""
        if self.tedio > 80.0:
            return False, "Estou entediado demais para correr agora..."
        return True, ""
    
    def obter_multiplicador_controle(self) -> float:
        """Retorna multiplicador de controle baseado no sono"""
        return 0.5 + (self.sono / 200.0)
    
    def carregar(self):
        """Carrega status do progresso.json"""
        # Primeiro, tentar carregar do progresso.json (fonte principal)
        try:
            from core.progresso import gerenciador_progresso
            caminho_progresso = os.path.join(os.path.dirname(CAMINHO_STATUS), 'progresso.json')
            caminho_progresso = os.path.normpath(caminho_progresso)
            
            if os.path.exists(caminho_progresso):
                with open(caminho_progresso, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'status_jogador' in data:
                        status_data = data.get('status_jogador', {})
                        self.popularidade = status_data.get('popularidade', 0.0)
                        self.fome = status_data.get('fome', 100.0)
                        self.sono = status_data.get('sono', 100.0)
                        self.tedio = status_data.get('tedio', 0.0)
                        print(f"[STATUS] Carregado do progresso.json: popularidade={self.popularidade:.1f}/500")
                        return  # Dados carregados do progresso.json
        except Exception as e:
            print(f"[STATUS] Erro ao carregar do progresso.json: {e}")
        
        # Fallback: valores padrão se não houver dados
        self.popularidade = 0.0  # Popularidade vai de 0 a 500
        self.fome = 100.0
        self.sono = 100.0
        self.tedio = 0.0
    
    def salvar(self):
        """Salva status"""
        # Dados são salvos através do GerenciadorProgresso.salvar()
        # Este método existe para compatibilidade, mas não salva mais em arquivo separado
        try:
            from core.progresso import gerenciador_progresso
            gerenciador_progresso.salvar()  # Isso salvará tudo, incluindo status
        except Exception as e:
            print(f"Erro ao salvar status: {e}")

status_jogador = StatusJogador()

