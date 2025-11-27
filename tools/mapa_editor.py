# tools/mapa_editor.py
"""
Editor de Áreas Clicáveis do Mapa da Cidade
Permite definir áreas clicáveis e acessíveis no mapa isométrico
"""

import os
import sys
import json
import pygame
from pathlib import Path

# Adicionar o diretório src ao path
diretorio_raiz = Path(__file__).parent.parent
sys.path.insert(0, str(diretorio_raiz))
sys.path.insert(0, str(diretorio_raiz / "src"))

from config import LARGURA, ALTURA, DIR_PROJETO

# Caminhos
CAMINHO_MAPA = os.path.join(DIR_PROJETO, "assets", "images", "ui", "cidade.png")
CAMINHO_AREAS = os.path.join(DIR_PROJETO, "data", "mapa_areas.json")

# Cores
COR_FUNDO = (30, 30, 40)
COR_AREA_NORMAL = (0, 200, 255, 100)
COR_AREA_SELECIONADA = (255, 200, 0, 150)
COR_BORDA = (255, 255, 255)
COR_TEXTO = (255, 255, 255)

class AreaClicavel:
    """Representa uma área clicável no mapa"""
    def __init__(self, id, nome, x, y, largura, altura, desbloqueada=True, sprite_fundo=None, territorio_id=None):
        self.id = id
        self.nome = nome
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.desbloqueada = desbloqueada
        self.sprite_fundo = sprite_fundo  # Caminho do sprite de fundo
        self.territorio_id = territorio_id  # ID do território correspondente
        self.selecionada = False
    
    def get_rect(self):
        """Retorna o retângulo pygame da área"""
        return pygame.Rect(self.x, self.y, self.largura, self.altura)
    
    def to_dict(self):
        """Converte para dicionário"""
        result = {
            "id": self.id,
            "nome": self.nome,
            "x": self.x,
            "y": self.y,
            "largura": self.largura,
            "altura": self.altura,
            "desbloqueada": self.desbloqueada
        }
        if self.sprite_fundo:
            result["sprite_fundo"] = self.sprite_fundo
        if self.territorio_id:
            result["territorio_id"] = self.territorio_id
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Cria a partir de um dicionário"""
        return cls(
            data["id"],
            data["nome"],
            data["x"],
            data["y"],
            data["largura"],
            data["altura"],
            data.get("desbloqueada", True),
            data.get("sprite_fundo"),
            data.get("territorio_id")
        )

class MapaEditor:
    """Editor de áreas clicáveis do mapa"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Editor de Áreas do Mapa - Turbo Racer")
        
        # Carregar imagem do mapa
        if os.path.exists(CAMINHO_MAPA):
            self.mapa_img = pygame.image.load(CAMINHO_MAPA).convert_alpha()
            # Escalar para caber na tela mantendo proporção
            escala_w = LARGURA / self.mapa_img.get_width()
            escala_h = ALTURA / self.mapa_img.get_height()
            escala = min(escala_w, escala_h, 1.0)  # Não aumentar além do original
            self.mapa_w = int(self.mapa_img.get_width() * escala)
            self.mapa_h = int(self.mapa_img.get_height() * escala)
            self.mapa_img = pygame.transform.scale(self.mapa_img, (self.mapa_w, self.mapa_h))
            self.mapa_x = (LARGURA - self.mapa_w) // 2
            self.mapa_y = (ALTURA - self.mapa_h) // 2
        else:
            print(f"AVISO: Mapa não encontrado em {CAMINHO_MAPA}")
            self.mapa_img = None
            self.mapa_w = LARGURA
            self.mapa_h = ALTURA
            self.mapa_x = 0
            self.mapa_y = 0
        
        # Áreas clicáveis
        self.areas = []
        self.area_selecionada = None
        self.area_em_arraste = None
        self.offset_arraste = (0, 0)
        
        # Modo de edição
        self.modo = "selecionar"  # "selecionar", "criar", "redimensionar"
        self.canto_redimensionamento = None
        
        # Carregar áreas salvas
        self.carregar_areas()
        
        # Fonte
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        
        # Estado
        self.clock = pygame.time.Clock()
        self.running = True
    
    def carregar_areas(self):
        """Carrega áreas do arquivo JSON"""
        if os.path.exists(CAMINHO_AREAS):
            try:
                with open(CAMINHO_AREAS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.areas = [AreaClicavel.from_dict(a) for a in data.get("areas", [])]
                print(f"✓ Carregadas {len(self.areas)} áreas do arquivo")
            except Exception as e:
                print(f"Erro ao carregar áreas: {e}")
                self.areas = []
        else:
            self.areas = []
    
    def salvar_areas(self):
        """Salva áreas no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_AREAS), exist_ok=True)
            data = {
                "areas": [area.to_dict() for area in self.areas]
            }
            with open(CAMINHO_AREAS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Salvas {len(self.areas)} áreas no arquivo")
        except Exception as e:
            print(f"Erro ao salvar áreas: {e}")
    
    def criar_nova_area(self, x, y):
        """Cria uma nova área na posição especificada"""
        nome = f"Area_{len(self.areas) + 1}"
        nova_area = AreaClicavel(
            id=nome.lower().replace(" ", "_"),
            nome=nome,
            x=x,
            y=y,
            largura=120,
            altura=80,
            desbloqueada=True
        )
        self.areas.append(nova_area)
        self.area_selecionada = nova_area
        return nova_area
    
    def encontrar_area_em(self, x, y):
        """Encontra a área que contém o ponto (x, y)"""
        for area in reversed(self.areas):  # Verificar de trás para frente (últimas por cima)
            rect = area.get_rect()
            if rect.collidepoint(x, y):
                return area
        return None
    
    def encontrar_canto_redimensionamento(self, area, x, y):
        """Encontra qual canto está sendo redimensionado"""
        rect = area.get_rect()
        margem = 10
        
        # Cantos
        cantos = {
            "nw": (rect.left, rect.top),
            "ne": (rect.right, rect.top),
            "sw": (rect.left, rect.bottom),
            "se": (rect.right, rect.bottom)
        }
        
        for nome, (cx, cy) in cantos.items():
            if abs(x - cx) < margem and abs(y - cy) < margem:
                return nome
        
        return None
    
    def processar_eventos(self):
        """Processa eventos do pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.area_selecionada = None
                    self.modo = "selecionar"
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.salvar_areas()
                elif event.key == pygame.K_n:
                    self.modo = "criar"
                elif event.key == pygame.K_DELETE and self.area_selecionada:
                    self.areas.remove(self.area_selecionada)
                    self.area_selecionada = None
                elif event.key == pygame.K_t and self.area_selecionada:
                    # Editar nome
                    nome_atual = self.area_selecionada.nome
                    novo_nome = input(f"Nome atual: {nome_atual}\nNovo nome (ou Enter para cancelar): ").strip()
                    if novo_nome:
                        self.area_selecionada.nome = novo_nome
                        self.area_selecionada.id = novo_nome.lower().replace(" ", "_")
                elif event.key == pygame.K_f and self.area_selecionada:
                    # Editar sprite de fundo (usar caminho relativo)
                    # Escanear sprites disponíveis na pasta UI
                    pasta_ui = os.path.join(DIR_PROJETO, "assets", "images", "ui")
                    sprites_disponiveis = []
                    if os.path.exists(pasta_ui):
                        for arquivo in os.listdir(pasta_ui):
                            if arquivo.endswith(('.png', '.jpg', '.jpeg')) and arquivo != "cidade.png" and arquivo != "menu.png":
                                sprites_disponiveis.append(arquivo)
                        sprites_disponiveis.sort()
                    
                    print("\nSprites disponíveis:")
                    sprites_dict = {}
                    for i, sprite in enumerate(sprites_disponiveis, start=1):
                        print(f"{i}. {sprite}")
                        sprites_dict[str(i)] = sprite
                    print(f"{len(sprites_disponiveis) + 1}. Nenhum (remover)")
                    sprites_dict[str(len(sprites_disponiveis) + 1)] = None
                    
                    escolha = input(f"Escolha o sprite (1-{len(sprites_disponiveis) + 1}): ").strip()
                    if escolha in sprites_dict:
                        sprite = sprites_dict[escolha]
                        if sprite:
                            # Salvar caminho relativo (será resolvido no jogo)
                            self.area_selecionada.sprite_fundo = os.path.join("assets", "images", "ui", sprite)
                            print(f"✓ Sprite definido: {sprite}")
                        else:
                            self.area_selecionada.sprite_fundo = None
                            print("✓ Sprite removido")
                    else:
                        print("✗ Escolha inválida")
                elif event.key == pygame.K_r and self.area_selecionada:
                    # Editar territorio_id
                    territorio_atual = self.area_selecionada.territorio_id or ""
                    novo_id = input(f"Território ID atual: {territorio_atual}\nNovo ID (ou Enter para remover): ").strip()
                    if novo_id:
                        self.area_selecionada.territorio_id = novo_id
                    else:
                        self.area_selecionada.territorio_id = None
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    mouse_x, mouse_y = event.pos
                    
                    # Ajustar coordenadas para o mapa
                    mapa_mouse_x = mouse_x - self.mapa_x
                    mapa_mouse_y = mouse_y - self.mapa_y
                    
                    if self.modo == "criar":
                        # Criar nova área
                        self.criar_nova_area(mapa_mouse_x, mapa_mouse_y)
                        self.modo = "selecionar"
                    else:
                        # Selecionar ou arrastar área
                        area = self.encontrar_area_em(mapa_mouse_x, mapa_mouse_y)
                        if area:
                            self.area_selecionada = area
                            # Verificar se está clicando em um canto para redimensionar
                            canto = self.encontrar_canto_redimensionamento(area, mapa_mouse_x, mapa_mouse_y)
                            if canto:
                                self.modo = "redimensionar"
                                self.canto_redimensionamento = canto
                                self.area_em_arraste = area
                                self.offset_arraste = (mapa_mouse_x - area.x, mapa_mouse_y - area.y)
                            else:
                                # Arrastar área
                                self.modo = "arrastar"
                                self.area_em_arraste = area
                                self.offset_arraste = (mapa_mouse_x - area.x, mapa_mouse_y - area.y)
                        else:
                            self.area_selecionada = None
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.area_em_arraste = None
                    self.modo = "selecionar"
                    self.canto_redimensionamento = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.area_em_arraste:
                    mouse_x, mouse_y = event.pos
                    mapa_mouse_x = mouse_x - self.mapa_x
                    mapa_mouse_y = mouse_y - self.mapa_y
                    
                    if self.modo == "arrastar":
                        # Mover área
                        self.area_em_arraste.x = mapa_mouse_x - self.offset_arraste[0]
                        self.area_em_arraste.y = mapa_mouse_y - self.offset_arraste[1]
                    elif self.modo == "redimensionar":
                        # Redimensionar área
                        canto = self.canto_redimensionamento
                        if canto == "nw":
                            # Canto superior esquerdo
                            nova_largura = self.area_em_arraste.x + self.area_em_arraste.largura - mapa_mouse_x
                            nova_altura = self.area_em_arraste.y + self.area_em_arraste.altura - mapa_mouse_y
                            if nova_largura > 20:
                                self.area_em_arraste.x = mapa_mouse_x
                                self.area_em_arraste.largura = nova_largura
                            if nova_altura > 20:
                                self.area_em_arraste.y = mapa_mouse_y
                                self.area_em_arraste.altura = nova_altura
                        elif canto == "ne":
                            # Canto superior direito
                            nova_largura = mapa_mouse_x - self.area_em_arraste.x
                            nova_altura = self.area_em_arraste.y + self.area_em_arraste.altura - mapa_mouse_y
                            if nova_largura > 20:
                                self.area_em_arraste.largura = nova_largura
                            if nova_altura > 20:
                                self.area_em_arraste.y = mapa_mouse_y
                                self.area_em_arraste.altura = nova_altura
                        elif canto == "sw":
                            # Canto inferior esquerdo
                            nova_largura = self.area_em_arraste.x + self.area_em_arraste.largura - mapa_mouse_x
                            nova_altura = mapa_mouse_y - self.area_em_arraste.y
                            if nova_largura > 20:
                                self.area_em_arraste.x = mapa_mouse_x
                                self.area_em_arraste.largura = nova_largura
                            if nova_altura > 20:
                                self.area_em_arraste.altura = nova_altura
                        elif canto == "se":
                            # Canto inferior direito
                            nova_largura = mapa_mouse_x - self.area_em_arraste.x
                            nova_altura = mapa_mouse_y - self.area_em_arraste.y
                            if nova_largura > 20:
                                self.area_em_arraste.largura = nova_largura
                            if nova_altura > 20:
                                self.area_em_arraste.altura = nova_altura
    
    def desenhar(self):
        """Desenha o editor"""
        self.screen.fill(COR_FUNDO)
        
        # Desenhar mapa
        if self.mapa_img:
            self.screen.blit(self.mapa_img, (self.mapa_x, self.mapa_y))
        
        # Desenhar áreas
        for area in self.areas:
            rect = area.get_rect()
            # Ajustar para posição do mapa
            rect_ajustado = pygame.Rect(
                rect.x + self.mapa_x,
                rect.y + self.mapa_y,
                rect.width,
                rect.height
            )
            
            # Cor baseada na seleção
            if area == self.area_selecionada:
                cor = COR_AREA_SELECIONADA
                espessura_borda = 3
            else:
                cor = COR_AREA_NORMAL
                espessura_borda = 2
            
            # Desenhar área
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            overlay.fill(cor)
            self.screen.blit(overlay, rect_ajustado.topleft)
            pygame.draw.rect(self.screen, COR_BORDA, rect_ajustado, espessura_borda)
            
            # Desenhar nome
            texto = self.fonte_pequena.render(area.nome, True, COR_TEXTO)
            texto_x = rect_ajustado.x + 5
            texto_y = rect_ajustado.y + 5
            self.screen.blit(texto, (texto_x, texto_y))
            
            # Desenhar cantos de redimensionamento se selecionada
            if area == self.area_selecionada:
                cantos = [
                    (rect_ajustado.left, rect_ajustado.top),
                    (rect_ajustado.right, rect_ajustado.top),
                    (rect_ajustado.left, rect_ajustado.bottom),
                    (rect_ajustado.right, rect_ajustado.bottom)
                ]
                for cx, cy in cantos:
                    pygame.draw.circle(self.screen, COR_BORDA, (cx, cy), 5)
        
        # Desenhar informações
        info_y = 10
        info_textos = [
            "Editor de Áreas do Mapa",
            "N - Criar nova área",
            "T - Editar nome da área selecionada",
            "F - Editar sprite de fundo",
            "R - Editar territorio_id",
            "DELETE - Remover área selecionada",
            "CTRL+S - Salvar",
            "ESC - Desselecionar",
            "",
            f"Áreas: {len(self.areas)}"
        ]
        
        # Mostrar informações da área selecionada
        if self.area_selecionada:
            info_textos.append("")
            info_textos.append(f"Selecionada: {self.area_selecionada.nome}")
            if self.area_selecionada.sprite_fundo:
                sprite_nome = os.path.basename(self.area_selecionada.sprite_fundo)
                info_textos.append(f"Sprite: {sprite_nome}")
            if self.area_selecionada.territorio_id:
                info_textos.append(f"Território: {self.area_selecionada.territorio_id}")
        
        for texto in info_textos:
            if texto:
                render = self.fonte_pequena.render(texto, True, COR_TEXTO)
                self.screen.blit(render, (10, info_y))
            info_y += 20
        
        pygame.display.flip()
    
    def run(self):
        """Loop principal do editor"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.processar_eventos()
            self.desenhar()
        
        # Salvar ao fechar
        self.salvar_areas()
        pygame.quit()

if __name__ == "__main__":
    editor = MapaEditor()
    editor.run()

