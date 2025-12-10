# src/core/missoes.py
import json
import os
from config import DIR_PROJETO

CAMINHO_MISSOES = os.path.join(DIR_PROJETO, "data", "missions.json")
CAMINHO_MISSOES_COMPLETAS = os.path.join(DIR_PROJETO, "data", "missoes_completas.json")
CAMINHO_MISSOES_INFO = os.path.join(DIR_PROJETO, "data", "missions_info.json")

class GerenciadorMissoes:
    """Gerencia as missões do jogo: ativação, conclusão e exibição no HUD"""
    
    def __init__(self):
        self.missoes = {}
        self.missao_ativa_id = None
        self.missoes_completas = set()
        self.missoes_info = {}  # Informações detalhadas das missões
        self.carregar()
    
    def carregar(self):
        """Carrega as missões do arquivo JSON"""
        if os.path.exists(CAMINHO_MISSOES):
            try:
                with open(CAMINHO_MISSOES, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for missao in data.get("missions", []):
                        self.missoes[missao["id"]] = {
                            "id": missao["id"],
                            "nome": missao.get("nome", missao["id"]),
                            "objetivo": missao.get("objetivo", ""),
                            "activateOnSceneId": missao.get("activateOnSceneId"),
                            "completeOnSceneId": missao.get("completeOnSceneId"),
                            "chapter": missao.get("chapter", "ch1")
                        }
            except Exception as e:
                print(f"Erro ao carregar missões: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Arquivo de missões não encontrado: {CAMINHO_MISSOES}")
        
        # Carregar missões completas
        self._carregar_missoes_completas()
        
        # IMPORTANTE: Para novos saves (nenhuma missão completa), ativar m1_primeira_faisca imediatamente
        # Usar try/except para evitar importação circular
        if len(self.missoes_completas) == 0:
            try:
                from core.progresso import gerenciador_progresso
                capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                if not capitulo_atual:
                    capitulo_atual = "ch1"
                    gerenciador_progresso.definir_capitulo_atual("ch1")
                    gerenciador_progresso.salvar()
                
                if capitulo_atual == "ch1" and "m1_primeira_faisca" in self.missoes:
                    if not self.missao_ativa_id or self.missao_ativa_id != "m1_primeira_faisca":
                        print(f"[MISSÕES] ====== NOVO SAVE: ATIVANDO m1_primeira_faisca NO CARREGAMENTO ======")
                        self.ativar_missao("m1_primeira_faisca", forcar_ativacao=True)
                        self.salvar()
                        print(f"[MISSÕES] m1_primeira_faisca ativada! missao_ativa_id={self.missao_ativa_id}")
            except ImportError as e:
                # Importação circular - tentar novamente depois
                print(f"[MISSÕES] Importação circular detectada ao ativar m1_primeira_faisca, será ativada depois: {e}")
            except Exception as e:
                print(f"[MISSÕES] Erro ao ativar m1_primeira_faisca no carregamento: {e}")
        
        # Verificar se m15_ruido_nos_servidores deve ser completada (jogador já foi até o Pixel)
        self._verificar_missao_pixel_completa()
        
        # Verificar se m19 deve ser ativada (jogador já venceu as 3 etapas do Circuito da Coroa)
        self._verificar_missao_m19_ativacao()
        
        # Carregar informações detalhadas das missões
        self._carregar_missoes_info()
    
    def _verificar_missao_pixel_completa(self):
        """Verifica se a missão m15_ruido_nos_servidores deve ser completada (jogador já foi até o Pixel)"""
        try:
            from core.progresso import gerenciador_progresso
            from core.narrative_system import narrative_system
            # Se o jogador já foi até o Pixel mas a missão não foi completada
            if hasattr(gerenciador_progresso, 'pixel_primeira_aparicao_mostrada') and gerenciador_progresso.pixel_primeira_aparicao_mostrada:
                if "m15_ruido_nos_servidores" in self.missoes and "m15_ruido_nos_servidores" not in self.missoes_completas:
                    print(f"[MISSÕES] Jogador já foi até o Pixel, completando missão m15_ruido_nos_servidores...")
                    self.completar_missao("m15_ruido_nos_servidores")
            
            # Verificar se m15 foi completada - se sim, ativar m16 (jogador já foi até o Pixel)
            if "m15_ruido_nos_servidores" in self.missoes_completas:
                # Se m16 não foi completada e não está ativa, ativar
                if "m16_conhecer_glub" in self.missoes and "m16_conhecer_glub" not in self.missoes_completas:
                    if not self.missao_ativa_id or self.missao_ativa_id != "m16_conhecer_glub":
                        print(f"[MISSÕES] Jogador já completou m15, ativando missão m16_conhecer_glub...")
                        self.ativar_missao("m16_conhecer_glub")
        except Exception as e:
            print(f"[MISSÕES] Erro ao verificar missão do Pixel: {e}")
    
    def _verificar_missao_m19_ativacao(self):
        """Verifica se a missão m19_jogo_do_rei deve ser ativada (jogador já venceu as 3 etapas do Circuito da Coroa)"""
        try:
            from core.progresso import gerenciador_progresso
            # Verificar se as 3 etapas foram vencidas
            if hasattr(gerenciador_progresso, 'crown_stages_won'):
                crown_stages_won = gerenciador_progresso.crown_stages_won
                # Converter para set se for lista
                if isinstance(crown_stages_won, list):
                    crown_stages_won = set(crown_stages_won)
                
                # Verificar se todas as 3 etapas foram vencidas
                venceu_todas = (
                    "crown_stage1" in crown_stages_won and
                    "crown_stage2" in crown_stages_won and
                    "crown_stage3" in crown_stages_won
                )
                
                if venceu_todas:
                    # Se m18 foi completada e m19 não foi completada nem está ativa, ativar m19
                    if "m18_circo_da_coroa" in self.missoes_completas:
                        if "m19_jogo_do_rei" in self.missoes and "m19_jogo_do_rei" not in self.missoes_completas:
                            if not self.missao_ativa_id or self.missao_ativa_id != "m19_jogo_do_rei":
                                print(f"[MISSÕES] Jogador já venceu as 3 etapas do Circuito da Coroa, ativando missão m19_jogo_do_rei...")
                                if self.ativar_missao("m19_jogo_do_rei", forcar_ativacao=True):
                                    self.salvar()
                                    print(f"[MISSÕES] Missão m19_jogo_do_rei ativada com sucesso!")
                                else:
                                    print(f"[MISSÕES] Não foi possível ativar missão m19_jogo_do_rei")
        except Exception as e:
            print(f"[MISSÕES] Erro ao verificar ativação da missão m19: {e}")
            import traceback
            traceback.print_exc()
    
    def _carregar_missoes_info(self):
        """Carrega informações detalhadas das missões do arquivo missions_info.json"""
        if os.path.exists(CAMINHO_MISSOES_INFO):
            try:
                with open(CAMINHO_MISSOES_INFO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.missoes_info = data.get("missions", {})
            except Exception as e:
                print(f"Erro ao carregar informações detalhadas das missões: {e}")
        else:
            print(f"Arquivo de informações detalhadas não encontrado: {CAMINHO_MISSOES_INFO}")
    
    def _carregar_missoes_completas(self):
        """Carrega as missões completas do progresso.json"""
        # Primeiro, tentar carregar do progresso.json (fonte principal)
        try:
            from core.progresso import gerenciador_progresso, CAMINHO_PROGRESSO
            
            if os.path.exists(CAMINHO_PROGRESSO):
                with open(CAMINHO_PROGRESSO, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Sempre carregar do progresso.json se existir (mesmo que vazio)
                    self.missoes_completas = set(data.get('missoes_completas', []))
                    self.missao_ativa_id = data.get('missao_ativa_id', None)
                    # Debug removido
                    # Continuar com a lógica de validação abaixo
                    if self.missao_ativa_id:
                        # Verificar se a missão existe no dicionário de missões
                        if self.missao_ativa_id not in self.missoes:
                            print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} não existe no dicionário de missões, limpando...")
                            self.missao_ativa_id = None
                            self.salvar()
                        elif self.missao_ativa_id in self.missoes_completas:
                            print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} já foi completada, limpando...")
                            self.missao_ativa_id = None
                            self.salvar()
                        else:
                            # Validar se a missão ativa é apropriada para o progresso atual
                            if not self._validar_missao_ativa_apropriada():
                                print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} não é apropriada para o progresso atual, limpando...")
                                self.missao_ativa_id = None
                                self.salvar()
                                # Tentar ativar a próxima missão correta automaticamente
                                self._ativar_proxima_missao_automaticamente()
                                if self.missao_ativa_id:
                                    print(f"[MISSÕES] Missão {self.missao_ativa_id} ativada automaticamente após limpar missão inválida")
                    # Remover arquivo antigo se existir (migração completa)
                    if os.path.exists(CAMINHO_MISSOES_COMPLETAS):
                        try:
                            os.remove(CAMINHO_MISSOES_COMPLETAS)
                            print(f"[MISSÕES] Arquivo antigo missoes_completas.json removido após migração")
                        except Exception as e:
                            print(f"[MISSÕES] Erro ao remover arquivo antigo: {e}")
                    return  # Dados carregados do progresso.json
            else:
                # Progresso.json não existe - resetar tudo para valores padrão
                print(f"[MISSÕES] progresso.json não existe, resetando missões...")
                self.missoes_completas = set()
                self.missao_ativa_id = None
                # Remover arquivo antigo se existir
                if os.path.exists(CAMINHO_MISSOES_COMPLETAS):
                    try:
                        os.remove(CAMINHO_MISSOES_COMPLETAS)
                        print(f"[MISSÕES] Arquivo antigo missoes_completas.json removido")
                    except Exception as e:
                        print(f"[MISSÕES] Erro ao remover arquivo antigo: {e}")
                return
        except Exception as e:
            print(f"[MISSÕES] Erro ao carregar do progresso.json: {e}")
            # Em caso de erro, resetar para valores padrão
            self.missoes_completas = set()
            self.missao_ativa_id = None
            return
        
        # Fallback: tentar carregar do arquivo antigo se ainda existir (migração)
        # NOTA: Este fallback só deve ser usado se o progresso.json existir mas não tiver os dados
        if os.path.exists(CAMINHO_MISSOES_COMPLETAS):
            try:
                with open(CAMINHO_MISSOES_COMPLETAS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.missoes_completas = set(data.get("missoes_completas", []))
                    self.missao_ativa_id = data.get("missao_ativa_id", None)
                    
                    # Se a missão ativa já foi completada, limpar
                    if self.missao_ativa_id:
                        if self.missao_ativa_id in self.missoes_completas:
                            print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} já foi completada, limpando...")
                            self.missao_ativa_id = None
                            self.salvar()  # Salvar imediatamente para corrigir o arquivo
                        else:
                            # Verificar se o jogador já avançou muito no jogo (7+ missões completas)
                            # Se sim, e a missão ativa é antiga (m1-m7), limpar e ativar a próxima correta
                            if len(self.missoes_completas) >= 7:
                                # Extrair número da missão ativa
                                try:
                                    missao_num = int(self.missao_ativa_id.split("_")[0].replace("m", ""))
                                except:
                                    missao_num = 0
                                
                                # Se a missão ativa é muito antiga (m1-m7) mas não está completa,
                                # e o jogador já completou 7 missões, provavelmente está no capítulo 3
                                if missao_num <= 7:
                                    print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} é antiga e não está completa, mas jogador já completou {len(self.missoes_completas)} missões. Limpando e ativando próxima...")
                                    self.missao_ativa_id = None
                                    self.salvar()
                    
                print(f"[MISSÕES] Missões carregadas: {len(self.missoes_completas)} completas, ativa: {self.missao_ativa_id}")
                
                # Verificar se m14_tres_mundos deve ser completada (reputação >= 500)
                try:
                    from core.status_jogador import status_jogador
                    # Garantir que o status está carregado
                    status_jogador.carregar()
                    popularidade_atual = status_jogador.popularidade
                    print(f"[MISSÕES] Verificando reputação no carregamento: {popularidade_atual:.1f}/500, missao_ativa={self.missao_ativa_id}, m14_completa={'m14_tres_mundos' in self.missoes_completas}")
                    if popularidade_atual >= 500.0:
                        if self.missao_ativa_id == "m14_tres_mundos":
                            if "m14_tres_mundos" not in self.missoes_completas:
                                print(f"[MISSÕES] Reputação já está em 500! Completando missão m14_tres_mundos no carregamento...")
                                self.completar_missao("m14_tres_mundos")
                                self.salvar()
                        else:
                            print(f"[MISSÕES] Reputação >= 500 mas missão ativa é {self.missao_ativa_id}, não m14_tres_mundos")
                    elif self.missao_ativa_id == "m14_tres_mundos":
                        print(f"[MISSÕES] Missão m14_tres_mundos ativa mas reputação é {popularidade_atual:.1f}, ainda não chegou a 500")
                except Exception as e:
                    print(f"[MISSÕES] Erro ao verificar reputação para m14_tres_mundos no carregamento: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Verificar consistência das missões após carregar
                self.verificar_consistencia_missoes()
                
                # Se não há missão ativa após carregar, tentar ativar automaticamente
                if not self.missao_ativa_id:
                    print(f"[MISSÕES] Nenhuma missão ativa após carregar, tentando ativar automaticamente...")
                    self._ativar_proxima_missao_automaticamente()
                    if self.missao_ativa_id:
                        print(f"[MISSÕES] Missão {self.missao_ativa_id} ativada automaticamente após carregar")
            except Exception as e:
                print(f"[MISSÕES] Erro ao carregar missões completas: {e}")
                import traceback
                traceback.print_exc()
                self.missoes_completas = set()
        else:
            print(f"[MISSÕES] Arquivo de missões completas não encontrado: {CAMINHO_MISSOES_COMPLETAS}")
            self.missoes_completas = set()
            # Tentar ativar automaticamente se não há arquivo
            if not self.missao_ativa_id:
                self._ativar_proxima_missao_automaticamente()
    
    def salvar(self):
        """Salva as missões completas"""
        # Dados são salvos através do GerenciadorProgresso.salvar()
        # Este método existe para compatibilidade, mas não salva mais em arquivo separado
        try:
            from core.progresso import gerenciador_progresso
            gerenciador_progresso.salvar()  # Isso salvará tudo, incluindo missões
            print(f"[MISSÕES] Missões salvas no progresso.json: {len(self.missoes_completas)} completas, ativa: {self.missao_ativa_id}")
        except Exception as e:
            print(f"[MISSÕES] Erro ao salvar missões: {e}")
            import traceback
            traceback.print_exc()
    
    def ativar_missao(self, missao_id: str, forcar_ativacao=False):
        """Ativa uma missão
        
        Args:
            missao_id: ID da missão a ser ativada
            forcar_ativacao: Se True, ativa a missão mesmo que tenha activateOnSceneId
        """
        if missao_id not in self.missoes:
            print(f"[MISSÕES] Tentativa de ativar missão inexistente: {missao_id}")
            return False
        
        if missao_id in self.missoes_completas:
            print(f"[MISSÕES] Tentativa de ativar missão já completada: {missao_id}")
            return False
        
        # Obter informações da missão
        missao = self.missoes[missao_id]
        activate_on_scene = missao.get("activateOnSceneId")
        
        # Verificar se a missão tem activateOnSceneId e se não estamos forçando
        if activate_on_scene and not forcar_ativacao:
            # Verificar se a cena já foi visitada
            try:
                from core.narrative_system import narrative_system
                scenes_visited = getattr(narrative_system, 'scenes_visited', set())
                if activate_on_scene not in scenes_visited:
                    print(f"[MISSÕES] Missão {missao_id} requer cena {activate_on_scene} que ainda não foi visitada. Use forcar_ativacao=True para ativar diretamente.")
                    return False
            except Exception as e:
                print(f"[MISSÕES] Erro ao verificar cena para {missao_id}: {e}")
                # Se houver erro, permitir ativação se forçar
                if not forcar_ativacao:
                    return False
        
        # Desbloquear localizações relacionadas quando missões são ativadas
        if missao_id == "m11_chamado_da_montanha":
            # Desbloquear montanha quando m11 é ativada
            from core.mapa_locations import gerenciador_localizacoes
            if not gerenciador_localizacoes.esta_desbloqueado("montanha"):
                print(f"[MISSÕES] Desbloqueando montanha para missão m11_chamado_da_montanha")
                gerenciador_localizacoes.desbloquear("montanha")
                gerenciador_localizacoes.salvar()
        elif missao_id == "m18_circo_da_coroa":
            # Desbloquear autódromo quando m18 é ativada
            from core.mapa_locations import gerenciador_localizacoes
            if not gerenciador_localizacoes.esta_desbloqueado("autódromo"):
                print(f"[MISSÕES] Desbloqueando autódromo para missão m18_circo_da_coroa")
                gerenciador_localizacoes.desbloquear("autódromo")
                gerenciador_localizacoes.salvar()
        
        # Verificar se a cena de conclusão já foi visitada
        missao = self.missoes[missao_id]
        complete_on_scene = missao.get("completeOnSceneId")
        if complete_on_scene:
            try:
                from core.narrative_system import narrative_system
                cenas_visitadas = getattr(narrative_system, 'cenas_visitadas', None) or getattr(narrative_system, 'scenes_visited', None) or set()
                current_scene = getattr(narrative_system, 'current_scene_id', None)
                
                # Se a cena de conclusão já foi visitada, completar a missão imediatamente
                if complete_on_scene in cenas_visitadas:
                    print(f"[MISSÕES] Missão {missao_id} ativada, mas cena de conclusão {complete_on_scene} já foi visitada. Completando automaticamente...")
                    self.completar_missao(missao_id)
                    return True
                # Se a cena atual já passou da cena de conclusão (comparando ordem), completar também
                elif current_scene and complete_on_scene:
                    # Comparar ordem das cenas: se current_scene vem depois de complete_on_scene, completar
                    # Exemplo: complete_on_scene="ch1_1_crank_garage_intro", current_scene="ch1_1b_the_deal" -> completar
                    scene_parts_current = current_scene.split("_")
                    scene_parts_complete = complete_on_scene.split("_")
                    if len(scene_parts_current) >= 2 and len(scene_parts_complete) >= 2:
                        # Comparar capítulo e número da cena
                        if scene_parts_current[0] == scene_parts_complete[0]:  # Mesmo capítulo
                            try:
                                # Extrair número da cena (pode ser "1", "1b", "2", etc.)
                                current_scene_num = scene_parts_current[1]
                                complete_scene_num = scene_parts_complete[1]
                                
                                # Se current_scene tem sufixo (ex: "1b") e complete_on_scene é só número (ex: "1"), completar
                                # Isso significa que já passou pela cena de conclusão
                                if len(current_scene_num) > len(complete_scene_num) and current_scene_num.startswith(complete_scene_num):
                                    print(f"[MISSÕES] Missão {missao_id} ativada, mas cena atual {current_scene} já passou da cena de conclusão {complete_on_scene}. Completando automaticamente...")
                                    self.completar_missao(missao_id)
                                    return True
                                
                                # Comparação numérica simples
                                current_num = int(current_scene_num) if current_scene_num.isdigit() else 0
                                complete_num = int(complete_scene_num) if complete_scene_num.isdigit() else 0
                                if current_num > complete_num:
                                    print(f"[MISSÕES] Missão {missao_id} ativada, mas cena atual {current_scene} já passou da cena de conclusão {complete_on_scene}. Completando automaticamente...")
                                    self.completar_missao(missao_id)
                                    return True
                            except:
                                pass
            except Exception as e:
                print(f"[MISSÕES] Erro ao verificar cena de conclusão para {missao_id}: {e}")
        
        self.missao_ativa_id = missao_id
        self.salvar()
        print(f"[MISSÕES] Missão '{missao_id}' ativada e salva. Rastreador deve ser atualizado.")
        return True
    
    def ativar_por_cena(self, scene_id: str):
        """Ativa uma missão baseada no ID da cena"""
        # Mapeamento de cenas para garantir compatibilidade
        mapeamento_ativacao = {
            "ch1_1c_crank_test_result": "ch1_1c_crank_test_result",  # ch1_1c_crank_test_result deve ativar missões com activateOnSceneId="ch1_1c_crank_test_result" (m3)
            "ch1_2_meet_boris": "ch1_2_meet_boris",  # ch1_2_meet_boris deve ativar missões com activateOnSceneId="ch1_2_meet_boris" (m4)
            "ch1_4_garage_return": "ch1_4_return_garage_upgrade",  # ch1_4_garage_return deve ativar missões com activateOnSceneId="ch1_4_return_garage_upgrade"
            "ch1_4b_housing_offer": "ch1_4b_housing_offer",  # ch1_4b_housing_offer deve ativar missões com activateOnSceneId="ch1_4b_housing_offer" (m2)
            "ch1_5_race_briefing": "ch1_5_first_race_unlocked",  # ch1_5_race_briefing deve ativar missões com activateOnSceneId="ch1_5_first_race_unlocked"
            "ch1_6_post_race": "ch1_6_post_first_race_and_pixel",  # ch1_6_post_race deve ativar missões com activateOnSceneId="ch1_6_post_first_race_and_pixel"
            "ch2_1_barao_intro": "ch2_2_barao_appears",  # ch2_1_barao_intro deve ativar missões com activateOnSceneId="ch2_2_barao_appears"
            "ch2_4_pixel_reacts": "ch2_4_loan_accepted",  # ch2_4_pixel_reacts deve ativar missões com activateOnSceneId="ch2_4_loan_accepted" (m9a)
            "ch2_5_boris_offer_again": "ch2_8_boris_unlock_offer",  # ch2_5_boris_offer_again deve ativar missões com activateOnSceneId="ch2_8_boris_unlock_offer" (m10)
            "ch2_6_crank_cinturao_offer": "ch2_8_boris_unlock_offer",  # ch2_6_crank_cinturao_offer deve ativar missões com activateOnSceneId="ch2_8_boris_unlock_offer" (m10)
            "ch3_6_pixel_wrap_up": "ch3_8_pixel_wrap",  # ch3_6_pixel_wrap_up deve ativar missões com activateOnSceneId="ch3_8_pixel_wrap" (m14)
        }
        
        # Verificar se há mapeamento para esta cena
        scene_id_original = mapeamento_ativacao.get(scene_id, scene_id)
        
        # Ordenar missões para garantir que missões intermediárias (com "b" no nome) sejam ativadas antes das principais
        # Isso garante que m16b seja ativada antes de m17 quando ambas têm o mesmo activateOnSceneId
        missoes_ordenadas = sorted(self.missoes.items(), key=lambda x: (
            # Priorizar missões com "b" no nome (intermediárias) antes das principais
            0 if "b" in x[0] else 1,
            x[0]  # Depois ordenar alfabeticamente
        ))
        
        print(f"[MISSÕES] ativar_por_cena: verificando cena {scene_id} (mapeada: {scene_id_original})")
        
        # IMPORTANTE: Marcar a cena mapeada como visitada também para garantir que missões sejam ativadas
        from core.narrative_system import narrative_system
        if scene_id_original != scene_id:
            narrative_system.scenes_visited.add(scene_id_original)
            print(f"[MISSÕES] Cena mapeada {scene_id_original} marcada como visitada (original: {scene_id})")
        
        for missao_id, missao in missoes_ordenadas:
            activate_on = missao.get("activateOnSceneId")
            if activate_on:
                print(f"[MISSÕES] Verificando missão {missao_id}: activateOnSceneId={activate_on}")
            # Verificar tanto a cena original quanto a mapeada
            if activate_on == scene_id or activate_on == scene_id_original:
                if missao_id not in self.missoes_completas:
                    print(f"[MISSÕES] Ativando missão {missao_id} pela cena {scene_id} (activateOnSceneId={activate_on})")
                    self.ativar_missao(missao_id)
                    return missao_id
                else:
                    print(f"[MISSÕES] Missão {missao_id} já foi completada, não ativando novamente")
        print(f"[MISSÕES] Nenhuma missão encontrada para ativar pela cena {scene_id}")
        return None
    
    def completar_missao(self, missao_id: str = None):
        """Completa a missão ativa ou uma missão específica"""
        from core.progresso import gerenciador_progresso
        from core.narrative_system import narrative_system
        
        if missao_id is None:
            missao_id = self.missao_ativa_id
        
        # IMPORTANTE: Quando m6 é completada, marcar cena para permitir ativação de m7
        if missao_id == "m6_batismo_de_pista":
            if "ch1_6_post_first_race_and_pixel" not in narrative_system.scenes_visited:
                narrative_system.scenes_visited.add("ch1_6_post_first_race_and_pixel")
                print(f"[MISSÕES] m6 completada - marcando ch1_6_post_first_race_and_pixel como visitada para permitir m7")
        
        if missao_id and missao_id in self.missoes:
            if missao_id not in self.missoes_completas:
                self.missoes_completas.add(missao_id)
                print(f"[MISSÕES] Missão '{missao_id}' marcada como completa")
                # Limpar missão ativa se foi completada
                if self.missao_ativa_id == missao_id:
                    self.missao_ativa_id = None
                    print(f"[MISSÕES] Missão ativa '{missao_id}' foi completada, limpando missao_ativa_id")
                # Se completou m14_tres_mundos, iniciar capítulo 4 e ativar missão intermediária (m14b_voltar_oficina_pixel)
                if missao_id == "m14_tres_mundos":
                    print(f"[MISSÕES] Missão m14_tres_mundos completada! Iniciando Capítulo 4 e ativando missão intermediária m14b_voltar_oficina_pixel...")
                    # Verificar se todas as missões do capítulo 3 foram completadas
                    missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo"]
                    todas_ch3_completas = all(m in self.missoes_completas for m in missoes_ch3)
                    if todas_ch3_completas:
                        print(f"[MISSÕES] Todas as missões do Capítulo 3 completadas! Iniciando Capítulo 4...")
                        gerenciador_progresso.marcar_capitulo_completo("ch3")
                        gerenciador_progresso.definir_capitulo_atual("ch4")
                        gerenciador_progresso.salvar()
                        # Atualizar current_chapter_id do narrative_system
                        from core.narrative_system import narrative_system
                        narrative_system.current_chapter_id = "ch4"
                        print(f"[MISSÕES] Capítulo atualizado para ch4. current_chapter_id={narrative_system.current_chapter_id}")
                    # Ativar missão intermediária que direciona o jogador para a oficina
                    if "m14b_voltar_oficina_pixel" in self.missoes and "m14b_voltar_oficina_pixel" not in self.missoes_completas:
                        self.ativar_missao("m14b_voltar_oficina_pixel")
                        print(f"[MISSÕES] Missão m14b_voltar_oficina_pixel ativada! Jogador deve ir à oficina.")
                    else:
                        print(f"[MISSÕES] Missão m14b_voltar_oficina_pixel não encontrada ou já completada.")
                
                # Se completou m14b_voltar_oficina_pixel, ativar m15_ruido_nos_servidores
                if missao_id == "m14b_voltar_oficina_pixel":
                    print(f"[MISSÕES] Missão m14b_voltar_oficina_pixel completada! Ativando m15_ruido_nos_servidores...")
                    if "m15_ruido_nos_servidores" in self.missoes and "m15_ruido_nos_servidores" not in self.missoes_completas:
                        self.ativar_missao("m15_ruido_nos_servidores")
                        print(f"[MISSÕES] Missão m15_ruido_nos_servidores ativada!")
                
                # Se completou m15_ruido_nos_servidores, ativar m16_conhecer_glub
                if missao_id == "m15_ruido_nos_servidores":
                    print(f"[MISSÕES] Missão m15_ruido_nos_servidores completada! Ativando m16_conhecer_glub...")
                    if "m16_conhecer_glub" in self.missoes and "m16_conhecer_glub" not in self.missoes_completas:
                        self.ativar_missao("m16_conhecer_glub")
                        print(f"[MISSÕES] Missão m16_conhecer_glub ativada!")
                    # Limpar missão ativa se foi completada
                    if self.missao_ativa_id == missao_id:
                        self.missao_ativa_id = None
                
                # Se completou m16_conhecer_glub, ativar m16b_voltar_pixel
                # NOTA: m16b_voltar_pixel também é ativada por ativar_por_cena quando ch4_4_meet_glub termina,
                # mas garantimos aqui também para casos onde a ativação por cena não aconteceu
                if missao_id == "m16_conhecer_glub":
                    print(f"[MISSÕES] Missão m16_conhecer_glub completada! Verificando se m16b_voltar_pixel precisa ser ativada...")
                    # IMPORTANTE: Se m17 está ativa, desativá-la porque m16b deve vir primeiro
                    if self.missao_ativa_id == "m17_conhecer_slick":
                        print(f"[MISSÕES] m17_conhecer_slick está ativa mas m16b ainda não foi completada! Desativando m17...")
                        self.missao_ativa_id = None
                    
                    if "m16b_voltar_pixel" in self.missoes and "m16b_voltar_pixel" not in self.missoes_completas:
                        # Só ativar se ainda não estiver ativa (pode ter sido ativada por ativar_por_cena)
                        if self.missao_ativa_id != "m16b_voltar_pixel":
                            self.ativar_missao("m16b_voltar_pixel")
                            print(f"[MISSÕES] Missão m16b_voltar_pixel ativada!")
                        else:
                            print(f"[MISSÕES] Missão m16b_voltar_pixel já está ativa (foi ativada por cena)")
                    # Limpar missão ativa se foi completada
                    if self.missao_ativa_id == missao_id:
                        self.missao_ativa_id = None
                
                # Se completou m16b_voltar_pixel, ativar m17_conhecer_slick
                if missao_id == "m16b_voltar_pixel":
                    print(f"[MISSÕES] Missão m16b_voltar_pixel completada! Ativando m17_conhecer_slick...")
                    if "m17_conhecer_slick" in self.missoes and "m17_conhecer_slick" not in self.missoes_completas:
                        self.ativar_missao("m17_conhecer_slick")
                        print(f"[MISSÕES] Missão m17_conhecer_slick ativada!")
                    # Limpar missão ativa se foi completada
                    if self.missao_ativa_id == missao_id:
                        self.missao_ativa_id = None
                
                # Salvar imediatamente após completar a missão
                self.salvar()
                print(f"[MISSÕES] Missão '{missao_id}' salva no progresso.json")
                # Tentar ativar próxima missão automaticamente (se ainda não foi ativada acima)
                if missao_id == "m14_tres_mundos" and not self.missao_ativa_id:
                    self._ativar_proxima_missao_automaticamente()
                
                # Se completou m10_portoes_do_cinturao, ativar m10b_corridas_cinturao
                if missao_id == "m10_portoes_do_cinturao":
                    if "m10b_corridas_cinturao" not in self.missoes_completas:
                        print(f"[MISSÕES] Missão m10_portoes_do_cinturao completada, ativando m10b_corridas_cinturao...")
                        self.ativar_missao("m10b_corridas_cinturao")
                
                # Se completou m10b_corridas_cinturao, atualizar capítulo para ch3 e ativar m11
                if missao_id == "m10b_corridas_cinturao":
                    print(f"[MISSÕES] Missão m10b_corridas_cinturao completada, atualizando capítulo para ch3...")
                    # Verificar se todas as missões do capítulo 2 foram completadas
                    missoes_ch2_necessarias = ["m8_oferta_envenenada", "m9a_peso_da_divida", "m10_portoes_do_cinturao", "m10b_corridas_cinturao"]
                    todas_ch2_completas = all(m in self.missoes_completas for m in missoes_ch2_necessarias)
                    if todas_ch2_completas:
                        print(f"[MISSÕES] Todas as missões do Capítulo 2 completadas! Avançando para Capítulo 3...")
                        gerenciador_progresso.marcar_capitulo_completo("ch2")
                        gerenciador_progresso.definir_capitulo_atual("ch3")
                        gerenciador_progresso.salvar()
                        # Atualizar current_chapter_id do narrative_system
                        from core.narrative_system import narrative_system
                        narrative_system.current_chapter_id = "ch3"
                        print(f"[MISSÕES] Capítulo atualizado para ch3. current_chapter_id={narrative_system.current_chapter_id}")
                    
                    # Ativar missão m10c_voltar_oficina_crank quando m10b é completada
                    if "m10c_voltar_oficina_crank" not in self.missoes_completas and "m10c_voltar_oficina_crank" in self.missoes:
                        print(f"[MISSÕES] Ativando missão m10c_voltar_oficina_crank após completar m10b_corridas_cinturao...")
                        self.ativar_missao("m10c_voltar_oficina_crank")
                
                # Verificar se completou todas as missões do capítulo 3
                missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo"]
                if missao_id in missoes_ch3:
                    todas_ch3_completas = all(m in self.missoes_completas for m in missoes_ch3)
                    if todas_ch3_completas:
                        print(f"[MISSÕES] Todas as missões do Capítulo 3 completadas! Preparando para iniciar Capítulo 4...")
                        # Marcar capítulo 3 como completo
                        gerenciador_progresso.marcar_capitulo_completo("ch3")
                        # Definir flag para iniciar capítulo 4 após narrativa
                        gerenciador_progresso.iniciar_capitulo_4_apos_narrativa = True
                        gerenciador_progresso.definir_capitulo_atual("ch4")
                        gerenciador_progresso.salvar()
                        print(f"[MISSÕES] Capítulo 4 será iniciado na próxima narrativa.")
                
                # Verificar se completou todas as missões do capítulo 4
                # IMPORTANTE: Não iniciar Capítulo 5 automaticamente quando m17_conhecer_slick é completada
                # A cena do Slick precisa terminar completamente antes de iniciar o Capítulo 5
                # A inicialização do Capítulo 5 será feita quando a cena ch4_5_meet_slick terminar (nextSceneId: null)
                missoes_ch4 = ["m15_ruido_nos_servidores", "m16_conhecer_glub", "m16b_voltar_pixel", "m17_conhecer_slick"]
                if missao_id in missoes_ch4:
                    todas_ch4_completas = all(m in self.missoes_completas for m in missoes_ch4)
                    if todas_ch4_completas:
                        print(f"[MISSÕES] Todas as missões do Capítulo 4 completadas! Capítulo 5 será iniciado quando a cena do Slick terminar.")
                        # Marcar capítulo 4 como completo, mas NÃO iniciar Capítulo 5 ainda
                        gerenciador_progresso.marcar_capitulo_completo("ch4")
                        # Definir flag para iniciar Capítulo 5 após a cena do Slick terminar
                        gerenciador_progresso.iniciar_capitulo_5_apos_slick = True
                        gerenciador_progresso.salvar()
                
                # Verificar se completou a missão m18_circo_da_coroa - desbloquear autódromo
                if missao_id == "m18_circo_da_coroa":
                    print(f"[MISSÕES] Missão m18_circo_da_coroa completada! Desbloqueando autódromo...")
                    from core.mapa_locations import gerenciador_localizacoes
                    gerenciador_localizacoes.desbloquear("autódromo")
                    gerenciador_localizacoes.salvar()
                    print(f"[MISSÕES] Autódromo desbloqueado!")
                
                # Verificar se completou m8_oferta_envenenada - decidir próxima missão baseado na escolha
                if missao_id == "m8_oferta_envenenada":
                    print(f"[MISSÕES] Missão m8_oferta_envenenada completada! Verificando escolha do jogador...")
                    # Verificar se o jogador aceitou ou recusou o empréstimo
                    has_debt = gerenciador_progresso.barao_emprestimo_ativo
                    # Verificar também a flag refusedDebt no narrative_system
                    from core.narrative_system import narrative_system
                    refused_debt = narrative_system.flags.get("refusedDebt", False)
                    
                    if has_debt:
                        # Jogador aceitou o empréstimo - ativar m9a_peso_da_divida normalmente
                        print(f"[MISSÕES] Jogador aceitou o empréstimo. Ativando m9a_peso_da_divida...")
                        # A missão será ativada automaticamente quando a cena ch2_4_loan_accepted for visitada
                    else:
                        # Jogador recusou o empréstimo - marcar m9a como completa e ativar m10
                        print(f"[MISSÕES] Jogador recusou o empréstimo. Marcando m9a_peso_da_divida como completa e ativando m10_portoes_do_cinturao...")
                        if "m9a_peso_da_divida" not in self.missoes_completas:
                            self.missoes_completas.add("m9a_peso_da_divida")
                            print(f"[MISSÕES] Missão m9a_peso_da_divida marcada como completa (jogador recusou empréstimo)")
                        # Ativar m10_portoes_do_cinturao imediatamente (jogador recusou empréstimo)
                        if "m10_portoes_do_cinturao" in self.missoes and "m10_portoes_do_cinturao" not in self.missoes_completas:
                            print(f"[MISSÕES] Ativando missão m10_portoes_do_cinturao imediatamente (jogador recusou empréstimo)")
                            self.ativar_missao("m10_portoes_do_cinturao")
            
            if self.missao_ativa_id == missao_id:
                self.missao_ativa_id = None
                print(f"[MISSÕES] Missão {missao_id} completada, tentando ativar próxima missão automaticamente...")
                # Tentar ativar a próxima missão automaticamente
                self._ativar_proxima_missao_automaticamente()
                if self.missao_ativa_id:
                    print(f"[MISSÕES] Próxima missão {self.missao_ativa_id} ativada automaticamente após completar {missao_id}")
                else:
                    print(f"[MISSÕES] Nenhuma próxima missão encontrada para ativar automaticamente após completar {missao_id}")
            self.salvar()
            print(f"[MISSÕES] Missão '{missao_id}' completada e salva. Missão ativa atual: {self.missao_ativa_id}")
            return True
        else:
            if missao_id:
                print(f"[MISSÕES] Aviso: Tentativa de completar missão inexistente: {missao_id}")
        return False
    
    def completar_por_cena(self, scene_id: str):
        """Completa uma missão baseada no ID da cena"""
        print(f"[MISSÕES] completar_por_cena chamado para cena: {scene_id}")
        
        # IMPORTANTE: Quando ch1_6_post_race ou ch1_6_post_first_race_and_pixel é visitada, completar m6
        # e marcar cena para permitir m7
        from core.narrative_system import narrative_system
        if scene_id in ["ch1_6_post_race", "ch1_6_post_first_race_and_pixel"]:
            if "m6_batismo_de_pista" not in self.missoes_completas:
                print(f"[MISSÕES] Cena pós-corrida visitada, completando m6_batismo_de_pista...")
                self.completar_missao("m6_batismo_de_pista")
            # Marcar cena para permitir m7
            if "ch1_6_post_first_race_and_pixel" not in narrative_system.scenes_visited:
                narrative_system.scenes_visited.add("ch1_6_post_first_race_and_pixel")
                print(f"[MISSÕES] Marcando ch1_6_post_first_race_and_pixel como visitada para permitir m7")
        
        # Mapeamento de cenas antigas para novas (compatibilidade)
        mapeamento_cenas = {
            "ch1_1b_crank_test_briefing": "ch1_1b_the_deal",
            "ch1_1c_crank_test_result": "ch1_1b_the_deal",
            "ch1_3_meet_boris": "ch1_2_meet_boris",
            "ch1_2_meet_boris": "ch1_2_meet_boris",  # Mapear ch1_2_meet_boris para si mesma para ativar m4
            "ch1_3_boris_deal": "ch1_3_boris_deal",  # Mapear ch1_3_boris_deal para si mesma para completar m4
            "ch1_4_return_garage_upgrade": "ch1_4_garage_return",
            "ch1_5_first_race_unlocked": "ch1_5_race_briefing",
            "ch1_6_post_first_race_and_pixel": "ch1_6_post_race",
            "ch1_7_pixel_intro": "ch1_7_pixel_voice_intro",  # Mapeamento importante para m7_olhos_no_painel
            "ch2_2_barao_appears": "ch2_1_barao_intro",
            "ch2_4_loan_accepted": "ch2_2_barao_offer",
            "ch2_5_loan_refused": "ch2_2_barao_offer",
            "ch2_6_pixel_reacts": "ch2_4_pixel_reacts",
            "ch2_8_boris_unlock_offer": "ch2_5_boris_offer_again",
            "ch3_1_crank_to_mountain": "ch3_1_crank_briefing",
            "ch3_3_meet_akira": "ch3_3_meet_akira",
            "ch3_4_akira_past": "ch3_4_test_result",
            "ch3_5_test_briefing": "ch3_3_meet_akira",
            "ch3_6_test_result": "ch3_4_test_result",
            "ch3_8_pixel_wrap": "ch3_6_pixel_wrap_up",
            "ch4_1_pixel_rex_watch": "ch4_1_pixel_warning",
            "ch4_2_rex_observes": "ch4_2_pixel_invitation",
            "ch4_2_pixel_invitation": "ch4_2_pixel_invitation",  # Mapear ch4_2_pixel_invitation para si mesma para completar m14b
            "ch4_4_meet_slick": "ch4_5_meet_slick",
            "ch4_5_meet_glub": "ch4_4_meet_glub",
            "ch5_1_rex_invite_circuit": "ch5_1_rex_invite",
            "ch5_3_akira_reacts": "ch5_3_akira_call",
            "ch5_5_stage1_intro": "ch5_5_stage1_intro",
            "ch5_5_stage3_post": "ch5_5_stage3_post",
            "ch5_6_pre_final_rex": "ch5_7_pre_final",
            "ch5_7_post_final_epilogue": "ch5_7_post_final_epilogue",
            "ch5_8_rex_close": "ch5_9_rex_final_words",
            "ch5_9_rex_final_words": "ch5_9_rex_final_words"
        }
        
        # Verificar se há mapeamento
        scene_id_mapeado = mapeamento_cenas.get(scene_id, scene_id)
        print(f"[MISSÕES] Cena mapeada: {scene_id} -> {scene_id_mapeado}")
        
        for missao_id, missao in self.missoes.items():
            complete_on_scene = missao.get("completeOnSceneId")
            if not complete_on_scene:
                continue
            print(f"[MISSÕES] Verificando missão {missao_id}: completeOnSceneId={complete_on_scene}")
            
            # Verificar correspondência direta
            if complete_on_scene == scene_id:
                print(f"[MISSÕES] Missão {missao_id} deve ser completada pela cena {scene_id} (correspondência direta)")
                self.completar_missao(missao_id)
                return missao_id
            
            # Verificar se complete_on_scene está no mapeamento e se o valor mapeado corresponde a scene_id
            # Exemplo: complete_on_scene="ch1_7_pixel_intro" mapeia para "ch1_7_pixel_voice_intro"
            # Se scene_id="ch1_7_pixel_voice_intro", então a missão deve ser completada
            if complete_on_scene in mapeamento_cenas:
                cena_mapeada = mapeamento_cenas[complete_on_scene]
                if cena_mapeada == scene_id:
                    print(f"[MISSÕES] Missão {missao_id} deve ser completada pela cena {scene_id} (via mapeamento: {complete_on_scene} -> {cena_mapeada})")
                    self.completar_missao(missao_id)
                    return missao_id
            
            # Verificar mapeamento reverso: se scene_id está mapeado de alguma cena original
            # Exemplo: se scene_id="ch1_7_pixel_voice_intro" e complete_on_scene="ch1_7_pixel_intro"
            # Precisamos verificar se há alguma entrada no mapeamento onde o valor é scene_id
            for cena_original, cena_mapeada_valor in mapeamento_cenas.items():
                if cena_mapeada_valor == scene_id and complete_on_scene == cena_original:
                    print(f"[MISSÕES] Missão {missao_id} deve ser completada pela cena {scene_id} (via mapeamento reverso: {cena_original} -> {scene_id})")
                    self.completar_missao(missao_id)
                    return missao_id
        
        print(f"[MISSÕES] Nenhuma missão encontrada para completar pela cena {scene_id}")
        return None
        
        # Completar m8_oferta_envenenada quando o jogador decide sobre o empréstimo
        # (tanto aceitando quanto recusando)
        if scene_id in ["ch2_4_loan_accepted", "ch2_5_loan_refused", "ch2_2_barao_offer"]:
            if "m8_oferta_envenenada" in self.missoes and "m8_oferta_envenenada" not in self.missoes_completas:
                self.completar_missao("m8_oferta_envenenada")
                return "m8_oferta_envenenada"
        
        return None
    
    def _validar_missao_ativa_apropriada(self):
        """Valida se a missão ativa é apropriada para o progresso atual do jogador"""
        if not self.missao_ativa_id or self.missao_ativa_id not in self.missoes:
            return False
        
        missao_ativa = self.missoes[self.missao_ativa_id]
        missao_chapter = missao_ativa.get("chapter", "ch1")
        
        # Extrair número da missão (m1, m2, m10b, etc.)
        try:
            # Para missões como m10b, extrair apenas o número base (10)
            missao_num_str = self.missao_ativa_id.split("_")[0].replace("m", "")
            # Remover letras do final (m10b -> 10)
            missao_num = int(''.join(filter(str.isdigit, missao_num_str)))
        except:
            missao_num = 0
        
        # Determinar qual capítulo o jogador deveria estar baseado nas missões completas
        missoes_ch1 = ["m1_primeira_faisca", "m2_teste_de_sobrevivencia", "m3_rota_da_ferrugem", 
                       "m4_coracao_de_sucata", "m5_cirurgia_na_garagem", "m6_batismo_de_pista", "m7_olhos_no_painel"]
        missoes_ch2 = ["m8_oferta_envenenada", "m9a_peso_da_divida", "m10_portoes_do_cinturao", "m10b_corridas_cinturao"]
        missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo", "m14_tres_mundos"]
        
        # Contar missões completas por capítulo
        ch1_completas = sum(1 for m in missoes_ch1 if m in self.missoes_completas)
        ch2_completas = sum(1 for m in missoes_ch2 if m in self.missoes_completas)
        ch3_completas = sum(1 for m in missoes_ch3 if m in self.missoes_completas)
        
        # Determinar capítulo esperado baseado no progresso
        if ch1_completas < len(missoes_ch1):
            capitulo_esperado = "ch1"
        elif ch2_completas < len(missoes_ch2):
            capitulo_esperado = "ch2"
        elif ch3_completas < len(missoes_ch3):
            capitulo_esperado = "ch3"
        else:
            capitulo_esperado = "ch4"  # Ou mais avançado
        
        # Se a missão ativa é de um capítulo muito mais avançado que o esperado, é inválida
        if missao_chapter == "ch2" and capitulo_esperado == "ch1":
            # Jogador está no ch1 mas missão ativa é do ch2
            if missao_num >= 8:  # m8 ou superior
                print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} é do ch2 mas jogador está no ch1 (completou {ch1_completas}/{len(missoes_ch1)} missões ch1)")
                return False
        elif missao_chapter == "ch3" and capitulo_esperado in ["ch1", "ch2"]:
            # Jogador está no ch1 ou ch2 mas missão ativa é do ch3
            if missao_num >= 11:  # m11 ou superior
                print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} é do ch3 mas jogador está no {capitulo_esperado}")
                return False
        elif missao_chapter in ["ch4", "ch5"] and capitulo_esperado in ["ch1", "ch2", "ch3"]:
            # Jogador está em capítulos anteriores mas missão ativa é muito avançada
            print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} é do {missao_chapter} mas jogador está no {capitulo_esperado}")
            return False
        
        # Verificar se há missões anteriores não completadas que deveriam vir antes
        # Ordenar todas as missões por capítulo e ordem
        todas_missoes_ordenadas = []
        for missao_id, missao in self.missoes.items():
            todas_missoes_ordenadas.append((missao_id, missao))
        todas_missoes_ordenadas.sort(key=lambda x: (x[1].get("chapter", "ch1"), x[0]))
        
        # Encontrar a posição da missão ativa na lista ordenada
        posicao_ativa = None
        for i, (mid, m) in enumerate(todas_missoes_ordenadas):
            if mid == self.missao_ativa_id:
                posicao_ativa = i
                break
        
        if posicao_ativa is not None:
            # Verificar se há missões anteriores não completadas no mesmo capítulo
            for i in range(posicao_ativa):
                missao_anterior_id, missao_anterior = todas_missoes_ordenadas[i]
                if missao_anterior.get("chapter") == missao_chapter:
                    if missao_anterior_id not in self.missoes_completas:
                        print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} requer que {missao_anterior_id} seja completada primeiro")
                        return False
        
        return True
    
    def verificar_consistencia_missoes(self):
        """Verifica e corrige inconsistências nas missões ativas"""
        # Se m17 está ativa mas m16b não foi completada, desativar m17 e ativar m16b
        if self.missao_ativa_id == "m17_conhecer_slick":
            if "m16b_voltar_pixel" not in self.missoes_completas:
                print(f"[MISSÕES] INCONSISTÊNCIA DETECTADA: m17 está ativa mas m16b não foi completada!")
                print(f"[MISSÕES] Desativando m17 e ativando m16b...")
                self.missao_ativa_id = None
                if "m16b_voltar_pixel" in self.missoes and "m16b_voltar_pixel" not in self.missoes_completas:
                    self.ativar_missao("m16b_voltar_pixel")
                    print(f"[MISSÕES] m16b_voltar_pixel ativada para corrigir inconsistência")
                return True
        return False
    
    def obter_missao_ativa(self):
        """Retorna a missão ativa atual"""
        # Verificar consistência antes de retornar a missão ativa
        self.verificar_consistencia_missoes()
        
        # Validar se a missão ativa é apropriada
        if self.missao_ativa_id and self.missao_ativa_id in self.missoes:
            if not self._validar_missao_ativa_apropriada():
                print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} não é apropriada, limpando...")
                self.missao_ativa_id = None
                self.salvar()
            else:
                return self.missoes[self.missao_ativa_id]
        
        # Se não há missão ativa, tentar ativar automaticamente a próxima baseada no progresso
        print(f"[MISSÕES] Nenhuma missão ativa, tentando ativar automaticamente... (completas: {len(self.missoes_completas)})")
        self._ativar_proxima_missao_automaticamente()
        
        if self.missao_ativa_id and self.missao_ativa_id in self.missoes:
            print(f"[MISSÕES] Missão ativada automaticamente: {self.missao_ativa_id}")
            self.salvar()  # IMPORTANTE: Salvar imediatamente após ativar
            return self.missoes[self.missao_ativa_id]
        else:
            print(f"[MISSÕES] Nenhuma missão pôde ser ativada automaticamente. missao_ativa_id={self.missao_ativa_id}")
            # DEBUG: Verificar qual é a próxima missão que deveria ser ativada
            from core.progresso import gerenciador_progresso
            capitulo_atual = gerenciador_progresso.obter_capitulo_atual() or "ch1"
            print(f"[MISSÕES] DEBUG: Capítulo atual: {capitulo_atual}, Missões completas: {sorted(self.missoes_completas)}")
            # Listar todas as missões do capítulo atual que não foram completadas
            missoes_capitulo = [(mid, m) for mid, m in self.missoes.items() if m.get("chapter") == capitulo_atual and mid not in self.missoes_completas]
            print(f"[MISSÕES] DEBUG: Missões do capítulo {capitulo_atual} não completadas: {[mid for mid, m in missoes_capitulo]}")
            for mid, m in missoes_capitulo:
                activate_on = m.get("activateOnSceneId")
                if activate_on:
                    from core.narrative_system import narrative_system
                    scenes_visited = getattr(narrative_system, 'scenes_visited', set())
                    print(f"[MISSÕES] DEBUG: {mid} requer cena {activate_on}, visitada: {activate_on in scenes_visited}")
        return None
    
    def _ativar_proxima_missao_automaticamente(self):
        """Ativa automaticamente a próxima missão baseada no progresso do jogador"""
        if self.missao_ativa_id:
            # Se já há uma missão ativa e ela é válida, não fazer nada
            if self.missao_ativa_id in self.missoes:
                return  # Já há uma missão ativa válida
            else:
                # Missão ativa é inválida, limpar
                print(f"[MISSÕES] Missão ativa {self.missao_ativa_id} é inválida, limpando...")
                self.missao_ativa_id = None
        
        # Obter capítulo atual
        from core.progresso import gerenciador_progresso
        capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
        if not capitulo_atual:
            # Se não há capítulo definido, tentar inferir baseado nas missões completas
            if len(self.missoes_completas) >= 7:
                capitulo_atual = "ch3"  # Se completou 7 missões, provavelmente está no capítulo 3
            elif len(self.missoes_completas) >= 4:
                capitulo_atual = "ch2"
            else:
                capitulo_atual = "ch1"
            print(f"[MISSÕES] Capítulo não definido, inferindo como {capitulo_atual} baseado em {len(self.missoes_completas)} missões completas")
        
        # IMPORTANTE: Para um novo save (nenhuma missão completa), ativar m1_primeira_faisca imediatamente
        # Esta missão será ativada novamente quando ch1_0_prologue for visitada (via ativar_por_cena),
        # mas precisamos ativá-la agora para que o jogador tenha uma missão ativa desde o início
        if len(self.missoes_completas) == 0 and capitulo_atual == "ch1":
            if "m1_primeira_faisca" in self.missoes and "m1_primeira_faisca" not in self.missoes_completas:
                if not self.missao_ativa_id or self.missao_ativa_id != "m1_primeira_faisca":
                    print(f"[MISSÕES] ====== NOVO SAVE DETECTADO ======")
                    print(f"[MISSÕES] Nenhuma missão completa, capítulo atual: {capitulo_atual}")
                    print(f"[MISSÕES] Ativando primeira missão m1_primeira_faisca imediatamente (sem esperar prólogo)")
                    self.ativar_missao("m1_primeira_faisca", forcar_ativacao=True)
                    print(f"[MISSÕES] m1_primeira_faisca ativada! missao_ativa_id={self.missao_ativa_id}")
                    return
                else:
                    print(f"[MISSÕES] m1_primeira_faisca já está ativa (missao_ativa_id={self.missao_ativa_id})")
                    return
        
        # Verificar se o capítulo atual está correto
        # Se está no ch4 mas as missões do ch3 não foram completadas, voltar para ch3
        if capitulo_atual == "ch4":
            missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo"]
            missoes_ch3_completas = [m for m in missoes_ch3 if m in self.missoes_completas]
            if len(missoes_ch3_completas) < len(missoes_ch3):
                print(f"[MISSÕES] Capítulo atual é ch4, mas missões do ch3 não foram completadas ({len(missoes_ch3_completas)}/{len(missoes_ch3)}). Ajustando para ch3...")
                capitulo_atual = "ch3"
                # Atualizar o capítulo no progresso
                gerenciador_progresso.definir_capitulo_atual("ch3")
                gerenciador_progresso.salvar()
        
        # Verificar se o capítulo atual está correto
        # Se está no ch4 mas as missões do ch3 não foram completadas, voltar para ch3
        if capitulo_atual == "ch4":
            missoes_ch3 = ["m11_chamado_da_montanha", "m12_fantasma_do_circuito", "m13_teste_de_fluxo"]
            missoes_ch3_completas = [m for m in missoes_ch3 if m in self.missoes_completas]
            if len(missoes_ch3_completas) < len(missoes_ch3):
                print(f"[MISSÕES] Capítulo atual é ch4, mas missões do ch3 não foram completadas ({len(missoes_ch3_completas)}/{len(missoes_ch3)}). Ajustando para ch3...")
                capitulo_atual = "ch3"
                # Atualizar o capítulo no progresso
                gerenciador_progresso.definir_capitulo_atual("ch3")
                gerenciador_progresso.salvar()
        
        # IMPORTANTE: Se completou m5 mas m6 não está ativa, marcar cena como visitada e ativar m6
        # Isso resolve o problema onde ch1_5_race_briefing nunca é visitada
        if capitulo_atual == "ch1":
            if "m5_cirurgia_na_garagem" in self.missoes_completas:
                if "m6_batismo_de_pista" not in self.missoes_completas and "m6_batismo_de_pista" in self.missoes:
                    from core.narrative_system import narrative_system
                    # Marcar a cena como visitada para permitir ativação
                    if "ch1_5_first_race_unlocked" not in narrative_system.scenes_visited:
                        narrative_system.scenes_visited.add("ch1_5_first_race_unlocked")
                        print(f"[MISSÕES] m5 completada mas m6 não ativa - marcando ch1_5_first_race_unlocked como visitada")
                    # Tentar ativar m6
                    if not self.missao_ativa_id or self.missao_ativa_id != "m6_batismo_de_pista":
                        print(f"[MISSÕES] m5 completada, ativando m6_batismo_de_pista automaticamente...")
                        self.ativar_missao("m6_batismo_de_pista", forcar_ativacao=True)
                        return
        
        # Verificar progresso da Akira para determinar qual missão ativar
        try:
            from core.akira import akira
            akira_ja_foi_vista = akira.primeira_aparicao_mostrada
        except Exception as e:
            akira_ja_foi_vista = False
        
        # Se está no capítulo 4, verificar se m16 precisa ser ativada
        if capitulo_atual == "ch4":
            # Se m15 foi completada, ativar m16
            if "m15_ruido_nos_servidores" in self.missoes_completas:
                if "m16_conhecer_glub" in self.missoes and "m16_conhecer_glub" not in self.missoes_completas:
                    if not self.missao_ativa_id or self.missao_ativa_id != "m16_conhecer_glub":
                        print(f"[MISSÕES] Capítulo 4: m15 completada, ativando m16_conhecer_glub...")
                        self.ativar_missao("m16_conhecer_glub")
                        return
        
        # Se está no capítulo 3, verificar missões da Akira
        if capitulo_atual == "ch3":
            # Se já viu a Akira, verificar qual missão ativar
            if akira_ja_foi_vista:
                if "m13_teste_de_fluxo" not in self.missoes_completas and "m13_teste_de_fluxo" in self.missoes:
                    print(f"[MISSÕES] Akira já foi vista, ativando missão m13_teste_de_fluxo")
                    self.ativar_missao("m13_teste_de_fluxo")
                    return
                elif "m12_fantasma_do_circuito" not in self.missoes_completas and "m12_fantasma_do_circuito" in self.missoes:
                    print(f"[MISSÕES] Akira já foi vista, ativando missão m12_fantasma_do_circuito")
                    self.ativar_missao("m12_fantasma_do_circuito")
                    return
                elif "m11_chamado_da_montanha" not in self.missoes_completas and "m11_chamado_da_montanha" in self.missoes:
                    print(f"[MISSÕES] Akira já foi vista, ativando missão m11_chamado_da_montanha")
                    self.ativar_missao("m11_chamado_da_montanha")
                    return
            else:
                # Se não viu a Akira ainda, ativar m11_chamado_da_montanha
                if "m11_chamado_da_montanha" not in self.missoes_completas and "m11_chamado_da_montanha" in self.missoes:
                    print(f"[MISSÕES] Jogador está no ch3 mas não viu Akira, ativando missão m11_chamado_da_montanha")
                    self.ativar_missao("m11_chamado_da_montanha")
                    return
        
        # Ordenar todas as missões por capítulo e ordem
        todas_missoes_ordenadas = []
        for missao_id, missao in self.missoes.items():
            todas_missoes_ordenadas.append((missao_id, missao))
        
        # Ordenar por capítulo e depois por ID
        todas_missoes_ordenadas.sort(key=lambda x: (x[1].get("chapter", "ch1"), x[0]))
        
        # Priorizar missões do capítulo atual
        missoes_capitulo_atual = [(mid, m) for mid, m in todas_missoes_ordenadas if m.get("chapter") == capitulo_atual]
        
        # Verificar se as missões do capítulo atual têm activateOnSceneId e se a cena já foi visitada
        from core.narrative_system import narrative_system
        scenes_visited = getattr(narrative_system, 'scenes_visited', set())
        
        # Para o capítulo 5, verificar se m18 foi completada e ativar m19
        if capitulo_atual == "ch5":
            if "m18_circo_da_coroa" in self.missoes_completas:
                if "m19_jogo_do_rei" not in self.missoes_completas and "m19_jogo_do_rei" in self.missoes:
                    # Verificar se a cena de ativação já foi vista
                    missao_m19 = self.missoes["m19_jogo_do_rei"]
                    activate_on_scene = missao_m19.get("activateOnSceneId")
                    if activate_on_scene:
                        try:
                            from core.narrative_system import narrative_system
                            cenas_visitadas = getattr(narrative_system, 'cenas_visitadas', None) or getattr(narrative_system, 'scenes_visited', None) or set()
                            if activate_on_scene in cenas_visitadas:
                                print(f"[MISSÕES] Ativando missão m19_jogo_do_rei (cena {activate_on_scene} já foi vista)")
                                self.ativar_missao("m19_jogo_do_rei")
                                return
                        except Exception as e:
                            print(f"[MISSÕES] Erro ao verificar cena para m19: {e}")
                    else:
                        # Sem activateOnSceneId, ativar diretamente
                        print(f"[MISSÕES] Ativando missão m19_jogo_do_rei (m18 completada)")
                        self.ativar_missao("m19_jogo_do_rei", forcar_ativacao=True)
                        return
        
        # Encontrar a primeira missão NÃO COMPLETA do capítulo atual
        # IMPORTANTE: Processar em ordem para garantir que a primeira missão disponível seja ativada
        for missao_id, missao in missoes_capitulo_atual:
            # PULAR missões que já foram completadas
            if missao_id in self.missoes_completas:
                continue
            
            # Verificar se os pré-requisitos foram cumpridos
            activate_on_scene = missao.get("activateOnSceneId")
            missao_chapter = missao.get("chapter", "ch1")
            
            # Verificar se todas as missões anteriores do mesmo capítulo foram completadas
            # Usar a ordem na lista ordenada, não apenas números
            todas_anteriores_completas = True
            posicao_atual = None
            for i, (outra_id, outra_missao) in enumerate(missoes_capitulo_atual):
                if outra_id == missao_id:
                    posicao_atual = i
                    break
            
            if posicao_atual is not None:
                # Verificar todas as missões anteriores na lista
                for i in range(posicao_atual):
                    outra_id, outra_missao = missoes_capitulo_atual[i]
                    if outra_id not in self.missoes_completas:
                        todas_anteriores_completas = False
                        print(f"[MISSÕES] Missão {missao_id} não pode ser ativada: {outra_id} ainda não foi completada")
                        break
            
            # Se a missão tem activateOnSceneId, verificar se a cena já foi vista
            if activate_on_scene:
                # Verificar se a cena já foi vista através do sistema narrativo
                try:
                    from core.narrative_system import narrative_system
                    # Verificar tanto cenas_visitadas quanto scenes_visited
                    cenas_visitadas = getattr(narrative_system, 'cenas_visitadas', None) or getattr(narrative_system, 'scenes_visited', None) or set()
                    if activate_on_scene in cenas_visitadas:
                        if todas_anteriores_completas:
                            print(f"[MISSÕES] Ativando automaticamente missão {missao_id} (cena {activate_on_scene} já foi vista, todas anteriores completas)")
                            self.ativar_missao(missao_id)
                            return
                        else:
                            print(f"[MISSÕES] Missão {missao_id} requer cena {activate_on_scene} (já vista), mas missões anteriores não foram completadas")
                    else:
                        # IMPORTANTE: Se a missão tem activateOnSceneId, NÃO ativar até que a cena seja visitada
                        # Mesmo que todas as anteriores tenham sido completadas
                        print(f"[MISSÕES] Missão {missao_id} não pode ser ativada automaticamente: cena {activate_on_scene} ainda não foi visitada (será ativada quando a cena for visitada)")
                        continue  # Pular esta missão e tentar a próxima
                except Exception as e:
                    print(f"[MISSÕES] Erro ao verificar cena para missão {missao_id}: {e}")
                    # Em caso de erro, não ativar missões com activateOnSceneId automaticamente
                    print(f"[MISSÕES] Erro ao verificar cena, pulando missão {missao_id} (tem activateOnSceneId)")
                    continue
            else:
                # Missão sem activateOnSceneId - verificar se todas as anteriores foram completadas
                if todas_anteriores_completas:
                    print(f"[MISSÕES] Ativando automaticamente missão {missao_id} (sem activateOnSceneId, todas anteriores completas)")
                    self.ativar_missao(missao_id)
                    return
                else:
                    print(f"[MISSÕES] Missão {missao_id} não pode ser ativada: missões anteriores não foram completadas")
                    # Se esta é a primeira missão não completada, parar aqui para não pular para missões mais avançadas
                    break
        
        # IMPORTANTE: NÃO ativar missões de capítulos futuros automaticamente
        # Se não encontrou missão no capítulo atual, significa que todas as missões do capítulo atual
        # requerem cenas que ainda não foram visitadas ou têm pré-requisitos não cumpridos
        # Neste caso, NÃO devemos pular para o próximo capítulo
        print(f"[MISSÕES] Nenhuma missão do capítulo {capitulo_atual} pode ser ativada automaticamente no momento. Aguardando progresso do jogador.")
        return
    
    def esta_completa(self, missao_id: str) -> bool:
        """Verifica se uma missão está completa"""
        return missao_id in self.missoes_completas
    
    def obter_nome_missao(self) -> str:
        """Retorna o nome da missão ativa para o HUD"""
        missao = self.obter_missao_ativa()
        if missao:
            # Tentar obter nome detalhado primeiro
            nome_detalhado = self._obter_nome_detalhado(missao["id"])
            if nome_detalhado:
                return nome_detalhado
            return missao["nome"]
        return ""
    
    def _mapear_id_missao_para_info(self, missao_id: str) -> tuple:
        """Mapeia o ID da missão para a chave no missions_info.json"""
        # Mapeamento de IDs de missões para chaves no missions_info.json
        mapeamento = {
            "m3_rota_da_ferrugem": ("ch1", "find_boris"),
            "m5_cirurgia_na_garagem": ("ch1", "return_to_crank"),
            "m6_batismo_de_pista": ("ch1", "finish_training_race"),
            "m10_portoes_do_cinturao": ("ch2", "unlock_cinturao"),
            "m10b_corridas_cinturao": ("ch2", "corridas_cinturao"),
            "m10c_voltar_oficina_crank": ("ch2", "voltar_oficina_crank"),
            "m8_oferta_envenenada": ("ch2", "baron_debt_active"),
            "m11_chamado_da_montanha": ("ch3", "meet_akira"),
            "m12_fantasma_do_circuito": ("ch3", "finish_mountain_test"),
            "m13_olhos_nas_torres": ("ch4", "meet_pixel_physical"),
            "m14_reputacao_em_alta": ("ch4", "increase_reputation"),
            "m15_convite_dourado": ("ch5", "prepare_for_stage1"),
            "m17_circo_da_coroa": ("ch5", "complete_crown_circuit"),
            "m19_jogo_do_rei": ("ch5", "win_final_race"),
        }
        return mapeamento.get(missao_id, (None, None))
    
    def _obter_nome_detalhado(self, missao_id: str) -> str:
        """Obtém o nome detalhado da missão se disponível"""
        chapter, key = self._mapear_id_missao_para_info(missao_id)
        if chapter and key:
            chapter_info = self.missoes_info.get(chapter, {})
            missao_info = chapter_info.get(key, {})
            return missao_info.get("name", "")
        return ""
    
    def _obter_descricao_detalhada(self, missao_id: str) -> str:
        """Obtém a descrição detalhada da missão se disponível"""
        chapter, key = self._mapear_id_missao_para_info(missao_id)
        if chapter and key:
            chapter_info = self.missoes_info.get(chapter, {})
            missao_info = chapter_info.get(key, {})
            return missao_info.get("description", "")
        return ""
    
    def obter_objetivo_missao(self) -> str:
        """Retorna o objetivo da missão ativa para o HUD"""
        missao = self.obter_missao_ativa()
        if missao:
            # Tentar obter descrição detalhada primeiro
            descricao_detalhada = self._obter_descricao_detalhada(missao["id"])
            if descricao_detalhada:
                return descricao_detalhada
            
            objetivo = missao["objetivo"]
            
            # Atualizar objetivo dinamicamente baseado no progresso
            if missao["id"] == "m10_portoes_do_cinturao":
                # Verificar se o cinturão está desbloqueado
                from core.mapa_locations import gerenciador_localizacoes, EstadoLocalizacao
                if gerenciador_localizacoes.esta_desbloqueado("cinturao_industrial"):
                    return "Corra no Cinturão Industrial"
            
            elif missao["id"] == "m11_chamado_da_montanha":
                # Verificar progresso da missão m11_chamado_da_montanha
                from core.akira import akira
                
                # Se já encontrou a Akira, objetivo foi cumprido (missão será completada na cena ch3_3_meet_akira)
                if akira.primeira_aparicao_mostrada:
                    return "Você encontrou Akira. Continue a conversa para descobrir mais sobre ela."
                
                # Objetivo padrão
                return "Suba até a montanha e encontre Akira."
            
            elif missao["id"] == "m12_fantasma_do_circuito":
                # Verificar progresso da missão m12_fantasma_do_circuito
                from core.akira import akira
                from core.narrative_system import narrative_system
                
                # Se já completou a cena ch3_4_akira_past, a missão foi completada
                if "ch3_4_akira_past" in getattr(narrative_system, 'cenas_visitadas', set()):
                    return "Você descobriu o passado de Akira. Continue a jornada."
                
                # Se está na montanha com Akira, orientar a continuar a conversa
                if akira.primeira_aparicao_mostrada:
                    return "Continue conversando com Akira na montanha para descobrir seu passado."
                
                # Objetivo padrão
                return "Vá até a montanha e converse com Akira para descobrir seu passado."
            
            elif missao["id"] == "m13_teste_de_fluxo":
                # Verificar progresso da missão m13_teste_de_fluxo
                from core.progresso import gerenciador_progresso
                from core.akira import akira
                
                # Se a missão foi completada (corrida feita), atualizar objetivo para ir à garagem
                if "m13_teste_de_fluxo" in self.missoes_completas:
                    return "Vá até a garagem falar com o Crank sobre a corrida."
                
                # Se ainda não viu a primeira aparição da Akira
                if not akira.primeira_aparicao_mostrada:
                    return "Suba até a montanha e encontre Akira."
                
                # Se já viu a primeira aparição, verificar se tem pneus nível 1
                carro_atual = gerenciador_progresso.obter_carro_atual(1)
                if not carro_atual:
                    carro_atual = "Car1"
                
                # Garantir que carro_atual é string (prefixo_cor)
                if isinstance(carro_atual, int):
                    from config import CARROS_DISPONIVEIS
                    if 0 <= carro_atual < len(CARROS_DISPONIVEIS):
                        carro_atual = CARROS_DISPONIVEIS[carro_atual].get("prefixo_cor", "Car1")
                    else:
                        carro_atual = "Car1"
                
                nivel_pneu = gerenciador_progresso.obter_upgrade(carro_atual, "rodas")
                
                # Se não tem pneus nível 1, pedir para comprar
                if nivel_pneu < 1:
                    return "Compre pneus nível 1 com Boris ou Crank para poder correr na montanha."
                
                # Se tem pneus, objetivo é completar a corrida
                return "Complete o Teste de Fluxo na montanha sob supervisão de Akira."
            
            return objetivo
        return ""
    
    def atualizar_objetivo_missao(self, missao_id: str, novo_objetivo: str):
        """Atualiza o objetivo de uma missão dinamicamente"""
        if missao_id in self.missoes:
            self.missoes[missao_id]["objetivo"] = novo_objetivo
    
    def obter_todas_missoes(self):
        """Retorna todas as missões como uma lista ordenada por capítulo"""
        missoes_lista = []
        for missao_id, missao in self.missoes.items():
            missoes_lista.append(missao)
        missoes_lista.sort(key=lambda m: (m.get("chapter", "ch1"), m.get("id", "")))
        return missoes_lista

gerenciador_missoes = GerenciadorMissoes()

