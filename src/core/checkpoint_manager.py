import json
import os
import pygame
from config import DIR_PROJETO, MAPAS_DISPONIVEIS, MAPA_ATUAL, obter_caminho_checkpoints

class CheckpointManager:
    """Gerenciador de checkpoints com edição em tempo real para múltiplos mapas"""
    
    def __init__(self, mapa_atual=None):
        self.checkpoints = []
        self.modo_edicao = False
        self.checkpoint_selecionado = -1
        self.checkpoint_em_arraste = -1
        self.mapa_atual = mapa_atual or MAPA_ATUAL
        self.arquivo_checkpoints = obter_caminho_checkpoints()
        self.carregar_checkpoints()
    
    def trocar_mapa(self, novo_mapa):
        """Troca para um novo mapa e carrega seus checkpoints"""
        if novo_mapa in MAPAS_DISPONIVEIS:
            # Salvar checkpoints do mapa atual antes de trocar
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
        """Carrega checkpoints do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_checkpoints):
                with open(self.arquivo_checkpoints, 'r', encoding='utf-8') as f:
                    self.checkpoints = json.load(f)
                print(f"Carregados {len(self.checkpoints)} checkpoints do arquivo")
            else:
                print("Arquivo de checkpoints não encontrado, usando lista vazia")
                self.checkpoints = []
        except Exception as e:
            print(f"Erro ao carregar checkpoints: {e}")
            self.checkpoints = []
    
    def salvar_checkpoints(self):
        """Salva checkpoints no arquivo JSON"""
        try:
            with open(self.arquivo_checkpoints, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoints, f, indent=2, ensure_ascii=False)
            print(f"Salvos {len(self.checkpoints)} checkpoints no arquivo")
            return True
        except Exception as e:
            print(f"Erro ao salvar checkpoints: {e}")
            return False
    
    def adicionar_checkpoint(self, x, y):
        """Adiciona um novo checkpoint na posição especificada"""
        self.checkpoints.append([float(x), float(y)])
        print(f"Checkpoint adicionado: ({x:.1f}, {y:.1f})")
    
    def remover_checkpoint(self, indice):
        """Remove checkpoint pelo índice"""
        if 0 <= indice < len(self.checkpoints):
            checkpoint = self.checkpoints.pop(indice)
            print(f"Checkpoint removido: ({checkpoint[0]:.1f}, {checkpoint[1]:.1f})")
            return True
        return False
    
    def mover_checkpoint(self, indice, novo_x, novo_y):
        """Move checkpoint para nova posição"""
        if 0 <= indice < len(self.checkpoints):
            self.checkpoints[indice] = [float(novo_x), float(novo_y)]
            print(f"Checkpoint {indice} movido para: ({novo_x:.1f}, {novo_y:.1f})")
            return True
        return False
    
    def encontrar_checkpoint_proximo(self, x, y, raio=30):
        """Encontra checkpoint próximo à posição especificada"""
        for i, (cx, cy) in enumerate(self.checkpoints):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= raio:
                return i
        return -1
    
    def alternar_modo_edicao(self):
        """Alterna entre modo de edição e modo normal"""
        self.modo_edicao = not self.modo_edicao
        self.checkpoint_selecionado = -1
        print(f"Modo de edição: {'ATIVADO' if self.modo_edicao else 'DESATIVADO'}")
    
    def processar_clique(self, x, y, camera=None):
        """Processa clique do mouse para edição de checkpoints"""
        if not self.modo_edicao or not camera:
            return
        
        # Converter coordenadas da tela para mundo
        mundo_x, mundo_y = camera.tela_para_mundo(x, y)
        
        # Verificar se clicou em checkpoint existente
        indice = self.encontrar_checkpoint_proximo(mundo_x, mundo_y, 30)
        
        if indice >= 0:
            # Clicou em checkpoint existente - selecionar para mover
            self.checkpoint_selecionado = indice
            print(f"Checkpoint {indice} selecionado para mover")
        else:
            # Clicou em área vazia - adicionar novo checkpoint
            self.adicionar_checkpoint(mundo_x, mundo_y)
            self.checkpoint_selecionado = len(self.checkpoints) - 1
    
    def processar_teclado(self, teclas):
        """Processa teclas para edição de checkpoints"""
        if not self.modo_edicao:
            return
        
        # Teclas de edição
        if teclas[pygame.K_DELETE] or teclas[pygame.K_BACKSPACE]:
            if self.checkpoint_selecionado >= 0:
                self.remover_checkpoint(self.checkpoint_selecionado)
                self.checkpoint_selecionado = -1
        
        # Teclas de navegação
        if teclas[pygame.K_LEFT] and self.checkpoint_selecionado > 0:
            self.checkpoint_selecionado -= 1
        elif teclas[pygame.K_RIGHT] and self.checkpoint_selecionado < len(self.checkpoints) - 1:
            self.checkpoint_selecionado += 1
    
    def desenhar(self, superficie, camera):
        """Desenha checkpoints na tela"""
        if not camera:
            return
        
        fonte = pygame.font.SysFont("consolas", 14, bold=True)
        
        for i, (cx, cy) in enumerate(self.checkpoints):
            # Converter coordenadas do mundo para tela
            screen_x, screen_y = camera.mundo_para_tela(cx, cy)
            
            # Cor diferente para checkpoint selecionado e em arraste
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
            
            # Desenhar círculo
            pygame.draw.circle(superficie, cor, (int(screen_x), int(screen_y)), raio, espessura)
            pygame.draw.circle(superficie, cor, (int(screen_x), int(screen_y)), 8)
            
            # Número do checkpoint
            texto = fonte.render(str(i + 1), True, (255, 255, 255))
            texto_rect = texto.get_rect(center=(int(screen_x), int(screen_y)))
            superficie.blit(texto, texto_rect)
            
            # Linha conectando checkpoints
            if i < len(self.checkpoints) - 1:
                next_cx, next_cy = self.checkpoints[i + 1]
                next_screen_x, next_screen_y = camera.mundo_para_tela(next_cx, next_cy)
                pygame.draw.line(superficie, (255, 0, 255), 
                               (int(screen_x), int(screen_y)), 
                               (int(next_screen_x), int(next_screen_y)), 2)
        
        # Desenhar interface de edição
        if self.modo_edicao:
            self.desenhar_interface_edicao(superficie, fonte)
    
    def desenhar_interface_edicao(self, superficie, fonte):
        """Desenha interface de edição de checkpoints"""
        # Fundo semi-transparente
        overlay = pygame.Surface((300, 150), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        superficie.blit(overlay, (10, 10))
        
        # Textos de instrução
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
        
        # Checkpoint selecionado/em arraste
        if self.checkpoint_em_arraste >= 0:
            cx, cy = self.checkpoints[self.checkpoint_em_arraste]
            texto_arraste = f"ARRÁSTANDO: {self.checkpoint_em_arraste + 1} ({cx:.1f}, {cy:.1f})"
            superficie.blit(fonte.render(texto_arraste, True, (255, 165, 0)), (15, 135))
        elif self.checkpoint_selecionado >= 0:
            cx, cy = self.checkpoints[self.checkpoint_selecionado]
            texto_selecionado = f"Selecionado: {self.checkpoint_selecionado + 1} ({cx:.1f}, {cy:.1f})"
            superficie.blit(fonte.render(texto_selecionado, True, (255, 255, 0)), (15, 135))
