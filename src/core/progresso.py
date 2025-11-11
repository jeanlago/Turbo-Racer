# src/core/progresso.py
import json
import os
from config import DIR_PROJETO

CAMINHO_PROGRESSO = os.path.join(DIR_PROJETO, "data", "progresso.json")

class GerenciadorProgresso:
    """Gerencia o progresso do jogador: dinheiro e carros desbloqueados"""
    
    def __init__(self):
        self.dinheiro = 0
        self.carros_desbloqueados = set()  # Set de prefixos de carros desbloqueados
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
                'carros_desbloqueados': list(self.carros_desbloqueados)
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

# Instância global
gerenciador_progresso = GerenciadorProgresso()

