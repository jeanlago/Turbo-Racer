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
        self.popularidade = 50.0
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
        self.popularidade = min(100.0, self.popularidade + quantidade)
    
    def perder_popularidade(self, quantidade: float):
        """Diminui popularidade (ao perder corridas)"""
        self.popularidade = max(0.0, self.popularidade - quantidade)
    
    def obter_multiplicador_dinheiro(self) -> float:
        """Retorna multiplicador de dinheiro baseado na popularidade"""
        return 0.5 + (self.popularidade / 100.0)
    
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
        """Carrega status do arquivo"""
        if os.path.exists(CAMINHO_STATUS):
            try:
                with open(CAMINHO_STATUS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.popularidade = data.get("popularidade", 50.0)
                    self.fome = data.get("fome", 100.0)
                    self.sono = data.get("sono", 100.0)
                    self.tedio = data.get("tedio", 0.0)
            except Exception as e:
                print(f"Erro ao carregar status: {e}")
    
    def salvar(self):
        """Salva status no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_STATUS), exist_ok=True)
            data = {
                "popularidade": self.popularidade,
                "fome": self.fome,
                "sono": self.sono,
                "tedio": self.tedio
            }
            with open(CAMINHO_STATUS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar status: {e}")

status_jogador = StatusJogador()

