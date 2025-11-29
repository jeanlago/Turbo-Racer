"""Sistema do Boris - O Sucateiro Ciborgue que vende peças com preços variáveis"""
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

CAMINHO_BORIS_DATA = os.path.join(DIR_PROJETO, "data", "boris.json")

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "boris")
SPRITE_TRABALHANDO = os.path.join(CAMINHO_SPRITES, "boris_.png")
SPRITE_RABUGENTO = os.path.join(CAMINHO_SPRITES, "boris_irritado_leve.png")
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "boris_neutro.png")
SPRITE_AMEAÇADOR = os.path.join(CAMINHO_SPRITES, "boris_ameacador.png")
SPRITE_CONVENCIDO = os.path.join(CAMINHO_SPRITES, "boris_persuasivo.png")

def obter_caminho_fabrica():
    from config import obter_caminho_sprite_dia_noite
    return obter_caminho_sprite_dia_noite("fabrica")

class Boris:
    """Boris - O Sucateiro Ciborgue que vende peças com preços variáveis"""
    
    PROBABILIDADE_PRECO_OTIMO = 0.25
    PROBABILIDADE_PRECO_PESSIMO = 0.75
    
    MULTIPLICADOR_PRECO_OTIMO = 0.5
    MULTIPLICADOR_PRECO_PESSIMO = 2.0
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_trabalhando = None
        self.sprite_rabugento = None
        self.sprite_neutro = None
        self.sprite_ameaçador = None
        self.sprite_convencido = None
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
        self.velocidade_texto = 60.0
        
        self.nome_revelado = False
        self.primeira_aparicao_mostrada = False
        
        self.loja_aberta = False
        self.peça_selecionada = None
        self.preco_tipo_atual = None
        
    def carregar_estado(self):
        """Carrega o estado do Boris do progresso.json"""
        self.nome_revelado = gerenciador_progresso.boris_nome_revelado if hasattr(gerenciador_progresso, 'boris_nome_revelado') else False
        self.primeira_aparicao_mostrada = gerenciador_progresso.boris_primeira_aparicao_mostrada if hasattr(gerenciador_progresso, 'boris_primeira_aparicao_mostrada') else False
    
    def salvar_estado(self):
        """Salva o estado do Boris no progresso.json"""
        gerenciador_progresso.boris_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.boris_primeira_aparicao_mostrada = getattr(self, 'primeira_aparicao_mostrada', False)
        gerenciador_progresso.salvar()
    
    def carregar_sprites(self):
        """Carrega os sprites do Boris"""
        if self.sprites_carregados:
            return
        
        try:
            print(f"[BORIS] Carregando sprites...")
            if os.path.exists(SPRITE_TRABALHANDO):
                self.sprite_trabalhando = pygame.image.load(SPRITE_TRABALHANDO).convert_alpha()
                print(f"[BORIS] ✓ Sprite trabalhando carregado")
            else:
                print(f"[BORIS] ✗ Sprite trabalhando não encontrado: {SPRITE_TRABALHANDO}")
            
            if os.path.exists(SPRITE_RABUGENTO):
                self.sprite_rabugento = pygame.image.load(SPRITE_RABUGENTO).convert_alpha()
                print(f"[BORIS] ✓ Sprite rabugento carregado")
            else:
                print(f"[BORIS] ✗ Sprite rabugento não encontrado: {SPRITE_RABUGENTO}")
            
            if os.path.exists(SPRITE_NEUTRO):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO).convert_alpha()
                print(f"[BORIS] ✓ Sprite neutro carregado")
            else:
                print(f"[BORIS] ✗ Sprite neutro não encontrado: {SPRITE_NEUTRO}")
            
            if os.path.exists(SPRITE_AMEAÇADOR):
                self.sprite_ameaçador = pygame.image.load(SPRITE_AMEAÇADOR).convert_alpha()
                print(f"[BORIS] ✓ Sprite ameaçador carregado")
            else:
                print(f"[BORIS] ✗ Sprite ameaçador não encontrado: {SPRITE_AMEAÇADOR}")
            
            if os.path.exists(SPRITE_CONVENCIDO):
                self.sprite_convencido = pygame.image.load(SPRITE_CONVENCIDO).convert_alpha()
                print(f"[BORIS] ✓ Sprite convencido carregado")
            else:
                print(f"[BORIS] ✗ Sprite convencido não encontrado: {SPRITE_CONVENCIDO}")
            
            CAMINHO_FABRICA = obter_caminho_fabrica()
            print(f"[BORIS] Tentando carregar fundo da fábrica: {CAMINHO_FABRICA}")
            if os.path.exists(CAMINHO_FABRICA):
                self.sprite_fundo = pygame.image.load(CAMINHO_FABRICA).convert_alpha()
                print(f"[BORIS] ✓ Fundo da fábrica carregado: {self.sprite_fundo.get_size()}")
            else:
                print(f"[BORIS] ✗ Fundo da fábrica não encontrado: {CAMINHO_FABRICA}")
            
            self.sprites_carregados = True
            print(f"[BORIS] Sprites carregados: trabalhando={self.sprite_trabalhando is not None}, rabugento={self.sprite_rabugento is not None}, fundo={self.sprite_fundo is not None}")
        except Exception as e:
            print(f"[BORIS] Erro ao carregar sprites: {e}")
            import traceback
            traceback.print_exc()
    
    def verificar_aparecer_primeira_vez(self):
        """Verifica se deve mostrar a primeira aparição do Boris"""
        if self.primeira_aparicao_mostrada:
            return False
        
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
                "sprite": "trabalhando",
                "texto": "",
                "duracao": 3.0
            },
            {
                "sprite": "rabugento",
                "texto": "GRRR! Quem é o rato que ousa invadir meu chiqueiro? Ah, é o novato de quem todos falam."
            },
            {
                "sprite": "ameaçador",
                "texto": "Olho para essa sua lata velha e só vejo uma coisa: falta de RESPEITO. Respeito pelo metal! Respeito pelo torque!"
            },
            {
                "sprite": "ameaçador",
                "texto": "Aquela panda lá em cima fala de 'fluxo', de 'dançar com a pista'... BAH! Besteira! Corrida é briga. É metal contra metal. É fazer o motor gritar até ele implorar por misericórdia."
            },
            {
                "sprite": "convencido",
                "texto": "Você está no meu território agora, o Fosso de Ferrugem. Aqui nós construímos monstros. Se você quer peças que aguentem porrada, veio ao lugar certo."
            },
            {
                "sprite": "rabugento",
                "texto": "Mas não espere que eu seja gentil com o preço. Eu sou mecânico, não instituição de caridade. Vamos ver o que você precisa. E torça para eu estar de bom humor."
            }
        ]
        
        if self.parte_cutscene < len(partes):
            parte = partes[self.parte_cutscene]
            
            sprite_nome = parte.get("sprite", "rabugento")
            print(f"[BORIS] Definindo sprite: {sprite_nome} (parte {self.parte_cutscene})")
            
            if sprite_nome == "trabalhando" and self.sprite_trabalhando:
                self.sprite_atual = self.sprite_trabalhando
                print(f"[BORIS] ✓ Sprite atual definido como trabalhando")
            elif sprite_nome == "rabugento" and self.sprite_rabugento:
                self.sprite_atual = self.sprite_rabugento
                print(f"[BORIS] ✓ Sprite atual definido como rabugento")
            elif sprite_nome == "ameaçador" and self.sprite_ameaçador:
                self.sprite_atual = self.sprite_ameaçador
                print(f"[BORIS] ✓ Sprite atual definido como ameaçador")
            elif sprite_nome == "convencido" and self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
                print(f"[BORIS] ✓ Sprite atual definido como convencido")
                else:
                    if self.sprite_rabugento:
                    self.sprite_atual = self.sprite_rabugento
                    print(f"[BORIS] ⚠ Usando fallback rabugento para sprite: {sprite_nome}")
                elif self.sprite_neutro:
                    self.sprite_atual = self.sprite_neutro
                    print(f"[BORIS] ⚠ Usando fallback neutro para sprite: {sprite_nome}")
                elif self.sprite_trabalhando:
                    self.sprite_atual = self.sprite_trabalhando
                    print(f"[BORIS] ⚠ Usando fallback trabalhando para sprite: {sprite_nome}")
                elif self.sprite_ameaçador:
                    self.sprite_atual = self.sprite_ameaçador
                    print(f"[BORIS] ⚠ Usando fallback ameaçador para sprite: {sprite_nome}")
                elif self.sprite_convencido:
                    self.sprite_atual = self.sprite_convencido
                    print(f"[BORIS] ⚠ Usando fallback convencido para sprite: {sprite_nome}")
                else:
                    self.sprite_atual = None
                    print(f"[BORIS] ✗ ERRO: Nenhum sprite disponível para {sprite_nome}!")
            
            texto = parte.get("texto", "")
            if texto:
                self._iniciar_animacao_texto(texto)
            else:
                self.texto_completo = ""
                self.texto_exibido = ""
        else:
            self.primeira_aparicao_mostrada = True
            self.salvar_estado()
            self.fase_dialogo = "loja"
            self._abrir_loja()
    
    def _abrir_loja(self):
        """Abre a loja do Boris"""
        self.loja_aberta = True
        self.sprite_atual = self.sprite_rabugento if self.sprite_rabugento else self.sprite_neutro
        
        saudacoes = [
            "Você de novo? Espero que tenha trazido dinheiro, ou um carro para eu compactar. O que você quer?",
            "Rápido, fala logo! Estou no meio de um transplante de pistão aqui. O que quebrou dessa vez?",
            "Sinto cheiro de embreagem queimada a quilômetros. Você dirige como minha avó. Veio comprar talento ou peças?"
        ]
        texto = random.choice(saudacoes)
        self._iniciar_animacao_texto(texto)
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        
        # Verificar se deve revelar nome
        texto_lower = texto.lower()
        if "boris" in texto_lower or "meu nome" in texto_lower or "me chamo boris" in texto_lower:
            if not self.nome_revelado:
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
        """Processa eventos do Boris"""
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
                        elif self.fase_dialogo == "loja":
                            # Fechar diálogo e abrir menu de loja
                            self.fechar()
                            return "abrir_loja"
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
                        elif self.fase_dialogo == "loja":
                            # Fechar diálogo e abrir menu de loja
                            self.fechar()
                            return "abrir_loja"
                elif evento.key == pygame.K_ESCAPE:
                    self.fechar()
                    return "fechado"
        
        return None
    
    def calcular_preco_peça(self, tipo_upgrade, preco_base):
        """Calcula o preço de uma peça com probabilidade"""
        # Determinar tipo de preço
        if random.random() < self.PROBABILIDADE_PRECO_OTIMO:
            self.preco_tipo_atual = "otimo"
            multiplicador = self.MULTIPLICADOR_PRECO_OTIMO
        else:
            self.preco_tipo_atual = "pessimo"
            multiplicador = self.MULTIPLICADOR_PRECO_PESSIMO
        
        preco_final = int(preco_base * multiplicador)
        
        return {
            'tipo': tipo_upgrade,
            'preco_base': preco_base,
            'preco_final': preco_final,
            'preco_tipo': self.preco_tipo_atual
        }
    
    def obter_texto_preco(self, peça_info):
        """Retorna o texto do Boris explicando o preço"""
        tipo = peça_info['preco_tipo']
        preco = peça_info['preco_final']
        tipo_upgrade = peça_info['tipo']
        
        if tipo == "otimo":
            textos = [
                f"Hm. Esse {self._nome_upgrade(tipo_upgrade)}? Arranquei de um caminhão que bateu ontem. Está sujo de sangue e óleo, mas funciona. Me dá ${preco:,} e tira isso da minha vista antes que eu mude de ideia.",
                f"Sorte sua, rato. Troquei essa {self._nome_upgrade(tipo_upgrade)} por uma caixa de charutos com um idiota. Leva por ${preco:,}. É quase de graça.",
                f"Toma. ${preco:,}. Está ocupando espaço na minha bancada e eu preciso esmagar alguma coisa agora. Vai!"
            ]
        else:  # pessimo
            textos = [
                f"Ah, você tem bom gosto. Esse {self._nome_upgrade(tipo_upgrade)}? Estava morto. Eu o ressuscitei com minhas próprias garras. Refiz cada solda. Vale ouro. O preço é ${preco:,}. Paga ou cai fora.",
                f"Você acha que isso nasce em árvore? Eu tive que brigar com três catadores no lixão por essa {self._nome_upgrade(tipo_upgrade)}. O preço é ${preco:,} pela peça e mais 20% pelo meu estresse.",
                f"${preco:,}. E não adianta chorar. Se você quer qualidade que aguenta o tranco, tem que pagar. Se quiser barato, vai comprar plástico com a Akira."
            ]
        
        return random.choice(textos)
    
    def _nome_upgrade(self, tipo):
        """Retorna o nome amigável do upgrade"""
        nomes = {
            'motor': 'motor',
            'freios': 'freios',
            'suspensao': 'suspensão',
            'pneus': 'pneus',
            'turbo': 'turbo',
            'nitro': 'nitro'
        }
        return nomes.get(tipo, 'peça')
    
    def processar_compra(self, peça_info):
        """Processa a compra de uma peça"""
        preco = peça_info['preco_final']
        
        # Verificar dinheiro
        if not gerenciador_progresso.tem_dinheiro(preco):
            self.sprite_atual = self.sprite_rabugento if self.sprite_rabugento else self.sprite_neutro
            texto = "BAH! Sabia. Muita pose, pouco dinheiro. Volte quando tiver coragem de investir em potência de verdade."
            self._iniciar_animacao_texto(texto)
            return False, "Dinheiro insuficiente"
        
        # Remover dinheiro
        gerenciador_progresso.remover_dinheiro(preco)
        
        # Reação baseada no tipo de preço
        if peça_info['preco_tipo'] == "otimo":
            self.sprite_atual = self.sprite_neutro if self.sprite_neutro else self.sprite_rabugento
            texto = "Você deu sorte hoje. Não se acostume. Amanhã eu cobro o dobro."
        else:
            self.sprite_atual = self.sprite_rabugento if self.sprite_rabugento else self.sprite_neutro
            texto = "GRRR. É assim que eu gosto. Um idiota e seu dinheiro logo se separam. Agora suma daqui."
        
        self._iniciar_animacao_texto(texto)
        return True, f"Peça comprada por ${preco:,}!"
    
    def atualizar(self, dt):
        """Atualiza o Boris"""
        if not self.ativo:
            return
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Boris"""
        if not self.ativo:
            return
        
        render_text = _get_render_text()
        
        CAMINHO_FABRICA = obter_caminho_fabrica()
        if os.path.exists(CAMINHO_FABRICA):
            try:
                self.sprite_fundo = pygame.image.load(CAMINHO_FABRICA).convert_alpha()
            except Exception as e:
                print(f"[BORIS] Erro ao recarregar fundo: {e}")
        
        if self.sprite_fundo:
            fundo_w, fundo_h = self.sprite_fundo.get_size()
            fundo_redimensionado = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
            tela.blit(fundo_redimensionado, (0, 0))
        else:
            print(f"[BORIS] AVISO: sprite_fundo é None, usando fallback. Caminho tentado: {CAMINHO_FABRICA}")
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            tela.blit(overlay, (0, 0))
        
        if self.sprite_atual:
            sprite_original_w = self.sprite_atual.get_width()
            sprite_original_h = self.sprite_atual.get_height()
            sprite_novo_w = int(sprite_original_w * 0.7)
            sprite_novo_h = int(sprite_original_h * 0.7)
            sprite_redimensionado = pygame.transform.scale(self.sprite_atual, (sprite_novo_w, sprite_novo_h))
            
            sprite_x = LARGURA // 2 - sprite_novo_w // 2
            sprite_y = ALTURA // 2 - sprite_novo_h // 2 - 50
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        else:
            print(f"[BORIS] AVISO: sprite_atual é None! fase_dialogo={self.fase_dialogo}, parte_cutscene={self.parte_cutscene}")
        
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        # Fundo da caixa
        overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay_caixa.fill((0, 0, 0, 200))
        tela.blit(overlay_caixa, (caixa_x, caixa_y))
        
        # Borda da caixa
        pygame.draw.rect(tela, (100, 100, 100), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Nome do personagem
        nome = "Boris" if self.nome_revelado else "???"
        nome_texto = render_text(nome, 20, (255, 200, 0), bold=True, pixel_style=True)
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
        
        # Indicador de avanço
        if len(self.texto_exibido) >= len(self.texto_completo):
            indicador = render_text("Pressione ESPAÇO ou clique para continuar", 14, (150, 150, 150), bold=False, pixel_style=True)
            tela.blit(indicador, (caixa_x + caixa_largura - 400, caixa_y + caixa_altura - 30))
    
    def fechar(self):
        """Fecha o diálogo do Boris"""
        self.ativo = False
        self.loja_aberta = False
        self.peça_selecionada = None
        self.preco_tipo_atual = None

# Instância global
boris = Boris()

