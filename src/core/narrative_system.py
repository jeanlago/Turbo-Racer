"""Sistema de narrativa baseado em JSON para a campanha"""
import pygame
import json
import os
from typing import Dict, List, Optional, Any
from config import DIR_PROJETO, LARGURA, ALTURA
def _get_render_text():
    from core.menu import render_text
    return render_text

def _get_t():
    from core.i18n import t
    return t

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative_new.json")

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
        
        self._escolha_ja_processada = False
        
        self.scenario_hitboxes = {}
        self.hover_hitbox_atual = None
        self.hover_sprite_atual = None
        
        self.ultimo_background = None
        
        self.creditos_auto_advance = False
        self.creditos_tempo_mostrado = 0.0
        self.creditos_tempo_por_texto = 3.5
        self.creditos_tempo_fade = 0.8
        self.creditos_texto_fade_alpha = 0.0
        self.creditos_texto_fade_direction = 1
        self.creditos_background_index = 0
        self.creditos_backgrounds = [
            "oficina_dia.png",
            "cidade_noite.png",
            "beco_neon_noite.png",
            "monte_akira_noite.png",
            "pista_corrida_anoitecendo.png",
            "predio_rex_noite.png",
            "autodromo_fora_noite.png"
        ]
        self.creditos_backgrounds_carregados = {}
        self.creditos_background_alpha = 1.0
        self.creditos_texto_atual_index = 0
        self.creditos_background_fade_direction = 0
        
        self.pending_scenes = []
        self.scenes_visited = set()
        self.chapter_start_time = {}
        
        # Flag para indicar que o jogo terminou (após créditos)
        self.game_ended = False
        
        self.carregar_narrativa()
        self.carregar_hitboxes_cenarios()
    
    def carregar_narrativa(self):
        """Carrega o arquivo JSON de narrativa"""
        print(f"[NARRATIVA] Tentando carregar narrativa de: {CAMINHO_NARRATIVA}")
        try:
            with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
                self.narrative_data = json.load(f)
            print(f"[NARRATIVA] Narrativa carregada com sucesso! Capítulos: {len(self.narrative_data.get('chapters', []))}")
            for ch in self.narrative_data.get('chapters', []):
                print(f"[NARRATIVA]   - Capítulo {ch.get('id')}: {len(ch.get('scenes', []))} cenas")
        except FileNotFoundError:
            print(f"[NARRATIVA] ERRO: Arquivo não encontrado: {CAMINHO_NARRATIVA}")
            self.narrative_data = {"chapters": []}
        except Exception as e:
            print(f"[NARRATIVA] Erro ao carregar narrativa: {e}")
            import traceback
            traceback.print_exc()
            self.narrative_data = {"chapters": []}
    
    def iniciar_capitulo(self, chapter_id: str):
        """Inicia um capítulo da narrativa"""
        if not self.narrative_data:
            print(f"[NARRATIVA] Erro: narrative_data não carregado")
            return False
        
        chapter = None
        for ch in self.narrative_data.get("chapters", []):
            if ch.get("id") == chapter_id:
                chapter = ch
                break
        
        if not chapter:
            print(f"[NARRATIVA] Erro: Capítulo {chapter_id} não encontrado no narrative_data")
            return False
        
        print(f"[NARRATIVA] Iniciando capítulo {chapter_id}, total de cenas: {len(chapter.get('scenes', []))}")
        
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
            
            # Verificar cenas com gatilho "immediate" para iniciar
            for scene in scenes:
                scene_id = scene.get("id")
                start_trigger = scene.get("startTrigger")
                
                # Se não tem startTrigger ou é "immediate", verificar condições
                if not start_trigger or start_trigger.get("type") == "immediate":
                    if scene_id == "ch1_0_prologue" and chapter_id == "ch1":
                        # Se é um novo save (nenhuma missão completa), forçar início
                        try:
                            from core.missoes import gerenciador_missoes
                            if len(gerenciador_missoes.missoes_completas) == 0:
                                print(f"[NARRATIVA] NOVO SAVE: Forçando início de ch1_0_prologue mesmo se já visitada")
                                # Remover de scenes_visited para permitir reinício
                                self.scenes_visited.discard(scene_id)
                        except:
                            pass
                    
                    # Verificar se já foi visitada
                    if scene_id not in self.scenes_visited:
                        # Verificar condições se houver
                        conditions = start_trigger.get("conditions", []) if start_trigger else []
                        if conditions:
                            if not self._verificar_condicoes(conditions):
                                print(f"[NARRATIVA] Cena {scene_id} tem condições não atendidas, pulando...")
                                continue  # Pular esta cena se condições não atendidas
                        
                        print(f"[NARRATIVA] Iniciando capítulo {chapter_id} com cena {scene_id} (trigger: {start_trigger.get('type') if start_trigger else 'none'})")
                        resultado = self.iniciar_cena(scene_id)
                        if resultado:
                            return True
                        else:
                            print(f"[NARRATIVA] Falha ao iniciar cena {scene_id}, tentando próxima...")
                            continue
            
            # Se não encontrou cena imediata, marcar capítulo como iniciado mas não ativar narrativa ainda
            print(f"[NARRATIVA] Capítulo {chapter_id} iniciado, aguardando gatilhos...")
            return True
        return False
    
    def iniciar_cena(self, scene_id: str):
        """Inicia uma cena específica (com transição de fade se já houver uma cena ativa)"""
        # Resetar flag de escolha processada ao iniciar nova cena
        self._escolha_ja_processada = False
        
        if scene_id == "ch1_0_prologue":
            try:
                from core.missoes import gerenciador_missoes
                if len(gerenciador_missoes.missoes_completas) == 0:
                    print(f"[NARRATIVA] NOVO SAVE: Permitindo reinício de ch1_0_prologue")
                    # Remover de scenes_visited para permitir reinício
                    self.scenes_visited.discard(scene_id)
            except:
                pass
        
        # Evitar reiniciar cenas que já foram visitadas quando a narrativa foi fechada para iniciar uma corrida
        # MAS permitir se a narrativa está ativa (para sequências)
        if scene_id in self.scenes_visited and not self.active:
            print(f"[NARRATIVA] Tentativa de reiniciar cena {scene_id} que já foi visitada. Narrativa está fechada, pulando...")
            return False
        
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
        
        # Resetar flag de escolha processada ao iniciar nova cena
        self._escolha_ja_processada = False
        
        if scene_id == "ch1_0_prologue":
            try:
                from core.missoes import gerenciador_missoes
                if len(gerenciador_missoes.missoes_completas) == 0:
                    print(f"[NARRATIVA] NOVO SAVE: Permitindo reinício de ch1_0_prologue em _iniciar_cena_sem_transicao")
                    # Remover de scenes_visited para permitir reinício
                    self.scenes_visited.discard(scene_id)
            except:
                pass
        
        scene_data = None
        for ch in self.narrative_data.get("chapters", []):
            for sc in ch.get("scenes", []):
                if sc.get("id") == scene_id:
                    scene_data = sc
                    break
            if scene_data:
                break
        
        # Se a cena tem startTrigger de race_finished, permitir reinício
        permitir_reinicio = False
        if scene_data:
            start_trigger = scene_data.get("startTrigger", {})
            if isinstance(start_trigger, dict) and start_trigger.get("type") == "race_finished":
                permitir_reinicio = True
                print(f"[NARRATIVA] Cena {scene_id} tem startTrigger race_finished, permitindo reinício mesmo se já foi visitada")
        
        # Evitar reiniciar cenas que já foram visitadas quando a narrativa foi fechada para iniciar uma corrida
        # MAS permitir avançar para cenas com nextSceneId mesmo se já foram visitadas (para permitir sequências)
        # E permitir reinício de cenas com startTrigger race_finished
        if scene_id in self.scenes_visited and not self.active and not permitir_reinicio:
            print(f"[NARRATIVA] Tentativa de reiniciar cena {scene_id} que já foi visitada. Narrativa está fechada, pulando...")
            return False
        
        # Se a narrativa está ativa e estamos avançando de uma cena para outra (via nextSceneId),
        # permitir mesmo se a cena já foi visitada (para permitir sequências de cenas finais, especialmente créditos)
        if scene_id in self.scenes_visited and self.active:
            print(f"[NARRATIVA] Cena {scene_id} já foi visitada, mas narrativa está ativa. Permitindo avanço para sequência de cenas (incluindo créditos).")
            # Remover da lista de visitadas temporariamente para permitir reativação
            self.scenes_visited.discard(scene_id)
        
        # Prevenir loops infinitos rastreando cenas já visitadas nesta cadeia
        if cenas_visitadas is None:
            cenas_visitadas = set()
        
        if scene_id in cenas_visitadas:
            print(f"[NARRATIVA] Loop detectado! Cena {scene_id} já foi visitada nesta cadeia. Desativando narrativa.")
            self.active = False
            return False
        
        cenas_visitadas.add(scene_id)
        
        # Primeiro, tentar encontrar a cena no capítulo atual
        chapter = None
        for ch in self.narrative_data.get("chapters", []):
            if ch.get("id") == self.current_chapter_id:
                chapter = ch
                break
        
        scene = None
        if chapter:
            for sc in chapter.get("scenes", []):
                if sc.get("id") == scene_id:
                    scene = sc
                    break
        
        # Se não encontrou no capítulo atual, procurar em todos os capítulos
        # (útil quando nextSceneId aponta para uma cena de outro capítulo)
        if not scene:
            print(f"[NARRATIVA] Cena {scene_id} não encontrada no capítulo atual ({self.current_chapter_id}), procurando em todos os capítulos...")
            for ch in self.narrative_data.get("chapters", []):
                for sc in ch.get("scenes", []):
                    if sc.get("id") == scene_id:
                        scene = sc
                        # Atualizar current_chapter_id para o capítulo onde a cena foi encontrada
                        self.current_chapter_id = ch.get("id")
                        print(f"[NARRATIVA] Cena {scene_id} encontrada no capítulo {self.current_chapter_id}, atualizando current_chapter_id")
                        break
                if scene:
                    break
        
        if not scene:
            print(f"[NARRATIVA] Erro: Cena {scene_id} não encontrada em nenhum capítulo")
            return False
        
        # Verificar se a cena já foi vista (primeira aparição de personagens)
        from core.progresso import gerenciador_progresso
        
        # Mapeamento de cenas para flags de progresso
        cena_para_flag = {
            "ch1_2_meet_boris": ("boris_primeira_aparicao_mostrada", "boris"),
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
        
        # Garantir que a narrativa está ativa após iniciar a cena
        print(f"[NARRATIVA] Cena {scene_id} iniciada. active: {self.active}, current_scene_id: {self.current_scene_id}, current_chapter_id: {self.current_chapter_id}")
        
        # NÃO marcar cena como visitada imediatamente ao iniciar
        # A cena será marcada como visitada apenas quando terminar (em _avancar_cena)
        # Isso permite que cenas com nextSceneId sejam reativadas se necessário
        # if scene_id not in self.scenes_visited:
        #     self.scenes_visited.add(scene_id)
        #     print(f"[NARRATIVA] Cena {scene_id} marcada como visitada")
        
        # Salvar flags da cena atual (ex: barao_nome_revelado)
        self._salvar_flags_cena_atual()
        
        # AUTOSAVE: Salvar progresso sempre que uma cena é iniciada
        # Isso garante que se o jogador sair no meio de uma cutscene, o progresso seja mantido
        try:
            from core.progresso import gerenciador_progresso
            from core.missoes import gerenciador_missoes
            from core.mapa_locations import gerenciador_localizacoes
            
            # Completar missões associadas a esta cena
            gerenciador_missoes.completar_por_cena(scene_id)
            
            # Ativar missões associadas a esta cena
            gerenciador_missoes.ativar_por_cena(scene_id)
            
            # Ativar m11_chamado_da_montanha quando ch3_2_pixel_route é iniciada (após Crank falar e Pixel falar)
            if scene_id == "ch3_2_pixel_route":
                if "m11_chamado_da_montanha" not in gerenciador_missoes.missoes_completas and "m11_chamado_da_montanha" in gerenciador_missoes.missoes:
                    print(f"[NARRATIVA] Cena ch3_2_pixel_route iniciada, ativando missão m11_chamado_da_montanha...")
                    gerenciador_missoes.ativar_missao("m11_chamado_da_montanha")
            
            gerenciador_progresso.salvar()
            gerenciador_missoes.salvar()
            gerenciador_localizacoes.salvar()
            print(f"[NARRATIVA] Autosave executado ao iniciar cena {scene_id}")
        except Exception as e:
            print(f"[NARRATIVA] Erro ao executar autosave ao iniciar cena: {e}")
            import traceback
            traceback.print_exc()
        
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
            # e garantir que a missão seja ativada
            if scene_id == "ch1_4b_housing_offer" and scene_id not in self.scenes_visited:
                self.scenes_visited.add(scene_id)
                print(f"[NARRATIVA] Marcando ch1_4b_housing_offer como visitada imediatamente para evitar reativação")
            
            if scene_id == "ch1_1c_crank_test_result" and scene_id not in self.scenes_visited:
                self.scenes_visited.add(scene_id)
                print(f"[NARRATIVA] Marcando ch1_1c_crank_test_result como visitada imediatamente para permitir ativação de m3")
            
            mapeamento_ativacao = {
                "ch1_5_race_briefing": "ch1_5_first_race_unlocked",
                "ch1_6_post_race": "ch1_6_post_first_race_and_pixel",
            }
            cena_mapeada = mapeamento_ativacao.get(scene_id)
            if cena_mapeada and cena_mapeada not in self.scenes_visited:
                self.scenes_visited.add(cena_mapeada)
                print(f"[NARRATIVA] Marcando cena mapeada {cena_mapeada} como visitada (original: {scene_id})")
            
            # Ativar missões que devem ser ativadas nesta cena
            print(f"[NARRATIVA] Chamando ativar_por_cena para cena {scene_id}")
            missao_ativada = gerenciador_missoes.ativar_por_cena(scene_id)
            if missao_ativada:
                print(f"[NARRATIVA] Missão {missao_ativada} ativada pela cena {scene_id}")
                gerenciador_missoes.salvar()  # Salvar imediatamente após ativar
            else:
                print(f"[NARRATIVA] Nenhuma missão foi ativada pela cena {scene_id}")
                for mid, m in gerenciador_missoes.missoes.items():
                    activate_on = m.get("activateOnSceneId")
                    if activate_on == scene_id:
                        print(f"[NARRATIVA] DEBUG: Missão {mid} tem activateOnSceneId={activate_on}, mas não foi ativada. Completa: {mid in gerenciador_missoes.missoes_completas}, visitada: {scene_id in self.scenes_visited}")
            # Completar missões que devem ser completadas quando esta cena é iniciada
            # (especialmente para cenas que são gatilhos de entrada, como ch1_1_crank_garage_intro)
            gerenciador_missoes.completar_por_cena(scene_id)
            
            # Ativar m11_chamado_da_montanha quando ch3_2_pixel_route é iniciada (após Crank falar e Pixel falar)
            if scene_id == "ch3_2_pixel_route":
                if "m11_chamado_da_montanha" not in gerenciador_missoes.missoes_completas and "m11_chamado_da_montanha" in gerenciador_missoes.missoes:
                    print(f"[NARRATIVA] Cena ch3_2_pixel_route iniciada, ativando missão m11_chamado_da_montanha...")
                    gerenciador_missoes.ativar_missao("m11_chamado_da_montanha")
        except Exception as e:
            print(f"[NARRATIVA] Erro ao ativar/completar missão por cena: {e}")
        self.selected_choice = 0
        
        # Processar efeitos da cena (ex: unlockLocation, unlockRace, etc.)
        # NOTA: Efeitos são processados ANTES de iniciar a cena para garantir que desbloqueios aconteçam imediatamente
        effects = scene.get("effects", [])
        if effects:
            print(f"[NARRATIVA] Processando {len(effects)} efeito(s) da cena {scene_id}")
            for effect in effects:
                # Não processar autoSave aqui - será processado quando nextSceneId for null
                if effect != "autoSave":
                    self._processar_efeito(effect)
                    # Se for a flag akira_nome_revelado, garantir que está salva e recarregada
                    if effect == "setFlag:akira_nome_revelado":
                        from core.progresso import gerenciador_progresso
                        gerenciador_progresso.carregar()  # Recarregar para garantir que temos o valor mais recente
                        print(f"[NARRATIVA] Flag akira_nome_revelado processada, valor atual: {gerenciador_progresso.akira_nome_revelado}")
        
        bg_name = scene.get("bg")
        if bg_name:
            self._carregar_background(bg_name)
        
        sprites_config = scene.get("sprites", [])
        print(f"[NARRATIVA] Cena {scene_id}: sprites_config={sprites_config}, type={type(sprites_config)}")
        self._carregar_sprites_cena(sprites_config)
        if not self.scene_sprites:
            print(f"[NARRATIVA] AVISO: Nenhum sprite carregado para a cena {scene_id} (pode ser normal se a cena não tem sprites)")
        else:
            print(f"[NARRATIVA] Carregados {len(self.scene_sprites)} sprite(s) para a cena {scene_id}: {list(self.scene_sprites.keys())}")
        
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
            "bg_garagem_interior_carro": "dentro_carro_oficina.png",
            "bg_fosso_ferrugem": "fosso.png",
            "bg_mapa_cidade": "cidade.png",
            "bg_santuario_montanha": "monte_akira.png",
            "bg_cobertura_corporativa": "predio_rex.png",
            "bg_beco_neon": "beco_neon_noite.png",
            "bg_beco_sucata": "beco_de_sucata",
            "bg_esconderijo_hacker": "bunker",
            "bg_apartamento_jogador": "casa.png",
            "bg_oficina_exterior_noite": "oficina_exterior_noite.png",
            "bg_grid_circuito_urbano": "autodromo_fora.png",
            "bg_pit_circuito": "oficina.png",
            "bg_pit_stop_dia": "pit_stop_dia.png",
            "bg_pista_corrida_anoitecendo": "pista_corrida_anoitecendo.png",
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
            
            sprites_dia_noite = ["cidade", "oficina", "casa", "monte_akira", "autodromo_fora", "fosso", "predio_rex", "iate_barao", "beco_de_sucata", "bunker"]
            
            # Se o nome_base está na lista de sprites dia/noite, usar sistema dia/noite
            # Mesmo que arquivo_cenario termine com .png, se o nome_base está na lista, usar dia/noite
            if nome_base in sprites_dia_noite:
                # Determinar se é dia ou noite baseado no bg_name
                # Se o bg_name termina com _noite ou _dia, usar isso para determinar o arquivo
                if bg_name.endswith("_noite"):
                    # Forçar noite para backgrounds que especificam _noite
                    from config import definir_estado_dia_noite
                    definir_estado_dia_noite("noite")
                    # Criar caminho manualmente para noite
                    bg_path = os.path.join(CAMINHO_BACKGROUNDS, f"{nome_base}_noite.png")
                    if not os.path.exists(bg_path):
                        # Se não existe _noite, tentar o padrão
                        bg_path = obter_caminho_sprite_dia_noite(nome_base, CAMINHO_BACKGROUNDS)
                elif bg_name.endswith("_dia"):
                    # Forçar dia para backgrounds que especificam _dia
                    from config import definir_estado_dia_noite
                    definir_estado_dia_noite("dia")
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
                if not os.path.exists(bg_path):
                    print(f"[NARRATIVA] AVISO: Arquivo não encontrado: {bg_path}")
                    # Tentar fallback direto
                    fallback_path = os.path.join(CAMINHO_BACKGROUNDS, f"{nome_base}_dia.png")
                    if os.path.exists(fallback_path):
                        print(f"[NARRATIVA] Usando fallback dia: {fallback_path}")
                        bg_path = fallback_path
                    else:
                        fallback_path = os.path.join(CAMINHO_BACKGROUNDS, f"{nome_base}_noite.png")
                        if os.path.exists(fallback_path):
                            print(f"[NARRATIVA] Usando fallback noite: {fallback_path}")
                            bg_path = fallback_path
            else:
                # Se o arquivo_cenario é um arquivo específico (ex: "beco_neon_noite.png"), usar diretamente
                # Mas apenas se não estiver na lista de sprites dia/noite
                if arquivo_cenario and arquivo_cenario.endswith(".png") and not arquivo_cenario.startswith("bg_"):
                    bg_path = os.path.join(CAMINHO_BACKGROUNDS, arquivo_cenario)
                    print(f"[NARRATIVA] Carregando background {bg_name} -> {arquivo_cenario}: {bg_path}")
                else:
                    # Fallback: tentar usar o arquivo diretamente
                    bg_path = os.path.join(CAMINHO_BACKGROUNDS, arquivo_cenario)
                    print(f"[NARRATIVA] Carregando background {bg_name} -> {arquivo_cenario}: {bg_path}")
        
        # Garantir que bg_path foi definido
        if 'bg_path' not in locals():
            # Fallback final: tentar usar o bg_name diretamente
            bg_path = os.path.join(CAMINHO_BACKGROUNDS, f"{bg_name}.png")
            print(f"[NARRATIVA] AVISO: bg_path não foi definido, usando fallback: {bg_path}")
        
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
        print(f"[NARRATIVA] _carregar_sprites_cena chamado com sprites_config={sprites_config}, type={type(sprites_config)}")
        self.scene_sprites = {}
        
        if not sprites_config:
            print(f"[NARRATIVA] AVISO: sprites_config está vazio ou None!")
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
            
            print(f"[NARRATIVA] Tentando carregar sprite: id={sprite_id}, sprite_name={sprite_name}, path={sprite_path}, exists={os.path.exists(sprite_path)}")
            
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
                    print(f"[NARRATIVA] Sprite {sprite_id}/{sprite_name} carregado com sucesso!")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao carregar sprite {sprite_id}/{sprite_name}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[NARRATIVA] AVISO: Sprite não encontrado: {sprite_path}")
            
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
            if self.current_scene_id == "ch1_3_boris_deal":
                print(f"[NARRATIVA] _avancar_linha: Todas as linhas foram exibidas! line_index={self.current_line_index}, total={len(lines)}")
                for i, line in enumerate(lines):
                    print(f"  Linha {i}: {line.get('speaker', '')} - {line.get('text', '')[:60]}...")
            
            # Se estávamos exibindo linhas de uma escolha, restaurar linhas originais e avançar para próxima cena
            if hasattr(self, '_original_scene_lines'):
                scene["lines"] = self._original_scene_lines
                next_scene_id = getattr(self, '_next_scene_id_escolha', None)
                delattr(self, '_original_scene_lines')
                if hasattr(self, '_next_scene_id_escolha'):
                    delattr(self, '_next_scene_id_escolha')
                
                # Completar missão m10 se o Cinturão foi desbloqueado
                if self.current_scene_id in ["ch2_6_crank_cinturao_offer", "ch2_5_boris_offer_again"]:
                    from core.missoes import gerenciador_missoes
                    from core.mapa_locations import gerenciador_localizacoes
                    # Verificar se o Cinturão foi desbloqueado
                    if gerenciador_localizacoes.esta_desbloqueado("cinturao_industrial"):
                        # Completar a missão m10
                        gerenciador_missoes.completar_missao("m10_portoes_do_cinturao")
                        # Atualizar objetivo da missão
                        gerenciador_missoes.atualizar_objetivo_missao("m10_portoes_do_cinturao", "Corra no Cinturão Industrial")
                        gerenciador_missoes.salvar()
                        print(f"[NARRATIVA] Missão m10_portoes_do_cinturao completada após desbloquear Cinturão")
                
                if getattr(self, '_escolha_ja_processada', False):
                    self._escolha_ja_processada = False  # Resetar flag
                    if next_scene_id:
                        print(f"[NARRATIVA] Linhas da escolha terminadas, avançando para {next_scene_id} (escolha já foi processada)")
                        # Marcar cena atual como visitada antes de avançar
                        if self.current_scene_id:
                            self.scenes_visited.add(self.current_scene_id)
                            self._salvar_flags_cena_atual()
                            # Completar missões quando necessário
                            from core.missoes import gerenciador_missoes
                            if self.current_scene_id == "ch2_2_barao_offer":
                                gerenciador_missoes.completar_por_cena(self.current_scene_id)
                                print(f"[NARRATIVA] Missão completada ao finalizar escolha na cena {self.current_scene_id}")
                        # Iniciar transição para próxima cena
                        self.scene_transition_active = True
                        self.scene_transition_fade_alpha = 0.0
                        self.scene_transition_fade_direction = 1
                        self.scene_transition_duration = 0.0
                        self.scene_transition_next_scene_id = next_scene_id
                        return
                    else:
                        print(f"[NARRATIVA] Linhas da escolha terminadas mas não há nextSceneId")
                        # Fechar narrativa se não há próxima cena
                        self.active = False
                        return
            
            # Mas só mostrar escolhas se uma escolha ainda não foi processada
            choices = scene.get("choices", [])
            if choices and not getattr(self, '_escolha_ja_processada', False):
                print(f"[NARRATIVA] Todas as linhas exibidas, mostrando {len(choices)} escolhas")
                self.choices_visible = True
                self.selected_choice = 0
                return  # Não avançar cena, aguardar escolha do jogador
            else:
                # Não há escolhas ou escolha já foi processada, avançar cena normalmente
                if getattr(self, '_escolha_ja_processada', False):
                    self._escolha_ja_processada = False  # Resetar flag
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
            # Marcar cena como visitada antes de sair
            if self.current_scene_id:
                self.scenes_visited.add(self.current_scene_id)
            # NÃO limpar current_scene_id ainda - o loop principal precisa dele para obter o trigger
            # O current_scene_id será limpo quando o trigger for processado em processar_trigger
            # Não desativar a narrativa ainda - o loop principal precisa processar o trigger primeiro
            print(f"[NARRATIVA] Cena {self.current_scene_id} marcada como visitada, mantendo current_scene_id para processar trigger")
            return
        
        next_scene_id = scene.get("nextSceneId")
        if next_scene_id:
            # Isso garante que cenas com nextSceneId sejam marcadas como visitadas corretamente
            if self.current_scene_id:
                self.scenes_visited.add(self.current_scene_id)
                print(f"[NARRATIVA] Cena {self.current_scene_id} marcada como visitada antes de avançar para {next_scene_id}")
            
            # Iniciar próxima cena diretamente sem transição para evitar tela preta
            # Transições podem causar problemas, então vamos iniciar diretamente
            print(f"[NARRATIVA] Avançando de {self.current_scene_id} para {next_scene_id} sem transição")
            print(f"[NARRATIVA] Capítulo atual: {self.current_chapter_id}, active: {self.active}")
            resultado = self._iniciar_cena_sem_transicao(next_scene_id)
            if not resultado:
                print(f"[NARRATIVA] Erro ao iniciar cena {next_scene_id} diretamente, tentando com transição...")
                self.iniciar_cena(next_scene_id)
            else:
                print(f"[NARRATIVA] Cena {next_scene_id} iniciada com sucesso. active: {self.active}, current_scene_id: {self.current_scene_id}")
        else:
            # Se nextSceneId é null, verificar se há gameplayTrigger antes de fechar
            # Se houver trigger, ele será processado pelo loop principal antes de fechar
            gameplay_trigger = scene.get("gameplayTrigger")
            if gameplay_trigger:
                print(f"[NARRATIVA] Cena {self.current_scene_id} tem gameplayTrigger e nextSceneId é null, trigger será processado pelo loop principal")
                # Não fechar a narrativa ainda - deixar o loop principal processar o trigger
                # A narrativa será fechada quando o trigger for processado
                # Marcar cena como visitada mas manter current_scene_id para o trigger ser processado
                if self.current_scene_id:
                    self.scenes_visited.add(self.current_scene_id)
                # Salvar flags antes de processar trigger
                self._salvar_flags_cena_atual()
                # Não limpar current_scene_id ainda - o loop principal vai processar o trigger
                return
            
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
            
            # Verificar se é a última cena de créditos (endGame)
            is_end_game = "endGame" in effects
            
            # Marcar cena como visitada (sempre marcar, mesmo se houver nextSceneId)
            # Isso é necessário para evitar loops infinitos
            if self.current_scene_id:
                self.scenes_visited.add(self.current_scene_id)
                if next_scene_id:
                    print(f"[NARRATIVA] Cena {self.current_scene_id} marcada como visitada (avançando para {next_scene_id})")
                else:
                    print(f"[NARRATIVA] Cena {self.current_scene_id} marcada como visitada (sem próxima cena)")
            
            # Se é a última cena e tem endGame, fechar narrativa após processar tudo
            if is_end_game and not next_scene_id:
                print(f"[NARRATIVA] Fim do jogo detectado - fechando narrativa após processar missões")
                
                # Isso garante que a missão anterior seja completada antes de ativar a próxima
                try:
                    from core.missoes import gerenciador_missoes
                    missao_completada = gerenciador_missoes.completar_por_cena(self.current_scene_id)
                    if missao_completada:
                        print(f"[NARRATIVA] Missão {missao_completada} completada pela cena {self.current_scene_id}")
                        # Salvar imediatamente após completar a missão
                        gerenciador_missoes.salvar()
                        print(f"[NARRATIVA] Missões salvas após completar {missao_completada}")
                    else:
                        print(f"[NARRATIVA] Nenhuma missão encontrada para completar pela cena {self.current_scene_id}")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao completar missão por cena: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Ativar missões que devem ser ativadas quando esta cena termina
                # (DEPOIS de completar missões, para garantir ordem correta)
                try:
                    from core.missoes import gerenciador_missoes
                    missao_ativada = gerenciador_missoes.ativar_por_cena(self.current_scene_id)
                    if missao_ativada:
                        print(f"[NARRATIVA] Missão {missao_ativada} ativada pela cena {self.current_scene_id}")
                        gerenciador_missoes.salvar()
                    else:
                        print(f"[NARRATIVA] Nenhuma missão encontrada para ativar pela cena {self.current_scene_id}")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao ativar missão por cena: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Verificar se é fim do jogo antes de limpar current_scene_id
            is_end_game = "endGame" in effects
            
            # Limpar current_scene_id quando nextSceneId é null para evitar que o jogo
            # tente continuar de uma cena que já terminou
            cena_atual = self.current_scene_id
            self.current_scene_id = None
            print(f"[NARRATIVA] Cena {cena_atual} marcada como visitada e current_scene_id limpo (nextSceneId: null)")
            
            # Se é fim do jogo, marcar flag especial para o loop principal retornar ao menu
            if is_end_game:
                print(f"[NARRATIVA] Fim do jogo - marcando flag para retornar ao menu principal")
                self.active = False
                # Adicionar flag especial para indicar que o jogo terminou
                self.game_ended = True
            
            if cena_atual in ["ch4_5_meet_slick", "ch4_5b_contar_pixel"]:
                print(f"[NARRATIVA] Cena {cena_atual} terminou, verificando se deve iniciar Capítulo 5...")
                try:
                    from core.progresso import gerenciador_progresso
                    # Verificar se há flag para iniciar Capítulo 5 após a cena do Slick
                    if getattr(gerenciador_progresso, 'iniciar_capitulo_5_apos_slick', False):
                        print(f"[NARRATIVA] Flag iniciar_capitulo_5_apos_slick ativa, iniciando Capítulo 5...")
                        gerenciador_progresso.iniciar_capitulo_5_apos_slick = False
                        gerenciador_progresso.definir_capitulo_atual("ch5")
                        gerenciador_progresso.salvar()
                        # Iniciar capítulo 5
                        if self.iniciar_capitulo("ch5"):
                            print(f"[NARRATIVA] Capítulo 5 iniciado após cena do Slick")
                            return  # Narrativa continua ativa com o capítulo 5
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao verificar início do Capítulo 5: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Se não iniciou Capítulo 5, fechar narrativa normalmente
                print(f"[NARRATIVA] Cena {cena_atual} terminou, fechando narrativa")
                self.active = False
                # Marcar flag temporária para evitar verificação de gatilhos imediatamente após
                self._ultima_cena_slick = True
                return
            
            # Se a cena atual é ch4_5a_beco_neon_empty, apenas fechar sem verificar outros gatilhos
            if cena_atual == "ch4_5a_beco_neon_empty":
                print(f"[NARRATIVA] Cena ch4_5a_beco_neon_empty terminou, avançando para próxima cena")
                # Esta cena tem nextSceneId, então não deve chegar aqui, mas por segurança:
                return
            
            # Desativar narrativa quando nextSceneId é null (pausa narrativa)
            self.active = False
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
            "ch1_2_meet_boris": ("boris_primeira_aparicao_mostrada", "boris"),
            "ch1_7_pixel_intro": ("pixel_primeira_aparicao_mostrada", "pixel"),
            "ch1_7_pixel_voice_intro": ("pixel_primeira_aparicao_mostrada", "pixel"),  # Cena real do Pixel
            "ch4_3_meet_pixel_physical": ("pixel_primeira_aparicao_mostrada", "pixel"),  # Encontro físico com Pixel
            "ch1_1_crank_garage_intro": ("crank_tutorial_mostrado", "crank"),
            "ch2_1_barao_intro": ("barao_nome_revelado", "barao"),  # Primeira aparição do Barão
            "ch2_2_barao_offer": ("barao_nome_revelado", "barao"),  # Oferta do empréstimo (também revela nome se ainda não foi)
            "ch3_1_crank_briefing": (None, "akira"),  # Crank menciona Akira pelo nome
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
            print(f"[NARRATIVA] obter_trigger_da_cena: current_scene_id={self.current_scene_id}, scene encontrada={scene is not None}")
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
            print(f"[NARRATIVA] obter_trigger_da_cena: cena não encontrada")
            return None
        
        trigger = scene.get("gameplayTrigger")
        if trigger:
            # Extrair o tipo do trigger
            trigger_type = trigger.get("trigger")
            # Todos os outros campos (exceto "trigger") são params
            params = {k: v for k, v in trigger.items() if k != "trigger"}
            print(f"[NARRATIVA] obter_trigger_da_cena: trigger encontrado: {trigger_type}, params={params}")
            print(f"[NARRATIVA] obter_trigger_da_cena: cena_id={scene_id or self.current_scene_id}, trigger_type={trigger_type}")
            # Salvar flags quando a cena termina com trigger
            self._salvar_flags_cena_atual()
            return {
                "trigger": trigger_type,
                "params": params
            }
        
        print(f"[NARRATIVA] obter_trigger_da_cena: cena não tem gameplayTrigger (scene_id={scene_id or self.current_scene_id})")
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
                elif key.startswith("requiredFlag:"):
                    # Verificar se uma flag específica está ativa
                    flag_name = key.split(":")[1]
                    flag_value = self.flags.get(flag_name, False)
                    # Também verificar no progresso (para flags como crownCircuitActive)
                    if not flag_value:
                        from core.progresso import gerenciador_progresso
                        flag_value = getattr(gerenciador_progresso, flag_name, False)
                    if not flag_value:
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
            # Se há trigger, retornar o trigger no formato esperado pelo processar_trigger
            # Extrair todos os campos do gameplayTrigger (exceto "trigger") como params
            params = {k: v for k, v in gameplay_trigger.items() if k != "trigger"}
            # NÃO fechar a narrativa aqui - deixar o loop principal processar o trigger primeiro
            # self.active = False
            return {
                "trigger": gameplay_trigger.get("trigger"),
                "params": params
            }
        
        self._escolha_ja_processada = True
        
        # Verificar se a escolha tem linhas para exibir após a escolha
        choice_lines = choice.get("lines", [])
        if choice_lines:
            # Adicionar as linhas da escolha temporariamente à cena atual
            scene = self._obter_cena_atual()
            if scene:
                # Salvar as linhas originais da cena
                if not hasattr(self, '_original_scene_lines'):
                    self._original_scene_lines = scene.get("lines", [])
                # Salvar o nextSceneId da escolha para usar depois
                if not hasattr(self, '_next_scene_id_escolha'):
                    self._next_scene_id_escolha = choice.get("nextSceneId")
                # Adicionar as linhas da escolha após as linhas originais
                scene["lines"] = self._original_scene_lines + choice_lines
                # Resetar o índice de linha para começar a exibir as linhas da escolha
                self.current_line_index = len(self._original_scene_lines)
                self.choices_visible = False
                # Iniciar a primeira linha da escolha
                self._avancar_linha()
                return None
        
        next_scene_id = choice.get("nextSceneId")
        if next_scene_id:
            # Marcar cena atual como visitada antes de avançar
            if self.current_scene_id:
                self.scenes_visited.add(self.current_scene_id)
                # Salvar flags da cena atual antes de avançar
                self._salvar_flags_cena_atual()
                # Completar missões quando uma escolha é feita (especialmente para ch2_2_barao_offer e ch5_0_prologue)
                from core.missoes import gerenciador_missoes
                if self.current_scene_id == "ch2_2_barao_offer":
                    gerenciador_missoes.completar_por_cena(self.current_scene_id)
                    print(f"[NARRATIVA] Missão completada ao fazer escolha na cena {self.current_scene_id}")
                elif self.current_scene_id == "ch5_0_prologue":
                    # Completar missão m17_convite_da_coroa quando aceita o convite
                    if "m17_convite_da_coroa" not in gerenciador_missoes.missoes_completas:
                        print(f"[NARRATIVA] Completando missão m17_convite_da_coroa...")
                        resultado = gerenciador_missoes.completar_missao("m17_convite_da_coroa")
                        if resultado:
                            print(f"[NARRATIVA] Missão m17_convite_da_coroa completada com sucesso")
                            # Garantir que a missão ativa seja limpa
                            if gerenciador_missoes.missao_ativa_id == "m17_convite_da_coroa":
                                gerenciador_missoes.missao_ativa_id = None
                                print(f"[NARRATIVA] Missão ativa limpa")
                            # Salvar imediatamente
                            gerenciador_missoes.salvar()
                            print(f"[NARRATIVA] Missões salvas após completar m17_convite_da_coroa")
                        else:
                            print(f"[NARRATIVA] ERRO: Falha ao completar missão m17_convite_da_coroa")
                    else:
                        print(f"[NARRATIVA] Missão m17_convite_da_coroa já estava completa")
                        # Mesmo assim, garantir que a missão ativa seja limpa
                        if gerenciador_missoes.missao_ativa_id == "m17_convite_da_coroa":
                            gerenciador_missoes.missao_ativa_id = None
                            gerenciador_missoes.salvar()
                            print(f"[NARRATIVA] Missão ativa limpa (missão já estava completa)")
                print(f"[NARRATIVA] Cena {self.current_scene_id} marcada como visitada ao processar escolha")
            
            self.scene_transition_active = True
            self.scene_transition_fade_alpha = 0.0
            self.scene_transition_fade_direction = 1
            self.scene_transition_duration = 0.0
            self.scene_transition_next_scene_id = next_scene_id
        else:
            # Se não há nextSceneId, completar missões se necessário (especialmente para ch5_0_prologue)
            if self.current_scene_id == "ch5_0_prologue":
                # Completar missão m17_convite_da_coroa quando aceita o convite
                from core.missoes import gerenciador_missoes
                if "m17_convite_da_coroa" not in gerenciador_missoes.missoes_completas:
                    print(f"[NARRATIVA] Completando missão m17_convite_da_coroa...")
                    resultado = gerenciador_missoes.completar_missao("m17_convite_da_coroa")
                    if resultado:
                        print(f"[NARRATIVA] Missão m17_convite_da_coroa completada com sucesso")
                        # Garantir que a missão ativa seja limpa
                        if gerenciador_missoes.missao_ativa_id == "m17_convite_da_coroa":
                            gerenciador_missoes.missao_ativa_id = None
                            print(f"[NARRATIVA] Missão ativa limpa")
                        # Salvar imediatamente
                        gerenciador_missoes.salvar()
                        print(f"[NARRATIVA] Missões salvas após completar m17_convite_da_coroa")
                    else:
                        print(f"[NARRATIVA] ERRO: Falha ao completar missão m17_convite_da_coroa")
                else:
                    print(f"[NARRATIVA] Missão m17_convite_da_coroa já estava completa")
                    # Mesmo assim, garantir que a missão ativa seja limpa
                    if gerenciador_missoes.missao_ativa_id == "m17_convite_da_coroa":
                        gerenciador_missoes.missao_ativa_id = None
                        gerenciador_missoes.salvar()
                        print(f"[NARRATIVA] Missão ativa limpa (missão já estava completa)")
            
            # Se não há nextSceneId e não há linhas da escolha, fechar a narrativa
            if not choice_lines:
                self.choices_visible = False
                # Completar missão m10 se o Cinturão foi desbloqueado
                if self.current_scene_id in ["ch2_6_crank_cinturao_offer", "ch2_5_boris_offer_again"]:
                    from core.missoes import gerenciador_missoes
                    from core.mapa_locations import gerenciador_localizacoes
                    # Verificar se o Cinturão foi desbloqueado
                    if gerenciador_localizacoes.esta_desbloqueado("cinturao_industrial"):
                        # Completar a missão m10
                        gerenciador_missoes.completar_missao("m10_portoes_do_cinturao")
                        # Atualizar objetivo da missão
                        gerenciador_missoes.atualizar_objetivo_missao("m10_portoes_do_cinturao", "Corra no Cinturão Industrial")
                        gerenciador_missoes.salvar()
                        print(f"[NARRATIVA] Missão m10_portoes_do_cinturao completada após desbloquear Cinturão")
                # Fechar a narrativa
                self._avancar_cena()
        
        return None
    
    def verificar_gatilho_cena(self, scene: Dict, context: Dict = None) -> bool:
        """Verifica se os gatilhos de uma cena foram atendidos
        
        Args:
            scene: Dicionário da cena
            context: Contexto adicional (ex: locationId, raceId, etc.)
        """
        start_trigger = scene.get("startTrigger")
        if not start_trigger:
            # Se não tem startTrigger e há um context específico (locationId, raceId, etc.),
            # não iniciar a cena (ela será iniciada via nextSceneId de outra cena)
            if context and (context.get("locationId") or context.get("raceId")):
                return False
            # Se não tem startTrigger e não há context específico, assume "immediate" (compatibilidade com sistema antigo)
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
            # Trigger immediate: só deve ser ativado no início do capítulo, não ao entrar em localizações
            # Se há um locationId no context, NÃO ativar triggers immediate
            # (eles só devem ser ativados quando o capítulo é iniciado, não ao entrar em localizações específicas)
            if context and context.get("locationId"):
                print(f"[NARRATIVA] Trigger 'immediate' ignorado porque há locationId no context: {context.get('locationId')}")
                return False
            
            # Verificar se já foi visitada
            scene_id = scene.get("id")
            if scene_id in self.scenes_visited:
                print(f"[NARRATIVA] Trigger 'immediate' ignorado porque cena {scene_id} já foi visitada")
                return False
            
            return True
        elif trigger_type == "enter_location":
            # Verificar se a cena já foi visitada - se sim, não reativar
            scene_id = scene.get("id")
            if scene_id in self.scenes_visited:
                print(f"[NARRATIVA] Trigger 'enter_location' ignorado porque cena {scene_id} já foi visitada")
                return False
            
            location_id = params.get("locationId")
            # Verificar se o contexto fornecido corresponde
            if context and context.get("locationId") == location_id:
                # Verificar condições adicionais
                required_item = params.get("requiredItem")
                required_flag = params.get("requiredFlag")
                time_of_day = params.get("timeOfDay")
                finished_quest = params.get("finishedQuest")
                
                if required_item:
                    # Verificar se o jogador tem o item necessário
                    if required_item == "any_part_from_boris":
                        # Verificar se o jogador comprou uma peça do Boris
                        # A compra completa a missão m4_coracao_de_sucata
                        from core.progresso import gerenciador_progresso
                        from core.missoes import gerenciador_missoes
                        
                        tem_peça = False
                        
                        # Verificar se a missão m4 foi completada (indica que comprou a peça)
                        if "m4_coracao_de_sucata" in gerenciador_missoes.missoes_completas:
                            tem_peça = True
                            print(f"[NARRATIVA] Trigger requer item '{required_item}' e jogador tem (missão m4 completada = peça comprada)")
                        
                        # Também verificar se há upgrades instalados (fallback)
                        if not tem_peça and hasattr(gerenciador_progresso, 'upgrades_instalados'):
                            upgrades = gerenciador_progresso.upgrades_instalados
                            if upgrades and len(upgrades) > 0:
                                tem_peça = True
                                print(f"[NARRATIVA] Trigger requer item '{required_item}' e jogador tem (upgrade instalado)")
                        
                        if not tem_peça:
                            print(f"[NARRATIVA] Trigger requer item '{required_item}' mas jogador não tem (missão m4 não completada e nenhum upgrade instalado)")
                            return False
                    else:
                        # Para outros itens, implementar verificação específica
                        print(f"[NARRATIVA] Trigger requer item '{required_item}' mas verificação não implementada")
                        # Por enquanto, retornar True para não bloquear outros triggers
                    pass
                
                if required_flag:
                    # Verificar flag no sistema narrativo ou no progresso
                    flag_value = self.flags.get(required_flag, False)
                    # Também verificar se a flag está no progresso (para flags como crownCircuitActive)
                    if not flag_value:
                        from core.progresso import gerenciador_progresso
                        # Tentar verificar se a flag existe como atributo do progresso
                        flag_value = getattr(gerenciador_progresso, required_flag, False)
                    if not flag_value:
                        return False
                
                if time_of_day:
                    # TODO: Verificar hora do dia
                    pass
                
                if finished_quest:
                    # Verificar se a quest foi completada
                    # finished_quest pode ser um ID de objetivo ou missão
                    from core.missoes import gerenciador_missoes
                    # Verificar se é um objetivo completado (ex: "finish_mountain_test")
                    # Por enquanto, assumir que se a quest está no nome, foi completada
                    # TODO: Implementar sistema de objetivos dinâmicos
                    print(f"[NARRATIVA] Trigger requer quest '{finished_quest}' completada")
                    # Se finished_quest é "finish_mountain_test", verificar se m13 foi completada
                    if finished_quest == "finish_mountain_test":
                        if "m13_teste_de_fluxo" not in gerenciador_missoes.missoes_completas:
                            print(f"[NARRATIVA] Trigger requer quest '{finished_quest}' mas missão m13 não foi completada - BLOQUEANDO")
                            return False
                        print(f"[NARRATIVA] Trigger requer quest '{finished_quest}' e está completa ✓")
                
                required_mission = params.get("requiredMission")
                if required_mission:
                    # Verificar se a missão está ativa
                    from core.missoes import gerenciador_missoes
                    print(f"[NARRATIVA] Trigger requer missão ativa '{required_mission}', missão ativa atual: '{gerenciador_missoes.missao_ativa_id}'")
                    if gerenciador_missoes.missao_ativa_id != required_mission:
                        print(f"[NARRATIVA] Trigger requer missão ativa '{required_mission}' mas missão ativa é '{gerenciador_missoes.missao_ativa_id}' - BLOQUEANDO")
                        return False
                    print(f"[NARRATIVA] Trigger requer missão ativa '{required_mission}' e está ativa ✓")
                
                required_mission_completed = params.get("requiredMissionCompleted")
                if required_mission_completed:
                    # Verificar se a missão foi completada
                    from core.missoes import gerenciador_missoes
                    print(f"[NARRATIVA] Trigger requer missão completada '{required_mission_completed}'")
                    if required_mission_completed not in gerenciador_missoes.missoes_completas:
                        print(f"[NARRATIVA] Trigger requer missão completada '{required_mission_completed}' mas não está completa - BLOQUEANDO")
                        return False
                    print(f"[NARRATIVA] Trigger requer missão completada '{required_mission_completed}' e está completa ✓")
                
                min_races_won = params.get("minRacesWon")
                if min_races_won:
                    # Verificar se o jogador completou o número mínimo de corridas no Cinturão
                    from core.progresso import gerenciador_progresso
                    corridas_completas = getattr(gerenciador_progresso, 'corridas_cinturao_completas', set())
                    if isinstance(corridas_completas, list):
                        corridas_completas = set(corridas_completas)
                    print(f"[NARRATIVA] Trigger requer {min_races_won} corridas no Cinturão, completadas: {len(corridas_completas)}")
                    if len(corridas_completas) < min_races_won:
                        print(f"[NARRATIVA] Trigger requer {min_races_won} corridas no Cinturão mas apenas {len(corridas_completas)} foram completadas - BLOQUEANDO")
                        return False
                    print(f"[NARRATIVA] Trigger requer {min_races_won} corridas no Cinturão e {len(corridas_completas)} foram completadas ✓")
                
                return True
            return False
        elif trigger_type == "enter_location_first_time":
            location_id = params.get("locationId")
            if context and context.get("locationId") == location_id:
                # Verificar se já visitou este local antes
                scene_id = scene.get("id")
                if scene_id in self.scenes_visited:
                    return False  # Já visitou, não disparar novamente
                
                # Isso previne que cenas sejam ativadas antes da narrativa desbloquear a localização
                from core.mapa_locations import gerenciador_localizacoes
                
                # Mapear locationId para ID de localização (alguns usam bg_ prefixo)
                location_map = {
                    "bg_beco_neon": "beco_neon",
                    "beco_neon": "beco_neon",
                    "bg_esconderijo_hacker": "esconderijo_pixel",
                    "esconderijo_pixel": "esconderijo_pixel",
                    "bg_garagem": "oficina",
                    "oficina": "oficina",
                    "bg_apartamento_jogador": "casa",
                    "casa": "casa"
                }
                location_key = location_map.get(location_id, location_id)
                
                if location_key and not gerenciador_localizacoes.esta_desbloqueado(location_key):
                    print(f"[NARRATIVA] Trigger enter_location_first_time bloqueado: {location_key} não está desbloqueado")
                    return False
                
                print(f"[NARRATIVA] Trigger enter_location_first_time permitido: {location_key} está desbloqueado")
                return True
            return False
        elif trigger_type == "race_finished":
            race_id = params.get("raceId")
            result = params.get("result", "any")
            print(f"[NARRATIVA] Verificando trigger race_finished: raceId={race_id}, result={result}")
            # Verificar se a corrida foi completada
            from core.progresso import gerenciador_progresso
            if context and context.get("raceId") == race_id:
                print(f"[NARRATIVA] Context raceId corresponde: {context.get('raceId')} == {race_id}")
                if result == "any":
                    print(f"[NARRATIVA] Result é 'any', gatilho atendido!")
                    return True
                # Verificar resultado da corrida
                race_result = context.get("raceResult") or self.variables.get("lastRaceResult", "")
                print(f"[NARRATIVA] Comparando resultados: race_result={race_result}, required={result}")
                if result == race_result:
                    print(f"[NARRATIVA] Resultados correspondem, gatilho atendido!")
                    return True
            elif hasattr(gerenciador_progresso, 'ultima_corrida_campanha'):
                if gerenciador_progresso.ultima_corrida_campanha == race_id:
                    if result == "any":
                        return True
                    race_result = self.variables.get("lastRaceResult", "")
                    if result == race_result:
                        return True
            print(f"[NARRATIVA] Gatilho race_finished NÃO atendido para raceId={race_id}")
            return False
        elif trigger_type == "time_passed":
            # Se há um context com locationId, não ativar cenas com time_passed
            # (elas devem ser ativadas apenas quando não há location específica)
            if context and context.get("locationId"):
                return False
            
            days = params.get("days", 1)
            after_scene_id = params.get("afterSceneId") or params.get("daysSinceScene")
            days_since_chapter = params.get("daysSinceChapterStart")
            
            if days_since_chapter is not None:
                # Verificar se passou tempo desde o início do capítulo
                if self.current_chapter_id in self.chapter_start_time:
                    import time
                    elapsed_days = (time.time() - self.chapter_start_time[self.current_chapter_id]) / 86400  # Converter para dias
                    if elapsed_days >= days:
                        return True
            elif after_scene_id:
                # Verificar se passou o tempo necessário desde a cena
                if after_scene_id in self.scenes_visited:
                    # TODO: Implementar verificação de tempo real baseado em quando a cena foi visitada
                    return True
            return False
        elif trigger_type == "reputation_threshold":
            min_reputation = params.get("minReputation", 0)
            zones = params.get("zones", [])
            # Verificar reputação do jogador
            try:
                from core.status_jogador import status_jogador
                popularidade_atual = status_jogador.popularidade
                print(f"[NARRATIVA] Verificando reputation_threshold: precisa {min_reputation}, tem {popularidade_atual}")
                if popularidade_atual >= min_reputation:
                    # Se há zonas específicas, verificar se correu em todas
                    if zones and "all" in zones:
                        # Verificar se correu nas três zonas: Ferrugem (pista 1-3), Cinturão (pista 4-6), Montanha (pista 3)
                        from core.estatisticas import gerenciador_estatisticas
                        gerenciador_estatisticas.carregar()
                        corridas_ferrugem = False
                        corridas_cinturao = False
                        corridas_montanha = False
                        
                        # Verificar Ferrugem (pistas 1, 2, 3)
                        for pista in [1, 2, 3]:
                            stats = gerenciador_estatisticas._obter_estatisticas_pista(pista)
                            if stats and stats.get("corridas_completas", 0) > 0:
                                corridas_ferrugem = True
                                break
                        
                        # Verificar Cinturão (pistas 4, 5, 6)
                        for pista in [4, 5, 6]:
                            stats = gerenciador_estatisticas._obter_estatisticas_pista(pista)
                            if stats and stats.get("corridas_completas", 0) > 0:
                                corridas_cinturao = True
                                break
                        
                        # Verificar Montanha (pista 3 - mesma da Akira)
                        stats_montanha = gerenciador_estatisticas._obter_estatisticas_pista(3)
                        if stats_montanha and stats_montanha.get("corridas_completas", 0) > 0:
                            corridas_montanha = True
                        
                        print(f"[NARRATIVA] Verificação de zonas: Ferrugem={corridas_ferrugem}, Cinturão={corridas_cinturao}, Montanha={corridas_montanha}")
                        return corridas_ferrugem and corridas_cinturao and corridas_montanha
                    else:
                        # Apenas verificar reputação
                        return True
                return False
            except Exception as e:
                print(f"[NARRATIVA] Erro ao verificar reputation_threshold: {e}")
                import traceback
                traceback.print_exc()
                return False
        elif trigger_type == "race_selected":
            race_id = params.get("raceId")
            if context and context.get("raceId") == race_id:
                return True
            return False
        
        return False
    
    def verificar_gatilhos_pendentes(self, context: Dict = None):
        """Verifica todos os gatilhos pendentes e inicia cenas que podem ser iniciadas"""
        if not self.narrative_data:
            return False
        
        # Se acabou de terminar a cena do Slick, não verificar outros gatilhos imediatamente
        if hasattr(self, '_ultima_cena_slick') and self._ultima_cena_slick:
            print(f"[NARRATIVA] Bloqueando verificação de gatilhos após cena do Slick")
            self._ultima_cena_slick = False  # Limpar flag
            return False
        
        # Se a missão m14b_voltar_oficina_pixel está ativa, também verificar capítulo 4
        from core.missoes import gerenciador_missoes
        verificar_ch4_adicional = gerenciador_missoes.missao_ativa_id == "m14b_voltar_oficina_pixel"
        
        # Lista de capítulos para verificar
        capitulos_para_verificar = []
        
        # Se há um context com locationId, verificar TODOS os capítulos (para permitir cenas como Glub no ch4)
        if context and context.get("locationId"):
            # Verificar todos os capítulos quando há um locationId (para permitir cenas de qualquer capítulo)
            for chapter in self.narrative_data.get("chapters", []):
                chapter_id = chapter.get("id")
                if chapter_id:
                    capitulos_para_verificar.append(chapter_id)
            print(f"[NARRATIVA] Context com locationId detectado, verificando todos os capítulos: {capitulos_para_verificar}")
        elif self.current_chapter_id:
            # Sem locationId, verificar apenas o capítulo atual
            capitulos_para_verificar = [self.current_chapter_id]
            if verificar_ch4_adicional and self.current_chapter_id != "ch4":
                capitulos_para_verificar.append("ch4")
                print(f"[NARRATIVA] Missão m14b_voltar_oficina_pixel ativa, também verificando capítulo 4")
        else:
            # Sem current_chapter_id e sem locationId, não verificar nada
            return False
        
        # Verificar cada capítulo
        for chapter_id in capitulos_para_verificar:
            chapter = None
            for ch in self.narrative_data.get("chapters", []):
                if ch.get("id") == chapter_id:
                    chapter = ch
                    break
            
            if not chapter:
                continue
            
            # Obter cenas do capítulo ANTES de verificar bloqueios
            scenes = chapter.get("scenes", [])
            
            # Verificar capítulo atual antes de processar gatilhos
            # PERMITIR cenas de capítulos futuros se o gatilho for enter_location_first_time (para Glub, Slick, etc.)
            from core.progresso import gerenciador_progresso
            capitulo_atual_progresso = gerenciador_progresso.obter_capitulo_atual()
            if capitulo_atual_progresso and capitulo_atual_progresso != chapter_id:
                # Se o capítulo do progresso não corresponde ao capítulo que estamos verificando,
                # verificar se estamos tentando ativar cenas de um capítulo futuro
                capitulos_ordem = ["ch1", "ch2", "ch3", "ch4", "ch5"]
                try:
                    indice_atual = capitulos_ordem.index(capitulo_atual_progresso)
                    indice_sistema = capitulos_ordem.index(chapter_id)
                    # PERMITIR cenas com enter_location_first_time mesmo em capítulos futuros
                    # (para permitir que Glub apareça antes do capítulo 4 se o jogador for até lá)
                    if indice_sistema > indice_atual and not verificar_ch4_adicional:
                        # Verificar se alguma cena deste capítulo tem enter_location_first_time
                        tem_enter_location_first_time = False
                        for scene in scenes:
                            start_trigger = scene.get("startTrigger", {})
                            if start_trigger.get("type") == "enter_location_first_time":
                                tem_enter_location_first_time = True
                                break
                        
                        if not tem_enter_location_first_time:
                            print(f"[NARRATIVA] Tentando ativar cenas do capítulo {chapter_id} mas jogador está no capítulo {capitulo_atual_progresso}, bloqueando...")
                            continue  # Pular este capítulo, mas verificar o próximo
                        else:
                            print(f"[NARRATIVA] Capítulo {chapter_id} tem cenas com enter_location_first_time, permitindo verificação mesmo estando no capítulo {capitulo_atual_progresso}")
                except ValueError:
                    pass  # Se não encontrar os capítulos na lista, continuar normalmente
            
            # Se há um context com raceId, priorizar cenas com gatilho race_finished
            # (scenes já foi obtido acima)
            if context and context.get("raceId"):
                # Separar cenas com gatilho race_finished das outras
                race_finished_scenes = []
                other_scenes = []
                for scene in scenes:
                    scene_id = scene.get("id")
                    # Pular se já foi visitada
                    if scene_id in self.scenes_visited:
                        continue
                    # Pular se já está ativa
                    if self.current_scene_id == scene_id:
                        continue
                    # Evitar reiniciar cenas de briefing após corrida ter sido completada
                    if context.get("raceId") == "training_01" and scene_id == "ch1_1b_crank_test_briefing":
                        print(f"[NARRATIVA] Pulando cena ch1_1b_crank_test_briefing após corrida training_01 (já foi visitada)")
                        continue
                    
                    trigger = scene.get("startTrigger", {})
                    if trigger.get("type") == "race_finished":
                        race_finished_scenes.append(scene)
                    else:
                        other_scenes.append(scene)
                
                # Verificar primeiro cenas com race_finished
                print(f"[NARRATIVA] Verificando {len(race_finished_scenes)} cenas com race_finished para raceId={context.get('raceId')}")
                for scene in race_finished_scenes:
                    scene_id = scene.get("id")
                    trigger = scene.get("startTrigger", {})
                    params = trigger.get("params", {})
                    print(f"[NARRATIVA] Verificando cena {scene_id} com trigger raceId={params.get('raceId')}")
                    if self.verificar_gatilho_cena(scene, context):
                        print(f"[NARRATIVA] Gatilho atendido para cena {scene_id}, iniciando...")
                        self.iniciar_cena(scene_id)
                        return True
                    else:
                        print(f"[NARRATIVA] Gatilho NÃO atendido para cena {scene_id}")
                
                # Depois verificar outras cenas
                for scene in other_scenes:
                    scene_id = scene.get("id")
                    if self.verificar_gatilho_cena(scene, context):
                        print(f"[NARRATIVA] Gatilho atendido para cena {scene_id}, iniciando...")
                        self.iniciar_cena(scene_id)
                        return True
                # Se não encontrou gatilho neste capítulo, continuar para o próximo
                continue
            else:
                # Sem context de corrida, verificar na ordem normal
                # PRIORIZAR cenas com requiredMission quando há context de location
                scenes_with_mission = []
                scenes_without_mission = []
                
                for scene in scenes:
                    scene_id = scene.get("id")
                    
                    # Pular se já foi visitada
                    if scene_id in self.scenes_visited:
                        print(f"[NARRATIVA] Cena {scene_id} já foi visitada, pulando verificação de gatilho")
                        continue
                    
                    # Pular se já está ativa
                    if self.current_scene_id == scene_id:
                        print(f"[NARRATIVA] Cena {scene_id} já está ativa, pulando verificação de gatilho")
                        continue
                    
                    # Evitar reiniciar cenas de briefing após corrida ter sido completada
                    # Se estamos processando um trigger de race_finished, não reiniciar cenas de briefing
                    if context and context.get("raceId") == "training_01" and scene_id == "ch1_1b_crank_test_briefing":
                        print(f"[NARRATIVA] Pulando cena ch1_1b_crank_test_briefing após corrida training_01 (já foi visitada)")
                        continue
                    
                    # Separar cenas com requiredMission das outras
                    start_trigger = scene.get("startTrigger", {})
                    params_trigger = start_trigger.get("params", {})
                    if params_trigger.get("requiredMission"):
                        scenes_with_mission.append(scene)
                    else:
                        scenes_without_mission.append(scene)
                
                # PRIORIZAR cenas com mais condições (requiredFlag + requiredItem) sobre cenas com menos condições
                # Isso garante que cenas mais específicas sejam verificadas primeiro
                scenes_with_more_conditions = []
                scenes_with_fewer_conditions = []
                
                for scene in scenes_without_mission:
                    start_trigger = scene.get("startTrigger", {})
                    params = start_trigger.get("params", {})
                    # Contar quantas condições a cena tem
                    condition_count = 0
                    if params.get("requiredItem"):
                        condition_count += 1
                    if params.get("requiredFlag"):
                        condition_count += 1
                    if params.get("requiredMission"):
                        condition_count += 1
                    if params.get("finishedQuest"):
                        condition_count += 1
                    
                    if condition_count > 1:
                        scenes_with_more_conditions.append(scene)
                    else:
                        scenes_with_fewer_conditions.append(scene)
                
                # Verificar primeiro cenas com requiredMission (prioridade máxima)
                for scene in scenes_with_mission:
                    scene_id = scene.get("id")
                    print(f"[NARRATIVA] Verificando gatilho para cena {scene_id} (com requiredMission) com context {context}")
                    if self.verificar_gatilho_cena(scene, context):
                        print(f"[NARRATIVA] Gatilho atendido para cena {scene_id}, iniciando...")
                        self.iniciar_cena(scene_id)
                        return True
                    else:
                        print(f"[NARRATIVA] Gatilho NÃO atendido para cena {scene_id}")
                
                # Depois verificar cenas com mais condições (requiredFlag + requiredItem, etc.)
                for scene in scenes_with_more_conditions:
                    scene_id = scene.get("id")
                    print(f"[NARRATIVA] Verificando gatilho para cena {scene_id} (com múltiplas condições) com context {context}")
                    if self.verificar_gatilho_cena(scene, context):
                        print(f"[NARRATIVA] Gatilho atendido para cena {scene_id}, iniciando...")
                        self.iniciar_cena(scene_id)
                        return True
                    else:
                        print(f"[NARRATIVA] Gatilho NÃO atendido para cena {scene_id}")
                
                # Por último, verificar cenas com menos condições
                for scene in scenes_with_fewer_conditions:
                    scene_id = scene.get("id")
                    print(f"[NARRATIVA] Verificando gatilho para cena {scene_id} com context {context}")
                    if self.verificar_gatilho_cena(scene, context):
                        print(f"[NARRATIVA] Gatilho atendido para cena {scene_id}, iniciando...")
                        self.iniciar_cena(scene_id)
                        return True
                    else:
                        print(f"[NARRATIVA] Gatilho NÃO atendido para cena {scene_id}")
        
        return False
    
    def verificar_gatilho_por_location(self, location_id: str):
        """Verifica gatilhos de enter_location para um local específico"""
        context = {"locationId": location_id}
        return self.verificar_gatilhos_pendentes(context)
    
    def verificar_gatilho_por_race(self, race_id: str, race_result: str = "any"):
        """Verifica gatilhos de race_finished para uma corrida específica"""
        context = {"raceId": race_id, "raceResult": race_result}
        return self.verificar_gatilhos_pendentes(context)
    
    def _verificar_condicoes(self, conditions: List[str]) -> bool:
        """Verifica se todas as condições são atendidas"""
        from core.progresso import gerenciador_progresso
        
        for condition in conditions:
            # Verificar condições que começam com requiredFlag: (sem =)
            if condition.startswith("requiredFlag:"):
                flag_name = condition.split(":")[1]
                flag_value = self.flags.get(flag_name, False)
                # Também verificar no progresso (para flags como crownCircuitActive)
                if not flag_value:
                    flag_value = getattr(gerenciador_progresso, flag_name, False)
                if not flag_value:
                    return False
            elif "=" in condition:
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
                    # Verificar performance da corrida
                    performance = self.variables.get("racePerformance", "")
                    if value != performance:
                        return False
                elif key == "refusedDebt":
                    # Verificar se recusou a dívida
                    if value == "true":
                        if getattr(gerenciador_progresso, 'barao_emprestimo_ativo', False):
                            return False
                    elif value == "false":
                        if not getattr(gerenciador_progresso, 'barao_emprestimo_ativo', False):
                            return False
                elif key.startswith("locationUnlocked:"):
                    location = key.split(":")[1]
                    should_be_unlocked = value == "true"
                    from core.mapa_locations import gerenciador_localizacoes
                    is_unlocked = gerenciador_localizacoes.esta_desbloqueado(location)
                    print(f"[NARRATIVA] Verificando condição locationUnlocked:{location}={value}: should_be_unlocked={should_be_unlocked}, is_unlocked={is_unlocked}")
                    if should_be_unlocked != is_unlocked:
                        print(f"[NARRATIVA] Condição locationUnlocked:{location}={value} NÃO atendida")
                        return False
                    print(f"[NARRATIVA] Condição locationUnlocked:{location}={value} atendida ✓")
                elif key.startswith("requiredFlag:"):
                    # Verificar se uma flag específica está ativa
                    flag_name = key.split(":")[1]
                    flag_value = self.flags.get(flag_name, False)
                    # Também verificar no progresso (para flags como crownCircuitActive)
                    if not flag_value:
                        from core.progresso import gerenciador_progresso
                        flag_value = getattr(gerenciador_progresso, flag_name, False)
                    if not flag_value:
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
            
            # Salvar flags importantes no progresso também
            from core.progresso import gerenciador_progresso
            
            if flag_name == "hasDebt":
                from core.barao import barao
                # Ativar empréstimo do Barão
                gerenciador_progresso.barao_emprestimo_ativo = True
                gerenciador_progresso.barao_valor_devido = barao.VALOR_TOTAL
                gerenciador_progresso.barao_corridas_restantes = barao.PRAZO_CORRIDAS
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Empréstimo do Barão ativado: valor_devido={gerenciador_progresso.barao_valor_devido}, corridas_restantes={gerenciador_progresso.barao_corridas_restantes}")
            elif flag_name == "crownCircuitActive":
                # Salvar flag do Circuito da Coroa no progresso
                gerenciador_progresso.crownCircuitActive = True
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Flag crownCircuitActive salva no progresso")
            elif flag_name == "housingActive":
                # Salvar flag de habilitar opção de casa no progresso
                gerenciador_progresso.housingActive = True
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Flag housingActive salva no progresso")
            elif flag_name == "akira_nome_revelado":
                # Revelar nome da Akira
                gerenciador_progresso.akira_nome_revelado = True
                try:
                    from core.akira import akira
                    akira.nome_revelado = True
                    akira.salvar_estado()
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao salvar estado da Akira: {e}")
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Nome da Akira revelado e salvo: akira_nome_revelado={gerenciador_progresso.akira_nome_revelado}")
        elif effect.startswith("unlockLocation:"):
            location = effect.split(":", 1)[1]
            try:
                from core.mapa_locations import gerenciador_localizacoes
                from core.progresso import gerenciador_progresso
                gerenciador_localizacoes.desbloquear(location)
                # Marcar que foi desbloqueado pela narrativa
                if not hasattr(gerenciador_progresso, 'locations_unlocked_by_narrative'):
                    gerenciador_progresso.locations_unlocked_by_narrative = {}
                gerenciador_progresso.locations_unlocked_by_narrative[location] = True
                gerenciador_progresso.salvar()
                print(f"[NARRATIVA] Desbloqueando localização: {location} (marcado como desbloqueado pela narrativa)")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao desbloquear localização {location}: {e}")
        elif effect.startswith("unlockRace:") or effect.startswith("unlockRaceSet:"):
            race = effect.split(":", 1)[1]
            if effect.startswith("unlockRaceSet:"):
                try:
                    from core.mapa_locations import gerenciador_localizacoes
                    from core.progresso import gerenciador_progresso
                    gerenciador_localizacoes.processar_efeito_narrativa(effect)
                    # Se desbloqueou o Cinturão, definir flag cinturaoUnlocked
                    if race == "cinturao_industrial":
                        self.flags["cinturaoUnlocked"] = True
                        gerenciador_progresso.cinturaoUnlocked = True
                        gerenciador_progresso.salvar()
                        print(f"[NARRATIVA] Flag cinturaoUnlocked definida após desbloquear Cinturão")
                    # Desbloquear apenas a primeira etapa do Circuito da Coroa (as outras serão desbloqueadas sequencialmente)
                    elif race == "crown_circuit_stages":
                        if not hasattr(gerenciador_progresso, 'corridas_desbloqueadas'):
                            gerenciador_progresso.corridas_desbloqueadas = set()
                        if isinstance(gerenciador_progresso.corridas_desbloqueadas, list):
                            gerenciador_progresso.corridas_desbloqueadas = set(gerenciador_progresso.corridas_desbloqueadas)
                        # Desbloquear apenas a primeira etapa
                        gerenciador_progresso.corridas_desbloqueadas.add("crown_stage1")
                        gerenciador_progresso.salvar()
                        print(f"[NARRATIVA] Primeira etapa do Circuito da Coroa desbloqueada (as outras serão desbloqueadas sequencialmente)")
                    print(f"[NARRATIVA] Desbloqueando conjunto de corridas: {race}")
                except Exception as e:
                    print(f"[NARRATIVA] Erro ao desbloquear conjunto de corridas {race}: {e}")
                    import traceback
                    traceback.print_exc()
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
        elif effect.startswith("unlockFeature:"):
            feature = effect.split(":", 1)[1]
            try:
                from core.progresso import gerenciador_progresso
                if feature == "scrapSell":
                    gerenciador_progresso.glub_desbloqueado = True
                    gerenciador_progresso.salvar()
                    print(f"[NARRATIVA] Feature {feature} desbloqueada (Glub agora está disponível)")
                else:
                    # Para outras features futuras
                    setattr(gerenciador_progresso, f"{feature}_desbloqueado", True)
                    gerenciador_progresso.salvar()
                    print(f"[NARRATIVA] Feature {feature} desbloqueada")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao desbloquear feature {feature}: {e}")
                import traceback
                traceback.print_exc()
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
            # Instalar primeiro upgrade e completar missão m5
            try:
                from core.progresso import gerenciador_progresso
                from core.missoes import gerenciador_missoes
                
                # Marcar que o primeiro upgrade foi instalado (se necessário)
                # A instalação real do upgrade já foi feita quando a peça foi comprada do Boris
                # Aqui apenas completamos a missão m5
                if "m5_cirurgia_na_garagem" not in gerenciador_missoes.missoes_completas:
                    gerenciador_missoes.completar_missao("m5_cirurgia_na_garagem")
                    gerenciador_missoes.salvar()
                    print(f"[NARRATIVA] Primeiro upgrade instalado e missão m5_cirurgia_na_garagem completada")
                else:
                    print(f"[NARRATIVA] Primeiro upgrade instalado (missão m5 já estava completa)")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao instalar primeiro upgrade: {e}")
                import traceback
                traceback.print_exc()
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
                # Atualizar current_chapter_id do narrative_system também
                self.current_chapter_id = chapter_id
                print(f"[NARRATIVA] Capítulo {chapter_id} iniciado")
            except Exception as e:
                print(f"[NARRATIVA] Erro ao iniciar capítulo: {e}")
        elif effect == "endGame":
            # Fim do jogo - após os créditos, fechar narrativa e voltar ao menu principal
            print(f"[NARRATIVA] Fim do jogo - créditos finalizados")
            # A narrativa será fechada quando nextSceneId for null na última cena de créditos
    
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
        
        # Verificar se é cena de créditos - usar sistema especial
        if self.current_scene_id == "ch5_10_creditos":
            self._desenhar_creditos(tela)
            return
        
        # Se não há cena atual, desenhar tela preta e retornar
        if not self.current_scene_id:
            tela.fill((0, 0, 0))
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
                    bg_atual = self.backgrounds[bg_name]
                    tela.blit(bg_atual, (0, 0))
                    # Guardar este background como último background válido
                    self.ultimo_background = bg_atual
                else:
                    print(f"[NARRATIVA] ERRO: Não foi possível carregar background {bg_name}, usando fallback")
                    # Fallback: fundo escuro (mas não completamente preto para debug)
                    tela.fill((20, 20, 30))
            else:
                # Sem background definido (bg: null) - usar último background para fade gradual
                if self.ultimo_background:
                    # Sempre usar o último background se disponível
                    tela.blit(self.ultimo_background, (0, 0))
                elif self.time_skip_active:
                    # Durante o fade, mostrar o último background e escurecer gradualmente
                    if self.ultimo_background:
                        tela.blit(self.ultimo_background, (0, 0))
                    else:
                        tela.fill((20, 20, 30))
                else:
                    # Se não há background anterior ou não está em fade, usar tela escura (não completamente preta)
                    tela.fill((20, 20, 30))
        else:
            # Se não há cena, usar tela escura
            tela.fill((20, 20, 30))
        
        if self.hover_sprite_atual:
            tela.blit(self.hover_sprite_atual, (0, 0))
        
        # Desenhar sprites (sem prints excessivos a cada frame)
        for sprite_id, sprite_data in self.scene_sprites.items():
            sprite = sprite_data["sprite"]
            position = sprite_data["position"]
            
            if sprite is None:
                continue
            
            sprite_original_w, sprite_original_h = sprite.get_size()
            if sprite_original_w == 0 or sprite_original_h == 0:
                continue
            
            # Slick deve ser maior que os outros personagens
            if sprite_id == "slick":
                sprite_altura_max = 900  # Muito maior que os outros
                sprite_largura_max = 800
            else:
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
                # Slick deve estar mais centralizado quando está à direita
                if sprite_id == "slick":
                    sprite_x = LARGURA - sprite_w - 100  # Mais próximo do centro
                else:
                    sprite_x = LARGURA - sprite_w - 50  # Posição à direita, mas não muito longe
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
            # Para cenas com bg null (tela preta), fazer fade gradual também
            scene = self._obter_cena_atual()
            bg_name = scene.get("bg") if scene else None
            
            # Aplicar overlay escuro gradual em todas as cenas (com ou sem bg)
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
        
        if self.current_scene_id == "ch1_3_boris_deal":
            print(f"[NARRATIVA] Exibindo linha {self.current_line_index} do Boris (total: {len(lines)}): {line.get('text', '')[:80]}...")
            if self.current_line_index == 1:
                print(f"[NARRATIVA] ✓ Segunda linha do Boris sobre o Cinturão Industrial está sendo exibida!")
        
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
        elif speaker.upper() == "AKIRA":
            # Verificar se o nome da Akira foi revelado
            from core.progresso import gerenciador_progresso
            # Recarregar o progresso para garantir que temos o valor mais recente
            try:
                gerenciador_progresso.carregar()
            except:
                pass
            if hasattr(gerenciador_progresso, 'akira_nome_revelado') and gerenciador_progresso.akira_nome_revelado:
                nome = "AKIRA"
            else:
                nome = "???"
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
            
            # Usar padrão de botões do jogo
            if i == self.selected_choice:
                # Botão selecionado
                cor_fundo = (0, 150, 255, 120)  # Azul ciano vibrante
                cor_borda = (0, 200, 255)  # Borda azul ciano
                cor_texto = (255, 255, 255)  # Texto branco
            else:
                # Botão normal
                cor_fundo = (0, 0, 0, 150)  # Preto semi-transparente
                cor_borda = (255, 255, 255)  # Borda branca
                cor_texto = (255, 255, 255)  # Texto branco
            
            choice_rect = pygame.Rect(50, choice_y, LARGURA - 100, choice_height)
            
            # Desenhar fundo do botão
            botao_fundo = pygame.Surface((choice_rect.width, choice_rect.height), pygame.SRCALPHA)
            botao_fundo.fill(cor_fundo)
            tela.blit(botao_fundo, choice_rect.topleft)
            
            # Desenhar borda
            pygame.draw.rect(tela, cor_borda, choice_rect, 3)
            
            # Desenhar texto
            texto_render = render_text(choice_text, 20, cor_texto, bold=True, pixel_style=True)
            texto_x = 50 + (choice_rect.width - texto_render.get_width()) // 2
            tela.blit(texto_render, (texto_x, choice_y + (choice_height - texto_render.get_height()) // 2))
    
    def _atualizar_creditos(self, dt: float):
        """Atualiza o sistema de créditos com backgrounds animados"""
        from config import LARGURA, ALTURA
        
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        lines = scene.get("lines", [])
        if not lines:
            return
        
        # Filtrar linhas vazias
        textos_creditos = [line.get("text", "").strip() for line in lines if line.get("text", "").strip()]
        
        if not textos_creditos:
            return
        
        # Inicializar sistema de créditos na primeira vez
        if not self.creditos_auto_advance:
            self.creditos_auto_advance = True
            self.creditos_tempo_mostrado = 0.0
            self.creditos_texto_atual_index = 0
            self.creditos_background_index = 0
            self.creditos_texto_fade_alpha = 0.0
            self.creditos_texto_fade_direction = 1
            self.creditos_background_alpha = 1.0
            self.creditos_background_fade_direction = 0
            # Carregar primeiro background
            self._carregar_background_creditos(0)
        
        self.creditos_tempo_mostrado += dt
        
        # Calcular fase atual do texto
        tempo_total_por_texto = self.creditos_tempo_por_texto + self.creditos_tempo_fade * 2
        tempo_no_texto = self.creditos_tempo_mostrado % tempo_total_por_texto
        
        # Fade in do texto
        if tempo_no_texto < self.creditos_tempo_fade:
            self.creditos_texto_fade_alpha = min(1.0, tempo_no_texto / self.creditos_tempo_fade)
            self.creditos_texto_fade_direction = 1
        # Texto visível
        elif tempo_no_texto < self.creditos_tempo_fade + self.creditos_tempo_por_texto:
            self.creditos_texto_fade_alpha = 1.0
        # Fade out do texto
        elif tempo_no_texto < self.creditos_tempo_fade * 2 + self.creditos_tempo_por_texto:
            fade_out_progress = (tempo_no_texto - self.creditos_tempo_fade - self.creditos_tempo_por_texto) / self.creditos_tempo_fade
            self.creditos_texto_fade_alpha = max(0.0, 1.0 - fade_out_progress)
            self.creditos_texto_fade_direction = -1
        # Transição para próximo texto
        else:
            # Avançar para próximo texto
            self.creditos_texto_atual_index += 1
            if self.creditos_texto_atual_index >= len(textos_creditos):
                # Todos os textos foram mostrados, finalizar créditos
                self._finalizar_creditos()
                return
            # Resetar timer e fade
            self.creditos_tempo_mostrado = 0.0
            self.creditos_texto_fade_alpha = 0.0
            self.creditos_texto_fade_direction = 1
            # Mudar background a cada 2 textos
            if self.creditos_texto_atual_index % 2 == 0:
                self.creditos_background_index = (self.creditos_background_index + 1) % len(self.creditos_backgrounds)
                self._carregar_background_creditos(self.creditos_background_index)
    
    def _carregar_background_creditos(self, index: int):
        """Carrega um background para os créditos"""
        from config import LARGURA, ALTURA
        
        if index >= len(self.creditos_backgrounds):
            return
        
        bg_name = self.creditos_backgrounds[index]
        bg_key = f"creditos_{index}"
        
        if bg_key in self.creditos_backgrounds_carregados:
            return
        
        bg_path = os.path.join(CAMINHO_BACKGROUNDS, bg_name)
        if os.path.exists(bg_path):
            try:
                bg = pygame.image.load(bg_path).convert()
                bg_scaled = pygame.transform.scale(bg, (LARGURA, ALTURA))
                self.creditos_backgrounds_carregados[bg_key] = bg_scaled
                print(f"[CRÉDITOS] Background {bg_name} carregado")
            except Exception as e:
                print(f"[CRÉDITOS] Erro ao carregar background {bg_name}: {e}")
                # Fallback: fundo escuro
                self.creditos_backgrounds_carregados[bg_key] = pygame.Surface((LARGURA, ALTURA))
                self.creditos_backgrounds_carregados[bg_key].fill((20, 20, 30))
        else:
            # Fallback: fundo escuro
            self.creditos_backgrounds_carregados[bg_key] = pygame.Surface((LARGURA, ALTURA))
            self.creditos_backgrounds_carregados[bg_key].fill((20, 20, 30))
    
    def _desenhar_creditos(self, tela: pygame.Surface):
        """Desenha os créditos com backgrounds animados e texto com fade"""
        from config import LARGURA, ALTURA
        render_text = _get_render_text()
        
        scene = self._obter_cena_atual()
        if not scene:
            return
        
        lines = scene.get("lines", [])
        textos_creditos = [line.get("text", "").strip() for line in lines if line.get("text", "").strip()]
        
        if not textos_creditos or self.creditos_texto_atual_index >= len(textos_creditos):
            return
        
        # Desenhar background atual
        bg_key = f"creditos_{self.creditos_background_index}"
        if bg_key in self.creditos_backgrounds_carregados:
            bg = self.creditos_backgrounds_carregados[bg_key]
            tela.blit(bg, (0, 0))
        else:
            tela.fill((20, 20, 30))
        
        # Overlay escuro
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Escurecer bastante
        tela.blit(overlay, (0, 0))
        
        # Desenhar texto centralizado com fade
        texto_atual = textos_creditos[self.creditos_texto_atual_index]
        if texto_atual:
            # Calcular alpha do texto
            texto_alpha = int(self.creditos_texto_fade_alpha * 255)
            
            # Renderizar texto
            fonte_tamanho = 56 if texto_atual == "TURBO RACER" else 36
            texto_render = render_text(texto_atual, fonte_tamanho, (255, 255, 255), bold=True, pixel_style=True)
            
            # Criar superfície com alpha para aplicar fade
            texto_surface = pygame.Surface((texto_render.get_width(), texto_render.get_height()), pygame.SRCALPHA)
            # Preencher com cor branca e alpha
            texto_surface.fill((255, 255, 255, texto_alpha))
            # Blit do texto renderizado usando BLEND_RGBA_MULT para aplicar o alpha
            texto_surface.blit(texto_render, (0, 0))
            # Aplicar alpha usando set_alpha
            texto_surface.set_alpha(texto_alpha)
            
            # Centralizar na tela
            texto_x = (LARGURA - texto_render.get_width()) // 2
            texto_y = ALTURA // 2 - texto_render.get_height() // 2
            
            tela.blit(texto_surface, (texto_x, texto_y))
    
    def _finalizar_creditos(self):
        """Finaliza os créditos e marca o jogo como terminado"""
        self.creditos_auto_advance = False
        self.game_ended = True
        self.active = False
        print(f"[CRÉDITOS] Créditos finalizados, marcando game_ended=True")
    
    def fechar(self):
        """Fecha o sistema de narrativa"""
        self.active = False

narrative_system = NarrativeSystem()

