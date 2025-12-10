"""
Sistema de Estados de Localizações no Mapa
Gerencia estados: invisível, bloqueado_visível, desbloqueado
"""
import json
import os
from typing import Dict, Optional, List
from config import DIR_PROJETO

CAMINHO_LOCATIONS = os.path.join(DIR_PROJETO, "data", "mapa_locations.json")

class EstadoLocalizacao:
    """Estados possíveis de uma localização"""
    INVISIVEL = "locked_hidden"
    BLOQUEADO_VISIVEL = "locked_visible"
    DESBLOQUEADO = "unlocked"

class GerenciadorLocalizacoes:
    """Gerencia os estados das localizações no mapa"""
    
    def __init__(self):
        self.locations = {}
        self.carregar()
    
    def carregar(self):
        """Carrega as localizações do progresso.json"""
        try:
            caminho_progresso = os.path.join(os.path.dirname(CAMINHO_LOCATIONS), 'progresso.json')
            caminho_progresso = os.path.normpath(caminho_progresso)
            
            if os.path.exists(caminho_progresso):
                with open(caminho_progresso, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'mapa_locations' in data:
                        self.locations = data.get('mapa_locations', {})
                        print(f"[LOCATIONS] Carregado do progresso.json: {len(self.locations)} localizações")
                        try:
                            self._verificar_estados_progresso()
                        except Exception as e:
                            print(f"[LOCATIONS] Erro ao verificar estados do progresso (será verificado depois): {e}")
                        return
        except Exception as e:
            print(f"[LOCATIONS] Erro ao carregar do progresso.json: {e}")
        
        if os.path.exists(CAMINHO_LOCATIONS):
            try:
                with open(CAMINHO_LOCATIONS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for loc in data.get("locations", []):
                        self.locations[loc["id"]] = {
                            "nome": loc.get("nome", loc["id"]),
                            "state": loc.get("state", EstadoLocalizacao.INVISIVEL),
                            "lockedThought": loc.get("lockedThought"),
                            "unlockFlags": loc.get("unlockFlags", [])
                        }
                self._verificar_estados_progresso()
            except Exception as e:
                print(f"Erro ao carregar localizações: {e}")
                import traceback
                traceback.print_exc()
                self._inicializar_padrao()
        else:
            self._inicializar_padrao()
    
    def _verificar_estados_progresso(self):
        """Verifica e corrige estados das localizações baseado no progresso do jogo"""
        try:
            from core.progresso import gerenciador_progresso
            from core.missoes import gerenciador_missoes
            
            # Verificar montanha - só desbloqueia quando a missão m11 é ativada ou quando unlockLocation:montanha é processado
            if "montanha" in self.locations:
                estado_atual = self.locations["montanha"].get("state")
                # Verificar se a missão m11 foi ativada ou se há flag de desbloqueio
                missao_m11_ativa = gerenciador_missoes.missao_ativa_id == "m11_chamado_da_montanha"
                missao_m11_completa = "m11_chamado_da_montanha" in gerenciador_missoes.missoes_completas
                capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                
                # Montanha deve estar desbloqueada se:
                # 1. Missão m11 está ativa, OU
                # 2. Missão m11 foi completada, OU
                # 3. Está no capítulo 3 ou depois e já completou m11
                deve_estar_desbloqueada = missao_m11_ativa or missao_m11_completa or (capitulo_atual in ["ch3", "ch4", "ch5"] and missao_m11_completa)
                
                if deve_estar_desbloqueada and estado_atual != EstadoLocalizacao.DESBLOQUEADO:
                    # Deveria estar desbloqueada mas não está - desbloquear
                    print(f"[LOCATIONS] Desbloqueando montanha: missão m11 ativa ou completada")
                    self.locations["montanha"]["state"] = EstadoLocalizacao.DESBLOQUEADO
                    self.salvar()
                elif not deve_estar_desbloqueada and estado_atual == EstadoLocalizacao.DESBLOQUEADO:
                    # Está desbloqueada mas não deveria estar - bloquear
                    if capitulo_atual and capitulo_atual not in ["ch3", "ch4", "ch5"]:
                        print(f"[LOCATIONS] Corrigindo estado da montanha: estava desbloqueada mas capítulo atual é {capitulo_atual}")
                        self.locations["montanha"]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
                        self.salvar()
                    elif capitulo_atual == "ch3" and not missao_m11_ativa and not missao_m11_completa:
                        print(f"[LOCATIONS] Corrigindo estado da montanha: missão m11 não está ativa nem completada")
                        self.locations["montanha"]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
                        self.salvar()
            
            # Verificar autódromo - desbloqueia quando m18 está ativa OU quando crownCircuitActive está definida
            if "autódromo" in self.locations:
                estado_atual = self.locations["autódromo"].get("state")
                missao_m18_ativa = gerenciador_missoes.missao_ativa_id == "m18_circo_da_coroa"
                missao_m18_completa = gerenciador_missoes.esta_completa("m18_circo_da_coroa")
                
                # Verificar flag crownCircuitActive
                try:
                    from core.progresso import gerenciador_progresso
                    crown_circuit_active = getattr(gerenciador_progresso, 'crownCircuitActive', False)
                except:
                    crown_circuit_active = False
                
                deve_estar_desbloqueado = missao_m18_ativa or missao_m18_completa or crown_circuit_active
                
                if deve_estar_desbloqueado and estado_atual != EstadoLocalizacao.DESBLOQUEADO:
                    # Deve estar desbloqueado mas não está - desbloquear
                    print(f"[LOCATIONS] Desbloqueando autódromo: m18_ativa={missao_m18_ativa}, m18_completa={missao_m18_completa}, crownCircuitActive={crown_circuit_active}")
                    self.locations["autódromo"]["state"] = EstadoLocalizacao.DESBLOQUEADO
                    self.salvar()
                elif not deve_estar_desbloqueado and estado_atual == EstadoLocalizacao.DESBLOQUEADO:
                    # Não deve estar desbloqueado mas está - bloquear (apenas se não completou)
                    if not missao_m18_completa:
                        print(f"[LOCATIONS] Bloqueando autódromo: m18 não está ativa nem completada e crownCircuitActive não está definida")
                        self.locations["autódromo"]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
                        self.salvar()
            
            # Verificar fosso_ferrugem - só desbloqueia quando unlockLocation:fosso_ferrugem é processado
            if "fosso_ferrugem" in self.locations:
                estado_atual = self.locations["fosso_ferrugem"].get("state")
                # Verificar se a missão m3 está ativa ou se já foi desbloqueado pela narrativa
                missao_m3_ativa = gerenciador_missoes.missao_ativa_id == "m3_rota_da_ferrugem"
                missao_m3_completa = "m3_rota_da_ferrugem" in gerenciador_missoes.missoes_completas
                capitulo_atual = gerenciador_progresso.obter_capitulo_atual()
                
                # Fosso deve estar desbloqueado se:
                # 1. Missão m3 está ativa (já foi mencionado pelo Crank), OU
                # 2. Missão m3 foi completada, OU
                # 3. Já foi desbloqueado pela narrativa (não bloquear novamente)
                deve_estar_desbloqueada = missao_m3_ativa or missao_m3_completa
                
                # Se já está desbloqueado pela narrativa, não bloquear novamente
                # (a narrativa desbloqueia quando o Crank menciona o Boris)
                if estado_atual == EstadoLocalizacao.DESBLOQUEADO:
                    # Se já está desbloqueado, manter desbloqueado (foi desbloqueado pela narrativa)
                    # Não bloquear novamente mesmo se a missão m3 não estiver ativa ainda
                    # A missão será ativada automaticamente quando todas as anteriores forem completas
                    pass
                elif deve_estar_desbloqueada and estado_atual != EstadoLocalizacao.DESBLOQUEADO:
                    # Deveria estar desbloqueado mas não está - desbloquear
                    print(f"[LOCATIONS] Desbloqueando fosso_ferrugem: missão m3 ativa ou completada")
                    self.locations["fosso_ferrugem"]["state"] = EstadoLocalizacao.DESBLOQUEADO
                    self.salvar()
            
            # Verificar cinturão industrial - só desbloqueia quando unlockLocation:cinturao_industrial é processado pela narrativa
            if "cinturao_industrial" in self.locations:
                estado_atual = self.locations["cinturao_industrial"].get("state")
                # Verificar se foi desbloqueado pela narrativa (através de locations_unlocked_by_narrative)
                foi_desbloqueado_narrativa = gerenciador_progresso.locations_unlocked_by_narrative.get("cinturao_industrial", False)
                
                # Se está desbloqueado mas não foi desbloqueado pela narrativa, bloquear novamente
                if estado_atual == EstadoLocalizacao.DESBLOQUEADO and not foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Corrigindo estado do cinturão: estava desbloqueado mas não foi desbloqueado pela narrativa")
                    self.locations["cinturao_industrial"]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
                    self.salvar()
                # Se foi desbloqueado pela narrativa mas está bloqueado, desbloquear
                elif estado_atual != EstadoLocalizacao.DESBLOQUEADO and foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Corrigindo estado do cinturão: foi desbloqueado pela narrativa mas estava bloqueado")
                    self.locations["cinturao_industrial"]["state"] = EstadoLocalizacao.DESBLOQUEADO
                    self.salvar()
            
            # Verificar iate do Barão - só desbloqueia quando unlockLocation:iate_barao é processado pela narrativa
            if "iate_barao" in self.locations:
                estado_atual = self.locations["iate_barao"].get("state")
                # Verificar se foi desbloqueado pela narrativa (através de locations_unlocked_by_narrative)
                foi_desbloqueado_narrativa = gerenciador_progresso.locations_unlocked_by_narrative.get("iate_barao", False)
                
                # Verificar se a cena ch2_2_barao_offer foi visitada (retrocompatibilidade)
                from core.narrative_system import narrative_system
                cena_visitada = "ch2_2_barao_offer" in narrative_system.scenes_visited
                
                # Se a cena foi visitada mas não está marcada como desbloqueado pela narrativa, marcar e desbloquear
                if cena_visitada and not foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Cena ch2_2_barao_offer foi visitada, desbloqueando iate do Barão retroativamente")
                    gerenciador_progresso.locations_unlocked_by_narrative["iate_barao"] = True
                    foi_desbloqueado_narrativa = True
                    gerenciador_progresso.salvar()
                
                # Se está desbloqueado mas não foi desbloqueado pela narrativa, bloquear novamente
                if estado_atual == EstadoLocalizacao.DESBLOQUEADO and not foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Corrigindo estado do iate do Barão: estava desbloqueado mas não foi desbloqueado pela narrativa")
                    self.locations["iate_barao"]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
                    self.salvar()
                # Se foi desbloqueado pela narrativa mas está bloqueado, desbloquear
                elif estado_atual != EstadoLocalizacao.DESBLOQUEADO and foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Corrigindo estado do iate do Barão: foi desbloqueado pela narrativa mas estava bloqueado")
                    self.locations["iate_barao"]["state"] = EstadoLocalizacao.DESBLOQUEADO
                    self.salvar()
            
            # Verificar esconderijo da Pixel - só desbloqueia quando unlockLocation:esconderijo_pixel é processado pela narrativa
            if "esconderijo_pixel" in self.locations:
                estado_atual = self.locations["esconderijo_pixel"].get("state")
                # Verificar se foi desbloqueado pela narrativa (através de locations_unlocked_by_narrative)
                foi_desbloqueado_narrativa = gerenciador_progresso.locations_unlocked_by_narrative.get("esconderijo_pixel", False)
                
                # Verificar se a cena ch4_2_pixel_invitation foi visitada (retrocompatibilidade)
                from core.narrative_system import narrative_system
                cena_visitada = "ch4_2_pixel_invitation" in narrative_system.scenes_visited
                
                # Verificar se a missão m15 está ativa (indica que Pixel já enviou as coordenadas)
                missao_m15_ativa = gerenciador_missoes.missao_ativa_id == "m15_ruido_nos_servidores"
                
                # Se a cena foi visitada OU a missão está ativa, mas não está marcada como desbloqueado pela narrativa, marcar e desbloquear
                if (cena_visitada or missao_m15_ativa) and not foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Cena ch4_2_pixel_invitation visitada ou missão m15 ativa, desbloqueando esconderijo da Pixel retroativamente")
                    gerenciador_progresso.locations_unlocked_by_narrative["esconderijo_pixel"] = True
                    foi_desbloqueado_narrativa = True
                    gerenciador_progresso.salvar()
                
                # Se está desbloqueado mas não foi desbloqueado pela narrativa, bloquear novamente
                if estado_atual == EstadoLocalizacao.DESBLOQUEADO and not foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Corrigindo estado do esconderijo da Pixel: estava desbloqueado mas não foi desbloqueado pela narrativa")
                    self.locations["esconderijo_pixel"]["state"] = EstadoLocalizacao.INVISIVEL
                    self.salvar()
                # Se foi desbloqueado pela narrativa mas está bloqueado, desbloquear
                elif estado_atual != EstadoLocalizacao.DESBLOQUEADO and foi_desbloqueado_narrativa:
                    print(f"[LOCATIONS] Corrigindo estado do esconderijo da Pixel: foi desbloqueado pela narrativa mas estava bloqueado")
                    self.locations["esconderijo_pixel"]["state"] = EstadoLocalizacao.DESBLOQUEADO
                    self.salvar()
        except Exception as e:
            print(f"[LOCATIONS] Erro ao verificar estados do progresso: {e}")
            import traceback
            traceback.print_exc()
    
    def _inicializar_padrao(self):
        """Inicializa com valores padrão se o arquivo não existir"""
        self.locations = {
            "oficina": {
                "nome": "Oficina do Crank",
                "state": EstadoLocalizacao.DESBLOQUEADO,
                "lockedThought": None,
                "unlockFlags": []
            },
            "fosso_ferrugem": {
                "nome": "Fosso de Ferrugem",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": "Ainda não tenho motivo pra ir até lá...",
                "unlockFlags": []
            },
            "cinturao_industrial": {
                "nome": "Cinturão Industrial",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": "Ouvi falar que aqui só entra quem tem inscrição paga… e eu não tô nessa lista ainda.",
                "unlockFlags": ["unlockRaceSet:cinturao_industrial"]
            },
            "montanha": {
                "nome": "Montanha da Akira",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": "Dizem que uma piloto fantasma domina essa montanha. Ainda não fui convidado pra esse velório.",
                "unlockFlags": ["unlockLocation:montanha"]
            },
            "torres_rex": {
                "nome": "Torres do Rex",
                "state": EstadoLocalizacao.BLOQUEADO_VISIVEL,
                "lockedThought": "Esse é outro mundo. Por enquanto, só posso olhar de longe.",
                "unlockFlags": []
            },
            "circuito_coroa": {
                "nome": "Circuito da Coroa",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": "Ainda não tenho motivo pra ir até lá...",
                "unlockFlags": []
            },
            "autódromo": {
                "nome": "Autódromo",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": None,
                "unlockFlags": []
            },
            "iate_barao": {
                "nome": "Iate do Barão",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": "O Barão tem um iate? Claro que tem. Mas ele só recebe quem ele quer.",
                "unlockFlags": ["unlockLocation:iate_barao"]
            },
            "esconderijo_pixel": {
                "nome": "Esconderijo da Pixel",
                "state": EstadoLocalizacao.INVISIVEL,
                "lockedThought": "Ainda não sei onde fica o esconderijo da Pixel...",
                "unlockFlags": ["unlockLocation:esconderijo_pixel"]
            }
        }
        self.salvar()
    
    def salvar(self):
        """Salva as localizações"""
        # Dados são salvos através do GerenciadorProgresso.salvar()
        # Este método existe para compatibilidade, mas não salva mais em arquivo separado
        try:
            from core.progresso import gerenciador_progresso
            gerenciador_progresso.salvar()  # Isso salvará tudo, incluindo localizações
        except Exception as e:
            print(f"Erro ao salvar localizações: {e}")
    
    def obter_estado(self, location_id: str) -> str:
        """Obtém o estado atual de uma localização"""
        if location_id not in self.locations:
            return EstadoLocalizacao.INVISIVEL
        state = self.locations[location_id]["state"]
        if state not in [EstadoLocalizacao.INVISIVEL, EstadoLocalizacao.BLOQUEADO_VISIVEL, EstadoLocalizacao.DESBLOQUEADO]:
            return EstadoLocalizacao.INVISIVEL
        return state
    
    def esta_visivel(self, location_id: str) -> bool:
        """Verifica se uma localização está visível no mapa"""
        state = self.obter_estado(location_id)
        return state in [EstadoLocalizacao.BLOQUEADO_VISIVEL, EstadoLocalizacao.DESBLOQUEADO]
    
    def esta_desbloqueado(self, location_id: str) -> bool:
        """Verifica se uma localização está desbloqueada"""
        return self.obter_estado(location_id) == EstadoLocalizacao.DESBLOQUEADO
    
    def obter_mensagem_bloqueado(self, location_id: str) -> Optional[str]:
        """Obtém a mensagem de pensamento quando a localização está bloqueada"""
        if location_id not in self.locations:
            return "Ainda não tenho motivo pra ir até lá..."
        return self.locations[location_id].get("lockedThought")
    
    def tornar_visivel(self, location_id: str):
        """Torna uma localização visível (mas ainda bloqueada)"""
        if location_id not in self.locations:
            self.locations[location_id] = {
                "nome": location_id.replace("_", " ").title(),
                "state": EstadoLocalizacao.BLOQUEADO_VISIVEL,
                "lockedThought": "Ainda não tenho motivo pra ir até lá...",
                "unlockFlags": []
            }
        else:
            if self.locations[location_id]["state"] == EstadoLocalizacao.INVISIVEL:
                self.locations[location_id]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
        self.salvar()
    
    def desbloquear(self, location_id: str):
        """Desbloqueia uma localização"""
        if location_id not in self.locations:
            self.locations[location_id] = {
                "nome": location_id.replace("_", " ").title(),
                "state": EstadoLocalizacao.DESBLOQUEADO,
                "lockedThought": None,
                "unlockFlags": []
            }
        else:
            self.locations[location_id]["state"] = EstadoLocalizacao.DESBLOQUEADO
        self.salvar()
    
    def processar_efeito_narrativa(self, effect: str):
        """Processa um efeito da narrativa que pode afetar localizações"""
        from core.progresso import gerenciador_progresso
        
        if effect.startswith("unlockLocation:"):
            location_id = effect.split(":", 1)[1]
            self.desbloquear(location_id)
            # Marcar que foi desbloqueado pela narrativa
            if not hasattr(gerenciador_progresso, 'locations_unlocked_by_narrative'):
                gerenciador_progresso.locations_unlocked_by_narrative = {}
            gerenciador_progresso.locations_unlocked_by_narrative[location_id] = True
            # Se desbloqueou o Cinturão, definir flag cinturaoUnlocked
            if location_id == "cinturao_industrial":
                gerenciador_progresso.cinturaoUnlocked = True
            gerenciador_progresso.salvar()
            print(f"[LOCATIONS] Localização {location_id} desbloqueada pela narrativa")
        
        elif effect.startswith("unlockRaceSet:"):
            race_set = effect.split(":", 1)[1]
            race_to_location = {
                "cinturao_industrial": "cinturao_industrial",
                "montanha": "montanha",
                "circuito_coroa": "circuito_coroa"
            }
            if race_set in race_to_location:
                location_id = race_to_location[race_set]
                self.desbloquear(location_id)
                # Marcar que foi desbloqueado pela narrativa
                if not hasattr(gerenciador_progresso, 'locations_unlocked_by_narrative'):
                    gerenciador_progresso.locations_unlocked_by_narrative = {}
                gerenciador_progresso.locations_unlocked_by_narrative[location_id] = True
                # Se desbloqueou o Cinturão, definir flag cinturaoUnlocked
                if location_id == "cinturao_industrial":
                    gerenciador_progresso.cinturaoUnlocked = True
                gerenciador_progresso.salvar()
                print(f"[LOCATIONS] Localização {location_id} desbloqueada pela narrativa (via unlockRaceSet:{race_set})")
        
        elif effect.startswith("mentionLocation:"):
            location_id = effect.split(":", 1)[1]
            self.tornar_visivel(location_id)

gerenciador_localizacoes = GerenciadorLocalizacoes()

