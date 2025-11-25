# src/core/mercador_alien.py
"""Sistema de mercador alien que aparece ocasionalmente oferecendo upgrades especiais"""
import pygame
import random
import os
import json
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso

# Caminhos dos sons
CAMINHO_SOM_COMPRA = os.path.join(DIR_PROJETO, "assets", "sounds", "purchase", "caixa.mp3")
CAMINHO_SOM_FAIL = os.path.join(DIR_PROJETO, "assets", "sounds", "fail", "falha.mp3")

# Import lazy para evitar import circular
def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

CAMINHO_MERCADOR_DATA = os.path.join(DIR_PROJETO, "data", "mercador_alien.json")

# Caminhos dos sprites
CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "vendedor")
SPRITE_CUMPRIMENTO = os.path.join(CAMINHO_SPRITES, "cumprimento.png")
SPRITE_OFERTA = os.path.join(CAMINHO_SPRITES, "oferta.png")
SPRITE_GOLPE = os.path.join(CAMINHO_SPRITES, "golpe.png")  # Quando jogador cai em golpe (aceita oferta ruim)
SPRITE_VENDEU = os.path.join(CAMINHO_SPRITES, "vendeu.png")
SPRITE_BRAVO = os.path.join(CAMINHO_SPRITES, "bravo.png")  # Quando está bravo
SPRITE_ENFURECIDO = os.path.join(CAMINHO_SPRITES, "enfurecido.png")  # Quando está enfurecido

# Caminho do fundo pós-corrida
CAMINHO_FUNDO_POS_CORRIDA = os.path.join(DIR_PROJETO, "assets", "images", "ui", "pos_corrida.png")

class MercadorAlien:
    """Mercador alien que aparece ocasionalmente oferecendo upgrades especiais"""
    
    # Probabilidade de aparecer (30% após corrida, 20% ao abrir upgrades)
    PROBABILIDADE_APOS_CORRIDA = 0.30
    PROBABILIDADE_AO_UPGRADE = 0.20
    
    # Cooldown mínimo entre aparições (em número de corridas/upgrades)
    COOLDOWN_MINIMO = 3
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_cumprimento = None
        self.sprite_oferta = None
        self.sprite_golpe = None  # Quando jogador cai em golpe (aceita oferta ruim)
        self.sprite_vendeu = None
        self.sprite_bravo = None  # Quando está bravo
        self.sprite_enfurecido = None  # Quando está enfurecido
        self.sprites_carregados = False
        
        # Estado atual da interação
        self.ativo = False
        self.oferta_atual = None
        self.sprite_atual = None
        self.texto_atual = ""
        self.opcao_selecionada = 0  # 0 = Aceitar, 1 = Recusar
        self.fase_dialogo = "apresentacao"  # "apresentacao", "oferta", "reacao"
        self.contexto_atual = "corrida"  # "corrida" ou "upgrade" - contexto da aparição
        
        # Fundo pós-corrida
        self.fundo_pos_corrida = None
        
        # Sistema de animação de texto flutuante "-$X"
        self.animacoes_dinheiro = []  # Lista de animações ativas: [(x, y, texto, tempo_restante, alpha)]
        
        # Sistema de animação de texto letra por letra
        self.texto_completo = ""  # Texto completo a ser exibido
        self.texto_exibido = ""  # Texto já exibido (animação)
        self.tempo_animacao = 0.0  # Tempo acumulado para animação
        self.velocidade_texto = 50.0  # Caracteres por segundo (aumentado de 30 para 50)
        
        # Sons
        self.som_compra = None
        self.som_fail = None
        self._carregar_sons()
        
    def _carregar_sons(self):
        """Carrega os sons do mercador"""
        try:
            # Garantir que pygame.mixer está inicializado
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            print(f"Tentando carregar som de compra de: {CAMINHO_SOM_COMPRA}")
            print(f"Arquivo existe? {os.path.exists(CAMINHO_SOM_COMPRA)}")
            if os.path.exists(CAMINHO_SOM_COMPRA):
                self.som_compra = pygame.mixer.Sound(CAMINHO_SOM_COMPRA)
                print(f"✓ Som de compra carregado: {CAMINHO_SOM_COMPRA}")
            else:
                print(f"✗ AVISO: Som de compra não encontrado: {CAMINHO_SOM_COMPRA}")
            
            print(f"Tentando carregar som de fail de: {CAMINHO_SOM_FAIL}")
            print(f"Arquivo existe? {os.path.exists(CAMINHO_SOM_FAIL)}")
            if os.path.exists(CAMINHO_SOM_FAIL):
                self.som_fail = pygame.mixer.Sound(CAMINHO_SOM_FAIL)
                print(f"✓ Som de fail carregado: {CAMINHO_SOM_FAIL}")
            else:
                print(f"✗ AVISO: Som de fail não encontrado: {CAMINHO_SOM_FAIL}")
        except Exception as e:
            print(f"ERRO ao carregar sons do mercador: {e}")
            import traceback
            traceback.print_exc()
    
    def _garantir_sons_carregados(self):
        """Garante que os sons estão carregados (carrega se necessário)"""
        if self.som_compra is None or self.som_fail is None:
            if pygame.mixer.get_init():
                self._carregar_sons()
    
    def carregar_sprites(self):
        """Carrega os sprites do mercador"""
        if self.sprites_carregados:
            # Mesmo se os sprites já estiverem carregados, garantir que o fundo também esteja
            if self.fundo_pos_corrida is None:
                self._carregar_fundo_pos_corrida()
            return  # Já foram carregados
        
        try:
            # Garantir que pygame está inicializado
            if not pygame.get_init():
                print("AVISO: pygame não inicializado, tentando inicializar...")
                pygame.init()
            
            print(f"Tentando carregar sprites do mercador de: {CAMINHO_SPRITES}")
            print(f"DIR_PROJETO: {DIR_PROJETO}")
            print(f"Pasta existe? {os.path.exists(CAMINHO_SPRITES)}")
            
            if os.path.exists(SPRITE_CUMPRIMENTO):
                self.sprite_cumprimento = pygame.image.load(SPRITE_CUMPRIMENTO).convert_alpha()
                print(f"✓ Sprite cumprimento carregado: {SPRITE_CUMPRIMENTO} ({self.sprite_cumprimento.get_size()})")
            else:
                print(f"✗ AVISO: Sprite cumprimento não encontrado: {SPRITE_CUMPRIMENTO}")
            
            if os.path.exists(SPRITE_OFERTA):
                self.sprite_oferta = pygame.image.load(SPRITE_OFERTA).convert_alpha()
                print(f"✓ Sprite oferta carregado: {SPRITE_OFERTA} ({self.sprite_oferta.get_size()})")
            else:
                print(f"✗ AVISO: Sprite oferta não encontrado: {SPRITE_OFERTA}")
            
            if os.path.exists(SPRITE_GOLPE):
                self.sprite_golpe = pygame.image.load(SPRITE_GOLPE).convert_alpha()
                print(f"✓ Sprite golpe carregado: {SPRITE_GOLPE} ({self.sprite_golpe.get_size()})")
            else:
                print(f"✗ AVISO: Sprite golpe não encontrado: {SPRITE_GOLPE}")
            
            if os.path.exists(SPRITE_VENDEU):
                self.sprite_vendeu = pygame.image.load(SPRITE_VENDEU).convert_alpha()
                print(f"✓ Sprite vendeu carregado: {SPRITE_VENDEU} ({self.sprite_vendeu.get_size()})")
            else:
                print(f"✗ AVISO: Sprite vendeu não encontrado: {SPRITE_VENDEU}")
            
            if os.path.exists(SPRITE_BRAVO):
                self.sprite_bravo = pygame.image.load(SPRITE_BRAVO).convert_alpha()
                print(f"✓ Sprite bravo carregado: {SPRITE_BRAVO} ({self.sprite_bravo.get_size()})")
            else:
                print(f"✗ AVISO: Sprite bravo não encontrado: {SPRITE_BRAVO}")
            
            if os.path.exists(SPRITE_ENFURECIDO):
                self.sprite_enfurecido = pygame.image.load(SPRITE_ENFURECIDO).convert_alpha()
                print(f"✓ Sprite enfurecido carregado: {SPRITE_ENFURECIDO} ({self.sprite_enfurecido.get_size()})")
            else:
                print(f"✗ AVISO: Sprite enfurecido não encontrado: {SPRITE_ENFURECIDO}")
            
            self.sprites_carregados = True
            
            # Carregar fundo pós-corrida se existir
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
                print(f"✓ Fundo pós-corrida carregado: {CAMINHO_FUNDO_POS_CORRIDA}")
            else:
                print(f"✗ AVISO: Fundo pós-corrida não encontrado: {CAMINHO_FUNDO_POS_CORRIDA}")
        except Exception as e:
            print(f"ERRO ao carregar fundo pós-corrida: {e}")
    
    def carregar_estado(self):
        """Carrega o estado do mercador (cooldown, etc)"""
        try:
            if os.path.exists(CAMINHO_MERCADOR_DATA):
                with open(CAMINHO_MERCADOR_DATA, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ultima_aparicao = data.get('ultima_aparicao', 0)
                    self.contador_eventos = data.get('contador_eventos', 0)
            else:
                self.ultima_aparicao = 0
                self.contador_eventos = 0
        except Exception as e:
            print(f"Erro ao carregar estado do mercador: {e}")
            self.ultima_aparicao = 0
            self.contador_eventos = 0
    
    def salvar_estado(self):
        """Salva o estado do mercador"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_MERCADOR_DATA), exist_ok=True)
            data = {
                'ultima_aparicao': self.ultima_aparicao,
                'contador_eventos': self.contador_eventos
            }
            with open(CAMINHO_MERCADOR_DATA, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar estado do mercador: {e}")
    
    def verificar_aparecer(self, contexto="corrida"):
        """Verifica se o mercador deve aparecer"""
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.contador_eventos += 1
        
        # Verificar cooldown
        eventos_desde_ultima = self.contador_eventos - self.ultima_aparicao
        if eventos_desde_ultima < self.COOLDOWN_MINIMO:
            print(f"Mercador: Cooldown ativo ({eventos_desde_ultima}/{self.COOLDOWN_MINIMO})")
            return False
        
        # Verificar probabilidade
        probabilidade = self.PROBABILIDADE_APOS_CORRIDA if contexto == "corrida" else self.PROBABILIDADE_AO_UPGRADE
        valor_aleatorio = random.random()
        print(f"Mercador: Verificando aparecimento (contexto={contexto}, prob={probabilidade:.2%}, random={valor_aleatorio:.3f})")
        if valor_aleatorio > probabilidade:
            print(f"Mercador: Não apareceu (random > probabilidade)")
            return False
        
        # Gerar oferta e ativar
        print(f"Mercador: VAI APARECER! Gerando oferta...")
        self.gerar_oferta()
        self.ativo = True
        self.contexto_atual = contexto  # Salvar o contexto da aparição
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
        
        # Definir sprite e texto inicial (FASE 1: Apresentação)
        if self.sprite_cumprimento:
            self.sprite_atual = self.sprite_cumprimento
            print(f"Mercador: Sprite cumprimento definido como atual")
        else:
            self.sprite_atual = None
            print(f"AVISO: Sprite cumprimento não disponível!")
        texto_completo = self.obter_texto_cumprimento()
        self._iniciar_animacao_texto(texto_completo)
        self.opcao_selecionada = 0
        self.fase_dialogo = "apresentacao"  # Começar na fase de apresentação
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
        
        # Verificar dinheiro
        if not gerenciador_progresso.tem_dinheiro(preco):
            self.sprite_atual = self.sprite_golpe
            texto_completo = "Você não tem dinheiro suficiente! Que pena... talvez na próxima vez!"
            self._iniciar_animacao_texto(texto_completo)
            return False, "Dinheiro insuficiente"
        
        # Tocar som ANTES de remover dinheiro (para resposta imediata)
        # Garantir que os sons estão carregados
        self._garantir_sons_carregados()
        
        # Determinar qual som tocar baseado no tipo de oferta
        e_golpe = self.oferta_atual['tipo'] == 'golpe'
        if e_golpe:
            # Tocar som de fail para golpe IMEDIATAMENTE
            if self.som_fail:
                try:
                    self.som_fail.play()
                except Exception as e:
                    print(f"Erro ao tocar som de fail: {e}")
        else:
            # Tocar som de compra para bom negócio IMEDIATAMENTE
            if self.som_compra:
                try:
                    self.som_compra.play()
                except Exception as e:
                    print(f"Erro ao tocar som de compra: {e}")
        
        # Remover dinheiro
        gerenciador_progresso.remover_dinheiro(preco)
        
        # Adicionar animação de "-$X" (centro da tela, subindo)
        self._adicionar_animacao_dinheiro(LARGURA // 2, ALTURA // 2, preco)
        
        # Aplicar upgrade baseado no tipo
        # IMPORTANTE: Como o dinheiro já foi removido, sempre considerar como sucesso
        # mesmo que não consiga aplicar o upgrade (evita mercador ficar triste após receber dinheiro)
        sucesso = True  # Sempre True após remover dinheiro
        mensagem = ""
        
        if self.oferta_atual['tipo'] == 'golpe':
            # Golpe: apenas 1 upgrade normal (mas já pagou caro)
            upgrade_aplicado = False
            if prefixo_cor:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'])
                if nivel_atual < 5:
                    gerenciador_progresso.comprar_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'], 0)  # Já pagou
                    upgrade_aplicado = True
                    mensagem = f"Upgrade de {self._nome_upgrade()} aplicado! (Você pagou mais do que deveria...)"
            else:
                # Aplicar ao primeiro carro desbloqueado
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
            # Múltiplos upgrades
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
        
        else:  # upgrade_especial
            # Upgrade especial com bônus
            if prefixo_cor:
                nivel_atual = gerenciador_progresso.obter_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'])
                # Aplicar upgrade principal
                if nivel_atual < 5:
                    gerenciador_progresso.comprar_upgrade(prefixo_cor, self.oferta_atual['tipo_upgrade'], 0)
                    # Aplicar bônus em upgrade relacionado
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
                            # Bônus
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
            # Registrar compra para diálogo raro do Crank
            quantidade = 1
            if self.oferta_atual['tipo'] == 'multi_upgrade':
                quantidade = self.oferta_atual.get('quantidade', 1)
            gerenciador_progresso.registrar_compra_alien(
                self.oferta_atual['tipo'],
                quantidade,
                self.oferta_atual.get('tipo_upgrade')
            )
            
            # Se foi golpe, usar sprite_golpe (quando jogador cai no golpe)
            if self.oferta_atual['tipo'] == 'golpe':
                self.sprite_atual = self.sprite_golpe if self.sprite_golpe else self.sprite_oferta
                textos_sucesso = [
                    "Excelente escolha! Hehe... Você não vai se arrepender. E lembre-se: sem devoluções!",
                    "Negócio fechado. Transfira os créditos antes que eu mude de ideia.",
                    "Um prazer fazer negócios com espécies inferiores. Volte sempre que tiver créditos sobrando."
                ]
            else:
                # Oferta boa - usar sprite_vendeu (feliz por ter vendido)
                # Se sprite_vendeu não estiver disponível, usar sprite_oferta como fallback (não usar sprite triste)
                if self.sprite_vendeu:
                    self.sprite_atual = self.sprite_vendeu
                elif self.sprite_oferta:
                    self.sprite_atual = self.sprite_oferta
                elif self.sprite_cumprimento:
                    self.sprite_atual = self.sprite_cumprimento
                else:
                    self.sprite_atual = self.sprite_golpe  # Último recurso, mas não ideal
                textos_sucesso = [
                    "Negócio fechado. Transfira os créditos antes que eu mude de ideia.",
                    "Um prazer fazer negócios com espécies inferiores. Volte sempre que tiver créditos sobrando.",
                    "Excelente escolha! Você não vai se arrepender desta vez."
                ]
            texto_completo = random.choice(textos_sucesso)
            self._iniciar_animacao_texto(texto_completo)
        else:
            # Erro ao aplicar upgrade - usar sprite_bravo
            self.sprite_atual = self.sprite_bravo if self.sprite_bravo else self.sprite_golpe
            texto_completo = "Hmm... parece que não consegui aplicar o upgrade. Mas o dinheiro já foi... que estranho!"
            self._iniciar_animacao_texto(texto_completo)
        
        return sucesso, mensagem
    
    def processar_recusar(self):
        """Processa quando o jogador recusa a oferta"""
        # Escolher sprite baseado na intensidade da reação
        reacao_intensidade = random.random()
        
        if reacao_intensidade < 0.4:
            # Reação mais leve - bravo
            self.sprite_atual = self.sprite_bravo if self.sprite_bravo else self.sprite_golpe
            textos_recusa = [
                "Bah! Terráqueos não têm visão de futuro. Fique aí com sua carroça lenta. Sua perda!",
                "Tsc. Desperdício de tempo. Saia da minha frente antes que eu vaporize seus pneus com meu laser de serviço.",
                "Tudo bem... mas você está perdendo uma oportunidade única! Sua perda, não minha!"
            ]
        else:
            # Reação mais intensa - enfurecido
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
        self.texto_atual = ""  # Garantir que texto_atual também começa vazio
        self.tempo_animacao = 0.0
    
    def _atualizar_animacao_texto(self, dt):
        """Atualiza animação de texto letra por letra"""
        # Garantir que temos um texto completo para animar
        if not self.texto_completo:
            return
        
        if len(self.texto_exibido) < len(self.texto_completo):
            self.tempo_animacao += dt
            
            # Calcular quantos caracteres mostrar baseado no tempo acumulado
            caracteres_esperados = int(self.tempo_animacao * self.velocidade_texto)
            caracteres_para_adicionar = caracteres_esperados - len(self.texto_exibido)
            
            if caracteres_para_adicionar > 0:
                # Limitar a adicionar no máximo alguns caracteres por frame para suavidade
                # Isso previne que o texto apareça completo de uma vez se dt for muito grande
                max_por_frame = max(1, int(self.velocidade_texto * dt * 5))  # Permitir até 5x a velocidade normal por frame
                caracteres_para_adicionar = min(caracteres_para_adicionar, max_por_frame)
                
                # Adicionar caracteres gradualmente
                novo_tamanho = min(len(self.texto_exibido) + caracteres_para_adicionar, len(self.texto_completo))
                self.texto_exibido = self.texto_completo[:novo_tamanho]
                self.texto_atual = self.texto_exibido
        else:
            # Garantir que texto_atual está sincronizado quando a animação termina
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
        # Não limpar animações aqui - deixar elas terminarem naturalmente
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do mercador na tela no estilo visual novel"""
        # Atualizar animações de dinheiro
        self._atualizar_animacoes_dinheiro(dt)
        
        if not self.ativo:
            # Desenhar animações mesmo quando inativo (para continuar animação após fechar)
            self._desenhar_animacoes_dinheiro(tela)
            return
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        if not self.sprite_atual:
            print(f"AVISO: Mercador ativo mas sprite_atual é None! Tentando usar sprite_cumprimento...")
            if self.sprite_cumprimento:
                self.sprite_atual = self.sprite_cumprimento
            else:
                print(f"ERRO: Nenhum sprite disponível para o mercador!")
                return
        
        # Desenhar fundo pós-corrida se o contexto for "corrida" e o fundo existir
        if self.contexto_atual == "corrida" and self.fundo_pos_corrida is not None:
            tela.blit(self.fundo_pos_corrida, (0, 0))
        
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
        sprite_y = ALTURA - sprite_h - 250  # Posicionar acima da caixa
        
        if lado_direito:
            sprite_x = LARGURA - sprite_w - 20
        else:
            sprite_x = 20
        
        # Desenhar sprite do personagem (antes da caixa para ficar por cima)
        if self.sprite_atual:
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        # Determinar cor do contorno baseado no sprite atual
        cor_contorno = (255, 255, 255)  # Branco padrão
        if self.sprite_atual == self.sprite_cumprimento:
            cor_contorno = (0, 255, 100)  # Verde para cumprimento
        elif self.sprite_atual == self.sprite_oferta:
            cor_contorno = (100, 150, 255)  # Azul para oferta
        elif self.sprite_atual == self.sprite_golpe:
            cor_contorno = (255, 100, 100)  # Vermelho para golpe
        elif self.sprite_atual == self.sprite_vendeu:
            cor_contorno = (255, 200, 0)  # Amarelo/dourado para vendeu
        elif self.sprite_atual == self.sprite_bravo:
            cor_contorno = (255, 50, 50)  # Vermelho escuro para bravo
        
        # Desenhar caixa de diálogo (igual ao Rex)
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
        nome_texto = render_text("SLICK", 24, (0, 255, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Atualizar animação de texto
        self._atualizar_animacao_texto(dt)
        
        # Desenhar texto do diálogo (igual ao Rex)
        if self.texto_exibido:
            fonte = pygame.font.SysFont("consolas", 18)
            # Quebrar texto em linhas
            palavras = self.texto_exibido.split(' ')
            linhas = []
            linha_atual = ""
            for palavra in palavras:
                teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                largura_teste = fonte.size(teste_linha)[0]
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
                texto_surface = fonte.render(linha, True, (255, 255, 255))
                tela.blit(texto_surface, (caixa_x + 20, y_texto))
                y_texto += 25
        
        # Desenhar indicador de continuar (igual ao Rex) - apenas quando não estiver na fase de oferta
        if len(self.texto_exibido) >= len(self.texto_completo) and self.fase_dialogo != "oferta":
            indicador = render_text("Pressione ENTER ou clique para continuar...", 16, (200, 200, 200), bold=False, pixel_style=True)
            indicador_x = caixa_x + caixa_largura - indicador.get_width() - 20
            indicador_y = caixa_y + caixa_altura - 30
            tela.blit(indicador, (indicador_x, indicador_y))
        
        # Botões de escolha (quando na fase de oferta)
        # Só exibir opções se o texto estiver completo e estiver na fase de oferta
        if self.fase_dialogo == "oferta" and len(self.texto_exibido) >= len(self.texto_completo):
            # FASE 2: Opções no meio da tela (apenas texto com linha embaixo)
            opcoes = ["ACEITAR", "RECUSAR"]
            espacamento = 25
            botao_largura_opcao = int(LARGURA * 0.5)  # 50% da largura da tela
            botao_x_opcao = (LARGURA - botao_largura_opcao) // 2  # Centralizado
            
            # Obter posição do mouse para hover
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Calcular posição Y para centralizar verticalmente
            altura_total = len(opcoes) * 40 + (len(opcoes) - 1) * espacamento
            inicio_y_opcao = (ALTURA - altura_total) // 2
            y_atual = inicio_y_opcao
            
            for i, opcao_nome in enumerate(opcoes):
                # Calcular área clicável (para hover e clique)
                texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                texto_opcao_y = y_atual
                linha_y = texto_opcao_y + texto_opcao_temp.get_height() + 5
                opcao_rect = pygame.Rect(botao_x_opcao, texto_opcao_y, botao_largura_opcao, linha_y - texto_opcao_y + 10)
                
                # Verificar hover
                hover = opcao_rect.collidepoint(mouse_x, mouse_y)
                
                # Verificar se mouse está sobre qualquer opção
                mouse_sobre_qualquer_opcao = False
                for j in range(len(opcoes)):
                    texto_temp = render_text(opcoes[j], 24, (255, 255, 255), bold=False, pixel_style=False)
                    y_temp = inicio_y_opcao + (j * 40) + (j * espacamento)
                    linha_y_temp = y_temp + texto_temp.get_height() + 5
                    rect_temp = pygame.Rect(botao_x_opcao, y_temp, botao_largura_opcao, linha_y_temp - y_temp + 10)
                    if rect_temp.collidepoint(mouse_x, mouse_y):
                        mouse_sobre_qualquer_opcao = True
                        break
                
                # Cor do texto: hover tem prioridade, senão mostrar seleção por teclado (mas só se não houver mouse sobre opções)
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
        
        # Desenhar animações de dinheiro por cima de tudo
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
                        # Se o texto ainda está sendo escrito, completar animação (não avança)
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # FASE 1 -> FASE 2: Ir para a oferta
                            self.fase_dialogo = "oferta"
                            self.sprite_atual = self.sprite_oferta
                            texto_completo = self.obter_texto_oferta()
                            self._iniciar_animacao_texto(texto_completo)
                            self.opcao_selecionada = 0  # Resetar seleção
                    elif self.fase_dialogo == "oferta":
                        # Se o texto ainda está sendo escrito, completar animação (não avança)
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Texto completo, agora pode confirmar escolha
                            if self.opcao_selecionada == 0:
                                # Aceitar oferta -> FASE 3: Reação
                                sucesso, mensagem = self.processar_aceitar(prefixo_cor)
                                self.fase_dialogo = "reacao"
                                # processar_aceitar já muda o sprite e texto
                                # Não retornar ainda, deixar jogador ver a reação
                            else:
                                # Recusar oferta -> FASE 3: Reação
                                self.processar_recusar()
                                self.fase_dialogo = "reacao"
                                # Não retornar ainda, deixar jogador ver a reação
                    elif self.fase_dialogo == "reacao":
                        # Se o texto ainda está sendo escrito, completar animação (não avança)
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Fechar diálogo após ver reação
                            self.fechar()
                            if self.oferta_atual and self.sprite_atual == self.sprite_vendeu:
                                return "comprado"
                            elif self.oferta_atual and self.sprite_atual == self.sprite_golpe:
                                return "recusado"
                            else:
                                return "fechado"
                elif ev.key == pygame.K_ESCAPE:
                    if self.fase_dialogo == "oferta":
                        # Se o texto ainda está sendo escrito, completar animação (não avança)
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Recusar oferta
                            self.processar_recusar()
                            self.fase_dialogo = "reacao"
                    elif self.fase_dialogo == "reacao":
                        # Se o texto ainda está sendo escrito, completar animação (não avança)
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        else:
                            # Fechar após ver reação
                            self.fechar()
                            if self.oferta_atual and self.sprite_atual == self.sprite_vendeu:
                                return "comprado"
                            elif self.oferta_atual and self.sprite_atual == self.sprite_golpe:
                                return "recusado"
                            else:
                                return "fechado"
                    else:
                        # Fechar diálogo
                        self.fechar()
                        return "fechado"
            
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Verificar clique nos botões (mesma lógica do desenho)
                caixa_altura = int(ALTURA * 0.35)
                caixa_y = ALTURA - caixa_altura - 20
                caixa_largura = LARGURA
                caixa_x = 0
                
                botao_y = caixa_y + caixa_altura - 50
                botao_largura = 180
                botao_altura = 38
                espacamento = 25
                
                if self.fase_dialogo == "apresentacao":
                    # Se o texto ainda está sendo escrito, completar animação (não avança)
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste clique
                    else:
                        # Texto completo, agora pode avançar
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fase_dialogo = "oferta"
                            self.sprite_atual = self.sprite_oferta
                            texto_completo = self.obter_texto_oferta()
                            self._iniciar_animacao_texto(texto_completo)
                            self.opcao_selecionada = 0
                
                elif self.fase_dialogo == "oferta":
                    # Se o texto ainda está sendo escrito, completar animação (não avança)
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
                                    sucesso, mensagem = self.processar_aceitar(prefixo_cor)
                                    self.fase_dialogo = "reacao"
                                else:
                                    self.processar_recusar()
                                    self.fase_dialogo = "reacao"
                                break
                
                elif self.fase_dialogo == "reacao":
                    # Se o texto ainda está sendo escrito, completar animação (não avança)
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste clique
                    else:
                        # Clicar em qualquer lugar fecha
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

