"""
Sistema de internacionalização (i18n) para o jogo Turbo Racer
Suporta múltiplos idiomas: Português, Inglês, Espanhol e Francês
"""
import json
import os
from config import DIR_PROJETO

DIR_LOCALES = os.path.join(DIR_PROJETO, "data", "locales")

# Idioma padrão
IDIOMA_PADRAO = "pt"

# Cache de traduções
_traducoes = {}
_idioma_atual = IDIOMA_PADRAO

def atualizar_titulo_janela(tipo="menu"):
    """
    Atualiza o título da janela do jogo baseado no idioma atual
    
    Args:
        tipo: "menu" ou "jogo" para escolher qual título usar
    """
    try:
        import pygame
        titulo = t(f"titulo_jogo.{tipo}")
        pygame.display.set_caption(titulo)
    except:
        pass  # Se pygame não estiver inicializado, ignora

def carregar_idioma(idioma):
    """
    Carrega as traduções de um idioma específico
    
    Args:
        idioma: Código do idioma ('pt', 'en', 'es', 'fr')
    
    Returns:
        dict: Dicionário com as traduções ou None se não encontrar
    """
    global _traducoes, _idioma_atual
    
    caminho_arquivo = os.path.join(DIR_LOCALES, f"{idioma}.json")
    
    if not os.path.exists(caminho_arquivo):
        print(f"AVISO: Arquivo de idioma não encontrado: {caminho_arquivo}")
        # Tentar carregar idioma padrão
        if idioma != IDIOMA_PADRAO:
            return carregar_idioma(IDIOMA_PADRAO)
        return None
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            _traducoes = json.load(f)
            _idioma_atual = idioma
            print(f"Idioma carregado: {idioma}")
            atualizar_titulo_janela("menu")
            return _traducoes
    except Exception as e:
        print(f"ERRO ao carregar idioma {idioma}: {e}")
        if idioma != IDIOMA_PADRAO:
            return carregar_idioma(IDIOMA_PADRAO)
        return None

def definir_idioma(idioma):
    """
    Define o idioma atual e carrega as traduções
    
    Args:
        idioma: Código do idioma ('pt', 'en', 'es', 'fr')
    
    Returns:
        bool: True se o idioma foi carregado com sucesso
    """
    return carregar_idioma(idioma) is not None

def obter_idioma_atual():
    """
    Retorna o código do idioma atual
    
    Returns:
        str: Código do idioma atual
    """
    return _idioma_atual

def t(chave, **kwargs):
    """
    Obtém a tradução de uma chave
    
    Args:
        chave: Chave da tradução (ex: 'menu.jogar')
        **kwargs: Parâmetros para substituição no texto (ex: {'nome': 'João'})
    
    Returns:
        str: Texto traduzido ou a chave se não encontrar tradução
    """
    if not _traducoes:
        carregar_idioma(IDIOMA_PADRAO)
    
    # Buscar tradução usando notação de ponto (ex: 'menu.jogar')
    partes = chave.split('.')
    valor = _traducoes
    
    try:
        for parte in partes:
            valor = valor[parte]
        
        # Se o valor é uma string, fazer substituições se necessário
        if isinstance(valor, str) and kwargs:
            return valor.format(**kwargs)
        
        return valor
    except (KeyError, TypeError):
        return chave

def inicializar_idioma():
    """Inicializa o idioma a partir das configurações"""
    try:
        from config import CONFIGURACOES
        idioma_config = CONFIGURACOES.get("idioma", {}).get("idioma_atual", IDIOMA_PADRAO)
        carregar_idioma(idioma_config)
    except:
        carregar_idioma(IDIOMA_PADRAO)

# Inicializar com idioma padrão ou do config
inicializar_idioma()
