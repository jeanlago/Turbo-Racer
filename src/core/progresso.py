# src/core/progresso.py
import json
import os
from config import DIR_PROJETO

CAMINHO_PROGRESSO = os.path.join(DIR_PROJETO, "data", "progresso.json")

class GerenciadorProgresso:
    """Gerencia o progresso do jogador: dinheiro, carros desbloqueados, recordes e troféus"""
    
    def __init__(self):
        self.dinheiro = 0
        self.nome_jogador = "JOGADOR"  # Nome do jogador (será definido na primeira aparição de NPC)
        self.carros_desbloqueados = set()
        self.recordes_corrida = {}
        self.recordes_drift = {}
        self.trofeus = {}
        self.upgrades = {}
        self.carro_p1_atual = None
        self.carro_p2_atual = None
        # Rastreamento de compras do mercador alien para diálogos raros do Crank
        self.ultima_compra_alien = None  # {'tipo': 'golpe'|'upgrade_especial'|'multi_upgrade', 'quantidade': int, 'tipo_upgrade': str}
        self.dialogo_alien_ja_mostrado = False  # Flag para rastrear se o diálogo sobre a última compra já foi mostrado
        # Rastreamento de carros que já visitaram a tela de upgrades (para esconder exclamação)
        self.upgrades_visitados = set()  # Set de prefixo_cor que já visitaram upgrades
        
        # Dados dos NPCs (consolidados no progresso.json)
        # Akira
        self.akira_nome_revelado = False
        self.akira_dialogos_pre_corrida_mostrados = {}  # {pista: True/False}
        
        # Ranking
        self.ranking_pilotos = []  # Lista de {nome, posicao, vitorias, derrotas, e_jogador}
        self.ranking_posicao_jogador = 10
        
        # Crank
        self.crank_humor_atual = 0  # -2 a 2
        self.crank_saude_carro = 1.0  # 0.0 a 1.0
        self.crank_tutorial_mostrado = False
        self.crank_tutorial_upgrades_mostrado = False
        self.crank_prefixo_cor_ultimo_carro = None
        self.crank_nome_revelado = False
        
        # Rex
        self.rex_primeira_aparicao_mostrada = False
        self.rex_nome_revelado = False
        
        # Glub
        self.glub_primeira_aparicao_feita = False
        self.glub_nome_revelado = False
        
        # MercadorAlien
        self.mercador_ultima_aparicao = 0
        self.mercador_contador_eventos = 0
        self.mercador_nome_revelado = False
        
        # Barão (Agiota)
        self.barao_nome_revelado = False
        self.barao_emprestimo_ativo = False
        self.barao_valor_devido = 0
        self.barao_corridas_restantes = 0
        
        # Achievements
        self.achievements_desbloqueados = set()  # Set de IDs de achievements desbloqueados
        self.achievements_visualizados = set()  # Set de IDs de achievements já visualizados
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
        
        # Desafios
        self.desafios_diarios = []
        self.desafios_semanais = []
        self.missoes_pista = {}  # {numero_pista: [missoes]}
        self.desafios_progresso = {}  # {desafio_id: progresso_atual}
        self.desafios_completados = set()  # IDs de desafios completados
        self.ultima_atualizacao_diaria = None
        self.ultima_atualizacao_semanal = None
        
        # Estatísticas
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
        self.estatisticas_por_pista = {}  # {numero_pista: {estatisticas}}
        
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
                    
                    # Dados dos NPCs
                    # Akira
                    self.akira_nome_revelado = data.get('akira_nome_revelado', False)
                    self.akira_dialogos_pre_corrida_mostrados = data.get('akira_dialogos_pre_corrida_mostrados', {})
                    
                    # Ranking
                    self.ranking_pilotos = data.get('ranking_pilotos', [])
                    self.ranking_posicao_jogador = data.get('ranking_posicao_jogador', 10)
                    
                    # Crank
                    self.crank_humor_atual = data.get('crank_humor_atual', 0)
                    self.crank_saude_carro = data.get('crank_saude_carro', 1.0)
                    self.crank_tutorial_mostrado = data.get('crank_tutorial_mostrado', False)
                    self.crank_tutorial_upgrades_mostrado = data.get('crank_tutorial_upgrades_mostrado', False)
                    self.crank_prefixo_cor_ultimo_carro = data.get('crank_prefixo_cor_ultimo_carro', None)
                    self.crank_nome_revelado = data.get('crank_nome_revelado', False)
                    
                    # Rex
                    self.rex_primeira_aparicao_mostrada = data.get('rex_primeira_aparicao_mostrada', False)
                    self.rex_nome_revelado = data.get('rex_nome_revelado', False)
                    
                    # Glub
                    self.glub_primeira_aparicao_feita = data.get('glub_primeira_aparicao_feita', False)
                    self.glub_nome_revelado = data.get('glub_nome_revelado', False)
                    
                    # MercadorAlien
                    self.mercador_ultima_aparicao = data.get('mercador_ultima_aparicao', 0)
                    self.mercador_contador_eventos = data.get('mercador_contador_eventos', 0)
                    self.mercador_nome_revelado = data.get('mercador_nome_revelado', False)
                    
                    # Barão (Agiota)
                    self.barao_nome_revelado = data.get('barao_nome_revelado', False)
                    self.barao_emprestimo_ativo = data.get('barao_emprestimo_ativo', False)
                    self.barao_valor_devido = data.get('barao_valor_devido', 0)
                    self.barao_corridas_restantes = data.get('barao_corridas_restantes', 0)
                    
                    # Achievements
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
                    
                    # Desafios
                    self.desafios_diarios = data.get('desafios_diarios', [])
                    self.desafios_semanais = data.get('desafios_semanais', [])
                    self.missoes_pista = data.get('missoes_pista', {})
                    self.desafios_progresso = data.get('desafios_progresso', {})
                    self.desafios_completados = set(data.get('desafios_completados', []))
                    self.ultima_atualizacao_diaria = data.get('ultima_atualizacao_diaria', None)
                    self.ultima_atualizacao_semanal = data.get('ultima_atualizacao_semanal', None)
                    
                    # Estatísticas
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
                    
                    # Migrar dados antigos de arquivos separados (apenas na primeira vez)
                    self._migrar_dados_antigos()
                    
                    # Garantir que upgrades seja um dicionário válido antes de migrar
                    if not isinstance(self.upgrades, dict):
                        self.upgrades = {}
                    
                    try:
                        self._migrar_upgrades_antigos()
                    except Exception as e:
                        print(f"Erro ao migrar upgrades antigos: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    # Garantir que todas as chaves sejam strings para evitar KeyError com inteiros
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
                self.carros_desbloqueados = {'Car1'}  # Primeiro carro sempre desbloqueado
                self.recordes_corrida = {}
                self.recordes_drift = {}
                self.trofeus = {}
                self.upgrades = {}
                self.carro_p1_atual = None
                self.carro_p2_atual = None
        else:
            self.dinheiro = 5000  # Dinheiro inicial aumentado para permitir compra de carros iniciais
            self.carros_desbloqueados = {'Car1'}
            self.salvar()
    
    def salvar(self):
        """Salva o progresso no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_PROGRESSO), exist_ok=True)
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
                
                # Dados dos NPCs
                # Akira
                'akira_nome_revelado': self.akira_nome_revelado,
                'akira_dialogos_pre_corrida_mostrados': self.akira_dialogos_pre_corrida_mostrados,
                
                # Ranking
                'ranking_pilotos': self.ranking_pilotos,
                'ranking_posicao_jogador': self.ranking_posicao_jogador,
                
                # Crank
                'crank_humor_atual': self.crank_humor_atual,
                'crank_saude_carro': self.crank_saude_carro,
                'crank_tutorial_mostrado': self.crank_tutorial_mostrado,
                'crank_tutorial_upgrades_mostrado': self.crank_tutorial_upgrades_mostrado,
                'crank_prefixo_cor_ultimo_carro': self.crank_prefixo_cor_ultimo_carro,
                'crank_nome_revelado': self.crank_nome_revelado,
                
                # Rex
                'rex_primeira_aparicao_mostrada': self.rex_primeira_aparicao_mostrada,
                'rex_nome_revelado': self.rex_nome_revelado,
                
                # Glub
                'glub_primeira_aparicao_feita': self.glub_primeira_aparicao_feita,
                'glub_nome_revelado': self.glub_nome_revelado,
                
                # MercadorAlien
                'mercador_ultima_aparicao': self.mercador_ultima_aparicao,
                'mercador_contador_eventos': self.mercador_contador_eventos,
                'mercador_nome_revelado': self.mercador_nome_revelado,
                
                # Barão (Agiota)
                'barao_nome_revelado': self.barao_nome_revelado,
                'barao_emprestimo_ativo': self.barao_emprestimo_ativo,
                'barao_valor_devido': self.barao_valor_devido,
                'barao_corridas_restantes': self.barao_corridas_restantes,
                
                # Achievements
                'achievements_desbloqueados': list(self.achievements_desbloqueados),
                'achievements_visualizados': list(self.achievements_visualizados),
                'achievements_estatisticas': self.achievements_estatisticas,
                
                # Desafios
                'desafios_diarios': self.desafios_diarios,
                'desafios_semanais': self.desafios_semanais,
                'missoes_pista': self.missoes_pista,
                'desafios_progresso': self.desafios_progresso,
                'desafios_completados': list(self.desafios_completados),
                'ultima_atualizacao_diaria': self.ultima_atualizacao_diaria,
                'ultima_atualizacao_semanal': self.ultima_atualizacao_semanal,
                
                # Estatísticas
                'estatisticas_gerais': self.estatisticas_gerais,
                'estatisticas_por_pista': self.estatisticas_por_pista
            }
            with open(CAMINHO_PROGRESSO, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar progresso: {e}")
    
    def adicionar_dinheiro(self, quantidade):
        """Adiciona dinheiro ao jogador"""
        self.dinheiro += quantidade
        self.salvar()
    
    def remover_dinheiro(self, quantidade):
        """Remove dinheiro do jogador"""
        if self.dinheiro >= quantidade:
            self.dinheiro -= quantidade
            self.salvar()
            return True
        return False
    
    def tem_dinheiro(self, quantidade):
        """Verifica se o jogador tem dinheiro suficiente"""
        return self.dinheiro >= quantidade
    
    def desbloquear_carro(self, prefixo_cor):
        """Desbloqueia um carro"""
        self.carros_desbloqueados.add(prefixo_cor)
        self.salvar()
    
    def esta_desbloqueado(self, prefixo_cor):
        """Verifica se um carro está desbloqueado"""
        return prefixo_cor in self.carros_desbloqueados
    
    def comprar_carro(self, prefixo_cor, preco):
        """Tenta comprar um carro"""
        if self.esta_desbloqueado(prefixo_cor):
            return True  # Já está desbloqueado
        if self.tem_dinheiro(preco):
            self.remover_dinheiro(preco)
            self.desbloquear_carro(prefixo_cor)
            # Resetar saúde do carro quando comprar um carro novo
            from core.crank import crank
            if hasattr(crank, 'saude_carro'):
                crank.saude_carro = 1.0
                crank.salvar_estado()
            return True
        return False
    
    def vender_carro(self, prefixo_cor, preco_venda):
        """Vende um carro e remove upgrades associados"""
        if not self.esta_desbloqueado(prefixo_cor):
            return False  # Carro não está desbloqueado
        
        # Verificar se não é o único carro desbloqueado
        if len(self.carros_desbloqueados) <= 1:
            return False  # Não pode vender o último carro
        
        # Remover carro dos desbloqueados
        self.carros_desbloqueados.discard(prefixo_cor)
        
        # Remover upgrades do carro
        if prefixo_cor in self.upgrades:
            del self.upgrades[prefixo_cor]
        
        # Adicionar dinheiro (50% do preço original)
        self.adicionar_dinheiro(preco_venda)
        return True
    
    def contar_carros_desbloqueados(self):
        """Retorna a quantidade de carros desbloqueados"""
        return len(self.carros_desbloqueados)
    
    def definir_carro_atual(self, carro_p1=None, carro_p2=None):
        if carro_p1 is not None:
            self.carro_p1_atual = carro_p1
        if carro_p2 is not None:
            self.carro_p2_atual = carro_p2
        self.salvar()
    
    def obter_carro_atual(self, jogador=1):
        if jogador == 1:
            return self.carro_p1_atual
        else:
            return self.carro_p2_atual
    
    def registrar_recorde(self, numero_pista, tempo):
        """Registra um novo recorde de corrida para uma pista (se for melhor)"""
        # Converter numero_pista para string para consistência no JSON
        pista_key = str(numero_pista)
        # Verificar se é um novo recorde (menor tempo = melhor)
        if pista_key not in self.recordes_corrida or tempo < self.recordes_corrida[pista_key]:
            self.recordes_corrida[pista_key] = tempo
            self.salvar()  # Salvar imediatamente
            print(f"Recorde de corrida salvo para pista {pista_key}: {tempo:.2f}s")
            return True
        return False
    
    def obter_recorde(self, numero_pista):
        """Obtém o melhor tempo de corrida de uma pista"""
        # Converter numero_pista para string para buscar no dicionário
        pista_key = str(numero_pista)
        return self.recordes_corrida.get(pista_key, None)
    
    def registrar_recorde_drift(self, numero_pista, score):
        """Registra um novo recorde de drift para uma pista (se for melhor)"""
        # Converter numero_pista para string para consistência no JSON
        pista_key = str(numero_pista)
        # Verificar se é um novo recorde (maior score = melhor)
        if pista_key not in self.recordes_drift or score > self.recordes_drift[pista_key]:
            self.recordes_drift[pista_key] = score
            self.salvar()  # Salvar imediatamente
            print(f"Recorde de drift salvo para pista {pista_key}: {score:.0f} pontos")
            return True
        return False
    
    def obter_recorde_drift(self, numero_pista):
        """Obtém o melhor score de drift de uma pista"""
        # Converter numero_pista para string para buscar no dicionário
        pista_key = str(numero_pista)
        return self.recordes_drift.get(pista_key, None)
    
    def registrar_trofeu(self, numero_pista, tipo_trofeu):
        """Registra o troféu ganho em uma pista (ouro, prata, bronze)"""
        # Converter numero_pista para string para consistência no JSON
        pista_key = str(numero_pista)
        # Só atualiza se for melhor que o atual
        ordem = {"ouro": 3, "prata": 2, "bronze": 1, None: 0}
        atual = self.trofeus.get(pista_key)
        if ordem.get(tipo_trofeu, 0) > ordem.get(atual, 0):
            self.trofeus[pista_key] = tipo_trofeu
            self.salvar()  # Salvar imediatamente
            print(f"Trofeu salvo para pista {pista_key}: {tipo_trofeu}")
    
    def obter_trofeu(self, numero_pista):
        """Obtém o troféu ganho em uma pista"""
        # Converter numero_pista para string para buscar no dicionário
        pista_key = str(numero_pista)
        return self.trofeus.get(pista_key, None)
    
    def obter_upgrade(self, prefixo_cor, tipo_upgrade):
        """Obtém o nível de upgrade de um carro (0-5)"""
        if prefixo_cor not in self.upgrades:
            return 0
        return self.upgrades[prefixo_cor].get(tipo_upgrade, 0)
    
    def obter_todos_upgrades(self, prefixo_cor):
        """Obtém todos os upgrades de um carro"""
        return self.upgrades.get(prefixo_cor, {})
    
    def comprar_upgrade(self, prefixo_cor, tipo_upgrade, preco):
        """Tenta comprar um upgrade para um carro"""
        nivel_atual = self.obter_upgrade(prefixo_cor, tipo_upgrade)
        if nivel_atual >= 5:
            return False  # Já está no nível máximo
        
        if self.tem_dinheiro(preco):
            self.remover_dinheiro(preco)
            if prefixo_cor not in self.upgrades:
                self.upgrades[prefixo_cor] = {}
            self.upgrades[prefixo_cor][tipo_upgrade] = nivel_atual + 1
            self.salvar()
            return True
        return False
    
    def registrar_compra_alien(self, tipo, quantidade=1, tipo_upgrade=None):
        """Registra uma compra do mercador alien para diálogos raros do Crank"""
        self.ultima_compra_alien = {
            'tipo': tipo,  # 'golpe', 'upgrade_especial', 'multi_upgrade'
            'quantidade': quantidade,
            'tipo_upgrade': tipo_upgrade
        }
        # Resetar flag quando uma nova compra é registrada
        self.dialogo_alien_ja_mostrado = False
        self.salvar()
    
    def obter_ultima_compra_alien(self):
        """Obtém a última compra do mercador alien"""
        return self.ultima_compra_alien
    
    def limpar_ultima_compra_alien(self):
        """Limpa o registro da última compra do mercador alien"""
        self.ultima_compra_alien = None
        self.salvar()
    
    def marcar_upgrades_visitado(self, prefixo_cor):
        """Marca que o jogador já visitou a tela de upgrades para este carro"""
        self.upgrades_visitados.add(prefixo_cor)
        self.salvar()
    
    def upgrades_ja_visitado(self, prefixo_cor):
        """Verifica se o jogador já visitou a tela de upgrades para este carro"""
        return prefixo_cor in self.upgrades_visitados
    
    def calcular_preco_upgrade(self, tipo_upgrade, nivel_atual):
        """Calcula o preço do próximo nível de upgrade"""
        precos_base = {
            'motor': 500,
            'filtro_ar': 400,
            'ecu': 350,
            'transmissao': 550,
            'rodas': 450,
            'suspensao': 420,
            'nitro': 480
        }
        preco_base = precos_base.get(tipo_upgrade, 500)
        return int(preco_base * (1.5 ** nivel_atual))  # Aumenta 50% por nível
    
    def _migrar_upgrades_antigos(self):
        """Migra upgrades antigos para os novos nomes"""
        mapeamento = {
            'turbo': 'nitro',  # Migrar turbo antigo para nitro
            'pneus': 'rodas',
            'freios': None  # Freios removidos, não migrar
        }
        
        for prefixo_cor, upgrades_carro in self.upgrades.items():
            if not isinstance(upgrades_carro, dict):
                continue
            
            upgrades_novos = {}
            for tipo_antigo, nivel in upgrades_carro.items():
                if tipo_antigo in mapeamento:
                    tipo_novo = mapeamento[tipo_antigo]
                    if tipo_novo:  # Se não for None
                        upgrades_novos[tipo_novo] = nivel
                else:
                    # Manter upgrades que não precisam migração
                    upgrades_novos[tipo_antigo] = nivel
            
            self.upgrades[prefixo_cor] = upgrades_novos
        
        if self.upgrades:
            self.salvar()
    
    def _migrar_dados_antigos(self):
        """Migra dados de arquivos JSON antigos para o progresso.json (apenas uma vez)"""
        # Verificar se já migrou (se já tem dados no progresso, não migra novamente)
        if (self.akira_nome_revelado or self.akira_dialogos_pre_corrida_mostrados or
            self.ranking_pilotos or self.crank_humor_atual != 0 or
            self.rex_primeira_aparicao_mostrada or self.glub_primeira_aparicao_feita or
            self.mercador_ultima_aparicao != 0 or self.achievements_desbloqueados or
            self.desafios_diarios or self.estatisticas_gerais.get("corridas_completas", 0) > 0):
            return  # Já tem dados, não migrar novamente
        
        # Migrar Akira
        caminho_akira = os.path.join(DIR_PROJETO, "data", "akira.json")
        if os.path.exists(caminho_akira):
            try:
                with open(caminho_akira, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.akira_nome_revelado = data.get('nome_revelado', False)
                    self.akira_dialogos_pre_corrida_mostrados = data.get('dialogos_pre_corrida_mostrados', {})
                    print("✓ Dados da Akira migrados")
            except Exception as e:
                print(f"Erro ao migrar dados da Akira: {e}")
        
        # Migrar Ranking
        caminho_ranking = os.path.join(DIR_PROJETO, "data", "ranking.json")
        if os.path.exists(caminho_ranking):
            try:
                with open(caminho_ranking, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ranking_pilotos = data.get('ranking', [])
                    self.ranking_posicao_jogador = data.get('posicao_jogador', 10)
                    print("✓ Dados do Ranking migrados")
            except Exception as e:
                print(f"Erro ao migrar dados do Ranking: {e}")
        
        # Migrar Crank
        caminho_crank = os.path.join(DIR_PROJETO, "data", "crank.json")
        if os.path.exists(caminho_crank):
            try:
                with open(caminho_crank, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.crank_humor_atual = data.get('humor_atual', 0)
                    self.crank_saude_carro = data.get('saude_carro', 1.0)
                    self.crank_tutorial_mostrado = data.get('tutorial_mostrado', False)
                    self.crank_tutorial_upgrades_mostrado = data.get('tutorial_upgrades_mostrado', False)
                    self.crank_prefixo_cor_ultimo_carro = data.get('prefixo_cor_ultimo_carro', None)
                    self.crank_nome_revelado = data.get('nome_revelado', False)
                    print("✓ Dados do Crank migrados")
            except Exception as e:
                print(f"Erro ao migrar dados do Crank: {e}")
        
        # Migrar Rex
        caminho_rex = os.path.join(DIR_PROJETO, "data", "rex.json")
        if os.path.exists(caminho_rex):
            try:
                with open(caminho_rex, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.rex_primeira_aparicao_mostrada = data.get('primeira_aparicao_mostrada', False)
                    self.rex_nome_revelado = data.get('nome_revelado', False)
                    print("✓ Dados do Rex migrados")
            except Exception as e:
                print(f"Erro ao migrar dados do Rex: {e}")
        
        # Migrar Glub
        caminho_glub = os.path.join(DIR_PROJETO, "data", "glub.json")
        if os.path.exists(caminho_glub):
            try:
                with open(caminho_glub, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.glub_primeira_aparicao_feita = data.get('primeira_aparicao_feita', False)
                    self.glub_nome_revelado = data.get('nome_revelado', False)
                    print("✓ Dados do Glub migrados")
            except Exception as e:
                print(f"Erro ao migrar dados do Glub: {e}")
        
        # Migrar MercadorAlien
        caminho_mercador = os.path.join(DIR_PROJETO, "data", "mercador_alien.json")
        if os.path.exists(caminho_mercador):
            try:
                with open(caminho_mercador, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mercador_ultima_aparicao = data.get('ultima_aparicao', 0)
                    self.mercador_contador_eventos = data.get('contador_eventos', 0)
                    self.mercador_nome_revelado = data.get('nome_revelado', False)
                    print("✓ Dados do MercadorAlien migrados")
            except Exception as e:
                print(f"Erro ao migrar dados do MercadorAlien: {e}")
        
        # Migrar Achievements
        caminho_achievements = os.path.join(DIR_PROJETO, "data", "achievements.json")
        if os.path.exists(caminho_achievements):
            try:
                with open(caminho_achievements, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.achievements_desbloqueados = set(data.get('achievements_desbloqueados', []))
                    self.achievements_visualizados = set(data.get('achievements_visualizados', []))
                    self.achievements_estatisticas = data.get('estatisticas', self.achievements_estatisticas)
                    print("✓ Dados de Achievements migrados")
            except Exception as e:
                print(f"Erro ao migrar dados de Achievements: {e}")
        
        # Migrar Desafios
        caminho_desafios = os.path.join(DIR_PROJETO, "data", "desafios.json")
        if os.path.exists(caminho_desafios):
            try:
                with open(caminho_desafios, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.desafios_diarios = data.get('desafios_diarios', [])
                    self.desafios_semanais = data.get('desafios_semanais', [])
                    self.missoes_pista = data.get('missoes_pista', {})
                    self.desafios_progresso = data.get('progresso', {})
                    self.desafios_completados = set(data.get('completados', []))
                    self.ultima_atualizacao_diaria = data.get('ultima_atualizacao_diaria', None)
                    self.ultima_atualizacao_semanal = data.get('ultima_atualizacao_semanal', None)
                    print("✓ Dados de Desafios migrados")
            except Exception as e:
                print(f"Erro ao migrar dados de Desafios: {e}")
        
        # Migrar Estatísticas
        caminho_estatisticas = os.path.join(DIR_PROJETO, "data", "estatisticas.json")
        if os.path.exists(caminho_estatisticas):
            try:
                with open(caminho_estatisticas, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.estatisticas_gerais = data.get('estatisticas_gerais', self.estatisticas_gerais)
                    self.estatisticas_por_pista = data.get('estatisticas_por_pista', {})
                    print("✓ Dados de Estatísticas migrados")
            except Exception as e:
                print(f"Erro ao migrar dados de Estatísticas: {e}")
        
        # Salvar após migração
        if any([self.akira_nome_revelado, self.akira_dialogos_pre_corrida_mostrados,
                self.ranking_pilotos, self.crank_humor_atual != 0,
                self.rex_primeira_aparicao_mostrada, self.glub_primeira_aparicao_feita,
                self.mercador_ultima_aparicao != 0, self.achievements_desbloqueados,
                self.desafios_diarios, self.estatisticas_gerais.get("corridas_completas", 0) > 0]):
            self.salvar()
            print("✓ Migração concluída e salva")

# Instância global
gerenciador_progresso = GerenciadorProgresso()

