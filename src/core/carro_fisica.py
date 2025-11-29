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

    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None, nome=None, tipo_tracao=None, upgrades=None, multiplicador_base=1.0):
        self.x = float(x); self.y = float(y)
        self.angulo = 0.0
        self.vx = 0.0; self.vy = 0.0
        self.r  = 0.0
        self.na_grama = False

        self.v_long = 0.0
        self.v_lat  = 0.0
        self.yaw_rate = 0.0

        self.controles = controles
        self.turbo_key = KEY_NAME_TO_CONST.get(turbo_key) if isinstance(turbo_key, str) else turbo_key
        self.nome = nome or f"Carro {prefixo_cor}"
        self.tipo_tracao = tipo_tracao or self.TRACAO_TRASEIRA
        self.prefixo_cor = prefixo_cor
        self.multiplicador_base = multiplicador_base
        self._carregar_sprite(prefixo_cor)

        self.m  = 1200.0
        self.g  = 9.81
        self.L  = 2.5
        self.b  = 1.55
        self.a  = self.L - self.b
        self.Iz = 2400.0

        self.Cf_base = (35000.0 if self.tipo_tracao != self.TRACAO_TRASEIRA else 34000.0) * self.multiplicador_base
        self.Cr_base = (25000.0 if self.tipo_tracao != self.TRACAO_TRASEIRA else 24000.0) * self.multiplicador_base
        self.mu_peak   = 0.75 + (self.multiplicador_base - 1.0) * 0.15
        self.mu_long   = 0.70 + (self.multiplicador_base - 1.0) * 0.15
        self.alpha_sat = math.radians(12.5)

        self.engine_force    = 6000.0 * self.multiplicador_base
        self.brake_force     = 5500.0 * self.multiplicador_base
        self.handbrake_force = 6000.0 * self.multiplicador_base
        self.drag            = 0.0003 / self.multiplicador_base
        self.roll_res        = 0.03 / self.multiplicador_base
        self.downforce_k     = 0.0
        self.friction_base   = 0.03 / self.multiplicador_base

        self.engine_force_fwd = 80000.0 * self.multiplicador_base
        self.engine_force_rev = 4000.0 * self.multiplicador_base
        self.V_TOP_REV        = 16.0 * self.multiplicador_base

        self.power_oversteer_k = 0.12
        self.min_speed_oversteer = 100.0

        self.V_TOP  = 400.0 * self.multiplicador_base
        self.V_SOFT = 0.95 * self.V_TOP

        self.steer_rad_max = math.radians(42.0)
        self.steer_rate    = math.radians(520.0)
        self.speed_steer_k = 0.016
        self._steer_wheel  = 0.0
        self._steer        = 0.0

        self.counter_steer_assist   = 0.24
        self.rear_grip_cut_hb       = 0.45
        self.rear_grip_cut_throttle = 0.97
        self.stability_k            = 0.043

        self.yaw_damp_k      = 3.8
        self.engine_yaw_push = 0.0006

        self._low_speed_thresh  = 1.2
        self._stop_snap_thresh  = 0.10

        nivel_nitro_inicial = upgrades.get('nitro', 0) if upgrades else 0
        self.turbo_carga = 100.0 if nivel_nitro_inicial > 0 else 0.0
        self.turbo_ativo = False
        self._turbo_timer = 0.0
        self._turbo_cd    = 0.0
        self._turbo_mul   = 1.0
        self._turbo_duracao_base = 0.9
        self._turbo_cooldown_base = 2.5
        self._turbo_forca_base = 1.5
        
        self.nivel_motor_inicial = upgrades.get('motor', 0) if upgrades else 0
        
        if upgrades:
            self.aplicar_upgrades(upgrades)

        self.emissor_nitro  = EmissorNitro()
        self.skidmarks      = GerenciadorSkidmarks()
        self.velocidade     = 0.0
        self.velocidade_kmh = 0.0
        self.marcha_atual   = 0
        self.rpm            = 0.0

        self.drift_hold        = False
        self.drift_ativado     = False
        self.drifting          = False
        self.drift_intensidade = 0.0
        self._ultimo_skidmark  = 0.0
        self.freio_mao_ativo   = False

        self.drift_front_bias   = 1.10
        self.drift_rear_cut     = 0.72
        self.drift_long_damp    = 0.80
        self.drift_yaw_boost    = 0.0009

        self._bateu = False
        
        self._vetor_frente_cache = None
        self._vetor_direita_cache = None
        self._angulo_cache = None
        self._sprite_rot_cache = None
        self._sprite_angulo_cache = None
    
    def aplicar_upgrades(self, upgrades):
        """Aplica upgrades ao carro. upgrades é um dict {tipo: nivel} onde nivel é 0-5"""
        from config import TURBO_FORCA_IMPULSO, TURBO_DURACAO_S, TURBO_COOLDOWN_S
        
        nivel_motor = upgrades.get('motor', 0)
        nivel_filtro_ar = upgrades.get('filtro_ar', 0)
        nivel_ecu = upgrades.get('ecu', 0)
        nivel_transmissao = upgrades.get('transmissao', 0)
        nivel_rodas = upgrades.get('rodas', 0)
        nivel_suspensao = upgrades.get('suspensao', 0)
        nivel_nitro = upgrades.get('nitro', 0)
        
        self.nivel_motor_inicial = nivel_motor
        
        mult_motor = 1.0 + (nivel_motor * 0.25)
        self.engine_force_fwd *= mult_motor
        self.engine_force_rev *= mult_motor
        self.engine_force *= mult_motor
        self.V_TOP *= 1.0 + (nivel_motor * 0.15)
        self.V_SOFT = 0.95 * self.V_TOP
        
        mult_filtro = 1.0 + (nivel_filtro_ar * 0.18)
        self.engine_force_fwd *= 1.0 + (nivel_filtro_ar * 0.12)
        self.engine_force_rev *= 1.0 + (nivel_filtro_ar * 0.12)
        self.drag *= 1.0 - (nivel_filtro_ar * 0.05)
        
        mult_ecu = 1.0 + (nivel_ecu * 0.15)
        self.engine_force_fwd *= 1.0 + (nivel_ecu * 0.10)
        self.steer_rate *= 1.0 + (nivel_ecu * 0.08)
        
        mult_trans = 1.0 + (nivel_transmissao * 0.12)
        self.engine_force_fwd *= 1.0 + (nivel_transmissao * 0.08)
        self.V_TOP *= 1.0 + (nivel_transmissao * 0.10)
        self.V_SOFT = 0.95 * self.V_TOP
        
        mult_rodas = 1.0 + (nivel_rodas * 0.18)
        self.Cf_base *= mult_rodas
        self.Cr_base *= mult_rodas
        mu_peak_base = 0.75 + (self.multiplicador_base - 1.0) * 0.15
        mu_long_base = 0.70 + (self.multiplicador_base - 1.0) * 0.15
        self.mu_peak = min(1.05, mu_peak_base + (nivel_rodas * 0.06))
        self.mu_long = min(1.00, mu_long_base + (nivel_rodas * 0.06))
        self.stability_k *= 1.0 + (nivel_rodas * 0.10)
        
        mult_suspensao = 1.0 + (nivel_suspensao * 0.16)
        self.stability_k *= 1.0 + (nivel_suspensao * 0.12)
        self.yaw_damp_k *= 1.0 + (nivel_suspensao * 0.08)
        self.counter_steer_assist *= 1.0 + (nivel_suspensao * 0.10)
        
        if nivel_nitro > 0 and self.turbo_carga == 0.0:
            self.turbo_carga = 100.0
        
        mult_nitro = 1.0 + (nivel_nitro * 0.20)
        self._turbo_forca_base = TURBO_FORCA_IMPULSO * mult_nitro
        self._turbo_duracao_base = TURBO_DURACAO_S * (1.0 + nivel_nitro * 0.15)
        self._turbo_cooldown_base = TURBO_COOLDOWN_S * (1.0 - nivel_nitro * 0.10)

    def _carregar_sprite(self, prefixo_cor):
        caminho_sprite = os.path.join(DIR_SPRITES, f"{prefixo_cor}.png")
        sprite = pygame.image.load(caminho_sprite).convert_alpha()
        w0, h0 = sprite.get_size()
        area_max = 48 * 48
        aspect = w0 / max(1, h0)
        if aspect >= 1.0:
            w = int((area_max * aspect) ** 0.5); h = int(w / aspect)
        else:
            h = int((area_max / aspect) ** 0.5); w = int(h * aspect)
        w = min(w, 64); h = min(h, 64)
        self.sprite_base = pygame.transform.smoothscale(sprite, (w, h))

    def _vetor_frente(self):
        if self._angulo_cache != self.angulo:
            rad = math.radians(self.angulo)
            self._vetor_frente_cache = (-math.cos(rad), math.sin(rad))
            self._vetor_direita_cache = (self._vetor_frente_cache[1], -self._vetor_frente_cache[0])
            self._angulo_cache = self.angulo
        return self._vetor_frente_cache

    def _vetor_direita(self):
        if self._angulo_cache != self.angulo:
            self._vetor_frente()
        return self._vetor_direita_cache

    def _mundo_para_local(self, vx, vy):
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        return vx * fx + vy * fy, vx * rx + vy * ry

    def _local_para_mundo(self, u, v):
        fx, fy = self._vetor_frente()
        rx, ry = self._vetor_direita()
        return fx * u + rx * v, fy * u + ry * v

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
        
        visao = camera.ret_visao()
        zoom_factor = camera.zoom
        
        x_corrigido = int((x - visao.left) * zoom_factor)
        y_corrigido = int((y - visao.top) * zoom_factor)
        
        x_corrigido = max(0, min(superficie_mascara.get_width() - 1, x_corrigido))
        y_corrigido = max(0, min(superficie_mascara.get_height() - 1, y_corrigido))
        
        return x_corrigido, y_corrigido

    def atualizar(self, teclas, superficie_mascara, dt, camera=None, superficie_pista_renderizada=None, inputs_controle=None, player_id=None):
        """
        Atualiza o carro com inputs de teclado ou controle
        
        Args:
            teclas: dict de teclas pressionadas (pygame.key.get_pressed())
            superficie_mascara: máscara de colisão
            dt: delta time
            camera: câmera do jogo
            superficie_pista_renderizada: superfície da pista
            inputs_controle: dict com inputs de controle {"acelerar", "frear", "direita", "esquerda", "turbo"}
            player_id: "p1" ou "p2" para identificar qual tecla de freio de mão usar no teclado
        """
        if inputs_controle is not None:
            acelerar = inputs_controle.get("acelerar", False)
            direita = inputs_controle.get("direita", False)
            esquerda = inputs_controle.get("esquerda", False)
            frear_re = inputs_controle.get("frear", False)
            turbo_pressed = inputs_controle.get("turbo", False)
            freio_mao_pressed = inputs_controle.get("freio_mao", False)
            drift_pressed = inputs_controle.get("drift", False)
        else:
            acelerar = teclas[self.controles[0]]
            direita  = teclas[self.controles[1]]
            esquerda = teclas[self.controles[2]]
            frear_re = teclas[self.controles[3]]

            turbo_pressed = False
            if self.turbo_key is not None:
                turbo_pressed = bool(teclas[self.turbo_key])
            
            freio_mao_pressed = False
            if player_id == "p1":
                freio_mao_pressed = teclas[pygame.K_SPACE]
            elif player_id == "p2":
                freio_mao_pressed = teclas[pygame.K_KP0]
            drift_pressed = False

        if freio_mao_pressed or drift_pressed:
            self.ativar_drift()
        else:
            self.desativar_drift()

        self._step(acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt, camera, superficie_pista_renderizada)

    def _step(self, acelerar, direita, esquerda, frear_re, turbo_pressed, superficie_mascara, dt, camera=None, superficie_pista_renderizada=None):
        TIME_SCALE        = 2.9
        ARCADE_SPEED_MULT = 2.5
        dt_fis = dt * TIME_SCALE

        x_ant, y_ant = self.x, self.y

        self.turbo_ativo = bool(turbo_pressed and self.turbo_carga > 0.0)

        na_grama = False
        if superficie_pista_renderizada is not None:
            cx, cy = int(self.x), int(self.y)
            na_grama = verificar_na_grama_grip(superficie_pista_renderizada, cx, cy, raio=15)
            self.na_grama = na_grama

        v_long, v_lat = self._decomp_vel()

        slip = math.degrees(math.atan2(v_lat, max(0.1, abs(v_long))))
        speed_abs = abs(v_long)

        drifteando = (
            self.freio_mao_ativo or self.drift_ativado or
            (acelerar and (abs(slip) > 14.0) and speed_abs > 90.0)
        )

        steer_input = -1.0 if direita else (1.0 if esquerda else 0.0)
        
        try:
            from core.status_jogador import status_jogador
            multiplicador_controle = status_jogador.obter_multiplicador_controle()
            steer_input *= multiplicador_controle
        except Exception as e:
            pass
        
        esta_em_re = v_long < 0.0
        if esta_em_re:
            steer_input = -steer_input

        if v_long < 0.0:
            lock_scale = max(0.70, 1.0 - self.speed_steer_k * abs(v_long) * 0.3)
        else:
            lock_scale = max(0.20, 1.0 - self.speed_steer_k * abs(v_long))
        target_wheel = self.steer_rad_max * lock_scale * steer_input

        if target_wheel > self._steer_wheel:
            self._steer_wheel = min(self._steer_wheel + self.steer_rate*dt_fis, target_wheel)
        else:
            self._steer_wheel = max(self._steer_wheel - self.steer_rate*dt_fis, target_wheel)

        if not drifteando and abs(steer_input) < 0.5:
            self._steer_wheel += (-self._steer_wheel) * 2.0 * dt_fis

        if abs(slip) > 9.0 and (acelerar or self.freio_mao_ativo or self.drift_ativado):
            target_counter = -math.radians(0.50 * slip)
            self._steer_wheel += self.counter_steer_assist * (target_counter - self._steer_wheel) * 6.0 * dt_fis

        Fzf, Fzr = self._static_normal_loads()

        spd_k = min(1.0, speed_abs / 450.0)
        Cf_eff = self.Cf_base * (1.0 - 0.16*spd_k)
        Cr_eff = self.Cr_base * (1.0 - 0.04*spd_k)

        escapando = (abs(slip) > 12.0) or self.freio_mao_ativo or self.drift_ativado
        if escapando:
            Cf_eff *= self.drift_front_bias
            Cr_eff *= self.drift_rear_cut
            if self.freio_mao_ativo:
                Cr_eff *= self.rear_grip_cut_hb
            if acelerar and abs(v_long) > 0.5:
                Cr_eff *= self.rear_grip_cut_throttle
        else:
            Cf_eff *= 1.12
            Cr_eff *= 1.18

        if (acelerar and abs(steer_input) > 0.15 and abs(v_long) > self.min_speed_oversteer):
            cut = 1.0 - self.power_oversteer_k * min(1.0, abs(steer_input))
            Cr_eff *= max(0.70, cut)

        r = self.yaw_rate
        alpha_f = self._steer_wheel - math.atan2(v_lat + self.a*r, max(0.1, abs(v_long)))
        alpha_r = - math.atan2(v_lat - self.b*r, max(0.1, abs(v_long)))

        Fy_f = max(-self.mu_peak*Fzf, min(Cf_eff * math.tanh(alpha_f / self.alpha_sat),  self.mu_peak*Fzf))
        Fy_r = max(-self.mu_peak*Fzr, min(Cr_eff * math.tanh(alpha_r / self.alpha_sat),  self.mu_peak*Fzr))

        thr = 1.0 if acelerar else 0.0
        brk = 1.0 if frear_re else 0.0

        if self.turbo_ativo:
            turbo_multiplier = TURBO_FATOR
        else:
            turbo_multiplier = 1.0
        
        esta_tentando_re = brk > 0.0
        
        if na_grama:
            velocidade_atual_temp = math.sqrt(v_long*v_long + v_lat*v_lat)
            ARCADE_SPEED_MULT = 2.5
            PXPS_TO_KMH = 1.0
            velocidade_kmh_temp = velocidade_atual_temp * ARCADE_SPEED_MULT * PXPS_TO_KMH
            
            if esta_tentando_re:
                limite_kmh = 50.0
                if velocidade_kmh_temp <= limite_kmh:
                    fator_grama = 0.90
                else:
                    excesso = velocidade_kmh_temp - limite_kmh
                    fator_grama = max(0.60, 0.90 - (excesso / 10.0) * 0.30)
            else:
                limite_kmh = 100.0
                if velocidade_kmh_temp <= limite_kmh:
                    fator_grama = 0.35
                else:
                    excesso = velocidade_kmh_temp - limite_kmh
                    fator_grama = max(0.15, 0.35 - (excesso / 15.0) * 0.20)
        else:
            fator_grama = 1.0
        Fx_long = self.engine_force_fwd * thr * turbo_multiplier * fator_grama

        if brk > 0.0:
            if v_long < 0.0:
                if na_grama and esta_tentando_re:
                    fator_grama_rev = fator_grama
                else:
                    fator_grama_rev = 1.0
                Fx_long += -self.engine_force_rev * brk * fator_grama_rev
            elif abs(v_long) > 1.0:
                Fx_long += -math.copysign(self.brake_force, v_long) * brk
            else:
                if na_grama and esta_tentando_re:
                    fator_grama_rev = fator_grama
                else:
                    fator_grama_rev = 1.0
                Fx_long += -self.engine_force_rev * brk * fator_grama_rev

        if v_long < 0.0 and thr > 0.0:
            velocidade_re_abs = abs(v_long)
            if velocidade_re_abs > 1.0:
                fator_freio_re = min(2.0, 1.0 + velocidade_re_abs / 10.0)
                Fx_long = +self.brake_force * fator_freio_re
            else:
                Fx_long = +self.brake_force * 1.0

        if v_long < 0.0:
            velocidade_total_pxps = math.sqrt(v_long*v_long + v_lat*v_lat)
            ARCADE_SPEED_MULT = 2.5
            PXPS_TO_KMH = 1.0
            velocidade_rev_kmh = velocidade_total_pxps * ARCADE_SPEED_MULT * PXPS_TO_KMH
            
            VEL_ALVO_KMH = 38.0
            VEL_INICIO_LIMITE_KMH = 35.0
            VEL_MAX_KMH = 45.0
            
            if velocidade_rev_kmh > VEL_INICIO_LIMITE_KMH:
                if velocidade_rev_kmh < VEL_ALVO_KMH:
                    progresso = (velocidade_rev_kmh - VEL_INICIO_LIMITE_KMH) / (VEL_ALVO_KMH - VEL_INICIO_LIMITE_KMH)
                    fator_forca = 1.0 - progresso * 0.5
                else:
                    excesso = velocidade_rev_kmh - VEL_ALVO_KMH
                    max_excesso = VEL_MAX_KMH - VEL_ALVO_KMH
                    fator_forca = 0.5 - (excesso / max_excesso) * 0.4
                    fator_forca = max(0.1, fator_forca)
                
                if brk > 0.0:
                    Fx_long *= fator_forca

        Fx_f, Fy_f = self._ellipse_clamp(0.0, Fy_f, Fzf)
        Fx_r, Fy_r = self._ellipse_clamp(Fx_long, Fy_r, Fzr)

        # somatório no chassi
        cs = math.cos(self._steer_wheel); sn = math.sin(self._steer_wheel)
        Fx = Fx_f*cs - Fy_f*sn + Fx_r
        Fy = Fy_f*cs + Fx_f*sn + Fy_r
        
        # Prevenir aceleração quando apenas direção é pressionada (sem acelerar ou frear)
        # Se não há aceleração nem freio E o carro está parado ou quase parado,
        # não deve haver força longitudinal resultante da direção
        # IMPORTANTE: Não aplicar quando está dando ré (brk > 0.0), pois ré precisa funcionar
        velocidade_atual = math.sqrt(v_long*v_long + v_lat*v_lat)
        if thr == 0.0 and brk == 0.0 and velocidade_atual < 5.0:
            # Remover componente longitudinal que vem da força lateral ao virar
            # Isso previne que o carro acelere para o lado quando apenas A ou D são pressionados
            Fx = 0.0

        # resistências
        Fy += - self.stability_k * v_lat * (1.0 + 0.6*abs(v_long))
        # Reduzir arrasto quando turbo está ativo para permitir velocidades maiores
        drag_multiplier = 0.05 if self.turbo_ativo else 1.0  # 95% menos arrasto com turbo (EXTREMAMENTE poderoso)
        # Aumentar arrasto na grama de forma significativa e progressiva
        # Menos arrasto para ré do que para frente
        if na_grama:
            # Calcular velocidade atual para ajustar arrasto dinamicamente
            v_long_atual, v_lat_atual = self._decomp_vel()
            esta_em_re_arrasto = v_long_atual < 0.0 or brk > 0.0
            velocidade_atual_grama = math.sqrt(v_long_atual*v_long_atual + v_lat_atual*v_lat_atual)
            ARCADE_SPEED_MULT = 2.5
            PXPS_TO_KMH = 1.0
            velocidade_kmh_atual = velocidade_atual_grama * ARCADE_SPEED_MULT * PXPS_TO_KMH
            
            if esta_em_re_arrasto:
                # Ré: arrasto muito menor na grama (1.2x base)
                # Acima de 50 km/h: aumentar progressivamente
                fator_arrasto_base = 1.2
                if velocidade_kmh_atual > 50.0:
                    excesso = velocidade_kmh_atual - 50.0
                    # Aumentar de 1.2x para até 1.8x conforme excesso
                    fator_arrasto_extra = min(0.6, excesso / 15.0)  # Máximo de 0.6 extra
                    fator_arrasto_base += fator_arrasto_extra
            else:
                # Frente: arrasto significativo na grama (2.0x base)
                # Acima de 100 km/h: aumentar progressivamente
                fator_arrasto_base = 2.0
                if velocidade_kmh_atual > 100.0:
                    excesso = velocidade_kmh_atual - 100.0
                    # Aumentar de 2.0x para até 3.5x conforme excesso
                    fator_arrasto_extra = min(1.5, excesso / 10.0)  # Máximo de 1.5 extra
                    fator_arrasto_base += fator_arrasto_extra
            drag_multiplier *= fator_arrasto_base
        # Aplicar arrasto e resistência ao rolamento
        # Reduzir resistência ao rolamento para ré (mais permissivo)
        roll_res_multiplier = 0.3 if v_long < 0.0 else 1.0  # 70% menos resistência na ré
        Fx += - self.drag * v_long * abs(v_long) * drag_multiplier - self.roll_res * v_long * roll_res_multiplier
        
        # Atrito de rolamento base (sempre ativo, faz desacelerar naturalmente)
        # Aplicar força de atrito proporcional à velocidade, mas menos agressivo em velocidades altas
        # Com turbo ativo, reduzir atrito significativamente
        if abs(v_long) > 0.1:  # Apenas se estiver se movendo
            # Atrito base: força oposta ao movimento
            # Reduzir atrito em velocidades altas para não limitar velocidade máxima
            # Em baixas velocidades: atrito normal, em altas: atrito reduzido
            speed_factor = 1.0
            if abs(v_long) > 100.0:  # Acima de ~100 px/s (começar a reduzir atrito mais cedo)
                # Reduzir atrito progressivamente em velocidades altas
                excesso = abs(v_long) - 100.0
                speed_factor = max(0.2, 1.0 - (excesso / 200.0) * 0.8)  # Reduzir até 20% do atrito
            
            # Com turbo ativo, reduzir atrito ainda mais (95% menos atrito)
            if self.turbo_ativo:
                speed_factor *= 0.05  # Reduzir atrito para 5% do normal com turbo (quase zero)
            
            friction_force = -math.copysign(self.friction_base * abs(v_long) * self.m * speed_factor, v_long)
            Fx += friction_force

        # integra (no frame do carro)
        v_long += (Fx / self.m + v_lat * r) * dt_fis
        v_lat  += (Fy / self.m - v_long * r) * dt_fis

        # Limitar velocidade total de ré após integração (previne bug ao virar)
        if v_long < 0.0:
            # Calcular velocidade total (magnitude) em km/h
            velocidade_total_pxps = math.sqrt(v_long*v_long + v_lat*v_lat)
            ARCADE_SPEED_MULT = 2.5
            PXPS_TO_KMH = 1.0
            velocidade_rev_kmh = velocidade_total_pxps * ARCADE_SPEED_MULT * PXPS_TO_KMH
            VEL_MAX_KMH = 45.0
            
            if velocidade_rev_kmh > VEL_MAX_KMH:
                velocidade_max_pxps = VEL_MAX_KMH / (ARCADE_SPEED_MULT * PXPS_TO_KMH)
                fator_reducao_vel = velocidade_max_pxps / velocidade_total_pxps
                v_long *= fator_reducao_vel
                v_lat *= fator_reducao_vel
                self._recomp_vel(v_long, v_lat)

        if escapando:
            v_long *= (self.drift_long_damp ** dt_fis)

        if not escapando:
            v_lat -= v_lat * (2.6 + 0.008 * abs(v_long)) * dt_fis
            if steer_input != 0.0:
                v_lat -= v_lat * (1.2 + 0.004 * abs(v_long)) * dt_fis

        LOW_SPEED = 80.0
        if not escapando and abs(v_long) < LOW_SPEED:
            self.yaw_rate += (self.steer_rad_max * steer_input * 1.5 - self.yaw_rate) * 0.5 * dt_fis
            v_lat *= (1.0 - 10.0 * dt_fis)

        speed_sq = v_long*v_long + v_lat*v_lat
        speed = math.sqrt(speed_sq)
        
        if self.turbo_ativo:
            multiplicador_base = self.multiplicador_base
            nivel_motor = getattr(self, 'nivel_motor_inicial', 0)
            
            V_TOP_base_calc = 400.0 * (1.0 + (multiplicador_base - 1.0) * 0.08)
            V_TOP_calc = V_TOP_base_calc * (1.0 + nivel_motor * 0.10)
            
            eficiencia_base_primeiro = 0.14
            eficiencia_base = eficiencia_base_primeiro - (multiplicador_base - 1.0) * 0.005
            fator_eficiencia_base = max(0.12, eficiencia_base)
            bonus_motor = nivel_motor * 0.004
            fator_eficiencia = min(0.20, fator_eficiencia_base + bonus_motor)
            
            vel_max_real_pxps = V_TOP_calc * fator_eficiencia
            
            ARCADE_SPEED_MULT = 2.5
            PXPS_TO_KMH = 1.0
            vel_max_real_kmh = vel_max_real_pxps * ARCADE_SPEED_MULT * PXPS_TO_KMH
            
            vel_max_nitro_kmh = vel_max_real_kmh * 1.20
            vel_max_nitro_pxps = (vel_max_nitro_kmh / (ARCADE_SPEED_MULT * PXPS_TO_KMH))
            
            V_SOFT_TURBO = vel_max_real_pxps * 1.10
            V_TOP_TURBO = vel_max_nitro_pxps
            
            if speed > V_SOFT_TURBO:
                cut = (speed - V_SOFT_TURBO) / max(1e-6, V_TOP_TURBO - V_SOFT_TURBO)
                v_long *= (1.0 - 0.15*cut)
                v_lat  *= (1.0 - 0.15*cut)
            if speed > V_TOP_TURBO:
                esc = V_TOP_TURBO / speed
                v_long *= esc
                v_lat  *= esc
        else:
            if speed > self.V_SOFT:
                cut = (speed - self.V_SOFT) / max(1e-6, self.V_TOP - self.V_SOFT)
                v_long *= (1.0 - 0.10*cut)
                v_lat  *= (1.0 - 0.10*cut)
            if speed > self.V_TOP:
                esc = self.V_TOP / speed
                v_long *= esc
                v_lat  *= esc

        Mz = self.a*(Fy_f*cs + Fx_f*sn) - self.b*Fy_r

        if thr > 0.2 and abs(steer_input) > 0.15:
            Mz += self.engine_yaw_push * self.engine_force_fwd * thr * math.copysign(1.0, steer_input)

        align_k = (0.28 + 0.24*spd_k)
        Mz += -align_k * v_lat * max(60.0, abs(v_long))

        if escapando:
            Mz += self.drift_yaw_boost * v_lat * (abs(v_long) + 60.0)

        self.yaw_rate += (Mz / self.Iz) * dt_fis
        self.yaw_rate -= self.yaw_rate * self.yaw_damp_k * dt_fis

        spdf = min(1.0, abs(v_long) / 380.0)
        yaw_max = 3.2 - 1.4*spdf
        self.yaw_rate = max(-yaw_max, min(yaw_max, self.yaw_rate))

        yaw_target = (abs(v_long) * math.tan(self._steer_wheel)) / max(0.1, self.L)
        blend = 0.7 if not escapando else 0.35
        self.yaw_rate += (yaw_target - self.yaw_rate) * blend * dt_fis

        self.angulo += math.degrees(self.yaw_rate) * dt_fis
        if self.angulo > 180: self.angulo -= 360
        if self.angulo < -180: self.angulo += 360

        self._recomp_vel(v_long, v_lat)
        speed_mult = ARCADE_SPEED_MULT * (0.88 if escapando else 1.0)
        dx = self.vx * dt_fis * speed_mult
        dy = self.vy * dt_fis * speed_mult
        max_move_per_frame = 200.0 * dt_fis
        dist_movimento = math.sqrt(dx*dx + dy*dy)
        if dist_movimento > max_move_per_frame:
            scale = max_move_per_frame / dist_movimento
            dx *= scale
            dy *= scale
        self.x += dx
        self.y += dy


        if na_grama:
            v_long, v_lat = self._decomp_vel()
            esta_em_re = v_long < 0.0 or brk > 0.0
            
            velocidade_atual_pxps = math.sqrt(v_long*v_long + v_lat*v_lat)
            ARCADE_SPEED_MULT = 2.5
            PXPS_TO_KMH = 1.0
            velocidade_kmh_atual = velocidade_atual_pxps * ARCADE_SPEED_MULT * PXPS_TO_KMH
            
            if esta_em_re:
                velocidade_alvo_kmh = 50.0
            else:
                velocidade_alvo_kmh = 100.0
            velocidade_alvo_pxps = velocidade_alvo_kmh / (ARCADE_SPEED_MULT * PXPS_TO_KMH)
            
            if velocidade_kmh_atual > velocidade_alvo_kmh:
                excesso_kmh = velocidade_kmh_atual - velocidade_alvo_kmh
                
                if esta_em_re:
                    fator_atrito_base = 0.95
                    fator_atrito_extra = min(0.10, excesso_kmh / 30.0)
                    fator_atrito_total = fator_atrito_base - fator_atrito_extra
                    fator_atrito_total = max(0.85, fator_atrito_total)
                else:
                    fator_atrito_base = 0.85
                    fator_atrito_extra = min(0.10, excesso_kmh / 30.0)
                    fator_atrito_total = fator_atrito_base - fator_atrito_extra
                    fator_atrito_total = max(0.75, fator_atrito_total)
                
                fator_atrito = fator_atrito_total ** dt
                v_long *= fator_atrito
                v_lat *= fator_atrito
            else:
                if esta_em_re:
                    fator_atrito = 0.99 ** dt
                else:
                    fator_atrito = 0.95 ** dt
                v_long *= fator_atrito
                v_lat *= fator_atrito
            
            self._recomp_vel(v_long, v_lat)
        
        houve_colisao = False
        
        if superficie_pista_renderizada is None:
            fx, fy = self._vetor_frente()
            dir_frente_x, dir_frente_y = fx, fy
            dir_direita_x, dir_direita_y = self._vetor_direita()

            cx, cy = int(self.x), int(self.y)
            colisao_count = 0
            total_amostras = 0
            
            amostras_local = [
                (0, 0),
                (10, 0), (-10, 0), (0, 6), (0, -6),
                (6, 3), (-6, 3), (6, -3), (-6, -3),
                (15, 0), (-15, 0), (0, 9), (0, -9)
            ]
            
            for ox, oy in amostras_local:
                px = int(cx + ox * dir_frente_x + oy * dir_direita_x)
                py = int(cy + ox * dir_frente_y + oy * dir_direita_y)
                
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
            
            # Remover limite de ré aqui - permitir ré normal
            # v_long, v_lat = self._decomp_vel()
            # if v_long < -1.5:
            #     v_long = -1.5
            # self._recomp_vel(v_long, v_lat)

        # Limites da área - parede invisível nas bordas
        if superficie_pista_renderizada is None:
            # Sistema antigo: limitar aos limites da tela
            x_antes = self.x
            y_antes = self.y
            self.x = max(0.0, min(LARGURA * 1.0, self.x))
            self.y = max(0.0, min(ALTURA * 1.0, self.y))
            
            # Se o carro tentou ultrapassar, parar o movimento naquela direção (parede invisível)
            if self.x != x_antes:
                self.vx = 0.0
            if self.y != y_antes:
                self.vy = 0.0
        else:
            # Sistema com tiles: limitar aos limites da superfície da pista
            # Parede invisível exata nas bordas
            pista_w = superficie_pista_renderizada.get_width()
            pista_h = superficie_pista_renderizada.get_height()
            
            # Verificar se está na borda ou ultrapassou e tentando ir além
            na_borda_esquerda = (self.x <= 0)
            na_borda_direita = (self.x >= pista_w)
            na_borda_cima = (self.y <= 0)
            na_borda_baixo = (self.y >= pista_h)
            
            # Se está na borda ou ultrapassou, parar o movimento naquela direção (parede invisível)
            if na_borda_esquerda:
                # Parar velocidade se tentando ir para a esquerda
                if self.vx < 0:
                    self.vx = 0.0
                    # Parar também a velocidade longitudinal se estava indo naquela direção
                    v_long, v_lat = self._decomp_vel()
                    fx, fy = self._vetor_frente()
                    if fx < 0:
                        v_long = 0.0
                    self._recomp_vel(v_long, v_lat)
                # Garantir que não ultrapasse
                self.x = max(0.0, self.x)
            
            if na_borda_direita:
                # Parar velocidade se tentando ir para a direita
                if self.vx > 0:
                    self.vx = 0.0
                    # Parar também a velocidade longitudinal se estava indo naquela direção
                    v_long, v_lat = self._decomp_vel()
                    fx, fy = self._vetor_frente()
                    if fx > 0:
                        v_long = 0.0
                    self._recomp_vel(v_long, v_lat)
                # Garantir que não ultrapasse
                self.x = min(pista_w, self.x)
            
            if na_borda_cima:
                # Parar velocidade se tentando ir para cima
                if self.vy < 0:
                    self.vy = 0.0
                    # Parar também a velocidade longitudinal se estava indo naquela direção
                    v_long, v_lat = self._decomp_vel()
                    fx, fy = self._vetor_frente()
                    if fy < 0:
                        v_long = 0.0
                    self._recomp_vel(v_long, v_lat)
                # Garantir que não ultrapasse
                self.y = max(0.0, self.y)
            
            if na_borda_baixo:
                # Parar velocidade se tentando ir para baixo
                if self.vy > 0:
                    self.vy = 0.0
                    # Parar também a velocidade longitudinal se estava indo naquela direção
                    v_long, v_lat = self._decomp_vel()
                    fx, fy = self._vetor_frente()
                    if fy > 0:
                        v_long = 0.0
                    self._recomp_vel(v_long, v_lat)
                # Garantir que não ultrapasse
                self.y = min(pista_h, self.y)

        ARCADE_SPEED_MULT = 2.5
        velocidade_com_mult = abs(v_long) * ARCADE_SPEED_MULT
        
        PXPS_TO_KMH = 1.0
        self.velocidade_kmh = velocidade_com_mult * PXPS_TO_KMH
        self.velocidade = v_long

        if MODO_DRIFT:
            self._atualizar_estado_drift(v_long, v_lat, dt_fis)
        
        self.skidmarks.atualizar(dt_fis)

        if self.turbo_ativo and self.turbo_carga > 0.0:
            self.turbo_carga = max(0.0, self.turbo_carga - 25.0 * dt_fis)
            
            if self.turbo_carga > 0.0:
                fx, fy = self._vetor_frente()
                rx, ry = self._vetor_direita()
                
                offset_traseira = 35.0
                offset_lateral = 6.0
                
                pos_x_nitro_esq = self.x - fx * offset_traseira - rx * offset_lateral
                pos_y_nitro_esq = self.y - fy * offset_traseira - ry * offset_lateral
                
                pos_x_nitro_dir = self.x - fx * offset_traseira + rx * offset_lateral
                pos_y_nitro_dir = self.y - fy * offset_traseira + ry * offset_lateral
                
                self.emissor_nitro.spawn(pos_x_nitro_esq, pos_y_nitro_esq, -fx, -fy, 120.0, dt_fis)
                self.emissor_nitro.spawn(pos_x_nitro_dir, pos_y_nitro_dir, -fx, -fy, 120.0, dt_fis)
        else:
            self.turbo_carga = min(100.0, self.turbo_carga + 12.0 * dt_fis)
            self.emissor_nitro._accum = 0.0
            if len(self.emissor_nitro.ps) > 0:
                self.emissor_nitro.ps.clear()


    def _verificar_colisao(self, superficie_mascara):
        return True

    def _atualizar_estado_drift(self, u, v, dt):
        vel_sq = u*u + v*v
        vel = math.sqrt(vel_sq) if vel_sq > 0.01 else 0.0
        slip = abs(math.degrees(math.atan2(v, max(0.1, abs(u)))))
        
        self.drifting = self.freio_mao_ativo or (vel > 5.0 and (slip > 0.5 or abs(v) > 1.0))
        
        criar_skidmark = self.drifting or self.na_grama
        
        if criar_skidmark:
            if self.freio_mao_ativo:
                self.drift_intensidade = 1.0
            elif self.na_grama:
                self.drift_intensidade = min(1.0, max(0.3, abs(u) / 60.0))
            else:
                self.drift_intensidade = min(1.0, abs(v) / 40.0)
            
            if self.na_grama:
                frequencia_skidmark = 0.15 if hasattr(self, 'eh_bot') and self.eh_bot else 0.08
            else:
                frequencia_skidmark = 0.2 if hasattr(self, 'eh_bot') and self.eh_bot else 0.1
                
            if self._ultimo_skidmark > frequencia_skidmark:
                fx, fy = self._vetor_frente()
                offset_tras = 12
                offset_lateral = 10
                
                pos_x_esq = self.x - fx * offset_tras - fy * offset_lateral
                pos_y_esq = self.y - fy * offset_tras + fx * offset_lateral
                self.skidmarks.adicionar_skidmark(pos_x_esq, pos_y_esq, self.angulo, self.drift_intensidade, "traseiro_esq", na_grama=self.na_grama)
                
                pos_x_dir = self.x - fx * offset_tras + fy * offset_lateral
                pos_y_dir = self.y - fy * offset_tras - fx * offset_lateral
                self.skidmarks.adicionar_skidmark(pos_x_dir, pos_y_dir, self.angulo, self.drift_intensidade, "traseiro_dir", na_grama=self.na_grama)
                
                angulo_minimo_dianteiro = 1.0 if (hasattr(self, 'eh_bot') and self.eh_bot) else 0.5
                if abs(self.angulo) > angulo_minimo_dianteiro or self.na_grama:
                    offset_frente = 10
                    
                    pos_x_frente_esq = self.x + fx * offset_frente - fy * offset_lateral
                    pos_y_frente_esq = self.y + fy * offset_frente + fx * offset_lateral
                    self.skidmarks.adicionar_skidmark(pos_x_frente_esq, pos_y_frente_esq, self.angulo, self.drift_intensidade * 0.7, "dianteiro_esq", na_grama=self.na_grama)
                    
                    pos_x_frente_dir = self.x + fx * offset_frente + fy * offset_lateral
                    pos_y_frente_dir = self.y + fy * offset_frente - fx * offset_lateral
                    self.skidmarks.adicionar_skidmark(pos_x_frente_dir, pos_y_frente_dir, self.angulo, self.drift_intensidade * 0.7, "dianteiro_dir", na_grama=self.na_grama)
                
                self._ultimo_skidmark = 0.0
        else:
            self.drift_intensidade *= 0.95
            if not self.na_grama:
                self.skidmarks.parar_rastro()
        
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

    def desenhar(self, superficie, camera=None):
        if camera is None:
            angulo_arredondado = round(self.angulo, 1)
            if self._sprite_angulo_cache is None or self._sprite_angulo_cache != angulo_arredondado:
                self._sprite_rot_cache = pygame.transform.rotozoom(self.sprite_base, self.angulo, 1.0)
                self._sprite_angulo_cache = angulo_arredondado
            sprite_rot = self._sprite_rot_cache
            rect = sprite_rot.get_rect(center=(self.x, self.y))
            superficie.blit(sprite_rot, rect.topleft)
            self.emissor_nitro.draw(superficie, camera)
            return
        sx, sy = camera.mundo_para_tela(self.x, self.y)
        angulo_arredondado = round(self.angulo, 1)
        zoom_arredondado = round(camera.zoom, 2)
        cache_key = (angulo_arredondado, zoom_arredondado)
        if self._sprite_angulo_cache is None or self._sprite_angulo_cache != cache_key:
            self._sprite_rot_cache = pygame.transform.rotozoom(self.sprite_base, self.angulo, camera.zoom)
            self._sprite_angulo_cache = cache_key
        sprite_rot = self._sprite_rot_cache
        rect = sprite_rot.get_rect(center=(sx, sy))
        superficie.blit(sprite_rot, rect.topleft)
        self.emissor_nitro.draw(superficie, camera)
    def usar_turbo(self):
        if self._turbo_cd > 0.0:
            return
        u, v = self._mundo_para_local(self.vx, self.vy)
        u += self._turbo_forca_base
        self.vx, self.vy = self._local_para_mundo(u, v)
        self.v_long, self.v_lat = self._mundo_para_local(self.vx, self.vy)
        self._turbo_timer = self._turbo_duracao_base
        self._turbo_mul   = TURBO_FATOR
        self._turbo_cd    = self._turbo_cooldown_base

    def ativar_drift(self, teclas=None):
        if "IA" in self.nome:
            return
        self.freio_mao_ativo = True
        self.drift_ativado   = True

    def desativar_drift(self):
        self.freio_mao_ativo = False
        self.drift_ativado   = False
