import math
import pygame

from config import (
    PP_WHEELBASE, PP_LD_MIN, PP_LD_MAX, PP_LD_KV,
    PP_V_MIN, PP_V_MAX, PP_K_CURV_SPEED,
    PP_BRAKE_EPS, PP_ACCEL_GAIN, PP_BRAKE_GAIN,
    PP_STEER_GAIN, PP_STEER_DEADZONE,
    PP_STUCK_EPS_V, PP_STUCK_TIME, PP_RECOVER_TIME, PP_RECOVER_STEER_DEG
)

def _ang_norm(rad):
    return (rad + math.pi) % (2*math.pi) - math.pi

def _dist(a: pygame.Vector2, b: pygame.Vector2):
    return (a - b).length()

class SeguidorPurePursuit:
    def __init__(self, waypoints, nome="IA"):
        self.nome = nome
        self.wp = [pygame.Vector2(p) for p in waypoints]
        self.i_near = 0
        self._stuck_timer = 0.0
        self._recover = False
        self._rec_timer = 0.0
        self._rec_steer = math.radians(PP_RECOVER_STEER_DEG)
        self.debug = False
        self._ultimo_alvo = None
        self._ld_usado = 0.0
        self._ultimo_vt = 0.0
        self._ultimo_kappa = 0.0

    def _advance_near_index(self, pos):
        n = len(self.wp)
        if n == 0:
            return
        best = self.i_near
        best_d = _dist(pos, self.wp[best])
        for k in range(1, min(n, 20)):
            j = (self.i_near + k) % n
            d = _dist(pos, self.wp[j])
            if d + 2.0 < best_d:
                best = j
                best_d = d
        self.i_near = best

    def _find_target_point(self, Ld):
        n = len(self.wp)
        if n == 0:
            return pygame.Vector2(0, 0), 0
        i = self.i_near
        total = 0.0
        prev = self.wp[i]
        for step in range(1, n + 1):
            j = (i + step) % n
            seg = self.wp[j] - prev
            L = seg.length()
            if L < 1e-6:
                prev = self.wp[j]
                continue
            if total + L >= Ld:
                t = (Ld - total) / L
                return prev + seg * t, j
            total += L
            prev = self.wp[j]
        return self.wp[self.i_near], self.i_near

    def _pp_steer(self, pos, ang_rad, alvo):
        v = alvo - pos
        theta_t = math.atan2(v.y, v.x)
        alpha = _ang_norm(theta_t - ang_rad)
        Ld = max(v.length(), 1.0)
        kappa = 2.0 * math.sin(alpha) / Ld
        delta = math.atan(PP_WHEELBASE * kappa)
        return delta, kappa

    def _speed_from_curv(self, kappa):
        v = PP_K_CURV_SPEED / (abs(kappa) + 1e-3)
        return max(PP_V_MIN, min(PP_V_MAX, v))

    def _update_stuck(self, vel, dt):
        if abs(vel) < PP_STUCK_EPS_V:
            self._stuck_timer += dt
        else:
            self._stuck_timer = 0.0
            self._recover = False
        if (not self._recover) and (self._stuck_timer > PP_STUCK_TIME):
            self._recover = True
            self._rec_timer = 0.0

    def controlar(self, carro, superficie_pista, is_on_track_fn, dt):
        if not self.wp:
            return

        pos = pygame.Vector2(carro.x, carro.y)
        v_px_s = abs(carro.velocidade) * 60.0

        self._advance_near_index(pos)

        Ld = max(PP_LD_MIN, min(PP_LD_MAX, PP_LD_MIN + PP_LD_KV * v_px_s * 0.02))
        alvo, j = self._find_target_point(Ld)
        ang_rad = math.radians(carro.angulo)
        steer_rad, kappa = self._pp_steer(pos, ang_rad, alvo)
        steer_rad *= PP_STEER_GAIN

        v_target = self._speed_from_curv(kappa)
        dv = v_target - v_px_s

        acelerar = False
        frear_re = False
        if dv > PP_BRAKE_EPS:
            acelerar = True
        elif dv < -PP_BRAKE_EPS:
            frear_re = True
        else:
            acelerar = True

        # Sonda à frente: se sair da pista, freia
        probe = pos + pygame.Vector2(math.cos(ang_rad), math.sin(ang_rad)) * 40
        if not is_on_track_fn(int(probe.x), int(probe.y)):
            frear_re = True
            acelerar = False

        self._update_stuck(v_px_s, dt)

        direita = esquerda = False
        if self._recover:
            self._rec_timer += dt
            frear_re = True
            acelerar = False
            steer_cmd = self._rec_steer if int(self._rec_timer * 4) % 2 == 0 else -self._rec_steer
        else:
            steer_cmd = steer_rad

        if steer_cmd > PP_STEER_DEADZONE:
            esquerda = True
        elif steer_cmd < -PP_STEER_DEADZONE:
            direita = True

        # >>> CORREÇÃO: assinatura nova do _step inclui turbo_pressed <<<
        carro._step(acelerar, direita, esquerda, frear_re, superficie_pista, dt)

        self._ultimo_alvo = (alvo.x, alvo.y)
        self._ld_usado = Ld
        self._ultimo_vt = v_target
        self._ultimo_kappa = kappa
        self.i_near = j

    def desenhar_debug(self, surf, camera=None):
        if not self.debug:
            return
        if self._ultimo_alvo:
            ax, ay = self._ultimo_alvo
            if camera:
                ax, ay = camera.mundo_para_tela(ax, ay)
            pygame.draw.circle(surf, (255, 255, 0), (int(ax), int(ay)), 6, 2)
