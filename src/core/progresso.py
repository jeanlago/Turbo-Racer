import json
import os
import time
from config import DIR_PROJETO

CAMINHO_PROGRESSO = os.path.join(DIR_PROJETO, "data", "progresso.json")

class GerenciadorProgresso:
    """Gerencia o progresso do jogador: dinheiro, carros desbloqueados, recordes e troféus"""
    
    def __init__(self):
        self.dinheiro = 0
        self.nome_jogador = "JOGADOR"
        self.carros_desbloqueados = set()
        self.recordes_corrida = {}
        self.recordes_drift = {}
        self.trofeus = {}
        self.upgrades = {}
        self.carro_p1_atual = None
        self.carro_p2_atual = None
        self.ultima_compra_alien = None
        self.dialogo_alien_ja_mostrado = False
        self.upgrades_visitados = set()
        
        self.akira_nome_revelado = False
        self.akira_dialogos_pre_corrida_mostrados = {}
        self.akira_primeira_aparicao_mostrada = False
        
        self.ranking_pilotos = []
        self.ranking_posicao_jogador = 10
        
        self.crank_humor_atual = 0
        self.crank_saude_carro = 1.0
        self.crank_tutorial_mostrado = False
        self.crank_tutorial_upgrades_mostrado = False
        self.crank_prefixo_cor_ultimo_carro = None
        self.crank_nome_revelado = False
        
        self.rex_primeira_aparicao_mostrada = False
        self.rex_nome_revelado = False
        
        self.glub_primeira_aparicao_feita = False
        self.glub_nome_revelado = False
        self.glub_ultima_aparicao_data = None  # Data (YYYY-MM-DD) em que o Glub apareceu pela última vez
        
        self.slick_ultima_aparicao_data = None  # Data (YYYY-MM-DD) em que o Slick apareceu pela última vez
        self.slick_primeira_aparicao_mostrada = False  # Flag para indicar se o Slick já apareceu no território após a cena narrativa
        
        self.mercador_ultima_aparicao = 0
        self.mercador_contador_eventos = 0
        self.mercador_nome_revelado = False
        
        self.barao_nome_revelado = False
        self.barao_emprestimo_ativo = False
        self.barao_valor_devido = 0
        self.barao_corridas_restantes = 0
        
        self.boris_nome_revelado = False
        self.boris_primeira_aparicao_mostrada = False
        
        self.pixel_nome_revelado = False
        self.pixel_primeira_aparicao_mostrada = False
        self.pixel_dialogo_explodiu_mostrado = False
        
        self.fuligem_nome_revelado = False
        self.fuligem_primeira_aparicao_mostrada = False
        self.fuligem_corridas_desbloqueadas = [0]  # Corrida 1 (índice 0) sempre desbloqueada
        
        self.capitulo_atual = None
        self.capitulos_completos = set()
        
        self.hierarquia_desbloqueada = False
        self.oficina_desbloqueada = False
        self.housingActive = False
        self.locations_unlocked_by_narrative = {}
        self.cinturaoUnlocked = False
        self.corridas_cinturao_completas = set()
        self.crownCircuitActive = False
        self.crown_stages_won = set()
        
        self.carro_campanha_estagio = 0
        self.carro_campanha_cor_final = None
        
        self.pixel_upgrade_nivel_6_desbloqueado = False
        self.pixel_cores_especiais_desbloqueadas = set()
        
        self.slick_upgrades_comprados = []
        
        self.glub_desbloqueado = False
        
        self.achievements_desbloqueados = set()
        self.achievements_visualizados = set()
        self.achievements_estatisticas = {
            "corridas_completas": 0,
            "voltas_drift": 0,
            "recordes_estabelecidos": 0,
            "carros_desbloqueados": 0,
            "corridas_sem_colisao": 0,
            "corridas_sem_erros": 0,
            "velocidade_maxima": 0.0,
            "upgrades_maximizados": 0
        }
        
        self.desafios_diarios = []
        self.desafios_semanais = []
        self.missoes_pista = {}
        self.desafios_progresso = {}
        self.desafios_completados = set()
        self.ultima_atualizacao_diaria = None
        self.ultima_atualizacao_semanal = None
        
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
        
        # Flag para rastrear última corrida da campanha
        self.ultima_corrida_campanha = None
        
        # Flag para iniciar capítulo 4 após narrativa pós-corrida da montanha
        self.iniciar_capitulo_4_apos_narrativa = False
        
        # Corridas desbloqueadas (race_id)
        self.corridas_desbloqueadas = set()
        
        self.carregar()
    
    def carregar(self):
        """Carrega o progresso do arquivo"""
        if os.path.exists(CAMINHO_PROGRESSO):
            try:
                with open(CAMINHO_PROGRESSO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dinheiro = data.get('dinheiro', 0)
                    self.nome_jogador = data.get('nome_jogador', 'JOGADOR')
                    self.carros_desbloqueados = set(data.get('carros_desbloqueados', ['Car1']))
                    if 'Car1' not in self.carros_desbloqueados:
                        self.carros_desbloqueados.add('Car1')
                    if 'recordes' in data and 'recordes_corrida' not in data:
                        self.recordes_corrida = data.get('recordes', {})
                    else:
                        self.recordes_corrida = data.get('recordes_corrida', {})
                    self.recordes_drift = data.get('recordes_drift', {})
                    self.trofeus = data.get('trofeus', {})
                    self.upgrades = data.get('upgrades', {})
                    self.carro_p1_atual = data.get('carro_p1_atual', None)
                    self.carro_p2_atual = data.get('carro_p2_atual', None)
                    self.ultima_compra_alien = data.get('ultima_compra_alien', None)
                    self.dialogo_alien_ja_mostrado = data.get('dialogo_alien_ja_mostrado', False)
                    self.upgrades_visitados = set(data.get('upgrades_visitados', []))
                    
                    self.akira_nome_revelado = data.get('akira_nome_revelado', False)
                    self.akira_dialogos_pre_corrida_mostrados = data.get('akira_dialogos_pre_corrida_mostrados', {})
                    self.akira_primeira_aparicao_mostrada = data.get('akira_primeira_aparicao_mostrada', False)
                    
                    self.ranking_pilotos = data.get('ranking_pilotos', [])
                    self.ranking_posicao_jogador = data.get('ranking_posicao_jogador', 10)
                    
                    self.crank_humor_atual = data.get('crank_humor_atual', 0)
                    self.crank_saude_carro = data.get('crank_saude_carro', 1.0)
                    self.crank_tutorial_mostrado = data.get('crank_tutorial_mostrado', False)
                    self.crank_tutorial_upgrades_mostrado = data.get('crank_tutorial_upgrades_mostrado', False)
                    self.crank_prefixo_cor_ultimo_carro = data.get('crank_prefixo_cor_ultimo_carro', None)
                    self.crank_nome_revelado = data.get('crank_nome_revelado', False)
                    
                    self.rex_primeira_aparicao_mostrada = data.get('rex_primeira_aparicao_mostrada', False)
                    self.rex_nome_revelado = data.get('rex_nome_revelado', False)
                    
                    self.glub_primeira_aparicao_feita = data.get('glub_primeira_aparicao_feita', False)
                    self.glub_nome_revelado = data.get('glub_nome_revelado', False)
                    glub_ultima_aparicao_dia_antigo = data.get('glub_ultima_aparicao_dia', 0)
                    slick_ultima_aparicao_dia_antigo = data.get('slick_ultima_aparicao_dia', 0)
                    
                    if 'glub_ultima_aparicao_data' in data:
                        self.glub_ultima_aparicao_data = data.get('glub_ultima_aparicao_data')
                    elif glub_ultima_aparicao_dia_antigo > 0:
                        from datetime import date, timedelta
                        data_base = date(1990, 12, 5)
                        self.glub_ultima_aparicao_data = (data_base + timedelta(days=glub_ultima_aparicao_dia_antigo - 1)).strftime("%Y-%m-%d")
                    else:
                        self.glub_ultima_aparicao_data = None
                    
                    if 'slick_ultima_aparicao_data' in data:
                        self.slick_ultima_aparicao_data = data.get('slick_ultima_aparicao_data')
                    elif slick_ultima_aparicao_dia_antigo > 0:
                        from datetime import date, timedelta
                        data_base = date(1990, 12, 5)
                        self.slick_ultima_aparicao_data = (data_base + timedelta(days=slick_ultima_aparicao_dia_antigo - 1)).strftime("%Y-%m-%d")
                    else:
                        self.slick_ultima_aparicao_data = None
                    
                    self.slick_primeira_aparicao_mostrada = data.get('slick_primeira_aparicao_mostrada', False)
                    
                    self.mercador_ultima_aparicao = data.get('mercador_ultima_aparicao', 0)
                    self.mercador_contador_eventos = data.get('mercador_contador_eventos', 0)
                    self.mercador_nome_revelado = data.get('mercador_nome_revelado', False)
                    
                    self.barao_nome_revelado = data.get('barao_nome_revelado', False)
                    self.barao_emprestimo_ativo = data.get('barao_emprestimo_ativo', False)
                    self.barao_valor_devido = data.get('barao_valor_devido', 0)
                    self.barao_corridas_restantes = data.get('barao_corridas_restantes', 0)
                    
                    self.boris_nome_revelado = data.get('boris_nome_revelado', False)
                    self.boris_primeira_aparicao_mostrada = data.get('boris_primeira_aparicao_mostrada', False)
                    
                    self.pixel_nome_revelado = data.get('pixel_nome_revelado', False)
                    self.pixel_primeira_aparicao_mostrada = data.get('pixel_primeira_aparicao_mostrada', False)
                    self.pixel_dialogo_explodiu_mostrado = data.get('pixel_dialogo_explodiu_mostrado', False)
                    
                    self.fuligem_nome_revelado = data.get('fuligem_nome_revelado', False)
                    self.fuligem_primeira_aparicao_mostrada = data.get('fuligem_primeira_aparicao_mostrada', False)
                    self.fuligem_corridas_desbloqueadas = data.get('fuligem_corridas_desbloqueadas', [0])
                    
                    self.capitulo_atual = data.get('capitulo_atual', None)
                    self.capitulos_completos = set(data.get('capitulos_completos', []))
                    
                    self.hierarquia_desbloqueada = data.get('hierarquia_desbloqueada', False)
                    self.oficina_desbloqueada = data.get('oficina_desbloqueada', False)
                    self.housingActive = data.get('housingActive', False)
                    self.locations_unlocked_by_narrative = data.get('locations_unlocked_by_narrative', {})
                    self.cinturaoUnlocked = data.get('cinturaoUnlocked', False)
                    corridas_cinturao_data = data.get('corridas_cinturao_completas', [])
                    self.corridas_cinturao_completas = set(corridas_cinturao_data) if isinstance(corridas_cinturao_data, list) else set()
                    crown_stages_won_data = data.get('crown_stages_won', [])
                    self.crown_stages_won = set(crown_stages_won_data) if isinstance(crown_stages_won_data, list) else set()
                    
                    self.achievements_desbloqueados = set(data.get('achievements_desbloqueados', []))
                    self.achievements_visualizados = set(data.get('achievements_visualizados', []))
                    self.achievements_estatisticas = data.get('achievements_estatisticas', {
                        "corridas_completas": 0,
                        "voltas_drift": 0,
                        "recordes_estabelecidos": 0,
                        "carros_desbloqueados": 0,
                        "corridas_sem_colisao": 0,
                        "corridas_sem_erros": 0,
                        "velocidade_maxima": 0.0,
                        "upgrades_maximizados": 0
                    })
                    
                    self.desafios_diarios = data.get('desafios_diarios', [])
                    self.desafios_semanais = data.get('desafios_semanais', [])
                    self.missoes_pista = data.get('missoes_pista', {})
                    self.desafios_progresso = data.get('desafios_progresso', {})
                    self.desafios_completados = set(data.get('desafios_completados', []))
                    self.ultima_atualizacao_diaria = data.get('ultima_atualizacao_diaria', None)
                    self.ultima_atualizacao_semanal = data.get('ultima_atualizacao_semanal', None)
                    
                    self.estatisticas_gerais = data.get('estatisticas_gerais', {
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
                    })
                    self.estatisticas_por_pista = data.get('estatisticas_por_pista', {})
                    
                    self.ultima_corrida_campanha = data.get('ultima_corrida_campanha', None)
                    self.iniciar_capitulo_4_apos_narrativa = data.get('iniciar_capitulo_4_apos_narrativa', False)
                    corridas_desbloqueadas_data = data.get('corridas_desbloqueadas', [])
                    self.corridas_desbloqueadas = set(corridas_desbloqueadas_data) if isinstance(corridas_desbloqueadas_data, list) else set()
                    
                    self.pixel_upgrade_nivel_6_desbloqueado = data.get('pixel_upgrade_nivel_6_desbloqueado', False)
                    self.pixel_cores_especiais_desbloqueadas = set(data.get('pixel_cores_especiais_desbloqueadas', []))
                    
                    self.slick_upgrades_comprados = data.get('slick_upgrades_comprados', [])
                    
                    self.carro_campanha_estagio = data.get('carro_campanha_estagio', 0)
                    self.carro_campanha_cor_final = data.get('carro_campanha_cor_final', None)
                    
                    self.crownCircuitActive = data.get('crownCircuitActive', False)
                    
                    self._carregar_dados_outros_sistemas(data)
                    
                    self._migrar_dados_antigos()
                    
                    if not isinstance(self.upgrades, dict):
                        self.upgrades = {}
                    
                    try:
                        self._migrar_upgrades_antigos()
                    except Exception as e:
                        print(f"Erro ao migrar upgrades antigos: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    if self.recordes_corrida:
                        try:
                            self.recordes_corrida = {str(k): v for k, v in self.recordes_corrida.items()}
                        except Exception as e:
                            print(f"Erro ao converter chaves de recordes_corrida: {e}")
                            self.recordes_corrida = {}
                    if self.recordes_drift:
                        try:
                            self.recordes_drift = {str(k): v for k, v in self.recordes_drift.items()}
                        except Exception as e:
                            print(f"Erro ao converter chaves de recordes_drift: {e}")
                            self.recordes_drift = {}
                    if self.trofeus:
                        try:
                            self.trofeus = {str(k): v for k, v in self.trofeus.items()}
                        except Exception as e:
                            print(f"Erro ao converter chaves de trofeus: {e}")
                            self.trofeus = {}
                    # Garantir que upgrades também tenha chaves válidas
                    if self.upgrades:
                        try:
                            upgrades_limpos = {}
                            for prefixo_cor, upgrades_carro in self.upgrades.items():
                                if isinstance(upgrades_carro, dict):
                                    upgrades_limpos[str(prefixo_cor)] = upgrades_carro
                                else:
                                    upgrades_limpos[str(prefixo_cor)] = {}
                            self.upgrades = upgrades_limpos
                        except Exception as e:
                            print(f"Erro ao limpar upgrades: {e}")
                            import traceback
                            traceback.print_exc()
                            self.upgrades = {}
            except Exception as e:
                print(f"Erro ao carregar progresso: {e}")
                import traceback
                traceback.print_exc()
                self.dinheiro = 0
                self.carros_desbloqueados = {'Car1'}
                self.recordes_corrida = {}
                self.recordes_drift = {}
                self.trofeus = {}
                self.upgrades = {}
                self.carro_p1_atual = None
                self.carro_p2_atual = None
        else:
            self.dinheiro = 5000
            self.carros_desbloqueados = {'Car1'}
            self.crank_humor_atual = 0
            self.crank_saude_carro = 1.0
            self.crank_tutorial_mostrado = False
            self.crank_tutorial_upgrades_mostrado = False
            self.crank_prefixo_cor_ultimo_carro = None
            self.crank_nome_revelado = False
            
            self.salvar()
    
    def salvar(self):
        """Salva o progresso no arquivo (incluindo todos os dados do jogo)"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_PROGRESSO), exist_ok=True)
            
            from core.missoes import gerenciador_missoes
            from core.mapa_locations import gerenciador_localizacoes
            from core.tempo_jogo import gerenciador_tempo
            from core.status_jogador import status_jogador
            from core.ghost import gerenciador_ghosts
            from core.narrative_system import narrative_system
            
            data = {
                'dinheiro': self.dinheiro,
                'nome_jogador': self.nome_jogador,
                'carros_desbloqueados': list(self.carros_desbloqueados),
                'recordes_corrida': self.recordes_corrida,
                'recordes_drift': self.recordes_drift,
                'trofeus': self.trofeus,
                'upgrades': self.upgrades,
                'carro_p1_atual': self.carro_p1_atual,
                'carro_p2_atual': self.carro_p2_atual,
                'ultima_compra_alien': self.ultima_compra_alien,
                'dialogo_alien_ja_mostrado': self.dialogo_alien_ja_mostrado,
                'upgrades_visitados': list(self.upgrades_visitados),
                
                # Dados de missões
                'missoes_completas': list(gerenciador_missoes.missoes_completas),
                'missao_ativa_id': gerenciador_missoes.missao_ativa_id,
                
                # Dados de localizações
                'mapa_locations': {
                    loc_id: {
                        "nome": loc_data["nome"],
                        "state": loc_data["state"],
                        "lockedThought": loc_data.get("lockedThought"),
                        "unlockFlags": loc_data.get("unlockFlags", [])
                    }
                    for loc_id, loc_data in gerenciador_localizacoes.locations.items()
                },
                
                # Dados de tempo
                'tempo_jogo': {
                    'hora_jogo': gerenciador_tempo.hora_jogo,
                    'dia_jogo': gerenciador_tempo.dia_jogo,
                    'ultima_atualizacao_timestamp': gerenciador_tempo.ultima_atualizacao_timestamp,
                    'data_inicial': gerenciador_tempo.data_inicial.strftime("%Y-%m-%d") if hasattr(gerenciador_tempo, 'data_inicial') else None
                },
                
                # Dados de status do jogador
                'status_jogador': {
                    'popularidade': status_jogador.popularidade,
                    'fome': status_jogador.fome,
                    'sono': status_jogador.sono,
                    'tedio': status_jogador.tedio
                },
                
                # Dados de ghosts
                'ghosts': gerenciador_ghosts.ghosts,
                
                # Dados do sistema narrativo
                'narrative_system': {
                    'current_chapter_id': narrative_system.current_chapter_id,
                    'current_scene_id': narrative_system.current_scene_id,
                    'scenes_visited': list(narrative_system.scenes_visited),
                    'flags': narrative_system.flags,
                    'variables': narrative_system.variables,
                    'chapter_start_time': narrative_system.chapter_start_time
                },
                
                'akira_nome_revelado': self.akira_nome_revelado,
                'akira_dialogos_pre_corrida_mostrados': self.akira_dialogos_pre_corrida_mostrados,
                'akira_primeira_aparicao_mostrada': self.akira_primeira_aparicao_mostrada,
                
                'ranking_pilotos': self.ranking_pilotos,
                'ranking_posicao_jogador': self.ranking_posicao_jogador,
                
                'crank_humor_atual': self.crank_humor_atual,
                'crank_saude_carro': self.crank_saude_carro,
                'crank_tutorial_mostrado': self.crank_tutorial_mostrado,
                'crank_tutorial_upgrades_mostrado': self.crank_tutorial_upgrades_mostrado,
                'crank_prefixo_cor_ultimo_carro': self.crank_prefixo_cor_ultimo_carro,
                'crank_nome_revelado': self.crank_nome_revelado,
                
                'rex_primeira_aparicao_mostrada': self.rex_primeira_aparicao_mostrada,
                'rex_nome_revelado': self.rex_nome_revelado,
                
                'glub_primeira_aparicao_feita': self.glub_primeira_aparicao_feita,
                'glub_nome_revelado': self.glub_nome_revelado,
                'glub_ultima_aparicao_data': getattr(self, 'glub_ultima_aparicao_data', None),
                
                'slick_ultima_aparicao_data': getattr(self, 'slick_ultima_aparicao_data', None),
                'slick_primeira_aparicao_mostrada': getattr(self, 'slick_primeira_aparicao_mostrada', False),
                
                'mercador_ultima_aparicao': self.mercador_ultima_aparicao,
                'mercador_contador_eventos': self.mercador_contador_eventos,
                'mercador_nome_revelado': self.mercador_nome_revelado,
                
                'barao_nome_revelado': self.barao_nome_revelado,
                'barao_emprestimo_ativo': self.barao_emprestimo_ativo,
                'barao_valor_devido': self.barao_valor_devido,
                'barao_corridas_restantes': self.barao_corridas_restantes,
                
                'boris_nome_revelado': self.boris_nome_revelado,
                'boris_primeira_aparicao_mostrada': self.boris_primeira_aparicao_mostrada,
                
                'pixel_nome_revelado': self.pixel_nome_revelado,
                'pixel_primeira_aparicao_mostrada': self.pixel_primeira_aparicao_mostrada,
                'pixel_dialogo_explodiu_mostrado': self.pixel_dialogo_explodiu_mostrado,
                
                'fuligem_nome_revelado': self.fuligem_nome_revelado,
                'fuligem_primeira_aparicao_mostrada': self.fuligem_primeira_aparicao_mostrada,
                'fuligem_corridas_desbloqueadas': self.fuligem_corridas_desbloqueadas,
                
                'capitulo_atual': self.capitulo_atual,
                'capitulos_completos': list(self.capitulos_completos),
                
                'hierarquia_desbloqueada': self.hierarquia_desbloqueada,
                'oficina_desbloqueada': self.oficina_desbloqueada,
                'housingActive': self.housingActive,
                'locations_unlocked_by_narrative': self.locations_unlocked_by_narrative,
                'cinturaoUnlocked': self.cinturaoUnlocked,
                'corridas_cinturao_completas': list(self.corridas_cinturao_completas) if isinstance(self.corridas_cinturao_completas, set) else self.corridas_cinturao_completas,
                'crown_stages_won': list(self.crown_stages_won) if isinstance(self.crown_stages_won, set) else self.crown_stages_won,
                
                'achievements_desbloqueados': list(self.achievements_desbloqueados),
                'achievements_visualizados': list(self.achievements_visualizados),
                'achievements_estatisticas': self.achievements_estatisticas,
                
                'desafios_diarios': self.desafios_diarios,
                'desafios_semanais': self.desafios_semanais,
                'missoes_pista': self.missoes_pista,
                'desafios_progresso': self.desafios_progresso,
                'desafios_completados': list(self.desafios_completados),
                'ultima_atualizacao_diaria': self.ultima_atualizacao_diaria,
                'ultima_atualizacao_semanal': self.ultima_atualizacao_semanal,
                
                'estatisticas_gerais': self.estatisticas_gerais,
                'estatisticas_por_pista': self.estatisticas_por_pista,
                
                'ultima_corrida_campanha': self.ultima_corrida_campanha,
                'iniciar_capitulo_4_apos_narrativa': self.iniciar_capitulo_4_apos_narrativa,
                'corridas_desbloqueadas': list(self.corridas_desbloqueadas) if isinstance(self.corridas_desbloqueadas, set) else self.corridas_desbloqueadas,
                
                'pixel_upgrade_nivel_6_desbloqueado': getattr(self, 'pixel_upgrade_nivel_6_desbloqueado', False),
                'pixel_cores_especiais_desbloqueadas': list(getattr(self, 'pixel_cores_especiais_desbloqueadas', set())),
                'slick_upgrades_comprados': getattr(self, 'slick_upgrades_comprados', []),
                
                'carro_campanha_estagio': getattr(self, 'carro_campanha_estagio', 0),
                'carro_campanha_cor_final': getattr(self, 'carro_campanha_cor_final', None),
                
                'crownCircuitActive': getattr(self, 'crownCircuitActive', False)
            }
            
            with open(CAMINHO_PROGRESSO, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self._restaurar_dados_outros_sistemas()
        except Exception as e:
            print(f"Erro ao salvar progresso: {e}")
            import traceback
            traceback.print_exc()
    
    def definir_carro_atual(self, carro_p1=None, carro_p2=None):
        """Define o carro atual dos jogadores"""
        if carro_p1 is not None:
            self.carro_p1_atual = carro_p1
        if carro_p2 is not None:
            self.carro_p2_atual = carro_p2
        self.salvar()
    
    def obter_carro_atual(self, jogador=1):
        """Obtém o carro atual do jogador"""
        if jogador == 1:
            return self.carro_p1_atual
        else:
            return self.carro_p2_atual
    
    def obter_recorde(self, numero_pista):
        """Obtém o recorde de corrida de uma pista"""
        return self.recordes_corrida.get(str(numero_pista), None)
    
    def registrar_recorde(self, numero_pista, tempo):
        """Registra um novo recorde de corrida se o tempo for melhor
        
        Args:
            numero_pista: Número da pista
            tempo: Tempo da corrida em segundos
            
        Returns:
            True se foi um novo recorde, False caso contrário
        """
        chave = str(numero_pista)
        recorde_atual = self.recordes_corrida.get(chave, None)
        
        if recorde_atual is None or tempo < recorde_atual:
            self.recordes_corrida[chave] = tempo
            from core.estatisticas import gerenciador_estatisticas
            stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(numero_pista)
            if stats_pista.get("melhor_tempo") is None or tempo < stats_pista.get("melhor_tempo", float('inf')):
                stats_pista["melhor_tempo"] = tempo
            self.salvar()
            return True
        return False
    
    def obter_recorde_drift(self, numero_pista):
        """Obtém o recorde de drift de uma pista"""
        return self.recordes_drift.get(str(numero_pista), None)
    
    def obter_trofeu(self, numero_pista):
        """Obtém o troféu de uma pista"""
        return self.trofeus.get(str(numero_pista), None)
    
    def registrar_trofeu(self, numero_pista, tipo_trofeu):
        """Registra um troféu para uma pista
        
        Args:
            numero_pista: Número da pista
            tipo_trofeu: Tipo do troféu ("ouro", "prata", "bronze")
        """
        chave = str(numero_pista)
        trofeu_atual = self.trofeus.get(chave, None)
        
        prioridade = {"ouro": 3, "prata": 2, "bronze": 1}
        prioridade_atual = prioridade.get(trofeu_atual, 0) if trofeu_atual else 0
        prioridade_nova = prioridade.get(tipo_trofeu, 0)
        
        if prioridade_nova > prioridade_atual:
            self.trofeus[chave] = tipo_trofeu
            self.salvar()
            return True
        return False
    
    def obter_upgrade(self, prefixo_cor, tipo_upgrade):
        """Obtém o nível de um upgrade de um carro"""
        if prefixo_cor not in self.upgrades:
            return 0
        return self.upgrades[prefixo_cor].get(tipo_upgrade, 0)
    
    def obter_todos_upgrades(self, prefixo_cor):
        """Obtém todos os upgrades de um carro"""
        return self.upgrades.get(prefixo_cor, {})
    
    def tem_dinheiro(self, valor):
        """Verifica se o jogador tem dinheiro suficiente"""
        return self.dinheiro >= valor
    
    def adicionar_dinheiro(self, valor):
        """Adiciona dinheiro ao jogador"""
        self.dinheiro += valor
        self.salvar()
    
    def remover_dinheiro(self, valor):
        """Remove dinheiro do jogador"""
        self.dinheiro = max(0, self.dinheiro - valor)
        self.salvar()
    
    def esta_desbloqueado(self, prefixo_cor):
        """Verifica se um carro está desbloqueado"""
        return prefixo_cor in self.carros_desbloqueados
    
    def comprar_carro(self, prefixo_cor, preco):
        """Compra um carro"""
        if self.tem_dinheiro(preco) and not self.esta_desbloqueado(prefixo_cor):
            self.remover_dinheiro(preco)
            self.carros_desbloqueados.add(prefixo_cor)
            self.salvar()
            return True
        return False
    
    def vender_carro(self, prefixo_cor, preco_venda):
        """Vende um carro"""
        if self.esta_desbloqueado(prefixo_cor) and prefixo_cor != "Car1":
            self.carros_desbloqueados.remove(prefixo_cor)
            self.adicionar_dinheiro(preco_venda)
            if prefixo_cor in self.upgrades:
                del self.upgrades[prefixo_cor]
            if self.carro_p1_atual == prefixo_cor:
                self.carro_p1_atual = None
            if self.carro_p2_atual == prefixo_cor:
                self.carro_p2_atual = None
            self.salvar()
            return True
        return False
    
    def contar_carros_desbloqueados(self):
        """Conta quantos carros estão desbloqueados"""
        return len(self.carros_desbloqueados)
    
    def calcular_preco_upgrade(self, tipo_upgrade, nivel_atual):
        """Calcula o preço de um upgrade baseado no tipo e nível atual"""
        precos_base = {
            'motor': 500,
            'filtro_ar': 400,
            'ecu': 600,
            'transmissao': 450,
            'rodas': 350,
            'suspensao': 400,
            'nitro': 800
        }
        preco_base = precos_base.get(tipo_upgrade, 500)
        return int(preco_base * (1.5 ** nivel_atual))
    
    def comprar_upgrade(self, prefixo_cor, tipo_upgrade, preco):
        """Compra um upgrade para um carro"""
        if prefixo_cor not in self.upgrades:
            self.upgrades[prefixo_cor] = {}
        
        nivel_atual = self.obter_upgrade(prefixo_cor, tipo_upgrade)
        nivel_maximo = 6 if getattr(self, 'pixel_upgrade_nivel_6_desbloqueado', False) else 5
        if nivel_atual < nivel_maximo:
            if self.tem_dinheiro(preco):
                self.remover_dinheiro(preco)
                self.upgrades[prefixo_cor][tipo_upgrade] = nivel_atual + 1
                self.salvar()
                return True
        return False
    
    def obter_nivel_maximo_upgrade(self):
        """Retorna o nível máximo de upgrades disponível (5 ou 6 se Pixel desbloqueou)"""
        return 6 if getattr(self, 'pixel_upgrade_nivel_6_desbloqueado', False) else 5
    
    def marcar_upgrades_visitado(self, prefixo_cor):
        """Marca que um carro visitou a tela de upgrades"""
        self.upgrades_visitados.add(prefixo_cor)
        self.salvar()
    
    def upgrades_ja_visitado(self, prefixo_cor):
        """Verifica se um carro já visitou a tela de upgrades"""
        return prefixo_cor in self.upgrades_visitados
    
    def registrar_compra_alien(self, tipo, quantidade=1, tipo_upgrade=None):
        """Registra uma compra do mercador alien para diálogos raros do Crank"""
        self.ultima_compra_alien = {
            'tipo': tipo,
            'quantidade': quantidade,
            'tipo_upgrade': tipo_upgrade
        }
        self.dialogo_alien_ja_mostrado = False
        self.salvar()
    
    def obter_ultima_compra_alien(self):
        """Obtém a última compra do mercador alien"""
        return self.ultima_compra_alien
    
    def limpar_ultima_compra_alien(self):
        """Limpa o registro da última compra do mercador alien"""
        self.ultima_compra_alien = None
        self.salvar()
    
    def obter_capitulo_atual(self):
        """Obtém o ID do capítulo atual da campanha"""
        return self.capitulo_atual
    
    def definir_capitulo_atual(self, chapter_id):
        """Define o ID do capítulo atual da campanha"""
        self.capitulo_atual = chapter_id
        self.salvar()
    
    def marcar_capitulo_completo(self, chapter_id):
        """Marca um capítulo como completo"""
        self.capitulos_completos.add(chapter_id)
        self.salvar()
    
    def capitulo_foi_completo(self, chapter_id):
        """Verifica se um capítulo foi completado"""
        return chapter_id in self.capitulos_completos
    
    def _carregar_dados_outros_sistemas(self, data: dict):
        """Carrega dados de outros sistemas do progresso.json e restaura nos sistemas"""
        try:
            # Carregar dados de missões
            if 'missoes_completas' in data or 'missao_ativa_id' in data:
                from core.missoes import gerenciador_missoes
                gerenciador_missoes.missoes_completas = set(data.get('missoes_completas', []))
                gerenciador_missoes.missao_ativa_id = data.get('missao_ativa_id', None)
            
            # Carregar dados de localizações
            if 'mapa_locations' in data:
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_localizacoes.locations = data.get('mapa_locations', {})
            
            # Carregar dados de tempo
            if 'tempo_jogo' in data:
                from core.tempo_jogo import gerenciador_tempo
                tempo_data = data.get('tempo_jogo', {})
                gerenciador_tempo.hora_jogo = tempo_data.get('hora_jogo', 12)
                gerenciador_tempo.ultima_atualizacao_timestamp = tempo_data.get('ultima_atualizacao_timestamp', time.time())
            
            # Carregar dados de status do jogador
            if 'status_jogador' in data:
                from core.status_jogador import status_jogador
                status_data = data.get('status_jogador', {})
                status_jogador.popularidade = status_data.get('popularidade', 0)
                status_jogador.fome = status_data.get('fome', 100)
                status_jogador.sono = status_data.get('sono', 100)
                status_jogador.tedio = status_data.get('tedio', 0)
            
            # Carregar dados de ghosts
            if 'ghosts' in data:
                from core.ghost import gerenciador_ghosts
                gerenciador_ghosts.ghosts = data.get('ghosts', {})
            
            # Carregar dados do sistema narrativo
            if 'narrative_system' in data:
                from core.narrative_system import narrative_system
                narrative_data = data.get('narrative_system', {})
                narrative_system.current_chapter_id = narrative_data.get('current_chapter_id', None)
                narrative_system.current_scene_id = narrative_data.get('current_scene_id', None)
                narrative_system.scenes_visited = set(narrative_data.get('scenes_visited', []))
                narrative_system.flags = narrative_data.get('flags', {})
                narrative_system.variables = narrative_data.get('variables', {})
                narrative_system.chapter_start_time = narrative_data.get('chapter_start_time', {})
                
                # Validar se o capítulo atual está correto baseado no progresso real
                from core.missoes import gerenciador_missoes
                gerenciador_missoes.carregar()
                
                # Determinar qual capítulo o jogador deveria estar baseado nas missões completas
                missoes_ch1 = ["m1_primeira_faisca", "m2_teste_de_sobrevivencia", "m3_rota_da_ferrugem", 
                               "m4_coracao_de_sucata", "m5_cirurgia_na_garagem", "m6_batismo_de_pista", "m7_olhos_no_painel"]
                missoes_ch2 = ["m8_oferta_envenenada", "m9a_peso_da_divida", "m10_portoes_do_cinturao", "m10b_corridas_cinturao"]
                missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo", "m14_tres_mundos"]
                
                ch1_completas = sum(1 for m in missoes_ch1 if m in gerenciador_missoes.missoes_completas)
                ch2_completas = sum(1 for m in missoes_ch2 if m in gerenciador_missoes.missoes_completas)
                ch3_completas = sum(1 for m in missoes_ch3 if m in gerenciador_missoes.missoes_completas)
                
                # Determinar capítulo esperado baseado no progresso
                if ch1_completas < len(missoes_ch1):
                    capitulo_esperado = "ch1"
                elif ch2_completas < len(missoes_ch2):
                    capitulo_esperado = "ch2"
                elif ch3_completas < len(missoes_ch3):
                    capitulo_esperado = "ch3"
                else:
                    capitulo_esperado = "ch4"
                
                # Se o capítulo atual está muito mais avançado que o esperado, corrigir
                if narrative_system.current_chapter_id:
                    capitulo_atual_num = int(narrative_system.current_chapter_id.replace("ch", "")) if narrative_system.current_chapter_id.startswith("ch") else 0
                    capitulo_esperado_num = int(capitulo_esperado.replace("ch", "")) if capitulo_esperado.startswith("ch") else 0
                    
                    if capitulo_atual_num > capitulo_esperado_num + 1:
                        print(f"[PROGRESSO] Capítulo atual ({narrative_system.current_chapter_id}) está muito mais avançado que o esperado ({capitulo_esperado}) baseado no progresso. Corrigindo...")
                        narrative_system.current_chapter_id = capitulo_esperado
                        narrative_system.current_scene_id = None
                        narrative_system.active = False
                        self.capitulo_atual = capitulo_esperado
                        print(f"[PROGRESSO] Capítulo corrigido para {capitulo_esperado} baseado no progresso real")
                
                # Verificar se a cena salva já foi visitada - se sim, limpar para evitar continuar de uma cena já completada
                # EXCEÇÃO: Se ch5_9_rex_final_words foi visitada, avançar automaticamente para ch5_10_creditos
                if "ch5_9_rex_final_words" in narrative_system.scenes_visited and "ch5_10_creditos" not in narrative_system.scenes_visited:
                    print(f"[PROGRESSO] ch5_9_rex_final_words foi visitada mas ch5_10_creditos não. Iniciando créditos...")
                    narrative_system.current_chapter_id = "ch5"
                    narrative_system.current_scene_id = "ch5_10_creditos"
                    narrative_system.current_line_index = 0
                    narrative_system.active = True
                    # Remover ch5_10_creditos da lista de visitadas se estiver lá (para permitir reativação)
                    narrative_system.scenes_visited.discard("ch5_10_creditos")
                    print(f"[PROGRESSO] Créditos iniciados automaticamente após carregar save")
                elif narrative_system.current_scene_id and narrative_system.current_scene_id in narrative_system.scenes_visited:
                    print(f"[PROGRESSO] Cena salva {narrative_system.current_scene_id} já foi visitada. Limpando current_scene_id para evitar continuar de cena já completada.")
                    narrative_system.current_scene_id = None
                    narrative_system.active = False
                    # Salvar o progresso após limpar a cena
                    try:
                        self.salvar()
                    except Exception as e:
                        print(f"[PROGRESSO] Erro ao salvar após limpar cena visitada: {e}")
        except Exception as e:
            print(f"[PROGRESSO] Erro ao carregar dados de outros sistemas: {e}")
            import traceback
            traceback.print_exc()
    
    def _restaurar_dados_outros_sistemas(self):
        """Restaura dados nos outros sistemas após salvar no progresso.json"""
        try:
            pass
        except Exception as e:
            print(f"[PROGRESSO] Erro ao restaurar dados de outros sistemas: {e}")
    
    def _migrar_dados_antigos(self):
        """Migra dados de arquivos antigos para o progresso.json"""
        pass
    
    def _migrar_upgrades_antigos(self):
        """Migra upgrades de formato antigo para novo"""
        pass

gerenciador_progresso = GerenciadorProgresso()
