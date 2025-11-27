# src/core/narrative_system.py
"""Sistema de narrativa baseado em JSON para a campanha"""
import pygame
import json
import os
from typing import Dict, List, Optional, Any
from config import DIR_PROJETO, LARGURA, ALTURA

# Import lazy para evitar import circular
def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

def _get_t():
    """Importa função de tradução de forma lazy"""
    from core.i18n import t
    return t

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")

# Caminhos de assets
CAMINHO_BACKGROUNDS = os.path.join(DIR_PROJETO, "assets", "images", "ui")
CAMINHO_SPRITES_CHARACTERS = os.path.join(DIR_PROJETO, "assets", "images", "characters")

class NarrativeSystem:
    """Sistema de narrativa baseado em JSON"""
    
    def __init__(self):
        self.narrative_data = None
        self.current_chapter_id = None
        self.current_scene_id = None
        self.current_line_index = 0
        self.active = False
        
        # Estado do jogo (flags, variáveis)
        self.flags = {}
        self.variables = {}
        
        # Assets carregados
        self.backgrounds = {}
        self.character_sprites = {}
        
        # Estado de animação de texto
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 60.0  # Caracteres por segundo
        
        # Escolhas
        self.choices_visible = False
        self.selected_choice = 0
        
        # Sprites da cena atual
        self.scene_sprites = {}
        
        # Estado de time-skip (stage direction)
        self.time_skip_active = False
        self.time_skip_text = ""
        self.time_skip_fade_alpha = 0.0
        self.time_skip_fade_direction = 1  # 1 = fade in (escurecendo), -1 = fade out (clareando)
        self.time_skip_duration = 0.0
        self.time_skip_total_duration = 2.5  # Duração total do fade (segundos)
        
        # Carregar narrativa
        self.carregar_narrativa()
    
    def carregar_narrativa(self):
        """Carrega o arquivo JSON de narrativa"""
        try:
            with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
                self.narrative_data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar narrativa: {e}")
            self.narrative_data = {"chapters": []}
    
    def iniciar_capitulo(self, chapter_id: str):
        """Inicia um capítulo da narrativa"""
        if not self.narrative_data:
            return False
        
        # Encontrar capítulo
        chapter = None
        for ch in self.narrative_data.get("chapters", []):
            if ch.get("id") == chapter_id:
                chapter = ch
                break
        
        if not chapter:
            return False
        
        self.current_chapter_id = chapter_id
        scenes = chapter.get("scenes", [])
        if scenes:
            self.iniciar_cena(scenes[0].get("id"))
            return True
        return False
    
    def iniciar_cena(self, scene_id: str):
        """Inicia uma cena específica"""
        if not self.narrative_data or not self.current_chapter_id:
            return False
        
        # Encontrar cena no capítulo atual
        chapter = None
        for ch in self.narrative_data.get("chapters", []):
            if ch.get("id") == self.current_chapter_id:
                chapter = ch
                break
        
        if not chapter:
            return False
        
        scene = None
        for sc in chapter.get("scenes", []):
            if sc.get("id") == scene_id:
                scene = sc
                break
        
        if not scene:
            return False
        
        self.current_scene_id = scene_id
        self.current_line_index = 0
        self.active = True
        self.choices_visible = False
        
        # Ativar missão se houver uma associada a esta cena
        try:
            from core.missoes import gerenciador_missoes
            gerenciador_missoes.ativar_por_cena(scene_id)
            # Completar missão se esta cena for de conclusão
            gerenciador_missoes.completar_por_cena(scene_id)
        except:
            pass
        self.selected_choice = 0
        
        # Carregar background
        bg_name = scene.get("bg")
        if bg_name:
            self._carregar_background(bg_name)
        
        # Carregar sprites da cena
        sprites_config = scene.get("sprites", [])
        self._carregar_sprites_cena(sprites_config)
        
        # Iniciar primeira linha
        self._avancar_linha()
        
        return True
    
    def _carregar_background(self, bg_name: str):
        """Carrega um background"""
        if bg_name in self.backgrounds:
            return
        
        # Mapeamento de nomes de background para arquivos
        bg_mapping = {
            "bg_rua_chuva": "cidade.png",
            "bg_garagem": "oficina.png",
            "bg_garagem_noite": "oficina.png",  # TODO: criar versão noturna
            "bg_fosso_ferrugem": "fabrica.png",
            "bg_mapa_cidade": "cidade.png",
            "bg_santuario_montanha": "monte_akira.png",
            "bg_cobertura_corporativa": "predio_rex.png",
            "bg_beco_neon": "cidade.png",
            "bg_beco_sucata": "fabrica.png",
            "bg_apartamento_jogador": "casa.png",
            "bg_grid_circuito_urbano": "autodromo_fora.png",
            "bg_pit_circuito": "oficina.png",
            "bg_circuito_industrial": "fabrica.png",
            "bg_circuito_hibrido": "cidade.png",
            "bg_camarim_circuito": "predio_rex.png",
            "bg_podio": "autodromo_fora.png",
            "bg_torre_alta": "predio_rex.png"
        }
        
        filename = bg_mapping.get(bg_name, "cidade.png")
        bg_path = os.path.join(CAMINHO_BACKGROUNDS, filename)
        
        if os.path.exists(bg_path):
            try:
                self.backgrounds[bg_name] = pygame.image.load(bg_path).convert()
                # Redimensionar para caber na tela
                bg = self.backgrounds[bg_name]
                self.backgrounds[bg_name] = pygame.transform.scale(bg, (LARGURA, ALTURA))
            except Exception as e:
                print(f"Erro ao carregar background {bg_name}: {e}")
    
    def _carregar_sprites_cena(self, sprites_config: List[Dict]):
        """Carrega os sprites de uma cena"""
        self.scene_sprites = {}
        
        if not sprites_config:
            return
        
        for sprite_config in sprites_config:
            sprite_id = sprite_config.get("id")
            sprite_name = sprite_config.get("sprite")
            position = sprite_config.get("position", "left")
            
            if not sprite_id or not sprite_name:
                continue
            
            # Determinar pasta do personagem (mapeamento de nomes)
            character_mapping = {
                "crank": "crank",
                "boris": "boris",
                "pixel": "pixel",
                "akira": "akira",
                "barao": "barao",
                "rex": "rex",
                "glub": "glub",
                "slick": "slick"
            }
            character_folder = character_mapping.get(sprite_id, sprite_id)
            sprite_file = f"{sprite_name}.png"
            sprite_path = os.path.join(CAMINHO_SPRITES_CHARACTERS, character_folder, sprite_file)
            
            sprite_carregado = False
            
            # Tentar carregar o sprite específico primeiro
            if os.path.exists(sprite_path):
                try:
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    self.scene_sprites[sprite_id] = {
                        "sprite": sprite,
                        "position": position,
                        "sprite_name": sprite_name
                    }
                    sprite_carregado = True
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao carregar sprite {sprite_id}/{sprite_name}: {e}")
            
            # Se não carregou, tentar fallback: primeiro sprite disponível
            if not sprite_carregado:
                character_dir = os.path.join(CAMINHO_SPRITES_CHARACTERS, character_folder)
                if os.path.exists(character_dir):
                    files = [f for f in os.listdir(character_dir) if f.endswith('.png')]
                    if files:
                        fallback_path = os.path.join(character_dir, files[0])
                        try:
                            sprite = pygame.image.load(fallback_path).convert_alpha()
                            self.scene_sprites[sprite_id] = {
                                "sprite": sprite,
                                "position": position,
                                "sprite_name": files[0].replace('.png', '')
                            }
                            sprite_carregado = True
                        except Exception as e:
                            print(f"[NARRATIVA] Erro ao carregar sprite fallback: {e}")
    
    def _avancar_linha(self):
        """Avança para a próxima linha de diálogo"""
        if not self.current_scene_id or not self.current_chapter_id:
            return
        
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        lines = scene.get("lines", [])
        if self.current_line_index >= len(lines):
            # Verificar se há escolhas
            choices = scene.get("choices", [])
            if choices:
                self.choices_visible = True
                self.selected_choice = 0
            else:
                # Avançar para próxima cena
                self._avancar_cena()
            return
        
        line = lines[self.current_line_index]
        
        # Verificar se é uma stage direction (time-skip)
        line_type = line.get("type", "dialogue")
        if line_type == "stageDirection":
            # Processar time-skip
            texto = line.get("text", "")
            # Extrair texto do time-skip (remover [TIME-SKIP: ...])
            if texto.startswith("[TIME-SKIP:"):
                # Extrair conteúdo entre os colchetes
                inicio = texto.find(":") + 1
                fim = texto.rfind("]")
                if fim > inicio:
                    self.time_skip_text = texto[inicio:fim].strip()
                else:
                    self.time_skip_text = texto.replace("[TIME-SKIP:", "").replace("]", "").strip()
            else:
                self.time_skip_text = texto
            
            # Iniciar fade
            self.time_skip_active = True
            self.time_skip_fade_alpha = 0.0
            self.time_skip_fade_direction = 1  # Começar escurecendo
            self.time_skip_duration = 0.0
            
            # Tocar SFX se mencionado no texto
            texto_lower = self.time_skip_text.lower()
            # TODO: Implementar sistema de SFX baseado em palavras-chave
            # Por enquanto, apenas marcar que o time-skip está ativo
            
            # Avançar para próxima linha após processar
            self.current_line_index += 1
            return
        
        # Verificar condições
        conditions = line.get("conditions", [])
        if conditions and not self._verificar_condicoes(conditions):
            self.current_line_index += 1
            self._avancar_linha()
            return
        
        # Atualizar sprite se especificado
        sprite_name = line.get("sprite")
        speaker = line.get("speaker", "")
        if sprite_name:
            # Atualizar sprite do personagem
            character_id = speaker.lower()
            if character_id in self.scene_sprites:
                # Mapeamento de pastas
                character_mapping = {
                    "crank": "crank",
                    "boris": "boris",
                    "pixel": "pixel",
                    "akira": "akira",
                    "barao": "barao",
                    "rex": "rex",
                    "glub": "glub",
                    "slick": "slick"
                }
                character_folder = character_mapping.get(character_id, character_id)
                # Recarregar sprite com novo nome
                sprite_path = os.path.join(
                    CAMINHO_SPRITES_CHARACTERS, 
                    character_folder, 
                    f"{sprite_name}.png"
                )
                if os.path.exists(sprite_path):
                    try:
                        self.scene_sprites[character_id]["sprite"] = pygame.image.load(sprite_path).convert_alpha()
                        self.scene_sprites[character_id]["sprite_name"] = sprite_name
                    except:
                        pass
        
        # Iniciar animação de texto (com suporte a tradução)
        texto = line.get("text", "")
        # Se o texto começa com "narrative.", é uma chave de tradução
        if texto.startswith("narrative."):
            t = _get_t()
            texto = t(texto)
        self._iniciar_animacao_texto(texto)
    
    def _avancar_cena(self):
        """Avança para a próxima cena"""
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        next_scene_id = scene.get("nextSceneId")
        if next_scene_id:
            self.iniciar_cena(next_scene_id)
        else:
            # Fim da cena/capítulo
            # Marcar capítulo como completo se houver
            if self.current_chapter_id:
                try:
                    from core.progresso import gerenciador_progresso
                    gerenciador_progresso.marcar_capitulo_completo(self.current_chapter_id)
                except:
                    pass
            self.active = False
    
    def obter_trigger_da_cena(self, scene_id: str = None) -> Optional[Dict]:
        """Obtém o trigger de uma cena específica ou da cena atual"""
        if scene_id is None:
            scene = self._obter_cena_atual()
        else:
            # Buscar cena específica
            scene = None
            if self.narrative_data:
                for chapter in self.narrative_data.get("chapters", []):
                    for s in chapter.get("scenes", []):
                        if s.get("id") == scene_id:
                            scene = s
                            break
                    if scene:
                        break
        
        if not scene:
            return None
        
        # Verificar se a cena tem trigger
        trigger = scene.get("gameplayTrigger")
        if trigger:
            return {
                "trigger": trigger.get("trigger"),
                "params": trigger.get("params", {})
            }
        
        return None
    
    def obter_trigger_atual(self) -> Optional[Dict]:
        """Obtém o trigger da cena atual"""
        return self.obter_trigger_da_cena()
    
    def _obter_cena_atual(self) -> Optional[Dict]:
        """Obtém a cena atual"""
        if not self.narrative_data or not self.current_chapter_id or not self.current_scene_id:
            return None
        
        chapter = None
        for ch in self.narrative_data.get("chapters", []):
            if ch.get("id") == self.current_chapter_id:
                chapter = ch
                break
        
        if not chapter:
            return None
        
        for scene in chapter.get("scenes", []):
            if scene.get("id") == self.current_scene_id:
                return scene
        
        return None
    
    def _verificar_condicoes(self, conditions: List[str]) -> bool:
        """Verifica se as condições são satisfeitas"""
        for condition in conditions:
            if "=" in condition:
                key, value = condition.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Verificar flags
                if key.startswith("has") or key.startswith("wants") or key.startswith("told") or key.startswith("set"):
                    flag_value = self.flags.get(key, False)
                    if value.lower() == "true":
                        if not flag_value:
                            return False
                    elif value.lower() == "false":
                        if flag_value:
                            return False
                # Verificar variáveis
                elif key in self.variables:
                    if str(self.variables[key]) != value:
                        return False
                else:
                    return False
        
        return True
    
    def _iniciar_animacao_texto(self, texto: str):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
    
    def _atualizar_animacao_texto(self, dt: float):
        """Atualiza animação de texto letra por letra"""
        if not self.texto_completo:
            return
        
        if len(self.texto_exibido) < len(self.texto_completo):
            self.tempo_animacao += dt
            caracteres_para_adicionar = int(self.tempo_animacao * self.velocidade_texto)
            if caracteres_para_adicionar > len(self.texto_exibido):
                self.texto_exibido = self.texto_completo[:caracteres_para_adicionar]
    
    def processar_eventos(self, eventos: List[pygame.event.Event]) -> Optional[str]:
        """Processa eventos do sistema de narrativa"""
        if not self.active:
            return None
        
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Botão esquerdo
                    if self.choices_visible:
                        # Processar clique em escolha
                        mouse_x, mouse_y = evento.pos
                        scene = self._obter_cena_atual()
                        if scene:
                            choices = scene.get("choices", [])
                            choice_height = 60
                            choice_y_start = ALTURA - 200 - (len(choices) * choice_height)
                            
                            for i, choice in enumerate(choices):
                                choice_y = choice_y_start + i * choice_height
                                if choice_y <= mouse_y <= choice_y + choice_height:
                                    self._processar_escolha(choice)
                                    return None
                    else:
                        # Durante time-skip, não processar cliques (aguardar fade completar)
                        if self.time_skip_active:
                            return None
                        # Pular animação de texto ou avançar linha
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self.texto_exibido = self.texto_completo
                        else:
                            self.current_line_index += 1
                            self._avancar_linha()
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    if self.choices_visible:
                        # Selecionar escolha atual
                        scene = self._obter_cena_atual()
                        if scene:
                            choices = scene.get("choices", [])
                            if 0 <= self.selected_choice < len(choices):
                                self._processar_escolha(choices[self.selected_choice])
                    else:
                        # Durante time-skip, não processar teclas (aguardar fade completar)
                        if self.time_skip_active:
                            return None
                        # Pular animação de texto ou avançar linha
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self.texto_exibido = self.texto_completo
                        else:
                            self.current_line_index += 1
                            self._avancar_linha()
                
                elif evento.key == pygame.K_UP or evento.key == pygame.K_w:
                    if self.choices_visible:
                        scene = self._obter_cena_atual()
                        if scene:
                            choices = scene.get("choices", [])
                            self.selected_choice = (self.selected_choice - 1) % len(choices)
                
                elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                    if self.choices_visible:
                        scene = self._obter_cena_atual()
                        if scene:
                            choices = scene.get("choices", [])
                            self.selected_choice = (self.selected_choice + 1) % len(choices)
                
                elif evento.key == pygame.K_ESCAPE:
                    self.active = False
                    return "fechado"
        
        return None
    
    def _processar_escolha(self, choice: Dict):
        """Processa uma escolha do jogador"""
        # Processar efeitos
        effects = choice.get("effects", [])
        for effect in effects:
            self._processar_efeito(effect)
        
        # Avançar para próxima cena
        next_scene_id = choice.get("nextSceneId")
        if next_scene_id:
            self.iniciar_cena(next_scene_id)
        else:
            self.choices_visible = False
            self.current_line_index += 1
            self._avancar_linha()
    
    def _processar_efeito(self, effect: str):
        """Processa um efeito (flag, desbloqueio, etc.)"""
        if effect.startswith("setFlag:"):
            flag_name = effect.split(":", 1)[1]
            self.flags[flag_name] = True
        elif effect.startswith("unlockLocation:"):
            location = effect.split(":", 1)[1]
            # Desbloquear localização no mapa
            try:
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_localizacoes.desbloquear(location)
                print(f"Desbloqueando localização: {location}")
            except:
                print(f"Desbloqueando localização: {location}")
        elif effect.startswith("unlockRace:") or effect.startswith("unlockRaceSet:"):
            race = effect.split(":", 1)[1]
            # Processar unlockRaceSet para desbloquear localização relacionada
            if effect.startswith("unlockRaceSet:"):
                try:
                    from core.mapa_locations import gerenciador_localizacoes
                    gerenciador_localizacoes.processar_efeito_narrativa(effect)
                except:
                    pass
            print(f"Desbloqueando corrida: {race}")
        elif effect.startswith("openShop:"):
            shop = effect.split(":", 1)[1]
            # TODO: abrir loja
            print(f"Abrindo loja: {shop}")
        elif effect.startswith("openGarage:"):
            garage_action = effect.split(":", 1)[1]
            # TODO: abrir garagem
            print(f"Abrindo garagem: {garage_action}")
        elif effect.startswith("addMoney:"):
            amount_str = effect.split(":", 1)[1]
            # TODO: adicionar dinheiro
            print(f"Adicionando dinheiro: {amount_str}")
        elif effect.startswith("mentionLocation:"):
            # Tornar localização visível (mas ainda bloqueada)
            location = effect.split(":", 1)[1]
            try:
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_localizacoes.tornar_visivel(location)
                print(f"Tornando localização visível: {location}")
            except:
                print(f"Tornando localização visível: {location}")
    
    def atualizar(self, dt: float):
        """Atualiza o sistema de narrativa"""
        if not self.active:
            return
        
        # Atualizar time-skip se ativo
        if self.time_skip_active:
            self.time_skip_duration += dt
            fade_speed = 1.0 / (self.time_skip_total_duration / 2.0)  # Metade do tempo para fade in, metade para fade out
            
            if self.time_skip_fade_direction == 1:  # Fade in (escurecendo)
                self.time_skip_fade_alpha += fade_speed * dt
                if self.time_skip_fade_alpha >= 1.0:
                    self.time_skip_fade_alpha = 1.0
                    # Aguardar um pouco antes de começar a clarear
                    if self.time_skip_duration >= self.time_skip_total_duration / 2.0:
                        self.time_skip_fade_direction = -1  # Começar a clarear
            else:  # Fade out (clareando)
                self.time_skip_fade_alpha -= fade_speed * dt
                if self.time_skip_fade_alpha <= 0.0:
                    self.time_skip_fade_alpha = 0.0
                    # Time-skip completo, avançar para próxima linha
                    self.time_skip_active = False
                    self._avancar_linha()
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar(self, tela: pygame.Surface):
        """Desenha a cena atual"""
        if not self.active:
            return
        
        render_text = _get_render_text()
        
        # Desenhar background
        scene = self._obter_cena_atual()
        if scene:
            bg_name = scene.get("bg")
            if bg_name and bg_name in self.backgrounds:
                tela.blit(self.backgrounds[bg_name], (0, 0))
            else:
                # Overlay escuro como fallback
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                tela.blit(overlay, (0, 0))
        
        # Desenhar sprites dos personagens
        for sprite_id, sprite_data in self.scene_sprites.items():
            sprite = sprite_data["sprite"]
            position = sprite_data["position"]
            
            # Verificar se o sprite é válido
            if sprite is None:
                print(f"ERRO: Sprite {sprite_id} é None!")
                continue
            
            # Calcular escala baseada em tamanhos máximos (similar ao sistema do Crank)
            sprite_original_w, sprite_original_h = sprite.get_size()
            if sprite_original_w == 0 or sprite_original_h == 0:
                print(f"[NARRATIVA] ERRO: Sprite {sprite_id} tem tamanho inválido ({sprite_original_w}, {sprite_original_h})")
                continue
            
            # Limitar tamanho máximo (mesmo que o Crank usa)
            sprite_altura_max = 400
            sprite_largura_max = 350
            
            # Calcular escala mantendo proporção
            escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
            escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
            escala = min(escala_w, escala_h, 1.0)  # Não aumentar além do original
            
            sprite_w = int(sprite_original_w * escala)
            sprite_h = int(sprite_original_h * escala)
            sprite_scaled = pygame.transform.scale(sprite, (sprite_w, sprite_h))
            
            # Calcular posição (alinhado com o chão, acima da caixa de diálogo)
            caixa_altura = 10
            caixa_y = ALTURA - caixa_altura - 50
            sprite_y_base = caixa_y - sprite_h - 20  # 20px acima da caixa de diálogo
            
            if position == "left":
                sprite_x = 50
                sprite_y = sprite_y_base
            elif position == "right":
                sprite_x = LARGURA - sprite_w - 500   # Direita da tela, 10px da borda (mais próximo)
                sprite_y = sprite_y_base
            elif position == "center":
                sprite_x = LARGURA // 2 - sprite_w // 2  # Centro horizontal
                sprite_y = sprite_y_base
            elif position == "hud":
                # Para HUD (como Pixel), posição diferente
                sprite_x = LARGURA // 2 - sprite_w // 2
                sprite_y = 100
            else:
                # Fallback: mesma posição do left
                sprite_x = 50
                sprite_y = ALTURA // 2 - sprite_h // 2 - 50
            
            # Desenhar sprite
            tela.blit(sprite_scaled, (sprite_x, sprite_y))
        
        # Desenhar time-skip se ativo (sobrepõe tudo)
        if self.time_skip_active:
            # Overlay escuro com fade
            overlay_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            alpha = int(self.time_skip_fade_alpha * 255)
            overlay_escuro.fill((0, 0, 0, alpha))
            tela.blit(overlay_escuro, (0, 0))
            
            # Texto do time-skip (centralizado, visível quando escuro)
            if self.time_skip_text and self.time_skip_fade_alpha > 0.3:
                # Calcular opacidade do texto (mais visível quando a tela está escura)
                texto_alpha = min(1.0, (self.time_skip_fade_alpha - 0.3) / 0.7) if self.time_skip_fade_alpha > 0.3 else 0.0
                texto_cor = (255, 255, 200)  # Amarelo claro
                
                # Renderizar texto centralizado
                texto_render = render_text(self.time_skip_text, 20, texto_cor, bold=True, pixel_style=True)
                texto_x = (LARGURA - texto_render.get_width()) // 2
                texto_y = ALTURA // 2
                
                # Fundo semi-transparente para o texto
                if texto_alpha > 0:
                    fundo_texto = pygame.Surface((texto_render.get_width() + 40, texto_render.get_height() + 20), pygame.SRCALPHA)
                    fundo_alpha = int(texto_alpha * 100)
                    fundo_texto.fill((0, 0, 0, fundo_alpha))
                    tela.blit(fundo_texto, (texto_x - 20, texto_y - 10))
                    tela.blit(texto_render, (texto_x, texto_y))
        
        # Desenhar caixa de diálogo (não desenhar durante time-skip)
        if not self.time_skip_active:
            if not self.choices_visible:
                self._desenhar_dialogo(tela, render_text)
            else:
                self._desenhar_escolhas(tela, render_text)
    
    def _desenhar_dialogo(self, tela: pygame.Surface, render_text):
        """Desenha a caixa de diálogo"""
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        lines = scene.get("lines", [])
        if self.current_line_index >= len(lines):
            return
        
        line = lines[self.current_line_index]
        speaker = line.get("speaker", "")
        
        # Caixa de diálogo
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        # Fundo da caixa
        overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay_caixa.fill((0, 0, 0, 200))
        tela.blit(overlay_caixa, (caixa_x, caixa_y))
        
        # Borda
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Nome do falante (com tradução)
        t = _get_t()
        if speaker == "NARRATOR":
            nome = t("narrative.narrator")
        elif speaker == "SISTEMA":
            nome = t("narrative.system")
        else:
            # Tentar traduzir nome do personagem
            nome_key = f"narrative.characters.{speaker.lower()}"
            nome_traduzido = t(nome_key)
            # Se retornou a chave, usar o nome original
            if nome_traduzido == nome_key:
                # Se não encontrou a tradução, usar o nome em maiúsculas
                nome = speaker.upper() if speaker else "???"
            else:
                nome = nome_traduzido
        nome_texto = render_text(nome, 20, (255, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Texto do diálogo com quebra de linha
        if self.texto_exibido:
            palavras = self.texto_exibido.split(' ')
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                teste_render = render_text(teste_linha, 18, (255, 255, 255), bold=False, pixel_style=True)
                if teste_render.get_width() <= caixa_largura - 40:
                    linha_atual = teste_linha
                else:
                    if linha_atual:
                        linhas.append(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual)
            
            y_texto = caixa_y + 50
            for linha in linhas:
                linha_render = render_text(linha, 18, (255, 255, 255), bold=False, pixel_style=True)
                tela.blit(linha_render, (caixa_x + 20, y_texto))
                y_texto += 25
        
        # Indicador de avanço (com tradução)
        if len(self.texto_exibido) >= len(self.texto_completo):
            t = _get_t()
            indicador_texto = t("narrative.press_to_continue")
            indicador = render_text(indicador_texto, 14, (200, 200, 200), bold=False, pixel_style=True)
            tela.blit(indicador, (caixa_x + caixa_largura - 400, caixa_y + caixa_altura - 30))
    
    def _desenhar_escolhas(self, tela: pygame.Surface, render_text):
        """Desenha as escolhas disponíveis"""
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        choices = scene.get("choices", [])
        if not choices:
            return
        
        choice_height = 60
        choice_y_start = ALTURA - 200 - (len(choices) * choice_height)
        
        t = _get_t()
        for i, choice in enumerate(choices):
            choice_y = choice_y_start + i * choice_height
            choice_text = choice.get("text", "")
            # Se o texto começa com "narrative.", é uma chave de tradução
            if choice_text.startswith("narrative."):
                choice_text = t(choice_text)
            
            # Cor baseada na seleção
            if i == self.selected_choice:
                cor = (255, 255, 255)
                cor_bg = (100, 100, 200)
            else:
                cor = (200, 200, 200)
                cor_bg = (50, 50, 100)
            
            # Fundo da escolha
            choice_rect = pygame.Rect(50, choice_y, LARGURA - 100, choice_height)
            pygame.draw.rect(tela, cor_bg, choice_rect)
            pygame.draw.rect(tela, cor, choice_rect, 2)
            
            # Texto
            texto_render = render_text(choice_text, 20, cor, bold=True, pixel_style=True)
            texto_x = 50 + (choice_rect.width - texto_render.get_width()) // 2
            tela.blit(texto_render, (texto_x, choice_y + (choice_height - texto_render.get_height()) // 2))
    
    def fechar(self):
        """Fecha o sistema de narrativa"""
        self.active = False

# Instância global
narrative_system = NarrativeSystem()

