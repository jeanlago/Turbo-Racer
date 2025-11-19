# src/core/progresso.py
import json
import os
from config import DIR_PROJETO

CAMINHO_PROGRESSO = os.path.join(DIR_PROJETO, "data", "progresso.json")

class GerenciadorProgresso:
    """Gerencia o progresso do jogador: dinheiro, carros desbloqueados, recordes e troféus"""
    
    def __init__(self):
        self.dinheiro = 0
        self.carros_desbloqueados = set()  # Set de prefixos de carros desbloqueados
        self.recordes_corrida = {}  # {numero_pista: melhor_tempo}
        self.recordes_drift = {}  # {numero_pista: melhor_score}
        self.trofeus = {}  # {numero_pista: "ouro"/"prata"/"bronze"/None}
        self.upgrades = {}  # {prefixo_cor: {tipo_upgrade: nivel}} - nivel de 0 a 5
        self.carregar()
    
    def carregar(self):
        """Carrega o progresso do arquivo"""
        if os.path.exists(CAMINHO_PROGRESSO):
            try:
                with open(CAMINHO_PROGRESSO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dinheiro = data.get('dinheiro', 0)
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
                    self._migrar_upgrades_antigos()
                    if self.recordes_corrida:
                        self.recordes_corrida = {str(k): v for k, v in self.recordes_corrida.items()}
                    if self.recordes_drift:
                        self.recordes_drift = {str(k): v for k, v in self.recordes_drift.items()}
                    if self.trofeus:
                        self.trofeus = {str(k): v for k, v in self.trofeus.items()}
            except Exception as e:
                print(f"Erro ao carregar progresso: {e}")
                self.dinheiro = 0
                self.carros_desbloqueados = {'Car1'}  # Primeiro carro sempre desbloqueado
        else:
            self.dinheiro = 500
            self.carros_desbloqueados = {'Car1'}
            self.salvar()
    
    def salvar(self):
        """Salva o progresso no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_PROGRESSO), exist_ok=True)
            data = {
                'dinheiro': self.dinheiro,
                'carros_desbloqueados': list(self.carros_desbloqueados),
                'recordes_corrida': self.recordes_corrida,
                'recordes_drift': self.recordes_drift,
                'trofeus': self.trofeus,
                'upgrades': self.upgrades
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

# Instância global
gerenciador_progresso = GerenciadorProgresso()

