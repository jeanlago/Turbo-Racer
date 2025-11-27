# src/core/missoes.py
import json
import os
from config import DIR_PROJETO

CAMINHO_MISSOES = os.path.join(DIR_PROJETO, "data", "missions.json")

class GerenciadorMissoes:
    """Gerencia as missões do jogo: ativação, conclusão e exibição no HUD"""
    
    def __init__(self):
        self.missoes = {}
        self.missao_ativa_id = None
        self.missoes_completas = set()
        self.carregar()
    
    def carregar(self):
        """Carrega as missões do arquivo JSON"""
        if os.path.exists(CAMINHO_MISSOES):
            try:
                with open(CAMINHO_MISSOES, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for missao in data.get("missions", []):
                        self.missoes[missao["id"]] = {
                            "id": missao["id"],
                            "nome": missao.get("nome", missao["id"]),
                            "objetivo": missao.get("objetivo", ""),
                            "activateOnSceneId": missao.get("activateOnSceneId"),
                            "completeOnSceneId": missao.get("completeOnSceneId"),
                            "chapter": missao.get("chapter", "ch1")
                        }
            except Exception as e:
                print(f"Erro ao carregar missões: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Arquivo de missões não encontrado: {CAMINHO_MISSOES}")
    
    def ativar_missao(self, missao_id: str):
        """Ativa uma missão"""
        if missao_id in self.missoes:
            self.missao_ativa_id = missao_id
            print(f"Missão ativada: {self.missoes[missao_id]['nome']}")
            return True
        return False
    
    def ativar_por_cena(self, scene_id: str):
        """Ativa uma missão baseada no ID da cena"""
        for missao_id, missao in self.missoes.items():
            if missao.get("activateOnSceneId") == scene_id:
                self.ativar_missao(missao_id)
                return missao_id
        return None
    
    def completar_missao(self, missao_id: str = None):
        """Completa a missão ativa ou uma missão específica"""
        if missao_id is None:
            missao_id = self.missao_ativa_id
        
        if missao_id and missao_id in self.missoes:
            self.missoes_completas.add(missao_id)
            if self.missao_ativa_id == missao_id:
                self.missao_ativa_id = None
            print(f"Missão completada: {self.missoes[missao_id]['nome']}")
            return True
        return False
    
    def completar_por_cena(self, scene_id: str):
        """Completa uma missão baseada no ID da cena"""
        for missao_id, missao in self.missoes.items():
            if missao.get("completeOnSceneId") == scene_id:
                self.completar_missao(missao_id)
                return missao_id
        return None
    
    def obter_missao_ativa(self):
        """Retorna a missão ativa atual"""
        if self.missao_ativa_id and self.missao_ativa_id in self.missoes:
            return self.missoes[self.missao_ativa_id]
        return None
    
    def esta_completa(self, missao_id: str) -> bool:
        """Verifica se uma missão está completa"""
        return missao_id in self.missoes_completas
    
    def obter_nome_missao(self) -> str:
        """Retorna o nome da missão ativa para o HUD"""
        missao = self.obter_missao_ativa()
        if missao:
            return missao["nome"]
        return ""
    
    def obter_objetivo_missao(self) -> str:
        """Retorna o objetivo da missão ativa para o HUD"""
        missao = self.obter_missao_ativa()
        if missao:
            return missao["objetivo"]
        return ""

# Instância global
gerenciador_missoes = GerenciadorMissoes()

