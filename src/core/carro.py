# core/carro.py
import os, math, pygame
from config import (
    LARGURA, ALTURA, DIR_SPRITES,
    MODO_DRIFT, DRIFT_MIN_VEL, DRIFT_EMISSAO_QPS,
    DRIFT_ATRITO_GERAL, DRIFT_ATRITO_DERRAPANDO, DRIFT_GIRO_RESP,
    VEL_MAX, ACEL_BASE,
    TURBO_FORCA_IMPULSO, TURBO_FATOR, TURBO_DURACAO_S, TURBO_COOLDOWN_S
)
from core.pista import eh_pixel_da_pista
from core.particulas import EmissorFumaca

# Mapear nomes ("K_LCTRL", etc.) -> constantes pygame.K_*
KEY_NAME_TO_CONST = {name: getattr(pygame, name) for name in dir(pygame) if name.startswith("K_")}

class Carro:
    """
    Física com drift arcade:
      - Mantém tua aceleração/freio.
      - Em drift (handbrake): grip lateral quase 1 (escorrega), injeta slip contínuo, e aplica yaw extra a partir do slip.
      - S (freio) NÃO ativa drift; drift só via self.drift_hold (Space/Shift no main).
    """
    # Grip lateral (fator por frame sobre v_lat): normal "mata" lateral; em drift quase não reduz.
    LATERAL_GRIP_NORMAL = 0.82
    LATERAL_GRIP_DRIFT  = 0.9985  # deixa escorregar de lado

    # Parâmetros do drift (ajuste fino)
    DRIFT_KICK_START     = 0.14   # fração de |v_long| injetada em v_lat ao iniciar a derrapagem
    DRIFT_FEED_PER_S     = 0.70   # slip contínuo por segundo enquanto handbrake+direção
    DRIFT_RATIO_MAX      = 1.25   # |v_lat| <= |v_long| * ratio + margem (limita ângulo de drift)
    DRIFT_RATIO_MARGIN   = 2.5    # margem fixa (px/frame) para baixa velocidade
    DRIFT_YAW_FROM_SLIP  = 0.90   # (deg) por (px/frame) de v_lat
    DRIFT_SPEED_HOLD_S   = 1.0    # janela mantendo mais velocidade no começo do drift
    DRIFT_LONG_EXTRA_LOSS = 0.985 # perda longitudinal extra após a janela

    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None):
        self.x = float(x)
        self.y = float(y)
        self.angulo = 0.0  # graus (0 aponta pra -x do sprite)
        # velocidades no mundo
        self.vx = 0.0
        self.vy = 0.0

        # compat p/ HUD/lógicas externas: projeção longitudinal
        self.velocidade = 0.0

        self.controles = controles
        self.turbo_key = KEY_NAME_TO_CONST.get(turbo_key) if isinstance(turbo_key, str) else turbo_key

        caminho_sprite = os.path.join(DIR_SPRITES, f"{prefixo_cor}.png")
        self.sprite_base = pygame.image.load(caminho_sprite).convert_alpha()

        # Física base (mantidas)
        self.VEL_MAX_FRENTE = VEL_MAX if 'VEL_MAX' in globals() else 6.0
        self.VEL_MAX_RE = -2.0
        self.ACELERACAO = ACEL_BASE if 'ACEL_BASE' in globals() else 0.08
        self.FREIO = 0.14
        self.ATRITO_LONG_NORMAL = DRIFT_ATRITO_GERAL if 'DRIFT_ATRITO_GERAL' in globals() else 0.992
        self.ATRITO_LONG_DRIFT  = DRIFT_ATRITO_DERRAPANDO if 'DRIFT_ATRITO_DERRAPANDO' in globals() else 0.985
        self.GIRO_MAX = 4.0

        # Turbo (modo hold)
        self.turbo_carga = 100.0
        self.turbo_ativo = False
        self.TURBO_MULT_VEL = 1.6
        self.TURBO_MULT_ACEL = 1.6
        self.TURBO_DRENO = 35.0
        self.TURBO_RECUP = 12.0

        # Efeitos/estado de drift
        self.emissor = EmissorFumaca()
        self.drifting = False
        self.drift_intensidade = 0.0
        self.drift_hold = False
        self._was_drifting = False
        self._drift_time = 0.0

        # Turbo "burst" opcional (mantido)
        self._turbo_timer = 0.0
        self._turbo_cd = 0.0
        self._turbo_mul = 1.0

    # ===== vetores úteis =====
    def _vetor_frente(self):
        rad = math.radians(self.angulo)
        return (-math.cos(rad), math.sin(rad))

    def _vetor_direita(self):
        fx, fy = self._vetor_frente()
        return (fy, -fx)

    def _decomp_vel(self):
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        v_long = self.vx * fx + self.vy * fy
        v_lat  = self.vx * rx + self.vy * ry
        return v_long, v_lat

    def _recomp_vel(self, v_long, v_lat):
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        self.vx = fx * v_long + rx * v_lat
        self.vy = fy * v_long + ry * v_lat

    # ===== Turbo opcional (impulso curto) =====
    def usar_turbo(self):
        if self._turbo_cd > 0.0:
            return
        v_long, v_lat = self._decomp_vel()
        v_long += TURBO_FORCA_IMPULSO * 0.016
        self._recomp_vel(v_long, v_lat)
        self._turbo_timer = TURBO_DURACAO_S
        self._turbo_mul = TURBO_FATOR
        self._turbo_cd = TURBO_COOLDOWN_S

    # ===== desenho =====
    def desenhar(self, superficie, camera=None):
        if camera is None:
            sprite_rot = pygame.transform.rotate(self.sprite_base, self.angulo)
            rect = sprite_rot.get_rect(center=(self.x, self.y))
            superficie.blit(sprite_rot, rect.topleft)
            self.emissor.draw(superficie, camera)
            return
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        sprite_rot = pygame.transform.rotozoom(self.sprite_base, self.angulo, camera.zoom)
        rect = sprite_rot.get_rect(center=(sx, sy))
        superficie.blit(sprite_rot, rect.topleft)
        self.emissor.draw(superficie, camera)

    # ===== física =====
    def _step(self, acelerar, direita, esquerda, frear_re, *rest):
        """
        Assinaturas aceitas:
          _step(a, d, e, f, turbo_pressed, superficie, dt)
          _step(a, d, e, f, superficie, dt)
        """
        if len(rest) == 3:
            turbo_pressed, superficie_mascara, dt = rest
        elif len(rest) == 2:
            superficie_mascara, dt = rest
            turbo_pressed = False
        else:
            raise TypeError("Assinatura inválida de Carro._step")

        x_ant, y_ant = self.x, self.y

        # Turbo (HOLD) separado da aceleração
        self.turbo_ativo = bool(turbo_pressed and self.turbo_carga > 0.0)
        acel_mult = (self.TURBO_MULT_ACEL if self.turbo_ativo or (self._turbo_timer > 0.0) else 1.0)
        vel_max   = self.VEL_MAX_FRENTE * (self.TURBO_MULT_VEL if self.turbo_ativo or (self._turbo_timer > 0.0) else 1.0)

        # Decompõe velocidade atual
        v_long, v_lat = self._decomp_vel()

        # Aceleração / Freio — mantidos
        if acelerar:
            v_long = min(v_long + self.ACELERACAO * acel_mult, vel_max)
        elif frear_re:
            if v_long > 0.2:
                v_long = max(0.0, v_long - self.FREIO)
            else:
                v_long = max(self.VEL_MAX_RE, v_long - (self.FREIO * 0.5))
        else:
            v_long *= self.ATRITO_LONG_NORMAL

        # Estado de drift: apenas com handbrake e velocidade mínima
        drifteando = bool(self.drift_hold) and (abs(v_long) * 60.0 > (DRIFT_MIN_VEL * 60.0 if 'DRIFT_MIN_VEL' in globals() else 0))

        # Timer para janela de "hold" de velocidade
        if drifteando:
            self._drift_time += dt
        else:
            self._drift_time = 0.0

        # Direção/ângulo base
        speed_mag = math.hypot(self.vx, self.vy)
        fator_giro = min(speed_mag * 0.5, self.GIRO_MAX)
        if drifteando:
            fator_giro *= (DRIFT_GIRO_RESP if 'DRIFT_GIRO_RESP' in globals() else 1.25)

        sinal_direcao = 1.0 if v_long >= 0.05 else -1.0
        if direita:
            self.angulo -= fator_giro * sinal_direcao
        if esquerda:
            self.angulo += fator_giro * sinal_direcao

        # ======== BLOCO: DRIFT MELHORADO ========
        # 1) Kick de slip quando COMEÇA o drift (traseira sai imediatamente)
        if drifteando and not self._was_drifting and (direita ^ esquerda) and abs(v_long) > 0.2:
            direcao_out = (1 if esquerda else -1)  # esquerda => traseira pra direita (v_lat > 0)
            v_lat += direcao_out * abs(v_long) * self.DRIFT_KICK_START

        # 2) Slip CONTÍNUO enquanto segura handbrake + direção (injeta lateral, não “só acelera”)
        if drifteando and (direita ^ esquerda) and abs(v_long) > 0.1:
            direcao_out = (1 if esquerda else -1)
            v_lat += direcao_out * abs(v_long) * (self.DRIFT_FEED_PER_S * dt)

        # 3) Grip lateral: quase 1.0 em drift (escorrega), forte no normal
        lat_grip = (self.LATERAL_GRIP_DRIFT if drifteando else self.LATERAL_GRIP_NORMAL)
        v_lat *= lat_grip

        # 4) Limite de drift angle: impede “pirueta” e mantém sensação arcade
        max_vlat = max(self.DRIFT_RATIO_MARGIN, abs(v_long) * self.DRIFT_RATIO_MAX)
        if v_lat >  max_vlat: v_lat =  max_vlat
        if v_lat < -max_vlat: v_lat = -max_vlat

        # 5) Yaw induzido pelo slip (sobre-esterço / contraesterço visual)
        if drifteando and abs(v_lat) > 0.001:
            yaw_extra = self.DRIFT_YAW_FROM_SLIP * v_lat * (1.0 if v_long >= 0.0 else -1.0)
            if yaw_extra >  self.GIRO_MAX: yaw_extra =  self.GIRO_MAX
            if yaw_extra < -self.GIRO_MAX: yaw_extra = -self.GIRO_MAX
            self.angulo += yaw_extra
        # ========== FIM DO BLOCO DRIFT ===========

        # Normaliza ângulo
        if self.angulo > 180: self.angulo -= 360
        if self.angulo < -180: self.angulo += 360

        # Atrito longitudinal: durante o drift segura um pouco e depois começa a cair
        if drifteando:
            v_long *= self.ATRITO_LONG_DRIFT
            if self._drift_time > self.DRIFT_SPEED_HOLD_S:
                v_long *= self.DRIFT_LONG_EXTRA_LOSS
        # (fora do drift já tratamos acima)

        # Recompor e avançar
        self._recomp_vel(v_long, v_lat)
        self.x += self.vx
        self.y += self.vy

        # Colisão com a pista (amostras estreitas)
        fx, fy = self._vetor_frente()
        dir_frente_x, dir_frente_y = fx, fy
        dir_direita_x, dir_direita_y = (fy, -fx)

        cx, cy = int(self.x), int(self.y)
        houve_colisao = False
        amostras_local = [(0, 0), (10, 0), (-10, 0), (0, 6), (0, -6)]
        for ox, oy in amostras_local:
            px = int(cx + ox * dir_frente_x + oy * dir_direita_x)
            py = int(cy + ox * dir_frente_y + oy * dir_direita_y)
            if not eh_pixel_da_pista(superficie_mascara, px, py):
                houve_colisao = True
                break

        if houve_colisao:
            self.x, self.y = x_ant, y_ant
            self.vx *= -0.4
            self.vy *= -0.4
            v_long, v_lat = self._decomp_vel()
            if v_long < self.VEL_MAX_RE:
                v_long = self.VEL_MAX_RE
            self._recomp_vel(v_long, v_lat)

        # Limites da área
        self.x = max(0.0, min(LARGURA * 1.0, self.x))
        self.y = max(0.0, min(ALTURA * 1.0, self.y))

        # Atualiza “velocidade” (longitudinal) para HUD/lógica existente
        self.velocidade = v_long

        # Partículas & intensidade de drift
        if MODO_DRIFT:
            v_px_s = math.hypot(self.vx, self.vy) * 60.0
            self.drifting = drifteando
            virando_flag = 1.0 if (direita or esquerda) else 0.0
            self.drift_intensidade = 0.7 * min(1.0, v_px_s / 300.0) + 0.3 * virando_flag
            if not self.drifting:
                self.drift_intensidade *= 0.3
            if self.drifting and (v_px_s > (DRIFT_MIN_VEL * 60.0) if 'DRIFT_MIN_VEL' in globals() else v_px_s > 40.0):
                taxa_base = DRIFT_EMISSAO_QPS * min(1.0, max(0.25, v_px_s / 320.0))
                taxa = taxa_base if v_px_s > 10.0 else DRIFT_EMISSAO_QPS * 0.6
                self.emissor.spawn(self.x, self.y, fx, fy, taxa, dt)

        self.emissor.update(dt)
        self._was_drifting = drifteando

        # Timers turbo "burst"
        if self._turbo_timer > 0.0:
            self._turbo_timer -= dt
            if self._turbo_timer <= 0.0:
                self._turbo_mul = 1.0
        if self._turbo_cd > 0.0:
            self._turbo_cd -= dt

        # Consumo/recarga do turbo (modo HOLD)
        if self.turbo_ativo:
            self.turbo_carga = max(0.0, self.turbo_carga - self.TURBO_DRENO * dt)
        else:
            self.turbo_carga = min(100.0, self.turbo_carga + self.TURBO_RECUP * dt)

    def atualizar(self, teclas, superficie_mascara, dt):
        acelerar = teclas[self.controles[0]]
        direita  = teclas[self.controles[1]]
        esquerda = teclas[self.controles[2]]
        frear_re = teclas[self.controles[3]]

        turbo_pressed = False
        if self.turbo_key is not None:
            turbo_pressed = bool(teclas[self.turbo_key])

        self._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt)

    def atualizar_com_ai(self, superficie_mascara, dt, waypoints, raio=32):
        if not hasattr(self, "_ai_idx"):
            self._ai_idx = 0
        alvo = waypoints[self._ai_idx]
        dx = alvo[0] - self.x
        dy = alvo[1] - self.y
        alvo_ang = math.degrees(math.atan2(dy, dx)) + 180
        diff = (alvo_ang - self.angulo + 180) % 360 - 180

        acelerar = True
        direita = diff < -3
        esquerda = diff > 3
        frear_re = False
        turbo_pressed = False

        if dx*dx + dy*dy < raio*raio:
            self._ai_idx = (self._ai_idx + 1) % len(waypoints)

        self._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt)
