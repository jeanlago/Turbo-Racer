"""Sistema do Barão - Agiota sofisticado que oferece empréstimos com juros"""
import pygame
import os
import random
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso

def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "barao")
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "neutro.png")
SPRITE_AGUARDANDO = os.path.join(CAMINHO_SPRITES, "aguardando.png")
SPRITE_CONVENCENDO = os.path.join(CAMINHO_SPRITES, "convencendo.png")
SPRITE_RECEBENDO = os.path.join(CAMINHO_SPRITES, "recebendo.png")
SPRITE_AMEACANDO = os.path.join(CAMINHO_SPRITES, "ameacando.png")
SPRITE_DESDEM = os.path.join(CAMINHO_SPRITES, "desdem.png")
SPRITE_OFERECENDO = os.path.join(CAMINHO_SPRITES, "oferecendo.png")

CAMINHO_FUNDO = os.path.join(DIR_PROJETO, "assets", "images", "ui", "garage_bg.png")

class Barao:
    """O Barão - Agiota sofisticado que oferece empréstimos com juros"""
    
    VALOR_EMPRESTIMO = 5000
    JUROS_PORCENTAGEM = 50
    VALOR_TOTAL = int(VALOR_EMPRESTIMO * (1 + JUROS_PORCENTAGEM / 100))
    PRAZO_CORRIDAS = 3
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_neutro = None
        self.sprite_aguardando = None
        self.sprite_convencendo = None
        self.sprite_recebendo = None
        self.sprite_ameacando = None
        self.sprite_desdem = None
        self.sprite_oferecendo = None
        self.sprite_fundo = None
        self.sprites_carregados = False
        
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "fechado"
        self.parte_dialogo = 0
        self.opcao_confirmacao_selecionada = 0
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 80.0
        
        self.nome_revelado = False
        
    def carregar_estado(self):
        """Carrega o estado do Barão do progresso.json"""
        self.nome_revelado = gerenciador_progresso.barao_nome_revelado
    
    def salvar_estado(self):
        """Salva o estado do Barão no progresso.json"""
        gerenciador_progresso.barao_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.salvar()
    
    def carregar_sprites(self):
        """Carrega os sprites do Barão"""
        if self.sprites_carregados:
            return
        
        try:
            # Carregar sprites sem redimensionar (será feito no desenhar_dialogo)
            if os.path.exists(SPRITE_NEUTRO):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO).convert_alpha()
            if os.path.exists(SPRITE_AGUARDANDO):
                self.sprite_aguardando = pygame.image.load(SPRITE_AGUARDANDO).convert_alpha()
            if os.path.exists(SPRITE_CONVENCENDO):
                self.sprite_convencendo = pygame.image.load(SPRITE_CONVENCENDO).convert_alpha()
            if os.path.exists(SPRITE_RECEBENDO):
                self.sprite_recebendo = pygame.image.load(SPRITE_RECEBENDO).convert_alpha()
            if os.path.exists(SPRITE_AMEACANDO):
                self.sprite_ameacando = pygame.image.load(SPRITE_AMEACANDO).convert_alpha()
            if os.path.exists(SPRITE_DESDEM):
                self.sprite_desdem = pygame.image.load(SPRITE_DESDEM).convert_alpha()
            if os.path.exists(SPRITE_OFERECENDO):
                self.sprite_oferecendo = pygame.image.load(SPRITE_OFERECENDO).convert_alpha()
            if os.path.exists(CAMINHO_FUNDO):
                self.sprite_fundo = pygame.image.load(CAMINHO_FUNDO).convert_alpha()
                self.sprite_fundo = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
            
            self.sprites_carregados = True
        except Exception as e:
            print(f"Erro ao carregar sprites do Barão: {e}")
    
    def verificar_aparecer_oferta(self):
        """
        Verifica se o Barão deve aparecer para oferecer empréstimo
        Condições: jogador sem dinheiro, carro quebrado, perdeu corrida recente
        """
        # Não aparecer se já tem empréstimo ativo
        if gerenciador_progresso.barao_emprestimo_ativo:
            return False
        
        dinheiro = gerenciador_progresso.dinheiro
        if dinheiro > 500:  # Ainda tem algum dinheiro
            return False
        
        from core.crank import crank
        saude_carro = crank.saude_carro if hasattr(crank, 'saude_carro') else 1.0
        if saude_carro > 0.3:  # Carro não está muito quebrado
            return False
        
        # Se chegou aqui, ativar diálogo de oferta
        self.ativo = True
        self.fase_dialogo = "oferecendo"
        self.parte_dialogo = 0
        self._iniciar_dialogo_oferta()
        return True
    
    def verificar_aparecer_lembrete(self):
        """
        Verifica se o Barão deve aparecer para lembrar sobre a dívida
        Aparece aleatoriamente após corridas se o empréstimo está ativo
        """
        if not gerenciador_progresso.barao_emprestimo_ativo:
            return False
        
        # Chance de 30% de aparecer após cada corrida
        if random.random() > 0.3:
            return False
        
        # Não aparecer se já está ativo
        if self.ativo:
            return False
        
        corridas_restantes = gerenciador_progresso.barao_corridas_restantes
        if corridas_restantes <= 0:
            return False  # Vai para cobrança
        
        self.ativo = True
        self.fase_dialogo = "lembrete"
        self.parte_dialogo = 0
        self._iniciar_dialogo_lembrete()
        return True
    
    def verificar_aparecer_cobranca(self):
        """
        Verifica se o Barão deve aparecer para cobrar a dívida
        Aparece quando o prazo acabou
        """
        if not gerenciador_progresso.barao_emprestimo_ativo:
            return False
        
        if gerenciador_progresso.barao_corridas_restantes > 0:
            return False  # Ainda tem tempo
        
        # Não aparecer se já está ativo
        if self.ativo:
            return False
        
        # Verificar se jogador tem dinheiro para pagar
        dinheiro = gerenciador_progresso.dinheiro
        valor_devido = gerenciador_progresso.barao_valor_devido
        
        if dinheiro >= valor_devido:
            # Jogador tem dinheiro - diálogo de pagamento
            self.ativo = True
            self.fase_dialogo = "pagamento"
            self.parte_dialogo = 0
            self._iniciar_dialogo_pagamento()
        else:
            # Jogador não tem dinheiro - diálogo de calote
            self.ativo = True
            self.fase_dialogo = "calote"
            self.parte_dialogo = 0
            self._iniciar_dialogo_calote()
        
        return True
    
    def _iniciar_dialogo_oferta(self):
        """Inicia o diálogo de oferta de empréstimo"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.sprite_atual = self.sprite_convencendo or self.sprite_oferecendo or self.sprite_neutro
        
        falas = [
            "Mrrr... Que cena deprimente. O cheiro de óleo queimado e... desespero.",
            "Ouvi dizer que você está em apuros. Sem carro. Sem dinheiro. Sem futuro.",
            "Sorte sua que eu sou um... filantropo. Eu gosto de apostar em causas perdidas.",
            f"Eu posso injetar ${self.VALOR_EMPRESTIMO:,} para você voltar à pista. Consertar essa lata velha.",
            f"Mas ouça bem, meu jovem... O dinheiro não é de graça. Eu cobro {self.JUROS_PORCENTAGEM}% de juros.",
            f"Você tem {self.PRAZO_CORRIDAS} corridas para me pagar ${self.VALOR_TOTAL:,}.",
            "Se não pagar... bem... digamos que eu não serei tão fofinho. Sss..."
        ]
        
        if self.parte_dialogo < len(falas):
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            # Mostrar opções de aceitar/recusar
            self.fase_dialogo = "aceitar_recusar"
            self.parte_dialogo = 0
            self.opcao_confirmacao_selecionada = 0  # Começar com "Aceitar" selecionado
            self._iniciar_animacao_texto("Aceitar o empréstimo?")
    
    def _iniciar_dialogo_lembrete(self):
        """Inicia o diálogo de lembrete"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.sprite_atual = self.sprite_aguardando or self.sprite_neutro
        
        corridas_restantes = gerenciador_progresso.barao_corridas_restantes
        valor_devido = gerenciador_progresso.barao_valor_devido
        
        falas = [
            "Mrrr. Apenas verificando meu investimento.",
            f"Você tem mais {corridas_restantes} corrida{'s' if corridas_restantes > 1 else ''}.",
            f"Espero que esteja guardando os ${valor_devido:,} que me deve.",
            "Tic-tac, meu caro. Tic-tac."
        ]
        
        if self.parte_dialogo < len(falas):
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            self.fechar()
    
    def _iniciar_dialogo_pagamento(self):
        """Inicia o diálogo de pagamento"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.sprite_atual = self.sprite_recebendo or self.sprite_neutro
        
        valor_devido = gerenciador_progresso.barao_valor_devido
        
        falas = [
            "O tempo acabou. Trouxe o que é meu?",
            f"${valor_devido:,}. Exatamente."
        ]
        
        if self.parte_dialogo < len(falas):
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            # Processar pagamento
            self._processar_pagamento()
    
    def _iniciar_dialogo_calote(self):
        """Inicia o diálogo de calote (jogador não tem dinheiro)"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.sprite_atual = self.sprite_ameacando or self.sprite_neutro
        
        falas = [
            "Sss... Decepcionante. Muito decepcionante.",
            "Eu odeio quando meus investimentos não dão retorno.",
            "Um contrato é sagrado. Se você não pode pagar com dinheiro, pagará com peças.",
            "Mrrrgggh!"
        ]
        
        if self.parte_dialogo < len(falas):
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            # Processar punição
            self._processar_punicao()
    
    def _processar_pagamento(self):
        """Processa o pagamento da dívida"""
        valor_devido = gerenciador_progresso.barao_valor_devido
        
        if gerenciador_progresso.tem_dinheiro(valor_devido):
            gerenciador_progresso.remover_dinheiro(valor_devido)
            gerenciador_progresso.barao_emprestimo_ativo = False
            gerenciador_progresso.barao_valor_devido = 0
            gerenciador_progresso.barao_corridas_restantes = 0
            gerenciador_progresso.salvar()
            
            self._iniciar_animacao_texto("Excelente. Sabia que você era um bom cavalo para apostar. Volte sempre que precisar se endividar. Mrrr...")
            self.parte_dialogo = 0
            # Jogador fecha manualmente pressionando ENTER ou clicando
        else:
            # Não tem dinheiro mesmo assim (não deveria acontecer, mas...)
            self._iniciar_dialogo_calote()
    
    def _processar_punicao(self):
        """Processa a punição quando jogador não paga"""
        # Opção 1: Confiscar melhor peça do carro
        from core.crank import crank
        
        carro_atual = gerenciador_progresso.obter_carro_atual(1)
        if carro_atual is None:
            carro_atual = 0
        
        from main import CARROS_DISPONIVEIS
        if 0 <= carro_atual < len(CARROS_DISPONIVEIS):
            prefixo_cor = CARROS_DISPONIVEIS[carro_atual]['prefixo_cor']
        else:
            prefixo_cor = "Car1"
        upgrades = gerenciador_progresso.obter_todos_upgrades(prefixo_cor)
        
        # Encontrar o upgrade de maior nível
        melhor_tipo = None
        melhor_nivel = 0
        
        tipos_prioridade = ['motor', 'transmissao', 'nitro', 'ecu', 'filtro_ar', 'rodas', 'suspensao']
        
        for tipo in tipos_prioridade:
            nivel = upgrades.get(tipo, 0)
            if nivel > melhor_nivel:
                melhor_nivel = nivel
                melhor_tipo = tipo
        
        if melhor_tipo and melhor_nivel > 0:
            # Remover o upgrade (definir nível como 0)
            if prefixo_cor not in gerenciador_progresso.upgrades:
                gerenciador_progresso.upgrades[prefixo_cor] = {}
            gerenciador_progresso.upgrades[prefixo_cor][melhor_tipo] = 0
            gerenciador_progresso.salvar()
            
            # Obter nome amigável do upgrade
            from core.i18n import t
            nomes_upgrades = {
                'motor': t("menu.upgrades.motor"),
                'filtro_ar': t("menu.upgrades.filtro_ar"),
                'ecu': t("menu.upgrades.ecu"),
                'transmissao': t("menu.upgrades.transmissao"),
                'rodas': t("menu.upgrades.rodas"),
                'suspensao': t("menu.upgrades.suspensao"),
                'nitro': t("menu.upgrades.nitro")
            }
            nome_amigavel = nomes_upgrades.get(melhor_tipo, melhor_tipo)
            self._iniciar_animacao_texto(f"Esse {nome_amigavel} deve cobrir os juros por enquanto. Mrrr...")
        else:
            # Se não tem upgrades, reduzir saúde do carro drasticamente
            if hasattr(crank, 'saude_carro'):
                crank.saude_carro = max(0.1, crank.saude_carro - 0.5)
                crank.salvar_estado()
            
            self._iniciar_animacao_texto("Comece de novo, rato. E dessa vez, faça direito. Sss...")
        
        # Cancelar empréstimo após punição
        gerenciador_progresso.barao_emprestimo_ativo = False
        gerenciador_progresso.barao_valor_devido = 0
        gerenciador_progresso.barao_corridas_restantes = 0
        gerenciador_progresso.salvar()
        
        self.parte_dialogo = 0
        # Jogador fecha manualmente pressionando ENTER ou clicando
    
    def aceitar_emprestimo(self):
        """Aceita o empréstimo do Barão"""
        gerenciador_progresso.adicionar_dinheiro(self.VALOR_EMPRESTIMO)
        gerenciador_progresso.barao_emprestimo_ativo = True
        gerenciador_progresso.barao_valor_devido = self.VALOR_TOTAL
        gerenciador_progresso.barao_corridas_restantes = self.PRAZO_CORRIDAS
        gerenciador_progresso.salvar()
        
        self._iniciar_animacao_texto("Sábia decisão. O relógio está correndo. Tique-taque. Mrrr...")
        self.parte_dialogo = 0
        # Jogador fecha manualmente pressionando ENTER ou clicando
    
    def recusar_emprestimo(self):
        """Recusa o empréstimo do Barão"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.sprite_atual = self.sprite_desdem or self.sprite_neutro
        self._iniciar_animacao_texto("Tolo. Orgulho não enche tanque de gasolina. Saia da minha vista. Sss...")
        self.parte_dialogo = 0
        # Jogador fecha manualmente pressionando ENTER ou clicando
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia a animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0  # Resetar tempo de animação
    
    def _atualizar_animacao_texto(self, dt):
        """Atualiza a animação de texto letra por letra (igual ao Crank)"""
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
    
    def _completar_animacao_texto(self):
        """Completa a animação de texto imediatamente"""
        self.texto_exibido = self.texto_completo
    
    def processar_eventos(self, eventos):
        """Processa eventos de entrada (igual ao Crank)"""
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    elif self.fase_dialogo == "aceitar_recusar":
                        # Confirmar opção selecionada
                        if not hasattr(self, 'opcao_confirmacao_selecionada'):
                            self.opcao_confirmacao_selecionada = 0
                        if self.opcao_confirmacao_selecionada == 0:
                            self.aceitar_emprestimo()
                        else:
                            self.recusar_emprestimo()
                    else:
                        self._avancar_dialogo()
                elif evento.key == pygame.K_ESCAPE:
                    # Fechar diálogo ou cancelar (tratado como recusar se estiver em aceitar/recusar)
                    if self.fase_dialogo == "aceitar_recusar":
                        self.recusar_emprestimo()
                    else:
                        self.fechar()
                elif self.fase_dialogo == "aceitar_recusar" and len(self.texto_exibido) >= len(self.texto_completo):
                    # Navegação nas opções
                    from core.i18n import t
                    try:
                        aceitar_texto = t("menu.confirmar")
                        recusar_texto = t("menu.cancelar")
                    except:
                        aceitar_texto = "ACEITAR"
                        recusar_texto = "RECUSAR"
                    opcoes = [aceitar_texto, recusar_texto]
                    
                    if not hasattr(self, 'opcao_confirmacao_selecionada'):
                        self.opcao_confirmacao_selecionada = 0
                    
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        self.opcao_confirmacao_selecionada = (self.opcao_confirmacao_selecionada - 1) % len(opcoes)
                    elif evento.key in (pygame.K_DOWN, pygame.K_s):
                        self.opcao_confirmacao_selecionada = (self.opcao_confirmacao_selecionada + 1) % len(opcoes)
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.fase_dialogo == "aceitar_recusar" and len(self.texto_exibido) >= len(self.texto_completo):
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    from core.i18n import t
                    try:
                        aceitar_texto = t("menu.confirmar")
                        recusar_texto = t("menu.cancelar")
                    except:
                        aceitar_texto = "ACEITAR"
                        recusar_texto = "RECUSAR"
                    opcoes = [aceitar_texto, recusar_texto]
                    espacamento = 25
                    botao_largura = int(LARGURA * 0.45)
                    botao_x = (LARGURA - botao_largura) // 2
                    altura_total = len(opcoes) * 40 + (len(opcoes) - 1) * espacamento
                    inicio_y = (ALTURA - altura_total) // 2
                    
                    # Calcular hitboxes
                    render_text = _get_render_text()
                    y_calc = inicio_y
                    for i, opcao_nome in enumerate(opcoes):
                        texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                        texto_y_calc = y_calc
                        linha_y_calc = texto_y_calc + texto_opcao_temp.get_height() + 5
                        altura_opcao = linha_y_calc - texto_y_calc + 10
                        hitbox = pygame.Rect(botao_x, texto_y_calc, botao_largura, altura_opcao)
                        
                        if hitbox.collidepoint(mouse_x, mouse_y):
                            if i == 0:
                                self.aceitar_emprestimo()
                            else:
                                self.recusar_emprestimo()
                            break
                        
                        y_calc = linha_y_calc + espacamento
                elif len(self.texto_exibido) < len(self.texto_completo):
                    self._completar_animacao_texto()
                else:
                    # Avançar diálogo
                    self._avancar_dialogo()
            # Removido timer automático - jogador fecha manualmente pressionando ENTER ou clicando
    
    def _avancar_dialogo(self):
        """Avança para a próxima parte do diálogo"""
        self.parte_dialogo += 1
        
        if self.fase_dialogo == "oferecendo":
            self._iniciar_dialogo_oferta()
        elif self.fase_dialogo == "lembrete":
            self._iniciar_dialogo_lembrete()
        elif self.fase_dialogo == "pagamento":
            self._iniciar_dialogo_pagamento()
        elif self.fase_dialogo == "calote":
            self._iniciar_dialogo_calote()
    
    def atualizar(self, dt):
        """Atualiza o estado do Barão"""
        if not self.ativo:
            return
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Barão (seguindo o padrão do Crank)"""
        if not self.ativo:
            return
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Overlay escuro no fundo (estilo visual novel)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))  # Preto com 140/255 de opacidade
        tela.blit(overlay, (0, 0))
        
        # Personagem no canto esquerdo (igual ao Crank)
        lado_direito = False
        
        # Tamanho do sprite (igual ao Crank)
        sprite_altura_max = 400
        sprite_largura_max = 350
        
        # Redimensionar sprite mantendo proporção
        sprite_redimensionado = None
        sprite_w = 0
        sprite_h = 0
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
        
        # Posição do sprite (igual ao Crank)
        if sprite_redimensionado:
            sprite_y = ALTURA - sprite_h - 150  # Posição acima da caixa (abaixado para não flutuar)
            
            if lado_direito:
                sprite_x = LARGURA - sprite_w - 20
            else:
                sprite_x = 20
            
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        cor_contorno = (255, 220, 100)
        
        render_text = _get_render_text()
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, cor_contorno, (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Nome do personagem
        nome = "O Barão" if getattr(self, 'nome_revelado', False) else "???"
        nome_texto = render_text(nome, 24, (255, 220, 100), bold=True, pixel_style=True)
        tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Atualizar animação de texto
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
        
        if self.fase_dialogo == "aceitar_recusar" and len(self.texto_exibido) >= len(self.texto_completo):
            from core.i18n import t
            try:
                aceitar_texto = t("menu.confirmar")  # Usar "Confirmar" como aceitar
                recusar_texto = t("menu.cancelar")  # Usar "Cancelar" como recusar
            except:
                aceitar_texto = "ACEITAR"
                recusar_texto = "RECUSAR"
            opcoes = [aceitar_texto, recusar_texto]
            espacamento = 25
            botao_largura = int(LARGURA * 0.45)
            botao_x = (LARGURA - botao_largura) // 2
            
            # Calcular posição Y para centralizar verticalmente
            altura_total = len(opcoes) * 40 + (len(opcoes) - 1) * espacamento
            inicio_y = (ALTURA - altura_total) // 2
            y_atual = inicio_y
            
            # Obter posição do mouse para hover
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Calcular hitboxes
            hitboxes = []
            y_calc = inicio_y
            for opcao_nome in opcoes:
                texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                texto_y_calc = y_calc
                linha_y_calc = texto_y_calc + texto_opcao_temp.get_height() + 5
                altura_opcao = linha_y_calc - texto_y_calc + 10
                hitboxes.append(pygame.Rect(botao_x, texto_y_calc, botao_largura, altura_opcao))
                y_calc = linha_y_calc + espacamento
            
            # Determinar qual opção está sob o mouse
            opcao_hover = None
            for i, rect in enumerate(hitboxes):
                if rect.collidepoint(mouse_x, mouse_y):
                    opcao_hover = i
                    break
            
            if not hasattr(self, 'opcao_confirmacao_selecionada'):
                self.opcao_confirmacao_selecionada = 0
            
            # Desenhar opções
            for i, opcao_nome in enumerate(opcoes):
                hover = (opcao_hover == i)
                selecionado = (self.opcao_confirmacao_selecionada == i)
                
                # Cor do texto: hover tem prioridade, senão mostrar seleção por teclado
                if hover:
                    cor_texto = (255, 255, 0)  # Amarelo quando hover
                    cor_linha = (255, 255, 0)  # Amarelo
                elif selecionado:
                    cor_texto = (255, 200, 0)  # Laranja quando selecionado
                    cor_linha = (255, 200, 0)  # Laranja
                else:
                    cor_texto = (180, 180, 180)  # Cinza quando não selecionado
                    cor_linha = (100, 100, 100)  # Cinza escuro
                
                # Desenhar texto da opção (centralizado)
                texto_opcao = render_text(opcao_nome, 24, cor_texto, bold=False, pixel_style=False)
                texto_opcao_x = botao_x + (botao_largura - texto_opcao.get_width()) // 2
                tela.blit(texto_opcao, (texto_opcao_x, y_atual))
                
                # Desenhar linha embaixo do texto
                linha_largura = botao_largura - 80
                linha_x = botao_x + (botao_largura - linha_largura) // 2
                linha_y = y_atual + texto_opcao.get_height() + 5
                pygame.draw.line(tela, cor_linha, (linha_x, linha_y), (linha_x + linha_largura, linha_y), 1)
                
                y_atual = linha_y + espacamento
        
        # Desenhar indicador de continuar (igual ao Crank - canto inferior direito)
        elif len(self.texto_exibido) >= len(self.texto_completo):
            indicador = render_text("Pressione ENTER ou clique para continuar...", 16, (200, 200, 200), bold=False, pixel_style=True)
            indicador_x = caixa_x + caixa_largura - indicador.get_width() - 20
            indicador_y = caixa_y + caixa_altura - 30
            tela.blit(indicador, (indicador_x, indicador_y))
    
    def fechar(self):
        """Fecha a interação com o Barão"""
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "fechado"
        self.parte_dialogo = 0
        self.texto_completo = ""
        self.texto_exibido = ""

# Instância global
barao = Barao()

