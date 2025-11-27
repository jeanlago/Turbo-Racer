#!/usr/bin/env python3
"""
Script para gerar PDF com todos os roteiros/diálogos dos personagens
"""
import os
import sys
import re
import ast
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("Instalando reportlab...")
    os.system(f"{sys.executable} -m pip install reportlab")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

# Caminhos dos arquivos
DIR_PROJETO = Path(__file__).parent.parent
ARQUIVOS_NPCS = {
    "Crank": DIR_PROJETO / "src" / "core" / "crank.py",
    "Boris": DIR_PROJETO / "src" / "core" / "boris.py",
    "Pixel": DIR_PROJETO / "src" / "core" / "pixel.py",
    "Mercador Alien (Slick)": DIR_PROJETO / "src" / "core" / "mercador_alien.py",
    "Akira": DIR_PROJETO / "src" / "core" / "akira.py",
    "Barão": DIR_PROJETO / "src" / "core" / "barao.py",
    "Rex": DIR_PROJETO / "src" / "core" / "rex.py",
    "Glub": DIR_PROJETO / "src" / "core" / "glub.py",
}

def extrair_textos_entre_aspas(texto):
    """Extrai todos os textos entre aspas duplas do código"""
    textos = []
    # Padrão para encontrar strings entre aspas (incluindo strings multilinha)
    padrao = r'["\'](?:[^"\'\\]|\\.|["\']{3}.*?["\']{3})*["\']'
    
    # Encontrar todas as strings
    matches = re.finditer(padrao, texto, re.DOTALL)
    for match in matches:
        try:
            # Tentar avaliar como string Python
            valor = ast.literal_eval(match.group(0))
            # Filtrar apenas strings longas (provavelmente diálogos)
            if isinstance(valor, str) and len(valor) > 20 and not valor.startswith("assets") and not valor.startswith("data"):
                textos.append(valor)
        except:
            pass
    
    return textos

def extrair_dialogos_arquivo(caminho_arquivo):
    """Extrai diálogos de um arquivo Python"""
    if not caminho_arquivo.exists():
        return []
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    dialogos = []
    
    # Extrair textos de _iniciar_animacao_texto (incluindo strings multilinha e f-strings)
    # Padrão mais flexível que captura strings simples e f-strings
    padrao_iniciar = r'_iniciar_animacao_texto\([f]?["\']([^"\']+)["\']\)'
    matches = re.finditer(padrao_iniciar, conteudo, re.MULTILINE)
    for match in matches:
        texto = match.group(1)
        if len(texto) > 5:  # Reduzir limite mínimo
            dialogos.append(texto)
    
    # Extrair textos de texto_completo = "..."
    padrao_texto_completo = r'texto_completo\s*=\s*[f]?["\']([^"\']+)["\']'
    matches = re.finditer(padrao_texto_completo, conteudo, re.MULTILINE)
    for match in matches:
        texto = match.group(1)
        if len(texto) > 5:
            dialogos.append(texto)
    
    # Extrair textos de listas (saudações, textos, etc) - melhorado para capturar strings multilinha
    padrao_lista = r'(?:saudacoes|textos|falas|dialogos|partes)\s*=\s*\[(.*?)\]'
    matches = re.finditer(padrao_lista, conteudo, re.DOTALL)
    for match in matches:
        lista_texto = match.group(1)
        # Extrair strings da lista (incluindo f-strings)
        padrao_string = r'f?["\']([^"\']+)["\']'
        strings = re.findall(padrao_string, lista_texto)
        for s in strings:
            if len(s) > 10:
                dialogos.append(s)
    
    # Extrair textos de dicionários (partes de cutscenes)
    padrao_dict = r'\{\s*["\']texto["\']\s*:\s*f?["\']([^"\']+)["\']'
    matches = re.finditer(padrao_dict, conteudo, re.MULTILINE | re.DOTALL)
    for match in matches:
        texto = match.group(1)
        if len(texto) > 10:
            dialogos.append(texto)
    
    # Extrair textos diretos de atribuições
    padrao_atrib = r'texto\s*=\s*f?["\']([^"\']+)["\']'
    matches = re.finditer(padrao_atrib, conteudo, re.MULTILINE)
    for match in matches:
        texto = match.group(1)
        if len(texto) > 20:
            dialogos.append(texto)
    
    # Extrair textos de f-strings em atribuições
    padrao_fstring_atrib = r'texto\s*=\s*f["\']([^"\']+)["\']'
    matches = re.finditer(padrao_fstring_atrib, conteudo, re.MULTILINE)
    for match in matches:
        texto = match.group(1)
        if len(texto) > 20:
            dialogos.append(texto)
    
    # Extrair textos de random.choice (listas inline)
    padrao_random = r'random\.choice\(\[(.*?)\]\)'
    matches = re.finditer(padrao_random, conteudo, re.DOTALL)
    for match in matches:
        lista_texto = match.group(1)
        padrao_string = r'f?["\']([^"\']+)["\']'
        strings = re.findall(padrao_string, lista_texto)
        for s in strings:
            if len(s) > 10:
                dialogos.append(s)
    
    # Remover duplicatas mantendo ordem
    dialogos_unicos = []
    vistos = set()
    for dialogo in dialogos:
        dialogo_limpo = dialogo.strip()
        if dialogo_limpo and dialogo_limpo not in vistos:
            dialogos_unicos.append(dialogo_limpo)
            vistos.add(dialogo_limpo)
    
    return dialogos_unicos

def gerar_pdf(dialogos_por_personagem, caminho_saida):
    """Gera PDF com os roteiros"""
    doc = SimpleDocTemplate(str(caminho_saida), pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=(0, 0, 0),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=(50, 50, 150),
        spaceAfter=20,
        spaceBefore=20
    )
    
    dialogo_style = ParagraphStyle(
        'Dialogo',
        parent=styles['Normal'],
        fontSize=11,
        textColor=(0, 0, 0),
        spaceAfter=12,
        leftIndent=20,
        rightIndent=20
    )
    
    # Título principal
    story.append(Paragraph("TURBO RACER", titulo_style))
    story.append(Paragraph("Roteiros dos Personagens", styles['Title']))
    story.append(Spacer(1, 1*cm))
    
    # Para cada personagem
    for nome_personagem, dialogos in dialogos_por_personagem.items():
        if not dialogos:
            continue
        
        story.append(PageBreak())
        story.append(Paragraph(nome_personagem.upper(), subtitulo_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar cada diálogo
        for i, dialogo in enumerate(dialogos, 1):
            # Escapar caracteres especiais para HTML/PDF
            dialogo_escaped = dialogo.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"<b>[{i}]</b> {dialogo_escaped}", dialogo_style))
        
        story.append(Spacer(1, 0.5*cm))
    
    # Gerar PDF
    doc.build(story)
    print(f"PDF gerado: {caminho_saida}")

def main():
    """Função principal"""
    print("Extraindo roteiros dos personagens...")
    
    dialogos_por_personagem = {}
    
    for nome, caminho in ARQUIVOS_NPCS.items():
        print(f"Processando {nome}...")
        dialogos = extrair_dialogos_arquivo(caminho)
        dialogos_por_personagem[nome] = dialogos
        print(f"  {len(dialogos)} dialogos encontrados")
    
    # Gerar PDF
    caminho_pdf = DIR_PROJETO / "Roteiros_Personagens.pdf"
    print(f"\nGerando PDF: {caminho_pdf}")
    gerar_pdf(dialogos_por_personagem, caminho_pdf)
    
    # Resumo
    print("\n=== RESUMO ===")
    total = 0
    for nome, dialogos in dialogos_por_personagem.items():
        count = len(dialogos)
        total += count
        print(f"{nome}: {count} diálogos")
    print(f"\nTotal: {total} diálogos")
    print(f"\nPDF salvo em: {caminho_pdf}")

if __name__ == "__main__":
    main()

