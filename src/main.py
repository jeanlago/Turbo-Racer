import os
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from config import (
    LARGURA, ALTURA, FPS, TURBO_P1, TURBO_P2,
    USAR_IA_NO_CARRO_2, MODO_DRIFT
)
from core.pista import (
    carregar_pista, gerar_rota_pp, eh_pixel_da_pista,
    salvar_waypoints, densificar, suavizar_chaikin, desenhar_rota_debug
)
from core.carro import Carro
from core.corrida import GerenciadorCorrida, GerenciadorDrift
from core.camera import Camera
from core.ia import SeguidorPurePursuit

def principal():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Turbo Racer")
    relogio = pygame.time.Clock()

    img_pista, mask_pista, mask_guias = carregar_pista()
    rota = gerar_rota_pp(mask_guias)

    camera = Camera(LARGURA, ALTURA, *img_pista.get_size(), zoom=1.6)

    fonte = pygame.font.SysFont("consolas", 26)
    fonte_small = pygame.font.SysFont("consolas", 18)
    corrida = GerenciadorCorrida(fonte)
    drift = GerenciadorDrift(fonte) if MODO_DRIFT else None

    # Controles: (acelerar, direita, esquerda, frear)
    carro1 = Carro(570, 145, "red",  (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s),     turbo_key=TURBO_P1)
    carro2 = Carro(570, 190, "blue", (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN), turbo_key=TURBO_P2)
    carro3 = Carro(560, 210, "blue2", (0, 0, 0, 0))

    for c in [carro1, carro2, carro3]:
        corrida.registrar_carro(c)

    camera.set_alvo(carro1)

    ia2 = SeguidorPurePursuit(rota, nome="IA-1")
    ia3 = SeguidorPurePursuit(rota, nome="IA-2")
    debug_ia = False
    debug_rota = False

    # gravação da rota
    gravando = False
    pontos_gravados = []
    dist_min_registro = 18.0

    def is_on_track(x, y):
        return eh_pixel_da_pista(mask_pista, x, y)

    rodando = True
    while rodando:
        dt = relogio.tick(FPS) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_F1:
                    debug_ia = not debug_ia
                    ia2.debug = ia3.debug = debug_ia
                elif ev.key == pygame.K_F2:
                    debug_rota = not debug_rota
                elif ev.key == pygame.K_F3:
                    gravando = not gravando
                    if gravando:
                        pontos_gravados.clear()
                elif ev.key == pygame.K_F4:
                    if len(pontos_gravados) >= 6:
                        base = pontos_gravados[:]
                        base = suavizar_chaikin(base, iters=2)
                        base = densificar(base, passo=26)
                        salvar_waypoints(base)
                        rota = base
                        ia2.wp = [pygame.Vector2(p) for p in rota]
                        ia3.wp = [pygame.Vector2(p) for p in rota]
                elif ev.key == pygame.K_c:
                    pontos_gravados.clear()

                # ---------- TURBO (Ctrl) P1 e P2 (barra/hold) ----------
                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    # (se quiser “burst”, chame carro1.usar_turbo_burst() aqui em vez do hold)
                    pass  # o hold é lido direto no update por tecla

                # ---------- DRIFT HOLD ----------
                # P1: Space
                if ev.key == pygame.K_SPACE:
                    carro1.drift_hold = True
                # P2: Shift (L/R)
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    carro2.drift_hold = True

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_SPACE:
                    carro1.drift_hold = False
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    carro2.drift_hold = False

        teclas = pygame.key.get_pressed()

        if not corrida.iniciada:
            corrida.atualizar_contagem(dt)
        corrida.atualizar_tempo(dt)

        if corrida.pode_controlar():
            # player 1
            carro1.atualizar(teclas, mask_pista, dt)

            # gravação de rota com P1
            if gravando:
                if not pontos_gravados:
                    pontos_gravados.append((carro1.x, carro1.y))
                else:
                    lx, ly = pontos_gravados[-1]
                    dx, dy = carro1.x - lx, carro1.y - ly
                    if dx*dx + dy*dy >= dist_min_registro*dist_min_registro:
                        pontos_gravados.append((carro1.x, carro1.y))

            # IA ou player 2
            if USAR_IA_NO_CARRO_2:
                ia2.controlar(carro2, mask_pista, is_on_track, dt)
            else:
                carro2.atualizar(teclas, mask_pista, dt)

            ia3.controlar(carro3, mask_pista, is_on_track, dt)

            for c in (carro1, carro2, carro3):
                corrida.atualizar_progresso_carro(c)

            if MODO_DRIFT and drift is not None:
                drift.atualizar(carro1, dt)

        camera.atualizar(dt)

        # draw
        camera.desenhar_fundo(tela, img_pista)

        if debug_rota and rota:
            desenhar_rota_debug(tela, camera, rota)

        carro1.desenhar(tela, camera=camera)
        carro2.desenhar(tela, camera=camera)
        carro3.desenhar(tela, camera=camera)

        if debug_ia:
            ia2.desenhar_debug(tela, camera=camera)
            ia3.desenhar_debug(tela, camera=camera)

        # overlay gravação
        if gravando:
            for (x, y) in pontos_gravados:
                sx, sy = camera.mundo_para_tela(x, y)
                pygame.draw.circle(tela, (255, 100, 100), (int(sx), int(sy)), 3)
            msg = "[GRAVANDO WAYPOINTS] F3: parar | F4: salvar | C: limpar"
            sombra = fonte_small.render(msg, True, (0, 0, 0))
            txt = fonte_small.render(msg, True, (255, 220, 120))
            tela.blit(sombra, (20+1, ALTURA-28+1))
            tela.blit(txt, (20, ALTURA-28))

        if MODO_DRIFT and drift is not None:
            drift.desenhar_hud(tela, 8, 8)
        else:
            corrida.desenhar_hud(tela, [carro1, carro2, carro3])

        corrida.desenhar_semaforo(tela, LARGURA, ALTURA)
        if corrida.alguem_finalizou():
            corrida.desenhar_podio(tela, LARGURA, ALTURA, [carro1, carro2, carro3])

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    principal()
