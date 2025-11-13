import os

DIR_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_LAPS = os.path.join(DIR_PROJETO, "data", "laps")
DIR_DATA = os.path.join(DIR_PROJETO, "data")

def carregar_checkpoints_grip(numero_pista):
    centro_x, centro_y = 2500, 2500
    
    if numero_pista == 1:
        checkpoint_1 = (centro_x + -244, centro_y + 42, 90)
        checkpoint_2 = (centro_x + -1257, centro_y + 2, 105)
        checkpoint_3 = (centro_x + -1577, centro_y + -544, 0)
        checkpoint_4 = (centro_x + -1257, centro_y + -1014, 60)
        checkpoint_5 = (centro_x + -564, centro_y + -1018, 120)
        checkpoint_6 = (centro_x + -297, centro_y + -471, 120)
        checkpoint_7 = (centro_x + 282, centro_y + -484, 60)
        checkpoint_8 = (centro_x + 551, centro_y + -853, 45)
        checkpoint_9 = (centro_x + 1109, centro_y + -784, 135)
        checkpoint_10 = (centro_x + 1323, centro_y + -224, 150)
        checkpoint_11 = (centro_x + 1730, centro_y + -38, 150)
        checkpoint_12 = (centro_x + 1677, centro_y + 1037, 30)
        checkpoint_13 = (centro_x + 1179, centro_y + 1275, 75)
        checkpoint_14 = (centro_x + -594, centro_y + 1265, 90)
        checkpoint_15 = (centro_x + -981, centro_y + 879, 0)
        checkpoint_16 = (centro_x + -698, centro_y + 561, 45)
        checkpoint_17 = (centro_x + 756, centro_y + 532, 45)
        checkpoint_18 = (centro_x + 744, centro_y + 100, 315)
        checkpoint_19 = (centro_x + -18, centro_y + 52, 90)
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
    elif numero_pista == 2:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 400, centro_y + 1250)
        section2 = (centro_x + 100, centro_y - 1150)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 3:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 900, centro_y + 1750)
        section2 = (centro_x - 600, centro_y + 1050)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 4:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 3150, centro_y + 600)
        section2 = (centro_x + 850, centro_y + 900)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 5:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 1500, centro_y + 1150)
        section2 = (centro_x - 500, centro_y + 2150)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 6:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 700, centro_y + 2750)
        section2 = (centro_x - 1000, centro_y + 950)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 7:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 400, centro_y + 1350)
        section2 = (centro_x + 700, centro_y - 450)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 8:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 950, centro_y + 700)
        section2 = (centro_x + 1700, centro_y + 1950)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 9:
        finish_line = (centro_x + 50, centro_y + 50)
        section1 = (centro_x + 1550, centro_y + 200)
        section2 = (centro_x + 1450, centro_y + 2600)
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    else:
        checkpoints = [(centro_x + 50, centro_y - 100)]
    
    print(f"Carregados {len(checkpoints)} checkpoints do GRIP para pista {numero_pista}")
    return checkpoints

def carregar_spawn_points(numero_pista):
    try:
        import json
        
        diretorio = os.path.join(DIR_PROJETO, "data")
        arquivo = os.path.join(diretorio, f"checkpoints_pista_{numero_pista}.json")
        
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            if isinstance(dados, dict):
                spawn_points = dados.get("spawn_points", [])
                if spawn_points:
                    return [(float(sp[0]), float(sp[1])) for sp in spawn_points if len(sp) >= 2]
        
        return None
    except Exception as e:
        print(f"Erro ao carregar spawn points: {e}")
        import traceback
        traceback.print_exc()
        return None


