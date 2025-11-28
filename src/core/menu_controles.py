# core/menu_controles.py
"""Funções auxiliares para processar eventos de controle no menu"""
import pygame

# Variável global para controlar debounce de navegação
_ultimo_tempo_navegacao = {}
_ultimo_valor_axis = {}  # Para detectar mudanças de direção
_ultimo_estado_dpad = {}  # Para detectar mudanças no D-pad (hat ou botões)
_tempo_inicio_hold = {}  # Para rastrear quando um botão começou a ser pressionado
_direcao_hold = {}  # Para rastrear a direção que está sendo mantida pressionada

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
    
    # Debounce: evitar movimento muito rápido
    # Se o botão está sendo mantido pressionado, usar debounce mais rápido
    chave_debounce = f"{joystick_id}_navegacao"
    chave_hold = f"{joystick_id}_hold"
    
    # Verificar se há um botão sendo mantido pressionado
    debounce_tempo = 200  # Debounce inicial (200ms)
    tempo_hold_inicial = 500  # Tempo antes de ativar modo "hold" (500ms)
    debounce_hold = 50  # Debounce quando em modo "hold" (50ms)
    
    # Verificar estado atual do D-pad para detectar "hold"
    from core.gamepad_manager import gerenciador_gamepad
    direcao_atual = None
    if joystick_id < len(gerenciador_gamepad.joysticks):
        joystick = gerenciador_gamepad.joysticks[joystick_id]
        
        # Verificar D-pad (hat ou botões)
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
    
    # Gerenciar estado de "hold"
    if direcao_atual:
        if chave_hold not in _direcao_hold or _direcao_hold[chave_hold] != direcao_atual:
            # Nova direção pressionada, iniciar contagem
            _tempo_inicio_hold[chave_hold] = tempo_atual
            _direcao_hold[chave_hold] = direcao_atual
        else:
            # Mesma direção ainda pressionada, verificar se deve acelerar
            tempo_segurando = tempo_atual - _tempo_inicio_hold.get(chave_hold, tempo_atual)
            if tempo_segurando >= tempo_hold_inicial:
                # Ativar modo "hold" - usar debounce mais rápido
                debounce_tempo = debounce_hold
    else:
        # Nenhuma direção pressionada, resetar hold
        if chave_hold in _direcao_hold:
            del _direcao_hold[chave_hold]
        if chave_hold in _tempo_inicio_hold:
            del _tempo_inicio_hold[chave_hold]
    
    if chave_debounce in _ultimo_tempo_navegacao:
        tempo_decorrido = tempo_atual - _ultimo_tempo_navegacao[chave_debounce]
        if tempo_decorrido < debounce_tempo:
            # Ainda em período de debounce, ignorar movimento do stick
            if ev.type == pygame.JOYAXISMOTION:
                return None
    
    if ev.type == pygame.JOYAXISMOTION:
        if ev.joy == joystick_id:
            # Eixo 1 = stick esquerdo vertical (cima/baixo)
            # Eixo 0 = stick esquerdo horizontal (esquerda/direita)
            
            # Deadzone maior para evitar movimento acidental
            deadzone = 0.7
            
            chave_axis = f"{joystick_id}_{ev.axis}"
            valor_anterior = _ultimo_valor_axis.get(chave_axis, 0.0)
            
            if ev.axis == 1:  # Stick esquerdo vertical (cima/baixo)
                valor_atual = ev.value
                # Deadzone maior e verificação mais rigorosa
                # Só processar quando o analógico ENTRA na deadzone (mudou de direção)
                if abs(valor_atual) > deadzone:
                    # Verificar se mudou de direção
                    mudou_direcao = False
                    if valor_anterior <= deadzone and valor_atual > deadzone:
                        # Saiu da deadzone para baixo
                        mudou_direcao = True
                    elif valor_anterior >= -deadzone and valor_atual < -deadzone:
                        # Saiu da deadzone para cima
                        mudou_direcao = True
                    elif (valor_anterior < 0 and valor_atual > 0) or (valor_anterior > 0 and valor_atual < 0):
                        # Mudou de lado (cima para baixo ou vice-versa)
                        mudou_direcao = True
                    
                    if mudou_direcao:
                        # Verificar debounce antes de processar
                        if chave_debounce not in _ultimo_tempo_navegacao or \
                           tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                            _ultimo_valor_axis[chave_axis] = valor_atual
                            _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                            if valor_atual < -deadzone:
                                # Cima: navegar entre opções
                                if num_opcoes > 0:
                                    return {"acao": "cima", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "analogico"}
                                else:
                                    return {"acao": "cima", "fonte": "analogico"}
                            elif valor_atual > deadzone:
                                # Baixo: navegar entre opções
                                if num_opcoes > 0:
                                    return {"acao": "baixo", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "analogico"}
                                else:
                                    return {"acao": "baixo", "fonte": "analogico"}
                    else:
                        # Atualizar valor mas não processar (ainda na mesma direção)
                        _ultimo_valor_axis[chave_axis] = valor_atual
                else:
                    # Voltou para dentro da deadzone - resetar para permitir novo movimento
                    if abs(valor_anterior) > deadzone:
                        # Acabou de sair da deadzone, resetar
                        _ultimo_valor_axis[chave_axis] = 0.0
                    else:
                        _ultimo_valor_axis[chave_axis] = valor_atual
            
            elif ev.axis == 0:  # Stick esquerdo horizontal
                valor_atual = ev.value
                # Deadzone maior e verificação mais rigorosa
                # Só processar quando o analógico ENTRA na deadzone (mudou de direção)
                # Isso cria um comportamento "por clique" - uma ação por movimento do analógico
                if abs(valor_atual) > deadzone:
                    # Verificar se mudou de direção (saiu da deadzone ou mudou de lado)
                    mudou_direcao = False
                    if valor_anterior <= deadzone and valor_atual > deadzone:
                        # Saiu da deadzone para direita
                        mudou_direcao = True
                    elif valor_anterior >= -deadzone and valor_atual < -deadzone:
                        # Saiu da deadzone para esquerda
                        mudou_direcao = True
                    elif (valor_anterior < 0 and valor_atual > 0) or (valor_anterior > 0 and valor_atual < 0):
                        # Mudou de lado (esquerda para direita ou vice-versa)
                        mudou_direcao = True
                    
                    if mudou_direcao:
                        # Verificar debounce antes de processar
                        if chave_debounce not in _ultimo_tempo_navegacao or \
                           tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                            _ultimo_valor_axis[chave_axis] = valor_atual
                            _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                            if valor_atual < -deadzone:
                                # Esquerda/Direita: navegar entre seções (não precisa de opção)
                                return {"acao": "esquerda", "fonte": "analogico"}
                            elif valor_atual > deadzone:
                                # Esquerda/Direita: navegar entre seções (não precisa de opção)
                                return {"acao": "direita", "fonte": "analogico"}
                    else:
                        # Atualizar valor mas não processar (ainda na mesma direção)
                        _ultimo_valor_axis[chave_axis] = valor_atual
                else:
                    # Voltou para dentro da deadzone - resetar para permitir novo movimento
                    if abs(valor_anterior) > deadzone:
                        # Acabou de sair da deadzone, resetar
                        _ultimo_valor_axis[chave_axis] = 0.0
                    else:
                        _ultimo_valor_axis[chave_axis] = valor_atual
    
    elif ev.type == pygame.JOYHATMOTION:
        if ev.joy == joystick_id:
            # D-pad
            # ev.value é uma tupla (x, y) para o hat
            hat_x, hat_y = ev.value
            # D-pad só retorna evento quando muda, então não precisa de debounce adicional
            if hat_y == 1:  # Cima
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    # Cima/Baixo: navegar entre opções dentro da seção
                    if num_opcoes > 0:
                        return {"acao": "cima", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "cima", "fonte": "dpad"}
            elif hat_y == -1:  # Baixo
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    # Cima/Baixo: navegar entre opções dentro da seção
                    if num_opcoes > 0:
                        return {"acao": "baixo", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "baixo", "fonte": "dpad"}
            elif hat_x == -1:  # Esquerda
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    # Esquerda/Direita: navegar horizontalmente se houver opções, senão apenas ação
                    if num_opcoes > 0:
                        return {"acao": "esquerda", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "esquerda", "fonte": "dpad"}
            elif hat_x == 1:  # Direita
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    # Esquerda/Direita: navegar horizontalmente se houver opções, senão apenas ação
                    if num_opcoes > 0:
                        return {"acao": "direita", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "direita", "fonte": "dpad"}
    
    elif ev.type == pygame.JOYBUTTONDOWN:
        if ev.joy == joystick_id:
            # Detectar tipo de controle para mapeamento correto
            from core.gamepad_manager import gerenciador_gamepad
            tipo_controle = "generic"
            if joystick_id < len(gerenciador_gamepad.joysticks):
                tipo_controle = gerenciador_gamepad._detectar_tipo_controle(joystick_id)
            
            # Mapeamento de botões baseado no tipo de controle
            # PS5/PS4: Botão 0 = X (Cross), Botão 1 = Círculo, Botão 2 = Quadrado, Botão 3 = Triângulo
            # Xbox: Botão 0 = A, Botão 1 = B, Botão 2 = X, Botão 3 = Y
            # Botão 0 (X/A) = Confirmar
            # Botão 1 (Círculo/B) = Cancelar/Voltar
            
            # PS5/PS4 D-pad como botões (quando não há hats):
            # Botão 11 = D-pad Up
            # Botão 12 = D-pad Down
            # Botão 13 = D-pad Left
            # Botão 14 = D-pad Right
            
            # Xbox D-pad geralmente usa hats, mas alguns drivers podem usar botões
            
            if ev.button == 0:  # X (PS5/PS4) / A (Xbox) - Confirmar
                return {"acao": "confirmar"}
            elif ev.button == 1:  # Círculo (PS5/PS4) / B (Xbox) - Cancelar/Voltar
                return {"acao": "cancelar"}
            elif ev.button == 2:  # Quadrado (PS5/PS4) / X (Xbox) - Alternativa
                return {"acao": "alternativa"}
            # L1/LB para troca de carros na oficina
            # PS5/PS4: L1 = botão 4
            # Xbox: LB = botão 4
            elif ev.button == 4:  # L1/LB (PS5/PS4/Xbox) - Carro anterior (na oficina)
                # Usar chave de debounce específica para L1/R1 para não interferir com outras ações
                chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                # Verificar debounce antes de processar
                if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                    return {"acao": "carro_anterior", "fonte": "botao"}
            elif ev.button == 5:  # R1 (PS5/PS4/Xbox) - Próximo carro (na oficina)
                # Usar chave de debounce específica para L1/R1 para não interferir com outras ações
                chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                # Verificar debounce antes de processar
                if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                    return {"acao": "carro_proximo", "fonte": "botao"}
            elif ev.button == 9:  # L1 (fallback) ou Options (PS5/PS4) - Verificar qual é
                # Verificar se é Options ou L1 baseado no número de botões e tipo de controle
                from core.gamepad_manager import gerenciador_gamepad
                if joystick_id < len(gerenciador_gamepad.joysticks):
                    joystick = gerenciador_gamepad.joysticks[joystick_id]
                    nome_controle = joystick.get_name().lower()
                    # PS5/PS4: botão 9 é Options (pausar), não L1
                    if "ps5" in nome_controle or "ps4" in nome_controle or "playstation" in nome_controle or "dualsense" in nome_controle or "dualshock" in nome_controle:
                        return {"acao": "pausar"}
                    # Para outros controles, pode ser L1
                    chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                    if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                       tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                        _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                        return {"acao": "carro_anterior", "fonte": "botao"}
                else:
                    # Fallback: tratar como L1
                    chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                    if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                       tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                        _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                        return {"acao": "carro_anterior", "fonte": "botao"}
            elif ev.button == 10:  # R1 (fallback para alguns controles) - Próximo carro
                chave_debounce_l1r1 = f"{joystick_id}_l1r1"
                if chave_debounce_l1r1 not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce_l1r1, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce_l1r1] = tempo_atual
                    return {"acao": "carro_proximo", "fonte": "botao"}
            elif ev.button == 11:  # PS4 D-pad Up
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    return {"acao": "cima", "opcao": (opcao_atual - 1) % num_opcoes if num_opcoes > 0 else 0, "fonte": "dpad"}
            elif ev.button == 12:  # PS4 D-pad Down
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    return {"acao": "baixo", "opcao": (opcao_atual + 1) % num_opcoes if num_opcoes > 0 else 0, "fonte": "dpad"}
            elif ev.button == 13:  # PS4 D-pad Left
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    # Esquerda/Direita: navegar horizontalmente se houver opções, senão apenas ação
                    if num_opcoes > 0:
                        return {"acao": "esquerda", "opcao": (opcao_atual - 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "esquerda", "fonte": "dpad"}
            elif ev.button == 14:  # PS4 D-pad Right
                # Verificar debounce antes de processar
                if chave_debounce not in _ultimo_tempo_navegacao or \
                   tempo_atual - _ultimo_tempo_navegacao.get(chave_debounce, 0) >= debounce_tempo:
                    _ultimo_tempo_navegacao[chave_debounce] = tempo_atual
                    # Esquerda/Direita: navegar horizontalmente se houver opções, senão apenas ação
                    if num_opcoes > 0:
                        return {"acao": "direita", "opcao": (opcao_atual + 1) % num_opcoes, "fonte": "dpad"}
                    else:
                        return {"acao": "direita", "fonte": "dpad"}
            # Botões de menu/pausa
            elif ev.button == 6:  # Share (PS5) / Back (Xbox) - Pausar
                # Xbox: botão 6 = Back (View button)
                if tipo_controle == "xbox":
                    return {"acao": "pausar"}
                # PS5: botão 6 = Share (pausar)
                elif tipo_controle in ["ps5", "ps4"]:
                    return {"acao": "pausar"}
                # Fallback genérico
                else:
                    return {"acao": "pausar"}
            elif ev.button == 7:  # Options (PS5) / Start (Xbox) - Pausar
                # Xbox: botão 7 = Start
                if tipo_controle == "xbox":
                    return {"acao": "pausar"}
                # PS5: pode ser Options em alguns drivers
                elif tipo_controle in ["ps5", "ps4"]:
                    return {"acao": "pausar"}
            elif ev.button == 8:  # PS5 Options button (alguns drivers) - Pausar
                if tipo_controle in ["ps5", "ps4"]:
                    return {"acao": "pausar"}
            # Botão 9 já foi tratado acima (pode ser Options para PS5/PS4 ou L1 para outros)
    
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
    
    # Verificar estado atual do D-pad
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
    
    # Se há uma direção pressionada e está em modo "hold"
    if direcao_atual:
        if chave_hold in _direcao_hold and _direcao_hold[chave_hold] == direcao_atual:
            # Mesma direção ainda pressionada, verificar se deve processar navegação
            tempo_segurando = tempo_atual - _tempo_inicio_hold.get(chave_hold, tempo_atual)
            tempo_hold_inicial = 500  # Tempo antes de ativar modo "hold"
            debounce_hold = 50  # Debounce quando em modo "hold"
            
            if tempo_segurando >= tempo_hold_inicial:
                # Verificar debounce
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
        
        # Verificar D-pad
        # PS4/PS5 pode reportar D-pad como hat OU como botões
        if joystick.get_numhats() > 0:
            # D-pad como hat (Xbox, alguns controles)
            hat = joystick.get_hat(0)
            hat_x, hat_y = hat
            chave_dpad = f"{joystick_id}_dpad"
            estado_anterior = _ultimo_estado_dpad.get(chave_dpad, (0, 0))
            
            # Só retornar True se o hat mudou de estado (comportamento "por clique")
            # Isso cria comportamento "por clique" - uma ação por mudança de estado
            hat_anterior_x, hat_anterior_y = estado_anterior
            
            if hat_y == 1 and hat_anterior_y != 1:
                estado["cima"] = True
            elif hat_y == -1 and hat_anterior_y != -1:
                estado["baixo"] = True
            if hat_x == -1 and hat_anterior_x != -1:
                estado["esquerda"] = True
            elif hat_x == 1 and hat_anterior_x != 1:
                estado["direita"] = True
            
            # Debug para verificar se o hat está sendo detectado
            if (hat_x != 0 or hat_y != 0) and (hat_x != hat_anterior_x or hat_y != hat_anterior_y):
                print(f"DEBUG HAT: hat_x={hat_x}, hat_y={hat_y}, anterior=({hat_anterior_x}, {hat_anterior_y})")
            
            _ultimo_estado_dpad[chave_dpad] = (hat_x, hat_y)
        else:
            # PS4/PS5 D-pad como botões (quando não há hats)
            # Verificar se os botões do D-pad estão pressionados
            if joystick.get_numbuttons() > 14:
                # Botão 11 = D-pad Up
                # Botão 12 = D-pad Down
                # Botão 13 = D-pad Left
                # Botão 14 = D-pad Right
                chave_dpad = f"{joystick_id}_dpad_buttons"
                estado_anterior = _ultimo_estado_dpad.get(chave_dpad, (False, False, False, False))
                
                dpad_up = joystick.get_button(11) if joystick.get_numbuttons() > 11 else False
                dpad_down = joystick.get_button(12) if joystick.get_numbuttons() > 12 else False
                dpad_left = joystick.get_button(13) if joystick.get_numbuttons() > 13 else False
                dpad_right = joystick.get_button(14) if joystick.get_numbuttons() > 14 else False
                
                # Só retornar True se o botão foi pressionado (mudou de False para True)
                # Isso cria comportamento "por clique" - uma ação por pressionamento
                if dpad_up and not estado_anterior[0]:
                    estado["cima"] = True
                if dpad_down and not estado_anterior[1]:
                    estado["baixo"] = True
                if dpad_left and not estado_anterior[2]:
                    estado["esquerda"] = True
                if dpad_right and not estado_anterior[3]:
                    estado["direita"] = True
                
                _ultimo_estado_dpad[chave_dpad] = (dpad_up, dpad_down, dpad_left, dpad_right)
        
        # NÃO verificar stick esquerdo aqui - isso é feito via eventos JOYAXISMOTION
        # A verificação contínua do D-pad não deve incluir o analógico
        
        # Verificar botões (só quando pressionados, não continuamente)
        # Os botões são tratados via eventos JOYBUTTONDOWN, não aqui
    
    return estado

