"""Sistema do Glub - Comprador de peças antigas/usadas"""
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

CAMINHO_GLUB_DATA = os.path.join(DIR_PROJETO, "data", "glub.json")

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "glub")
SPRITE_ENCONTRO = os.path.join(CAMINHO_SPRITES, "encontro.png")
SPRITE_CURIOSO = os.path.join(CAMINHO_SPRITES, "curioso.png")
SPRITE_OFERTA = os.path.join(CAMINHO_SPRITES, "oferta.png")
SPRITE_COMPROU = os.path.join(CAMINHO_SPRITES, "comprou.png")
SPRITE_TRISTE = os.path.join(CAMINHO_SPRITES, "triste.png")
SPRITE_DORMINDO = os.path.join(CAMINHO_SPRITES, "dormindo.png")
SPRITE_CHORANDO = os.path.join(CAMINHO_SPRITES, "chorando.png")
SPRITE_COMPRO_FELIZ = os.path.join(CAMINHO_SPRITES, "compro_feliz.png")
SPRITE_SEM_ENTENDER = os.path.join(CAMINHO_SPRITES, "sem_entender.png")

class Glub:
    """Glub - Comprador de peças antigas/usadas por preços altos"""
    
    MULTIPLICADOR_PRECO = 2.5
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_encontro = None
        self.sprite_curioso = None
        self.sprite_oferta = None
        self.sprite_comprou = None
        self.sprite_triste = None
        self.sprite_dormindo = None
        self.sprite_chorando = None
        self.sprite_compro_feliz = None
        self.sprite_sem_entender = None
        self.sprites_carregados = False
        
        self.ativo = False
        self.oferta_atual = None
        self.sprite_atual = None
        self.texto_atual = ""
        self.opcao_selecionada = 0
        self.fase_dialogo = "apresentacao"
        
        self.animacoes_dinheiro = []
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 80.0
        
        self.nome_revelado = False
        
        self.som_compra = None
        self._carregar_sons()
    
    def _carregar_sons(self):
        """Carrega os sons do Glub"""
        try:
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except pygame.error:
                    print("[AVISO] Dispositivo de áudio não disponível. Sons do Glub desabilitados.")
                    self.som_compra = None
                    return
            
            caminho_som_compra = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
            if os.path.exists(caminho_som_compra):
                try:
                    self.som_compra = pygame.mixer.Sound(caminho_som_compra)
                    print(f"✓ Som de compra do Glub carregado")
                except pygame.error:
                    print(f"✗ AVISO: Não foi possível carregar som de compra (áudio indisponível)")
                    self.som_compra = None
            else:
                print(f"✗ AVISO: Som de compra não encontrado: {caminho_som_compra}")
        except Exception as e:
            print(f"ERRO ao carregar sons do Glub: {e}")
            self.som_compra = None
    
    def carregar_sprites(self):
        """Carrega os sprites do Glub"""
        if self.sprites_carregados:
            return
        
        try:
            if not pygame.get_init():
                print("AVISO: pygame não inicializado, tentando inicializar...")
                pygame.init()
            
            print(f"Tentando carregar sprites do Glub de: {CAMINHO_SPRITES}")
            
            if os.path.exists(SPRITE_ENCONTRO):
                self.sprite_encontro = pygame.image.load(SPRITE_ENCONTRO).convert_alpha()
                print(f"✓ Sprite encontro carregado")
            else:
                print(f"✗ AVISO: Sprite encontro não encontrado: {SPRITE_ENCONTRO}")
            
            if os.path.exists(SPRITE_CURIOSO):
                self.sprite_curioso = pygame.image.load(SPRITE_CURIOSO).convert_alpha()
                print(f"✓ Sprite curioso carregado")
            else:
                print(f"✗ AVISO: Sprite curioso não encontrado: {SPRITE_CURIOSO}")
            
            if os.path.exists(SPRITE_OFERTA):
                self.sprite_oferta = pygame.image.load(SPRITE_OFERTA).convert_alpha()
                print(f"✓ Sprite oferta carregado")
            else:
                print(f"✗ AVISO: Sprite oferta não encontrado: {SPRITE_OFERTA}")
            
            if os.path.exists(SPRITE_COMPROU):
                self.sprite_comprou = pygame.image.load(SPRITE_COMPROU).convert_alpha()
                print(f"✓ Sprite comprou carregado")
            else:
                print(f"✗ AVISO: Sprite comprou não encontrado: {SPRITE_COMPROU}")
            
            if os.path.exists(SPRITE_TRISTE):
                self.sprite_triste = pygame.image.load(SPRITE_TRISTE).convert_alpha()
                print(f"✓ Sprite triste carregado")
            else:
                print(f"✗ AVISO: Sprite triste não encontrado: {SPRITE_TRISTE}")
            
            if os.path.exists(SPRITE_DORMINDO):
                self.sprite_dormindo = pygame.image.load(SPRITE_DORMINDO).convert_alpha()
                print(f"✓ Sprite dormindo carregado")
            else:
                print(f"✗ AVISO: Sprite dormindo não encontrado: {SPRITE_DORMINDO}")
            
            if os.path.exists(SPRITE_CHORANDO):
                self.sprite_chorando = pygame.image.load(SPRITE_CHORANDO).convert_alpha()
                print(f"✓ Sprite chorando carregado")
            else:
                print(f"✗ AVISO: Sprite chorando não encontrado: {SPRITE_CHORANDO}")
            
            if os.path.exists(SPRITE_COMPRO_FELIZ):
                self.sprite_compro_feliz = pygame.image.load(SPRITE_COMPRO_FELIZ).convert_alpha()
                print(f"✓ Sprite compro feliz carregado")
            else:
                print(f"✗ AVISO: Sprite compro feliz não encontrado: {SPRITE_COMPRO_FELIZ}")
            
            if os.path.exists(SPRITE_SEM_ENTENDER):
                self.sprite_sem_entender = pygame.image.load(SPRITE_SEM_ENTENDER).convert_alpha()
                print(f"✓ Sprite sem entender carregado")
            else:
                print(f"✗ AVISO: Sprite sem entender não encontrado: {SPRITE_SEM_ENTENDER}")
            
            self.sprites_carregados = True
        except Exception as e:
            print(f"ERRO ao carregar sprites do Glub: {e}")
            import traceback
            traceback.print_exc()
    
    def carregar_estado(self):
        """Carrega o estado do Glub do progresso.json"""
        from core.progresso import gerenciador_progresso
        self.primeira_aparicao_feita = gerenciador_progresso.glub_primeira_aparicao_feita
        self.nome_revelado = gerenciador_progresso.glub_nome_revelado
    
    def salvar_estado(self):
        """Salva o estado do Glub no progresso.json"""
        from core.progresso import gerenciador_progresso
        gerenciador_progresso.glub_primeira_aparicao_feita = self.primeira_aparicao_feita
        gerenciador_progresso.glub_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.salvar()
    
    def verificar_aparecer_primeira_vez(self):
        """Verifica se deve mostrar a primeira aparição do Glub na loja"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Verificar cooldown de 4 dias
        from core.tempo_jogo import gerenciador_tempo
        from core.progresso import gerenciador_progresso
        
        data_atual = gerenciador_tempo.obter_data_atual()
        ultima_aparicao_data = getattr(gerenciador_progresso, 'glub_ultima_aparicao_data', None)
        
        # Calcular dias desde última aparição
        dias_desde_ultima_aparicao = 999  # Valor alto se nunca apareceu
        if ultima_aparicao_data:
            from datetime import datetime
            ultima_aparicao = datetime.strptime(ultima_aparicao_data, "%Y-%m-%d").date()
            dias_desde_ultima_aparicao = (data_atual - ultima_aparicao).days
        
        # Se não é a primeira vez e não passaram 4 dias, não aparecer
        if self.primeira_aparicao_feita and dias_desde_ultima_aparicao < 4:
            print(f"[GLUB] Cooldown ativo: {dias_desde_ultima_aparicao}/4 dias passados")
            return False
        
        if not self.primeira_aparicao_feita:
            # Primeira aparição - mostrar apresentação
            self.ativo = True
            self.fase_dialogo = "apresentacao"
            self.sprite_atual = self.sprite_encontro if self.sprite_encontro else self.sprite_curioso
            texto = "Olá! Eu sou o Glub. Compro peças antigas por um bom preço. Se você tiver alguma peça usada que não precisa mais, eu posso comprar dela por 2.5x o valor que você pagou!"
            self._iniciar_animacao_texto(texto)
            # Atualizar última aparição
            gerenciador_progresso.glub_ultima_aparicao_data = data_atual.strftime("%Y-%m-%d")
            gerenciador_progresso.salvar()
            return True
        else:
            # Já foi apresentado - verificar se pode aparecer (cooldown de 4 dias)
            if dias_desde_ultima_aparicao >= 4:
                # Atualizar última aparição
                gerenciador_progresso.glub_ultima_aparicao_data = data_atual.strftime("%Y-%m-%d")
                gerenciador_progresso.salvar()
                # Abrir loja diretamente
                self.ativo = True
                self.fase_dialogo = "loja"
                return True
            else:
                return False
    
    def ativar_loja(self):
        """Ativa a loja do Glub diretamente (sem verificar cooldown)"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        self.ativo = True
        self.fase_dialogo = "loja"
        return True
    
    def verificar_aparecer(self, tipo_upgrade, nivel_antigo, prefixo_cor):
        """
        Verifica se o Glub deve aparecer após um upgrade ser comprado
        
        Args:
            tipo_upgrade: Tipo do upgrade comprado (ex: 'motor')
            nivel_antigo: Nível antigo da peça (antes do upgrade)
            prefixo_cor: Prefixo do carro que recebeu o upgrade
        """
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Se já está ativo, não aparecer novamente
        if self.ativo:
            return False
        
        # Se não há peça antiga (nível 0), não há nada para vender
        if nivel_antigo <= 0:
            return False
        
        # Primeira vez: 100% de chance de aparecer (tutorial)
        if not self.primeira_aparicao_feita:
            self.gerar_oferta(tipo_upgrade, nivel_antigo)
            self.ativo = True
            self.primeira_aparicao_feita = True
            self.salvar_estado()
            print(f"Glub: Primeira aparição! Oferecendo comprar {tipo_upgrade} nível {nivel_antigo}")
            return True
        
        # Depois da primeira vez: probabilidade baseada no dinheiro do jogador
        dinheiro_atual = gerenciador_progresso.dinheiro
        
        # Quanto menos dinheiro, maior a chance (máximo 80% quando está pobre)
        # Fórmula: chance = 0.1 + (0.7 * (1 - min(dinheiro/50000, 1)))
        # Se tem 0 dinheiro: 80% chance
        # Se tem 50000+ dinheiro: 10% chance
        dinheiro_normalizado = min(dinheiro_atual / 50000.0, 1.0)
        probabilidade = 0.1 + (0.7 * (1.0 - dinheiro_normalizado))
        
        valor_aleatorio = random.random()
        print(f"Glub: Verificando aparecimento (dinheiro=${dinheiro_atual:,}, prob={probabilidade:.2%}, random={valor_aleatorio:.3f})")
        
        if valor_aleatorio <= probabilidade:
            self.gerar_oferta(tipo_upgrade, nivel_antigo)
            self.ativo = True
            print(f"Glub: VAI APARECER! Oferecendo comprar {tipo_upgrade} nível {nivel_antigo}")
            return True
        
        return False
    
    def gerar_oferta(self, tipo_upgrade, nivel_antigo):
        """Gera uma oferta do Glub para comprar a peça antiga"""
        # Calcular preço que o Glub pagará (2.5x o valor original da peça antiga)
        # O valor original é o preço que foi pago para comprar essa peça no nível anterior
        preco_original = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, nivel_antigo - 1)
        preco_oferta = int(preco_original * self.MULTIPLICADOR_PRECO)
        
        self.oferta_atual = {
            'tipo_upgrade': tipo_upgrade,
            'nivel_antigo': nivel_antigo,
            'preco': preco_oferta
        }
        
        # Inicializar diálogo
        self.fase_dialogo = "apresentacao"
        # Escolher aleatoriamente entre "encontro" e "dormindo" para apresentação
        sprites_apresentacao = []
        if self.sprite_encontro:
            sprites_apresentacao.append(self.sprite_encontro)
        if self.sprite_dormindo:
            sprites_apresentacao.append(self.sprite_dormindo)
        if self.sprite_curioso:
            sprites_apresentacao.append(self.sprite_curioso)
        
        if sprites_apresentacao:
            self.sprite_atual = random.choice(sprites_apresentacao)
        texto_completo = self.obter_texto_cumprimento()
        self._iniciar_animacao_texto(texto_completo)
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        
        if not getattr(self, 'nome_revelado', False):
            texto_lower = texto.lower()
            if "glub" in texto_lower or "eu sou" in texto_lower or "meu nome" in texto_lower:
                self.nome_revelado = True
                self.salvar_estado()
    
    def atualizar(self, dt):
        """Atualiza animações do Glub (texto, etc)"""
        if self.ativo:
            self._atualizar_animacao_texto(dt)
    
    def _atualizar_animacao_texto(self, dt):
        """Atualiza animação de texto letra por letra"""
        if len(self.texto_exibido) < len(self.texto_completo):
            caracteres_por_frame = self.velocidade_texto * dt
            self.tempo_animacao += dt
            
            # Calcular quantos caracteres mostrar
            caracteres_para_adicionar = int(self.tempo_animacao * self.velocidade_texto) - len(self.texto_exibido)
            
            if caracteres_para_adicionar > 0:
                self.texto_exibido = self.texto_completo[:len(self.texto_exibido) + caracteres_para_adicionar]
                self.texto_atual = self.texto_exibido
    
    def _completar_animacao_texto(self):
        """Completa a animação de texto de uma vez"""
        if len(self.texto_exibido) < len(self.texto_completo):
            self.texto_exibido = self.texto_completo
            self.texto_atual = self.texto_exibido
    
    def _nome_upgrade(self):
        """Retorna o nome amigável do upgrade"""
        if not self.oferta_atual:
            return "Peça"
        nomes = {
            'motor': 'Motor',
            'filtro_ar': 'Filtro de Ar',
            'ecu': 'ECU',
            'transmissao': 'Transmissão',
            'rodas': 'Rodas',
            'suspensao': 'Suspensão',
            'nitro': 'Nitro'
        }
        return nomes.get(self.oferta_atual.get('tipo_upgrade', ''), self.oferta_atual.get('tipo_upgrade', 'Peça'))
    
    def obter_texto_cumprimento(self):
        """Retorna o texto de cumprimento do Glub"""
        textos = [
            "Ooooh... A atmosfera deste planeta... tem gosto de borracha queimada e óleo diesel. *Delicioso*.",
            "Saudações, unidade bípede sólida. Glub viajou por muitas dobras dimensionais para testemunhar suas... 'geringonças barulhentas'.",
            "Tanta matéria sólida em um só lugar. Tão pouco gel. Fascinante. Vocês, humanos, são colecionadores interessantes.",
            "Esta substância preta e viscosa... é considerada uma iguaria no meu mundo natal. Posso lamber?",
            "Glub detectou uma peça antiga aqui... Que aroma fascinante de metal enferrujado!"
        ]
        return random.choice(textos)
    
    def obter_texto_oferta(self):
        """Retorna o texto da oferta do Glub"""
        if not self.oferta_atual:
            return "Humano! Pare! Eu preciso de peças antigas! Traga suas peças usadas para mim!"
        nome = self._nome_upgrade()
        nivel = self.oferta_atual.get('nivel_antigo', 1)
        preco = self.oferta_atual.get('preco', 0)
        
        textos = [
            f"Humano! Pare! Aquele '{nome} Nível {nivel} Enferrujado' que você ia jogar fora... Ele vibra com energias primitivas! É uma obra de arte! Eu *preciso* absorvê-lo. Te dou ${preco:,} por ele!",
            f"Aquele círculo de borracha gasto... A assimetria! A textura áspera! É magnífico! Eu troco! Eu troco agora! ${preco:,} pelo seu {nome} Nível {nivel}!",
            f"Escute, amigo sólido. Eu estou cheio dessas... pedras amarelas brilhantes e pesadas (ouro) aqui dentro. Elas estão atrapalhando minha flutuação. Você aceita ${preco:,} delas em troca daquela sua {nome} Nível {nivel} quebrada?",
            f"Eu ofereço um negócio justo: você me dá esse {nome} Nível {nivel} sujo de graxa, e eu te dou esse monte de papel verde que vocês usam para trocar por comida. Eu tenho ${preco:,} sobrando.",
            f"Glub precisa daquela {nome} Nível {nivel}! Ela tem o cheiro perfeito de metal crocante! Te pago ${preco:,} por ela!"
        ]
        return random.choice(textos)
    
    def processar_aceitar(self):
        """Processa quando o jogador aceita a oferta do Glub"""
        if not self.oferta_atual:
            return False, "Erro: nenhuma oferta disponível"
        
        preco = self.oferta_atual['preco']
        
        # Adicionar dinheiro ao jogador
        gerenciador_progresso.adicionar_dinheiro(preco)
        
        # Tocar som de compra
        if self.som_compra:
            try:
                self.som_compra.play()
            except Exception as e:
                print(f"Erro ao tocar som de compra: {e}")
        
        # Adicionar animação de "+$X" (centro da tela, subindo)
        self._adicionar_animacao_dinheiro(LARGURA // 2, ALTURA // 2, preco)
        
        # Atualizar sprite e texto
        if self.sprite_comprou:
            self.sprite_atual = self.sprite_comprou
        elif self.sprite_oferta:
            self.sprite_atual = self.sprite_oferta
        
        textos_sucesso = [
            "Bloop! Ahhh... A textura crocante da ferrugem terrestre. Obrigado, amigo sólido.",
            "Sim! Uma nova adição para minha galeria interna. Tome estas moedas inúteis. Não sei por que vocês gostam tanto delas, são tão... sem gosto.",
            "Excelente troca! Eu fiquei com o metal pesado e fedido, e você ficou com o lixo brilhante. Acho que eu te passei a perna! Hehe.",
            "Glub absorveu a peça! Ela agora flutua dentro de mim junto com minhas outras relíquias terrestres. Obrigado!"
        ]
        texto_completo = random.choice(textos_sucesso)
        self._iniciar_animacao_texto(texto_completo)
        self.fase_dialogo = "reacao"
        
        return True, f"Peça vendida por ${preco:,}!"
    
    def processar_recusar(self):
        """Processa quando o jogador recusa a oferta do Glub"""
        if self.sprite_triste:
            self.sprite_atual = self.sprite_triste
        elif self.sprite_curioso:
            self.sprite_atual = self.sprite_curioso
        
        textos_recusa = [
            "Oh... Você deseja manter o peso de papel metálico? Eu entendo. O valor sentimental deve ser imenso para sua espécie.",
            "M-mas... eu te ofereci tantas pedras amarelas! Os manuais diziam que humanos adoram pedras amarelas! Sua lógica confunde o Glub.",
            "Muito bem. Glub vai procurar metal crocante em outro lugar. Adeus, estranho acumulador.",
            "Glub não entende... Por que guardar algo que não funciona mais? Mas respeito sua escolha, humano sólido."
        ]
        texto_completo = random.choice(textos_recusa)
        self._iniciar_animacao_texto(texto_completo)
        self.fase_dialogo = "reacao"
        return True, "Oferta recusada"
    
    def processar_eventos(self, eventos, prefixo_cor=None):
        """Processa eventos de entrada do jogador"""
        if not self.ativo:
            return None
        
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    if self.fase_dialogo == "oferta":
                        self.opcao_selecionada = 0
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    if self.fase_dialogo == "oferta":
                        self.opcao_selecionada = 1
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.fase_dialogo == "apresentacao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Avançar para oferta
                            self.fase_dialogo = "oferta"
                            if self.sprite_oferta:
                                self.sprite_atual = self.sprite_oferta
                            elif self.sprite_curioso:
                                self.sprite_atual = self.sprite_curioso
                            elif self.sprite_encontro:
                                self.sprite_atual = self.sprite_encontro
                            texto_completo = self.obter_texto_oferta()
                            self._iniciar_animacao_texto(texto_completo)
                    elif self.fase_dialogo == "oferta":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Texto completo, agora pode confirmar escolha
                            if self.opcao_selecionada == 0:
                                # Aceitar
                                sucesso, mensagem = self.processar_aceitar()
                                if sucesso:
                                    return "vendido"
                            else:
                                # Recusar
                                self.processar_recusar()
                                return "recusado"
                    elif self.fase_dialogo == "reacao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Fechar diálogo
                            self.fechar()
                            return "fechado"
                elif ev.key == pygame.K_ESCAPE:
                    if self.fase_dialogo == "oferta":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Recusar
                            self.processar_recusar()
                            return "recusado"
                    elif self.fase_dialogo == "reacao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Fechar
                            self.fechar()
                            return "fechado"
                    else:
                        # Fechar
                        self.fechar()
                        return "fechado"
            
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                caixa_altura = int(ALTURA * 0.28)
                caixa_y = ALTURA - caixa_altura - 20
                caixa_largura = LARGURA
                caixa_x = 0
                
                botao_y = caixa_y + caixa_altura - 50
                botao_largura = 180
                botao_altura = 38
                espacamento = 25
                total_largura_botoes = (botao_largura * 2) + espacamento
                botoes_x_inicio = caixa_x + caixa_largura - total_largura_botoes - 30
                
                if self.fase_dialogo == "apresentacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste clique
                    else:
                        # Texto completo, agora pode avançar
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fase_dialogo = "oferta"
                            if self.sprite_oferta:
                                self.sprite_atual = self.sprite_oferta
                            elif self.sprite_curioso:
                                self.sprite_atual = self.sprite_curioso
                            elif self.sprite_encontro:
                                self.sprite_atual = self.sprite_encontro
                            texto_completo = self.obter_texto_oferta()
                            self._iniciar_animacao_texto(texto_completo)
                            self.opcao_selecionada = 0
                
                elif self.fase_dialogo == "oferta":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste clique
                    else:
                        # Só processar clique se o texto estiver completo
                        render_text = _get_render_text()
                        botao_largura_opcao = int(LARGURA * 0.5)
                        botao_x_opcao = (LARGURA - botao_largura_opcao) // 2
                        espacamento_opcao = 25
                        
                        altura_total = 2 * 40 + espacamento_opcao
                        inicio_y_opcao = (ALTURA - altura_total) // 2
                        
                        opcoes = ["ACEITAR", "RECUSAR"]
                        # Calcular todas as hitboxes de forma consistente
                        hitboxes = []
                        y_calc = inicio_y_opcao
                        for opcao_nome in opcoes:
                            texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                            texto_y_calc = y_calc
                            linha_y_calc = texto_y_calc + texto_opcao_temp.get_height() + 5
                            altura_opcao = linha_y_calc - texto_y_calc + 10
                            hitboxes.append(pygame.Rect(botao_x_opcao, texto_y_calc, botao_largura_opcao, altura_opcao))
                            y_calc = linha_y_calc + espacamento_opcao
                        
                        # Verificar clique (usar as hitboxes calculadas)
                        for i, rect in enumerate(hitboxes):
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.opcao_selecionada = i
                                if i == 0:
                                    sucesso, mensagem = self.processar_aceitar()
                                    if sucesso:
                                        return "vendido"
                                else:
                                    self.processar_recusar()
                                    return "recusado"
                                break
                
                elif self.fase_dialogo == "reacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste clique
                    else:
                        # Clicar em qualquer lugar fecha
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fechar()
                            return "fechado"
        
        return None
    
    def _adicionar_animacao_dinheiro(self, x, y, valor):
        """Adiciona uma animação de texto flutuante '+$X'"""
        texto = f"+${valor:,}"
        self.animacoes_dinheiro.append({
            'x': x,
            'y': y,
            'texto': texto,
            'tempo_restante': 2.0,  # 2 segundos
            'alpha': 255
        })
    
    def _atualizar_animacoes_dinheiro(self, dt):
        """Atualiza as animações de dinheiro flutuantes"""
        for anim in self.animacoes_dinheiro[:]:
            anim['tempo_restante'] -= dt
            anim['y'] -= 60 * dt  # Subir 60 pixels por segundo
            # Fade out nos últimos 0.5 segundos
            if anim['tempo_restante'] < 0.5:
                anim['alpha'] = int(255 * (anim['tempo_restante'] / 0.5))
            
            if anim['tempo_restante'] <= 0:
                self.animacoes_dinheiro.remove(anim)
    
    def _desenhar_animacoes_dinheiro(self, tela):
        """Desenha as animações de dinheiro flutuantes"""
        render_text = _get_render_text()
        for anim in self.animacoes_dinheiro:
            # Cor verde (dinheiro ganho)
            texto_surface = render_text(anim['texto'], 36, (0, 200, 0), bold=True, pixel_style=False)
            # Aplicar alpha
            texto_surface.set_alpha(anim['alpha'])
            # Centralizar texto
            texto_x = anim['x'] - texto_surface.get_width() // 2
            texto_y = anim['y'] - texto_surface.get_height() // 2
            tela.blit(texto_surface, (texto_x, texto_y))
    
    def fechar(self):
        """Fecha a interação com o Glub"""
        self.ativo = False
        self.oferta_atual = None
        self.sprite_atual = None
        self.texto_atual = ""
        self.texto_completo = ""
        self.texto_exibido = ""
        self.opcao_selecionada = 0
        self.fase_dialogo = "apresentacao"
        # Não limpar animações aqui - deixar elas terminarem naturalmente
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Glub na tela no estilo visual novel"""
        # Atualizar animação do texto
        self._atualizar_animacao_texto(dt)
        
        # Atualizar animações de dinheiro
        self._atualizar_animacoes_dinheiro(dt)
        
        if not self.ativo:
            self._desenhar_animacoes_dinheiro(tela)
            return
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        if not self.sprite_atual:
            # Escolher sprite padrão se não houver um definido
            if self.sprite_encontro:
                self.sprite_atual = self.sprite_encontro
            elif self.sprite_dormindo:
                self.sprite_atual = self.sprite_dormindo
            elif self.sprite_curioso:
                self.sprite_atual = self.sprite_curioso
            else:
                print(f"ERRO: Nenhum sprite disponível para o Glub!")
                return
        
        # Overlay escuro no fundo (estilo visual novel)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))  # Preto com 140/255 de opacidade (menos escuro)
        tela.blit(overlay, (0, 0))
        
        # Personagem no canto direito (apenas metade do corpo - do peito para cima)
        lado_direito = True
        
        # Tamanho do sprite (personagem grande, mas só metade do corpo)
        sprite_altura_max = 400  # Altura para mostrar só do peito para cima
        sprite_largura_max = 350
        
        if self.sprite_atual:
            sprite_original_w = self.sprite_atual.get_width()
            sprite_original_h = self.sprite_atual.get_height()
            
            # Calcular escala mantendo proporção
            escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
            escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
            escala = min(escala_w, escala_h, 1.0)  # Não aumentar além do original
            
            sprite_w = int(sprite_original_w * escala)
            sprite_h = int(sprite_original_h * escala)
            
            sprite_redimensionado = pygame.transform.scale(self.sprite_atual, (sprite_w, sprite_h))
        
        # Posição do sprite no canto direito (manter estilo visual novel)
        # Se for o sprite "encontro" ou "dormindo" (deitados), posicionar mais alto
        if self.sprite_atual == self.sprite_encontro or self.sprite_atual == self.sprite_dormindo:
            sprite_y = ALTURA - sprite_h - 250  # Mais alto para sprites deitados
        else:
            sprite_y = ALTURA - sprite_h - 250  # Posição acima da caixa
        
        if lado_direito:
            sprite_x = LARGURA - sprite_w - 20
        else:
            sprite_x = 20
        
        # Efeito de glow dourado quando estiver na fase de oferta
        if self.fase_dialogo == "oferta" and self.sprite_atual:
            # Criar efeito de glow real com gradiente suave
            glow_radius = 60  # Raio máximo do glow
            num_circles = 15  # Número de círculos concêntricos para gradiente suave
            
            # Calcular centro do sprite
            center_x = sprite_x + sprite_w // 2
            center_y = sprite_y + sprite_h // 2
            
            for i in range(num_circles):
                radius = int(glow_radius * (1.0 - (i / num_circles)))
                alpha = int(80 * (1.0 - (i / num_circles)))
                
                if radius > 0 and alpha > 0:
                    circle_size = radius * 2 + 10
                    circle_surface = pygame.Surface((circle_size, circle_size), pygame.SRCALPHA)
                    circle_center = circle_size // 2
                    
                    pygame.draw.circle(
                        circle_surface,
                        (255, 215, 0, alpha),
                        (circle_center, circle_center),
                        radius
                    )
                    
                    glow_x = center_x - circle_center
                    glow_y = center_y - circle_center
                    tela.blit(circle_surface, (glow_x, glow_y))
        
        # Desenhar sprite do personagem (antes da caixa para ficar por cima)
        if self.sprite_atual:
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        # Determinar cor do contorno baseado no sprite atual
        cor_contorno = (255, 255, 255)  # Branco padrão
        if self.sprite_atual == self.sprite_encontro:
            cor_contorno = (100, 200, 255)  # Azul claro para encontro
        elif self.sprite_atual == self.sprite_curioso:
            cor_contorno = (150, 200, 255)  # Azul médio para curioso
        elif self.sprite_atual == self.sprite_oferta:
            cor_contorno = (255, 215, 0)  # Dourado para oferta
        elif self.sprite_atual == self.sprite_comprou:
            cor_contorno = (100, 255, 100)  # Verde claro para comprou
        elif self.sprite_atual == self.sprite_triste:
            cor_contorno = (150, 150, 200)  # Azul acinzentado para triste
        elif self.sprite_atual == self.sprite_dormindo:
            cor_contorno = (100, 100, 150)  # Azul escuro para dormindo
        elif self.sprite_atual == self.sprite_chorando:
            cor_contorno = (200, 150, 200)  # Roxo claro para chorando
        elif self.sprite_atual == self.sprite_compro_feliz:
            cor_contorno = (100, 255, 150)  # Verde brilhante para compro feliz
        elif self.sprite_atual == self.sprite_sem_entender:
            cor_contorno = (200, 200, 100)  # Amarelo esverdeado para sem entender
        
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, cor_contorno, (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Desenhar nome do personagem
        render_text = _get_render_text()
        nome_display = "???" if not getattr(self, 'nome_revelado', False) else "GLUB"
        nome_texto = render_text(nome_display, 24, (0, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Atualizar animação de texto
        self._atualizar_animacao_texto(dt)
        
        if self.texto_exibido:
            # Quebrar texto em linhas usando render_text para medir largura
            palavras = self.texto_exibido.split(' ')
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                # Usar render_text para medir a largura corretamente
                teste_render = render_text(teste_linha, 18, (255, 255, 255), bold=False, pixel_style=True)
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
                linha_render = render_text(linha, 18, (255, 255, 255), bold=False, pixel_style=True)
                tela.blit(linha_render, (caixa_x + 20, y_texto))
                y_texto += 25
        
        if len(self.texto_exibido) >= len(self.texto_completo):
            indicador = render_text("Pressione ENTER ou clique para continuar...", 16, (200, 200, 200), bold=False, pixel_style=True)
            indicador_x = caixa_x + caixa_largura - indicador.get_width() - 20
            indicador_y = caixa_y + caixa_altura - 30
            tela.blit(indicador, (indicador_x, indicador_y))
        
        # Botões de escolha (dentro da caixa, no canto direito inferior)
        botao_y = caixa_y + caixa_altura - 50
        botao_largura = 180
        botao_altura = 38
        espacamento = 25
        
        # Posicionar botões no canto direito da caixa
        total_largura_botoes = (botao_largura * 2) + espacamento
        botoes_x_inicio = caixa_x + caixa_largura - total_largura_botoes - 30
        
        # Só exibir opções se o texto estiver completo
        if self.fase_dialogo == "oferta" and len(self.texto_exibido) >= len(self.texto_completo):
            # FASE 2: Opções no meio da tela (apenas texto com linha embaixo)
            opcoes = ["ACEITAR", "RECUSAR"]
            espacamento = 25
            botao_largura_opcao = int(LARGURA * 0.5)  # 50% da largura da tela
            botao_x_opcao = (LARGURA - botao_largura_opcao) // 2  # Centralizado
            
            # Calcular posição Y para centralizar verticalmente
            altura_total = len(opcoes) * 40 + (len(opcoes) - 1) * espacamento
            inicio_y_opcao = (ALTURA - altura_total) // 2
            y_atual = inicio_y_opcao
            
            # Obter posição do mouse para hover
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Primeiro, calcular todas as hitboxes de forma consistente
            hitboxes = []
            y_calc = inicio_y_opcao
            for opcao_nome in opcoes:
                texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                texto_y_calc = y_calc
                linha_y_calc = texto_y_calc + texto_opcao_temp.get_height() + 5
                altura_opcao = linha_y_calc - texto_y_calc + 10
                hitboxes.append(pygame.Rect(botao_x_opcao, texto_y_calc, botao_largura_opcao, altura_opcao))
                y_calc = linha_y_calc + espacamento
            
            # Determinar qual opção está sob o mouse (apenas uma)
            opcao_hover = None
            for i, rect in enumerate(hitboxes):
                if rect.collidepoint(mouse_x, mouse_y):
                    opcao_hover = i
                    break  # Primeira opção encontrada ganha (evita sobreposição)
            
            # Verificar se mouse está sobre qualquer opção
            mouse_sobre_qualquer_opcao = opcao_hover is not None
            
            # Agora desenhar as opções
            y_atual = inicio_y_opcao
            for i, opcao_nome in enumerate(opcoes):
                # Calcular área clicável (para hover e clique)
                texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                texto_opcao_y = y_atual
                linha_y = texto_opcao_y + texto_opcao_temp.get_height() + 5
                
                # Verificar hover (usar a hitbox calculada anteriormente)
                hover = (opcao_hover == i)
                
                # Cor do texto: hover tem prioridade, senão mostrar seleção por teclado
                if hover:
                    cor_texto = (255, 255, 255)  # Branco quando hover
                    cor_linha = (220, 220, 220)  # Cinza mais claro no hover
                elif i == self.opcao_selecionada and not mouse_sobre_qualquer_opcao:
                    cor_texto = (255, 255, 255)  # Branco quando selecionado por teclado (sem mouse)
                    cor_linha = (200, 200, 200)  # Cinza claro
                else:
                    cor_texto = (180, 180, 180)  # Cinza quando não selecionado
                    cor_linha = (100, 100, 100)  # Cinza escuro
                
                # Desenhar texto da opção (centralizado)
                texto_opcao = render_text(opcao_nome, 24, cor_texto, bold=False, pixel_style=False)
                texto_opcao_x = botao_x_opcao + (botao_largura_opcao - texto_opcao.get_width()) // 2  # Centralizado
                tela.blit(texto_opcao, (texto_opcao_x, texto_opcao_y))
                
                # Desenhar linha embaixo do texto (mais fina e menor, centralizada)
                linha_largura = botao_largura_opcao - 80  # Menor que antes (era -40)
                linha_x = botao_x_opcao + (botao_largura_opcao - linha_largura) // 2  # Centralizada
                pygame.draw.line(tela, cor_linha, (linha_x, linha_y), (linha_x + linha_largura, linha_y), 1)  # Espessura 1 (era 2)
                
                y_atual = linha_y + espacamento
        
        # Não desenhar botão FECHAR - o jogador clica na caixa para fechar
        
        # Desenhar animações de dinheiro
        self._desenhar_animacoes_dinheiro(tela)

# Instância global
glub = Glub()

