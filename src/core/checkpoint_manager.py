import json
import os
import pygame
from config import DIR_PROJETO, MAPAS_DISPONIVEIS, MAPA_ATUAL, obter_caminho_checkpoints

class CheckpointManager:
    """Gerenciador de checkpoints com edição em tempo real para múltiplos mapas"""
    
    TILE_SIZE = 300
    CENTRO_PISTA_X = 2500
    CENTRO_PISTA_Y = 2500
    
    def _centralizar_no_tile(self, x, y):
        """
        Centraliza coordenadas no centro do tile mais próximo.
        Os tiles têm 300x300px e são posicionados em relação ao centro (2500, 2500).
        O centro de um tile é: canto_superior_esquerdo + 150px (metade de 300px).
        """
        offset_x = x - self.CENTRO_PISTA_X
        offset_y = y - self.CENTRO_PISTA_Y
        
        tile_canto_x = round(offset_x / self.TILE_SIZE) * self.TILE_SIZE
        tile_canto_y = round(offset_y / self.TILE_SIZE) * self.TILE_SIZE
        
        tile_centro_x = tile_canto_x + (self.TILE_SIZE // 2)
        tile_centro_y = tile_canto_y + (self.TILE_SIZE // 2)
        
        return self.CENTRO_PISTA_X + tile_centro_x, self.CENTRO_PISTA_Y + tile_centro_y
    
    def __init__(self, mapa_atual=None, checkpoints_iniciais=None, numero_pista=None):
        self.checkpoints = []
        self.modo_edicao = False
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.mapa_atual = mapa_atual or MAPA_ATUAL
        self.numero_pista = numero_pista
        self.arquivo_checkpoints = obter_caminho_checkpoints()
        self.carregar_checkpoints()
        if not self.checkpoints and checkpoints_iniciais:
            self.checkpoints = []
            for cp in checkpoints_iniciais:
                if isinstance(cp, (list, tuple)) and len(cp) >= 2:
                    if len(cp) >= 3:
                        self.checkpoints.append([float(cp[0]), float(cp[1]), float(cp[2])])
                    else:
                        self.checkpoints.append([float(cp[0]), float(cp[1])])
    
    def trocar_mapa(self, novo_mapa):
        """Troca para um novo mapa e carrega seus checkpoints"""
        if novo_mapa in MAPAS_DISPONIVEIS:
            if self.checkpoints:
                self.salvar_checkpoints()
            
            self.mapa_atual = novo_mapa
            self.arquivo_checkpoints = obter_caminho_checkpoints()
            self.checkpoint_selecionado = -1
            self.checkpoint_em_arraste = -1
            self.carregar_checkpoints()
            print(f"Trocado para mapa: {MAPAS_DISPONIVEIS[novo_mapa]['nome']}")
            return True
        return False
    
    def carregar_checkpoints(self):
        """Carrega checkpoints do arquivo JSON (prioridade: checkpoint_editor, depois arquivo antigo)"""
        try:
            numero_pista = self.numero_pista
            
            if numero_pista is None:
                if self.mapa_atual and isinstance(self.mapa_atual, str):
                    import re
                    match = re.search(r'(\d+)', self.mapa_atual)
                    if match:
                        numero_pista = int(match.group(1))
                
                if numero_pista is None and self.mapa_atual in MAPAS_DISPONIVEIS:
                    nome_mapa = MAPAS_DISPONIVEIS[self.mapa_atual].get("nome", "")
                    match = re.search(r'(\d+)', nome_mapa)
                    if match:
                        numero_pista = int(match.group(1))
            
            if numero_pista and 1 <= numero_pista <= 9:
                from config import DIR_PROJETO
                DIR_DATA = os.path.join(DIR_PROJETO, "data")
                arquivo_checkpoint_editor = os.path.join(DIR_DATA, f"checkpoints_pista_{numero_pista}.json")
                
                print(f"Tentando carregar checkpoints da pista {numero_pista} do arquivo: {arquivo_checkpoint_editor}")
                print(f"Arquivo existe? {os.path.exists(arquivo_checkpoint_editor)}")
                
                if os.path.exists(arquivo_checkpoint_editor):
                    with open(arquivo_checkpoint_editor, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    if isinstance(dados, dict):
                        checkpoints_json = dados.get("checkpoints", [])
                    else:
                        checkpoints_json = dados
                    
                    if checkpoints_json:
                        self.checkpoints = []
                        for cp in checkpoints_json:
                            if len(cp) >= 3:
                                self.checkpoints.append([float(cp[0]), float(cp[1]), float(cp[2])])
                            elif len(cp) >= 2:
                                self.checkpoints.append([float(cp[0]), float(cp[1])])
                        return
            
            if os.path.exists(self.arquivo_checkpoints):
                with open(self.arquivo_checkpoints, 'r', encoding='utf-8') as f:
                    self.checkpoints = json.load(f)
            else:
                self.checkpoints = []
        except Exception:
            self.checkpoints = []
    
    def salvar_checkpoints(self):
        """Salva checkpoints no arquivo JSON"""
        try:
            diretorio = os.path.dirname(self.arquivo_checkpoints)
            if diretorio and not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
            
            with open(self.arquivo_checkpoints, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoints, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def adicionar_checkpoint(self, x, y):
        """Adiciona um novo checkpoint na posição especificada, centralizado no tile"""
        cx, cy = self._centralizar_no_tile(x, y)
        self.checkpoints.append([float(cx), float(cy)])
    
    def remover_checkpoint(self, indice):
        """Remove checkpoint pelo índice"""
        if 0 <= indice < len(self.checkpoints):
            self.checkpoints.pop(indice)
            return True
        return False
    
    def mover_checkpoint(self, indice, novo_x, novo_y):
        """Move checkpoint para nova posição, centralizado no tile"""
        if 0 <= indice < len(self.checkpoints):
            cx, cy = self._centralizar_no_tile(novo_x, novo_y)
            if len(self.checkpoints[indice]) >= 3:
                self.checkpoints[indice] = [float(cx), float(cy), float(self.checkpoints[indice][2])]
            else:
                self.checkpoints[indice] = [float(cx), float(cy)]
            return True
        return False
    
    def encontrar_checkpoint_proximo(self, x, y, raio=30):
        """Encontra checkpoint próximo à posição especificada"""
        melhor_indice = -1
        menor_distancia = float('inf')
        
        for i, cp in enumerate(self.checkpoints):
            cx, cy = cp[0], cp[1] if len(cp) >= 2 else (cp[0], cp[1])
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= raio and dist < menor_distancia:
                melhor_indice = i
                menor_distancia = dist
        
        return melhor_indice
    
    def alternar_modo_edicao(self):
        """Alterna entre modo de edição e modo normal"""
        self.modo_edicao = not self.modo_edicao
        self.checkpoint_selecionado = -1
    
    def processar_clique(self, x, y, camera=None):
        """Processa clique do mouse para edição de checkpoints"""
        if not self.modo_edicao or not camera:
            return
        
        mundo_x, mundo_y = camera.tela_para_mundo(x, y)
        indice = self.encontrar_checkpoint_proximo(mundo_x, mundo_y, 30)
        
        if indice >= 0:
            self.checkpoint_selecionado = indice
    
    def adicionar_checkpoint_na_posicao(self, x, y, camera):
        """Adiciona checkpoint na posição especificada, centralizado no tile"""
        if not self.modo_edicao or not camera:
            return
        
        mundo_x, mundo_y = camera.tela_para_mundo(x, y)
        self.adicionar_checkpoint(mundo_x, mundo_y)
        self.checkpoint_selecionado = len(self.checkpoints) - 1
    
    def processar_teclado(self, teclas):
        """Processa teclas para edição de checkpoints"""
        if not self.modo_edicao:
            return
        
        if teclas[pygame.K_DELETE] or teclas[pygame.K_BACKSPACE]:
            if self.checkpoint_selecionado >= 0:
                self.remover_checkpoint(self.checkpoint_selecionado)
                self.checkpoint_selecionado = -1
        
        if teclas[pygame.K_LEFT] and self.checkpoint_selecionado > 0:
            self.checkpoint_selecionado -= 1
        elif teclas[pygame.K_RIGHT] and self.checkpoint_selecionado < len(self.checkpoints) - 1:
            self.checkpoint_selecionado += 1
    
    def processar_teclas_f(self, teclas):
        """Processa teclas F para comandos do editor"""
        if teclas[pygame.K_F7]:
            self.modo_edicao = not self.modo_edicao
        
        if teclas[pygame.K_F5]:
            self.salvar_checkpoints()
        
        if teclas[pygame.K_F6]:
            self.carregar_checkpoints()
        
        if teclas[pygame.K_F8]:
            self.checkpoints = []
            self.checkpoint_selecionado = -1
    
    def desenhar(self, superficie, camera):
        """Desenha checkpoints na tela"""
        if not camera:
            return
        
        fonte = pygame.font.SysFont("consolas", 14, bold=True)
        
        for i, cp in enumerate(self.checkpoints):
            cx, cy = cp[0], cp[1] if len(cp) >= 2 else (cp[0], cp[1])
            screen_x, screen_y = camera.mundo_para_tela(cx, cy)
            
            if i == self.checkpoint_em_arraste:
                cor = (255, 165, 0)  # Laranja para em arraste
                raio = 25
                espessura = 4
            elif i == self.checkpoint_selecionado:
                cor = (255, 255, 0)  # Amarelo para selecionado
                raio = 20
                espessura = 3
            else:
                cor = (255, 0, 255)  # Magenta para normal
                raio = 15
                espessura = 2
            
            pygame.draw.circle(superficie, cor, (int(screen_x), int(screen_y)), raio, espessura)
            pygame.draw.circle(superficie, cor, (int(screen_x), int(screen_y)), 8)
            
            texto = fonte.render(str(i + 1), True, (255, 255, 255))
            texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
            superficie.blit(texto, texto_rect)
            
            if i < len(self.checkpoints) - 1:
                next_cx, next_cy = self.checkpoints[i + 1]
                next_screen_x, next_screen_y = camera.mundo_para_tela(next_cx, next_cy)
                pygame.draw.line(superficie, (255, 0, 255), 
                               (int(screen_x), int(screen_y)), 
                               (int(next_screen_x), int(next_screen_y)), 2)
        
        if self.modo_edicao:
            self.desenhar_interface_edicao(superficie, fonte)
    
    def desenhar_interface_edicao(self, superficie, fonte):
        """Desenha interface de edição de checkpoints"""
        overlay = pygame.Surface((300, 150), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        superficie.blit(overlay, (10, 10))
        
        nome_mapa = MAPAS_DISPONIVEIS[self.mapa_atual]["nome"]
        textos = [
            "MODO EDIÇÃO DE CHECKPOINTS",
            f"Mapa: {nome_mapa}",
            f"Total: {len(self.checkpoints)} checkpoints",
            "Clique: Adicionar/Mover",
            "DEL: Remover selecionado",
            "← →: Navegar",
            "F5: Salvar | F6: Carregar"
        ]
        
        for i, texto in enumerate(textos):
            cor = (255, 255, 0) if i == 0 else (255, 255, 255)
            superficie.blit(fonte.render(texto, True, cor), (15, 15 + i * 20))
        
        if self.checkpoint_em_arraste >= 0:
            cp = self.checkpoints[self.checkpoint_em_arraste]
            cx, cy = cp[0], cp[1] if len(cp) >= 2 else (cp[0], cp[1])
            texto_arraste = f"ARRÁSTANDO: {self.checkpoint_em_arraste + 1} ({cx:.1f}, {cy:.1f})"
            superficie.blit(fonte.render(texto_arraste, True, (255, 165, 0)), (15, 135))
        elif self.checkpoint_selecionado >= 0:
            cp = self.checkpoints[self.checkpoint_selecionado]
            cx, cy = cp[0], cp[1] if len(cp) >= 2 else (cp[0], cp[1])
            texto_selecionado = f"Selecionado: {self.checkpoint_selecionado + 1} ({cx:.1f}, {cy:.1f})"
            superficie.blit(fonte.render(texto_selecionado, True, (255, 255, 0)), (15, 135))
