import pygame
import random
import os
import json
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso

CAMINHO_SOM_COMPRA = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
CAMINHO_SOM_FAIL = os.path.join(DIR_PROJETO, "assets", "sounds", "fail", "falha.mp3")

def _get_render_text():
    from core.menu import render_text
    return render_text

CAMINHO_MERCADOR_DATA = os.path.join(DIR_PROJETO, "data", "mercador_alien.json")

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "slick")
SPRITE_CUMPRIMENTO = os.path.join(CAMINHO_SPRITES, "cumprimento.png")
SPRITE_OFERTA = os.path.join(CAMINHO_SPRITES, "oferta.png")
SPRITE_GOLPE = os.path.join(CAMINHO_SPRITES, "golpe.png")
SPRITE_VENDEU = os.path.join(CAMINHO_SPRITES, "vendeu.png")
SPRITE_BRAVO = os.path.join(CAMINHO_SPRITES, "bravo.png")
SPRITE_ENFURECIDO = os.path.join(CAMINHO_SPRITES, "enfurecido.png")

CAMINHO_FUNDO_POS_CORRIDA = os.path.join(DIR_PROJETO, "assets", "images", "ui", "pos_corrida.png")

class MercadorAlien:
    """Mercador alien que aparece ocasionalmente oferecendo upgrades especiais"""
    
    PROBABILIDADE_APOS_CORRIDA = 0.30
    PROBABILIDADE_AO_UPGRADE = 0.20
    
    COOLDOWN_MINIMO = 3
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_cumprimento = None
        self.sprite_oferta = None
        self.sprite_golpe = None
        self.sprite_vendeu = None
        self.sprite_bravo = None
        self.sprite_enfurecido = None
        self.sprites_carregados = False
        
        self.ativo = False
        self.oferta_atual = None
        self.sprite_atual = None
        self.texto_atual = ""
        self.opcao_selecionada = 0
        self.fase_dialogo = "apresentacao"
        self.contexto_atual = "corrida"
        
        self.fundo_pos_corrida = None
        
        self.animacoes_dinheiro = []
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 80.0
        
        self.nome_revelado = False
        
        self.som_compra = None
        self.som_fail = None
        self._carregar_sons()
        
    def _carregar_sons(self):
        """Carrega os sons do mercador"""
        try:
            # Verificar se o mixer está inicializado
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except pygame.error:
                    # Se não conseguir inicializar, não há dispositivo de áudio
                    print("[AVISO] Dispositivo de áudio não disponível. Sons do mercador desabilitados.")
                    self.som_compra = None
                    self.som_fail = None
                    return
            
            print(f"Tentando carregar som de compra de: {CAMINHO_SOM_COMPRA}")
            print(f"Arquivo existe? {os.path.exists(CAMINHO_SOM_COMPRA)}")
            if os.path.exists(CAMINHO_SOM_COMPRA):
                try:
                    self.som_compra = pygame.mixer.Sound(CAMINHO_SOM_COMPRA)
                    print(f"[OK] Som de compra carregado: {CAMINHO_SOM_COMPRA}")
                except pygame.error:
                    print(f"[AVISO] Não foi possível carregar som de compra (áudio indisponível)")
                    self.som_compra = None
            else:
                print(f"[AVISO] Som de compra nao encontrado: {CAMINHO_SOM_COMPRA}")
            
            print(f"Tentando carregar som de fail de: {CAMINHO_SOM_FAIL}")
            print(f"Arquivo existe? {os.path.exists(CAMINHO_SOM_FAIL)}")
            if os.path.exists(CAMINHO_SOM_FAIL):
                try:
                    self.som_fail = pygame.mixer.Sound(CAMINHO_SOM_FAIL)
                    print(f"[OK] Som de fail carregado: {CAMINHO_SOM_FAIL}")
                except pygame.error:
                    print(f"[AVISO] Não foi possível carregar som de fail (áudio indisponível)")
                    self.som_fail = None
            else:
                print(f"[AVISO] Som de fail nao encontrado: {CAMINHO_SOM_FAIL}")
        except Exception as e:
            print(f"ERRO ao carregar sons do mercador: {e}")
            self.som_compra = None
            self.som_fail = None
    
    def _garantir_sons_carregados(self):
        """Garante que os sons estão carregados (carrega se necessário)"""
        if self.som_compra is None or self.som_fail is None:
            if pygame.mixer.get_init():
                self._carregar_sons()
    
    def carregar_sprites(self):
        """Carrega os sprites do mercador"""
        if self.sprites_carregados:
            if self.fundo_pos_corrida is None:
                self._carregar_fundo_pos_corrida()
            return
        
        try:
            if not pygame.get_init():
                print("AVISO: pygame não inicializado, tentando inicializar...")
                pygame.init()
            
            print(f"Tentando carregar sprites do mercador de: {CAMINHO_SPRITES}")
            print(f"DIR_PROJETO: {DIR_PROJETO}")
            print(f"Pasta existe? {os.path.exists(CAMINHO_SPRITES)}")
            
            if os.path.exists(SPRITE_CUMPRIMENTO):
                self.sprite_cumprimento = pygame.image.load(SPRITE_CUMPRIMENTO).convert_alpha()
                print(f"[OK] Sprite cumprimento carregado: {SPRITE_CUMPRIMENTO} ({self.sprite_cumprimento.get_size()})")
            else:
                print(f"[AVISO] Sprite cumprimento nao encontrado: {SPRITE_CUMPRIMENTO}")
            
            if os.path.exists(SPRITE_OFERTA):
                self.sprite_oferta = pygame.image.load(SPRITE_OFERTA).convert_alpha()
                print(f"[OK] Sprite oferta carregado: {SPRITE_OFERTA} ({self.sprite_oferta.get_size()})")
            else:
                print(f"[AVISO] Sprite oferta nao encontrado: {SPRITE_OFERTA}")
            
            if os.path.exists(SPRITE_GOLPE):
                self.sprite_golpe = pygame.image.load(SPRITE_GOLPE).convert_alpha()
                print(f"[OK] Sprite golpe carregado: {SPRITE_GOLPE} ({self.sprite_golpe.get_size()})")
            else:
                print(f"[AVISO] Sprite golpe nao encontrado: {SPRITE_GOLPE}")
            
            if os.path.exists(SPRITE_VENDEU):
                self.sprite_vendeu = pygame.image.load(SPRITE_VENDEU).convert_alpha()
                print(f"[OK] Sprite vendeu carregado: {SPRITE_VENDEU} ({self.sprite_vendeu.get_size()})")
            else:
                print(f"[AVISO] Sprite vendeu nao encontrado: {SPRITE_VENDEU}")
            
            if os.path.exists(SPRITE_BRAVO):
                self.sprite_bravo = pygame.image.load(SPRITE_BRAVO).convert_alpha()
                print(f"[OK] Sprite bravo carregado: {SPRITE_BRAVO} ({self.sprite_bravo.get_size()})")
            else:
                print(f"[AVISO] Sprite bravo nao encontrado: {SPRITE_BRAVO}")
            
            if os.path.exists(SPRITE_ENFURECIDO):
                self.sprite_enfurecido = pygame.image.load(SPRITE_ENFURECIDO).convert_alpha()
                print(f"[OK] Sprite enfurecido carregado: {SPRITE_ENFURECIDO} ({self.sprite_enfurecido.get_size()})")
            else:
                print(f"[AVISO] Sprite enfurecido nao encontrado: {SPRITE_ENFURECIDO}")
            
            self.sprites_carregados = True
            
            self._carregar_fundo_pos_corrida()
        except Exception as e:
            print(f"ERRO ao carregar sprites do mercador: {e}")
            import traceback
            traceback.print_exc()
    
    def _carregar_fundo_pos_corrida(self):
        """Carrega o fundo pós-corrida se existir"""
        try:
            if os.path.exists(CAMINHO_FUNDO_POS_CORRIDA):
                self.fundo_pos_corrida = pygame.image.load(CAMINHO_FUNDO_POS_CORRIDA).convert()
                # Redimensionar para a resolução atual se necessário
                if self.fundo_pos_corrida.get_size() != (LARGURA, ALTURA):
                    self.fundo_pos_corrida = pygame.transform.scale(self.fundo_pos_corrida, (LARGURA, ALTURA))
                print(f"[OK] Fundo pos-corrida carregado: {CAMINHO_FUNDO_POS_CORRIDA}")
            else:
                print(f"[AVISO] Fundo pos-corrida nao encontrado: {CAMINHO_FUNDO_POS_CORRIDA}")
        except Exception as e:
            print(f"ERRO ao carregar fundo pós-corrida: {e}")
    
    def carregar_estado(self):
        """Carrega o estado do mercador do progresso.json"""
        from core.progresso import gerenciador_progresso
        self.ultima_aparicao = gerenciador_progresso.mercador_ultima_aparicao
        self.contador_eventos = gerenciador_progresso.mercador_contador_eventos
        self.nome_revelado = gerenciador_progresso.mercador_nome_revelado
    
    def salvar_estado(self):
        """Salva o estado do mercador no progresso.json"""
        from core.progresso import gerenciador_progresso
        gerenciador_progresso.mercador_ultima_aparicao = self.ultima_aparicao
        gerenciador_progresso.mercador_contador_eventos = self.contador_eventos
        gerenciador_progresso.mercador_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.salvar()
    
    def verificar_aparecer(self, contexto="corrida"):
        """Verifica se o mercador deve aparecer"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.contador_eventos += 1
        
        eventos_desde_ultima = self.contador_eventos - self.ultima_aparicao
        if eventos_desde_ultima < self.COOLDOWN_MINIMO:
            print(f"Mercador: Cooldown ativo ({eventos_desde_ultima}/{self.COOLDOWN_MINIMO})")
            return False
        
        probabilidade = self.PROBABILIDADE_APOS_CORRIDA if contexto == "corrida" else self.PROBABILIDADE_AO_UPGRADE
        valor_aleatorio = random.random()
        print(f"Mercador: Verificando aparecimento (contexto={contexto}, prob={probabilidade:.2%}, random={valor_aleatorio:.3f})")
        if valor_aleatorio > probabilidade:
            print(f"Mercador: Não apareceu (random > probabilidade)")
            return False
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        print(f"Mercador: VAI APARECER! Gerando oferta...")
        self.gerar_oferta()
        self.ativo = True
        self.contexto_atual = contexto
        self.ultima_aparicao = self.contador_eventos
        self.salvar_estado()
        print(f"Mercador: Ativado! Sprite atual: {self.sprite_atual is not None}, contexto: {self.contexto_atual}")
        return True
    
    def gerar_oferta(self):
        """Gera uma oferta aleatória do mercador"""
        # 60% chance de oferta boa, 40% chance de golpe
        e_golpe = random.random() < 0.40
        
        tipos_upgrade = ['motor', 'filtro_ar', 'ecu', 'transmissao', 'rodas', 'suspensao', 'nitro']
        tipo_upgrade = random.choice(tipos_upgrade)
        
        if e_golpe:
            # Golpe: oferece 1 upgrade normal por preço muito alto
            nivel_base = random.randint(0, 3)  # Nível base aleatório
            preco_normal = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, nivel_base)
            preco_oferta = int(preco_normal * random.uniform(2.5, 4.0))  # 2.5x a 4x mais caro
            
            self.oferta_atual = {
                'tipo': 'golpe',
                'tipo_upgrade': tipo_upgrade,
                'nivel': nivel_base + 1,
                'preco': preco_oferta,
                'valor_real': preco_normal,
                'carro_especifico': None  # Aplica a qualquer carro
            }
        else:
            # Oferta boa: upgrade múltiplo ou upgrade especial
            tipo_oferta = random.choice(['multi_upgrade', 'upgrade_especial'])
            
            if tipo_oferta == 'multi_upgrade':
                # Oferece 2-3 upgrades de uma vez por preço razoável
                num_upgrades = random.randint(2, 3)
                nivel_base = random.randint(0, 2)
                preco_base = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, nivel_base)
                preco_total = int(preco_base * num_upgrades * 0.7)  # 30% desconto
                
                self.oferta_atual = {
                    'tipo': 'multi_upgrade',
                    'tipo_upgrade': tipo_upgrade,
                    'nivel': nivel_base + 1,
                    'quantidade': num_upgrades,
                    'preco': preco_total,
                    'carro_especifico': None
                }
            else:
                # Upgrade especial: aumenta múltiplos atributos
                preco_base = gerenciador_progresso.calcular_preco_upgrade(tipo_upgrade, 2)
                preco_oferta = int(preco_base * 1.5)
                
                self.oferta_atual = {
                    'tipo': 'upgrade_especial',
                    'tipo_upgrade': tipo_upgrade,
                    'nivel': 3,  # Nível alto
                    'preco': preco_oferta,
                    'bonus_extra': True,  # Dá bônus em múltiplos atributos
                    'carro_especifico': None
                }
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        if self.sprite_cumprimento:
            self.sprite_atual = self.sprite_cumprimento
            print(f"Mercador: Sprite cumprimento definido como atual")
        elif self.sprite_oferta:
            self.sprite_atual = self.sprite_oferta
            print(f"Mercador: Usando sprite_oferta como fallback")
        elif self.sprite_golpe:
            self.sprite_atual = self.sprite_golpe
            print(f"Mercador: Usando sprite_golpe como fallback")
        elif self.sprite_vendeu:
            self.sprite_atual = self.sprite_vendeu
            print(f"Mercador: Usando sprite_vendeu como fallback")
        else:
            self.sprite_atual = None
            print(f"AVISO: Nenhum sprite disponivel para o mercador!")
        texto_completo = self.obter_texto_cumprimento()
        self._iniciar_animacao_texto(texto_completo)
        self.opcao_selecionada = 0
        self.fase_dialogo = "apresentacao"
        print(f"Mercador: Oferta gerada - Tipo: {self.oferta_atual['tipo']}, Preço: ${self.oferta_atual['preco']:,}")
    
    def obter_texto_cumprimento(self):
        """Retorna texto de cumprimento aleatório"""
        textos = [
            "Saudações, forma de vida baseada em carbono. Meus sensores indicam que você está precisando de uma... vantagem competitiva.",
            "Psiu. Ei, você aí no veículo terrestre primitivo. Tenho uma oportunidade de negócios que vai explodir sua mente. Literalmente, se você instalar errado.",
            "Ah, o cheiro de borracha queimada e desespero financeiro... Meus aromas favoritos. Vamos negociar, humano?",
            "Olha quem apareceu. O piloto com mais sorte do que juízo. Hoje é seu dia de sorte... talvez.",
            "Eu não deveria estar vendendo isso aqui nesse planeta atrasado, mas... digamos que eu preciso liberar espaço no meu compartimento de carga rápido."
        ]
        return random.choice(textos)
    
    def obter_texto_oferta(self):
        """Retorna texto da oferta baseado no tipo"""
        if self.oferta_atual['tipo'] == 'golpe':
            textos = [
                f"Contemple! Um {self._nome_upgrade()} recuperado das minas de plasma de Centauri Prime. "
                f"O que ele faz? Ah, meu amigo, descobrir é metade da diversão. Por ${self.oferta_atual['preco']:,}.",
                
                f"Esta peça caiu de uma nave de transporte Imperial. É tecnologia de ponta. "
                f"Ou talvez lixo espacial radioativo. Só há um jeito de saber. ${self.oferta_atual['preco']:,}. Vai arriscar?",
                
                f"Tenho aqui um {self._nome_upgrade()} 'levemente usado'. O dono anterior? "
                f"Digamos que ele não precisa mais dela depois daquela curva na volta 7. ${self.oferta_atual['preco']:,}. Interessado?",
                
                f"A sorte favorece os audazes, terráqueo. Este {self._nome_upgrade()} contém o destino da sua próxima corrida. "
                f"O custo é ${self.oferta_atual['preco']:,}, mas a recompensa pode ser... astronômica.",
                
                f"Isso aqui? É um protótipo de {self._nome_upgrade()}. Se funcionar, você voa. "
                f"Se não funcionar... bem, espero que você tenha um bom seguro. ${self.oferta_atual['preco']:,}.",
                
                f"Vejo que você tem um olho refinado! Este '{self._nome_upgrade()} Quântico' é raríssimo. "
                f"Para você, meu amigo? Preço especial de ${self.oferta_atual['preco']:,}. Uma pechincha!",
                
                f"Não deixe o preço te assustar. Isso aqui não é uma peça, é um investimento! "
                f"Vai valorizar assim que você cruzar a linha de chegada em primeiro! ${self.oferta_atual['preco']:,}.",
                
                f"Garantia? A garantia sou eu te dizendo que é incrível! Confia no Slick. "
                f"Eu nunca mentiria para um cliente preferencial... ${self.oferta_atual['preco']:,}.",
                
                f"Isso aqui foi usado pelo Grande Campeão Zorg na Copa Galáctica. "
                f"Está impregnado com a essência da vitória! ${self.oferta_atual['preco']:,}!"
            ]
        elif self.oferta_atual['tipo'] == 'multi_upgrade':
            textos = [
                f"Olha, estou me sentindo generoso hoje. Talvez a atmosfera da Terra esteja afetando meus circuitos lógicos. "
                f"Leva {self.oferta_atual['quantidade']}x {self._nome_upgrade()} por ${self.oferta_atual['preco']:,}. Preço de custo.",
                
                f"Shhh. Fala baixo. Eu 'adquiri' este lote de {self._nome_upgrade()} de elite e preciso me livrar deles "
                f"antes que a Polícia Galáctica rastreie minha nave. {self.oferta_atual['quantidade']}x por ${self.oferta_atual['preco']:,}. É pegar ou largar.",
                
                f"Não conte para ninguém que eu fiz isso. Arruinaria minha reputação de mercenário implacável. "
                f"Mas toma, {self.oferta_atual['quantidade']}x {self._nome_upgrade()} por ${self.oferta_atual['preco']:,}. Você vai precisar.",
                
                f"Hoje eu acordei de bom humor. Vou te vender {self.oferta_atual['quantidade']}x {self._nome_upgrade()} "
                f"Classe S pelo preço de Classe C. ${self.oferta_atual['preco']:,}. Não me faça arrepender disso."
            ]
        else:  # upgrade_especial
            textos = [
                f"Contemple! Um artefato recuperado das minas de plasma de Centauri Prime. "
                f"{self._nome_upgrade()} Especial que melhora MÚLTIPLOS aspectos do seu carro. "
                f"O que ele faz? Descobrir é metade da diversão. ${self.oferta_atual['preco']:,}.",
                
                f"Esta peça caiu de uma nave de transporte Imperial. É tecnologia de ponta. "
                f"{self._nome_upgrade()} Especial com bônus extras por ${self.oferta_atual['preco']:,}. "
                "Só há um jeito de saber. Vai arriscar?",
                
                f"A sorte favorece os audazes, terráqueo. Este {self._nome_upgrade()} Especial contém o destino da sua próxima corrida. "
                f"O custo é ${self.oferta_atual['preco']:,}, mas a recompensa pode ser... astronômica.",
                
                f"Olha, estou me sentindo generoso hoje. {self._nome_upgrade()} Especial que aumenta "
                f"potência, velocidade E estabilidade por ${self.oferta_atual['preco']:,}. "
                "Não me faça arrepender disso."
            ]
        return random.choice(textos)
    
    def _nome_upgrade(self):
        """Retorna o nome traduzido do upgrade"""
        nomes = {
            'motor': 'Motor',
            'filtro_ar': 'Filtro de Ar',
            'ecu': 'ECU',
            'transmissao': 'Transmissão',
            'rodas': 'Rodas',
            'suspensao': 'Suspensão',
            'nitro': 'Nitro'
        }
        return nomes.get(self.oferta_atual['tipo_upgrade'], 'Upgrade')
    
    def processar_aceitar(self, prefixo_cor=None):
        """Processa quando o jogador aceita a oferta"""
        if not self.oferta_atual:
            return False, "Erro: nenhuma oferta disponível"
        
        preco = self.oferta_atual['preco']
        
        if not gerenciador_progresso.tem_dinheiro(preco):
            self.sprite_atual = self.sprite_golpe
            texto_completo = "Você não tem dinheiro suficiente! Que pena... talvez na próxima vez!"
            self._iniciar_animacao_texto(texto_completo)
            return False, "Dinheiro insuficiente"
        
        self._garantir_sons_carregados()
        
        e_golpe = self.oferta_atual['tipo'] == 'golpe'
        if e_golpe:
            if self.som_fail:
                try:
                    self.som_fail.play()
                except Exception as e:
                    print(f"Erro ao tocar som de fail: {e}")
        else:
            if self.som_compra:
                try:
                    self.som_compra.play()
                except Exception as e:
                    print(f"Erro ao tocar som de compra: {e}")
        
        gerenciador_progresso.remover_dinheiro(preco)
        
        self._adicionar_animacao_dinheiro(LARGURA // 2, ALTURA // 2, preco)
        
        sucesso = True
        mensagem = ""
        
        if self.oferta_atual['tipo'] == 'golpe':
            upgrade_aplicado = False
            if prefixo_cor:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'])
                if nivel_atual < 5:
                    gerenciador_progresso.comprar_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'], 0)  # Já pagou
                    upgrade_aplicado = True
                    mensagem = f"Upgrade de {self._nome_upgrade()} aplicado! (Você pagou mais do que deveria...)"
            else:
                carros = ['Car1', 'Car2', 'Car3', 'Car4', 'Car5', 'Car6', 'Car7', 'Car8', 'Car9', 'Car10', 'Car11', 'Car12', 'Car13']
                for carro in carros:
                    if gerenciador_progresso.esta_desbloqueado(carro):
                        nivel_atual = gerenciador_progresso.obter_upgrade(carro, self.oferta_atual['tipo_upgrade'])
                        if nivel_atual < 5:
                            gerenciador_progresso.comprar_upgrade(carro, self.oferta_atual['tipo_upgrade'], 0)
                            upgrade_aplicado = True
                            mensagem = f"Upgrade de {self._nome_upgrade()} aplicado ao {carro}! (Você pagou mais do que deveria...)"
                            break
            if not upgrade_aplicado:
                mensagem = f"Upgrade de {self._nome_upgrade()} não pôde ser aplicado (nível máximo atingido), mas o dinheiro já foi cobrado!"
        
        elif self.oferta_atual['tipo'] == 'multi_upgrade':
            aplicados = 0
            if prefixo_cor:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'])
                for _ in range(self.oferta_atual['quantidade']):
                    if nivel_atual < 5:
                        gerenciador_progresso.comprar_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'], 0)
                        nivel_atual += 1
                        aplicados += 1
                    else:
                        break
                if aplicados > 0:
                    mensagem = f"{aplicados} upgrades de {self._nome_upgrade()} aplicados!"
                else:
                    mensagem = f"Upgrades não puderam ser aplicados (nível máximo atingido), mas o dinheiro já foi cobrado!"
            else:
                carros = ['Car1', 'Car2', 'Car3', 'Car4', 'Car5', 'Car6', 'Car7', 'Car8', 'Car9', 'Car10', 'Car11', 'Car12', 'Car13']
                for carro in carros:
                    if gerenciador_progresso.esta_desbloqueado(carro):
                        nivel_atual = gerenciador_progresso.obter_upgrade(carro, self.oferta_atual['tipo_upgrade'])
                        for _ in range(self.oferta_atual['quantidade']):
                            if nivel_atual < 5:
                                gerenciador_progresso.comprar_upgrade(carro, self.oferta_atual['tipo_upgrade'], 0)
                                nivel_atual += 1
                                aplicados += 1
                            else:
                                break
                        if aplicados > 0:
                            mensagem = f"{aplicados} upgrades de {self._nome_upgrade()} aplicados ao {carro}!"
                        else:
                            mensagem = f"Upgrades não puderam ser aplicados (nível máximo atingido), mas o dinheiro já foi cobrado!"
                        break
        
        else:
            if prefixo_cor:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'])
                if nivel_atual < 5:
                    gerenciador_progresso.comprar_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'], 0)
                    upgrades_relacionados = {
                        'motor': 'filtro_ar',
                        'filtro_ar': 'ecu',
                        'ecu': 'motor',
                        'transmissao': 'rodas',
                        'rodas': 'suspensao',
                        'suspensao': 'transmissao',
                        'nitro': 'motor'
                    }
                    upgrade_bonus = upgrades_relacionados.get(self.oferta_atual['tipo_upgrade'], 'motor')
                    nivel_bonus = gerenciador_progresso.obter_upgrade(prefixo_cor, upgrade_bonus)
                    if nivel_bonus < 5:
                        gerenciador_progresso.comprar_upgrade(prefixo_cor, upgrade_bonus, 0)
                    sucesso = True
                    mensagem = f"Upgrade especial de {self._nome_upgrade()} aplicado com bônus extra!"
            else:
                carros = ['Car1', 'Car2', 'Car3', 'Car4', 'Car5', 'Car6', 'Car7', 'Car8', 'Car9', 'Car10', 'Car11', 'Car12', 'Car13']
                for carro in carros:
                    if gerenciador_progresso.esta_desbloqueado(carro):
                        nivel_atual = gerenciador_progresso.obter_upgrade(carro, self.oferta_atual['tipo_upgrade'])
                        if nivel_atual < 5:
                            gerenciador_progresso.comprar_upgrade(carro, self.oferta_atual['tipo_upgrade'], 0)
                            upgrades_relacionados = {
                                'motor': 'filtro_ar',
                                'filtro_ar': 'ecu',
                                'ecu': 'motor',
                                'transmissao': 'rodas',
                                'rodas': 'suspensao',
                                'suspensao': 'transmissao',
                                'nitro': 'motor'
                            }
                            upgrade_bonus = upgrades_relacionados.get(self.oferta_atual['tipo_upgrade'], 'motor')
                            nivel_bonus = gerenciador_progresso.obter_upgrade(carro, upgrade_bonus)
                            if nivel_bonus < 5:
                                gerenciador_progresso.comprar_upgrade(carro, upgrade_bonus, 0)
                            sucesso = True
                            mensagem = f"Upgrade especial de {self._nome_upgrade()} aplicado ao {carro} com bônus!"
                            break
        
        if sucesso:
            quantidade = 1
            if self.oferta_atual['tipo'] == 'multi_upgrade':
                quantidade = self.oferta_atual.get('quantidade', 1)
            gerenciador_progresso.registrar_compra_alien(
                self.oferta_atual['tipo'],
                quantidade,
                self.oferta_atual.get('tipo_upgrade')
            )
            
            if self.oferta_atual['tipo'] == 'golpe':
                self.sprite_atual = self.sprite_golpe if self.sprite_golpe else self.sprite_oferta
                textos_sucesso = [
                    "Excelente escolha! Hehe... Você não vai se arrepender. E lembre-se: sem devoluções!",
                    "Negócio fechado. Transfira os créditos antes que eu mude de ideia.",
                    "Um prazer fazer negócios com espécies inferiores. Volte sempre que tiver créditos sobrando."
                ]
            else:
                if self.sprite_vendeu:
                    self.sprite_atual = self.sprite_vendeu
                elif self.sprite_oferta:
                    self.sprite_atual = self.sprite_oferta
                elif self.sprite_cumprimento:
                    self.sprite_atual = self.sprite_cumprimento
                else:
                    self.sprite_atual = self.sprite_golpe
                textos_sucesso = [
                    "Negócio fechado. Transfira os créditos antes que eu mude de ideia.",
                    "Um prazer fazer negócios com espécies inferiores. Volte sempre que tiver créditos sobrando.",
                    "Excelente escolha! Você não vai se arrepender desta vez."
                ]
            texto_completo = random.choice(textos_sucesso)
            self._iniciar_animacao_texto(texto_completo)
        else:
            self.sprite_atual = self.sprite_bravo if self.sprite_bravo else self.sprite_golpe
            texto_completo = "Hmm... parece que não consegui aplicar o upgrade. Mas o dinheiro já foi... que estranho!"
            self._iniciar_animacao_texto(texto_completo)
        
        return sucesso, mensagem
    
    def processar_recusar(self):
        """Processa quando o jogador recusa a oferta"""
        reacao_intensidade = random.random()
        
        if reacao_intensidade < 0.4:
            self.sprite_atual = self.sprite_bravo if self.sprite_bravo else self.sprite_golpe
            textos_recusa = [
                "Bah! Terráqueos não têm visão de futuro. Fique aí com sua carroça lenta. Sua perda!",
                "Tsc. Desperdício de tempo. Saia da minha frente antes que eu vaporize seus pneus com meu laser de serviço.",
                "Tudo bem... mas você está perdendo uma oportunidade única! Sua perda, não minha!"
            ]
        else:
            self.sprite_atual = self.sprite_enfurecido if self.sprite_enfurecido else (self.sprite_bravo if self.sprite_bravo else self.sprite_golpe)
            textos_recusa = [
                "Você ousa recusar uma oferta do grande Slick?! Insolente! Vou vender isso pelo triplo no próximo sistema solar!",
                "Argh! Guarde seus créditos patéticos então. Espero que seu motor exploda na última volta!",
                "Como você DARE recusar?! Eu vou... eu vou... AHHH! Sua perda, humano estúpido!"
            ]
        
        texto_completo = random.choice(textos_recusa)
        self._iniciar_animacao_texto(texto_completo)
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.texto_atual = ""
        self.tempo_animacao = 0.0
        
        if not getattr(self, 'nome_revelado', False):
            texto_lower = texto.lower()
            if "slick" in texto_lower or "eu sou" in texto_lower or "meu nome" in texto_lower:
                self.nome_revelado = True
                self.salvar_estado()
    
    def _atualizar_animacao_texto(self, dt):
        """Atualiza animação de texto letra por letra"""
        if not self.texto_completo:
            return
        
        if len(self.texto_exibido) < len(self.texto_completo):
            self.tempo_animacao += dt
            
            caracteres_esperados = int(self.tempo_animacao * self.velocidade_texto)
            caracteres_para_adicionar = caracteres_esperados - len(self.texto_exibido)
            
            if caracteres_para_adicionar > 0:
                max_por_frame = max(1, int(self.velocidade_texto * dt * 5))
                caracteres_para_adicionar = min(caracteres_para_adicionar, max_por_frame)
                
                novo_tamanho = min(len(self.texto_exibido) + caracteres_para_adicionar, len(self.texto_completo))
                self.texto_exibido = self.texto_completo[:novo_tamanho]
                self.texto_atual = self.texto_exibido
        else:
            if self.texto_atual != self.texto_exibido:
                self.texto_atual = self.texto_exibido
    
    def _completar_animacao_texto(self):
        """Completa a animação de texto de uma vez"""
        if len(self.texto_exibido) < len(self.texto_completo):
            self.texto_exibido = self.texto_completo
            self.texto_atual = self.texto_exibido
    
    def _adicionar_animacao_dinheiro(self, x, y, valor):
        """Adiciona uma animação de texto flutuante '-$X'"""
        self.animacoes_dinheiro.append({
            'x': x,
            'y': y,
            'texto': f"-${valor:,}",
            'tempo': 2.0,  # 2 segundos de duração
            'alpha': 255,
            'velocidade_y': -50  # Pixels por segundo (sobe)
        })
    
    def _atualizar_animacoes_dinheiro(self, dt):
        """Atualiza as animações de dinheiro"""
        for anim in self.animacoes_dinheiro[:]:  # Cópia da lista para poder remover
            anim['tempo'] -= dt
            anim['y'] += anim['velocidade_y'] * dt
            # Fade out gradual
            anim['alpha'] = max(0, int(255 * (anim['tempo'] / 2.0)))
            
            if anim['tempo'] <= 0 or anim['alpha'] <= 0:
                self.animacoes_dinheiro.remove(anim)
    
    def _desenhar_animacoes_dinheiro(self, tela):
        """Desenha as animações de dinheiro flutuantes"""
        render_text = _get_render_text()
        for anim in self.animacoes_dinheiro:
            # Cor vermelha
            texto_surface = render_text(anim['texto'], 36, (200, 0, 0), bold=True, pixel_style=False)
            # Aplicar alpha
            texto_surface.set_alpha(anim['alpha'])
            # Centralizar texto
            texto_x = anim['x'] - texto_surface.get_width() // 2
            texto_y = anim['y'] - texto_surface.get_height() // 2
            tela.blit(texto_surface, (texto_x, texto_y))
    
    def fechar(self):
        """Fecha a interação com o mercador"""
        self.ativo = False
        self.oferta_atual = None
        self.sprite_atual = None
        self.texto_atual = ""
        self.opcao_selecionada = 0
        self.fase_dialogo = "apresentacao"
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do mercador na tela no estilo visual novel"""
        self._atualizar_animacoes_dinheiro(dt)
        
        if not self.ativo:
            self._desenhar_animacoes_dinheiro(tela)
            return
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        if not self.sprite_atual:
            print(f"AVISO: Mercador ativo mas sprite_atual é None! Tentando usar fallback...")
            if self.sprite_cumprimento:
                self.sprite_atual = self.sprite_cumprimento
            elif self.sprite_oferta:
                self.sprite_atual = self.sprite_oferta
            elif self.sprite_golpe:
                self.sprite_atual = self.sprite_golpe
            elif self.sprite_vendeu:
                self.sprite_atual = self.sprite_vendeu
            elif self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            else:
                print(f"ERRO: Nenhum sprite disponivel para o mercador!")
                return
        
        if self.contexto_atual == "corrida" and self.fundo_pos_corrida is not None:
            fundo_redimensionado = pygame.transform.scale(self.fundo_pos_corrida, (LARGURA, ALTURA))
            tela.blit(fundo_redimensionado, (0, 0))
        
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        tela.blit(overlay, (0, 0))
        
        if self.sprite_atual:
            sprite_original_w = self.sprite_atual.get_width()
            sprite_original_h = self.sprite_atual.get_height()
            sprite_novo_w = int(sprite_original_w * 0.7)
            sprite_novo_h = int(sprite_original_h * 0.7)
            sprite_redimensionado = pygame.transform.scale(self.sprite_atual, (sprite_novo_w, sprite_novo_h))
            
            sprite_x = LARGURA // 2 - sprite_novo_w // 2
            sprite_y = int(ALTURA * 0.6) - sprite_novo_h // 2
            
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        cor_contorno = (255, 255, 255)
        if self.sprite_atual == self.sprite_cumprimento:
            cor_contorno = (0, 255, 100)  # Verde para cumprimento
        elif self.sprite_atual == self.sprite_oferta:
            cor_contorno = (100, 150, 255)  # Azul para oferta
        elif self.sprite_atual == self.sprite_golpe:
            cor_contorno = (255, 100, 100)  # Vermelho para golpe
        elif self.sprite_atual == self.sprite_vendeu:
            cor_contorno = (255, 200, 0)  # Amarelo/dourado para vendeu
        elif self.sprite_atual == self.sprite_bravo:
            cor_contorno = (255, 50, 50)
        
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, cor_contorno, (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        render_text = _get_render_text()
        nome_display = "???" if not getattr(self, 'nome_revelado', False) else "SLICK"
        nome_texto = render_text(nome_display, 24, (0, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        self._atualizar_animacao_texto(dt)
        
        if self.texto_exibido:
            palavras = self.texto_exibido.split(' ')
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
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
        
        if self.fase_dialogo == "oferta" and len(self.texto_exibido) >= len(self.texto_completo):
            opcoes = ["ACEITAR", "RECUSAR"]
            espacamento = 25
            botao_largura_opcao = int(LARGURA * 0.5)
            botao_x_opcao = (LARGURA - botao_largura_opcao) // 2
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            altura_total = len(opcoes) * 40 + (len(opcoes) - 1) * espacamento
            inicio_y_opcao = (ALTURA - altura_total) // 2
            y_atual = inicio_y_opcao
            
            for i, opcao_nome in enumerate(opcoes):
                texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                texto_opcao_y = y_atual
                linha_y = texto_opcao_y + texto_opcao_temp.get_height() + 5
                opcao_rect = pygame.Rect(botao_x_opcao, texto_opcao_y, botao_largura_opcao, linha_y - texto_opcao_y + 10)
                
                hover = opcao_rect.collidepoint(mouse_x, mouse_y)
                
                mouse_sobre_qualquer_opcao = False
                for j in range(len(opcoes)):
                    texto_temp = render_text(opcoes[j], 24, (255, 255, 255), bold=False, pixel_style=False)
                    y_temp = inicio_y_opcao + (j * 40) + (j * espacamento)
                    linha_y_temp = y_temp + texto_temp.get_height() + 5
                    rect_temp = pygame.Rect(botao_x_opcao, y_temp, botao_largura_opcao, linha_y_temp - y_temp + 10)
                    if rect_temp.collidepoint(mouse_x, mouse_y):
                        mouse_sobre_qualquer_opcao = True
                        break
                
                if hover:
                    cor_texto = (255, 255, 255)
                    cor_linha = (220, 220, 220)
                elif i == self.opcao_selecionada and not mouse_sobre_qualquer_opcao:
                    cor_texto = (255, 255, 255)
                    cor_linha = (200, 200, 200)
                else:
                    cor_texto = (180, 180, 180)
                    cor_linha = (100, 100, 100)
                
                texto_opcao = render_text(opcao_nome, 24, cor_texto, bold=False, pixel_style=False)
                texto_opcao_x = botao_x_opcao + (botao_largura_opcao - texto_opcao.get_width()) // 2
                tela.blit(texto_opcao, (texto_opcao_x, texto_opcao_y))
                
                linha_largura = botao_largura_opcao - 80
                linha_x = botao_x_opcao + (botao_largura_opcao - linha_largura) // 2
                pygame.draw.line(tela, cor_linha, (linha_x, linha_y), (linha_x + linha_largura, linha_y), 1)
                
                y_atual = linha_y + espacamento
        
        self._desenhar_animacoes_dinheiro(tela)
    
    def processar_eventos(self, eventos, prefixo_cor=None):
        """Processa eventos de input para o diálogo do mercador"""
        if not self.ativo:
            return None
        
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    self.opcao_selecionada = 0
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    self.opcao_selecionada = 1
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.fase_dialogo == "apresentacao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                        else:
                            self.fase_dialogo = "oferta"
                            self.sprite_atual = self.sprite_oferta
                            texto_completo = self.obter_texto_oferta()
                            self._iniciar_animacao_texto(texto_completo)
                            self.opcao_selecionada = 0
                    elif self.fase_dialogo == "oferta":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                        else:
                            if self.opcao_selecionada == 0:
                                sucesso, mensagem = self.processar_aceitar(prefixo_cor)
                                self.fase_dialogo = "reacao"
                            else:
                                self.processar_recusar()
                                self.fase_dialogo = "reacao"
                    elif self.fase_dialogo == "reacao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                        else:
                            self.fechar()
                            if self.oferta_atual and self.sprite_atual == self.sprite_vendeu:
                                return "comprado"
                            elif self.oferta_atual and self.sprite_atual == self.sprite_golpe:
                                return "recusado"
                            else:
                                return "fechado"
                elif ev.key == pygame.K_ESCAPE:
                    if self.fase_dialogo == "oferta":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                        else:
                            self.processar_recusar()
                            self.fase_dialogo = "reacao"
                    elif self.fase_dialogo == "reacao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                        else:
                            self.fechar()
                            if self.oferta_atual and self.sprite_atual == self.sprite_vendeu:
                                return "comprado"
                            elif self.oferta_atual and self.sprite_atual == self.sprite_golpe:
                                return "recusado"
                            else:
                                return "fechado"
                    else:
                        self.fechar()
                        return "fechado"
            
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                caixa_altura = int(ALTURA * 0.35)
                caixa_y = ALTURA - caixa_altura - 20
                caixa_largura = LARGURA
                caixa_x = 0
                
                botao_y = caixa_y + caixa_altura - 50
                botao_largura = 180
                botao_altura = 38
                espacamento = 25
                
                if self.fase_dialogo == "apresentacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fase_dialogo = "oferta"
                            self.sprite_atual = self.sprite_oferta
                            texto_completo = self.obter_texto_oferta()
                            self._iniciar_animacao_texto(texto_completo)
                            self.opcao_selecionada = 0
                
                elif self.fase_dialogo == "oferta":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        render_text = _get_render_text()
                        botao_largura_opcao = int(LARGURA * 0.5)
                        botao_x_opcao = (LARGURA - botao_largura_opcao) // 2
                        espacamento_opcao = 25
                        
                        altura_total = 2 * 40 + espacamento_opcao
                        inicio_y_opcao = (ALTURA - altura_total) // 2
                        
                        opcoes = ["ACEITAR", "RECUSAR"]
                        hitboxes = []
                        y_calc = inicio_y_opcao
                        for opcao_nome in opcoes:
                            texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                            texto_y_calc = y_calc
                            linha_y_calc = texto_y_calc + texto_opcao_temp.get_height() + 5
                            altura_opcao = linha_y_calc - texto_y_calc + 10
                            hitboxes.append(pygame.Rect(botao_x_opcao, texto_y_calc, botao_largura_opcao, altura_opcao))
                            y_calc = linha_y_calc + espacamento_opcao
                        
                        for i, rect in enumerate(hitboxes):
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.opcao_selecionada = i
                                if i == 0:
                                    sucesso, mensagem = self.processar_aceitar(prefixo_cor)
                                    self.fase_dialogo = "reacao"
                                else:
                                    self.processar_recusar()
                                    self.fase_dialogo = "reacao"
                                break
                
                elif self.fase_dialogo == "reacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fechar()
                            if self.oferta_atual and self.sprite_atual == self.sprite_vendeu:
                                return "comprado"
                            elif self.oferta_atual and self.sprite_atual == self.sprite_golpe:
                                return "recusado"
                            else:
                                return "fechado"
        
        return None

# Instância global
mercador_alien = MercadorAlien()

