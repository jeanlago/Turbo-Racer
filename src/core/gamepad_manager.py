# core/gamepad_manager.py
import pygame
import json
import os
from config import DIR_PROJETO

class GamepadManager:
    """Gerenciador de controles (gamepads/joysticks)"""
    
    def __init__(self):
        self.joysticks = []
        self.controles_config = {}
        self.config_path = os.path.join(DIR_PROJETO, 'data', 'controles_config.json')
        self._inicializar_joysticks()
        self._carregar_configuracao()
    
    def _inicializar_joysticks(self):
        """Inicializa todos os joysticks conectados"""
        pygame.joystick.init()
        num_joysticks = pygame.joystick.get_count()
        
        for i in range(num_joysticks):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            print(f"Controle conectado: {joystick.get_name()} (ID: {i})")
            print(f"  - Eixos: {joystick.get_numaxes()}, Botões: {joystick.get_numbuttons()}, Hats: {joystick.get_numhats()}")
    
    def _carregar_configuracao(self):
        """Carrega configuração de controles do arquivo"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.controles_config = json.load(f)
                self._ajustar_joystick_ids()
                # Verificar se precisa atualizar configuração para PS5
                self._atualizar_configuracao_ps5()
            except Exception as e:
                print(f"Erro ao carregar configuração de controles: {e}")
                self._configuracao_padrao()
        else:
            self._configuracao_padrao()
    
    def _atualizar_configuracao_ps5(self):
        """Atualiza configuração se detectar PS5 e ainda não estiver configurado corretamente"""
        atualizado = False
        
        # Verificar P1
        if len(self.joysticks) > 0:
            tipo_p1 = self._detectar_tipo_controle(0)
            if tipo_p1 in ["ps5", "ps4"]:
                # Verificar se a configuração atual está correta
                p1_config = self.controles_config.get("p1", {})
                freio_mao_index = p1_config.get("freio_mao", {}).get("index")
                drift_index = p1_config.get("drift", {}).get("index")
                
                # Atualizar se necessário (PS5/PS4 usa botão 2 para freio_mao e botão 1 para drift)
                if freio_mao_index != 2 or drift_index != 1:
                    config = {
                        "acelerar": {"tipo": "axis", "index": 5, "invertido": False},
                        "frear": {"tipo": "axis", "index": 4, "invertido": False},
                        "direita": {"tipo": "axis", "index": 0, "invertido": False},
                        "esquerda": {"tipo": "axis", "index": 0, "invertido": False},
                        "turbo": {"tipo": "button", "index": 0},
                        "freio_mao": {"tipo": "button", "index": 2},
                        "drift": {"tipo": "button", "index": 1},
                    }
                    if "p1" not in self.controles_config:
                        self.controles_config["p1"] = {}
                    self.controles_config["p1"].update(config)
                    atualizado = True
                    print(f"{tipo_p1.upper()} detectado para Player 1 - Configuração atualizada")
        
        # Verificar P2
        if len(self.joysticks) > 1:
            tipo_p2 = self._detectar_tipo_controle(1)
            if tipo_p2 in ["ps5", "ps4"]:
                p2_config = self.controles_config.get("p2", {})
                freio_mao_index = p2_config.get("freio_mao", {}).get("index")
                drift_index = p2_config.get("drift", {}).get("index")
                
                if freio_mao_index != 2 or drift_index != 1:
                    config = {
                        "acelerar": {"tipo": "axis", "index": 5, "invertido": False},
                        "frear": {"tipo": "axis", "index": 4, "invertido": False},
                        "direita": {"tipo": "axis", "index": 0, "invertido": False},
                        "esquerda": {"tipo": "axis", "index": 0, "invertido": False},
                        "turbo": {"tipo": "button", "index": 0},
                        "freio_mao": {"tipo": "button", "index": 2},
                        "drift": {"tipo": "button", "index": 1},
                    }
                    if "p2" not in self.controles_config:
                        self.controles_config["p2"] = {}
                    self.controles_config["p2"].update(config)
                    atualizado = True
                    print(f"{tipo_p2.upper()} detectado para Player 2 - Configuração atualizada")
        
        if atualizado:
            self._salvar_configuracao()
    
    def _ajustar_joystick_ids(self):
        """Ajusta os IDs dos joysticks baseado no número de controles conectados"""
        num_joysticks = len(self.joysticks)
        
        if "p1" in self.controles_config:
            joystick_id_p1 = self.controles_config["p1"].get("joystick_id", 0)
            if joystick_id_p1 >= num_joysticks:
                self.controles_config["p1"]["joystick_id"] = 0
        
        if "p2" in self.controles_config:
            joystick_id_p2 = self.controles_config["p2"].get("joystick_id", 1)
            if joystick_id_p2 >= num_joysticks:
                self.controles_config["p2"]["joystick_id"] = 1 if num_joysticks > 1 else -1
    
    def _detectar_tipo_controle(self, joystick_id):
        """Detecta o tipo de controle baseado no nome"""
        if joystick_id >= len(self.joysticks):
            return "generic"
        
        nome = self.joysticks[joystick_id].get_name().lower()
        
        # Detectar PS5
        if "ps5" in nome or "playstation 5" in nome or "dualsense" in nome:
            return "ps5"
        # Detectar PS4
        elif "ps4" in nome or "playstation 4" in nome or "dualshock" in nome:
            return "ps4"
        # Detectar Xbox
        elif "xbox" in nome or "xinput" in nome:
            return "xbox"
        else:
            return "generic"
    
    def _configuracao_padrao(self):
        """Define configuração padrão para controles"""
        # Detectar tipo de controle para P1
        tipo_p1 = self._detectar_tipo_controle(0) if len(self.joysticks) > 0 else "generic"
        tipo_p2 = self._detectar_tipo_controle(1) if len(self.joysticks) > 1 else "generic"
        
        # Configuração para PS5
        config_ps5 = {
            "acelerar": {"tipo": "axis", "index": 5, "invertido": False},  # R2 (trigger direito)
            "frear": {"tipo": "axis", "index": 4, "invertido": False},     # L2 (trigger esquerdo)
            "direita": {"tipo": "axis", "index": 0, "invertido": False},    # Stick esquerdo horizontal
            "esquerda": {"tipo": "axis", "index": 0, "invertido": False},   # Stick esquerdo horizontal
            "turbo": {"tipo": "button", "index": 0},                         # X (Cross)
            "freio_mao": {"tipo": "button", "index": 2},                     # Quadrado
            "drift": {"tipo": "button", "index": 1},                         # Círculo
        }
        
        # Configuração para PS4 (similar ao PS5)
        config_ps4 = {
            "acelerar": {"tipo": "axis", "index": 5, "invertido": False},  # R2
            "frear": {"tipo": "axis", "index": 4, "invertido": False},     # L2
            "direita": {"tipo": "axis", "index": 0, "invertido": False},    # Stick esquerdo horizontal
            "esquerda": {"tipo": "axis", "index": 0, "invertido": False},   # Stick esquerdo horizontal
            "turbo": {"tipo": "button", "index": 0},                         # X
            "freio_mao": {"tipo": "button", "index": 2},                     # Quadrado
            "drift": {"tipo": "button", "index": 1},                         # Círculo
        }
        
        # Configuração genérica (Xbox ou outros)
        config_generic = {
            "acelerar": {"tipo": "axis", "index": 5, "invertido": False},
            "frear": {"tipo": "axis", "index": 4, "invertido": False},
            "direita": {"tipo": "axis", "index": 0, "invertido": False},
            "esquerda": {"tipo": "axis", "index": 0, "invertido": False},
            "turbo": {"tipo": "button", "index": 0},
            "freio_mao": {"tipo": "button", "index": 2},
            "drift": {"tipo": "button", "index": 1},
        }
        
        # Selecionar configuração baseada no tipo detectado
        if tipo_p1 == "ps5":
            config_p1 = config_ps5.copy()
            print("PS5 detectado para Player 1 - Configuração aplicada")
        elif tipo_p1 == "ps4":
            config_p1 = config_ps4.copy()
            print("PS4 detectado para Player 1 - Configuração aplicada")
        else:
            config_p1 = config_generic.copy()
        
        if tipo_p2 == "ps5":
            config_p2 = config_ps5.copy()
            print("PS5 detectado para Player 2 - Configuração aplicada")
        elif tipo_p2 == "ps4":
            config_p2 = config_ps4.copy()
            print("PS4 detectado para Player 2 - Configuração aplicada")
        else:
            config_p2 = config_generic.copy()
        
        self.controles_config = {
            "p1": {
                **config_p1,
                "joystick_id": 0
            },
            "p2": {
                **config_p2,
                "joystick_id": 1 if len(self.joysticks) > 1 else -1
            }
        }
        self._salvar_configuracao()
    
    def _salvar_configuracao(self):
        """Salva configuração de controles no arquivo"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.controles_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração de controles: {e}")
    
    def obter_input(self, player_id, acao, teclas=None):
        """
        Obtém input de controle ou teclado para uma ação específica
        
        Args:
            player_id: "p1" ou "p2"
            acao: "acelerar", "frear", "direita", "esquerda", "turbo", "freio_mao", "drift"
            teclas: dict de teclas pressionadas (opcional, para fallback)
        
        Returns:
            float ou bool: valor do input (0.0-1.0 para eixos, True/False para botões)
        """
        if player_id not in self.controles_config:
            return False
        
        config = self.controles_config[player_id]
        joystick_id = config.get("joystick_id", 0)
        
        if joystick_id < len(self.joysticks) and joystick_id >= 0:
            joystick = self.joysticks[joystick_id]
            
            if acao in config:
                acao_config = config[acao]
                tipo = acao_config.get("tipo")
                index = acao_config.get("index", 0)
                
                if tipo == "axis":
                    # Eixo analógico
                    valor_raw = joystick.get_axis(index)
                    
                    # Aplicar deadzone
                    deadzone = 0.2
                    if abs(valor_raw) < deadzone:
                        valor_raw = 0.0
                    
                    # Para direção (esquerda/direita), processar ANTES de inverter
                    if acao in ["direita", "esquerda"]:
                        # O eixo 0 retorna: negativo = esquerda, positivo = direita
                        if acao == "direita":
                            # Direita: retornar apenas valores positivos do eixo
                            valor = max(0.0, valor_raw)
                        elif acao == "esquerda":
                            # Esquerda: retornar apenas valores negativos (convertidos para positivo)
                            valor = max(0.0, -valor_raw)
                        return min(1.0, max(0.0, valor))
                    
                    # Para outras ações, aplicar inversão se necessário
                    valor = valor_raw
                    if acao_config.get("invertido", False):
                        valor = -valor
                    
                    # Normalizar para 0.0-1.0
                    if index >= 4:  # Triggers (RT/LT) - geralmente vêm como -1.0 a 1.0
                        # Triggers: converter de -1.0 a 1.0 para 0.0 a 1.0
                        # PS5: triggers vêm como -1.0 (solto) a 1.0 (pressionado)
                        # Mas alguns drivers podem reportar 0.0 a 1.0
                        if valor < 0:
                            # Se negativo, converter para positivo (0.0 a 1.0)
                            valor = (valor + 1.0) / 2.0
                        else:
                            # Se já positivo, usar diretamente
                            valor = abs(valor)
                    else:  # Sticks - vêm como -1.0 a 1.0
                        if acao in ["acelerar", "frear"]:
                            # Para acelerar/frear, usar apenas positivo (eixo Y do stick esquerdo)
                            # Assumindo que acelerar/frear usam eixo Y (index 1) ou triggers
                            if acao == "acelerar":
                                # Acelerar: usar valor negativo do eixo Y (para frente = negativo no pygame)
                                valor = max(0.0, -valor) if index == 1 else max(0.0, valor)
                            else:  # frear
                                # Frear: usar valor positivo do eixo Y (para trás = positivo no pygame)
                                valor = max(0.0, valor) if index == 1 else max(0.0, -valor)
                        else:
                            valor = abs(valor)
                    
                    return min(1.0, max(0.0, valor))
                
                elif tipo == "button":
                    # Botão digital
                    valor = joystick.get_button(index) > 0
                    # DEBUG: Mostrar quando botão de freio de mão ou drift é pressionado
                    if acao in ("freio_mao", "drift") and valor:
                        print(f"[DEBUG GAMEPAD] {acao} ativado - botão {index} pressionado (player {player_id})")
                    return valor
        
        # Fallback para teclado se configurado
        if teclas is not None:
            # Mapear ações para teclas padrão
            teclas_padrao = {
                "p1": {
                    "acelerar": pygame.K_w,
                    "frear": pygame.K_s,
                    "direita": pygame.K_d,
                    "esquerda": pygame.K_a,
                    "turbo": pygame.K_LSHIFT
                },
                "p2": {
                    "acelerar": pygame.K_UP,
                    "frear": pygame.K_DOWN,
                    "direita": pygame.K_RIGHT,
                    "esquerda": pygame.K_LEFT,
                    "turbo": pygame.K_RSHIFT
                }
            }
            
            if player_id in teclas_padrao and acao in teclas_padrao[player_id]:
                tecla = teclas_padrao[player_id][acao]
                return teclas[tecla] if tecla in teclas else False
        
        return False
    
    def obter_inputs_carro(self, player_id, teclas=None):
        """
        Obtém todos os inputs necessários para controlar um carro
        
        Returns:
            dict ou None: {
                "acelerar": bool,
                "frear": bool,
                "direita": bool,
                "esquerda": bool,
                "turbo": bool,
                "freio_mao": bool,
                "drift": bool
            } ou None se deve usar teclado
        """
        config = self.controles_config.get(player_id, {})
        joystick_id = config.get("joystick_id", 0)
        
        # Obter inputs do controle
        acelerar_input = None
        frear_input = None
        direita_input = None
        esquerda_input = None
        turbo_input = None
        freio_mao_input = None
        drift_input = None
        
        if joystick_id < len(self.joysticks) and joystick_id >= 0:
            acelerar_input = self.obter_input(player_id, "acelerar", None)
            frear_input = self.obter_input(player_id, "frear", None)
            direita_input = self.obter_input(player_id, "direita", None)
            esquerda_input = self.obter_input(player_id, "esquerda", None)
            turbo_input = self.obter_input(player_id, "turbo", None)
            freio_mao_input = self.obter_input(player_id, "freio_mao", None)
            drift_input = self.obter_input(player_id, "drift", None)
        
        # Verificar se há input de controle ativo
        tem_input_controle = (acelerar_input or frear_input or direita_input or esquerda_input or turbo_input or freio_mao_input or drift_input)
        
        # Se não há controle conectado ou nenhum input ativo, usar teclado
        if not tem_input_controle and teclas is not None:
            # Se não há controle, retornar None para usar teclado padrão
            # O freio de mão do teclado será adicionado no main.py
            return None
        
        # Se há controle mas não tem freio_mao configurado, usar teclado como fallback
        if joystick_id < len(self.joysticks) and joystick_id >= 0:
            import pygame
            if not freio_mao_input and not drift_input and teclas is not None:
                # Adicionar freio de mão do teclado como fallback se não estiver configurado no controle
                if player_id == "p1":
                    freio_mao_input = freio_mao_input or teclas[pygame.K_SPACE]
                elif player_id == "p2":
                    freio_mao_input = freio_mao_input or teclas[pygame.K_KP0]
        
        # Converter inputs para booleanos com threshold
        return {
            "acelerar": (acelerar_input > 0.1) if isinstance(acelerar_input, (int, float)) else bool(acelerar_input),
            "frear": (frear_input > 0.1) if isinstance(frear_input, (int, float)) else bool(frear_input),
            "direita": (direita_input > 0.1) if isinstance(direita_input, (int, float)) else bool(direita_input),
            "esquerda": (esquerda_input > 0.1) if isinstance(esquerda_input, (int, float)) else bool(esquerda_input),
            "turbo": (turbo_input > 0) if isinstance(turbo_input, (int, float)) else bool(turbo_input),
            "freio_mao": (freio_mao_input > 0) if isinstance(freio_mao_input, (int, float)) else bool(freio_mao_input),
            "drift": (drift_input > 0) if isinstance(drift_input, (int, float)) else bool(drift_input)
        }
    
    def atualizar_configuracao(self, player_id, acao, tipo, index, invertido=False):
        """Atualiza configuração de um controle"""
        if player_id not in self.controles_config:
            self.controles_config[player_id] = {}
        
        self.controles_config[player_id][acao] = {
            "tipo": tipo,
            "index": index,
            "invertido": invertido
        }
        self._salvar_configuracao()
    
    def obter_numero_controles(self):
        """Retorna o número de controles conectados"""
        return len(self.joysticks)
    
    def obter_nome_controle(self, joystick_id):
        """Retorna o nome de um controle"""
        if 0 <= joystick_id < len(self.joysticks):
            return self.joysticks[joystick_id].get_name()
        return "Nenhum"

# Instância global
gerenciador_gamepad = GamepadManager()

