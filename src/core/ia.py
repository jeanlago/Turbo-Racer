import math
import pygame

from config import (
    PP_WHEELBASE, PP_LD_MIN, PP_LD_MAX, PP_LD_KV,
    PP_V_MIN, PP_V_MAX, PP_K_CURV_SPEED,
    PP_BRAKE_EPS, PP_ACCEL_GAIN, PP_BRAKE_GAIN,
    PP_STEER_GAIN, PP_STEER_DEADZONE,
    PP_STUCK_EPS_V, PP_STUCK_TIME, PP_RECOVER_TIME, PP_RECOVER_STEER_DEG,
    PONTOS_DE_CONTROLE
)

def _ang_norm(rad):
    return (rad + math.pi) % (2*math.pi) - math.pi

def _dist(a: pygame.Vector2, b: pygame.Vector2):
    return (a - b).length()

class SeguidorPurePursuit:
    def __init__(self, waypoints, nome="IA", usar_checkpoints=True):
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

        # Sequência ordenada de checkpoints (opcional)
        self.usar_checkpoints = usar_checkpoints and bool(PONTOS_DE_CONTROLE)
        self.checkpoints = []
        self.cp_centers = []
        for (x, y, w, h) in PONTOS_DE_CONTROLE:
            self.checkpoints.append(pygame.Rect(x, y, w, h))
            self.cp_centers.append(pygame.Vector2(x + w/2, y + h/2))
        self.cp_idx = 0

        self.cp_wp_idx = []
        if self.usar_checkpoints and self.wp:
            self.cp_wp_idx = [
                min(range(len(self.wp)), key=lambda j: (self.wp[j] - c).length())
                for c in self.cp_centers
            ]
        else:
            self.checkpoints = []
            self.cp_centers = []
            self.cp_idx = 0

    def _advance_near_index(self, pos):
        # ... (seu algoritmo atual)
        if not self.wp:
            return
        j = self.i_near
        best_d = _dist(pos, self.wp[j])
        improved = True
        while improved:
            improved = False
            j2 = (j + 1) % len(self.wp)
            d2 = _dist(pos, self.wp[j2])
            if d2 + 1e-6 < best_d:
                best_d = d2
                j = j2
                improved = True
        self.i_near = j

    def _find_target_point(self, Ld):
        # ... (seu algoritmo atual)
        if not self.wp:
            return pygame.Vector2(), self.i_near
        j = self.i_near
        acc = 0.0
        while acc < Ld:
            j2 = (j + 1) % len(self.wp)
            acc += _dist(self.wp[j], self.wp[j2])
            j = j2
        return self.wp[j], j

    def _pp_steer(self, pos, ang_rad, alvo):
        # ... (seu algoritmo atual)
        dx, dy = (alvo.x - pos.x), (alvo.y - pos.y)
        local_x =  math.cos(ang_rad) * dx + math.sin(ang_rad) * dy
        local_y = -math.sin(ang_rad) * dx + math.cos(ang_rad) * dy
        if abs(local_x) < 1e-6:
            local_x = 1e-6
        curva = (2.0 * local_y) / (local_x*local_x + local_y*local_y)
        steer = math.atan(PP_WHEELBASE * curva)
        return steer, curva

    def _speed_from_curv(self, kappa):
        v = max(PP_V_MIN, min(PP_V_MAX, PP_K_CURV_SPEED / (1.0 + abs(kappa))))
        return v

    def controlar(self, carro, superficie_pista, is_on_track_fn, dt):
        if not self.wp:
            return

        pos = pygame.Vector2(carro.x, carro.y)
        v_px_s = abs(carro.velocidade) * 60.0

        self._advance_near_index(pos)

        Ld = max(PP_LD_MIN, min(PP_LD_MAX, PP_LD_MIN + PP_LD_KV * v_px_s * 0.02))
        if self.usar_checkpoints and self.cp_centers:
            # Entre pelo traçado, não pelo centro do retângulo
            if self.cp_wp_idx:
                base_idx = self.cp_wp_idx[self.cp_idx]
                ahead = 8  # experimente 6–12 conforme a pista
                j = (base_idx + ahead) % len(self.wp)
                alvo = self.wp[j]
            else:
                alvo = self.cp_centers[self.cp_idx]  # fallback

            # avançar checkpoint ao entrar no retângulo
            if self.checkpoints[self.cp_idx].collidepoint(pos.x, pos.y):
                self.cp_idx = (self.cp_idx + 1) % len(self.cp_centers)
        else:
            alvo, j = self._find_target_point(Ld)
        ang_rad = math.radians(carro.angulo)
        steer_rad, kappa = self._pp_steer(pos, ang_rad, alvo)
        steer_rad *= PP_STEER_GAIN

        v_target = self._speed_from_curv(kappa)
        dv = v_target - v_px_s

        # Controle simples acel/freio (o seu já existente)
        acelerar = dv > PP_BRAKE_EPS
        frear = dv < -PP_BRAKE_EPS

        # Aplicar no carro
        keys = pygame.key.get_pressed()  # apenas para manter assinatura; não usado
        carro._step(acelerar, steer_rad < -PP_STEER_DEADZONE, steer_rad > PP_STEER_DEADZONE, frear,
                    False, superficie_pista, dt)

        # debug
        self._ultimo_alvo = (alvo.x, alvo.y)
        self._ld_usado = Ld
        self._ultimo_vt = v_target
        self._ultimo_kappa = kappa
        # i_near já atualizado

    def desenhar_debug(self, surf, camera=None):
        if not self.debug:
            return
        if self._ultimo_alvo:
            ax, ay = self._ultimo_alvo
            if camera:
                ax, ay = camera.mundo_para_tela(ax, ay)
            pygame.draw.circle(surf, (255, 255, 0), (int(ax), int(ay)), 6, 2)
