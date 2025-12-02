# src/core/narrative_system.py
"""Sistema de narrativa baseado em JSON para a campanha"""
import pygame
import json
import os
from typing import Dict, List, Optional, Any
from config import DIR_PROJETO, LARGURA, ALTURA
def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

def _get_t():
    """Importa função de tradução de forma lazy"""
    from core.i18n import t
    return t

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")

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
        
        self.flags = {}
        self.variables = {}
        
        self.backgrounds = {}
        self.character_sprites = {}
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 60.0
        
        self.choices_visible = False
        self.selected_choice = 0
        
        self.scene_sprites = {}
        
        self.time_skip_active = False
        self.time_skip_text = ""
        self.time_skip_fade_alpha = 0.0
        self.time_skip_fade_direction = 1
        self.time_skip_duration = 0.0
        self.time_skip_total_duration = 7.5
        
        self.scene_transition_active = False
        self.scene_transition_fade_alpha = 0.0
        self.scene_transition_fade_direction = 1
        self.scene_transition_duration = 0.0
        self.scene_transition_next_scene_id = None
        self.scene_transition_tempo_fade = 0.3
        self.scene_transition_tempo_escuro = 0.1
        self.scene_transition_tempo_clarear = 0.3
        
        self.scenario_hitboxes = {}
        self.hover_hitbox_atual = None
        self.hover_sprite_atual = None
        
        # Sistema de créditos (auto-avanço)
        self.creditos_auto_advance = False
        self.creditos_tempo_mostrado = 0.0
        self.creditos_tempo_por_cena = 3.0  # 3 segundos por cena de créditos
        self.creditos_texto_fade_alpha = 0.0
        self.creditos_texto_fade_direction = 1  # 1 = aparecendo, -1 = desaparecendo
        
        # Sistema de gatilhos dinâmicos
        self.pending_scenes = []  # Cenas aguardando gatilhos
        self.scenes_visited = set()  # Cenas já visitadas
        self.chapter_start_time = {}  # Tempo de início de cada capítulo
        
        # Sistema de gatilhos dinâmicos
        self.pending_scenes = []  # Cenas aguardando gatilhos
        self.scenes_visited = set()  # Cenas já visitadas
        self.chapter_start_time = {}  # Tempo de início de cada capítulo
        
        self.carregar_narrativa()
        self.carregar_hitboxes_cenarios()
    
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
        
        chapter = None
        for ch in self.narrative_data.get("chapters", []):
            if ch.get("id") == chapter_id:
                chapter = ch
                break
        
        if not chapter:
            return False
        
        self.current_chapter_id = chapter_id
        import time
        self.chapter_start_time[chapter_id] = time.time()
        
        scenes = chapter.get("scenes", [])
        if scenes:
            # Se estamos no Capítulo 2, verificar se já decidimos sobre o empréstimo
            if chapter_id == "ch2":
                from core.progresso import gerenciador_progresso
                # Se o Barão já foi visto (nome revelado), significa que já passamos pela decisão
                if gerenciador_progresso.barao_nome_revelado:
                    # Se o Pixel já foi visto, ir direto para a cena do Boris
                    if gerenciador_progresso.pixel_primeira_aparicao_mostrada:
                        # Procurar a cena ch2_8_boris_unlock_offer
                        for scene in scenes:
                            if scene.get("id") == "ch2_8_boris_unlock_offer":
                                print(f"[NARRATIVA] Capítulo 2: Pulando para cena do Boris (empréstimo já decidido, Pixel já visto)")
                                return self._iniciar_cena_sem_transicao(scene.get("id"))
                    else:
                        # Ir para a cena do Pixel
                        for scene in scenes:
                            if scene.get("id") == "ch2_6_pixel_reacts":
                                print(f"[NARRATIVA] Capítulo 2: Pulando para cena do Pixel (empréstimo já decidido)")
                                return self._iniciar_cena_sem_transicao(scene.get("id"))
            
            # Se estamos no Capítulo 3, verificar se já completamos o cinturão
            if chapter_id == "ch3":
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                # Se a missão m10 já foi completada, podemos pular para a cena inicial do capítulo 3
                if gerenciador_missoes.esta_completa("m10_portoes_do_cinturao"):
                    print(f"[NARRATIVA] Capítulo 3: Cinturão já completado, iniciando normalmente")
            
            # Iniciar normalmente pela primeira cena
            self.iniciar_cena(scenes[0].get("id"))
            return True
        return False
    
    def iniciar_cena(self, scene_id: str):
        """Inicia uma cena específica (com transição de fade se já houver uma cena ativa)"""
        if self.current_scene_id and self.current_scene_id != scene_id:
            self.scene_transition_active = True
            self.scene_transition_fade_alpha = 0.0
            self.scene_transition_fade_direction = 1  # Começar escurecendo
            self.scene_transition_duration = 0.0
            self.scene_transition_next_scene_id = scene_id
            return True
        
        return self._iniciar_cena_sem_transicao(scene_id)
    
    def _iniciar_cena_sem_transicao(self, scene_id: str, cenas_visitadas=None):
        """Inicia uma cena específica sem transição (usado internamente durante fade)"""
        if not self.narrative_data or not self.current_chapter_id:
            return False
        
        # Prevenir loops infinitos rastreando cenas já visitadas nesta cadeia
        if cenas_visitadas is None:
            cenas_visitadas = set()
        
        if scene_id in cenas_visitadas:
            print(f"[NARRATIVA] Loop detectado! Cena {scene_id} já foi visitada nesta cadeia. Desativando narrativa.")
            self.active = False
            return False
        
        cenas_visitadas.add(scene_id)
        
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
        
        # Verificar se a cena já foi vista (primeira aparição de personagens)
        from core.progresso import gerenciador_progresso
        
        # Mapeamento de cenas para flags de progresso
        cena_para_flag = {
            "ch1_3_meet_boris": ("boris_primeira_aparicao_mostrada", "boris"),
            "ch1_7_pixel_intro": ("pixel_primeira_aparicao_mostrada", "pixel"),
            "ch1_1_crank_garage_intro": ("crank_tutorial_mostrado", "crank"),
        }
        
        if scene_id in cena_para_flag:
            flag_name, personagem = cena_para_flag[scene_id]
            flag_value = getattr(gerenciador_progresso, flag_name, False)
            if flag_value:
                print(f"[NARRATIVA] Cena {scene_id} já foi vista (flag {flag_name}=True), pulando...")
                # Se a cena já foi vista, verificar se há próxima cena ou trigger
                if scene.get("nextSceneId"):
                    next_scene_id = scene.get("nextSceneId")
                    print(f"[NARRATIVA] Avançando para próxima cena: {next_scene_id}")
                    # Passar o conjunto de cenas visitadas para evitar loops
                    return self._iniciar_cena_sem_transicao(next_scene_id, cenas_visitadas)
                elif scene.get("gameplayTrigger"):
                    # Se tem trigger, processar o trigger diretamente
                    trigger = scene.get("gameplayTrigger")
                    print(f"[NARRATIVA] Cena já vista, processando trigger: {trigger}")
                    # Retornar o trigger para ser processado
                    return {
                        "trigger": trigger.get("trigger"),
                        "params": trigger.get("params", {})
                    }
                else:
                    # Cena já vista e não há próxima, desativar narrativa
                    print(f"[NARRATIVA] Cena {scene_id} já vista e não há próxima cena, desativando narrativa")
                    self.active = False
                    return False
        
        self.current_scene_id = scene_id
        self.current_line_index = 0
        self.active = True
        self.choices_visible = False
        
        # Desativar NPCs quando a narrativa está ativa para evitar sobreposição
        try:
            from core.pixel import pixel
            from core.crank import crank
            from core.akira import akira
            pixel.ativo = False
            crank.ativo = False
            # Não desativar Akira aqui pois ela pode ser usada na narrativa
            print(f"[NARRATIVA] NPCs desativados ao iniciar cena {scene_id}")
        except Exception as e:
            print(f"[NARRATIVA] Erro ao desativar NPCs: {e}")
        
        try:
            from core.missoes import gerenciador_missoes
            # Ativar missões que devem ser ativadas nesta cena
            gerenciador_missoes.ativar_por_cena(scene_id)
            # Não completar aqui - será completado quando a cena terminar
        except:
            pass
        self.selected_choice = 0
        
        # Processar efeitos da cena (ex: unlockLocation, unlockRace, etc.)
        effects = scene.get("effects", [])
        if effects:
            print(f"[NARRATIVA] Processando {len(effects)} efeito(s) da cena {scene_id}")
            for effect in effects:
                self._processar_efeito(effect)
        
        bg_name = scene.get("bg")
        if bg_name:
            self._carregar_background(bg_name)
        
        sprites_config = scene.get("sprites", [])
        self._carregar_sprites_cena(sprites_config)
        
        self._avancar_linha()
        
        return True
    
    def carregar_hitboxes_cenarios(self):
        """Carrega hitboxes de cenários do arquivo JSON"""
        caminho_hitboxes = os.path.join(DIR_PROJETO, "data", "scenario_hitboxes.json")
        if os.path.exists(caminho_hitboxes):
            try:
                with open(caminho_hitboxes, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for cenario, hitboxes in data.items():
                        self.scenario_hitboxes[cenario] = []
                        for hb in hitboxes:
                            if hb.get("hover_sprite"):
                                hover_path = hb["hover_sprite"].replace("\\", "/")
                                hb["hover_sprite"] = hover_path
                            self.scenario_hitboxes[cenario].append(hb)
                print(f"✓ Carregadas hitboxes de {len(self.scenario_hitboxes)} cenários")
            except Exception as e:
                print(f"Erro ao carregar hitboxes de cenários: {e}")
                self.scenario_hitboxes = {}
        else:
            self.scenario_hitboxes = {}
    
    def _obter_arquivo_cenario(self, bg_name: str) -> Optional[str]:
        """Obtém o nome do arquivo do cenário baseado no bg_name"""
        bg_mapping = {
            "bg_rua_chuva": "cidade.png",
            "bg_garagem": "oficina.png",
            "bg_garagem_noite": "oficina.png",
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
            "bg_torre_alta": "predio_rex.png",
            "iate_barao_dia": "iate_barao_dia.png",
            "iate_barao_noite": "iate_barao_noite.png",
            "nissan_350z_inicial_noite": "nissan_350z_inicial_noite.png"
        }
        return bg_mapping.get(bg_name)
    
    def _verificar_hover_hitbox(self, mouse_x: int, mouse_y: int):
        """Verifica se o mouse está sobre uma hitbox e atualiza o hover"""
        scene = self._obter_cena_atual()
        if not scene:
            self.hover_hitbox_atual = None
            self.hover_sprite_atual = None
            return
        
        bg_name = scene.get("bg")
        if not bg_name:
            self.hover_hitbox_atual = None
            self.hover_sprite_atual = None
            return
        
        arquivo_cenario = self._obter_arquivo_cenario(bg_name)
        if not arquivo_cenario or arquivo_cenario not in self.scenario_hitboxes:
            self.hover_hitbox_atual = None
            self.hover_sprite_atual = None
            return
        
        hitboxes = self.scenario_hitboxes[arquivo_cenario]
        hitbox_encontrada = None
        
        for hb in hitboxes:
            rect = pygame.Rect(hb["x"], hb["y"], hb["largura"], hb["altura"])
            if rect.collidepoint(mouse_x, mouse_y):
                hitbox_encontrada = hb
                break
        
        if hitbox_encontrada != self.hover_hitbox_atual:
            self.hover_hitbox_atual = hitbox_encontrada
            self.hover_sprite_atual = None
            
            if hitbox_encontrada and hitbox_encontrada.get("hover_sprite"):
                from config import obter_caminho_hover_dia_noite
                hover_path_original = os.path.join(DIR_PROJETO, hitbox_encontrada["hover_sprite"])
                hover_path = obter_caminho_hover_dia_noite(hover_path_original)
                if os.path.exists(hover_path):
                    try:
                        self.hover_sprite_atual = pygame.image.load(hover_path).convert_alpha()
                        if self.hover_sprite_atual:
                            self.hover_sprite_atual = pygame.transform.scale(
                                self.hover_sprite_atual, (LARGURA, ALTURA)
                            )
                    except Exception as e:
                        print(f"Erro ao carregar sprite de hover: {e}")
                        self.hover_sprite_atual = None
                else:
                    print(f"AVISO: Sprite de hover não encontrado: {hover_path}")
    
    def _carregar_background(self, bg_name: str):
        """Carrega um background"""
        if bg_name in self.backgrounds:
            return
        
        arquivo_cenario = self._obter_arquivo_cenario(bg_name)
        
        # Se o bg_name já especifica dia/noite explicitamente (ex: "iate_barao_dia", "iate_barao_noite")
        # E não está no mapeamento (ou seja, é um arquivo específico), usar diretamente
        if (bg_name.endswith("_dia") or bg_name.endswith("_noite")) and not arquivo_cenario:
            # Se não encontrou no mapeamento, usar o bg_name como nome do arquivo
            bg_path = os.path.join(CAMINHO_BACKGROUNDS, f"{bg_name}.png")
        else:
            # Para backgrounds mapeados (ex: bg_garagem_noite -> oficina.png), usar sistema dia/noite
            if not arquivo_cenario:
                arquivo_cenario = "cidade.png"
            
            from config import obter_caminho_sprite_dia_noite, obter_estado_dia_noite
            nome_base = os.path.splitext(arquivo_cenario)[0]
            
            sprites_dia_noite = ["cidade", "oficina", "casa", "monte_akira", "autodromo_fora", "fabrica", "predio_rex", "iate_barao"]
            
            if nome_base in sprites_dia_noite:
                # Determinar se é dia ou noite baseado no bg_name
                # Se o bg_name termina com _noite ou _dia, usar isso para determinar o arquivo
                if bg_name.endswith("_noite"):
                    # Forçar noite para backgrounds que especificam _noite
                    # Criar caminho manualmente para noite
                    bg_path = os.path.join(CAMINHO_BACKGROUNDS, f"{nome_base}_noite.png")
                    if not os.path.exists(bg_path):
                        # Se não existe _noite, tentar o padrão
                        bg_path = obter_caminho_sprite_dia_noite(nome_base, CAMINHO_BACKGROUNDS)
                elif bg_name.endswith("_dia"):
                    # Forçar dia para backgrounds que especificam _dia
                    # Criar caminho manualmente para dia
                    bg_path = os.path.join(CAMINHO_BACKGROUNDS, f"{nome_base}_dia.png")
                    if not os.path.exists(bg_path):
                        # Se não existe _dia, tentar o padrão
                        bg_path = obter_caminho_sprite_dia_noite(nome_base, CAMINHO_BACKGROUNDS)
                else:
                    # Usar estado atual do jogo
                    bg_path = obter_caminho_sprite_dia_noite(nome_base, CAMINHO_BACKGROUNDS)
                
                estado_dia_noite = obter_estado_dia_noite()
                print(f"[NARRATIVA] Carregando background {bg_name} -> {nome_base} ({estado_dia_noite}): {bg_path}")
            else:
                bg_path = os.path.join(CAMINHO_BACKGROUNDS, arquivo_cenario)
                print(f"[NARRATIVA] Carregando background {bg_name} -> {arquivo_cenario}: {bg_path}")
        
        if os.path.exists(bg_path):
            try:
                self.backgrounds[bg_name] = pygame.image.load(bg_path).convert()
                bg = self.backgrounds[bg_name]
                self.backgrounds[bg_name] = pygame.transform.scale(bg, (LARGURA, ALTURA))
                print(f"[NARRATIVA] Background {bg_name} carregado com sucesso: {bg_path}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao carregar background {bg_name} de {bg_path}: {e}")
                import traceback
                traceback.print_exc()
                # Criar fallback
                self.backgrounds[bg_name] = pygame.Surface((LARGURA, ALTURA))
                self.backgrounds[bg_name].fill((20, 20, 30))
        else:
            print(f"[NARRATIVA] AVISO: Background {bg_name} não encontrado em {bg_path}")
            # Criar fallback
            self.backgrounds[bg_name] = pygame.Surface((LARGURA, ALTURA))
            self.backgrounds[bg_name].fill((20, 20, 30))
    
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
            choices = scene.get("choices", [])
            if choices:
                self.choices_visible = True
                self.selected_choice = 0
            else:
                self._avancar_cena()
            return
        
        line = lines[self.current_line_index]
        
        line_type = line.get("type", "dialogue")
        if line_type == "stageDirection":
            texto = line.get("text", "")
            if texto.startswith("[TIME-SKIP:"):
                inicio = texto.find(":") + 1
                fim = texto.rfind("]")
                if fim > inicio:
                    self.time_skip_text = texto[inicio:fim].strip()
                else:
                    self.time_skip_text = texto.replace("[TIME-SKIP:", "").replace("]", "").strip()
            else:
                self.time_skip_text = texto
            
            self.time_skip_active = True
            self.time_skip_fade_alpha = 0.0
            self.time_skip_fade_direction = 1
            self.time_skip_duration = 0.0
            
            texto_lower = self.time_skip_text.lower()
            
            self.current_line_index += 1
            return
        
        conditions = line.get("conditions", [])
        if conditions and not self._verificar_condicoes(conditions):
            self.current_line_index += 1
            self._avancar_linha()
            return
        
        sprite_name = line.get("sprite")
        speaker = line.get("speaker", "")
        if sprite_name:
            character_id = speaker.lower()
            if character_id in self.scene_sprites:
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
        
        texto = line.get("text", "")
        if texto.startswith("narrative."):
            t = _get_t()
            texto = t(texto)
        self._iniciar_animacao_texto(texto)
    
    def _avancar_cena(self):
        """Avança para a próxima cena"""
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        # Salvar flags de progresso quando a cena termina
        self._salvar_flags_cena_atual()
        
        # Salvar progresso após avançar cena (IMPORTANTE: salvar sempre para não repetir cutscenes)
        try:
            from core.progresso import gerenciador_progresso
            from core.missoes import gerenciador_missoes
            from core.mapa_locations import gerenciador_localizacoes
            gerenciador_progresso.salvar()
            gerenciador_missoes.salvar()
            gerenciador_localizacoes.salvar()
            print(f"[NARRATIVA] Progresso salvo após avançar cena {self.current_scene_id}")
        except Exception as e:
            print(f"[NARRATIVA] Erro ao salvar progresso: {e}")
            import traceback
            traceback.print_exc()
        
        # Se a cena possui um gameplayTrigger, não avançar automaticamente aqui.
        # O loop de narrativa em menu.py chama obter_trigger_atual quando todas
        # as linhas terminam e então processa o trigger (ex: start_race, goto_map,
        # open_shop). Se avançarmos de cena agora, o trigger se perde.
        if scene.get("gameplayTrigger"):
            print(f"[NARRATIVA] Cena {self.current_scene_id} tem gameplayTrigger, aguardando processamento no loop principal")
            return
        
        next_scene_id = scene.get("nextSceneId")
        if next_scene_id:
            self.iniciar_cena(next_scene_id)
        else:
            # Se nextSceneId é null, verificar se há auto-save nos efeitos
            effects = scene.get("effects", [])
            if "autoSave" in effects:
                try:
                    from core.progresso import gerenciador_progresso
                    from core.missoes import gerenciador_missoes
                    from core.mapa_locations import gerenciador_localizacoes
                    gerenciador_progresso.salvar()
                    gerenciador_missoes.salvar()
                    gerenciador_localizacoes.salvar()
                    print(f"[NARRATIVA] Auto-save executado ao final da cena {self.current_scene_id} (nextSceneId: null)")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao executar auto-save: {e}")
            
            # Marcar cena como visitada
            if self.current_scene_id:
                self.scenes_visited.add(self.current_scene_id)
            if self.current_chapter_id:
                try:
                    from core.progresso import gerenciador_progresso
                    
                    # Se completou a última cena do capítulo 3 (ch3_8_pixel_wrap)
                    if self.current_chapter_id == "ch3" and self.current_scene_id == "ch3_8_pixel_wrap":
                        print(f"[NARRATIVA] Última cena do Capítulo 3 completada (ch3_8_pixel_wrap)")
                        # Marcar capítulo 3 como completo
                        gerenciador_progresso.marcar_capitulo_completo("ch3")
                        
                        # Verificar se deve iniciar capítulo 4 (após completar corrida da montanha)
                        if getattr(gerenciador_progresso, 'iniciar_capitulo_4_apos_narrativa', False):
                            print(f"[NARRATIVA] Flag iniciar_capitulo_4_apos_narrativa ativa, iniciando Capítulo 4...")
                            gerenciador_progresso.iniciar_capitulo_4_apos_narrativa = False
                            gerenciador_progresso.definir_capitulo_atual("ch4")
                            gerenciador_progresso.salvar()
                            # Iniciar capítulo 4
                            if self.iniciar_capitulo("ch4"):
                                return  # Narrativa continua ativa com o capítulo 4
                        else:
                            print(f"[NARRATIVA] Capítulo 3 marcado como completo. Capítulo 4 será iniciado após completar a corrida da montanha.")
                            gerenciador_progresso.salvar()
                    # Se completou a última cena do capítulo 4 (ch4_7_rex_direct_call)
                    elif self.current_chapter_id == "ch4" and self.current_scene_id == "ch4_7_rex_direct_call":
                        print(f"[NARRATIVA] Última cena do Capítulo 4 completada (ch4_7_rex_direct_call)")
                        # Marcar capítulo 4 como completo
                        gerenciador_progresso.marcar_capitulo_completo("ch4")
                        gerenciador_progresso.definir_capitulo_atual("ch5")
                        gerenciador_progresso.salvar()
                        # Iniciar capítulo 5
                        if self.iniciar_capitulo("ch5"):
                            print(f"[NARRATIVA] Capítulo 5 iniciado automaticamente após completar Capítulo 4")
                            return  # Narrativa continua ativa com o capítulo 5
                    elif self.current_chapter_id != "ch3" and self.current_chapter_id != "ch4":
                        # Para outros capítulos, marcar como completo normalmente
                        gerenciador_progresso.marcar_capitulo_completo(self.current_chapter_id)
                        gerenciador_progresso.salvar()
                    
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao processar fim de capítulo: {e}")
                    import traceback
                    traceback.print_exc()
            self.active = False
    
    def _salvar_flags_cena_atual(self):
        """Salva as flags de progresso quando uma cena termina"""
        if not self.current_scene_id:
            return
        
        from core.progresso import gerenciador_progresso
        
        # Completar missões que devem ser completadas nesta cena
        try:
            from core.missoes import gerenciador_missoes
            gerenciador_missoes.completar_por_cena(self.current_scene_id)
        except:
            pass
        
        # Mapeamento de cenas para flags de progresso
        cena_para_flag = {
            "ch1_3_meet_boris": ("boris_primeira_aparicao_mostrada", "boris"),
            "ch1_7_pixel_intro": ("pixel_primeira_aparicao_mostrada", "pixel"),
            "ch1_1_crank_garage_intro": ("crank_tutorial_mostrado", "crank"),
            "ch2_2_barao_appears": ("barao_nome_revelado", "barao"),
            "ch3_1_crank_to_mountain": (None, "akira"),  # Crank menciona Akira pelo nome
        }
        
        if self.current_scene_id in cena_para_flag:
            flag_name, personagem = cena_para_flag[self.current_scene_id]
            
            # Se flag_name é None, apenas revelar o nome do personagem
            if flag_name is None:
                if personagem == "akira" and not gerenciador_progresso.akira_nome_revelado:
                    print(f"[NARRATIVA] Revelando nome da Akira na cena {self.current_scene_id}")
                    gerenciador_progresso.akira_nome_revelado = True
                    # Salvar estado da Akira também
                    try:
                        from core.akira import akira
                        akira.nome_revelado = True
                        akira.salvar_estado()
                    except Exception as e:
                        print(f"[NARRATIVA] Erro ao salvar estado da Akira: {e}")
                    gerenciador_progresso.salvar()
                    print(f"[NARRATIVA] Nome da Akira revelado e salvo com sucesso!")
            elif not getattr(gerenciador_progresso, flag_name, False):
                print(f"[NARRATIVA] Salvando flag {flag_name}=True para cena {self.current_scene_id}")
                setattr(gerenciador_progresso, flag_name, True)
                
                # Salvar também o nome revelado se aplicável
                if personagem == "boris" and not gerenciador_progresso.boris_nome_revelado:
                    gerenciador_progresso.boris_nome_revelado = True
                elif personagem == "pixel" and not gerenciador_progresso.pixel_nome_revelado:
                    gerenciador_progresso.pixel_nome_revelado = True
                elif personagem == "barao" and not gerenciador_progresso.barao_nome_revelado:
                    gerenciador_progresso.barao_nome_revelado = True
                    # Salvar estado do Barão também
                    try:
                        from core.barao import barao
                        barao.nome_revelado = True
                        barao.salvar_estado()
                    except Exception as e:
                        print(f"[NARRATIVA] Erro ao salvar estado do Barão: {e}")
                elif personagem == "akira" and not gerenciador_progresso.akira_nome_revelado:
                    gerenciador_progresso.akira_nome_revelado = True
                    # Salvar estado da Akira também
                    try:
                        from core.akira import akira
                        akira.nome_revelado = True
                        akira.salvar_estado()
                    except Exception as e:
                        print(f"[NARRATIVA] Erro ao salvar estado da Akira: {e}")
                
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Flag {flag_name} salva com sucesso!")
    
    def obter_trigger_da_cena(self, scene_id: str = None) -> Optional[Dict]:
        """Obtém o trigger de uma cena específica ou da cena atual"""
        if scene_id is None:
            scene = self._obter_cena_atual()
        else:
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
        
        trigger = scene.get("gameplayTrigger")
        if trigger:
            # Salvar flags quando a cena termina com trigger
            self._salvar_flags_cena_atual()
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
                
                if key.startswith("has") or key.startswith("wants") or key.startswith("told") or key.startswith("set"):
                    flag_value = self.flags.get(key, False)
                    # Verificar também no progresso se for hasDebt
                    if key == "hasDebt":
                        from core.progresso import gerenciador_progresso
                        flag_value = flag_value or gerenciador_progresso.barao_emprestimo_ativo
                    
                    if value.lower() == "true":
                        if not flag_value:
                            return False
                    elif value.lower() == "false":
                        if flag_value:
                            return False
                elif key in self.variables:
                    if str(self.variables[key]) != value:
                        return False
                elif key == "lastRaceResult":
                    if self.variables.get("lastRaceResult") != value:
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
            if evento.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = evento.pos
                self._verificar_hover_hitbox(mouse_x, mouse_y)
            
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if self.choices_visible:
                        mouse_x, mouse_y = evento.pos
                        scene = self._obter_cena_atual()
                        if scene:
                            choices = scene.get("choices", [])
                            choice_height = 60
                            choice_y_start = ALTURA - 200 - (len(choices) * choice_height)
                            
                            for i, choice in enumerate(choices):
                                choice_y = choice_y_start + i * choice_height
                                if choice_y <= mouse_y <= choice_y + choice_height:
                                    resultado = self._processar_escolha(choice)
                                    # Se a escolha retornou um trigger, retornar para ser processado
                                    if resultado:
                                        return resultado
                                    return None
                    else:
                        if self.time_skip_active or self.scene_transition_active:
                            return None
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self.texto_exibido = self.texto_completo
                        else:
                            self.current_line_index += 1
                            self._avancar_linha()
            
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    if self.choices_visible:
                        scene = self._obter_cena_atual()
                        if scene:
                            choices = scene.get("choices", [])
                            if 0 <= self.selected_choice < len(choices):
                                resultado = self._processar_escolha(choices[self.selected_choice])
                                # Se a escolha retornou um trigger, retornar para ser processado
                                if resultado:
                                    return resultado
                    else:
                        if self.time_skip_active or self.scene_transition_active:
                            return None
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
        effects = choice.get("effects", [])
        for effect in effects:
            self._processar_efeito(effect)
        
        # Verificar se há gameplayTrigger na escolha (ex: "Ir correr")
        gameplay_trigger = choice.get("gameplayTrigger")
        if gameplay_trigger:
            # Se há trigger, fechar narrativa e retornar o trigger para ser processado
            self.active = False
            return gameplay_trigger
        
        next_scene_id = choice.get("nextSceneId")
        if next_scene_id:
            self.scene_transition_active = True
            self.scene_transition_fade_alpha = 0.0
            self.scene_transition_fade_direction = 1
            self.scene_transition_duration = 0.0
            self.scene_transition_next_scene_id = next_scene_id
        else:
            self.choices_visible = False
            self.current_line_index += 1
            self._avancar_linha()
        
        return None
    
    def verificar_gatilho_cena(self, scene: Dict) -> bool:
        """Verifica se os gatilhos de uma cena foram atendidos"""
        start_trigger = scene.get("startTrigger")
        if not start_trigger:
            # Se não tem startTrigger, assume "immediate" (compatibilidade com sistema antigo)
            return True
        
        trigger_type = start_trigger.get("type", "immediate")
        params = start_trigger.get("params", {})
        conditions = start_trigger.get("conditions", [])
        
        # Verificar condições primeiro
        if conditions:
            if not self._verificar_condicoes(conditions):
                return False
        
        # Verificar tipo de gatilho
        if trigger_type == "immediate":
            return True
        elif trigger_type == "enter_location":
            location_id = params.get("locationId")
            # Isso será verificado externamente quando o jogador entrar no local
            return False  # Retorna False para que seja verificado externamente
        elif trigger_type == "race_finished":
            race_id = params.get("raceId")
            result = params.get("result", "any")
            # Verificar se a corrida foi completada
            from core.progresso import gerenciador_progresso
            if hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
                if gerenciador_progresso.ultima_corrida_campanha == race_id:
                    if result == "any":
                        return True
                    # Verificar resultado da corrida
                    race_result = self.variables.get("lastRaceResult", "")
                    if result == race_result:
                        return True
            return False
        elif trigger_type == "time_passed":
            days = params.get("days", 1)
            after_scene_id = params.get("afterSceneId") or params.get("daysSinceScene") or params.get("daysSinceChapterStart")
            if after_scene_id:
                # Verificar se passou o tempo necessário desde a cena
                if after_scene_id in self.scenes_visited:
                    # TODO: Implementar verificação de tempo real
                    return True
            return False
        elif trigger_type == "reputation_threshold":
            min_reputation = params.get("minReputation", 0)
            # TODO: Implementar sistema de reputação
            return False
        elif trigger_type == "race_selected":
            race_id = params.get("raceId")
            # Isso será verificado externamente quando o jogador selecionar a corrida
            return False
        
        return False
    
    def _verificar_condicoes(self, conditions: List[str]) -> bool:
        """Verifica se todas as condições são atendidas"""
        from core.progresso import gerenciador_progresso
        
        for condition in conditions:
            if "=" in condition:
                key, value = condition.split("=", 1)
                if key == "hasDebt":
                    if value == "true":
                        if not getattr(gerenciador_progresso, 'barao_emprestimo_ativo', False):
                            return False
                    elif value == "false":
                        if getattr(gerenciador_progresso, 'barao_emprestimo_ativo', False):
                            return False
                elif key == "raceResult":
                    if value != self.variables.get("lastRaceResult", ""):
                        return False
                elif key == "racePerformance":
                    # TODO: Implementar verificação de performance
                    pass
                elif key.startswith("locationUnlocked:"):
                    location = key.split(":")[1]
                    should_be_unlocked = value == "true"
                    from core.mapa_locations import gerenciador_localizacoes
                    is_unlocked = gerenciador_localizacoes.esta_desbloqueado(location)
                    if should_be_unlocked != is_unlocked:
                        return False
                elif ">=" in condition:
                    key, value = condition.split(">=", 1)
                    if key == "playerMoney":
                        required = int(value)
                        if gerenciador_progresso.dinheiro < required:
                            return False
        
        return True
    
    def _processar_efeito(self, effect: str):
        """Processa um efeito (flag, desbloqueio, etc.)"""
        if effect.startswith("setFlag:"):
            flag_name = effect.split(":", 1)[1]
            self.flags[flag_name] = True
            print(f"[NARRATIVA] Flag '{flag_name}' definida como True")
            
            # Se for hasDebt, também salvar no progresso
            if flag_name == "hasDebt":
                from core.progresso import gerenciador_progresso
                from core.barao import barao
                # Ativar empréstimo do Barão
                gerenciador_progresso.barao_emprestimo_ativo = True
                gerenciador_progresso.barao_valor_devido = barao.VALOR_TOTAL
                gerenciador_progresso.barao_corridas_restantes = barao.PRAZO_CORRIDAS
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Empréstimo do Barão ativado: valor_devido={gerenciador_progresso.barao_valor_devido}, corridas_restantes={gerenciador_progresso.barao_corridas_restantes}")
        elif effect.startswith("unlockLocation:"):
            location = effect.split(":", 1)[1]
            try:
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_localizacoes.desbloquear(location)
                print(f"[NARRATIVA] Desbloqueando localização: {location}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao desbloquear localização {location}: {e}")
        elif effect.startswith("unlockRace:") or effect.startswith("unlockRaceSet:"):
            race = effect.split(":", 1)[1]
            if effect.startswith("unlockRaceSet:"):
                try:
                    from core.mapa_locations import gerenciador_localizacoes
                    gerenciador_localizacoes.processar_efeito_narrativa(effect)
                    print(f"[NARRATIVA] Desbloqueando conjunto de corridas: {race}")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao desbloquear conjunto de corridas {race}: {e}")
            else:
                # unlockRace: desbloqueia uma corrida específica
                # Salvar no progresso que a corrida está desbloqueada
                try:
                    from core.progresso import gerenciador_progresso
                    if not hasattr(gerenciador_progresso, 'corridas_desbloqueadas'):
                        gerenciador_progresso.corridas_desbloqueadas = set()
                    if isinstance(gerenciador_progresso.corridas_desbloqueadas, list):
                        gerenciador_progresso.corridas_desbloqueadas = set(gerenciador_progresso.corridas_desbloqueadas)
                    gerenciador_progresso.corridas_desbloqueadas.add(race)
                    gerenciador_progresso.salvar()
                    print(f"[NARRATIVA] Corrida '{race}' desbloqueada e salva no progresso")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao desbloquear corrida {race}: {e}")
                print(f"[NARRATIVA] Desbloqueando corrida: {race}")
        elif effect.startswith("openShop:"):
            shop = effect.split(":", 1)[1]
            # TODO: abrir loja
            print(f"[NARRATIVA] Abrindo loja: {shop}")
        elif effect.startswith("openGarage:"):
            garage_action = effect.split(":", 1)[1]
            print(f"[NARRATIVA] Abrindo garagem: {garage_action}")
        elif effect.startswith("addMoney:"):
            amount_str = effect.split(":", 1)[1]
            try:
                from core.progresso import gerenciador_progresso
                # Se for "loanAmount", usar valor do empréstimo do Barão
                if amount_str == "loanAmount":
                    from core.barao import barao
                    amount = barao.VALOR_EMPRESTIMO
                else:
                    # Tentar converter para número
                    amount = int(amount_str)
                
                gerenciador_progresso.adicionar_dinheiro(amount)
                print(f"[NARRATIVA] Adicionando dinheiro: {amount}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao adicionar dinheiro '{amount_str}': {e}")
        elif effect.startswith("mentionLocation:"):
            location = effect.split(":", 1)[1]
            try:
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_localizacoes.tornar_visivel(location)
                print(f"[NARRATIVA] Tornando localização visível: {location}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao tornar localização visível {location}: {e}")
        elif effect == "autoSave":
            try:
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_progresso.salvar()
                gerenciador_missoes.salvar()
                gerenciador_localizacoes.salvar()
                print(f"[NARRATIVA] Auto-save executado após cena {self.current_scene_id}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao executar auto-save: {e}")
        elif effect.startswith("addObjective:"):
            objective = effect.split(":", 1)[1]
            try:
                from core.missoes import gerenciador_missoes
                # TODO: Implementar sistema de objetivos dinâmicos
                print(f"[NARRATIVA] Adicionando objetivo: {objective}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao adicionar objetivo: {e}")
        elif effect.startswith("completeObjective:"):
            objective = effect.split(":", 1)[1]
            try:
                from core.missoes import gerenciador_missoes
                # TODO: Implementar sistema de objetivos dinâmicos
                print(f"[NARRATIVA] Completando objetivo: {objective}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao completar objetivo: {e}")
        elif effect.startswith("removeMoney:"):
            amount_str = effect.split(":", 1)[1]
            try:
                from core.progresso import gerenciador_progresso
                amount = int(amount_str)
                gerenciador_progresso.remover_dinheiro(amount)
                print(f"[NARRATIVA] Removendo dinheiro: {amount}")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao remover dinheiro '{amount_str}': {e}")
        elif effect.startswith("advanceTime:"):
            time_str = effect.split(":", 1)[1]
            # TODO: Implementar avanço de tempo
            print(f"[NARRATIVA] Avançando tempo: {time_str}")
        elif effect.startswith("installFirstUpgrade"):
            # TODO: Implementar instalação de primeiro upgrade
            print(f"[NARRATIVA] Instalando primeiro upgrade")
        elif effect.startswith("endChapter:"):
            chapter_id = effect.split(":", 1)[1]
            try:
                from core.progresso import gerenciador_progresso
                gerenciador_progresso.marcar_capitulo_completo(chapter_id)
                print(f"[NARRATIVA] Capítulo {chapter_id} marcado como completo")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao finalizar capítulo: {e}")
        elif effect.startswith("startChapter:"):
            chapter_id = effect.split(":", 1)[1]
            try:
                from core.progresso import gerenciador_progresso
                gerenciador_progresso.definir_capitulo_atual(chapter_id)
                print(f"[NARRATIVA] Capítulo {chapter_id} iniciado")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao iniciar capítulo: {e}")
        elif effect == "endGame":
            # TODO: Implementar fim do jogo
            print(f"[NARRATIVA] Fim do jogo")
    
    def atualizar(self, dt: float):
        """Atualiza o sistema de narrativa"""
        if not self.active:
            return
        
        if self.scene_transition_active:
            self.scene_transition_duration += dt
            
            tempo_fade_in = self.scene_transition_tempo_fade
            tempo_escuro = self.scene_transition_tempo_escuro
            tempo_fade_out = self.scene_transition_tempo_clarear
            
            fade_speed_in = 1.0 / tempo_fade_in if tempo_fade_in > 0 else 1.0
            fade_speed_out = 1.0 / tempo_fade_out if tempo_fade_out > 0 else 1.0
            
            if self.scene_transition_fade_direction == 1:
                self.scene_transition_fade_alpha += fade_speed_in * dt
                if self.scene_transition_fade_alpha >= 1.0:
                    self.scene_transition_fade_alpha = 1.0
                    if self.scene_transition_duration >= tempo_fade_in + tempo_escuro:
                        if self.scene_transition_next_scene_id:
                            self._iniciar_cena_sem_transicao(self.scene_transition_next_scene_id)
                            self.scene_transition_next_scene_id = None
                        self.scene_transition_fade_direction = -1
            else:
                self.scene_transition_fade_alpha -= fade_speed_out * dt
                if self.scene_transition_fade_alpha <= 0.0:
                    self.scene_transition_fade_alpha = 0.0
                    self.scene_transition_active = False
            return
        
        if self.time_skip_active:
            self.time_skip_duration += dt
            
            tempo_fade_in = 3.0
            tempo_escuro = 1.5
            tempo_fade_out = 3.0
            
            fade_speed_in = 1.0 / tempo_fade_in
            fade_speed_out = 1.0 / tempo_fade_out
            
            if self.time_skip_fade_direction == 1:
                self.time_skip_fade_alpha += fade_speed_in * dt
                if self.time_skip_fade_alpha >= 1.0:
                    self.time_skip_fade_alpha = 1.0
                    if self.time_skip_duration >= tempo_fade_in + tempo_escuro:
                        self.time_skip_fade_direction = -1
            else:
                self.time_skip_fade_alpha -= fade_speed_out * dt
                if self.time_skip_fade_alpha <= 0.0:
                    self.time_skip_fade_alpha = 0.0
                    self.time_skip_active = False
                    # Após o time-skip, avançar para a próxima linha
                    # Se não houver mais linhas, avançar para a próxima cena
                    scene = self._obter_cena_atual()
                    if scene:
                        lines = scene.get("lines", [])
                        if self.current_line_index >= len(lines):
                            # Não há mais linhas, avançar para a próxima cena
                            self._avancar_cena()
                        else:
                            self._avancar_linha()
        
        # Sistema de créditos (auto-avanço com fade)
        if self.creditos_auto_advance:
            self.creditos_tempo_mostrado += dt
            
            # Fade in do texto (primeiro 1 segundo)
            if self.creditos_tempo_mostrado < 1.0:
                self.creditos_texto_fade_alpha = min(1.0, self.creditos_tempo_mostrado / 1.0)
                self.creditos_texto_fade_direction = 1
            # Texto visível (1 segundo a 2.5 segundos)
            elif self.creditos_tempo_mostrado < 2.5:
                self.creditos_texto_fade_alpha = 1.0
            # Fade out do texto (2.5 a 3.5 segundos)
            elif self.creditos_tempo_mostrado < 3.5:
                self.creditos_texto_fade_alpha = max(0.0, 1.0 - (self.creditos_tempo_mostrado - 2.5) / 1.0)
                self.creditos_texto_fade_direction = -1
            # Após 3.5 segundos, avançar para próxima cena
            elif self.creditos_tempo_mostrado >= 3.5:
                scene = self._obter_cena_atual()
                if scene:
                    next_scene_id = scene.get("nextSceneId")
                    if next_scene_id:
                        # Usar transição de cena para mudar o background
                        self._iniciar_cena_com_transicao(next_scene_id)
                    else:
                        # Última cena de créditos, desativar auto-avanço
                        self.creditos_auto_advance = False
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar(self, tela: pygame.Surface):
        """Desenha a cena atual"""
        if not self.active:
            return
        
        render_text = _get_render_text()
        
        scene = self._obter_cena_atual()
        if scene:
            bg_name = scene.get("bg")
            if bg_name:
                # Tentar carregar o background se não estiver carregado
                if bg_name not in self.backgrounds:
                    print(f"[NARRATIVA] Background {bg_name} não está carregado, tentando carregar...")
                    self._carregar_background(bg_name)
                
                # Se ainda não está carregado após tentar, usar fallback
                if bg_name in self.backgrounds:
                    tela.blit(self.backgrounds[bg_name], (0, 0))
                else:
                    print(f"[NARRATIVA] ERRO: Não foi possível carregar background {bg_name}, usando fallback")
                    # Fallback: fundo escuro
                    tela.fill((20, 20, 30))
            else:
                # Sem background definido, usar fundo escuro
                tela.fill((20, 20, 30))
        
        if self.hover_sprite_atual:
            tela.blit(self.hover_sprite_atual, (0, 0))
        
        for sprite_id, sprite_data in self.scene_sprites.items():
            sprite = sprite_data["sprite"]
            position = sprite_data["position"]
            
            if sprite is None:
                print(f"ERRO: Sprite {sprite_id} é None!")
                continue
            
            sprite_original_w, sprite_original_h = sprite.get_size()
            if sprite_original_w == 0 or sprite_original_h == 0:
                print(f"[NARRATIVA] ERRO: Sprite {sprite_id} tem tamanho inválido ({sprite_original_w}, {sprite_original_h})")
                continue
            
            sprite_altura_max = 400
            sprite_largura_max = 350
            
            escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
            escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
            escala = min(escala_w, escala_h, 1.0)
            
            sprite_w = int(sprite_original_w * escala)
            sprite_h = int(sprite_original_h * escala)
            sprite_scaled = pygame.transform.scale(sprite, (sprite_w, sprite_h))
            
            caixa_altura = 10
            caixa_y = ALTURA - caixa_altura - 50
            sprite_y_base = caixa_y - sprite_h - 20
            
            if position == "left":
                sprite_x = 50
                sprite_y = sprite_y_base
            elif position == "right":
                sprite_x = LARGURA - sprite_w - 500
                sprite_y = sprite_y_base
            elif position == "center":
                sprite_x = LARGURA // 2 - sprite_w // 2
                sprite_y = sprite_y_base
            elif position == "hud":
                sprite_x = LARGURA // 2 - sprite_w // 2
                sprite_y = 100
            else:
                sprite_x = 50
                sprite_y = ALTURA // 2 - sprite_h // 2 - 50
            
            tela.blit(sprite_scaled, (sprite_x, sprite_y))
        
        if self.scene_transition_active:
            overlay_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            alpha = int(self.scene_transition_fade_alpha * 255)
            overlay_escuro.fill((0, 0, 0, alpha))
            tela.blit(overlay_escuro, (0, 0))
        
        elif self.time_skip_active:
            overlay_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            alpha = int(self.time_skip_fade_alpha * 255)
            overlay_escuro.fill((0, 0, 0, alpha))
            tela.blit(overlay_escuro, (0, 0))
            
            if self.time_skip_text and self.time_skip_fade_alpha > 0.3:
                texto_alpha = min(1.0, (self.time_skip_fade_alpha - 0.3) / 0.7) if self.time_skip_fade_alpha > 0.3 else 0.0
                texto_cor = (255, 255, 200)
                
                texto_render = render_text(self.time_skip_text, 20, texto_cor, bold=True, pixel_style=True)
                texto_x = (LARGURA - texto_render.get_width()) // 2
                texto_y = ALTURA // 2
                
                if texto_alpha > 0:
                    fundo_texto = pygame.Surface((texto_render.get_width() + 40, texto_render.get_height() + 20), pygame.SRCALPHA)
                    fundo_alpha = int(texto_alpha * 100)
                    fundo_texto.fill((0, 0, 0, fundo_alpha))
                    tela.blit(fundo_texto, (texto_x - 20, texto_y - 10))
                    tela.blit(texto_render, (texto_x, texto_y))
        
        if not self.time_skip_active and not self.scene_transition_active:
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
        
        # Para cenas de créditos, usar fade no texto
        texto_alpha = 1.0
        if self.creditos_auto_advance:
            texto_alpha = self.creditos_texto_fade_alpha
        
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay_caixa.fill((0, 0, 0, 200))
        tela.blit(overlay_caixa, (caixa_x, caixa_y))
        
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        t = _get_t()
        if speaker == "NARRATOR":
            nome = t("narrative.narrator")
        elif speaker == "SISTEMA":
            nome = t("narrative.system")
        else:
            nome_key = f"narrative.characters.{speaker.lower()}"
            nome_traduzido = t(nome_key)
            if nome_traduzido == nome_key:
                nome = speaker.upper() if speaker else "???"
            else:
                nome = nome_traduzido
        nome_texto = render_text(nome, 20, (255, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
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
                # Aplicar alpha para créditos
                if self.creditos_auto_advance and texto_alpha < 1.0:
                    linha_surface = linha_render.copy()
                    linha_surface.set_alpha(int(texto_alpha * 255))
                    tela.blit(linha_surface, (caixa_x + 20, y_texto))
                else:
                    tela.blit(linha_render, (caixa_x + 20, y_texto))
                y_texto += 25
        
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
            if choice_text.startswith("narrative."):
                choice_text = t(choice_text)
            
            if i == self.selected_choice:
                cor = (255, 255, 255)
                cor_bg = (100, 100, 200)
            else:
                cor = (200, 200, 200)
                cor_bg = (50, 50, 100)
            
            choice_rect = pygame.Rect(50, choice_y, LARGURA - 100, choice_height)
            pygame.draw.rect(tela, cor_bg, choice_rect)
            pygame.draw.rect(tela, cor, choice_rect, 2)
            
            texto_render = render_text(choice_text, 20, cor, bold=True, pixel_style=True)
            texto_x = 50 + (choice_rect.width - texto_render.get_width()) // 2
            tela.blit(texto_render, (texto_x, choice_y + (choice_height - texto_render.get_height()) // 2))
    
    def fechar(self):
        """Fecha o sistema de narrativa"""
        self.active = False

narrative_system = NarrativeSystem()

