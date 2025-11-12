# core/carro_fisica.py
import os, math, pygame
from config import (
    LARGURA, ALTURA, DIR_SPRITES,
    MODO_DRIFT, DRIFT_MIN_VEL, DRIFT_EMISSAO_QPS,
    VEL_MAX, ACEL_BASE,
    TURBO_FORCA_IMPULSO, TURBO_FATOR, TURBO_DURACAO_S, TURBO_COOLDOWN_S
)
from core.pista_grip import eh_pixel_transitavel_grip, verificar_colisao_grip, verificar_na_grama_grip
from core.particulas import EmissorNitro
from core.skidmarks import GerenciadorSkidmarks

KEY_NAME_TO_CONST = {name: getattr(pygame, name) for name in dir(pygame) if name.startswith("K_")}

class CarroFisica:
    TRACAO_TRASEIRA = "rear"
    TRACAO_FRONTAL  = "front"
    TRACAO_INTEGRAL = "awd"

    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None, nome=None, tipo_tracao=None):
        # --- Estado global ---
        self.x = float(x); self.y = float(y)
        self.angulo = 0.0
        self.vx = 0.0; self.vy = 0.0
        self.r  = 0.0
        
        # Flag para indicar se está na grama (estilo GRIP)
        self.na_grama = False

        # --- Estado no frame do carro ---
        self.v_long = 0.0
        self.v_lat  = 0.0
        self.yaw_rate = 0.0

        # --- Config básica / sprites ---
        self.controles = controles
        self.turbo_key = KEY_NAME_TO_CONST.get(turbo_key) if isinstance(turbo_key, str) else turbo_key
        self.nome = nome or f"Carro {prefixo_cor}"
        self.tipo_tracao = tipo_tracao or self.TRACAO_TRASEIRA
        self._carregar_sprite(prefixo_cor)

        # --- Parâmetros físicos ---
        self.m  = 1200.0
        self.g  = 9.81
        self.L  = 2.5
        self.b  = 1.55
        self.a  = self.L - self.b
        self.Iz = 2400.0

        # pneus
        self.Cf_base = 70000.0 if self.tipo_tracao != self.TRACAO_TRASEIRA else 68000.0
        self.Cr_base = 50000.0 if self.tipo_tracao != self.TRACAO_TRASEIRA else 48000.0
        self.mu_peak   = 1.05
        self.mu_long   = 1.00
        self.alpha_sat = math.radians(12.5)

        # motor e resistências
        self.engine_force    = 12000.0
        self.brake_force     = 11000.0
        self.handbrake_force = 12000.0
        self.drag            = 0.0009
        self.roll_res        = 0.10
        self.downforce_k     = 0.0

        # forças separadas p/ frente e ré + limite de ré
        self.engine_force_fwd = 90000.0
        self.engine_force_rev = 1800.0
        self.V_TOP_REV        = 120.0

        # power oversteer (mais contido)
        self.power_oversteer_k = 0.12      # ★ antes 0.18: menos sobre-esterço só por acelerar
        self.min_speed_oversteer = 100.0

        # limites de velocidade
        self.V_TOP  = 750.0
        self.V_SOFT = 0.95 * self.V_TOP

        # direção e estabilidade
        self.steer_rad_max = math.radians(42.0)  # ★ antes 46: menos lock → mais estável
        self.steer_rate    = math.radians(520.0)
        self.speed_steer_k = 0.016               # ★ mais redução de lock com a velocidade
        # ↑ (0.018) = menos lock em alta = mais estável; ↓ = mais lock em alta
        self._steer_wheel  = 0.0
        self._steer        = 0.0

        self.counter_steer_assist   = 0.24       # ★ um pouco menor
        self.rear_grip_cut_hb       = 0.45
        self.rear_grip_cut_throttle = 0.97       # ★ quase não corta grip só por “dar pé”
        self.stability_k            = 0.043     # ★ damping lateral um pouco mais forte
        # ↑ (0.0033) = mais estável se parecer "sabão"; ↓ = menos damping

        # amortecimento de guinada
        self.yaw_damp_k      = 3.8              # ★ mais damping de yaw
        self.engine_yaw_push = 0.0006           # ★ menos empurrão de guinada do motor

        # Anti-pêndulo
        self._low_speed_thresh  = 1.2
        self._stop_snap_thresh  = 0.10

        # Turbo
        self.turbo_carga = 100.0
        self.turbo_ativo = False
        self._turbo_timer = 0.0
        self._turbo_cd    = 0.0
        self._turbo_mul   = 1.0

        # HUD/Efeitos
        self.emissor_nitro  = EmissorNitro()
        self.skidmarks      = GerenciadorSkidmarks()
        self.velocidade     = 0.0
        self.velocidade_kmh = 0.0
        self.marcha_atual   = 0
        self.rpm            = 0.0

        # Drift/handbrake
        self.drift_hold        = False
        self.drift_ativado     = False
        self.drifting          = False
        self.drift_intensidade = 0.0
        self._ultimo_skidmark  = 0.0  # Controle de frequência
        self.freio_mao_ativo   = False

        # --- Drift tuning (fechar curva) ---
        # === AJUSTES FINOS DE DRIFT ===
        # Para lapidar o comportamento do drift, ajuste estes valores:
        
        self.drift_front_bias   = 1.10  # ↑ grip dianteiro em drift (frente morde mais)
        # ↑ (1.12–1.15) = frente "morde" mais; ↓ se ficar "trocando de traseira"
        
        self.drift_rear_cut     = 0.72  # ↓ grip traseiro em drift (traseira mais solta)
        # ↑ (0.75–0.80) = traseira menos solta; ↓ = mais solta
        
        self.drift_long_damp    = 0.80  # fator por segundo na vel. longitudinal em drift
        # ↑ (0.88–0.92) = perde menos velocidade no drift (anda mais pra frente)
        # ↓ (0.80–0.85) = fecha mais a curva
        
        self.drift_yaw_boost    = 0.0009  # empurrão de guinada extra proporcional ao slip
        # ↓ (0.0007–0.0008) = gira menos; ↑ (0.0010) = gira mais

        # Internos
        self._bateu = False
        
        # Cache de performance
        self._vetor_frente_cache = None
        self._vetor_direita_cache = None
        self._angulo_cache = None
        self._sprite_rot_cache = None
        self._sprite_angulo_cache = None  # Inicializar como None para forçar primeiro cálculo

    # ---------------- Sprites ----------------
    def _carregar_sprite(self, prefixo_cor):
        caminho_sprite = os.path.join(DIR_SPRITES, f"{prefixo_cor}.png")
        sprite = pygame.image.load(caminho_sprite).convert_alpha()
        w0, h0 = sprite.get_size()
        # Tamanho original mantido
        area_max = 48 * 48
        aspect = w0 / max(1, h0)
        if aspect >= 1.0:
            w = int((area_max * aspect) ** 0.5); h = int(w / aspect)
        else:
            h = int((area_max / aspect) ** 0.5); w = int(h * aspect)
        w = min(w, 64); h = min(h, 64)
        # Usar smoothscale ao invés de scale para melhor qualidade de interpolação
        self.sprite_base = pygame.transform.smoothscale(sprite, (w, h))

    # ---------------- Bases / transformações ---------------- 
    def _vetor_frente(self):
        # Cache para evitar recálculos
        if self._angulo_cache != self.angulo:
            rad = math.radians(self.angulo)
            self._vetor_frente_cache = (-math.cos(rad), math.sin(rad))
            self._vetor_direita_cache = (self._vetor_frente_cache[1], -self._vetor_frente_cache[0])
            self._angulo_cache = self.angulo
        return self._vetor_frente_cache

    def _vetor_direita(self):
        # Usar cache
        if self._angulo_cache != self.angulo:
            self._vetor_frente()  # Atualiza ambos os caches
        return self._vetor_direita_cache

    def _mundo_para_local(self, vx, vy):
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        return vx * fx + vy * fy, vx * rx + vy * ry

    def _local_para_mundo(self, u, v):
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        return fx * u + rx * v, fy * u + ry * v

    # ---------------- Pneus / elipse ----------------
    def _tire_lateral(self, slip_angle, Ca, Fz, mu_lat=None):
        if mu_lat is None:
            mu_lat = self.mu_peak
        Fy_lin = Ca * math.tanh(slip_angle / self.alpha_sat)
        Fy_max = mu_lat * max(0.0, Fz)
        return max(-Fy_max, min(Fy_lin, Fy_max))

    def _ellipse_clamp(self, Fx, Fy, Fz):
        if Fz <= 0.0:
            return 0.0, 0.0
        ax = Fx / (self.mu_long * Fz)
        ay = Fy / (self.mu_peak * Fz)
        s = ax * ax + ay * ay
        if s <= 1.0:
            return Fx, Fy
        k = 1.0 / math.sqrt(max(1e-9, s))
        return Fx * k, Fy * k

    def _static_normal_loads(self):
        Fzf = self.m * self.g * (self.b / self.L)
        Fzr = self.m * self.g * (self.a / self.L)
        return Fzf, Fzr

    # ---------------- Métodos auxiliares ----------------
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

    def _corrigir_coordenadas_para_guide(self, x, y, camera, superficie_mascara):
        """Corrige as coordenadas para considerar o zoom da câmera no guide"""
        if camera is None:
            return x, y
        
        # Obter a visão atual da câmera
        visao = camera.ret_visao()
        
        # Aplicar o zoom da câmera para corrigir as coordenadas
        # Quando a câmera tem zoom > 1, as coordenadas precisam ser ajustadas
        zoom_factor = camera.zoom
        
        # Converter coordenadas do mundo para coordenadas da superfície do guide
        # considerando o offset da câmera
        x_corrigido = int((x - visao.left) * zoom_factor)
        y_corrigido = int((y - visao.top) * zoom_factor)
        
        # Garantir que as coordenadas estejam dentro dos limites da superfície
        x_corrigido = max(0, min(superficie_mascara.get_width() - 1, x_corrigido))
        y_corrigido = max(0, min(superficie_mascara.get_height() - 1, y_corrigido))
        
        return x_corrigido, y_corrigido

    # ---------------- Loop principal ----------------
    def atualizar(self, teclas, superficie_mascara, dt, camera=None, superficie_pista_renderizada=None):
        acelerar = teclas[self.controles[0]]
        direita  = teclas[self.controles[1]]
        esquerda = teclas[self.controles[2]]
        frear_re = teclas[self.controles[3]]

        turbo_pressed = False
        if self.turbo_key is not None:
            turbo_pressed = bool(teclas[self.turbo_key])

        self._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt, camera, superficie_pista_renderizada)

    def _step(self, acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt, camera=None, superficie_pista_renderizada=None):
        # Escalas arcade
        TIME_SCALE        = 2.9
        ARCADE_SPEED_MULT = 2.5
        dt_fis = dt * TIME_SCALE

        x_ant, y_ant = self.x, self.y

        # Turbo (HOLD)
        self.turbo_ativo = bool(turbo_pressed and self.turbo_carga > 0.0)

        # Decompõe velocidade
        v_long, v_lat = self._decomp_vel()

        # ======== DRIFT / ESTADO ========
        slip = math.degrees(math.atan2(v_lat, max(0.1, abs(v_long))))
        speed_abs = abs(v_long)

        # precisa de mais slip e mais velocidade para “armar”
        drifteando = (
            self.freio_mao_ativo or self.drift_ativado or
            (acelerar and (abs(slip) > 14.0) and speed_abs > 90.0)
        )

        # direção desejada
        steer_input = -1.0 if direita else (1.0 if esquerda else 0.0)
        # Remover inversão problemática que causa travamento em ré
        # if v_long < -0.25:
        #     steer_input = -steer_input

        # lock reduz com a velocidade
        lock_scale = max(0.20, 1.0 - self.speed_steer_k * abs(v_long))  # ★ um pouco mais agressivo
        target_wheel = self.steer_rad_max * lock_scale * steer_input

        # slewing da roda
        if target_wheel > self._steer_wheel:
            self._steer_wheel = min(self._steer_wheel + self.steer_rate*dt_fis, target_wheel)
        else:
            self._steer_wheel = max(self._steer_wheel - self.steer_rate*dt_fis, target_wheel)

        # centragem suave quando NÃO está derrapando (tira “nervosismo”)
        if not drifteando and abs(steer_input) < 0.5:            # ★
            self._steer_wheel += (-self._steer_wheel) * 2.0 * dt_fis  # ★

        # contra-esterço leve quando escorrega
        if abs(slip) > 9.0 and (acelerar or self.freio_mao_ativo or self.drift_ativado):
            target_counter = -math.radians(0.50 * slip)          # ★ um tico menos
            self._steer_wheel += self.counter_steer_assist * (target_counter - self._steer_wheel) * 6.0 * dt_fis

        # cargas
        Fzf, Fzr = self._static_normal_loads()

        # grip dependente da velocidade
        spd_k = min(1.0, speed_abs / 450.0)
        Cf_eff = self.Cf_base * (1.0 - 0.16*spd_k)               # ★ ligeiro ajuste
        Cr_eff = self.Cr_base * (1.0 - 0.04*spd_k)

        # fora do drift: mais grip e viés pró-traseira (estabilidade)
        escapando = (abs(slip) > 12.0) or self.freio_mao_ativo or self.drift_ativado
        if escapando:
            # solta traseira e dá mordida na dianteira → carro aponta melhor
            Cf_eff *= self.drift_front_bias
            Cr_eff *= self.drift_rear_cut
            if self.freio_mao_ativo:
                Cr_eff *= self.rear_grip_cut_hb
            if acelerar and abs(v_long) > 0.5:
                Cr_eff *= self.rear_grip_cut_throttle
        else:
            Cf_eff *= 1.12
            Cr_eff *= 1.18


        # power oversteer contido
        if (acelerar and abs(steer_input) > 0.15 and abs(v_long) > self.min_speed_oversteer):
            cut = 1.0 - self.power_oversteer_k * min(1.0, abs(steer_input))
            Cr_eff *= max(0.70, cut)  # ★ não deixa a traseira cair demais

        # slip por eixo
        r = self.yaw_rate
        alpha_f = self._steer_wheel - math.atan2(v_lat + self.a*r, max(0.1, abs(v_long)))
        alpha_r = - math.atan2(v_lat - self.b*r, max(0.1, abs(v_long)))

        # força lateral por eixo
        Fy_f = max(-self.mu_peak*Fzf, min(Cf_eff * math.tanh(alpha_f / self.alpha_sat),  self.mu_peak*Fzf))
        Fy_r = max(-self.mu_peak*Fzr, min(Cr_eff * math.tanh(alpha_r / self.alpha_sat),  self.mu_peak*Fzr))

        # --- Longitudinal ---
        thr = 1.0 if acelerar else 0.0
        brk = 1.0 if frear_re else 0.0

        # Turbo: aumentar significativamente a força do motor
        turbo_multiplier = TURBO_FATOR if self.turbo_ativo else 1.0
        Fx_long = self.engine_force_fwd * thr * turbo_multiplier
        
        # Boost adicional: reduzir resistência do arrasto quando turbo está ativo
        # Isso permite que o carro acelere mais e atinja velocidades maiores
        # A resistência será aplicada mais abaixo no código, mas aqui podemos ajustar

        # freio sempre contra o movimento
        if brk > 0.0:
            if abs(v_long) > 1.0:
                Fx_long += -math.copysign(self.brake_force, v_long) * brk
            else:
                Fx_long += -self.engine_force_rev * brk

        # ré -> frente com W (mata ré rápido)
        if v_long < 0.0 and thr > 0.0:
            if v_long < -1.0:
                Fx_long = +self.brake_force * 1.6
            else:
                Fx_long = +self.brake_force * 1.0

        # limite de ré
        if v_long < -self.V_TOP_REV:
            Fx_long = max(Fx_long, 0.0)
        if v_long < -self.V_TOP_REV * 1.05:
            Fx_long += self.brake_force * 0.6

        Fx_f, Fy_f = self._ellipse_clamp(0.0, Fy_f, Fzf)
        Fx_r, Fy_r = self._ellipse_clamp(Fx_long, Fy_r, Fzr)

        # somatório no chassi
        cs = math.cos(self._steer_wheel); sn = math.sin(self._steer_wheel)
        Fx = Fx_f*cs - Fy_f*sn + Fx_r
        Fy = Fy_f*cs + Fx_f*sn + Fy_r

        # resistências
        Fy += - self.stability_k * v_lat * (1.0 + 0.6*abs(v_long))
        # Reduzir arrasto quando turbo está ativo para permitir velocidades maiores
        drag_multiplier = 0.7 if self.turbo_ativo else 1.0  # 30% menos arrasto com turbo
        Fx += - self.drag * v_long * abs(v_long) * drag_multiplier - self.roll_res * v_long

        # integra (no frame do carro)
        v_long += (Fx / self.m + v_lat * r) * dt_fis
        v_lat  += (Fy / self.m - v_long * r) * dt_fis

        # Perda de velocidade só no drift para fechar a curva
        if escapando:
            # damping multiplicativo por segundo (ex.: 0.85 => -15%/s)
            v_long *= (self.drift_long_damp ** dt_fis)
            # opcional: "freio" linear leve (se quiser fechar ainda mais)
            # v_long -= 20.0 * dt_fis

    
        # anti-crab quando NÃO escapando (mais forte)
        if not escapando:
            v_lat -= v_lat * (2.6 + 0.008 * abs(v_long)) * dt_fis   # ★ mais sangria lateral
            if steer_input != 0.0:
                v_lat -= v_lat * (1.2 + 0.004 * abs(v_long)) * dt_fis  # ★

        # baixa velocidade: gira mais, desliza menos
        LOW_SPEED = 80.0
        if not escapando and abs(v_long) < LOW_SPEED:
            self.yaw_rate += (self.steer_rad_max * steer_input * 1.5 - self.yaw_rate) * 0.5 * dt_fis
            v_lat *= (1.0 - 10.0 * dt_fis)

        # --- soft limiter + clamp duro ---
        # Usar distância ao quadrado para evitar sqrt quando possível
        speed_sq = v_long*v_long + v_lat*v_lat
        speed = math.sqrt(speed_sq)
        if speed > self.V_SOFT:
            cut = (speed - self.V_SOFT) / max(1e-6, self.V_TOP - self.V_SOFT)
            v_long *= (1.0 - 0.25*cut)
            v_lat  *= (1.0 - 0.25*cut)
        if speed > self.V_TOP:
            esc = self.V_TOP / speed
            v_long *= esc
            v_lat  *= esc

        # torque de guinada + aligning torque
        Mz = self.a*(Fy_f*cs + Fx_f*sn) - self.b*Fy_r

        # guinada pelo motor (reduzido) - funcionar em ré também
        if thr > 0.2 and abs(steer_input) > 0.15:
            Mz += self.engine_yaw_push * self.engine_force_fwd * thr * math.copysign(1.0, steer_input)

        # aligning torque (um pouco mais forte sempre)
        align_k = (0.28 + 0.24*spd_k)     # ★
        Mz += -align_k * v_lat * max(60.0, abs(v_long))

        # Boost de guinada em drift (gira mais fácil e fecha o raio)
        if escapando:
            Mz += self.drift_yaw_boost * v_lat * (abs(v_long) + 60.0)


        # integra yaw + damping
        self.yaw_rate += (Mz / self.Iz) * dt_fis
        self.yaw_rate -= self.yaw_rate * self.yaw_damp_k * dt_fis   # ★

        # limite de yaw_rate mais baixo em alta
        spdf = min(1.0, abs(v_long) / 380.0)
        yaw_max = 3.2 - 1.4*spdf           # ★ menos giro máximo
        self.yaw_rate = max(-yaw_max, min(yaw_max, self.yaw_rate))

        # alinhar rotação ao esterço (blend menor durante drift)
        yaw_target = (v_long * math.tan(self._steer_wheel)) / max(0.1, self.L)
        blend = 0.7 if not escapando else 0.35
        self.yaw_rate += (yaw_target - self.yaw_rate) * blend * dt_fis

        # aplica ao ângulo do sprite
        self.angulo += math.degrees(self.yaw_rate) * dt_fis
        if self.angulo > 180: self.angulo -= 360
        if self.angulo < -180: self.angulo += 360

        # recompor mundo e avançar posição
        self._recomp_vel(v_long, v_lat)
        speed_mult = ARCADE_SPEED_MULT * (0.88 if escapando else 1.0)
        # Limitar movimento máximo por frame para evitar "blip" ou teleporte
        # Calcular movimento desejado
        dx = self.vx * dt_fis * speed_mult
        dy = self.vy * dt_fis * speed_mult
        # Limitar movimento máximo por frame (evitar saltos grandes)
        max_move_per_frame = 200.0 * dt_fis  # Limite razoável baseado em dt
        dist_movimento = math.sqrt(dx*dx + dy*dy)
        if dist_movimento > max_move_per_frame:
            # Normalizar e limitar
            scale = max_move_per_frame / dist_movimento
            dx *= scale
            dy *= scale
        self.x += dx
        self.y += dy


        # Sistema estilo GRIP - verificar se está na grama
        # No GRIP, você pode andar em qualquer lugar, mas na grama fica mais lento
        na_grama = False
        
        if superficie_pista_renderizada is not None:
            # Sistema GRIP: verificar se está na grama
            cx, cy = int(self.x), int(self.y)
            na_grama = verificar_na_grama_grip(superficie_pista_renderizada, cx, cy, raio=15)
            
            # Armazenar flag de grama para uso em pontuação
            self.na_grama = na_grama
            
            # Se está na grama, reduzir velocidade levemente (estilo GRIP)
            if na_grama:
                # Reduzir velocidade quando está na grama, mas não muito (usuário pediu um pouco mais rápido)
                # Aplicar leve redução de velocidade na grama
                v_long, v_lat = self._decomp_vel()
                
                # Reduzir velocidade longitudinal na grama (mas menos que antes)
                if v_long > 0:
                    v_long *= 0.97  # Reduzir velocidade em apenas 3% na grama (antes era 8%)
                elif v_long < 0:
                    v_long *= 0.97
                
                # Reduzir velocidade lateral também (menos que antes)
                v_lat *= 0.95  # Reduzir velocidade lateral em 5% (antes era 10%)
                
                self._recomp_vel(v_long, v_lat)
        
        # Colisão com a pista - Sistema antigo (compatibilidade)
        # No sistema GRIP, não há colisão, apenas redução de velocidade na grama
        houve_colisao = False
        
        if superficie_pista_renderizada is None:
            # Sistema antigo: usar mask para compatibilidade
            fx, fy = self._vetor_frente()
            dir_frente_x, dir_frente_y = fx, fy
            dir_direita_x, dir_direita_y = self._vetor_direita()

            cx, cy = int(self.x), int(self.y)
            colisao_count = 0
            total_amostras = 0
            
            # Mais amostras para melhor detecção, especialmente nas bordas
            amostras_local = [
                (0, 0),      # Centro
                (10, 0), (-10, 0), (0, 6), (0, -6),  # Pontos principais
                (6, 3), (-6, 3), (6, -3), (-6, -3),  # Pontos diagonais
                (15, 0), (-15, 0), (0, 9), (0, -9)   # Pontos externos
            ]
            
            for ox, oy in amostras_local:
                px = int(cx + ox * dir_frente_x + oy * dir_direita_x)
                py = int(cy + ox * dir_frente_y + oy * dir_direita_y)
                
                # Aplicar correção de coordenadas baseada na câmera se disponível
                if camera is not None:
                    px, py = self._corrigir_coordenadas_para_guide(px, py, camera, superficie_mascara)
                
                total_amostras += 1
                pass

        if houve_colisao:
            escape_x, escape_y = 0, 0
            fx, fy = self._vetor_frente()
            dir_frente_x, dir_frente_y = fx, fy
            dir_direita_x, dir_direita_y = self._vetor_direita()
            cx, cy = int(self.x), int(self.y)
            
            for ox, oy in [(10, 0), (-10, 0), (0, 6), (0, -6)]:
                px = int(cx + ox * dir_frente_x + oy * dir_direita_x)
                py = int(cy + ox * dir_frente_y + oy * dir_direita_y)
                
                if superficie_pista_renderizada is not None:
                    if eh_pixel_transitavel_grip(superficie_pista_renderizada, px, py):
                        escape_x += ox * 0.1
                        escape_y += oy * 0.1
            
            if escape_x != 0 or escape_y != 0:
                self.x += escape_x
                self.y += escape_y
            else:
                # Se não há direção de escape clara, voltar à posição anterior
                self.x, self.y = x_ant, y_ant
            
            # Reduzir velocidade de forma mais suave (estilo GRIP)
            # No GRIP, quando está na grama, a velocidade é reduzida
            self.vx *= -0.2
            self.vy *= -0.2
            
            # Aplicar damping adicional para evitar oscilações
            self.vx *= 0.8
            self.vy *= 0.8
            
            v_long, v_lat = self._decomp_vel()
            if v_long < -1.5:
                v_long = -1.5
            self._recomp_vel(v_long, v_lat)

        # Limites da área
        # Se estamos usando tiles (superfície grande), não limitar aos limites da tela
        # Os limites só se aplicam quando não estamos usando o sistema de tiles GRIP
        if superficie_pista_renderizada is None:
            # Sistema antigo: limitar aos limites da tela
            self.x = max(0.0, min(LARGURA * 1.0, self.x))
            self.y = max(0.0, min(ALTURA * 1.0, self.y))
        # Se usar tiles, não limitar (a pista é maior que a tela)

        # HUD - velocímetro mais fiel ao que anda na tela
        # v_long está em pixels/segundo (antes do multiplicador arcade)
        # O movimento aplica ARCADE_SPEED_MULT = 2.5, mas para o velocímetro
        # queremos mostrar a velocidade "real" que o jogador vê na tela
        # Calcular velocidade considerando o multiplicador arcade aplicado no movimento
        ARCADE_SPEED_MULT = 2.5
        velocidade_com_mult = abs(v_long) * ARCADE_SPEED_MULT
        
        # Converter para km/h: 
        # v_long está em px/s, e V_TOP = 750 px/s é o limite máximo teórico
        # Na prática, v_long real chega a valores menores devido às limitações físicas
        # Se o velocímetro está mostrando apenas 40 km/h como máxima, precisamos aumentar muito o fator
        # Ajustar para que velocidades típicas resultem em valores de 0-180 km/h
        # Se velocidade_com_mult típica é ~200 px/s e queremos mostrar até 180 km/h:
        # PXPS_TO_KMH = 180 / 200 = 0.9
        # Mas vamos usar um valor maior para garantir que chegue a 180 km/h mesmo em velocidades menores
        PXPS_TO_KMH = 1.0  # Aumentado drasticamente para que o velocímetro mostre valores corretos
        # Isso faz com que velocidade_com_mult de ~180 px/s resulte em 180 km/h
        self.velocidade_kmh = velocidade_com_mult * PXPS_TO_KMH
        self.velocidade = v_long  # mantém a telemetria longitudinal se precisar

        # Partículas & drift FX
        if MODO_DRIFT:
            # Usar a função dedicada para atualizar estado de drift
            self._atualizar_estado_drift(v_long, v_lat, dt_fis)
        
        # Atualizar skidmarks
        self.skidmarks.atualizar(dt_fis)

        # Turbo (hold) carga
        if self.turbo_ativo:
            self.turbo_carga = max(0.0, self.turbo_carga - 25.0 * dt_fis)
            fx, fy = self._vetor_frente()
            self.emissor_nitro.spawn(self.x, self.y, -fx, -fy, 50.0, dt_fis)
        else:
            self.turbo_carga = min(100.0, self.turbo_carga + 12.0 * dt_fis)


    def _verificar_colisao(self, superficie_mascara):
        return True

    def _atualizar_estado_drift(self, u, v, dt):
        vel_sq = u*u + v*v
        vel = math.sqrt(vel_sq) if vel_sq > 0.01 else 0.0
        slip = abs(math.degrees(math.atan2(v, max(0.1, abs(u)))))
        
        # Detecção de drift: handbrake ativo OU drift natural (extremamente sensível)
        self.drifting = self.freio_mao_ativo or (vel > 5.0 and (slip > 0.5 or abs(v) > 1.0))
        
        if self.drifting:
            # Se handbrake ativo, intensidade máxima; senão, baseada na velocidade
            if self.freio_mao_ativo:
                self.drift_intensidade = 1.0  # Intensidade máxima para handbrake
            else:
                self.drift_intensidade = min(1.0, abs(v) / 40.0)  # Mais sensível para intensidade
            
            # Criar skidmark quando derrapando (com controle de frequência otimizado)
            # Para bots, usar frequência menor para evitar lag (0.2s ao invés de 0.1s)
            frequencia_skidmark = 0.2 if hasattr(self, 'eh_bot') and self.eh_bot else 0.1
            if self._ultimo_skidmark > frequencia_skidmark:
                # Criar skidmarks dos 2 pneus traseiros paralelos
                fx, fy = self._vetor_frente()
                offset_tras = 12  # pixels atrás do carro (bem próximo)
                offset_lateral = 10  # pixels para os lados (bem próximo das quinas)
                
                # Pneu traseiro esquerdo
                pos_x_esq = self.x - fx * offset_tras - fy * offset_lateral
                pos_y_esq = self.y - fy * offset_tras + fx * offset_lateral
                self.skidmarks.adicionar_skidmark(pos_x_esq, pos_y_esq, self.angulo, self.drift_intensidade, "traseiro_esq", na_grama=self.na_grama)
                
                # Pneu traseiro direito
                pos_x_dir = self.x - fx * offset_tras + fy * offset_lateral
                pos_y_dir = self.y - fy * offset_tras - fx * offset_lateral
                self.skidmarks.adicionar_skidmark(pos_x_dir, pos_y_dir, self.angulo, self.drift_intensidade, "traseiro_dir", na_grama=self.na_grama)
                
                # Se muito angular, criar marcas dos pneus dianteiros também
                # Para bots, apenas criar pneus dianteiros em ângulos muito grandes (otimização)
                angulo_minimo_dianteiro = 1.0 if (hasattr(self, 'eh_bot') and self.eh_bot) else 0.5
                if abs(self.angulo) > angulo_minimo_dianteiro:
                    offset_frente = 10  # pixels na frente do carro (bem próximo)
                    
                    # Pneu dianteiro esquerdo
                    pos_x_frente_esq = self.x + fx * offset_frente - fy * offset_lateral
                    pos_y_frente_esq = self.y + fy * offset_frente + fx * offset_lateral
                    self.skidmarks.adicionar_skidmark(pos_x_frente_esq, pos_y_frente_esq, self.angulo, self.drift_intensidade * 0.7, "dianteiro_esq", na_grama=self.na_grama)
                    
                    # Pneu dianteiro direito
                    pos_x_frente_dir = self.x + fx * offset_frente + fy * offset_lateral
                    pos_y_frente_dir = self.y + fy * offset_frente - fx * offset_lateral
                    self.skidmarks.adicionar_skidmark(pos_x_frente_dir, pos_y_frente_dir, self.angulo, self.drift_intensidade * 0.7, "dianteiro_dir", na_grama=self.na_grama)
                
                self._ultimo_skidmark = 0.0
        else:
            self.drift_intensidade *= 0.95
            # Parar o rastro quando não estiver derrapando
            self.skidmarks.parar_rastro()
        
        # Atualizar timer de skidmark
        self._ultimo_skidmark += dt

    def _atualizar_velocimetro(self, u, dt):
        PXPS_TO_KMH = 0.35
        self.velocidade_kmh = abs(u) * PXPS_TO_KMH
        if u > 0:
            self.rpm = min(8200, 1000 + (self.velocidade_kmh * 85))
            if   self.velocidade_kmh < 10: self.marcha_atual = 1
            elif self.velocidade_kmh < 20: self.marcha_atual = 2
            elif self.velocidade_kmh < 35: self.marcha_atual = 3
            elif self.velocidade_kmh < 55: self.marcha_atual = 4
            elif self.velocidade_kmh < 75: self.marcha_atual = 5
            else:                           self.marcha_atual = 6
        elif u < 0:
            self.rpm = min(4500, 800 + (self.velocidade_kmh * 45))
            self.marcha_atual = -1
        else:
            self.rpm = 800
            self.marcha_atual = 0

    # ---------------- Render ----------------
    def desenhar(self, superficie, camera=None):
        if camera is None:
            # Cache de sprite rotacionado
            # Arredondar ângulo para evitar recálculos frequentes que causam "flicando"
            angulo_arredondado = round(self.angulo, 1)  # Arredondar para 1 casa decimal
            if self._sprite_angulo_cache is None or self._sprite_angulo_cache != angulo_arredondado:
                # Usar rotozoom com zoom=1.0 para melhor qualidade na rotação
                self._sprite_rot_cache = pygame.transform.rotozoom(self.sprite_base, self.angulo, 1.0)
                self._sprite_angulo_cache = angulo_arredondado
            sprite_rot = self._sprite_rot_cache
            rect = sprite_rot.get_rect(center=(self.x, self.y))
            superficie.blit(sprite_rot, rect.topleft)
            self.emissor_nitro.draw(superficie, camera)
            return
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        # Cache com zoom (mais complexo, mas ainda vale a pena)
        # Usar precisão menor no cache para evitar recálculos frequentes que causam "flicando"
        # Arredondar ângulo e zoom para reduzir recálculos
        angulo_arredondado = round(self.angulo, 1)  # Arredondar para 1 casa decimal
        zoom_arredondado = round(camera.zoom, 2)  # Arredondar para 2 casas decimais
        cache_key = (angulo_arredondado, zoom_arredondado)
        if self._sprite_angulo_cache is None or self._sprite_angulo_cache != cache_key:
            # rotozoom já usa interpolação suave, mas vamos garantir qualidade
            # Se o zoom for muito diferente de 1.0, pode causar perda de qualidade
            # Vamos usar rotozoom que já tem boa qualidade
            self._sprite_rot_cache = pygame.transform.rotozoom(self.sprite_base, self.angulo, camera.zoom)
            self._sprite_angulo_cache = cache_key
        sprite_rot = self._sprite_rot_cache
        rect = sprite_rot.get_rect(center=(sx, sy))
        # Usar blit com flags para melhor qualidade (se disponível)
        superficie.blit(sprite_rot, rect.topleft)
        self.emissor_nitro.draw(superficie, camera)

    # ---------------- API extra ----------------
    def usar_turbo(self):
        if self._turbo_cd > 0.0:
            return
        u, v = self._mundo_para_local(self.vx, self.vy)
        u += TURBO_FORCA_IMPULSO
        self.vx, self.vy = self._local_para_mundo(u, v)
        self.v_long, self.v_lat = self._mundo_para_local(self.vx, self.vy)
        self._turbo_timer = TURBO_DURACAO_S
        self._turbo_mul   = TURBO_FATOR
        self._turbo_cd    = TURBO_COOLDOWN_S

    def ativar_drift(self, teclas=None):
        if "IA" in self.nome:
            return
        self.freio_mao_ativo = True
        self.drift_ativado   = True

    def desativar_drift(self):
        self.freio_mao_ativo = False
        self.drift_ativado   = False
