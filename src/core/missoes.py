# src/core/missoes.py
import json
import os
from config import DIR_PROJETO

CAMINHO_MISSOES = os.path.join(DIR_PROJETO, "data", "missions.json")
CAMINHO_MISSOES_COMPLETAS = os.path.join(DIR_PROJETO, "data", "missoes_completas.json")

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
        
        # Carregar missões completas
        self._carregar_missoes_completas()
    
    def _carregar_missoes_completas(self):
        """Carrega as missões completas do arquivo"""
        if os.path.exists(CAMINHO_MISSOES_COMPLETAS):
            try:
                with open(CAMINHO_MISSOES_COMPLETAS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.missoes_completas = set(data.get("missoes_completas", []))
                    self.missao_ativa_id = data.get("missao_ativa_id", None)
                print(f"[MISSÕES] Missões carregadas: {len(self.missoes_completas)} completas, ativa: {self.missao_ativa_id}")
            except Exception as e:
                print(f"[MISSÕES] Erro ao carregar missões completas: {e}")
                import traceback
                traceback.print_exc()
                self.missoes_completas = set()
        else:
            print(f"[MISSÕES] Arquivo de missões completas não encontrado: {CAMINHO_MISSOES_COMPLETAS}")
            self.missoes_completas = set()
    
    def salvar(self):
        """Salva as missões completas no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_MISSOES_COMPLETAS), exist_ok=True)
            data = {
                "missoes_completas": list(self.missoes_completas),
                "missao_ativa_id": self.missao_ativa_id
            }
            with open(CAMINHO_MISSOES_COMPLETAS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[MISSÕES] Missões salvas: {len(self.missoes_completas)} completas, ativa: {self.missao_ativa_id}")
        except Exception as e:
            print(f"[MISSÕES] Erro ao salvar missões completas: {e}")
            import traceback
            traceback.print_exc()
    
    def ativar_missao(self, missao_id: str):
        """Ativa uma missão"""
        if missao_id in self.missoes:
            self.missao_ativa_id = missao_id
            self.salvar()
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
            if missao_id not in self.missoes_completas:
                self.missoes_completas.add(missao_id)
                print(f"[MISSÕES] Missão '{missao_id}' marcada como completa")
            if self.missao_ativa_id == missao_id:
                self.missao_ativa_id = None
            self.salvar()
            return True
        else:
            if missao_id:
                print(f"[MISSÕES] Aviso: Tentativa de completar missão inexistente: {missao_id}")
        return False
    
    def completar_por_cena(self, scene_id: str):
        """Completa uma missão baseada no ID da cena"""
        for missao_id, missao in self.missoes.items():
            if missao.get("completeOnSceneId") == scene_id:
                self.completar_missao(missao_id)
                return missao_id
        
        # Completar m8_oferta_envenenada quando o jogador decide sobre o empréstimo
        # (tanto aceitando quanto recusando)
        if scene_id in ["ch2_4_loan_accepted", "ch2_5_loan_refused"]:
            if "m8_oferta_envenenada" in self.missoes and "m8_oferta_envenenada" not in self.missoes_completas:
                self.completar_missao("m8_oferta_envenenada")
                return "m8_oferta_envenenada"
        
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
    
    def obter_todas_missoes(self):
        """Retorna todas as missões como uma lista ordenada por capítulo"""
        missoes_lista = []
        for missao_id, missao in self.missoes.items():
            missoes_lista.append(missao)
        missoes_lista.sort(key=lambda m: (m.get("chapter", "ch1"), m.get("id", "")))
        return missoes_lista

gerenciador_missoes = GerenciadorMissoes()

