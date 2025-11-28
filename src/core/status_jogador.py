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
        # Status (0.0 a 100.0)
        self.popularidade = 50.0  # Ganha/perde com corridas, afeta multiplicador de dinheiro
        self.fome = 100.0  # Desce com tempo, sobe ao comer
        self.sono = 100.0  # Desce com tempo, sobe ao dormir
        self.tedio = 0.0  # Sobe com tempo, desce ao assistir TV
        
        # Timestamps para decaimento
        self.ultima_atualizacao = 0.0  # Timestamp da última atualização
        
        # Taxas de decaimento (por segundo)
        self.taxa_fome = 0.5  # 0.5 por segundo = 50 por 100 segundos
        self.taxa_sono = 0.3  # 0.3 por segundo = 30 por 100 segundos
        self.taxa_tedio = 0.2  # 0.2 por segundo = 20 por 100 segundos
        
        # Carregar status salvos
        self.carregar()
    
    def atualizar(self, dt: float):
        """Atualiza os status com base no tempo decorrido"""
        # Decaimento de fome
        self.fome = max(0.0, self.fome - self.taxa_fome * dt)
        
        # Decaimento de sono
        self.sono = max(0.0, self.sono - self.taxa_sono * dt)
        
        # Aumento de tédio
        self.tedio = min(100.0, self.tedio + self.taxa_tedio * dt)
    
    def comer(self, quantidade: float = 50.0):
        """Aumenta fome ao comer na geladeira"""
        self.fome = min(100.0, self.fome + quantidade)
    
    def dormir(self, local: str = "cama", quantidade: float = None):
        """Aumenta sono ao dormir"""
        if quantidade is None:
            # Valores padrão por local
            valores = {
                "cama": 100.0,  # Recarrega completamente
                "sofa": 50.0,  # Recarrega metade
                "cafe": 30.0   # Recarrega pouco (café)
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
        # Popularidade 0 = 0.5x, 50 = 1.0x, 100 = 1.5x
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
        # Sono 0 = 0.5x controle, 100 = 1.0x controle
        # Fórmula: 0.5 + (sono / 200.0) = 0.5 + (100 / 200.0) = 1.0 quando sono = 100
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

# Instância global
status_jogador = StatusJogador()

