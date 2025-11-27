# src/core/territorios.py
"""
Sistema de Territórios da Cidade
Define os locais disponíveis no mapa isométrico e suas funcionalidades
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

class TipoTerritorio(Enum):
    """Tipos de territórios disponíveis"""
    DINHEIRO_RAPIDO = "dinheiro_rapido"  # Alto risco, alta recompensa
    PECAS_BRUTAS = "pecas_brutas"  # Sorte/azar, peças
    TECNICA = "tecnica"  # Melhorar dirigibilidade
    INFORMACAO = "informacao"  # Desbloqueios, informações
    PROGRESSAO = "progressao"  # História principal

class Territorio:
    """Representa um território no mapa da cidade"""
    
    def __init__(
        self,
        id: str,
        nome: str,
        descricao: str,
        tipo: TipoTerritorio,
        npc_id: str,
        posicao_mapa: Tuple[int, int],  # Posição no mapa isométrico (x, y)
        area_clicavel: Tuple[int, int, int, int],  # (x, y, largura, altura) para hitbox
        desbloqueado: bool = True,
        imagem_fundo: Optional[str] = None,
        atividades: Optional[List[Dict]] = None
    ):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.tipo = tipo
        self.npc_id = npc_id
        self.posicao_mapa = posicao_mapa
        self.area_clicavel = area_clicavel
        self.desbloqueado = desbloqueado
        self.imagem_fundo = imagem_fundo
        self.atividades = atividades or []
    
    def adicionar_atividade(self, atividade: Dict):
        """Adiciona uma atividade ao território"""
        self.atividades.append(atividade)
    
    def esta_desbloqueado(self) -> bool:
        """Verifica se o território está desbloqueado"""
        return self.desbloqueado
    
    def verificar_clique(self, mouse_x: int, mouse_y: int) -> bool:
        """Verifica se o mouse clicou na área clicável do território"""
        x, y, largura, altura = self.area_clicavel
        return (x <= mouse_x <= x + largura and 
                y <= mouse_y <= y + altura)

# Definição dos territórios da cidade
TERRITORIOS = {
    "docas_barao": Territorio(
        id="docas_barao",
        nome="As Docas do Barão",
        descricao="Empréstimos e corridas de aposta alta. Alto risco, alta recompensa.",
        tipo=TipoTerritorio.DINHEIRO_RAPIDO,
        npc_id="barao",
        posicao_mapa=(200, 150),  # Posição no mapa isométrico
        area_clicavel=(180, 130, 120, 80),  # Hitbox retangular
        desbloqueado=True,
        atividades=[
            {"tipo": "emprestimo", "nome": "Pegar Empréstimo", "risco": "alto"},
            {"tipo": "corrida_aposta", "nome": "Corrida de Aposta Alta", "risco": "alto", "recompensa": "alta"}
        ]
    ),
    
    "fabrica_boris": Territorio(
        id="fabrica_boris",
        nome="A Fábrica do Boris",
        descricao="Peças brutas e corridas de arrancada. Sorte e azar determinam o resultado.",
        tipo=TipoTerritorio.PECAS_BRUTAS,
        npc_id="boris",  # Assumindo que existe um NPC Boris
        posicao_mapa=(600, 200),
        area_clicavel=(580, 180, 140, 90),
        desbloqueado=True,
        atividades=[
            {"tipo": "loja_roleta", "nome": "Roleta de Preços", "risco": "medio"},
            {"tipo": "corrida_arrancada", "nome": "Corrida de Arrancada", "risco": "medio", "dano_carro": "alto"}
        ]
    ),
    
    "templo_akira": Territorio(
        id="templo_akira",
        nome="O Templo da Akira",
        descricao="Técnica e dirigibilidade. Pneus de drift e desafios de montanha.",
        tipo=TipoTerritorio.TECNICA,
        npc_id="akira",
        posicao_mapa=(400, 400),
        area_clicavel=(380, 380, 130, 100),
        desbloqueado=True,
        atividades=[
            {"tipo": "loja_pecas", "nome": "Comprar Pneus de Drift", "risco": "baixo"},
            {"tipo": "desafio_touge", "nome": "Desafio de Montanha (Touge)", "risco": "medio", "pontos_penalidade": "alto"}
        ]
    ),
    
    "bueiro_pixel": Territorio(
        id="bueiro_pixel",
        nome="O Bueiro do Pixel",
        descricao="Informações e desbloqueios. Descubra segredos e fraquezas.",
        tipo=TipoTerritorio.INFORMACAO,
        npc_id="pixel",  # Assumindo que existe um NPC Pixel
        posicao_mapa=(100, 500),
        area_clicavel=(80, 480, 110, 70),
        desbloqueado=True,
        atividades=[
            {"tipo": "informacao", "nome": "Revelar Próxima Corrida", "custo": "medio"},
            {"tipo": "desbloqueio", "nome": "Descobrir Fraqueza de Chefe", "custo": "alto"}
        ]
    ),
    
    "torre_rex": Territorio(
        id="torre_rex",
        nome="A Torre Neon do Rex",
        descricao="Corridas principais do ranking. Progressão na história.",
        tipo=TipoTerritorio.PROGRESSAO,
        npc_id="rex",
        posicao_mapa=(800, 300),
        area_clicavel=(780, 280, 150, 110),
        desbloqueado=False,  # Desbloqueado após primeira corrida
        atividades=[
            {"tipo": "corrida_ranking", "nome": "Corrida do Ranking", "dificuldade": "alta", "reputacao": "alta"}
        ]
    )
}

def obter_territorio(id: str) -> Optional[Territorio]:
    """Retorna um território pelo ID"""
    return TERRITORIOS.get(id)

def obter_territorios_desbloqueados() -> List[Territorio]:
    """Retorna lista de territórios desbloqueados"""
    return [t for t in TERRITORIOS.values() if t.desbloqueado]

def obter_territorio_por_npc(npc_id: str) -> Optional[Territorio]:
    """Retorna o território associado a um NPC"""
    for territorio in TERRITORIOS.values():
        if territorio.npc_id == npc_id:
            return territorio
    return None

