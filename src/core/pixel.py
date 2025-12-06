"""Sistema do Pixel - O Fennec Informante que vende informações secretas"""
import pygame
import random
import os
import json
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso

def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

CAMINHO_PIXEL_DATA = os.path.join(DIR_PROJETO, "data", "pixel.json")

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "pixel")
# Usar os sprites reais que existem
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "pixel_neutro.png")
SPRITE_SERIO = os.path.join(CAMINHO_SPRITES, "pixel_serio.png")
SPRITE_MALANDRO = os.path.join(CAMINHO_SPRITES, "pixel_malandro.png")
SPRITE_SORRISO = os.path.join(CAMINHO_SPRITES, "pixel_sorriso.png")
# Fallbacks (usar os mesmos se não existirem)
SPRITE_DIGITANDO = SPRITE_NEUTRO  # Usar neutro como digitando
SPRITE_ASSUSTADO = SPRITE_SERIO  # Usar sério como assustado
SPRITE_PARANOICO = SPRITE_MALANDRO  # Usar malandro como paranoico
SPRITE_VENDENDO = SPRITE_SORRISO  # Usar sorriso como vendendo

def obter_caminho_bunker():
    from config import obter_caminho_sprite_dia_noite
    return obter_caminho_sprite_dia_noite("bunker")

CAMINHO_BUNKER_FALLBACK = os.path.join(DIR_PROJETO, "assets", "images", "ui", "esconderijo_pixel.png")

class Pixel:
    """Pixel - O Fennec Informante que vende informações secretas"""
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_digitando = None
        self.sprite_assustado = None
        self.sprite_neutro = None
        self.sprite_paranoico = None
        self.sprite_vendendo = None
        self.sprite_fundo = None
        self.sprites_carregados = False
        
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "fechado"
        self.parte_dialogo = 0
        self.parte_cutscene = 0
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 80.0
        
        self.nome_revelado = False
        self.primeira_aparicao_mostrada = False
        
        self.loja_aberta = False
        self.informacao_selecionada = None
        self.menu_desbloqueios_aberto = False
        self.desbloqueio_selecionado = None
        
        self.informacoes_disponiveis = []
        self._gerar_informacoes()
        
        # Desbloqueios exclusivos do Pixel
        self.desbloqueios_disponiveis = [
            {
                'tipo': 'upgrade_nivel_6',
                'nome': 'Tunagem Nível 6',
                'descricao': 'Eu hackeei o sistema de upgrades da cidade. Posso desbloquear um nível extra de tunagem que ninguém mais tem acesso. Seus upgrades podem ir até nível 6 agora.',
                'preco': 15000,
                'ja_desbloqueado': False
            },
            {
                'tipo': 'cores_especiais',
                'nome': 'Cores Especiais',
                'descricao': 'Interceptei um catálogo de cores exclusivas de uma fábrica de tinta premium. Posso desbloquear opções de cor especiais para seus carros que não estão disponíveis no mercado normal.',
                'preco': 10000,
                'ja_desbloqueado': False
            }
        ]
    
    def _gerar_informacoes(self):
        """Gera lista de informações disponíveis para venda"""
        self.informacoes_disponiveis = [
            {
                'tipo': 'corrida_secreta',
                'nome': 'Corrida Secreta nos Túneis',
                'descricao': 'Rex acha que controla a noite com aquelas luzes neon ridículas. Patético. Eu interceptei um sinal fantasma. Tem uma corrida acontecendo nos túneis de drenagem abandonados. Sem regras, sem câmeras, pagamento em dinheiro vivo.',
                'preco': 5000,
                'dica': 'Corrida secreta desbloqueada nos túneis'
            },
            {
                'tipo': 'fraqueza_boris',
                'nome': 'Fraqueza do Boris',
                'descricao': 'O javali... Boris. Ele só pensa em torque. Eu hackeei o histórico de compras dele. Ele gastou uma fortuna no motor, mas economizou na refrigeração. O sistema dele não aguenta pressão prolongada.',
                'preco': 3000,
                'dica': 'Boris tem fraqueza na refrigeração do motor'
            },
            {
                'tipo': 'fraqueza_rex',
                'nome': 'Fraqueza do Rex',
                'descricao': 'Rex é arrogante demais. Ele sempre subestima os adversários. Se você começar devagar e acelerar no final, ele vai se confiar e cometer erros.',
                'preco': 3000,
                'dica': 'Rex subestima adversários - acelere no final'
            },
            {
                'tipo': 'peca_rara',
                'nome': 'Peça Rara nas Docas',
                'descricao': 'Tem um contêiner "perdido" nas docas do Barão hoje à noite. O manifesto diz "peças de trator", mas meu scanner térmico detectou uma transmissão de corrida importada. Se você chegar lá antes dos capangas dele... é sua.',
                'preco': 4000,
                'dica': 'Peça rara disponível nas docas do Barão'
            },
            {
                'tipo': 'blitz_policia',
                'nome': 'Alerta de Blitz',
                'descricao': 'Shhh. Estou ouvindo a frequência da polícia. Eles estão montando uma blitz na Avenida Central. Evite essa área nas próximas 2 horas.',
                'preco': 2000,
                'dica': 'Blitz policial na Avenida Central - evite'
            }
        ]
    
    def carregar_estado(self):
        """Carrega o estado do Pixel do progresso.json"""
        self.nome_revelado = gerenciador_progresso.pixel_nome_revelado if hasattr(gerenciador_progresso, 'pixel_nome_revelado') else False
        self.primeira_aparicao_mostrada = gerenciador_progresso.pixel_primeira_aparicao_mostrada if hasattr(gerenciador_progresso, 'pixel_primeira_aparicao_mostrada') else False
    
    def salvar_estado(self):
        """Salva o estado do Pixel no progresso.json"""
        gerenciador_progresso.pixel_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.pixel_primeira_aparicao_mostrada = getattr(self, 'primeira_aparicao_mostrada', False)
        gerenciador_progresso.salvar()
    
    def carregar_sprites(self):
        """Carrega os sprites do Pixel"""
        if self.sprites_carregados:
            return
        
        try:
            # Carregar sprites reais que existem
            if os.path.exists(SPRITE_NEUTRO):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO).convert_alpha()
                print(f"[PIXEL] Sprite neutro carregado: {SPRITE_NEUTRO}")
            else:
                print(f"[PIXEL] ERRO: Sprite neutro não encontrado: {SPRITE_NEUTRO}")
            
            if os.path.exists(SPRITE_SERIO):
                self.sprite_serio = pygame.image.load(SPRITE_SERIO).convert_alpha()
                print(f"[PIXEL] Sprite sério carregado: {SPRITE_SERIO}")
            else:
                print(f"[PIXEL] ERRO: Sprite sério não encontrado: {SPRITE_SERIO}")
            
            if os.path.exists(SPRITE_MALANDRO):
                self.sprite_malandro = pygame.image.load(SPRITE_MALANDRO).convert_alpha()
                print(f"[PIXEL] Sprite malandro carregado: {SPRITE_MALANDRO}")
            else:
                print(f"[PIXEL] ERRO: Sprite malandro não encontrado: {SPRITE_MALANDRO}")
            
            if os.path.exists(SPRITE_SORRISO):
                self.sprite_sorriso = pygame.image.load(SPRITE_SORRISO).convert_alpha()
                print(f"[PIXEL] Sprite sorriso carregado: {SPRITE_SORRISO}")
            else:
                print(f"[PIXEL] ERRO: Sprite sorriso não encontrado: {SPRITE_SORRISO}")
            
            # Mapear sprites antigos para os novos
            self.sprite_digitando = self.sprite_neutro if self.sprite_neutro else None
            self.sprite_assustado = self.sprite_serio if self.sprite_serio else self.sprite_neutro
            self.sprite_paranoico = self.sprite_malandro if self.sprite_malandro else self.sprite_neutro
            self.sprite_vendendo = self.sprite_sorriso if self.sprite_sorriso else self.sprite_neutro
            
            # Carregar fundo (bunker) com sistema dia/noite e fallback
            CAMINHO_BUNKER = obter_caminho_bunker()
            if os.path.exists(CAMINHO_BUNKER):
                self.sprite_fundo = pygame.image.load(CAMINHO_BUNKER).convert_alpha()
                print(f"[PIXEL] Fundo carregado: {CAMINHO_BUNKER}")
            elif os.path.exists(CAMINHO_BUNKER_FALLBACK):
                self.sprite_fundo = pygame.image.load(CAMINHO_BUNKER_FALLBACK).convert_alpha()
                print(f"[PIXEL] Fundo carregado (fallback): {CAMINHO_BUNKER_FALLBACK}")
            else:
                print(f"[PIXEL] ERRO: Fundo não encontrado! Tentou: {CAMINHO_BUNKER} e {CAMINHO_BUNKER_FALLBACK}")
            
            self.sprites_carregados = True
        except Exception as e:
            print(f"Erro ao carregar sprites do Pixel: {e}")
    
    def verificar_ganhou_todas_corridas_ouro(self):
        """Verifica se o jogador ganhou todas as corridas do cinturão e da montanha com ouro"""
        # Corridas do Cinturão Industrial (Fuligem): pistas 4, 5, 6
        # Corridas da Montanha (Akira): pista 3
        pistas_necessarias = [3, 4, 5, 6]
        
        for pista in pistas_necessarias:
            trofeu = gerenciador_progresso.obter_trofeu(pista)
            if trofeu != "ouro":
                return False
        
        return True
    
    def verificar_aparecer_primeira_vez(self):
        """Verifica se deve mostrar a primeira aparição do Pixel"""
        # Carregar estado atualizado do progresso
        self.carregar_estado()
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Revelar nome se ainda não foi revelado (após primeira aparição física)
        if not self.nome_revelado:
            # Verificar se a cena ch4_3_meet_pixel_physical foi visitada
            from core.progresso import gerenciador_progresso
            if hasattr(gerenciador_progresso, 'pixel_primeira_aparicao_mostrada') and gerenciador_progresso.pixel_primeira_aparicao_mostrada:
                self.nome_revelado = True
                self.salvar_estado()
        
        if self.primeira_aparicao_mostrada:
            # Se já mostrou a primeira aparição, verificar se deve mostrar o diálogo "explodiu nos servidores"
            if self.verificar_ganhou_todas_corridas_ouro():
                # Verificar se já mostrou esse diálogo
                if not hasattr(gerenciador_progresso, 'pixel_dialogo_explodiu_mostrado'):
                    gerenciador_progresso.pixel_dialogo_explodiu_mostrado = False
                
                if not gerenciador_progresso.pixel_dialogo_explodiu_mostrado:
                    if not self.sprites_carregados:
                        self.carregar_sprites()
                    
                    # Ativar diálogo "explodiu nos servidores"
                    self.ativo = True
                    self.fase_dialogo = "explodiu_servidores"
                    self.parte_dialogo = 0
                    # Garantir que o sprite está definido
                    if not self.sprite_atual:
                        self.sprite_atual = self.sprite_paranoico if self.sprite_paranoico else self.sprite_neutro
                    # Revelar nome se ainda não foi revelado
                    if not self.nome_revelado:
                        self.nome_revelado = True
                        self.salvar_estado()
                    self._iniciar_dialogo_explodiu()
                    return True
            # Se não ganhou todas ou já mostrou, oferecer menu de desbloqueios
            if not self.sprites_carregados:
                self.carregar_sprites()
            self.ativo = True
            # Revelar nome se ainda não foi revelado
            if not self.nome_revelado:
                self.nome_revelado = True
                self.salvar_estado()
            self.fase_dialogo = "desbloqueios"
            self.ativar_menu_desbloqueios()
            return True
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Ativar primeira aparição
        self.ativo = True
        self.fase_dialogo = "primeira_aparicao"
        self.parte_cutscene = 0
        self._iniciar_primeira_aparicao()
        return True
    
    def _iniciar_primeira_aparicao(self):
        """Inicia a cutscene de primeira aparição"""
        self.parte_cutscene = 0
        self._avancar_cutscene()
    
    def _avancar_cutscene(self):
        """Avança para a próxima parte da cutscene"""
        partes = [
            {
                "sprite": "digitando",
                "texto": "",
                "duracao": 2.0
            },
            {
                "sprite": "assustado",
                "texto": "SHHH! Fecha! Fecha a entrada! Você quer deixar o sinal vazar? Você tem ideia de quantos firewalls eu tive que quebrar para manter este lugar fora do grid?"
            },
            {
                "sprite": "paranoico",
                "texto": "Espera... minha leitura biométrica diz que você é o novato. O projeto de estimação do Crank. Hmpf. O guaxinim velho finalmente achou alguém para sujar as mãos."
            },
            {
                "sprite": "digitando",
                "texto": "Olha, eu não me importo com o seu carro. Eu não me importo com lataria e óleo. O mundo lá em cima é só barulho analógico. A verdade... a verdade está aqui embaixo. Nos dados. No fluxo binário."
            },
            {
                "sprite": "vendendo",
                "texto": "Eu vejo tudo. Sei onde o Rex esconde o dinheiro das apostas. Sei qual sensor do carro da Akira está falhando. Sei quando o próximo carregamento ilegal do Barão chega no porto."
            },
            {
                "sprite": "paranoico",
                "texto": "Informação é poder, novato. E eu sou a fonte. Se você tiver os créditos para pagar pela largura de banda, eu posso te dar a vantagem que você precisa. Mas seja rápido. Meus dados expiram. Tique-taque."
            }
        ]
        
        if self.parte_cutscene < len(partes):
            parte = partes[self.parte_cutscene]
            
            sprite_nome = parte.get("sprite", "neutro")
            if sprite_nome == "digitando" and self.sprite_digitando:
                self.sprite_atual = self.sprite_digitando
            elif sprite_nome == "assustado" and self.sprite_assustado:
                self.sprite_atual = self.sprite_assustado
            elif sprite_nome == "paranoico" and self.sprite_paranoico:
                self.sprite_atual = self.sprite_paranoico
            elif sprite_nome == "vendendo" and self.sprite_vendendo:
                self.sprite_atual = self.sprite_vendendo
            else:
                self.sprite_atual = self.sprite_neutro if self.sprite_neutro else self.sprite_digitando
            
            texto = parte.get("texto", "")
            if texto:
                self._iniciar_animacao_texto(texto)
            else:
                self.texto_completo = ""
                self.texto_exibido = ""
        else:
            self.primeira_aparicao_mostrada = True
            self.salvar_estado()
            # Após primeira aparição, oferecer menu de desbloqueios
            self.fase_dialogo = "desbloqueios"
            self.ativar_menu_desbloqueios()
    
    def _iniciar_dialogo_explodiu(self):
        """Inicia o diálogo 'explodiu nos servidores'"""
        self.parte_dialogo = 0
        self._avancar_dialogo_explodiu()
    
    def _avancar_dialogo_explodiu(self):
        """Avança o diálogo 'explodiu nos servidores'"""
        if self.parte_dialogo == 0:
            self.sprite_atual = self.sprite_paranoico if self.sprite_paranoico else self.sprite_neutro
            self._iniciar_animacao_texto("Seus dados explodiram nos servidores. Até agora, você era ruído. Agora é padrão interessante.")
        elif self.parte_dialogo == 1:
            self.sprite_atual = self.sprite_assustado if self.sprite_assustado else self.sprite_neutro
            self._iniciar_animacao_texto("Isso só acontece quando o Rex pensa: 'Talvez eu possa usar isso… ou destruir.'")
        else:
            # Finalizar diálogo e marcar como mostrado
            gerenciador_progresso.pixel_dialogo_explodiu_mostrado = True
            gerenciador_progresso.salvar()
            self.fase_dialogo = "loja"
            self._abrir_loja()
    
    def _abrir_loja(self):
        """Abre a loja de informações do Pixel"""
        self.loja_aberta = True
        # Garantir que o sprite está definido
        if not self.sprite_atual:
            self.sprite_atual = self.sprite_digitando if self.sprite_digitando else self.sprite_neutro
        
        # Atualizar status dos desbloqueios
        self._atualizar_status_desbloqueios()
        
        # Revelar nome se ainda não foi revelado
        if not self.nome_revelado:
            self.nome_revelado = True
            self.salvar_estado()
        
        saudacoes = [
            "Você de novo? Rápido, estou no meio de uma descriptografia de nível 5. O que você quer?",
            "Espero que não tenha sido seguido. Meus sensores de proximidade estão apitando que nem loucos. Fala logo.",
            "Se veio pedir fiado, a resposta é 404: Crédito Não Encontrado. Se veio comprar, o menu está na tela.",
            "Shhh. Estou ouvindo a frequência da polícia. Eles estão montando uma blitz na Avenida Central. Viu? Informação de graça. A próxima vai custar."
        ]
        texto = random.choice(saudacoes)
        self._iniciar_animacao_texto(texto)
    
    def _atualizar_status_desbloqueios(self):
        """Atualiza o status dos desbloqueios baseado no progresso"""
        for desbloqueio in self.desbloqueios_disponiveis:
            if desbloqueio['tipo'] == 'upgrade_nivel_6':
                desbloqueio['ja_desbloqueado'] = getattr(gerenciador_progresso, 'pixel_upgrade_nivel_6_desbloqueado', False)
            elif desbloqueio['tipo'] == 'cores_especiais':
                # Verificar se pelo menos uma cor especial foi desbloqueada
                cores_desbloqueadas = getattr(gerenciador_progresso, 'pixel_cores_especiais_desbloqueadas', set())
                desbloqueio['ja_desbloqueado'] = len(cores_desbloqueadas) > 0
    
    def ativar_menu_desbloqueios(self):
        """Ativa o menu de desbloqueios exclusivos"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        self.ativo = True
        self.fase_dialogo = "desbloqueios"
        self.menu_desbloqueios_aberto = True
        self._atualizar_status_desbloqueios()
        # Garantir que o sprite está definido
        if not self.sprite_atual:
            self.sprite_atual = self.sprite_vendendo if self.sprite_vendendo else (self.sprite_neutro if self.sprite_neutro else self.sprite_digitando)
        # Revelar nome se ainda não foi revelado
        if not self.nome_revelado:
            self.nome_revelado = True
            self.salvar_estado()
        texto = "Ah, você quer os desbloqueios exclusivos? Claro. Eu hackeei sistemas que nem o Rex sabe que existem. Mas isso tem um preço."
        self._iniciar_animacao_texto(texto)
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        
        texto_lower = texto.lower()
        # Revelar nome do Pixel na primeira aparição ou quando ele se apresenta
        if "pixel" in texto_lower or "meu nome" in texto_lower or "me chamo pixel" in texto_lower or "sou pixel" in texto_lower:
            if not self.nome_revelado:
                self.nome_revelado = True
                self.salvar_estado()
        
        # Se já passou da primeira aparição, revelar o nome automaticamente
        if self.primeira_aparicao_mostrada and not self.nome_revelado:
            self.nome_revelado = True
            self.salvar_estado()
    
    def _atualizar_animacao_texto(self, dt):
        """Atualiza animação de texto letra por letra"""
        if not self.texto_completo:
            return
        
        if len(self.texto_exibido) < len(self.texto_completo):
            self.tempo_animacao += dt
            caracteres_para_adicionar = int(self.tempo_animacao * self.velocidade_texto)
            if caracteres_para_adicionar > len(self.texto_exibido):
                self.texto_exibido = self.texto_completo[:caracteres_para_adicionar]
    
    def processar_eventos(self, eventos):
        """Processa eventos do Pixel"""
        if not self.ativo:
            return None
        
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Botão esquerdo
                    # Se o texto ainda está sendo animado, pular para o final
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self.texto_exibido = self.texto_completo
                    else:
                        # Avançar diálogo
                        if self.fase_dialogo == "primeira_aparicao":
                            self.parte_cutscene += 1
                            self._avancar_cutscene()
                        elif self.fase_dialogo == "explodiu_servidores":
                            self.parte_dialogo += 1
                            self._avancar_dialogo_explodiu()
                        elif self.fase_dialogo == "loja":
                            # Fechar diálogo e abrir menu de loja
                            self.fechar()
                            return "abrir_loja"
                        elif self.fase_dialogo == "desbloqueios":
                            # Se o texto do diálogo inicial terminou, processar clique no menu
                            if len(self.texto_exibido) >= len(self.texto_completo) and self.menu_desbloqueios_aberto:
                                mouse_x, mouse_y = evento.pos
                                self._processar_clique_desbloqueios(mouse_x, mouse_y)
                            # Se o texto ainda não terminou, apenas pular para o final (não fazer nada mais)
                            # O menu aparecerá automaticamente quando o texto terminar
                        elif self.fase_dialogo == "despedida":
                            # Após despedida, fechar completamente
                            self.fechar()
                            return "fechado"
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    # Se o texto ainda está sendo animado, pular para o final
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self.texto_exibido = self.texto_completo
                    else:
                        # Avançar diálogo
                        if self.fase_dialogo == "primeira_aparicao":
                            self.parte_cutscene += 1
                            self._avancar_cutscene()
                        elif self.fase_dialogo == "explodiu_servidores":
                            self.parte_dialogo += 1
                            self._avancar_dialogo_explodiu()
                        elif self.fase_dialogo == "loja":
                            # Fechar diálogo e abrir menu de loja
                            self.fechar()
                            return "abrir_loja"
                        elif self.fase_dialogo == "desbloqueios":
                            # Se o texto ainda não terminou, apenas pular para o final
                            if len(self.texto_exibido) < len(self.texto_completo):
                                self.texto_exibido = self.texto_completo
                            # Se o texto do diálogo inicial terminou, processar teclas no menu
                            elif len(self.texto_exibido) >= len(self.texto_completo) and self.menu_desbloqueios_aberto:
                                if evento.key == pygame.K_ESCAPE:
                                    # Fechar menu e mostrar despedida
                                    self.menu_desbloqueios_aberto = False
                                    self.sprite_atual = self.sprite_digitando if self.sprite_digitando else self.sprite_neutro
                                    despedidas = [
                                        "Tchau. Volte quando tiver mais créditos. Meus dados não esperam ninguém.",
                                        "Até. E cuidado com quem você fala sobre isso. O Rex tem ouvidos em todo lugar.",
                                        "Sai daqui. Tenho firewalls para quebrar e sistemas para hackear. Não me atrapalhe."
                                    ]
                                    import random
                                    texto = random.choice(despedidas)
                                    self._iniciar_animacao_texto(texto)
                                    self.fase_dialogo = "despedida"
                        elif self.fase_dialogo == "despedida":
                            # Após despedida, fechar completamente
                            self.fechar()
                            return "fechado"
                elif evento.key == pygame.K_ESCAPE:
                    if self.fase_dialogo == "desbloqueios" and self.menu_desbloqueios_aberto:
                        # Fechar menu e mostrar despedida
                        self.menu_desbloqueios_aberto = False
                        self.sprite_atual = self.sprite_digitando if self.sprite_digitando else self.sprite_neutro
                        despedidas = [
                            "Tchau. Volte quando tiver mais créditos. Meus dados não esperam ninguém.",
                            "Até. E cuidado com quem você fala sobre isso. O Rex tem ouvidos em todo lugar.",
                            "Sai daqui. Tenho firewalls para quebrar e sistemas para hackear. Não me atrapalhe."
                        ]
                        import random
                        texto = random.choice(despedidas)
                        self._iniciar_animacao_texto(texto)
                        self.fase_dialogo = "despedida"
                    elif self.fase_dialogo == "despedida":
                        # Após despedida, fechar completamente
                        self.fechar()
                        return "fechado"
                    else:
                        self.fechar()
                        return "fechado"
        
        return None
    
    def processar_compra(self, informacao_info):
        """Processa a compra de uma informação"""
        preco = informacao_info['preco']
        
        # Verificar dinheiro
        if not gerenciador_progresso.tem_dinheiro(preco):
            self.sprite_atual = self.sprite_paranoico if self.sprite_paranoico else self.sprite_neutro
            texto = "404: Crédito Não Encontrado. Volte quando tiver largura de banda suficiente para pagar."
            self._iniciar_animacao_texto(texto)
            return False, "Dinheiro insuficiente"
        
        # Remover dinheiro
        gerenciador_progresso.remover_dinheiro(preco)
        
        # Reação
        self.sprite_atual = self.sprite_vendendo if self.sprite_vendendo else self.sprite_neutro
        texto = "Transação concluída. Os dados estão no seu GPS. Agora suma daqui antes que rastreiem o pacote até meu servidor."
        
        self._iniciar_animacao_texto(texto)
        return True, f"Informação comprada por ${preco:,}!"
    
    def atualizar(self, dt):
        """Atualiza o Pixel"""
        if not self.ativo:
            return
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Pixel"""
        if not self.ativo:
            return
        
        render_text = _get_render_text()
        
        # Sempre desenhar fundo primeiro (limpar tela)
        if self.sprite_fundo:
            fundo_redimensionado = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
            tela.blit(fundo_redimensionado, (0, 0))
        else:
            # Se não há fundo, desenhar overlay escuro
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 20, 10, 200))
            tela.blit(overlay, (0, 0))
            print("[PIXEL] AVISO: sprite_fundo não carregado, usando overlay")
        
        # Desenhar sprite do Pixel (sempre, mesmo quando menu está aberto)
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Se sprite_atual não está definido, usar sprite padrão
        sprite_para_desenhar = self.sprite_atual
        if not sprite_para_desenhar:
            sprite_para_desenhar = self.sprite_neutro if self.sprite_neutro else self.sprite_digitando
        
        if sprite_para_desenhar:
            sprite_original_w = sprite_para_desenhar.get_width()
            sprite_original_h = sprite_para_desenhar.get_height()
            if sprite_original_w > 0 and sprite_original_h > 0:
                # Usar mesma configuração da cutscene: altura_max 400, largura_max 350
                sprite_altura_max = 400
                sprite_largura_max = 350
                
                escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
                escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
                escala = min(escala_w, escala_h, 1.0)
                
                sprite_w = int(sprite_original_w * escala)
                sprite_h = int(sprite_original_h * escala)
                sprite_redimensionado = pygame.transform.scale(sprite_para_desenhar, (sprite_w, sprite_h))
                
                # Posicionar baseado na caixa de texto (mesma lógica da cutscene)
                # Na cutscene: caixa_altura = 10 (apenas para cálculo), caixa_y = ALTURA - 10 - 50
                # sprite_y_base = caixa_y - sprite_h - 20
                # Mas a caixa real de diálogo está em ALTURA - 200 - 50
                # Para manter a mesma posição visual, usar o mesmo cálculo da cutscene
                caixa_altura_calc = 10  # Mesmo valor usado na cutscene para posicionar sprite
                caixa_y_calc = ALTURA - caixa_altura_calc - 50
                sprite_y_base = caixa_y_calc - sprite_h - 20
                
                sprite_x = LARGURA // 2 - sprite_w // 2
                sprite_y = sprite_y_base
                tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
            else:
                print(f"[PIXEL] AVISO: Sprite tem tamanho inválido ({sprite_original_w}, {sprite_original_h})")
        else:
            print(f"[PIXEL] AVISO: Nenhum sprite disponível para desenhar! sprite_atual={self.sprite_atual}, sprite_neutro={self.sprite_neutro}, sprite_digitando={self.sprite_digitando}")
        
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        # Fundo da caixa
        overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay_caixa.fill((0, 0, 0, 200))
        tela.blit(overlay_caixa, (caixa_x, caixa_y))
        
        # Borda da caixa (branca como na cutscene)
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Nome do personagem
        # Carregar estado atualizado do progresso para verificar nome
        self.carregar_estado()
        # Revelar nome automaticamente se já passou da primeira aparição
        if self.primeira_aparicao_mostrada and not self.nome_revelado:
            self.nome_revelado = True
            self.salvar_estado()
        nome = "Pixel" if self.nome_revelado else "???"
        # Usar mesma cor da cutscene: (255, 255, 100)
        nome_texto = render_text(nome, 20, (255, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Atualizar animação de texto
        self._atualizar_animacao_texto(dt)
        
        # Texto do diálogo com quebra de linha
        if self.texto_exibido:
            # Quebrar texto em linhas usando render_text para medir largura
            palavras = self.texto_exibido.split(' ')
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                # Usar render_text para medir a largura corretamente
                teste_render = render_text(teste_linha, 18, (200, 255, 200), bold=False, pixel_style=True)
                largura_teste = teste_render.get_width()
                if largura_teste <= caixa_largura - 40:
                    linha_atual = teste_linha
                else:
                    if linha_atual:
                        linhas.append(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual)
            
            y_texto = caixa_y + 50
            for linha in linhas:
                linha_render = render_text(linha, 18, (200, 255, 200), bold=False, pixel_style=True)
                tela.blit(linha_render, (caixa_x + 20, y_texto))
                y_texto += 25
        
        # Indicador de avanço
        if len(self.texto_exibido) >= len(self.texto_completo):
            indicador = render_text("Pressione ESPAÇO ou clique para continuar", 14, (0, 200, 0), bold=False, pixel_style=True)
            tela.blit(indicador, (caixa_x + caixa_largura - 400, caixa_y + caixa_altura - 30))
        
        # Se o menu de desbloqueios está aberto e o texto terminou, desenhar menu
        # Mas não desenhar se está na fase de despedida
        if self.menu_desbloqueios_aberto and len(self.texto_exibido) >= len(self.texto_completo) and self.fase_dialogo == "desbloqueios":
            self.desenhar_menu_desbloqueios(tela)
        elif self.menu_desbloqueios_aberto:
            # Debug: verificar por que o menu não está sendo desenhado
            print(f"[PIXEL DEBUG] Menu não desenhado. menu_aberto={self.menu_desbloqueios_aberto}, texto_exibido={len(self.texto_exibido)}, texto_completo={len(self.texto_completo)}, fase={self.fase_dialogo}")
    
    def _desenhar_caixa_dialogo(self, tela, dt):
        """Desenha apenas a caixa de diálogo (usado quando menu de desbloqueios está aberto)"""
        render_text = _get_render_text()
        
        caixa_largura = 1000
        caixa_altura = 150
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 20
        
        # Fundo da caixa
        overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay_caixa.fill((0, 0, 0, 220))
        tela.blit(overlay_caixa, (caixa_x, caixa_y))
        
        # Borda
        pygame.draw.rect(tela, (0, 255, 0), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Nome
        nome = "Pixel" if self.nome_revelado else "???"
        nome_texto = render_text(nome, 18, (0, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Atualizar animação
        self._atualizar_animacao_texto(dt)
        
        # Texto
        if self.texto_exibido:
            palavras = self.texto_exibido.split(' ')
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                teste_render = render_text(teste_linha, 16, (200, 255, 200), bold=False, pixel_style=True)
                if teste_render.get_width() <= caixa_largura - 40:
                    linha_atual = teste_linha
                else:
                    if linha_atual:
                        linhas.append(linha_atual)
                    linha_atual = palavra
            if linha_atual:
                linhas.append(linha_atual)
            
            y_texto = caixa_y + 40
            for linha in linhas:
                linha_render = render_text(linha, 16, (200, 255, 200), bold=False, pixel_style=True)
                tela.blit(linha_render, (caixa_x + 20, y_texto))
                y_texto += 20
    
    def _processar_clique_desbloqueios(self, mouse_x, mouse_y):
        """Processa cliques no menu de desbloqueios"""
        # Área do menu (centro da tela)
        menu_largura = 800
        menu_altura = 500
        menu_x = (LARGURA - menu_largura) // 2
        menu_y = (ALTURA - menu_altura) // 2
        
        # Verificar cliques nos desbloqueios
        y_inicio = menu_y + 150
        altura_item = 80
        espacamento = 10
        
        for i, desbloqueio in enumerate(self.desbloqueios_disponiveis):
            item_y = y_inicio + i * (altura_item + espacamento)
            item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                if not desbloqueio['ja_desbloqueado']:
                    # Tentar comprar
                    self._comprar_desbloqueio(desbloqueio)
                else:
                    # Já desbloqueado
                    self.sprite_atual = self.sprite_paranoico if self.sprite_paranoico else self.sprite_neutro
                    texto = "Você já tem isso. Não me faça perder tempo repetindo transações."
                    self._iniciar_animacao_texto(texto)
                break
        
        # Verificar clique no botão "Voltar"
        voltar_y = menu_y + menu_altura - 50
        voltar_rect = pygame.Rect(menu_x + menu_largura - 150, voltar_y, 130, 35)
        if voltar_rect.collidepoint(mouse_x, mouse_y):
            # Fechar menu e mostrar mensagem de despedida
            self.menu_desbloqueios_aberto = False
            self.sprite_atual = self.sprite_digitando if self.sprite_digitando else self.sprite_neutro
            despedidas = [
                "Tchau. Volte quando tiver mais créditos. Meus dados não esperam ninguém.",
                "Até. E cuidado com quem você fala sobre isso. O Rex tem ouvidos em todo lugar.",
                "Sai daqui. Tenho firewalls para quebrar e sistemas para hackear. Não me atrapalhe."
            ]
            import random
            texto = random.choice(despedidas)
            self._iniciar_animacao_texto(texto)
            # Após mostrar a mensagem, fechar completamente
            # O fechamento será feito quando o jogador clicar novamente
            self.fase_dialogo = "despedida"
    
    def _comprar_desbloqueio(self, desbloqueio):
        """Processa a compra de um desbloqueio"""
        preco = desbloqueio['preco']
        
        # Verificar dinheiro
        if not gerenciador_progresso.tem_dinheiro(preco):
            self.sprite_atual = self.sprite_paranoico if self.sprite_paranoico else self.sprite_neutro
            texto = "404: Crédito Não Encontrado. Volte quando tiver largura de banda suficiente para pagar."
            self._iniciar_animacao_texto(texto)
            return False
        
        # Remover dinheiro
        gerenciador_progresso.remover_dinheiro(preco)
        
        # Aplicar desbloqueio
        if desbloqueio['tipo'] == 'upgrade_nivel_6':
            gerenciador_progresso.pixel_upgrade_nivel_6_desbloqueado = True
            self.sprite_atual = self.sprite_vendendo if self.sprite_vendendo else self.sprite_neutro
            texto = "Pronto. Hacked. Seus upgrades agora podem ir até nível 6. Não espalhe isso, ou o Rex vai querer saber como você conseguiu."
        elif desbloqueio['tipo'] == 'cores_especiais':
            # Desbloquear cores especiais
            if not hasattr(gerenciador_progresso, 'pixel_cores_especiais_desbloqueadas'):
                gerenciador_progresso.pixel_cores_especiais_desbloqueadas = set()
            gerenciador_progresso.pixel_cores_especiais_desbloqueadas.add("todas")
            self.sprite_atual = self.sprite_vendendo if self.sprite_vendendo else self.sprite_neutro
            texto = "Catálogo de cores premium desbloqueado. Agora você tem acesso a opções de cor que ninguém mais tem. Use com moderação."
        
        gerenciador_progresso.salvar()
        desbloqueio['ja_desbloqueado'] = True
        self._iniciar_animacao_texto(texto)
        return True
    
    def desenhar_menu_desbloqueios(self, tela):
        """Desenha o menu de desbloqueios exclusivos"""
        if not self.menu_desbloqueios_aberto:
            return
        
        render_text = _get_render_text()
        
        # Área do menu (centro da tela)
        menu_largura = 800
        menu_altura = 500
        menu_x = (LARGURA - menu_largura) // 2
        menu_y = (ALTURA - menu_altura) // 2
        
        # Fundo do menu
        overlay_menu = pygame.Surface((menu_largura, menu_altura), pygame.SRCALPHA)
        overlay_menu.fill((0, 0, 0, 240))
        tela.blit(overlay_menu, (menu_x, menu_y))
        
        # Borda verde (tema tecnológico)
        pygame.draw.rect(tela, (0, 255, 0), (menu_x, menu_y, menu_largura, menu_altura), 3)
        
        # Título
        titulo = render_text("DESBLOQUEIOS EXCLUSIVOS", 28, (0, 255, 100), bold=True, pixel_style=True)
        tela.blit(titulo, (menu_x + (menu_largura - titulo.get_width()) // 2, menu_y + 20))
        
        # Desenhar desbloqueios disponíveis
        y_inicio = menu_y + 100
        altura_item = 80
        espacamento = 10
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for i, desbloqueio in enumerate(self.desbloqueios_disponiveis):
            item_y = y_inicio + i * (altura_item + espacamento)
            item_rect = pygame.Rect(menu_x + 20, item_y, menu_largura - 40, altura_item)
            
            # Verificar hover
            hover = item_rect.collidepoint(mouse_x, mouse_y)
            cor_fundo = (20, 50, 20, 200) if hover else (10, 30, 10, 200)
            cor_borda = (0, 255, 0) if hover else (0, 200, 0)
            
            # Fundo do item
            overlay_item = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
            overlay_item.fill(cor_fundo)
            tela.blit(overlay_item, item_rect.topleft)
            pygame.draw.rect(tela, cor_borda, item_rect, 2)
            
            # Nome do desbloqueio
            nome = desbloqueio['nome']
            if desbloqueio['ja_desbloqueado']:
                nome += " [DESBLOQUEADO]"
            nome_texto = render_text(nome, 20, (0, 255, 150) if not desbloqueio['ja_desbloqueado'] else (150, 150, 150), bold=True, pixel_style=True)
            tela.blit(nome_texto, (item_rect.x + 10, item_rect.y + 10))
            
            # Descrição (truncada para caber)
            desc_curta = desbloqueio['descricao'][:80] + "..." if len(desbloqueio['descricao']) > 80 else desbloqueio['descricao']
            desc_texto = render_text(desc_curta, 14, (200, 255, 200), bold=False, pixel_style=True)
            tela.blit(desc_texto, (item_rect.x + 10, item_rect.y + 35))
            
            # Preço
            if not desbloqueio['ja_desbloqueado']:
                preco_texto = render_text(f"${desbloqueio['preco']:,}", 18, (255, 255, 0), bold=True, pixel_style=True)
                tela.blit(preco_texto, (item_rect.right - preco_texto.get_width() - 10, item_rect.y + 10))
        
        # Botão Voltar
        voltar_y = menu_y + menu_altura - 50
        voltar_rect = pygame.Rect(menu_x + menu_largura - 150, voltar_y, 130, 35)
        hover_voltar = voltar_rect.collidepoint(mouse_x, mouse_y)
        cor_voltar = (0, 255, 0) if hover_voltar else (0, 200, 0)
        pygame.draw.rect(tela, (0, 0, 0), voltar_rect)
        pygame.draw.rect(tela, cor_voltar, voltar_rect, 2)
        voltar_texto = render_text("VOLTAR", 16, cor_voltar, bold=True, pixel_style=True)
        tela.blit(voltar_texto, (voltar_rect.x + (voltar_rect.width - voltar_texto.get_width()) // 2, voltar_rect.y + 8))
    
    def fechar(self):
        """Fecha o diálogo do Pixel"""
        self.ativo = False
        self.fase_dialogo = "fechado"
        self.loja_aberta = False
        self.menu_desbloqueios_aberto = False
        self.informacao_selecionada = None
        self.texto_completo = ""
        self.texto_exibido = ""

# Instância global
pixel = Pixel()

