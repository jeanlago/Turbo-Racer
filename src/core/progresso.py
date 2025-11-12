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
        self.recordes = {}  # {numero_pista: melhor_tempo}
        self.trofeus = {}  # {numero_pista: "ouro"/"prata"/"bronze"/None}
        self.carregar()
    
    def carregar(self):
        """Carrega o progresso do arquivo"""
        if os.path.exists(CAMINHO_PROGRESSO):
            try:
                with open(CAMINHO_PROGRESSO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dinheiro = data.get('dinheiro', 0)
                    # Primeiro carro sempre desbloqueado
                    self.carros_desbloqueados = set(data.get('carros_desbloqueados', ['Car1']))
                    if 'Car1' not in self.carros_desbloqueados:
                        self.carros_desbloqueados.add('Car1')
                    # Recordes e troféus (garantir que são dicionários)
                    self.recordes = data.get('recordes', {})
                    self.trofeus = data.get('trofeus', {})
                    # Converter chaves numéricas para strings se necessário (compatibilidade)
                    if self.recordes:
                        self.recordes = {str(k): v for k, v in self.recordes.items()}
                    if self.trofeus:
                        self.trofeus = {str(k): v for k, v in self.trofeus.items()}
            except Exception as e:
                print(f"Erro ao carregar progresso: {e}")
                self.dinheiro = 0
                self.carros_desbloqueados = {'Car1'}  # Primeiro carro sempre desbloqueado
        else:
            # Primeira vez - desbloquear primeiro carro e dar dinheiro inicial
            self.dinheiro = 500  # Dinheiro inicial
            self.carros_desbloqueados = {'Car1'}  # Primeiro carro sempre desbloqueado
            self.salvar()
    
    def salvar(self):
        """Salva o progresso no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_PROGRESSO), exist_ok=True)
            data = {
                'dinheiro': self.dinheiro,
                'carros_desbloqueados': list(self.carros_desbloqueados),
                'recordes': self.recordes,
                'trofeus': self.trofeus
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
    
    def registrar_recorde(self, numero_pista, tempo):
        """Registra um novo recorde para uma pista (se for melhor)"""
        # Converter numero_pista para string para consistência no JSON
        pista_key = str(numero_pista)
        # Verificar se é um novo recorde (menor tempo = melhor)
        if pista_key not in self.recordes or tempo < self.recordes[pista_key]:
            self.recordes[pista_key] = tempo
            self.salvar()  # Salvar imediatamente
            print(f"Recorde salvo para pista {pista_key}: {tempo:.2f}s")
            return True
        return False
    
    def obter_recorde(self, numero_pista):
        """Obtém o melhor tempo de uma pista"""
        # Converter numero_pista para string para buscar no dicionário
        pista_key = str(numero_pista)
        return self.recordes.get(pista_key, None)
    
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

# Instância global
gerenciador_progresso = GerenciadorProgresso()

