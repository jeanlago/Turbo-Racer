# tools/scenario_editor.py
"""
Editor de Hitboxes de Cenários
Permite definir áreas clicáveis com hover em cenários do jogo
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

from config import LARGURA, ALTURA, DIR_PROJETO, obter_caminho_sprite_dia_noite, obter_caminho_hover_dia_noite

# Caminhos
CAMINHO_UI = os.path.join(DIR_PROJETO, "assets", "images", "ui")
CAMINHO_HOVER = os.path.join(DIR_PROJETO, "assets", "images", "hover")
CAMINHO_HITBOXES = os.path.join(DIR_PROJETO, "data", "scenario_hitboxes.json")

# Cores
COR_FUNDO = (30, 30, 40)
COR_HITBOX_NORMAL = (0, 200, 255, 100)
COR_HITBOX_SELECIONADA = (255, 200, 0, 150)
COR_HITBOX_HOVER = (255, 100, 0, 120)
COR_BORDA = (255, 255, 255)
COR_TEXTO = (255, 255, 255)

class HitboxClicavel:
    """Representa uma hitbox clicável em um cenário"""
    def __init__(self, id, nome, x, y, largura, altura, hover_sprite=None, acao=None):
        self.id = id
        self.nome = nome
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.hover_sprite = hover_sprite  # Caminho do sprite de hover
        self.acao = acao  # Ação a ser executada ao clicar (opcional)
        self.selecionada = False
    
    def get_rect(self):
        """Retorna o retângulo pygame da hitbox"""
        return pygame.Rect(self.x, self.y, self.largura, self.altura)
    
    def to_dict(self):
        """Converte para dicionário"""
        result = {
            "id": self.id,
            "nome": self.nome,
            "x": self.x,
            "y": self.y,
            "largura": self.largura,
            "altura": self.altura
        }
        if self.hover_sprite:
            result["hover_sprite"] = self.hover_sprite
        if self.acao:
            result["acao"] = self.acao
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
            data.get("hover_sprite"),
            data.get("acao")
        )

class ScenarioEditor:
    """Editor de hitboxes de cenários"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Editor de Hitboxes de Cenários - Turbo Racer")
        
        # Cenário atual
        self.cenario_atual = None
        self.cenario_img = None
        self.cenario_w = LARGURA
        self.cenario_h = ALTURA
        self.cenario_x = 0
        self.cenario_y = 0
        
        # Hitboxes
        self.hitboxes = {}
        self.hitbox_selecionada = None
        self.hitbox_em_arraste = None
        self.offset_arraste = (0, 0)
        
        # Modo de edição
        self.modo = "selecionar"  # "selecionar", "criar", "redimensionar"
        self.canto_redimensionamento = None
        
        # Carregar cenários disponíveis
        self.cenarios_disponiveis = self._listar_cenarios()
        
        # Carregar hitboxes salvas
        self.carregar_hitboxes()
        
        # Fonte
        self.fonte = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
        
        # Estado
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Mouse hover
        self.mouse_hover_hitbox = None
        self.hover_sprite_cache = {}  # Cache de sprites de hover carregados
        
        # Menu de seleção de cenário
        self.menu_cenario_aberto = False
        self.menu_cenario_selecionado = 0
        
        # Menu de seleção de hover
        self.menu_hover_aberto = False
        self.menu_hover_selecionado = 0
        self.hover_sprites_lista = []
        
        # Mostrar hitboxes
        self.mostrar_hitboxes = True
    
    def _listar_cenarios(self):
        """Lista todos os cenários disponíveis na pasta UI"""
        cenarios = []
        if os.path.exists(CAMINHO_UI):
            for arquivo in os.listdir(CAMINHO_UI):
                if arquivo.endswith(('.png', '.jpg', '.jpeg')):
                    cenarios.append(arquivo)
        cenarios.sort()
        return cenarios
    
    def _listar_hover_sprites(self, subpasta=None):
        """Lista sprites de hover disponíveis"""
        hover_sprites = []
        
        if not os.path.exists(CAMINHO_HOVER):
            print(f"AVISO: Pasta de hover não encontrada: {CAMINHO_HOVER}")
            return hover_sprites
        
        # Se subpasta especificada, listar apenas ela
        if subpasta:
            caminho_hover = os.path.join(CAMINHO_HOVER, subpasta)
            if os.path.exists(caminho_hover):
                for arquivo in os.listdir(caminho_hover):
                    if arquivo.endswith(('.png', '.jpg', '.jpeg')):
                        hover_sprites.append(f"{subpasta}/{arquivo}")
        else:
            # Listar todos os arquivos na raiz
            for arquivo in os.listdir(CAMINHO_HOVER):
                arquivo_path = os.path.join(CAMINHO_HOVER, arquivo)
                if os.path.isfile(arquivo_path) and arquivo.endswith(('.png', '.jpg', '.jpeg')):
                    hover_sprites.append(arquivo)
            
            # Listar arquivos em subpastas
            for item in os.listdir(CAMINHO_HOVER):
                item_path = os.path.join(CAMINHO_HOVER, item)
                if os.path.isdir(item_path):
                    for arquivo in os.listdir(item_path):
                        if arquivo.endswith(('.png', '.jpg', '.jpeg')):
                            hover_sprites.append(f"{item}/{arquivo}")
        
        hover_sprites.sort()
        print(f"DEBUG: Encontrados {len(hover_sprites)} sprites de hover")
        return hover_sprites
    
    def carregar_cenario(self, nome_arquivo):
        """Carrega um cenário (usando sistema dia/noite)"""
        # Tentar carregar usando sistema dia/noite
        nome_base = os.path.splitext(nome_arquivo)[0]
        caminho = obter_caminho_sprite_dia_noite(nome_base)
        
        if not os.path.exists(caminho):
            # Fallback: tentar caminho direto
            caminho = os.path.join(CAMINHO_UI, nome_arquivo)
        
        if os.path.exists(caminho):
            try:
                self.cenario_img = pygame.image.load(caminho).convert_alpha()
                # Escalar para caber na tela mantendo proporção
                escala_w = LARGURA / self.cenario_img.get_width()
                escala_h = ALTURA / self.cenario_img.get_height()
                escala = min(escala_w, escala_h, 1.0)  # Não aumentar além do original
                self.cenario_w = int(self.cenario_img.get_width() * escala)
                self.cenario_h = int(self.cenario_img.get_height() * escala)
                self.cenario_img = pygame.transform.scale(self.cenario_img, (self.cenario_w, self.cenario_h))
                self.cenario_x = (LARGURA - self.cenario_w) // 2
                self.cenario_y = (ALTURA - self.cenario_h) // 2
                # Usar o nome original do arquivo para identificar as hitboxes
                self.cenario_atual = nome_arquivo
                print(f"✓ Cenário carregado: {nome_arquivo} (de: {os.path.basename(caminho)})")
                return True
            except Exception as e:
                print(f"Erro ao carregar cenário: {e}")
                return False
        else:
            print(f"AVISO: Cenário não encontrado em {caminho}")
            return False
    
    def carregar_hitboxes(self):
        """Carrega hitboxes do arquivo JSON"""
        if os.path.exists(CAMINHO_HITBOXES):
            try:
                with open(CAMINHO_HITBOXES, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Converter para dicionário por cenário
                    for cenario, hitboxes in data.items():
                        self.hitboxes[cenario] = [HitboxClicavel.from_dict(h) for h in hitboxes]
                print(f"✓ Carregadas hitboxes de {len(self.hitboxes)} cenários")
            except Exception as e:
                print(f"Erro ao carregar hitboxes: {e}")
                self.hitboxes = {}
        else:
            self.hitboxes = {}
    
    def salvar_hitboxes(self):
        """Salva hitboxes no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_HITBOXES), exist_ok=True)
            # Converter para dicionário simples
            data = {}
            for cenario, hitboxes in self.hitboxes.items():
                data[cenario] = [h.to_dict() for h in hitboxes]
            with open(CAMINHO_HITBOXES, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Salvas hitboxes de {len(self.hitboxes)} cenários")
        except Exception as e:
            print(f"Erro ao salvar hitboxes: {e}")
    
    def obter_hitboxes_cenario(self):
        """Obtém hitboxes do cenário atual (tenta várias variações do nome para suportar dia/noite)"""
        if not self.cenario_atual:
            return []
        
        # Primeiro, tentar o nome exato (ex: casa.png)
        if self.cenario_atual in self.hitboxes:
            return self.hitboxes[self.cenario_atual]
        
        # Extrair nome base (sem extensão e sem sufixos dia/noite)
        nome_completo = self.cenario_atual
        nome_base_original = os.path.splitext(nome_completo)[0]  # Remove extensão
        
        # Remover sufixos _dia ou _noite se existirem
        if nome_base_original.endswith("_dia"):
            nome_base_original = nome_base_original[:-4]  # Remove "_dia"
        elif nome_base_original.endswith("_noite"):
            nome_base_original = nome_base_original[:-6]  # Remove "_noite"
        
        extensao = os.path.splitext(nome_completo)[1]  # Pega extensão
        
        # Tentar na ordem: nome original, _dia, _noite, e qualquer que comece com o nome base
        chaves_para_tentar = [
            f"{nome_base_original}{extensao}",  # casa.png
            f"{nome_base_original}_dia{extensao}",  # casa_dia.png
            f"{nome_base_original}_noite{extensao}",  # casa_noite.png
        ]
        
        for chave in chaves_para_tentar:
            if chave in self.hitboxes:
                print(f"✓ Hitboxes encontradas para chave: {chave}")
                return self.hitboxes[chave]
        
        # Última tentativa: qualquer chave que comece com o nome base
        for chave in self.hitboxes.keys():
            chave_base = os.path.splitext(chave)[0]
            # Remover sufixos da chave também
            if chave_base.endswith("_dia"):
                chave_base = chave_base[:-4]
            elif chave_base.endswith("_noite"):
                chave_base = chave_base[:-6]
            
            if chave_base.lower() == nome_base_original.lower():
                print(f"✓ Hitboxes encontradas para chave (match parcial): {chave}")
                return self.hitboxes[chave]
        
        print(f"AVISO: Nenhuma hitbox encontrada para '{self.cenario_atual}'. Chaves disponíveis: {list(self.hitboxes.keys())}")
        return []
    
    def adicionar_hitbox_cenario(self, hitbox):
        """Adiciona uma hitbox ao cenário atual"""
        if not self.cenario_atual:
            print("AVISO: Nenhum cenário carregado")
            return
        if self.cenario_atual not in self.hitboxes:
            self.hitboxes[self.cenario_atual] = []
        self.hitboxes[self.cenario_atual].append(hitbox)
    
    def remover_hitbox_cenario(self, hitbox):
        """Remove uma hitbox do cenário atual"""
        if not self.cenario_atual:
            return
        if self.cenario_atual in self.hitboxes:
            if hitbox in self.hitboxes[self.cenario_atual]:
                self.hitboxes[self.cenario_atual].remove(hitbox)
    
    def criar_nova_hitbox(self, x, y):
        """Cria uma nova hitbox na posição especificada"""
        nome = f"Hitbox_{len(self.obter_hitboxes_cenario()) + 1}"
        nova_hitbox = HitboxClicavel(
            id=nome.lower().replace(" ", "_"),
            nome=nome,
            x=x,
            y=y,
            largura=120,
            altura=80,
            hover_sprite=None
        )
        self.adicionar_hitbox_cenario(nova_hitbox)
        self.hitbox_selecionada = nova_hitbox
        return nova_hitbox
    
    def encontrar_hitbox_em(self, x, y):
        """Encontra a hitbox que contém o ponto (x, y)"""
        hitboxes = self.obter_hitboxes_cenario()
        for hitbox in reversed(hitboxes):  # Verificar de trás para frente
            rect = hitbox.get_rect()
            if rect.collidepoint(x, y):
                return hitbox
        return None
    
    def encontrar_canto_redimensionamento(self, hitbox, x, y):
        """Encontra qual canto está sendo redimensionado"""
        rect = hitbox.get_rect()
        margem = 15  # Aumentado para facilitar o clique
        
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
        
        # Também verificar bordas para redimensionamento
        margem_borda = 8
        if abs(x - rect.left) < margem_borda and rect.top <= y <= rect.bottom:
            return "w"  # Borda esquerda
        elif abs(x - rect.right) < margem_borda and rect.top <= y <= rect.bottom:
            return "e"  # Borda direita
        elif abs(y - rect.top) < margem_borda and rect.left <= x <= rect.right:
            return "n"  # Borda superior
        elif abs(y - rect.bottom) < margem_borda and rect.left <= x <= rect.right:
            return "s"  # Borda inferior
        
        return None
    
    def processar_eventos(self):
        """Processa eventos do pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.hitbox_selecionada = None
                    self.modo = "selecionar"
                elif event.key == pygame.K_v:
                    # Alternar visualização de hitboxes
                    self.mostrar_hitboxes = not self.mostrar_hitboxes
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.salvar_hitboxes()
                elif event.key == pygame.K_n:
                    self.modo = "criar"
                elif event.key == pygame.K_DELETE and self.hitbox_selecionada:
                    self.remover_hitbox_cenario(self.hitbox_selecionada)
                    self.hitbox_selecionada = None
                elif event.key == pygame.K_t and self.hitbox_selecionada and not self.menu_cenario_aberto:
                    # Editar nome (usando input simples, mas com try/except para evitar crash)
                    try:
                        nome_atual = self.hitbox_selecionada.nome
                        print(f"\nNome atual: {nome_atual}")
                        print("Digite o novo nome no console (ou Enter para cancelar):")
                        novo_nome = input().strip()
                        if novo_nome:
                            self.hitbox_selecionada.nome = novo_nome
                            self.hitbox_selecionada.id = novo_nome.lower().replace(" ", "_")
                            print(f"✓ Nome atualizado para: {novo_nome}")
                    except Exception as e:
                        print(f"Erro ao editar nome: {e}")
                elif event.key == pygame.K_h and self.hitbox_selecionada and not self.menu_cenario_aberto:
                    # Abrir/fechar menu de seleção de hover
                    if hasattr(self, 'menu_hover_aberto') and self.menu_hover_aberto:
                        self.menu_hover_aberto = False
                    else:
                        self.menu_hover_aberto = True
                        self.menu_hover_selecionado = 0
                        self.hover_sprites_lista = self._listar_hover_sprites()
                        if not self.hover_sprites_lista:
                            print(f"AVISO: Nenhum sprite de hover encontrado em {CAMINHO_HOVER}")
                            self.menu_hover_aberto = False
                elif hasattr(self, 'menu_hover_aberto') and self.menu_hover_aberto:
                    # Navegação no menu de hover
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_hover_selecionado = (self.menu_hover_selecionado - 1) % (len(self.hover_sprites_lista) + 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_hover_selecionado = (self.menu_hover_selecionado + 1) % (len(self.hover_sprites_lista) + 1)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Selecionar hover
                        if self.menu_hover_selecionado < len(self.hover_sprites_lista):
                            sprite = self.hover_sprites_lista[self.menu_hover_selecionado]
                            self.hitbox_selecionada.hover_sprite = os.path.join("assets", "images", "hover", sprite)
                            print(f"✓ Sprite de hover definido: {sprite}")
                        else:
                            # Opção "Nenhum"
                            self.hitbox_selecionada.hover_sprite = None
                            print("✓ Sprite de hover removido")
                        self.menu_hover_aberto = False
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_hover_aberto = False
                elif event.key == pygame.K_a and self.hitbox_selecionada and not self.menu_cenario_aberto:
                    # Editar ação (usando input simples, mas com try/except)
                    try:
                        acao_atual = self.hitbox_selecionada.acao or ""
                        print(f"\nAção atual: {acao_atual}")
                        print("Digite a nova ação no console (ou Enter para remover):")
                        nova_acao = input().strip()
                        if nova_acao:
                            self.hitbox_selecionada.acao = nova_acao
                            print(f"✓ Ação atualizada para: {nova_acao}")
                        else:
                            self.hitbox_selecionada.acao = None
                            print("✓ Ação removida")
                    except Exception as e:
                        print(f"Erro ao editar ação: {e}")
                elif event.key == pygame.K_c:
                    # Abrir/fechar menu de seleção de cenário
                    if self.menu_cenario_aberto:
                        self.menu_cenario_aberto = False
                    else:
                        self.menu_cenario_aberto = True
                        self.menu_cenario_selecionado = 0
                elif self.menu_cenario_aberto:
                    # Navegação no menu de cenários
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_cenario_selecionado = (self.menu_cenario_selecionado - 1) % len(self.cenarios_disponiveis)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_cenario_selecionado = (self.menu_cenario_selecionado + 1) % len(self.cenarios_disponiveis)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Selecionar cenário
                        if 0 <= self.menu_cenario_selecionado < len(self.cenarios_disponiveis):
                            self.carregar_cenario(self.cenarios_disponiveis[self.menu_cenario_selecionado])
                            self.menu_cenario_aberto = False
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_cenario_aberto = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    mouse_x, mouse_y = event.pos
                    
                    # Verificar se clicou no menu de hover
                    if hasattr(self, 'menu_hover_aberto') and self.menu_hover_aberto:
                        menu_x = LARGURA // 2 - 200
                        menu_y = ALTURA // 2 - 150
                        menu_w = 400
                        menu_h = min(400, (len(self.hover_sprites_lista) + 1) * 30 + 60)
                        
                        if menu_x <= mouse_x <= menu_x + menu_w and menu_y <= mouse_y <= menu_y + menu_h:
                            # Calcular qual item foi clicado
                            item_y = menu_y + 40
                            for i in range(len(self.hover_sprites_lista) + 1):
                                if item_y <= mouse_y <= item_y + 25:
                                    self.menu_hover_selecionado = i
                                    if i < len(self.hover_sprites_lista):
                                        sprite = self.hover_sprites_lista[i]
                                        self.hitbox_selecionada.hover_sprite = os.path.join("assets", "images", "hover", sprite)
                                        print(f"✓ Sprite de hover definido: {sprite}")
                                    else:
                                        self.hitbox_selecionada.hover_sprite = None
                                        print("✓ Sprite de hover removido")
                                    self.menu_hover_aberto = False
                                    break
                                item_y += 25
                        else:
                            # Clicou fora do menu, fechar
                            self.menu_hover_aberto = False
                    # Verificar se clicou no menu de cenários
                    elif self.menu_cenario_aberto:
                        menu_x = LARGURA // 2 - 200
                        menu_y = ALTURA // 2 - 150
                        menu_w = 400
                        menu_h = min(300, len(self.cenarios_disponiveis) * 30 + 60)
                        
                        if menu_x <= mouse_x <= menu_x + menu_w and menu_y <= mouse_y <= menu_y + menu_h:
                            # Calcular qual item foi clicado
                            item_y = menu_y + 40
                            for i, cenario in enumerate(self.cenarios_disponiveis):
                                if item_y <= mouse_y <= item_y + 25:
                                    self.menu_cenario_selecionado = i
                                    self.carregar_cenario(self.cenarios_disponiveis[i])
                                    self.menu_cenario_aberto = False
                                    break
                                item_y += 25
                        else:
                            # Clicou fora do menu, fechar
                            self.menu_cenario_aberto = False
                    else:
                        # Ajustar coordenadas para o cenário
                        cenario_mouse_x = mouse_x - self.cenario_x
                        cenario_mouse_y = mouse_y - self.cenario_y
                        
                        if self.modo == "criar":
                            # Criar nova hitbox
                            self.criar_nova_hitbox(cenario_mouse_x, cenario_mouse_y)
                            self.modo = "selecionar"
                        else:
                            # Selecionar ou arrastar hitbox
                            hitbox = self.encontrar_hitbox_em(cenario_mouse_x, cenario_mouse_y)
                            if hitbox:
                                self.hitbox_selecionada = hitbox
                                # Verificar se está clicando em um canto para redimensionar
                                canto = self.encontrar_canto_redimensionamento(hitbox, cenario_mouse_x, cenario_mouse_y)
                                if canto:
                                    self.modo = "redimensionar"
                                    self.canto_redimensionamento = canto
                                    self.hitbox_em_arraste = hitbox
                                    self.offset_arraste = (cenario_mouse_x - hitbox.x, cenario_mouse_y - hitbox.y)
                                else:
                                    # Arrastar hitbox
                                    self.modo = "arrastar"
                                    self.hitbox_em_arraste = hitbox
                                    self.offset_arraste = (cenario_mouse_x - hitbox.x, cenario_mouse_y - hitbox.y)
                            else:
                                self.hitbox_selecionada = None
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.hitbox_em_arraste = None
                    self.modo = "selecionar"
                    self.canto_redimensionamento = None
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                cenario_mouse_x = mouse_x - self.cenario_x
                cenario_mouse_y = mouse_y - self.cenario_y
                
                # Verificar hover
                self.mouse_hover_hitbox = self.encontrar_hitbox_em(cenario_mouse_x, cenario_mouse_y)
                
                # Carregar sprite de hover se necessário (usando sistema dia/noite)
                if self.mouse_hover_hitbox and self.mouse_hover_hitbox.hover_sprite:
                    if self.mouse_hover_hitbox.hover_sprite not in self.hover_sprite_cache:
                        hover_path_original = os.path.join(DIR_PROJETO, self.mouse_hover_hitbox.hover_sprite.replace("\\", "/"))
                        # Usar sistema dia/noite para obter o caminho correto
                        hover_path = obter_caminho_hover_dia_noite(hover_path_original)
                        
                        if os.path.exists(hover_path):
                            try:
                                hover_sprite_raw = pygame.image.load(hover_path).convert_alpha()
                                # Escalas diferentes por objeto
                                hitbox_id = self.mouse_hover_hitbox.id.lower()
                                
                                # Inicializar variáveis com valores padrão (garantir que sempre tenham valor)
                                hover_largura = int(self.mouse_hover_hitbox.largura * 1.15)
                                hover_altura = int(self.mouse_hover_hitbox.altura * 1.15)
                                
                                if "sofa" in hitbox_id:
                                    escala = 1.35  # Sofá: 35% maior
                                    hover_largura = int(self.mouse_hover_hitbox.largura * escala)
                                    hover_altura = int(self.mouse_hover_hitbox.altura * escala)
                                elif "tv" in hitbox_id:
                                    escala = 1.30  # TV: 30% maior
                                    hover_largura = int(self.mouse_hover_hitbox.largura * escala)
                                    hover_altura = int(self.mouse_hover_hitbox.altura * escala)
                                elif "cama" in hitbox_id:
                                    escala = 1.20  # Cama: 20% maior
                                    hover_largura = int(self.mouse_hover_hitbox.largura * escala)
                                    hover_altura = int(self.mouse_hover_hitbox.altura * escala)
                                elif "cafe" in hitbox_id or "cafeteira" in hitbox_id:
                                    # Cafeteira: manter proporção original do sprite
                                    sprite_w, sprite_h = hover_sprite_raw.get_size()
                                    if sprite_w > 0 and sprite_h > 0:
                                        escala_w = self.mouse_hover_hitbox.largura / sprite_w
                                        escala_h = self.mouse_hover_hitbox.altura / sprite_h
                                        escala = min(escala_w, escala_h) * 1.15  # 15% maior mantendo proporção
                                        hover_largura = int(sprite_w * escala)
                                        hover_altura = int(sprite_h * escala)
                                else:
                                    escala = 1.15  # Padrão: 15% maior
                                    hover_largura = int(self.mouse_hover_hitbox.largura * escala)
                                    hover_altura = int(self.mouse_hover_hitbox.altura * escala)
                                
                                self.hover_sprite_cache[self.mouse_hover_hitbox.hover_sprite] = pygame.transform.scale(
                                    hover_sprite_raw, (hover_largura, hover_altura)
                                )
                            except Exception as e:
                                print(f"Erro ao carregar sprite de hover: {e}")
                        else:
                            print(f"AVISO: Sprite de hover não encontrado: {hover_path} (original: {hover_path_original})")
                
                if self.hitbox_em_arraste:
                    if self.modo == "arrastar":
                        # Mover hitbox
                        self.hitbox_em_arraste.x = cenario_mouse_x - self.offset_arraste[0]
                        self.hitbox_em_arraste.y = cenario_mouse_y - self.offset_arraste[1]
                    elif self.modo == "redimensionar":
                        # Redimensionar hitbox
                        canto = self.canto_redimensionamento
                        min_tamanho = 20
                        
                        if canto == "nw":
                            # Canto superior esquerdo
                            nova_largura = self.hitbox_em_arraste.x + self.hitbox_em_arraste.largura - cenario_mouse_x
                            nova_altura = self.hitbox_em_arraste.y + self.hitbox_em_arraste.altura - cenario_mouse_y
                            if nova_largura > min_tamanho:
                                self.hitbox_em_arraste.x = cenario_mouse_x
                                self.hitbox_em_arraste.largura = nova_largura
                            if nova_altura > min_tamanho:
                                self.hitbox_em_arraste.y = cenario_mouse_y
                                self.hitbox_em_arraste.altura = nova_altura
                        elif canto == "ne":
                            # Canto superior direito
                            nova_largura = cenario_mouse_x - self.hitbox_em_arraste.x
                            nova_altura = self.hitbox_em_arraste.y + self.hitbox_em_arraste.altura - cenario_mouse_y
                            if nova_largura > min_tamanho:
                                self.hitbox_em_arraste.largura = nova_largura
                            if nova_altura > min_tamanho:
                                self.hitbox_em_arraste.y = cenario_mouse_y
                                self.hitbox_em_arraste.altura = nova_altura
                        elif canto == "sw":
                            # Canto inferior esquerdo
                            nova_largura = self.hitbox_em_arraste.x + self.hitbox_em_arraste.largura - cenario_mouse_x
                            nova_altura = cenario_mouse_y - self.hitbox_em_arraste.y
                            if nova_largura > min_tamanho:
                                self.hitbox_em_arraste.x = cenario_mouse_x
                                self.hitbox_em_arraste.largura = nova_largura
                            if nova_altura > min_tamanho:
                                self.hitbox_em_arraste.altura = nova_altura
                        elif canto == "se":
                            # Canto inferior direito
                            nova_largura = cenario_mouse_x - self.hitbox_em_arraste.x
                            nova_altura = cenario_mouse_y - self.hitbox_em_arraste.y
                            if nova_largura > min_tamanho:
                                self.hitbox_em_arraste.largura = nova_largura
                            if nova_altura > min_tamanho:
                                self.hitbox_em_arraste.altura = nova_altura
                        elif canto == "n":
                            # Borda superior
                            nova_altura = self.hitbox_em_arraste.y + self.hitbox_em_arraste.altura - cenario_mouse_y
                            if nova_altura > min_tamanho:
                                self.hitbox_em_arraste.y = cenario_mouse_y
                                self.hitbox_em_arraste.altura = nova_altura
                        elif canto == "s":
                            # Borda inferior
                            nova_altura = cenario_mouse_y - self.hitbox_em_arraste.y
                            if nova_altura > min_tamanho:
                                self.hitbox_em_arraste.altura = nova_altura
                        elif canto == "w":
                            # Borda esquerda
                            nova_largura = self.hitbox_em_arraste.x + self.hitbox_em_arraste.largura - cenario_mouse_x
                            if nova_largura > min_tamanho:
                                self.hitbox_em_arraste.x = cenario_mouse_x
                                self.hitbox_em_arraste.largura = nova_largura
                        elif canto == "e":
                            # Borda direita
                            nova_largura = cenario_mouse_x - self.hitbox_em_arraste.x
                            if nova_largura > min_tamanho:
                                self.hitbox_em_arraste.largura = nova_largura
    
    def desenhar(self):
        """Desenha o editor"""
        self.screen.fill(COR_FUNDO)
        
        # Desenhar cenário
        if self.cenario_img:
            self.screen.blit(self.cenario_img, (self.cenario_x, self.cenario_y))
        
        # Desenhar sprite de hover se houver hitbox em hover
        if self.mouse_hover_hitbox and self.mouse_hover_hitbox.hover_sprite:
            if self.mouse_hover_hitbox.hover_sprite in self.hover_sprite_cache:
                hover_sprite = self.hover_sprite_cache[self.mouse_hover_hitbox.hover_sprite]
                # Calcular posição (centralizado na hitbox)
                # Usar a escala que foi usada para criar o sprite
                hitbox_id = self.mouse_hover_hitbox.id.lower()
                if "sofa" in hitbox_id:
                    escala = 1.35
                elif "tv" in hitbox_id:
                    escala = 1.30
                else:
                    escala = 1.15
                
                offset_x = (self.mouse_hover_hitbox.largura - int(self.mouse_hover_hitbox.largura * escala)) // 2
                offset_y = (self.mouse_hover_hitbox.altura - int(self.mouse_hover_hitbox.altura * escala)) // 2
                hover_x = self.cenario_x + self.mouse_hover_hitbox.x + offset_x
                hover_y = self.cenario_y + self.mouse_hover_hitbox.y + offset_y
                self.screen.blit(hover_sprite, (hover_x, hover_y))
        
        # Desenhar menu de seleção de hover se aberto
        if hasattr(self, 'menu_hover_aberto') and self.menu_hover_aberto:
            menu_x = LARGURA // 2 - 200
            menu_y = ALTURA // 2 - 150
            menu_w = 400
            menu_h = min(400, (len(self.hover_sprites_lista) + 1) * 30 + 60)
            
            # Fundo do menu
            menu_surface = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
            menu_surface.fill((40, 40, 50, 240))
            self.screen.blit(menu_surface, (menu_x, menu_y))
            pygame.draw.rect(self.screen, COR_BORDA, (menu_x, menu_y, menu_w, menu_h), 2)
            
            # Título
            titulo = self.fonte.render("Selecione o Sprite de Hover", True, COR_TEXTO)
            titulo_x = menu_x + (menu_w - titulo.get_width()) // 2
            self.screen.blit(titulo, (titulo_x, menu_y + 10))
            
            # Lista de sprites
            item_y = menu_y + 40
            for i, sprite in enumerate(self.hover_sprites_lista):
                if i == self.menu_hover_selecionado:
                    # Item selecionado
                    pygame.draw.rect(self.screen, COR_HITBOX_SELECIONADA, 
                                    (menu_x + 5, item_y - 2, menu_w - 10, 25))
                
                texto = self.fonte_pequena.render(sprite, True, COR_TEXTO)
                self.screen.blit(texto, (menu_x + 10, item_y))
                item_y += 25
            
            # Opção "Nenhum"
            if len(self.hover_sprites_lista) == self.menu_hover_selecionado:
                pygame.draw.rect(self.screen, COR_HITBOX_SELECIONADA, 
                                (menu_x + 5, item_y - 2, menu_w - 10, 25))
            texto_nenhum = self.fonte_pequena.render("Nenhum (remover)", True, COR_TEXTO)
            self.screen.blit(texto_nenhum, (menu_x + 10, item_y))
            item_y += 25
            
            # Instruções
            instrucoes = [
                "↑↓ ou W/S - Navegar",
                "ENTER - Selecionar",
                "ESC - Cancelar"
            ]
            instrucoes_y = item_y + 10
            for instrucao in instrucoes:
                texto_inst = self.fonte_pequena.render(instrucao, True, (200, 200, 200))
                self.screen.blit(texto_inst, (menu_x + 10, instrucoes_y))
                instrucoes_y += 18
        
        # Desenhar menu de seleção de cenário se aberto
        elif self.menu_cenario_aberto:
            menu_x = LARGURA // 2 - 200
            menu_y = ALTURA // 2 - 150
            menu_w = 400
            menu_h = min(300, len(self.cenarios_disponiveis) * 30 + 60)
            
            # Fundo do menu
            menu_surface = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
            menu_surface.fill((40, 40, 50, 240))
            self.screen.blit(menu_surface, (menu_x, menu_y))
            pygame.draw.rect(self.screen, COR_BORDA, (menu_x, menu_y, menu_w, menu_h), 2)
            
            # Título
            titulo = self.fonte.render("Selecione o Cenário", True, COR_TEXTO)
            titulo_x = menu_x + (menu_w - titulo.get_width()) // 2
            self.screen.blit(titulo, (titulo_x, menu_y + 10))
            
            # Lista de cenários
            item_y = menu_y + 40
            for i, cenario in enumerate(self.cenarios_disponiveis):
                if i == self.menu_cenario_selecionado:
                    # Item selecionado
                    pygame.draw.rect(self.screen, COR_HITBOX_SELECIONADA, 
                                    (menu_x + 5, item_y - 2, menu_w - 10, 25))
                
                texto = self.fonte_pequena.render(cenario, True, COR_TEXTO)
                self.screen.blit(texto, (menu_x + 10, item_y))
                item_y += 25
            
            # Instruções
            instrucoes = [
                "↑↓ ou W/S - Navegar",
                "ENTER - Selecionar",
                "ESC - Cancelar"
            ]
            instrucoes_y = item_y + 10
            for instrucao in instrucoes:
                texto_inst = self.fonte_pequena.render(instrucao, True, (200, 200, 200))
                self.screen.blit(texto_inst, (menu_x + 10, instrucoes_y))
                instrucoes_y += 18
        
        # Desenhar hitboxes (se habilitado)
        if self.mostrar_hitboxes:
            hitboxes = self.obter_hitboxes_cenario()
            for hitbox in hitboxes:
                rect = hitbox.get_rect()
                # Ajustar para posição do cenário
                rect_ajustado = pygame.Rect(
                    rect.x + self.cenario_x,
                    rect.y + self.cenario_y,
                    rect.width,
                    rect.height
                )
                
                # Cor baseada na seleção e hover
                if hitbox == self.hitbox_selecionada:
                    cor = COR_HITBOX_SELECIONADA
                    espessura_borda = 3
                elif hitbox == self.mouse_hover_hitbox:
                    cor = COR_HITBOX_HOVER
                    espessura_borda = 2
                else:
                    cor = COR_HITBOX_NORMAL
                    espessura_borda = 2
                
                # Desenhar hitbox
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                overlay.fill(cor)
                self.screen.blit(overlay, rect_ajustado.topleft)
                pygame.draw.rect(self.screen, COR_BORDA, rect_ajustado, espessura_borda)
                
                # Desenhar nome
                texto = self.fonte_pequena.render(hitbox.nome, True, COR_TEXTO)
                texto_x = rect_ajustado.x + 5
                texto_y = rect_ajustado.y + 5
                self.screen.blit(texto, (texto_x, texto_y))
                
                # Desenhar cantos e bordas de redimensionamento se selecionada
                if hitbox == self.hitbox_selecionada:
                    # Cantos (círculos maiores)
                    cantos = [
                        (rect_ajustado.left, rect_ajustado.top),
                        (rect_ajustado.right, rect_ajustado.top),
                        (rect_ajustado.left, rect_ajustado.bottom),
                        (rect_ajustado.right, rect_ajustado.bottom)
                    ]
                    for cx, cy in cantos:
                        pygame.draw.circle(self.screen, COR_BORDA, (cx, cy), 8)
                        pygame.draw.circle(self.screen, (255, 255, 0), (cx, cy), 6)
                    
                    # Indicadores de bordas (pequenos retângulos)
                    margem_borda = 8
                    # Borda superior
                    pygame.draw.rect(self.screen, COR_BORDA, 
                                   (rect_ajustado.centerx - 15, rect_ajustado.top - margem_borda, 30, margem_borda))
                    # Borda inferior
                    pygame.draw.rect(self.screen, COR_BORDA, 
                                   (rect_ajustado.centerx - 15, rect_ajustado.bottom, 30, margem_borda))
                    # Borda esquerda
                    pygame.draw.rect(self.screen, COR_BORDA, 
                                   (rect_ajustado.left - margem_borda, rect_ajustado.centery - 15, margem_borda, 30))
                    # Borda direita
                    pygame.draw.rect(self.screen, COR_BORDA, 
                                   (rect_ajustado.right, rect_ajustado.centery - 15, margem_borda, 30))
        
        # Desenhar informações
        info_y = 10
        info_textos = [
            "Editor de Hitboxes de Cenários",
            "C - Carregar cenário",
            "N - Criar nova hitbox",
            "T - Editar nome da hitbox selecionada",
            "H - Editar sprite de hover",
            "A - Editar ação",
            "V - Mostrar/Ocultar hitboxes",
            "DELETE - Remover hitbox selecionada",
            "CTRL+S - Salvar",
            "ESC - Desselecionar",
            "",
            f"Cenário: {self.cenario_atual or 'Nenhum'}",
            f"Hitboxes: {len(self.obter_hitboxes_cenario())}",
            f"Mostrar hitboxes: {'SIM' if self.mostrar_hitboxes else 'NÃO'}"
        ]
        
        # Mostrar informações da hitbox selecionada
        if self.hitbox_selecionada:
            info_textos.append("")
            info_textos.append(f"Selecionada: {self.hitbox_selecionada.nome}")
            if self.hitbox_selecionada.hover_sprite:
                sprite_nome = os.path.basename(self.hitbox_selecionada.hover_sprite)
                info_textos.append(f"Hover: {sprite_nome}")
            if self.hitbox_selecionada.acao:
                info_textos.append(f"Ação: {self.hitbox_selecionada.acao}")
        
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
        self.salvar_hitboxes()
        pygame.quit()

if __name__ == "__main__":
    editor = ScenarioEditor()
    editor.run()

