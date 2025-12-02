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
        
        # Carregar informações detalhadas das missões
        self._carregar_missoes_info()
    
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
        """Carrega as missões completas do arquivo"""
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
        """Salva as missões completas no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_MISSOES_COMPLETAS), exist_ok=True)
            data = {
                "missoes_completas": list(self.missoes_completas),
                "missao_ativa_id": self.missao_ativa_id
            }
            with open(CAMINHO_MISSOES_COMPLETAS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[MISSÕES] Missões salvas: {len(self.missoes_completas)} completas, ativa: {self.missao_ativa_id}")
        except Exception as e:
            print(f"[MISSÕES] Erro ao salvar missões completas: {e}")
            import traceback
            traceback.print_exc()
    
    def ativar_missao(self, missao_id: str):
        """Ativa uma missão"""
        if missao_id in self.missoes:
            self.missao_ativa_id = missao_id
            self.salvar()
            return True
        return False
    
    def ativar_por_cena(self, scene_id: str):
        """Ativa uma missão baseada no ID da cena"""
        for missao_id, missao in self.missoes.items():
            if missao.get("activateOnSceneId") == scene_id:
                if missao_id not in self.missoes_completas:
                    print(f"[MISSÕES] Ativando missão {missao_id} pela cena {scene_id}")
                    self.ativar_missao(missao_id)
                    return missao_id
                else:
                    print(f"[MISSÕES] Missão {missao_id} já foi completada, não ativando novamente")
        return None
    
    def completar_missao(self, missao_id: str = None):
        """Completa a missão ativa ou uma missão específica"""
        from core.progresso import gerenciador_progresso
        from core.narrative_system import narrative_system
        
        if missao_id is None:
            missao_id = self.missao_ativa_id
        
        if missao_id and missao_id in self.missoes:
            if missao_id not in self.missoes_completas:
                self.missoes_completas.add(missao_id)
                print(f"[MISSÕES] Missão '{missao_id}' marcada como completa")
                
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
                missoes_ch4 = ["m15_ruido_nos_servidores", "m16_contatos_estranhos"]
                if missao_id in missoes_ch4:
                    todas_ch4_completas = all(m in self.missoes_completas for m in missoes_ch4)
                    if todas_ch4_completas:
                        print(f"[MISSÕES] Todas as missões do Capítulo 4 completadas! Preparando para iniciar Capítulo 5...")
                        # Marcar capítulo 4 como completo
                        gerenciador_progresso.marcar_capitulo_completo("ch4")
                        gerenciador_progresso.definir_capitulo_atual("ch5")
                        gerenciador_progresso.salvar()
                        # Iniciar capítulo 5 automaticamente
                        if narrative_system.iniciar_capitulo("ch5"):
                            narrative_system.active = True
                            print(f"[MISSÕES] Capítulo 5 iniciado automaticamente!")
                
                # Verificar se completou a missão m18_circo_da_coroa - desbloquear autódromo
                if missao_id == "m18_circo_da_coroa":
                    print(f"[MISSÕES] Missão m18_circo_da_coroa completada! Desbloqueando autódromo...")
                    from core.mapa_locations import gerenciador_localizacoes
                    gerenciador_localizacoes.desbloquear("autódromo")
                    gerenciador_localizacoes.salvar()
                    print(f"[MISSÕES] Autódromo desbloqueado!")
            
            if self.missao_ativa_id == missao_id:
                self.missao_ativa_id = None
                # Tentar ativar a próxima missão automaticamente
                self._ativar_proxima_missao_automaticamente()
            self.salvar()
            return True
        else:
            if missao_id:
                print(f"[MISSÕES] Aviso: Tentativa de completar missão inexistente: {missao_id}")
        return False
    
    def completar_por_cena(self, scene_id: str):
        """Completa uma missão baseada no ID da cena"""
        for missao_id, missao in self.missoes.items():
            if missao.get("completeOnSceneId") == scene_id:
                self.completar_missao(missao_id)
                return missao_id
        
        # Completar m8_oferta_envenenada quando o jogador decide sobre o empréstimo
        # (tanto aceitando quanto recusando)
        if scene_id in ["ch2_4_loan_accepted", "ch2_5_loan_refused"]:
            if "m8_oferta_envenenada" in self.missoes and "m8_oferta_envenenada" not in self.missoes_completas:
                self.completar_missao("m8_oferta_envenenada")
                return "m8_oferta_envenenada"
        
        return None
    
    def obter_missao_ativa(self):
        """Retorna a missão ativa atual"""
        if self.missao_ativa_id and self.missao_ativa_id in self.missoes:
            return self.missoes[self.missao_ativa_id]
        
        # Se não há missão ativa, tentar ativar automaticamente a próxima baseada no progresso
        self._ativar_proxima_missao_automaticamente()
        
        if self.missao_ativa_id and self.missao_ativa_id in self.missoes:
            return self.missoes[self.missao_ativa_id]
        return None
    
    def _ativar_proxima_missao_automaticamente(self):
        """Ativa automaticamente a próxima missão baseada no progresso do jogador"""
        if self.missao_ativa_id:
            return  # Já há uma missão ativa
        
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
        
        # Verificar progresso da Akira para determinar qual missão ativar
        try:
            from core.akira import akira
            akira_ja_foi_vista = akira.primeira_aparicao_mostrada
        except Exception as e:
            akira_ja_foi_vista = False
        
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
                        self.ativar_missao("m19_jogo_do_rei")
                        return
        
        # Encontrar a primeira missão NÃO COMPLETA do capítulo atual
        for missao_id, missao in missoes_capitulo_atual:
            # PULAR missões que já foram completadas
            if missao_id in self.missoes_completas:
                continue
            
            # Verificar se os pré-requisitos foram cumpridos
            activate_on_scene = missao.get("activateOnSceneId")
            missao_chapter = missao.get("chapter", "ch1")
            
            # Extrair número da missão (m1, m2, m11, m13, etc.)
            try:
                missao_num = int(missao_id.split("_")[0].replace("m", ""))
            except:
                missao_num = 0
            
            # Verificar se todas as missões anteriores do mesmo capítulo foram completadas
            todas_anteriores_completas = True
            for outra_id, outra_missao in missoes_capitulo_atual:
                try:
                    outra_num = int(outra_id.split("_")[0].replace("m", ""))
                except:
                    outra_num = 0
                # Se é uma missão anterior do mesmo capítulo e não está completa
                if outra_num < missao_num and outra_id not in self.missoes_completas:
                    todas_anteriores_completas = False
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
                    # Se a cena ainda não foi vista, mas todas as anteriores foram completadas,
                    # ativar mesmo assim (a cena será vista em breve)
                    elif todas_anteriores_completas:
                        print(f"[MISSÕES] Ativando automaticamente missão {missao_id} (todas anteriores completas, cena {activate_on_scene} será vista em breve)")
                        self.ativar_missao(missao_id)
                        return
                    else:
                        print(f"[MISSÕES] Missão {missao_id} não pode ser ativada: cena {activate_on_scene} não foi vista e nem todas anteriores foram completadas")
                except Exception as e:
                    print(f"[MISSÕES] Erro ao verificar cena para missão {missao_id}: {e}")
                    # Em caso de erro, se todas anteriores foram completadas, ativar mesmo assim
                    if todas_anteriores_completas:
                        print(f"[MISSÕES] Ativando automaticamente missão {missao_id} (erro ao verificar cena, mas todas anteriores completas)")
                        self.ativar_missao(missao_id)
                        return
            else:
                # Missão sem activateOnSceneId - verificar se todas as anteriores foram completadas
                if todas_anteriores_completas:
                    print(f"[MISSÕES] Ativando automaticamente missão {missao_id} (sem activateOnSceneId, todas anteriores completas)")
                    self.ativar_missao(missao_id)
                    return
        
        # Se não encontrou missão no capítulo atual, verificar próximo capítulo
        if capitulo_atual == "ch1":
            proximo_capitulo = "ch2"
        elif capitulo_atual == "ch2":
            proximo_capitulo = "ch3"
        elif capitulo_atual == "ch3":
            proximo_capitulo = "ch4"
        elif capitulo_atual == "ch4":
            proximo_capitulo = "ch5"
        elif capitulo_atual == "ch5":
            # No capítulo 5, não há próximo capítulo, mas pode haver missões pendentes
            pass
        else:
            return
        
        # Verificar se há missões no próximo capítulo
        missoes_proximo = [(mid, m) for mid, m in todas_missoes_ordenadas if m.get("chapter") == proximo_capitulo]
        
        if missoes_proximo:
            for missao_id, missao in missoes_proximo:
                if missao_id not in self.missoes_completas:
                    activate_on_scene = missao.get("activateOnSceneId")
                    if activate_on_scene:
                        try:
                            from core.narrative_system import narrative_system
                            # Verificar tanto cenas_visitadas quanto scenes_visited
                            cenas_visitadas = getattr(narrative_system, 'cenas_visitadas', None) or getattr(narrative_system, 'scenes_visited', None) or set()
                            if activate_on_scene in cenas_visitadas:
                                    print(f"[MISSÕES] Ativando automaticamente missão {missao_id} do próximo capítulo (cena {activate_on_scene} já foi vista)")
                                    self.ativar_missao(missao_id)
                                    return
                        except:
                            pass
                    else:
                        print(f"[MISSÕES] Ativando automaticamente missão {missao_id} do próximo capítulo (sem activateOnSceneId)")
                        self.ativar_missao(missao_id)
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
            "m8_sombra_do_agiota": ("ch2", "baron_debt_active"),
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

