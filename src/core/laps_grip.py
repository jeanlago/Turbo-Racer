# src/core/laps_grip.py
"""
Sistema de carregamento de checkpoints e tempos de volta do GRIP
"""
import os

# Caminho para os arquivos de laps
DIR_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_LAPS = os.path.join(DIR_PROJETO, "data", "laps")
DIR_DATA = os.path.join(DIR_PROJETO, "data")

def carregar_checkpoints_grip(numero_pista):
    """
    Carrega checkpoints baseados nas linhas de chegada do GRIP
    No GRIP, há 3 linhas: finishLine, section1, section2
    Retorna lista de checkpoints [(x, y, angulo), ...] ou [(x, y), ...]
    Se o checkpoint tiver 3 elementos, o terceiro é o ângulo em graus.
    Se tiver 2 elementos, o ângulo será calculado automaticamente.
    """
    # No GRIP, as linhas de chegada são definidas assim:
    # finishLine = (position[0]+50, position[1]-100)
    # section1 = (position[0], position[1]+1100) para pista 1
    # section2 = (position[0]-700, position[1]-1200) para pista 1
    
    # Posição inicial do GRIP é aproximadamente (650, 250)
    # No nosso sistema, o centro é (2500, 2500)
    # Então position[0] = 650, position[1] = 250 no GRIP
    # No nosso sistema, isso seria aproximadamente (0, -100) relativo ao centro
    
    centro_x, centro_y = 2500, 2500
    
    # Definir checkpoints baseados na pista (baseado no GRIP)
    # No GRIP, position[0] e position[1] são relativos ao centro da tela
    # No nosso sistema, o centro é (2500, 2500)
    
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
        checkpoint_12 = (centro_x + 1677, centro_y + 1037, 30)  # Ângulo: 30°
        checkpoint_13 = (centro_x + 1179, centro_y + 1275, 75)  # Ângulo: 75°
        checkpoint_14 = (centro_x + -594, centro_y + 1265, 90)  # Ângulo: 90°
        checkpoint_15 = (centro_x + -981, centro_y + 879, 0)  # Ângulo: 0°
        checkpoint_16 = (centro_x + -698, centro_y + 561, 45)  # Ângulo: 45°
        checkpoint_17 = (centro_x + 756, centro_y + 532, 45)  # Ângulo: 45°
        checkpoint_18 = (centro_x + 744, centro_y + 100, 315)  # Ângulo: 315°
        checkpoint_19 = (centro_x + -18, centro_y + 52, 90)  # Ângulo: 90°
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
    elif numero_pista == 2:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+400, position[1]+1100) - linha vertical de 300px
        section1 = (centro_x + 400, centro_y + 1250)
        # section2: (position[0]+100, position[1]-1300) - linha vertical de 300px
        section2 = (centro_x + 100, centro_y - 1150)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 3:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+900, position[1]+1600) - linha vertical de 300px
        section1 = (centro_x + 900, centro_y + 1750)
        # section2: (position[0]-600, position[1]+900) - linha vertical de 300px
        section2 = (centro_x - 600, centro_y + 1050)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 4:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+3000, position[1]+600) - linha horizontal de 300px
        # O centro da linha está em position[0]+3000 + 150 = position[0]+3150
        section1 = (centro_x + 3150, centro_y + 600)
        # section2: (position[0]+700, position[1]+900) - linha horizontal de 300px
        # O centro da linha está em position[0]+700 + 150 = position[0]+850
        section2 = (centro_x + 850, centro_y + 900)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 5:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+1500, position[1]+1000) - linha vertical de 300px
        section1 = (centro_x + 1500, centro_y + 1150)
        # section2: (position[0]-500, position[1]+2000) - linha vertical de 300px
        section2 = (centro_x - 500, centro_y + 2150)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 6:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+700, position[1]+2600) - linha vertical de 300px
        section1 = (centro_x + 700, centro_y + 2750)
        # section2: (position[0]-1000, position[1]+800) - linha vertical de 300px
        section2 = (centro_x - 1000, centro_y + 950)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 7:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+400, position[1]+1200) - linha vertical de 300px
        section1 = (centro_x + 400, centro_y + 1350)
        # section2: (position[0]+700, position[1]-600) - linha vertical de 300px
        section2 = (centro_x + 700, centro_y - 450)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 8:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+800, position[1]+700) - linha horizontal de 300px
        # O centro da linha está em position[0]+800 + 150 = position[0]+950
        section1 = (centro_x + 950, centro_y + 700)
        # section2: (position[0]+1700, position[1]+1800) - linha vertical de 300px
        section2 = (centro_x + 1700, centro_y + 1950)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    elif numero_pista == 9:
        # finishLine: (position[0]+50, position[1]-100) - linha vertical de 300px
        finish_line = (centro_x + 50, centro_y + 50)
        # section1: (position[0]+1400, position[1]+200) - linha horizontal de 300px
        # O centro da linha está em position[0]+1400 + 150 = position[0]+1550
        section1 = (centro_x + 1550, centro_y + 200)
        # section2: (position[0]+1300, position[1]+2600) - linha horizontal de 300px
        # O centro da linha está em position[0]+1300 + 150 = position[0]+1450
        section2 = (centro_x + 1450, centro_y + 2600)
        # Garantir que checkpoints sejam tuplas (x, y) para compatibilidade
        checkpoints = [tuple(finish_line), tuple(section1), tuple(section2)]
    else:
        # Para outras pistas, usar checkpoints padrão
        checkpoints = [(centro_x + 50, centro_y - 100)]
    
    print(f"Carregados {len(checkpoints)} checkpoints do GRIP para pista {numero_pista}")
    return checkpoints

def carregar_spawn_points(numero_pista):
    """
    Carrega spawn points (posições de spawn dos carros) do arquivo JSON específico da pista
    Retorna lista de spawn points [(x, y), ...] ou None se não houver
    """
    try:
        import json
        
        # Carregar do arquivo JSON específico da pista (mesmo sistema do editor)
        diretorio = os.path.join(DIR_PROJETO, "data")
        arquivo = os.path.join(diretorio, f"checkpoints_pista_{numero_pista}.json")
        
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Verificar se é formato novo (com spawn_points) ou antigo (só checkpoints)
            if isinstance(dados, dict):
                spawn_points = dados.get("spawn_points", [])
                if spawn_points:
                    # Converter para tuplas
                    return [(float(sp[0]), float(sp[1])) for sp in spawn_points if len(sp) >= 2]
        
        return None
    except Exception as e:
        print(f"Erro ao carregar spawn points: {e}")
        import traceback
        traceback.print_exc()
        return None

def carregar_tempos_recorde_grip(numero_pista):
    """
    Carrega os tempos de recorde do arquivo de laps do GRIP
    Retorna lista de tempos: [(tempo_total, tempo_secao1, tempo_secao2, tempo_secao3), ...]
    """
    nome_arquivo = f"laps{numero_pista}.txt"
    caminho_arquivo = os.path.join(DIR_LAPS, nome_arquivo)
    
    tempos = []
    
    if not os.path.exists(caminho_arquivo):
        print(f"AVISO: Arquivo de laps não encontrado: {caminho_arquivo}")
        return tempos
    
    try:
        with open(caminho_arquivo, 'r') as f:
            linhas = f.readlines()
            
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            # Formato do GRIP: "x y tempo1 tempo2 tempo3"
            partes = linha.split()
            if len(partes) >= 5:
                try:
                    tempo_total = float(partes[0])  # Primeiro valor pode ser tempo total
                    tempo_secao1 = float(partes[2]) if len(partes) > 2 else 0.0
                    tempo_secao2 = float(partes[3]) if len(partes) > 3 else 0.0
                    tempo_secao3 = float(partes[4]) if len(partes) > 4 else 0.0
                    tempos.append((tempo_total, tempo_secao1, tempo_secao2, tempo_secao3))
                except ValueError:
                    continue
        
        return tempos
        
    except Exception as e:
        print(f"Erro ao carregar tempos do GRIP: {e}")
        return tempos

