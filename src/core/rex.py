# src/core/rex.py
"""Sistema do Rex - Rival do jogador"""
import pygame
import os
import json
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso
from core.estatisticas import gerenciador_estatisticas

# Import lazy para evitar import circular
def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

CAMINHO_REX_DATA = os.path.join(DIR_PROJETO, "data", "rex.json")

# Caminhos dos sprites
CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "rival")
SPRITE_COMPETITIVE = os.path.join(CAMINHO_SPRITES, "competitive.png")
SPRITE_MOCKING = os.path.join(CAMINHO_SPRITES, "mocking.png")
SPRITE_ANGRY = os.path.join(CAMINHO_SPRITES, "angry.png")
SPRITE_CHALLENGING = os.path.join(CAMINHO_SPRITES, "challenging.png")
SPRITE_SCHEMING = os.path.join(CAMINHO_SPRITES, "scheming.png")

# Caminho da cena de fundo
CAMINHO_CENA_FUNDO = os.path.join(DIR_PROJETO, "assets", "images", "pista_corrida.png")

class Rex:
    """Rex - Rival do jogador que aparece após a primeira corrida"""
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_competitive = None
        self.sprite_mocking = None
        self.sprite_angry = None
        self.sprite_challenging = None
        self.sprite_scheming = None
        self.sprite_fundo = None
        self.sprites_carregados = False
        
        # Estado atual da interação
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "apresentacao"  # "apresentacao", "fechado"
        self.parte_dialogo = 0  # Parte atual do diálogo
        self.roteiro_tipo = None  # "carro_lixo" ou "carro_decente"
        
        # Sistema de animação de texto letra por letra
        self.texto_completo = ""  # Texto completo a ser exibido
        self.texto_exibido = ""  # Texto já exibido (animação)
        self.tempo_animacao = 0.0  # Tempo acumulado para animação
        self.velocidade_texto = 50.0  # Caracteres por segundo
        
    def carregar_estado(self):
        """Carrega o estado do Rex"""
        if os.path.exists(CAMINHO_REX_DATA):
            try:
                with open(CAMINHO_REX_DATA, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.primeira_aparicao_mostrada = data.get('primeira_aparicao_mostrada', False)
            except Exception as e:
                print(f"Erro ao carregar estado do Rex: {e}")
                self.primeira_aparicao_mostrada = False
        else:
            self.primeira_aparicao_mostrada = False
    
    def salvar_estado(self):
        """Salva o estado do Rex"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_REX_DATA), exist_ok=True)
            data = {
                'primeira_aparicao_mostrada': self.primeira_aparicao_mostrada
            }
            with open(CAMINHO_REX_DATA, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar estado do Rex: {e}")
    
    def carregar_sprites(self):
        """Carrega os sprites do Rex"""
        if self.sprites_carregados:
            return  # Já foram carregados
        
        try:
            # Garantir que pygame está inicializado
            if not pygame.get_init():
                print("AVISO: pygame não inicializado, tentando inicializar...")
                pygame.init()
            
            print(f"Tentando carregar sprites do Rex de: {CAMINHO_SPRITES}")
            
            if os.path.exists(SPRITE_COMPETITIVE):
                self.sprite_competitive = pygame.image.load(SPRITE_COMPETITIVE).convert_alpha()
                print(f"✓ Sprite competitive carregado")
            else:
                print(f"✗ AVISO: Sprite competitive não encontrado: {SPRITE_COMPETITIVE}")
            
            if os.path.exists(SPRITE_MOCKING):
                self.sprite_mocking = pygame.image.load(SPRITE_MOCKING).convert_alpha()
                print(f"✓ Sprite mocking carregado")
            else:
                print(f"✗ AVISO: Sprite mocking não encontrado: {SPRITE_MOCKING}")
            
            if os.path.exists(SPRITE_ANGRY):
                self.sprite_angry = pygame.image.load(SPRITE_ANGRY).convert_alpha()
                print(f"✓ Sprite angry carregado")
            else:
                print(f"✗ AVISO: Sprite angry não encontrado: {SPRITE_ANGRY}")
            
            if os.path.exists(SPRITE_CHALLENGING):
                self.sprite_challenging = pygame.image.load(SPRITE_CHALLENGING).convert_alpha()
                print(f"✓ Sprite challenging carregado")
            else:
                print(f"✗ AVISO: Sprite challenging não encontrado: {SPRITE_CHALLENGING}")
            
            if os.path.exists(SPRITE_SCHEMING):
                self.sprite_scheming = pygame.image.load(SPRITE_SCHEMING).convert_alpha()
                print(f"✓ Sprite scheming carregado")
            else:
                print(f"✗ AVISO: Sprite scheming não encontrado: {SPRITE_SCHEMING}")
            
            # Carregar cena de fundo
            if os.path.exists(CAMINHO_CENA_FUNDO):
                self.sprite_fundo = pygame.image.load(CAMINHO_CENA_FUNDO).convert_alpha()
                # Redimensionar para a tela
                self.sprite_fundo = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
                print(f"✓ Cena de fundo carregada")
            else:
                print(f"✗ AVISO: Cena de fundo não encontrada: {CAMINHO_CENA_FUNDO}")
                self.sprite_fundo = None
            
            self.sprites_carregados = True
            print(f"✓ Sprites do Rex carregados")
        except Exception as e:
            print(f"ERRO ao carregar sprites do Rex: {e}")
            import traceback
            traceback.print_exc()
    
    def _verificar_carro_lixo(self, prefixo_cor):
        """Verifica se o carro do jogador é 'lixo' (poucos ou nenhum upgrade)"""
        upgrades = gerenciador_progresso.obter_todos_upgrades(prefixo_cor)
        
        # Contar quantos upgrades estão no nível máximo (5)
        upgrades_maximos = sum(1 for nivel in upgrades.values() if nivel >= 5)
        # Contar quantos upgrades estão no nível 0 (sem upgrade)
        upgrades_zerados = sum(1 for nivel in upgrades.values() if nivel == 0)
        
        # Carro é considerado "lixo" se:
        # - Tem mais upgrades zerados do que no nível 3+
        # - Ou tem menos de 2 upgrades no nível 3+
        upgrades_medio_alto = sum(1 for nivel in upgrades.values() if nivel >= 3)
        
        return upgrades_medio_alto < 2 or upgrades_zerados >= 4
    
    def verificar_aparecer(self):
        """Verifica se o Rex deve aparecer (após primeira corrida)"""
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Verificar se já mostrou a primeira aparição
        if self.primeira_aparicao_mostrada:
            return False
        
        # Verificar se completou pelo menos uma corrida
        corridas_completas = gerenciador_estatisticas.estatisticas_gerais.get("corridas_completas", 0)
        if corridas_completas < 1:
            return False
        
        # Obter o carro atual do jogador
        carro_p1_atual = gerenciador_progresso.obter_carro_atual(1)
        if carro_p1_atual is None:
            carro_p1_atual = 0  # Default para Car1
        
        from main import CARROS_DISPONIVEIS
        if 0 <= carro_p1_atual < len(CARROS_DISPONIVEIS):
            prefixo_cor = CARROS_DISPONIVEIS[carro_p1_atual]["prefixo_cor"]
        else:
            prefixo_cor = "Car1"
        
        # Determinar qual roteiro usar baseado no estado do carro
        self.roteiro_tipo = "carro_decente" if not self._verificar_carro_lixo(prefixo_cor) else "carro_lixo"
        
        # Ativar e iniciar diálogo
        self.ativo = True
        self.fase_dialogo = "apresentacao"
        self.parte_dialogo = 0
        self._iniciar_dialogo()
        
        return True
    
    def _iniciar_dialogo(self):
        """Inicia o diálogo do Rex"""
        self.parte_dialogo = 0
        self._avancar_dialogo()
    
    def _avancar_dialogo(self):
        """Avança para a próxima parte do diálogo"""
        if self.roteiro_tipo == "carro_lixo":
            self._avancar_dialogo_carro_lixo()
        else:
            self._avancar_dialogo_carro_decente()
    
    def _avancar_dialogo_carro_lixo(self):
        """Avança o diálogo para carro lixo"""
        if self.parte_dialogo == 0:
            # Parte 1: Competitive - desprezo inicial
            self.sprite_atual = self.sprite_competitive
            self._iniciar_animacao_texto("Sssshhh... (Som sibilante). O que temos aqui? Achei que hoje era dia de corrida, não de coleta de lixo reciclável.")
        elif self.parte_dialogo == 1:
            # Parte 2: Mocking - rindo
            self.sprite_atual = self.sprite_mocking
            self._iniciar_animacao_texto("Hahaha! Olha para isso! Onde você achou essas peças? Num ferro-velho ou roubou do cortador de grama da sua avó?")
        elif self.parte_dialogo == 2:
            # Parte 3: Mocking - continuação
            self.sprite_atual = self.sprite_mocking
            self._iniciar_animacao_texto("Sério, garoto. Você vai entrar na pista com *isso*? É perigoso. Você pode pegar tétano só de segurar no volante.")
        elif self.parte_dialogo == 3:
            # Parte 4: Angry - ameaça
            self.sprite_atual = self.sprite_angry
            self._iniciar_animacao_texto("Escuta aqui, sangue-quente. Eu sou o Rex. O Rei dessa pista. Isso aqui não é brincadeira de criança.")
        elif self.parte_dialogo == 4:
            # Parte 5: Angry - continuação da ameaça
            self.sprite_atual = self.sprite_angry
            self._iniciar_animacao_texto("Se você ficar na minha frente, eu não vou frear. Eu vou passar por cima. E acredite, meu para-choque vale mais que a sua vida inteira.")
        elif self.parte_dialogo == 5:
            # Parte 6: Challenging - desafio final
            self.sprite_atual = self.sprite_challenging
            self._iniciar_animacao_texto("Mas ei, se quiser doar sua taxa de inscrição para o meu fundo de champanhe, fique à vontade. Tente ver pelo menos a cor da minha lanterna traseira... se conseguir chegar perto.")
        else:
            # Fim do diálogo
            self.fechar()
    
    def _avancar_dialogo_carro_decente(self):
        """Avança o diálogo para carro decente"""
        if self.parte_dialogo == 0:
            # Parte 1: Scheming - analisando
            self.sprite_atual = self.sprite_scheming
            self._iniciar_animacao_texto("Hmmmm... ssssnif, sssnif. Motor novo. Pneus de composto macio. Interessante.")
        elif self.parte_dialogo == 1:
            # Parte 2: Scheming - continuação
            self.sprite_atual = self.sprite_scheming
            self._iniciar_animacao_texto("Parece que alguém andou gastando a mesada da mamãe na oficina. Nada mal para um primata amador.")
        elif self.parte_dialogo == 2:
            # Parte 3: Competitive - superioridade
            self.sprite_atual = self.sprite_competitive
            self._iniciar_animacao_texto("Mas não se iluda. Ter um carro rápido e ser um piloto rápido são duas coisas muito diferentes. O equipamento não compra talento... nem sangue frio.")
        elif self.parte_dialogo == 3:
            # Parte 4: Scheming - ameaça sutil
            self.sprite_atual = self.sprite_scheming
            self._iniciar_animacao_texto("Eu vi novatos como você aparecerem o tempo todo. Brilham por uma corrida e depois... *puf*. Desaparecem na primeira curva difícil. Ou na primeira 'falha mecânica' misteriosa.")
        elif self.parte_dialogo == 4:
            # Parte 5: Angry - ameaça direta
            self.sprite_atual = self.sprite_angry
            self._iniciar_animacao_texto("Eu sou o Rex. E eu não divido meu trono. Fique longe do meu traçado, ou eu vou te mandar para o muro tão rápido que você vai virar fóssil.")
        elif self.parte_dialogo == 5:
            # Parte 6: Competitive - despedida
            self.sprite_atual = self.sprite_competitive
            self._iniciar_animacao_texto("Nos vemos no pódio. Eu estarei no degrau de cima, é claro.")
        else:
            # Fim do diálogo
            self.fechar()
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
    
    def _atualizar_animacao_texto(self, dt):
        """Atualiza animação de texto letra por letra"""
        if len(self.texto_exibido) < len(self.texto_completo):
            self.tempo_animacao += dt
            caracteres_para_exibir = int(self.tempo_animacao * self.velocidade_texto)
            if caracteres_para_exibir > len(self.texto_exibido):
                self.texto_exibido = self.texto_completo[:caracteres_para_exibir]
    
    def _completar_animacao_texto(self):
        """Completa a animação de texto imediatamente"""
        self.texto_exibido = self.texto_completo
        self.tempo_animacao = 0.0
    
    def processar_eventos(self, eventos):
        """Processa eventos de entrada"""
        if not self.ativo:
            return None
        
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    # Avançar diálogo ou fechar
                    if len(self.texto_exibido) < len(self.texto_completo):
                        # Completar animação de texto
                        self._completar_animacao_texto()
                    else:
                        # Avançar para próxima parte
                        self.parte_dialogo += 1
                        self._avancar_dialogo()
                    return "processado"
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Clique do mouse
                if len(self.texto_exibido) < len(self.texto_completo):
                    # Completar animação de texto
                    self._completar_animacao_texto()
                else:
                    # Avançar para próxima parte
                    self.parte_dialogo += 1
                    self._avancar_dialogo()
                return "processado"
            elif ev.type == pygame.JOYBUTTONDOWN:
                # Botão do controle (X/A ou Options/Start para fechar)
                if ev.button == 0 or ev.button == 6:  # X/A ou Options/Start
                    if len(self.texto_exibido) < len(self.texto_completo):
                        # Completar animação de texto
                        self._completar_animacao_texto()
                    else:
                        # Avançar para próxima parte
                        self.parte_dialogo += 1
                        self._avancar_dialogo()
                    return "processado"
        
        return None
    
    def atualizar(self, dt):
        """Atualiza o estado do Rex"""
        if not self.ativo:
            return
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Rex"""
        if not self.ativo:
            return
        
        render_text = _get_render_text()
        
        # Desenhar cena de fundo
        if self.sprite_fundo:
            tela.blit(self.sprite_fundo, (0, 0))
        else:
            # Fallback: overlay escuro
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            tela.blit(overlay, (0, 0))
        
        # Desenhar sprite do Rex
        if self.sprite_atual:
            sprite_x = LARGURA // 2 - self.sprite_atual.get_width() // 2
            sprite_y = ALTURA // 2 - self.sprite_atual.get_height() // 2 - 100
            tela.blit(self.sprite_atual, (sprite_x, sprite_y))
        
        # Desenhar caixa de diálogo
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Desenhar nome do personagem
        nome_texto = render_text("REX", 24, (255, 200, 0), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Desenhar texto do diálogo
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
        
        # Desenhar indicador de continuar
        if len(self.texto_exibido) >= len(self.texto_completo):
            indicador = render_text("Pressione ENTER ou clique para continuar...", 16, (200, 200, 200), bold=False, pixel_style=True)
            indicador_x = caixa_x + caixa_largura - indicador.get_width() - 20
            indicador_y = caixa_y + caixa_altura - 30
            tela.blit(indicador, (indicador_x, indicador_y))
    
    def fechar(self):
        """Fecha o diálogo do Rex"""
        self.ativo = False
        self.primeira_aparicao_mostrada = True
        self.salvar_estado()

# Instância global
rex = Rex()

