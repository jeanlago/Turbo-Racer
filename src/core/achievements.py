"""
Sistema de Achievements/Conquistas
"""
import json
import os
from config import DIR_PROJETO

CAMINHO_ACHIEVEMENTS = os.path.join(DIR_PROJETO, "data", "achievements.json")

ACHIEVEMENTS = {
    "primeira_corrida": {
        "id": "primeira_corrida",
        "nome": "Primeira Corrida",
        "descricao": "Complete sua primeira corrida",
        "recompensa": 200
    },
    "velocista": {
        "id": "velocista",
        "nome": "Velocista",
        "descricao": "Alcance 200 km/h",
        "recompensa": 400
    },
    "velocista_pro": {
        "id": "velocista_pro",
        "nome": "Velocista Pro",
        "descricao": "Alcance 250 km/h",
        "recompensa": 600
    },
    "velocidade_extrema": {
        "id": "velocidade_extrema",
        "nome": "Velocidade Extrema",
        "descricao": "Alcance 300 km/h",
        "recompensa": 1000
    },
    "drift_master": {
        "id": "drift_master",
        "nome": "Mestre do Drift",
        "descricao": "Complete 10 voltas em modo drift",
        "recompensa": 500
    },
    "drift_expert": {
        "id": "drift_expert",
        "nome": "Expert em Drift",
        "descricao": "Complete 25 voltas em modo drift",
        "recompensa": 800
    },
    "drift_legend": {
        "id": "drift_legend",
        "nome": "Lenda do Drift",
        "descricao": "Complete 50 voltas em modo drift",
        "recompensa": 1500
    },
    "sem_colisao": {
        "id": "sem_colisao",
        "nome": "Piloto Limpo",
        "descricao": "Complete uma corrida sem colisões",
        "recompensa": 400
    },
    "sem_colisao_mestre": {
        "id": "sem_colisao_mestre",
        "nome": "Mestre da Precisão",
        "descricao": "Complete 5 corridas sem colisões",
        "recompensa": 800
    },
    "trofeu_ouro": {
        "id": "trofeu_ouro",
        "nome": "Campeão",
        "descricao": "Ganhe um troféu de ouro",
        "recompensa": 1000
    },
    "colecionador": {
        "id": "colecionador",
        "nome": "Colecionador",
        "descricao": "Desbloqueie 5 carros",
        "recompensa": 600
    },
    "colecionador_pro": {
        "id": "colecionador_pro",
        "nome": "Colecionador Pro",
        "descricao": "Desbloqueie 10 carros",
        "recompensa": 1200
    },
    "perfeccionista": {
        "id": "perfeccionista",
        "nome": "Perfeccionista",
        "descricao": "Complete 10 corridas sem erros",
        "recompensa": 600
    },
    "perfeccionista_mestre": {
        "id": "perfeccionista_mestre",
        "nome": "Mestre Perfeccionista",
        "descricao": "Complete 25 corridas sem erros",
        "recompensa": 1200
    },
    "sem_erros_perfeito": {
        "id": "sem_erros_perfeito",
        "nome": "Perfeição Absoluta",
        "descricao": "Complete 50 corridas sem erros",
        "recompensa": 2000
    },
    "recordista": {
        "id": "recordista",
        "nome": "Recordista",
        "descricao": "Estabeleça 5 novos recordes",
        "recompensa": 800
    },
    "recordista_pro": {
        "id": "recordista_pro",
        "nome": "Recordista Pro",
        "descricao": "Estabeleça 10 novos recordes",
        "recompensa": 1500
    },
    "upgrade_completo": {
        "id": "upgrade_completo",
        "nome": "Tunado",
        "descricao": "Maximize todos os upgrades de um carro",
        "recompensa": 1000
    },
    "upgrade_mestre": {
        "id": "upgrade_mestre",
        "nome": "Mestre da Tunagem",
        "descricao": "Maximize todos os upgrades de 3 carros",
        "recompensa": 2500
    },
    "veterano": {
        "id": "veterano",
        "nome": "Veterano",
        "descricao": "Complete 50 corridas",
        "recompensa": 1200
    },
    "lenda": {
        "id": "lenda",
        "nome": "Lenda",
        "descricao": "Complete 100 corridas",
        "recompensa": 2000
    },
    "piloto_estrella": {
        "id": "piloto_estrella",
        "nome": "Piloto Estrela",
        "descricao": "Complete 200 corridas",
        "recompensa": 3500
    }
}


class GerenciadorAchievements:
    """Gerencia achievements/conquistas do jogador"""
    
    def __init__(self):
        from core.progresso import gerenciador_progresso
        self.gerenciador_progresso = gerenciador_progresso
        self.carregar()
    
    @property
    def achievements_desbloqueados(self):
        """Retorna os achievements desbloqueados do progresso.json"""
        return self.gerenciador_progresso.achievements_desbloqueados
    
    @achievements_desbloqueados.setter
    def achievements_desbloqueados(self, value):
        """Define os achievements desbloqueados no progresso.json"""
        self.gerenciador_progresso.achievements_desbloqueados = value if isinstance(value, set) else set(value)
        self.gerenciador_progresso.salvar()
    
    @property
    def achievements_visualizados(self):
        """Retorna os achievements visualizados do progresso.json"""
        return self.gerenciador_progresso.achievements_visualizados
    
    @achievements_visualizados.setter
    def achievements_visualizados(self, value):
        """Define os achievements visualizados no progresso.json"""
        self.gerenciador_progresso.achievements_visualizados = value if isinstance(value, set) else set(value)
        self.gerenciador_progresso.salvar()
    
    @property
    def estatisticas(self):
        """Retorna as estatísticas de achievements do progresso.json"""
        return self.gerenciador_progresso.achievements_estatisticas
    
    @estatisticas.setter
    def estatisticas(self, value):
        """Define as estatísticas de achievements no progresso.json"""
        self.gerenciador_progresso.achievements_estatisticas = value
        self.gerenciador_progresso.salvar()
    
    def carregar(self):
        """Carrega achievements do progresso.json"""
        pass
    
    def salvar(self):
        """Salva achievements no progresso.json"""
        self.gerenciador_progresso.salvar()
    
    def esta_desbloqueado(self, achievement_id):
        """Verifica se um achievement está desbloqueado"""
        return achievement_id in self.achievements_desbloqueados
    
    def desbloquear(self, achievement_id, gerenciador_progresso=None):
        """
        Desbloqueia um achievement e concede recompensa
        
        Args:
            achievement_id: ID do achievement
            gerenciador_progresso: Instância do GerenciadorProgresso para adicionar dinheiro
        """
        if achievement_id in self.achievements_desbloqueados:
            return False  # Já está desbloqueado
        
        if achievement_id not in ACHIEVEMENTS:
            print(f"Erro: Achievement '{achievement_id}' não encontrado")
            return False
        
        self.achievements_desbloqueados.add(achievement_id)
        achievement = ACHIEVEMENTS[achievement_id]
        
        if gerenciador_progresso:
            gerenciador_progresso.adicionar_dinheiro(achievement['recompensa'])
        
        self.salvar()
        print(f"🎉 Achievement desbloqueado: {achievement['nome']} - {achievement['descricao']} (+${achievement['recompensa']})")
        return True
    
    def atualizar_estatistica(self, chave, valor=None, incrementar=False):
        """
        Atualiza uma estatística
        
        Args:
            chave: Nome da estatística
            valor: Novo valor (se incrementar=False) ou valor a adicionar (se incrementar=True)
            incrementar: Se True, adiciona ao valor atual; se False, substitui
        """
        if chave not in self.estatisticas:
            self.estatisticas[chave] = 0
        
        if incrementar:
            self.estatisticas[chave] += valor if valor is not None else 1
        else:
            self.estatisticas[chave] = valor if valor is not None else self.estatisticas[chave]
        
        self.salvar()
    
    def obter_estatistica(self, chave):
        """Obtém o valor de uma estatística"""
        return self.estatisticas.get(chave, 0)
    
    def verificar_achievements(self, gerenciador_progresso):
        """
        Verifica e desbloqueia achievements baseado nas estatísticas atuais
        
        Args:
            gerenciador_progresso: Instância do GerenciadorProgresso
        
        Returns:
            list: Lista de achievements recém-desbloqueados (cada item é um dict com 'id', 'nome', 'recompensa')
        """
        achievements_desbloqueados = []
        
        # Primeira corrida
        if not self.esta_desbloqueado("primeira_corrida") and self.estatisticas["corridas_completas"] >= 1:
            if self.desbloquear("primeira_corrida", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "primeira_corrida",
                    'nome': ACHIEVEMENTS["primeira_corrida"]["nome"],
                    'recompensa': ACHIEVEMENTS["primeira_corrida"]["recompensa"]
                })
        
        # Velocista (200 km/h)
        if not self.esta_desbloqueado("velocista") and self.estatisticas["velocidade_maxima"] >= 200.0:
            if self.desbloquear("velocista", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "velocista",
                    'nome': ACHIEVEMENTS["velocista"]["nome"],
                    'recompensa': ACHIEVEMENTS["velocista"]["recompensa"]
                })
        
        # Velocista Pro (250 km/h)
        if not self.esta_desbloqueado("velocista_pro") and self.estatisticas["velocidade_maxima"] >= 250.0:
            if self.desbloquear("velocista_pro", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "velocista_pro",
                    'nome': ACHIEVEMENTS["velocista_pro"]["nome"],
                    'recompensa': ACHIEVEMENTS["velocista_pro"]["recompensa"]
                })
        
        # Velocidade Extrema (300 km/h)
        if not self.esta_desbloqueado("velocidade_extrema") and self.estatisticas["velocidade_maxima"] >= 300.0:
            if self.desbloquear("velocidade_extrema", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "velocidade_extrema",
                    'nome': ACHIEVEMENTS["velocidade_extrema"]["nome"],
                    'recompensa': ACHIEVEMENTS["velocidade_extrema"]["recompensa"]
                })
        
        # Mestre do Drift (10 voltas)
        if not self.esta_desbloqueado("drift_master") and self.estatisticas["voltas_drift"] >= 10:
            if self.desbloquear("drift_master", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "drift_master",
                    'nome': ACHIEVEMENTS["drift_master"]["nome"],
                    'recompensa': ACHIEVEMENTS["drift_master"]["recompensa"]
                })
        
        # Expert em Drift (25 voltas)
        if not self.esta_desbloqueado("drift_expert") and self.estatisticas["voltas_drift"] >= 25:
            if self.desbloquear("drift_expert", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "drift_expert",
                    'nome': ACHIEVEMENTS["drift_expert"]["nome"],
                    'recompensa': ACHIEVEMENTS["drift_expert"]["recompensa"]
                })
        
        # Lenda do Drift (50 voltas)
        if not self.esta_desbloqueado("drift_legend") and self.estatisticas["voltas_drift"] >= 50:
            if self.desbloquear("drift_legend", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "drift_legend",
                    'nome': ACHIEVEMENTS["drift_legend"]["nome"],
                    'recompensa': ACHIEVEMENTS["drift_legend"]["recompensa"]
                })
        
        # Piloto Limpo (sem colisão)
        if not self.esta_desbloqueado("sem_colisao") and self.estatisticas["corridas_sem_colisao"] >= 1:
            if self.desbloquear("sem_colisao", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "sem_colisao",
                    'nome': ACHIEVEMENTS["sem_colisao"]["nome"],
                    'recompensa': ACHIEVEMENTS["sem_colisao"]["recompensa"]
                })
        
        # Mestre da Precisão (5 corridas sem colisão)
        if not self.esta_desbloqueado("sem_colisao_mestre") and self.estatisticas["corridas_sem_colisao"] >= 5:
            if self.desbloquear("sem_colisao_mestre", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "sem_colisao_mestre",
                    'nome': ACHIEVEMENTS["sem_colisao_mestre"]["nome"],
                    'recompensa': ACHIEVEMENTS["sem_colisao_mestre"]["recompensa"]
                })
        
        # Colecionador (5 carros)
        if not self.esta_desbloqueado("colecionador") and self.estatisticas["carros_desbloqueados"] >= 5:
            if self.desbloquear("colecionador", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "colecionador",
                    'nome': ACHIEVEMENTS["colecionador"]["nome"],
                    'recompensa': ACHIEVEMENTS["colecionador"]["recompensa"]
                })
        
        # Colecionador Pro (10 carros)
        if not self.esta_desbloqueado("colecionador_pro") and self.estatisticas["carros_desbloqueados"] >= 10:
            if self.desbloquear("colecionador_pro", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "colecionador_pro",
                    'nome': ACHIEVEMENTS["colecionador_pro"]["nome"],
                    'recompensa': ACHIEVEMENTS["colecionador_pro"]["recompensa"]
                })
        
        # Perfeccionista (10 corridas sem erros)
        if not self.esta_desbloqueado("perfeccionista") and self.estatisticas["corridas_sem_erros"] >= 10:
            if self.desbloquear("perfeccionista", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "perfeccionista",
                    'nome': ACHIEVEMENTS["perfeccionista"]["nome"],
                    'recompensa': ACHIEVEMENTS["perfeccionista"]["recompensa"]
                })
        
        # Mestre Perfeccionista (25 corridas sem erros)
        if not self.esta_desbloqueado("perfeccionista_mestre") and self.estatisticas["corridas_sem_erros"] >= 25:
            if self.desbloquear("perfeccionista_mestre", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "perfeccionista_mestre",
                    'nome': ACHIEVEMENTS["perfeccionista_mestre"]["nome"],
                    'recompensa': ACHIEVEMENTS["perfeccionista_mestre"]["recompensa"]
                })
        
        # Perfeição Absoluta (50 corridas sem erros)
        if not self.esta_desbloqueado("sem_erros_perfeito") and self.estatisticas["corridas_sem_erros"] >= 50:
            if self.desbloquear("sem_erros_perfeito", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "sem_erros_perfeito",
                    'nome': ACHIEVEMENTS["sem_erros_perfeito"]["nome"],
                    'recompensa': ACHIEVEMENTS["sem_erros_perfeito"]["recompensa"]
                })
        
        # Recordista (5 recordes)
        if not self.esta_desbloqueado("recordista") and self.estatisticas["recordes_estabelecidos"] >= 5:
            if self.desbloquear("recordista", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "recordista",
                    'nome': ACHIEVEMENTS["recordista"]["nome"],
                    'recompensa': ACHIEVEMENTS["recordista"]["recompensa"]
                })
        
        # Recordista Pro (10 recordes)
        if not self.esta_desbloqueado("recordista_pro") and self.estatisticas["recordes_estabelecidos"] >= 10:
            if self.desbloquear("recordista_pro", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "recordista_pro",
                    'nome': ACHIEVEMENTS["recordista_pro"]["nome"],
                    'recompensa': ACHIEVEMENTS["recordista_pro"]["recompensa"]
                })
        
        # Tunado (upgrade completo)
        if not self.esta_desbloqueado("upgrade_completo") and self.estatisticas["upgrades_maximizados"] >= 1:
            if self.desbloquear("upgrade_completo", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "upgrade_completo",
                    'nome': ACHIEVEMENTS["upgrade_completo"]["nome"],
                    'recompensa': ACHIEVEMENTS["upgrade_completo"]["recompensa"]
                })
        
        # Mestre da Tunagem (3 upgrades completos)
        if not self.esta_desbloqueado("upgrade_mestre") and self.estatisticas["upgrades_maximizados"] >= 3:
            if self.desbloquear("upgrade_mestre", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "upgrade_mestre",
                    'nome': ACHIEVEMENTS["upgrade_mestre"]["nome"],
                    'recompensa': ACHIEVEMENTS["upgrade_mestre"]["recompensa"]
                })
        
        # Veterano (50 corridas)
        if not self.esta_desbloqueado("veterano") and self.estatisticas["corridas_completas"] >= 50:
            if self.desbloquear("veterano", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "veterano",
                    'nome': ACHIEVEMENTS["veterano"]["nome"],
                    'recompensa': ACHIEVEMENTS["veterano"]["recompensa"]
                })
        
        # Lenda (100 corridas)
        if not self.esta_desbloqueado("lenda") and self.estatisticas["corridas_completas"] >= 100:
            if self.desbloquear("lenda", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "lenda",
                    'nome': ACHIEVEMENTS["lenda"]["nome"],
                    'recompensa': ACHIEVEMENTS["lenda"]["recompensa"]
                })
        
        # Piloto Estrela (200 corridas)
        if not self.esta_desbloqueado("piloto_estrella") and self.estatisticas["corridas_completas"] >= 200:
            if self.desbloquear("piloto_estrella", gerenciador_progresso):
                achievements_desbloqueados.append({
                    'id': "piloto_estrella",
                    'nome': ACHIEVEMENTS["piloto_estrella"]["nome"],
                    'recompensa': ACHIEVEMENTS["piloto_estrella"]["recompensa"]
                })
        
        return achievements_desbloqueados
    
    def obter_todos_achievements(self):
        """Retorna todos os achievements com status de desbloqueio"""
        resultado = []
        for achievement_id, achievement_data in ACHIEVEMENTS.items():
            desbloqueado = achievement_id in self.achievements_desbloqueados
            resultado.append({
                **achievement_data,
                'desbloqueado': desbloqueado
            })
        return resultado
    
    def contar_desbloqueados(self):
        """Retorna o número de achievements desbloqueados"""
        return len(self.achievements_desbloqueados)
    
    def contar_total(self):
        """Retorna o número total de achievements"""
        return len(ACHIEVEMENTS)
    
    def tem_achievements_nao_visualizados(self):
        """Verifica se há achievements desbloqueados mas não visualizados"""
        return len(self.achievements_desbloqueados - self.achievements_visualizados) > 0
    
    def marcar_como_visualizado(self, achievement_id):
        """Marca um achievement como visualizado"""
        if achievement_id in self.achievements_desbloqueados:
            self.achievements_visualizados.add(achievement_id)
            self.salvar()
    
    def marcar_todos_como_visualizados(self):
        """Marca todos os achievements desbloqueados como visualizados"""
        self.achievements_visualizados = self.achievements_desbloqueados.copy()
        self.salvar()


gerenciador_achievements = GerenciadorAchievements()

