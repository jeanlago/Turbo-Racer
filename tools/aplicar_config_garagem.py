#!/usr/bin/env python3
"""
Script para aplicar configurações da garagem do JSON no main.py
===============================================================

Este script lê o arquivo data/garage_config.json e atualiza automaticamente
a lista CARROS_DISPONIVEIS no src/main.py com as novas configurações.

Uso:
    python tools/aplicar_config_garagem.py
"""

import sys
import os
import json
import re

# Caminhos
DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_JSON = os.path.join(DIR_BASE, 'data', 'garage_config.json')
CAMINHO_MAIN = os.path.join(DIR_BASE, 'src', 'main.py')

def aplicar_configuracoes():
    """Aplica as configurações do JSON no main.py"""
    
    # 1. Ler configurações do JSON
    if not os.path.exists(CAMINHO_JSON):
        print(f"Erro: Arquivo não encontrado: {CAMINHO_JSON}")
        print("Execute o garage_editor.py e salve as configurações (F5) primeiro.")
        return False
    
    try:
        with open(CAMINHO_JSON, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return False
    
    # Criar dicionário por prefixo_cor para busca rápida
    configs_por_carro = {carro['prefixo_cor']: carro for carro in dados.get('carros', [])}
    
    # 2. Ler main.py
    if not os.path.exists(CAMINHO_MAIN):
        print(f"Erro: Arquivo não encontrado: {CAMINHO_MAIN}")
        return False
    
    try:
        with open(CAMINHO_MAIN, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"Erro ao ler main.py: {e}")
        return False
    
    # 3. Encontrar e atualizar cada carro na lista CARROS_DISPONIVEIS
    # Padrão para encontrar cada linha de carro
    # Exemplo: {"nome": "Nissan 350Z", "prefixo_cor": "Car1", ...}
    
    linhas = conteudo.split('\n')
    novas_linhas = []
    i = 0
    
    while i < len(linhas):
        linha = linhas[i]
        
        # Verificar se é uma linha de carro (contém "prefixo_cor")
        if '"prefixo_cor"' in linha:
            # Extrair prefixo_cor da linha
            match = re.search(r'"prefixo_cor":\s*"([^"]+)"', linha)
            if match:
                prefixo_cor = match.group(1)
                
                # Verificar se temos configuração para este carro
                if prefixo_cor in configs_por_carro:
                    config = configs_por_carro[prefixo_cor]
                    
                    # Atualizar posicao
                    if 'posicao' in config:
                        posicao = tuple(config['posicao'])
                        linha = re.sub(
                            r'"posicao":\s*\([^)]+\)',
                            f'"posicao": {posicao}',
                            linha
                        )
                    
                    # Atualizar tamanho_oficina
                    if 'tamanho_oficina' in config:
                        tamanho = tuple(config['tamanho_oficina'])
                        linha = re.sub(
                            r'"tamanho_oficina":\s*\([^)]+\)',
                            f'"tamanho_oficina": {tamanho}',
                            linha
                        )
                    
                    # Atualizar posicao_oficina
                    if 'posicao_oficina' in config:
                        pos_oficina = tuple(config['posicao_oficina'])
                        # Pode estar como expressão (LARGURA//2 - 430) ou como tupla
                        linha = re.sub(
                            r'"posicao_oficina":\s*\([^)]+\)',
                            f'"posicao_oficina": {pos_oficina}',
                            linha
                        )
                    
                    print(f"✓ Atualizado: {prefixo_cor}")
        
        novas_linhas.append(linha)
        i += 1
    
    # 4. Salvar main.py atualizado
    try:
        with open(CAMINHO_MAIN, 'w', encoding='utf-8') as f:
            f.write('\n'.join(novas_linhas))
        print(f"\n✓ Configurações aplicadas com sucesso em {CAMINHO_MAIN}")
        return True
    except Exception as e:
        print(f"Erro ao salvar main.py: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Aplicando configurações da garagem no main.py...")
    print("="*60)
    
    if aplicar_configuracoes():
        print("\n✓ Processo concluído!")
        print("Agora você pode executar o jogo e ver as mudanças.")
    else:
        print("\n✗ Erro ao aplicar configurações.")
        sys.exit(1)

