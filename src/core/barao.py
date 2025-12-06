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
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "barao_neutro.png")
SPRITE_INOCENTE = os.path.join(CAMINHO_SPRITES, "barao_inocente.png")
SPRITE_SORRISO_FINO = os.path.join(CAMINHO_SPRITES, "barao_sorriso_fino.png")
SPRITE_SORRISO_LARGO = os.path.join(CAMINHO_SPRITES, "barao_sorriso_largo.png")

# CAMINHO_FUNDO será carregado dinamicamente baseado em dia/noite
from config import obter_caminho_sprite_dia_noite

class Barao:
    """O Barão - Agiota sofisticado que oferece empréstimos com juros"""
    
    VALOR_EMPRESTIMO = 5000
    JUROS_PORCENTAGEM = 50
    VALOR_TOTAL = int(VALOR_EMPRESTIMO * (1 + JUROS_PORCENTAGEM / 100))
    PRAZO_CORRIDAS = 3
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_neutro = None
        self.sprite_inocente = None
        self.sprite_sorriso_fino = None
        self.sprite_sorriso_largo = None
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
        # Garantir que o nome seja revelado se já foi apresentado na narrativa
        from core.narrative_system import narrative_system
        if "ch2_2_barao_offer" in narrative_system.scenes_visited:
            self.nome_revelado = True
            gerenciador_progresso.barao_nome_revelado = True
    
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
            if os.path.exists(SPRITE_INOCENTE):
                self.sprite_inocente = pygame.image.load(SPRITE_INOCENTE).convert_alpha()
            if os.path.exists(SPRITE_SORRISO_FINO):
                self.sprite_sorriso_fino = pygame.image.load(SPRITE_SORRISO_FINO).convert_alpha()
            if os.path.exists(SPRITE_SORRISO_LARGO):
                self.sprite_sorriso_largo = pygame.image.load(SPRITE_SORRISO_LARGO).convert_alpha()
            # Carregar fundo do iate baseado em dia/noite
            CAMINHO_FUNDO_IATE = obter_caminho_sprite_dia_noite("iate_barao")
            if os.path.exists(CAMINHO_FUNDO_IATE):
                self.sprite_fundo = pygame.image.load(CAMINHO_FUNDO_IATE).convert_alpha()
                self.sprite_fundo = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
            else:
                # Fallback para garage_bg se iate não existir
                CAMINHO_FUNDO_FALLBACK = os.path.join(DIR_PROJETO, "assets", "images", "ui", "garage_bg.png")
                if os.path.exists(CAMINHO_FUNDO_FALLBACK):
                    self.sprite_fundo = pygame.image.load(CAMINHO_FUNDO_FALLBACK).convert_alpha()
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
    
    def ativar_dialogo_visita(self):
        """Ativa o diálogo quando o jogador visita o iate pela primeira vez"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Garantir que o sprite seja definido antes de ativar
        if not self.sprite_atual:
            self.sprite_atual = self.sprite_sorriso_fino or self.sprite_neutro
        
        self.ativo = True
        self.fase_dialogo = "visita"
        self.parte_dialogo = 0
        self._iniciar_dialogo_visita()
        return True
    
    def _iniciar_dialogo_visita(self):
        """Inicia o diálogo de visita ao iate"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        falas = [
            "Mrrr... Então decidiu ouvir a razão.",
            "Bem-vindo ao meu iate. Eu sou o Barão, e você... você precisa de dinheiro.",
            "Vejo que você tem ambição. Gosto disso. Mas ambição sem capital é apenas... frustração.",
            f"Posso te oferecer ${self.VALOR_EMPRESTIMO:,}. É dinheiro suficiente para você se reerguer.",
            f"Mas não é de graça, claro. Eu cobro {self.JUROS_PORCENTAGEM}% de juros.",
            f"Você terá {self.PRAZO_CORRIDAS} corridas para me pagar ${self.VALOR_TOTAL:,}.",
            "Se não pagar a tempo... bem, digamos que não serei tão cordial. Sss..."
        ]
        
        # Mapear cada fala para o sprite mais adequado
        sprites_por_fala = [
            self.sprite_neutro,  # "Mrrr... Então decidiu ouvir a razão."
            self.sprite_sorriso_fino,  # "Bem-vindo ao meu iate..."
            self.sprite_sorriso_fino,  # "Vejo que você tem ambição..."
            self.sprite_sorriso_largo,  # "Posso te oferecer..."
            self.sprite_inocente,  # "Mas não é de graça..."
            self.sprite_neutro,  # "Você terá X corridas..."
            self.sprite_inocente,  # "Se não pagar a tempo..."
        ]
        
        if self.parte_dialogo < len(falas):
            # Definir sprite baseado na fala atual
            sprite_para_fala = sprites_por_fala[self.parte_dialogo] or self.sprite_neutro
            self.sprite_atual = sprite_para_fala
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            # Mostrar opções de aceitar/recusar
            self.fase_dialogo = "aceitar_recusar"
            self.parte_dialogo = 0
            self.opcao_confirmacao_selecionada = 0  # Começar com "Aceitar" selecionado
            self._iniciar_animacao_texto("Aceitar o empréstimo?")
    
    def _iniciar_dialogo_oferta(self):
        """Inicia o diálogo de oferta de empréstimo"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        falas = [
            "Mrrr... Que cena deprimente. O cheiro de óleo queimado e... desespero.",
            "Ouvi dizer que você está em apuros. Sem carro. Sem dinheiro. Sem futuro.",
            "Sorte sua que eu sou um... filantropo. Eu gosto de apostar em causas perdidas.",
            f"Eu posso injetar ${self.VALOR_EMPRESTIMO:,} para você voltar à pista. Consertar essa lata velha.",
            f"Mas ouça bem, meu jovem... O dinheiro não é de graça. Eu cobro {self.JUROS_PORCENTAGEM}% de juros.",
            f"Você tem {self.PRAZO_CORRIDAS} corridas para me pagar ${self.VALOR_TOTAL:,}.",
            "Se não pagar... bem... digamos que eu não serei tão fofinho. Sss..."
        ]
        
        # Mapear cada fala para o sprite mais adequado
        sprites_por_fala = [
            self.sprite_neutro,  # "Mrrr... Que cena deprimente..."
            self.sprite_inocente,  # "Ouvi dizer que você está em apuros..."
            self.sprite_sorriso_fino,  # "Sorte sua que eu sou um... filantropo..."
            self.sprite_sorriso_largo,  # "Eu posso injetar..."
            self.sprite_inocente,  # "Mas ouça bem..."
            self.sprite_neutro,  # "Você tem X corridas..."
            self.sprite_inocente,  # "Se não pagar..."
        ]
        
        if self.parte_dialogo < len(falas):
            # Definir sprite baseado na fala atual
            sprite_para_fala = sprites_por_fala[self.parte_dialogo] or self.sprite_neutro
            self.sprite_atual = sprite_para_fala
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
        
        corridas_restantes = gerenciador_progresso.barao_corridas_restantes
        valor_devido = gerenciador_progresso.barao_valor_devido
        
        falas = [
            "Mrrr. Apenas verificando meu investimento.",
            f"Você tem mais {corridas_restantes} corrida{'s' if corridas_restantes > 1 else ''}.",
            f"Espero que esteja guardando os ${valor_devido:,} que me deve.",
            "Tic-tac, meu caro. Tic-tac."
        ]
        
        # Mapear cada fala para o sprite mais adequado
        sprites_por_fala = [
            self.sprite_neutro,  # "Mrrr. Apenas verificando..."
            self.sprite_neutro,  # "Você tem mais X corridas..."
            self.sprite_inocente,  # "Espero que esteja guardando..."
            self.sprite_sorriso_fino,  # "Tic-tac, meu caro..."
        ]
        
        if self.parte_dialogo < len(falas):
            # Definir sprite baseado na fala atual
            sprite_para_fala = sprites_por_fala[self.parte_dialogo] or self.sprite_neutro
            self.sprite_atual = sprite_para_fala
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            self.fechar()
    
    def _iniciar_dialogo_pagamento(self):
        """Inicia o diálogo de pagamento"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        valor_devido = gerenciador_progresso.barao_valor_devido
        
        falas = [
            "O tempo acabou. Trouxe o que é meu?",
            f"${valor_devido:,}. Exatamente."
        ]
        
        # Mapear cada fala para o sprite mais adequado
        sprites_por_fala = [
            self.sprite_neutro,  # "O tempo acabou..."
            self.sprite_sorriso_largo,  # "Exatamente." (satisfeito com o pagamento)
        ]
        
        if self.parte_dialogo < len(falas):
            # Definir sprite baseado na fala atual
            sprite_para_fala = sprites_por_fala[self.parte_dialogo] or self.sprite_neutro
            self.sprite_atual = sprite_para_fala
            self._iniciar_animacao_texto(falas[self.parte_dialogo])
        else:
            # Processar pagamento
            self._processar_pagamento()
    
    def _iniciar_dialogo_calote(self):
        """Inicia o diálogo de calote (jogador não tem dinheiro)"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        falas = [
            "Sss... Decepcionante. Muito decepcionante.",
            "Eu odeio quando meus investimentos não dão retorno.",
            "Um contrato é sagrado. Se você não pode pagar com dinheiro, pagará com peças.",
            "Mrrrgggh!"
        ]
        
        # Mapear cada fala para o sprite mais adequado
        sprites_por_fala = [
            self.sprite_neutro,  # "Sss... Decepcionante..."
            self.sprite_neutro,  # "Eu odeio quando..."
            self.sprite_inocente,  # "Um contrato é sagrado..." (irônico)
            self.sprite_neutro,  # "Mrrrgggh!" (irritado)
        ]
        
        if self.parte_dialogo < len(falas):
            # Definir sprite baseado na fala atual
            sprite_para_fala = sprites_por_fala[self.parte_dialogo] or self.sprite_neutro
            self.sprite_atual = sprite_para_fala
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
        
        # Completar missão m8_oferta_envenenada quando aceita o empréstimo
        from core.missoes import gerenciador_missoes
        gerenciador_missoes.completar_por_cena("ch2_4_loan_accepted")
        
        self.sprite_atual = self.sprite_sorriso_largo  # Satisfeito ao aceitar
        self.fase_dialogo = "aceito"
        self.parte_dialogo = 0
        self._iniciar_animacao_texto("Sábia decisão. O relógio está correndo. Tique-taque. Mrrr...")
    
    def recusar_emprestimo(self):
        """Recusa o empréstimo do Barão"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Completar missão m8_oferta_envenenada quando recusa o empréstimo
        from core.missoes import gerenciador_missoes
        gerenciador_missoes.completar_por_cena("ch2_5_loan_refused")
        
        self.sprite_atual = self.sprite_neutro  # Neutro/irritado ao recusar
        self.fase_dialogo = "recusado"
        self.parte_dialogo = 0
        self._iniciar_animacao_texto("Tolo. Orgulho não enche tanque de gasolina. Saia da minha vista. Sss...")
    
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
                    elif self.fase_dialogo in ["aceito", "recusado"]:
                        # Fechar diálogo após aceitar ou recusar
                        self.fechar()
                        return "fechado"
                    else:
                        self._avancar_dialogo()
                elif evento.key == pygame.K_ESCAPE:
                    # Fechar diálogo ou cancelar (tratado como recusar se estiver em aceitar/recusar)
                    if self.fase_dialogo == "aceitar_recusar":
                        self.recusar_emprestimo()
                    elif self.fase_dialogo in ["aceito", "recusado"]:
                        self.fechar()
                        return "fechado"
                    else:
                        self.fechar()
                        return "fechado"
                elif self.fase_dialogo == "aceitar_recusar" and len(self.texto_exibido) >= len(self.texto_completo):
                    # Navegação nas opções
                    aceitar_texto = "ACEITAR EMPRÉSTIMO"
                    recusar_texto = "SAIR"
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
                    aceitar_texto = "ACEITAR EMPRÉSTIMO"
                    recusar_texto = "SAIR"
                    opcoes = [aceitar_texto, recusar_texto]
                    
                    # Calcular hitboxes baseado na caixa de confirmação (mesmo estilo da tela de upgrade)
                    caixa_confirmacao_largura = 500
                    caixa_confirmacao_altura = 180
                    caixa_confirmacao_x = (LARGURA - caixa_confirmacao_largura) // 2
                    caixa_confirmacao_y = ALTURA - caixa_confirmacao_altura - 260
                    
                    # Verificar clique nas opções dentro da caixa de confirmação
                    for i, opcao_nome in enumerate(opcoes):
                        y_opcao = caixa_confirmacao_y + 105 + i * 30
                        rect_opcao = pygame.Rect(caixa_confirmacao_x + 40, y_opcao, caixa_confirmacao_largura - 80, 30)
                        
                        if rect_opcao.collidepoint(mouse_x, mouse_y):
                            if i == 0:
                                self.aceitar_emprestimo()
                            else:
                                self.recusar_emprestimo()
                            break
                elif len(self.texto_exibido) < len(self.texto_completo):
                    self._completar_animacao_texto()
                elif self.fase_dialogo in ["aceito", "recusado"]:
                    # Fechar diálogo após aceitar ou recusar
                    self.fechar()
                    return "fechado"
                else:
                    # Avançar diálogo
                    self._avancar_dialogo()
            # Removido timer automático - jogador fecha manualmente pressionando ENTER ou clicando
    
    def _avancar_dialogo(self):
        """Avança para a próxima parte do diálogo"""
        self.parte_dialogo += 1
        
        if self.fase_dialogo == "visita":
            self._iniciar_dialogo_visita()
        elif self.fase_dialogo == "oferecendo":
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
        
        # Desenhar fundo do iate primeiro (se existir)
        if self.sprite_fundo:
            tela.blit(self.sprite_fundo, (0, 0))
        else:
            # Recarregar fundo se não estiver carregado (pode ter mudado dia/noite)
            CAMINHO_FUNDO_IATE = obter_caminho_sprite_dia_noite("iate_barao")
            if os.path.exists(CAMINHO_FUNDO_IATE):
                try:
                    self.sprite_fundo = pygame.image.load(CAMINHO_FUNDO_IATE).convert_alpha()
                    self.sprite_fundo = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
                    tela.blit(self.sprite_fundo, (0, 0))
                except Exception as e:
                    print(f"Erro ao recarregar fundo do iate: {e}")
        
        # Overlay escuro no fundo (estilo visual novel)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))  # Preto com 140/255 de opacidade
        tela.blit(overlay, (0, 0))
        
        # Personagem centralizado na tela
        # Tamanho do sprite (igual ao Crank)
        sprite_altura_max = 400
        sprite_largura_max = 350
        
        # Redimensionar sprite mantendo proporção
        sprite_redimensionado = None
        sprite_w = 0
        sprite_h = 0
        
        # Garantir que o sprite seja definido
        if not self.sprite_atual:
            self.sprite_atual = self.sprite_sorriso_fino or self.sprite_neutro
        
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
        
        # Posição do sprite (centralizado na tela)
        if sprite_redimensionado:
            sprite_y = ALTURA - sprite_h - 150  # Posição acima da caixa (abaixado para não flutuar)
            sprite_x = (LARGURA - sprite_w) // 2  # Centralizado horizontalmente
            
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
        
        # Nome do personagem - sempre mostrar "O Barão" se já foi apresentado na narrativa
        from core.progresso import gerenciador_progresso
        nome = "O Barão" if gerenciador_progresso.barao_nome_revelado else "???"
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
            aceitar_texto = "ACEITAR EMPRÉSTIMO"
            recusar_texto = "SAIR"
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
            
            # Desenhar opções no estilo da tela de upgrade (caixa de confirmação)
            caixa_confirmacao_largura = 500
            caixa_confirmacao_altura = 180
            caixa_confirmacao_x = (LARGURA - caixa_confirmacao_largura) // 2
            caixa_confirmacao_y = ALTURA - caixa_confirmacao_altura - 260
            
            overlay_confirmacao = pygame.Surface((caixa_confirmacao_largura, caixa_confirmacao_altura), pygame.SRCALPHA)
            overlay_confirmacao.fill((0, 0, 0, 220))
            tela.blit(overlay_confirmacao, (caixa_confirmacao_x, caixa_confirmacao_y))
            pygame.draw.rect(tela, (255, 255, 255), (caixa_confirmacao_x, caixa_confirmacao_y, caixa_confirmacao_largura, caixa_confirmacao_altura), 2)
            
            titulo = render_text("OFERTA DO BARÃO", 22, (255, 255, 0), bold=True, pixel_style=True)
            tela.blit(titulo, (caixa_confirmacao_x + (caixa_confirmacao_largura - titulo.get_width()) // 2, caixa_confirmacao_y + 10))
            
            desc = render_text(f"Empréstimo de ${self.VALOR_EMPRESTIMO:,}", 18, (220, 220, 220), bold=False, pixel_style=True)
            preco_txt = render_text(f"Total a pagar: ${self.VALOR_TOTAL:,}", 18, (180, 255, 180), bold=False, pixel_style=True)
            tela.blit(desc, (caixa_confirmacao_x + 20, caixa_confirmacao_y + 45))
            tela.blit(preco_txt, (caixa_confirmacao_x + 20, caixa_confirmacao_y + 70))
            
            # Desenhar opções no estilo da tela de upgrade
            for i, texto_opcao in enumerate(opcoes):
                cor = (0, 200, 255) if (opcao_hover == i or self.opcao_confirmacao_selecionada == i) else (200, 200, 200)
                txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
                y = caixa_confirmacao_y + 105 + i * 30
                tela.blit(txt, (caixa_confirmacao_x + 40, y))
        
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

