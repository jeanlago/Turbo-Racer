# core/menu_controles.py
"""Funções auxiliares para processar eventos de controle no menu"""
import pygame

_ultimo_tempo_navegacao = {}
_ultimo_valor_axis = {}
_ultimo_estado_dpad = {}
_tempo_inicio_hold = {}
_direcao_hold = {}

def processar_eventos_controle_menu(ev, opcao_atual, num_opcoes, joystick_id=0, tempo_atual=None):
    """
    Processa eventos de controle para navegação no menu
    
    Args:
        ev: evento do pygame
        opcao_atual: índice da opção atual
        num_opcoes: número total de opções
        joystick_id: ID do joystick a usar (padrão: 0)
        tempo_atual: tempo atual em milissegundos (para debounce)
    
    Returns:
        dict com ações: {"acao": "cima"|"baixo"|"esquerda"|"direita"|"confirmar"|"cancelar"|None}
    """
    global _ultimo_tempo_navegacao, _ultimo_valor_axis, _tempo_inicio_hold, _direcao_hold
    
    if tempo_atual is None:
        tempo_atual = pygame.time.get_ticks()
    
    chave_debounce = f"{joystick_id}_navegacao"
    chave_hold = f"{joystick_id}_hold"
    
    debounce_tempo = 200
    tempo_hold_inicial = 500
    debounce_hold = 50
    
    from core.gamepad_manager import gerenciador_gamepad
    direcao_atual = None
    if joystick_id < len(gerenciador_gamepad.joysticks):
        joystick = gerenciador_gamepad.joysticks[joystick_id]
        
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            hat_x, hat_y = hat
            if hat_y == 1:
                direcao_atual = "cima"
            elif hat_y == -1:
                direcao_atual = "baixo"
            elif hat_x == -1:
                direcao_atual = "esquerda"
            elif hat_x == 1:
                direcao_atual = "direita"
        else:
            # D-pad como botões
            if joystick.get_numbuttons() > 14:
                if joystick.get_button(11):  # D-pad Up
                    direcao_atual = "cima"
                elif joystick.get_button(12):  # D-pad Down
                    direcao_atual = "baixo"
                elif joystick.get_button(13):  # D-pad Left
                    direcao_atual = "esquerda"
                elif joystick.get_button(14):  # D-pad Right
                    direcao_atual = "direita"
    
    if direcao_atual:
        if chave_hold not in _direcao_hold or _direcao_hold[chave_hold] != direcao_atual:
            _tempo_inicio_hold[chave_hold] = tempo_atual
            _direcao_hold[chave_hold] = direcao_atual
        else:
            tempo_segurando = tempo_atual - _tempo_inicio_hold.get(chave_hold, tempo_atual)
            if tempo_segurando >= tempo_hold_inicial:
                debounce_tempo = debounce_hold
    else:
        if chave_hold in _direcao_hold:
            del _direcao_hold[chave_hold]
        if chave_hold in _tempo_inicio_hold:
            del _tempo_inicio_hold[chave_hold]
    
    if chave_debounce in _ultimo_tempo_navegacao:
        tempo_decorrido = tempo_atual - _ultimo_tempo_navegacao[chave_debounce]
        if tempo_decorrido < debounce_tempo:
            if ev.type == pygame.JOYAXISMOTION:
                return None
    
    if ev.type == pygame.JOYAXISMOTION:
        if ev.joy == joystick_id:
            deadzone = 0.7
            
            chave_axis = f"{joystick_id}_{ev.axis}"
            valor_anterior = _ultimo_valor_axis.get(chave_axis, 0.0)
            
            if ev.axis == 1:
                valor_atual = ev.value
                if abs(valor_atual) > deadzone:
                    mudou_direcao = False
                    if valor_anterior <= deadzone and valor_atual > deadzone:
                        mudou_direcao = True
                    elif valor_anterior >= -deadzone and valor_atual < -deadzone:
                        mudou_direcao = True
                    elif (valor_anterior < 0 and valor_atual > 0) or (valor_anterior > 0 and valor_atual < 0):
                        mudou_direcao = True
                    
                    if mudou_direcao:
                        if chave_debounce not in _ultimo_tempo_navegacao or \
                           tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                            _ultimo_valor_axis[chave_axis] = valor_atual
                            _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                            if valor_atual < -deadzone:
                                if num_opcoes > 0:
                                    return {"acao": "cima", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "analogico"}
                                else:
                                    return {"acao": "cima", "fonte": "analogico"}
                            elif valor_atual > deadzone:
                                if num_opcoes > 0:
                                    return {"acao": "baixo", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "analogico"}
                                else:
                                    return {"acao": "baixo", "fonte": "analogico"}
                    else:
                        _ultimo_valor_axis[chave_axis] = valor_atual
                else:
                    if abs(valor_anterior) > deadzone:
                        _ultimo_valor_axis[chave_axis] = 0.0
                    else:
                        _ultimo_valor_axis[chave_axis] = valor_atual
            
            elif ev.axis == 0:
                valor_atual = ev.value
                if abs(valor_atual) > deadzone:
                    mudou_direcao = False
                    if valor_anterior <= deadzone and valor_atual > deadzone:
                        mudou_direcao = True
                    elif valor_anterior >= -deadzone and valor_atual < -deadzone:
                        mudou_direcao = True
                    elif (valor_anterior < 0 and valor_atual > 0) or (valor_anterior > 0 and valor_atual < 0):
                        mudou_direcao = True
                    
                    if mudou_direcao:
                        if chave_debounce not in _ultimo_tempo_navegacao or \
                           tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                            _ultimo_valor_axis[chave_axis] = valor_atual
                            _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                            if valor_atual < -deadzone:
                                return {"acao": "esquerda", "fonte": "analogico"}
                            elif valor_atual > deadzone:
                                return {"acao": "direita", "fonte": "analogico"}
                    else:
                        _ultimo_valor_axis[chave_axis] = valor_atual
                else:
                    if abs(valor_anterior) > deadzone:
                        _ultimo_valor_axis[chave_axis] = 0.0
                    else:
                        _ultimo_valor_axis[chave_axis] = valor_atual
    
    elif ev.type == pygame.JOYHATMOTION:
        if ev.joy == joystick_id:
            hat_x, hat_y = ev.value
            if hat_y == 1:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    if num_opcoes > 0:
                        return {"acao": "cima", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "cima", "fonte": "dpad"}
            elif hat_y == -1:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    if num_opcoes > 0:
                        return {"acao": "baixo", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "baixo", "fonte": "dpad"}
            elif hat_x == -1:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    if num_opcoes > 0:
                        return {"acao": "esquerda", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "esquerda", "fonte": "dpad"}
            elif hat_x == 1:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    if num_opcoes > 0:
                        return {"acao": "direita", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "direita", "fonte": "dpad"}
    
    elif ev.type == pygame.JOYBUTTONDOWN:
        if ev.joy == joystick_id:
            from core.gamepad_manager import gerenciador_gamepad
            tipo_controle = "generic"
            if joystick_id < len(gerenciador_gamepad.joysticks):
                tipo_controle = gerenciador_gamepad._detectar_tipo_controle(joystick_id)
            
            if ev.button == 0:
                return {"acao": "confirmar"}
            elif ev.button == 1:
                return {"acao": "cancelar"}
            elif ev.button == 2:
                return {"acao": "alternativa"}
            elif ev.button == 4:
                chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                    return {"acao": "carro_anterior", "fonte": "botao"}
            elif ev.button == 5:
                chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                    return {"acao": "carro_proximo", "fonte": "botao"}
            elif ev.button == 9:
                from core.gamepad_manager import gerenciador_gamepad
                if joystick_id < len(gerenciador_gamepad.joysticks):
                    joystick = gerenciador_gamepad.joysticks[joystick_id]
                    nome_controle = joystick.get_name().lower()
                    if "ps5" in nome_controle or "ps4" in nome_controle or "playstation" in nome_controle or "dualsense" in nome_controle or "dualshock" in nome_controle:
                        return {"acao": "pausar"}
                    chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                    if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                       tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                        _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                        return {"acao": "carro_anterior", "fonte": "botao"}
                else:
                    chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                    if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                       tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                        _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                        return {"acao": "carro_anterior", "fonte": "botao"}
            elif ev.button == 10:
                chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                    return {"acao": "carro_proximo", "fonte": "botao"}
            elif ev.button == 11:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    return {"acao": "cima", "opcao": (opcao_atual - 1) % num_opcoes if num_opcoes > 0 else 0, "fonte": "dpad"}
            elif ev.button == 12:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    return {"acao": "baixo", "opcao": (opcao_atual + 1) % num_opcoes if num_opcoes > 0 else 0, "fonte": "dpad"}
            elif ev.button == 13:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    if num_opcoes > 0:
                        return {"acao": "esquerda", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "esquerda", "fonte": "dpad"}
            elif ev.button == 14:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    if num_opcoes > 0:
                        return {"acao": "direita", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "direita", "fonte": "dpad"}
            elif ev.button == 6:
                if tipo_controle == "xbox":
                    return {"acao": "pausar"}
                elif tipo_controle in ["ps5", "ps4"]:
                    return {"acao": "pausar"}
                else:
                    return {"acao": "pausar"}
            elif ev.button == 7:
                if tipo_controle == "xbox":
                    return {"acao": "pausar"}
                elif tipo_controle in ["ps5", "ps4"]:
                    return {"acao": "pausar"}
            elif ev.button == 8:
                if tipo_controle in ["ps5", "ps4"]:
                    return {"acao": "pausar"}
    
    return None

def processar_navegacao_hold(joystick_id=0, tempo_atual=None):
    """
    Processa navegação contínua quando um botão está sendo mantido pressionado (modo "hold")
    
    Args:
        joystick_id: ID do joystick a usar (padrão: 0)
        tempo_atual: tempo atual em milissegundos
    
    Returns:
        dict com ações ou None se não houver navegação em modo hold
    """
    global _tempo_inicio_hold, _direcao_hold, _ultimo_tempo_navegacao
    
    if tempo_atual is None:
        tempo_atual = pygame.time.get_ticks()
    
    from core.gamepad_manager import gerenciador_gamepad
    
    if joystick_id >= len(gerenciador_gamepad.joysticks):
        return None
    
    joystick = gerenciador_gamepad.joysticks[joystick_id]
    chave_hold = f"{joystick_id}_hold"
    chave_debounce = f"{joystick_id}_navegacao"
    
    direcao_atual = None
    if joystick.get_numhats() > 0:
        hat = joystick.get_hat(0)
        hat_x, hat_y = hat
        if hat_y == 1:
            direcao_atual = "cima"
        elif hat_y == -1:
            direcao_atual = "baixo"
        elif hat_x == -1:
            direcao_atual = "esquerda"
        elif hat_x == 1:
            direcao_atual = "direita"
    else:
        if joystick.get_numbuttons() > 14:
            if joystick.get_button(11):  # D-pad Up
                direcao_atual = "cima"
            elif joystick.get_button(12):  # D-pad Down
                direcao_atual = "baixo"
            elif joystick.get_button(13):  # D-pad Left
                direcao_atual = "esquerda"
            elif joystick.get_button(14):  # D-pad Right
                direcao_atual = "direita"
    
    if direcao_atual:
        if chave_hold in _direcao_hold and _direcao_hold[chave_hold] == direcao_atual:
            tempo_segurando = tempo_atual - _tempo_inicio_hold.get(chave_hold, tempo_atual)
            tempo_hold_inicial = 500
            debounce_hold = 50
            
            if tempo_segurando >= tempo_hold_inicial:
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_hold:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    return {"acao": direcao_atual, "fonte": "hold"}
    
    return None

def obter_estado_controle_menu(joystick_id=0):
    """
    Obtém estado atual do controle (para detecção contínua, não apenas eventos)
    
    Returns:
        dict com estado: {"cima": bool, "baixo": bool, "esquerda": bool, "direita": bool, "confirmar": bool, "cancelar": bool}
    """
    global _ultimo_estado_dpad, _ultimo_tempo_navegacao
    from core.gamepad_manager import gerenciador_gamepad
    
    estado = {
        "cima": False,
        "baixo": False,
        "esquerda": False,
        "direita": False,
        "confirmar": False,
        "cancelar": False
    }
    
    if joystick_id < len(gerenciador_gamepad.joysticks):
        joystick = gerenciador_gamepad.joysticks[joystick_id]
        
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            hat_x, hat_y = hat
            chave_dpad = f"{joystick_id}_dpad"
            estado_anterior = _ultimo_estado_dpad.get(chave_dpad, (0, 0))
            
            hat_anterior_x, hat_anterior_y = estado_anterior
            
            if hat_y == 1 and hat_anterior_y != 1:
                estado["cima"] = True
            elif hat_y == -1 and hat_anterior_y != -1:
                estado["baixo"] = True
            if hat_x == -1 and hat_anterior_x != -1:
                estado["esquerda"] = True
            elif hat_x == 1 and hat_anterior_x != 1:
                estado["direita"] = True
            
            if (hat_x != 0 or hat_y != 0) and (hat_x != hat_anterior_x or hat_y != hat_anterior_y):
                print(f"DEBUG HAT: hat_x={hat_x}, hat_y={hat_y}, anterior=({hat_anterior_x}, {hat_anterior_y})")
            
            _ultimo_estado_dpad[chave_dpad] = (hat_x, hat_y)
        else:
            if joystick.get_numbuttons() > 14:
                chave_dpad = f"{joystick_id}_dpad_buttons"
                estado_anterior = _ultimo_estado_dpad.get(chave_dpad, (False, False, False, False))
                
                dpad_up = joystick.get_button(11) if joystick.get_numbuttons() > 11 else False
                dpad_down = joystick.get_button(12) if joystick.get_numbuttons() > 12 else False
                dpad_left = joystick.get_button(13) if joystick.get_numbuttons() > 13 else False
                dpad_right = joystick.get_button(14) if joystick.get_numbuttons() > 14 else False
                
                if dpad_up and not estado_anterior[0]:
                    estado["cima"] = True
                if dpad_down and not estado_anterior[1]:
                    estado["baixo"] = True
                if dpad_left and not estado_anterior[2]:
                    estado["esquerda"] = True
                if dpad_right and not estado_anterior[3]:
                    estado["direita"] = True
                
                _ultimo_estado_dpad[chave_dpad] = (dpad_up, dpad_down, dpad_left, dpad_right)
    
    return estado

