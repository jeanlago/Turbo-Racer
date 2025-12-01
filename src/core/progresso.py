# src/core/progresso.py
import json
import os
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
        
        self.fuligem_nome_revelado = False
        self.fuligem_primeira_aparicao_mostrada = False
        
        self.capitulo_atual = None
        self.capitulos_completos = set()
        
        self.hierarquia_desbloqueada = False
        self.oficina_desbloqueada = False
        
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
                    
                    self.fuligem_nome_revelado = data.get('fuligem_nome_revelado', False)
                    self.fuligem_primeira_aparicao_mostrada = data.get('fuligem_primeira_aparicao_mostrada', False)
                    
                    self.capitulo_atual = data.get('capitulo_atual', None)
                    self.capitulos_completos = set(data.get('capitulos_completos', []))
                    
                    self.hierarquia_desbloqueada = data.get('hierarquia_desbloqueada', False)
                    self.oficina_desbloqueada = data.get('oficina_desbloqueada', False)
                    
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
                    
                    # Carregar flag de última corrida da campanha
                    self.ultima_corrida_campanha = data.get('ultima_corrida_campanha', None)
                    
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
                
                'akira_nome_revelado': self.akira_nome_revelado,
                'akira_dialogos_pre_corrida_mostrados': self.akira_dialogos_pre_corrida_mostrados,
                
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
                
                'fuligem_nome_revelado': self.fuligem_nome_revelado,
                'fuligem_primeira_aparicao_mostrada': self.fuligem_primeira_aparicao_mostrada,
                
                'capitulo_atual': self.capitulo_atual,
                'capitulos_completos': list(self.capitulos_completos),
                
                'hierarquia_desbloqueada': self.hierarquia_desbloqueada,
                'oficina_desbloqueada': self.oficina_desbloqueada,
                
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
                
                'ultima_corrida_campanha': self.ultima_corrida_campanha
            }
            
            with open(CAMINHO_PROGRESSO, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
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
    
    def obter_recorde_drift(self, numero_pista):
        """Obtém o recorde de drift de uma pista"""
        return self.recordes_drift.get(str(numero_pista), None)
    
    def obter_trofeu(self, numero_pista):
        """Obtém o troféu de uma pista"""
        return self.trofeus.get(str(numero_pista), None)
    
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
            # Remover upgrades do carro vendido
            if prefixo_cor in self.upgrades:
                del self.upgrades[prefixo_cor]
            # Se era o carro atual, resetar
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
        # Preço aumenta exponencialmente: base * (1.5 ^ nivel)
        return int(preco_base * (1.5 ** nivel_atual))
    
    def comprar_upgrade(self, prefixo_cor, tipo_upgrade, preco):
        """Compra um upgrade para um carro"""
        if prefixo_cor not in self.upgrades:
            self.upgrades[prefixo_cor] = {}
        
        nivel_atual = self.obter_upgrade(prefixo_cor, tipo_upgrade)
        if nivel_atual < 5:  # Máximo de 5 níveis
            if self.tem_dinheiro(preco):
                self.remover_dinheiro(preco)
                self.upgrades[prefixo_cor][tipo_upgrade] = nivel_atual + 1
                self.salvar()
                return True
        return False
    
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
    
    def _migrar_dados_antigos(self):
        """Migra dados de arquivos antigos para o progresso.json"""
        # Implementação básica - pode ser expandida conforme necessário
        pass
    
    def _migrar_upgrades_antigos(self):
        """Migra upgrades de formato antigo para novo"""
        # Implementação básica - pode ser expandida conforme necessário
        pass

# Instância global
gerenciador_progresso = GerenciadorProgresso()
