# src/core/casa.py
"""
Sistema de Point and Click da Casa
Gerencia interações com objetos da casa e status do jogador
"""

import os
import json
from typing import Optional
# Importar config primeiro para aplicar filtro de stderr
from config import LARGURA, ALTURA, DIR_PROJETO
# Importar pygame depois do config (filtro já aplicado)
import pygame

# Import lazy
def _get_render_text():
    from core.menu import render_text
    return render_text

CAMINHO_HITBOXES = os.path.join(DIR_PROJETO, "data", "scenario_hitboxes.json")
CAMINHO_HOVER = os.path.join(DIR_PROJETO, "assets", "images", "hover")

def casa_loop(screen, sprite_fundo: Optional[str] = None) -> Optional[str]:
    """
    Loop principal da casa (point and click)
    Retorna "voltar_mapa" para voltar ao mapa ou None
    """
    from core.status_jogador import status_jogador
    from config import FPS
    
    clock = pygame.time.Clock()
    render_text = _get_render_text()
    
    # Carregar background
    if sprite_fundo and os.path.exists(sprite_fundo):
        bg_raw = pygame.image.load(sprite_fundo).convert_alpha()
        bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
    else:
        from config import obter_caminho_sprite_dia_noite
        caminho_casa = obter_caminho_sprite_dia_noite("casa")
        if os.path.exists(caminho_casa):
            bg_raw = pygame.image.load(caminho_casa).convert_alpha()
            bg = pygame.transform.scale(bg_raw, (LARGURA, ALTURA))
        else:
            bg = pygame.Surface((LARGURA, ALTURA))
            bg.fill((30, 30, 40))
    
    # Carregar hitboxes
    hitboxes = []
    hover_hitbox = None
    hover_sprite = None
    
    if os.path.exists(CAMINHO_HITBOXES):
        try:
            with open(CAMINHO_HITBOXES, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Tentar várias chaves possíveis (casa.png, casa_dia.png, casa_noite.png)
                if "casa.png" in data:
                    hitboxes = data["casa.png"]
                elif "casa_dia.png" in data:
                    hitboxes = data["casa_dia.png"]
                elif "casa_noite.png" in data:
                    hitboxes = data["casa_noite.png"]
                else:
                    # Se não encontrou, tentar qualquer chave que comece com "casa"
                    for key in data.keys():
                        if key.lower().startswith("casa"):
                            hitboxes = data[key]
                            print(f"Carregadas hitboxes da chave: {key}")
                            break
                
                if not hitboxes:
                    print(f"AVISO: Nenhuma hitbox encontrada para 'casa' no arquivo {CAMINHO_HITBOXES}")
                    print(f"Chaves disponíveis: {list(data.keys())}")
        except Exception as e:
            print(f"Erro ao carregar hitboxes da casa: {e}")
            import traceback
            traceback.print_exc()
    
    # Estado
    mensagem_temporaria = None
    tempo_mensagem = 0.0
    duracao_mensagem = 2.0
    
    # Estado de hover (mantido entre frames)
    hover_sprite_rect = None
    hover_hitbox_atual = None
    hover_sprite_atual = None
    
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Atualizar tempo do jogo (1 minuto real = 1 hora do jogo)
        from core.tempo_jogo import gerenciador_tempo
        gerenciador_tempo.atualizar(dt)
        
        # Atualizar status
        status_jogador.atualizar(dt)
        
        # Atualizar mensagem temporária
        if mensagem_temporaria:
            tempo_mensagem += dt
            if tempo_mensagem >= duracao_mensagem:
                mensagem_temporaria = None
                tempo_mensagem = 0.0
        
        # Verificar hover continuamente (não apenas em eventos de movimento)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_hitbox_atual = None
        hover_sprite_atual = None
        hover_sprite_rect = None
        
        for hb in hitboxes:
            rect = pygame.Rect(hb["x"], hb["y"], hb["largura"], hb["altura"])
            if rect.collidepoint(mouse_x, mouse_y):
                hover_hitbox_atual = hb
                # Carregar sprite de hover e dimensionar para a hitbox (com aumento)
                if hb.get("hover_sprite"):
                    from config import obter_caminho_hover_dia_noite
                    hover_path_original = os.path.join(DIR_PROJETO, hb["hover_sprite"].replace("\\", "/"))
                    # Tentar carregar versão dia/noite
                    hover_path = obter_caminho_hover_dia_noite(hover_path_original)
                    if os.path.exists(hover_path):
                        try:
                            hover_sprite_raw = pygame.image.load(hover_path).convert_alpha()
                            
                            # Escalas diferentes por objeto para melhor proporção
                            hitbox_id = hb.get("id", "").lower()
                            if "sofa" in hitbox_id:
                                escala = 1.35  # Sofá: 35% maior
                            elif "tv" in hitbox_id:
                                escala = 1.30  # TV: 30% maior
                            elif "cafe" in hitbox_id or "cafeteira" in hitbox_id:
                                # Cafeteira: manter proporção original do sprite
                                sprite_w, sprite_h = hover_sprite_raw.get_size()
                                # Calcular escala baseada na hitbox, mas manter proporção do sprite
                                escala_w = hb["largura"] / sprite_w if sprite_w > 0 else 1.0
                                escala_h = hb["altura"] / sprite_h if sprite_h > 0 else 1.0
                                escala = min(escala_w, escala_h) * 1.15  # 15% maior mantendo proporção
                            else:
                                escala = 1.15  # Padrão: 15% maior
                            
                            hover_largura = int(hb["largura"] * escala)
                            hover_altura = int(hb["altura"] * escala)
                            # Centralizar o hover na hitbox
                            offset_x = (hb["largura"] - hover_largura) // 2
                            offset_y = (hb["altura"] - hover_altura) // 2
                            
                            hover_sprite_atual = pygame.transform.scale(
                                hover_sprite_raw, 
                                (hover_largura, hover_altura)
                            )
                            hover_sprite_rect = (hb["x"] + offset_x, hb["y"] + offset_y)
                        except Exception as e:
                            print(f"Erro ao carregar sprite de hover: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"AVISO: Sprite de hover não encontrado: {hover_path}")
                        print(f"  Caminho original: {hover_path_original}")
                break
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from core.tempo_jogo import gerenciador_tempo
                    status_jogador.salvar()
                    gerenciador_tempo.salvar()
                    return "voltar_mapa"
            
            # MOUSEMOTION não precisa mais processar hover aqui, já é feito continuamente acima
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    mouse_x, mouse_y = event.pos
                    
                    # Verificar clique em hitbox
                    for hb in hitboxes:
                        rect = pygame.Rect(hb["x"], hb["y"], hb["largura"], hb["altura"])
                        if rect.collidepoint(mouse_x, mouse_y):
                            hitbox_id = hb.get("id", "").lower()
                            
                            # Processar interações
                            if "geladeira" in hitbox_id:
                                status_jogador.comer(50.0)
                                mensagem_temporaria = "Você comeu algo da geladeira. Fome restaurada!"
                                tempo_mensagem = 0.0
                            
                            elif "cama" in hitbox_id:
                                from core.tempo_jogo import gerenciador_tempo
                                status_jogador.dormir("cama", 100.0)
                                gerenciador_tempo.avancar_horas(8.0)  # Avançar 8 horas
                                gerenciador_tempo.salvar()
                                hora_atual = gerenciador_tempo.obter_hora_formatada()
                                mensagem_temporaria = f"Você dormiu na cama. Sono restaurado completamente! Agora são {hora_atual}."
                                tempo_mensagem = 0.0
                            
                            elif "sofa" in hitbox_id:
                                from core.tempo_jogo import gerenciador_tempo
                                status_jogador.dormir("sofa", 50.0)
                                gerenciador_tempo.avancar_horas(3.0)  # Avançar 3 horas
                                gerenciador_tempo.salvar()
                                hora_atual = gerenciador_tempo.obter_hora_formatada()
                                mensagem_temporaria = f"Você descansou no sofá. Sono parcialmente restaurado. Agora são {hora_atual}."
                                tempo_mensagem = 0.0
                            
                            elif "cafe" in hitbox_id or "cafeteira" in hitbox_id:
                                status_jogador.dormir("cafe", 30.0)
                                mensagem_temporaria = "Você tomou café. Um pouco mais alerta!"
                                tempo_mensagem = 0.0
                            
                            elif "tv" in hitbox_id:
                                status_jogador.assistir_tv(50.0)
                                mensagem_temporaria = "Você assistiu TV. Tédio reduzido!"
                                tempo_mensagem = 0.0
                            
                            elif "pc" in hitbox_id:
                                # Abrir menu de corridas
                                from core.pc_corridas import pc_corridas_loop
                                corrida_info = pc_corridas_loop(screen)
                                
                                if corrida_info:
                                    # Iniciar corrida
                                    from main import principal
                                    from core.progresso import gerenciador_progresso
                                    from core.game_modes import ModoJogo, TipoJogo
                                    
                                    # Obter carro atual do jogador
                                    carro_p1_idx = 0
                                    if gerenciador_progresso.carro_p1_atual:
                                        from config import CARROS_DISPONIVEIS
                                        for i, carro in enumerate(CARROS_DISPONIVEIS):
                                            if carro.get("prefixo_cor") == gerenciador_progresso.carro_p1_atual:
                                                carro_p1_idx = i
                                                break
                                    
                                    # Iniciar corrida no modo campanha
                                    principal(
                                        carro_selecionado_p1=carro_p1_idx,
                                        mapa_selecionado=corrida_info["pista"],
                                        modo_jogo=ModoJogo.UM_JOGADOR,
                                        tipo_jogo=TipoJogo.CORRIDA,
                                        voltas=corrida_info["voltas"],
                                        dificuldade_ia=corrida_info["dificuldade"],
                                        modo_arcade=False
                                    )
                                
                                # Voltar para a casa após a corrida
                                continue
                            
                            break
        
        # Desenhar
        screen.blit(bg, (0, 0))
        
        # Desenhar sprite de hover (posicionado na hitbox)
        if hover_sprite_atual and hover_sprite_rect:
            screen.blit(hover_sprite_atual, hover_sprite_rect)
        
        # Debug: desenhar hitboxes (opcional, remover depois)
        # for hb in hitboxes:
        #     pygame.draw.rect(screen, (255, 0, 0), (hb["x"], hb["y"], hb["largura"], hb["altura"]), 2)
        
        # Desenhar status do jogador (canto superior direito)
        status_x = LARGURA - 250
        status_y = 20
        
        # Fundo do status
        status_bg = pygame.Surface((230, 180), pygame.SRCALPHA)
        status_bg.fill((0, 0, 0, 180))
        screen.blit(status_bg, (status_x, status_y))
        pygame.draw.rect(screen, (255, 255, 255), (status_x, status_y, 230, 180), 2)
        
        # Título
        titulo_status = render_text("STATUS", 20, (255, 255, 255), bold=True, pixel_style=True)
        screen.blit(titulo_status, (status_x + 10, status_y + 10))
        
        # Popularidade
        cor_pop = (100, 200, 255) if status_jogador.popularidade >= 50 else (255, 150, 100)
        pop_texto = render_text(f"Popularidade: {int(status_jogador.popularidade)}%", 14, cor_pop, bold=False, pixel_style=True)
        screen.blit(pop_texto, (status_x + 10, status_y + 40))
        
        # Fome
        cor_fome = (100, 255, 100) if status_jogador.fome >= 50 else (255, 100, 100)
        fome_texto = render_text(f"Fome: {int(status_jogador.fome)}%", 14, cor_fome, bold=False, pixel_style=True)
        screen.blit(fome_texto, (status_x + 10, status_y + 65))
        
        # Sono
        cor_sono = (100, 255, 100) if status_jogador.sono >= 50 else (255, 100, 100)
        sono_texto = render_text(f"Sono: {int(status_jogador.sono)}%", 14, cor_sono, bold=False, pixel_style=True)
        screen.blit(sono_texto, (status_x + 10, status_y + 90))
        
        # Tédio
        cor_tedio = (255, 100, 100) if status_jogador.tedio >= 50 else (100, 255, 100)
        tedio_texto = render_text(f"Tédio: {int(status_jogador.tedio)}%", 14, cor_tedio, bold=False, pixel_style=True)
        screen.blit(tedio_texto, (status_x + 10, status_y + 115))
        
        # Multiplicador de dinheiro
        mult_texto = render_text(f"$ Multi: {status_jogador.obter_multiplicador_dinheiro():.2f}x", 12, (255, 255, 100), bold=False, pixel_style=True)
        screen.blit(mult_texto, (status_x + 10, status_y + 145))
        
        # Mensagem temporária
        if mensagem_temporaria:
            alpha = 1.0 - (tempo_mensagem / duracao_mensagem)
            if alpha > 0:
                msg_texto = render_text(mensagem_temporaria, 18, (255, 255, 200), bold=True, pixel_style=True)
                msg_x = (LARGURA - msg_texto.get_width()) // 2
                msg_y = ALTURA - 100
                
                # Fundo semi-transparente
                msg_bg = pygame.Surface((msg_texto.get_width() + 40, msg_texto.get_height() + 20), pygame.SRCALPHA)
                msg_alpha = int(alpha * 200)
                msg_bg.fill((0, 0, 0, msg_alpha))
                screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
                screen.blit(msg_texto, (msg_x, msg_y))
        
        # Instruções
        instrucoes = render_text("Clique nos objetos | ESC para voltar", 14, (150, 150, 150), bold=False, pixel_style=True)
        screen.blit(instrucoes, (10, ALTURA - 30))
        
        pygame.display.flip()
    
    status_jogador.salvar()
    return "voltar_mapa"

