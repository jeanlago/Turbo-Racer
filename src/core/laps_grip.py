import os
import math
from config import DIR_PROJETO

DIR_LAPS = os.path.join(DIR_PROJETO, "data", "laps")
DIR_DATA = os.path.join(DIR_PROJETO, "data")

def ajustar_checkpoint_centro_pista(x, y, angulo, superficie_pista=None):
    """
    Ajusta um checkpoint para ficar no centro da pista.
    
    Args:
        x: Coordenada X do checkpoint
        y: Coordenada Y do checkpoint
        angulo: Ângulo do checkpoint em graus (opcional)
        superficie_pista: Superfície renderizada da pista (opcional)
    
    Returns:
        Tupla (x, y) com as coordenadas ajustadas ao centro da pista
    """
    if superficie_pista is None:
        return x, y
    
    try:
        from core.pista_grip import eh_pixel_grama_grip
    except:
        return x, y
    
    ponto_pista_x, ponto_pista_y = x, y
    esta_na_pista = False
    
    if 0 <= int(x) < superficie_pista.get_width() and 0 <= int(y) < superficie_pista.get_height():
        esta_na_pista = not eh_pixel_grama_grip(superficie_pista, int(x), int(y))
    
    if not esta_na_pista:
        melhor_dist = float('inf')
        for angulo_busca in range(0, 360, 10):
            rad_busca = math.radians(angulo_busca)
            for dist in range(5, 400, 5):
                test_x = int(x + dist * math.cos(rad_busca))
                test_y = int(y + dist * math.sin(rad_busca))
                
                if 0 <= test_x < superficie_pista.get_width() and 0 <= test_y < superficie_pista.get_height():
                    if not eh_pixel_grama_grip(superficie_pista, test_x, test_y):
                        if dist < melhor_dist:
                            melhor_dist = dist
                            ponto_pista_x = test_x
                            ponto_pista_y = test_y
                            break
            if melhor_dist < 50:
                break
    
    if angulo is not None:
        rad = math.radians(angulo)
        perp_rad = rad + math.pi / 2
    else:
        melhor_centro_x, melhor_centro_y = ponto_pista_x, ponto_pista_y
        melhor_largura = 0
        
        for angulo_teste in range(0, 180, 15):
            rad_teste = math.radians(angulo_teste)
            perp_rad = rad_teste + math.pi / 2
            
            pontos_pista = []
            for offset in range(-300, 301, 2):
                test_x = int(ponto_pista_x + offset * math.cos(perp_rad))
                test_y = int(ponto_pista_y + offset * math.sin(perp_rad))
                
                if 0 <= test_x < superficie_pista.get_width() and 0 <= test_y < superficie_pista.get_height():
                    if not eh_pixel_grama_grip(superficie_pista, test_x, test_y):
                        pontos_pista.append(offset)
            
            if len(pontos_pista) > 20:
                pontos_pista.sort()
                largura = pontos_pista[-1] - pontos_pista[0]
                if largura > melhor_largura:
                    melhor_largura = largura
                    centro_offset = (pontos_pista[0] + pontos_pista[-1]) / 2
                    melhor_centro_x = ponto_pista_x + centro_offset * math.cos(perp_rad)
                    melhor_centro_y = ponto_pista_y + centro_offset * math.sin(perp_rad)
        
        if melhor_largura > 20:
            return melhor_centro_x, melhor_centro_y
        else:
            perp_rad = math.pi / 2
    
    pontos_pista = []
    for offset in range(-300, 301, 2):
        test_x = int(ponto_pista_x + offset * math.cos(perp_rad))
        test_y = int(ponto_pista_y + offset * math.sin(perp_rad))
        
        if 0 <= test_x < superficie_pista.get_width() and 0 <= test_y < superficie_pista.get_height():
            if not eh_pixel_grama_grip(superficie_pista, test_x, test_y):
                pontos_pista.append(offset)
    
    if len(pontos_pista) > 20:
        pontos_pista.sort()
        centro_offset = (pontos_pista[0] + pontos_pista[-1]) / 2
        centro_x = ponto_pista_x + centro_offset * math.cos(perp_rad)
        centro_y = ponto_pista_y + centro_offset * math.sin(perp_rad)
        return centro_x, centro_y
    
    return ponto_pista_x, ponto_pista_y

def carregar_checkpoints_grip(numero_pista, superficie_pista=None):
    """
    Carrega checkpoints do JSON ou do código hardcoded.
    Ajusta automaticamente os checkpoints ao centro da pista se superficie_pista for fornecida.
    
    Args:
        numero_pista: Número da pista (1-9)
        superficie_pista: Superfície renderizada da pista (opcional)
    
    Returns:
        Lista de tuplas (x, y, angulo) ou (x, y, 0) representando os checkpoints
    """
    centro_x, centro_y = 2500, 2500
    
    try:
        import json
        arquivo = os.path.join(DIR_DATA, f"checkpoints_pista_{numero_pista}.json")
        
        print(f"[CHECKPOINTS] Tentando carregar checkpoints da pista {numero_pista} de: {arquivo}")
        print(f"[CHECKPOINTS] Arquivo existe? {os.path.exists(arquivo)}")
        
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            checkpoints_json = dados.get("checkpoints", []) if isinstance(dados, dict) else dados
            
            if checkpoints_json:
                checkpoints = []
                for cp in checkpoints_json:
                    if len(cp) >= 3:
                        checkpoints.append((float(cp[0]), float(cp[1]), float(cp[2])))
                    elif len(cp) >= 2:
                        checkpoints.append((float(cp[0]), float(cp[1]), 0))
                
                if checkpoints:
                    print(f"[CHECKPOINTS] Carregados {len(checkpoints)} checkpoints do JSON para pista {numero_pista}")
                    return checkpoints
                else:
                    print(f"[CHECKPOINTS] Arquivo JSON existe mas não contém checkpoints válidos")
            else:
                print(f"[CHECKPOINTS] Arquivo JSON existe mas checkpoints_json está vazio")
        else:
            print(f"[CHECKPOINTS] Arquivo JSON não encontrado, usando checkpoints hardcoded")
    except Exception as e:
        print(f"[CHECKPOINTS] Erro ao carregar checkpoints do JSON: {e}")
        import traceback
        traceback.print_exc()
    
    if numero_pista == 1:
        checkpoint_1 = (centro_x + -244, centro_y + 42, 90)  # Ângulo: 90°
        checkpoint_2 = (centro_x + -1257, centro_y + 2, 105)  # Ângulo: 105°
        checkpoint_3 = (centro_x + -1577, centro_y + -544, 0)  # Ângulo: 0°
        checkpoint_4 = (centro_x + -1257, centro_y + -1014, 60)  # Ângulo: 60°
        checkpoint_5 = (centro_x + -564, centro_y + -1018, 120)  # Ângulo: 120°
        checkpoint_6 = (centro_x + -297, centro_y + -471, 120)  # Ângulo: 120°
        checkpoint_7 = (centro_x + 282, centro_y + -484, 60)  # Ângulo: 60°
        checkpoint_8 = (centro_x + 551, centro_y + -853, 45)  # Ângulo: 45°
        checkpoint_9 = (centro_x + 1109, centro_y + -784, 135)  # Ângulo: 135°
        checkpoint_10 = (centro_x + 1323, centro_y + -224, 150)  # Ângulo: 150°
        checkpoint_11 = (centro_x + 1730, centro_y + -38, 150)  # Ângulo: 150°
        checkpoint_12 = (centro_x + 1583, centro_y + 1073, 30)  # Ângulo: 30°
        checkpoint_13 = (centro_x + 1069, centro_y + 1246, 75)  # Ângulo: 75°
        checkpoint_14 = (centro_x + -754, centro_y + 1208, 120)  # Ângulo: 120°
        checkpoint_15 = (centro_x + -952, centro_y + 912, 0)  # Ângulo: 0°
        checkpoint_16 = (centro_x + -698, centro_y + 582, 45)  # Ângulo: 45°
        checkpoint_17 = (centro_x + 756, centro_y + 532, 45)  # Ângulo: 45°
        checkpoint_18 = (centro_x + 744, centro_y + 100, 315)  # Ângulo: 315°
        checkpoint_19 = (centro_x + -243, centro_y + 37, 90)  # Ângulo: 90°
        # Checkpoints com ângulo: (x, y, angulo) ou (x, y) para cálculo automático
        checkpoints = [
            tuple(checkpoint_1),
            tuple(checkpoint_2),
            tuple(checkpoint_3),
            tuple(checkpoint_4),
            tuple(checkpoint_5),
            tuple(checkpoint_6),
            tuple(checkpoint_7),
            tuple(checkpoint_8),
            tuple(checkpoint_9),
            tuple(checkpoint_10),
            tuple(checkpoint_11),
            tuple(checkpoint_12),
            tuple(checkpoint_13),
            tuple(checkpoint_14),
            tuple(checkpoint_15),
            tuple(checkpoint_16),
            tuple(checkpoint_17),
            tuple(checkpoint_18),
            tuple(checkpoint_19),
        ]
    else:
        checkpoints = [(centro_x + 50, centro_y - 100)]
    
    if superficie_pista is not None:
        checkpoints_ajustados = []
        for i, cp in enumerate(checkpoints):
            if len(cp) >= 3:
                x, y, angulo = cp[0], cp[1], cp[2]
            else:
                x, y = cp[0], cp[1]
                angulo = None
            
            novo_x, novo_y = ajustar_checkpoint_centro_pista(x, y, angulo, superficie_pista)
            
            try:
                from core.pista_grip import eh_pixel_grama_grip
                if 0 <= int(novo_x) < superficie_pista.get_width() and 0 <= int(novo_y) < superficie_pista.get_height():
                    if eh_pixel_grama_grip(superficie_pista, int(novo_x), int(novo_y)):
                        for angulo_busca in range(0, 360, 5):
                            rad_busca = math.radians(angulo_busca)
                            for dist in range(10, 500, 5):
                                test_x = int(x + dist * math.cos(rad_busca))
                                test_y = int(y + dist * math.sin(rad_busca))
                                
                                if 0 <= test_x < superficie_pista.get_width() and 0 <= test_y < superficie_pista.get_height():
                                    if not eh_pixel_grama_grip(superficie_pista, test_x, test_y):
                                        pontos_pista = []
                                        for search_dist in range(-400, 401, 3):
                                            search_x = int(test_x + search_dist * math.cos(rad_busca + math.pi/2))
                                            search_y = int(test_y + search_dist * math.sin(rad_busca + math.pi/2))
                                            if 0 <= search_x < superficie_pista.get_width() and 0 <= search_y < superficie_pista.get_height():
                                                if not eh_pixel_grama_grip(superficie_pista, search_x, search_y):
                                                    pontos_pista.append(search_dist)
                                        
                                        if len(pontos_pista) > 30:
                                            pontos_pista.sort()
                                            centro_offset = (pontos_pista[0] + pontos_pista[-1]) / 2
                                            centro_x = test_x + centro_offset * math.cos(rad_busca + math.pi/2)
                                            centro_y = test_y + centro_offset * math.sin(rad_busca + math.pi/2)
                                            if 0 <= int(centro_x) < superficie_pista.get_width() and 0 <= int(centro_y) < superficie_pista.get_height():
                                                if not eh_pixel_grama_grip(superficie_pista, int(centro_x), int(centro_y)):
                                                    novo_x, novo_y = centro_x, centro_y
                                                    break
                                        if len(pontos_pista) > 30:
                                            break
                                if len(pontos_pista) > 30:
                                    break
                            if len(pontos_pista) > 30:
                                break
            except:
                pass
            
            if len(cp) >= 3:
                checkpoints_ajustados.append((float(novo_x), float(novo_y), float(angulo)))
            else:
                checkpoints_ajustados.append((float(novo_x), float(novo_y), 0))
        
        return checkpoints_ajustados
    
    return checkpoints

def carregar_spawn_points(numero_pista):
    """
    Carrega spawn points do arquivo JSON da pista.
    
    Args:
        numero_pista: Número da pista (1-9)
    
    Returns:
        Lista de tuplas (x, y) com os spawn points ou None se não encontrado
    """
    try:
        import json
        arquivo = os.path.join(DIR_DATA, f"checkpoints_pista_{numero_pista}.json")
        
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            if isinstance(dados, dict):
                spawn_points = dados.get("spawn_points", [])
                if spawn_points:
                    return [(float(sp[0]), float(sp[1])) for sp in spawn_points if len(sp) >= 2]
        
        return None
    except Exception:
        return None


