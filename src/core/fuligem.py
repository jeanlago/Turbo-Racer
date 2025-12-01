"""Sistema do Fuligem (apelido Graxa) - Organizador do Cinturão Industrial"""
import pygame
import os
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso

def _get_gerenciador_tempo():
    """Importa gerenciador_tempo de forma lazy para evitar import circular"""
    from core.tempo_jogo import gerenciador_tempo
    return gerenciador_tempo

def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "fuligem")
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "neutro.png")
SPRITE_DESPRESO = os.path.join(CAMINHO_SPRITES, "despreso.png")
SPRITE_IRRITADO = os.path.join(CAMINHO_SPRITES, "irritado.png")

class Fuligem:
    """Fuligem (apelido Graxa) - Organizador do Cinturão Industrial"""
    
    PRECO_ENTRADA_CORRIDA = 800
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_neutro = None
        self.sprite_despreso = None
        self.sprite_irritado = None
        self.sprite_fundo = None
        self.sprites_carregados = False
        
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "fechado"
        self.parte_dialogo = 0
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 60.0
        
        self.nome_revelado = False
        self.primeira_aparicao_mostrada = False
        
        self.corrida_aberta = False
        self.pista_selecionada = None
        self.opcao_corrida_selecionada = 0
        self.corridas_disponiveis = [
            {"nome": "Rota da Caldeira", "pista": 4, "preco": 800, "dificuldade": "alta"},
            {"nome": "Circuito Industrial", "pista": 5, "preco": 800, "dificuldade": "alta"},
            {"nome": "Torneio Industrial", "pista": 6, "preco": 800, "dificuldade": "muito_alta"}
        ]
    
    def carregar_estado(self):
        """Carrega o estado do Fuligem do progresso.json"""
        self.nome_revelado = gerenciador_progresso.fuligem_nome_revelado if hasattr(gerenciador_progresso, 'fuligem_nome_revelado') else False
        self.primeira_aparicao_mostrada = gerenciador_progresso.fuligem_primeira_aparicao_mostrada if hasattr(gerenciador_progresso, 'fuligem_primeira_aparicao_mostrada') else False
    
    def salvar_estado(self):
        """Salva o estado do Fuligem no progresso.json"""
        gerenciador_progresso.fuligem_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.fuligem_primeira_aparicao_mostrada = getattr(self, 'primeira_aparicao_mostrada', False)
        gerenciador_progresso.salvar()
    
    def carregar_sprites(self):
        """Carrega os sprites do Fuligem"""
        if self.sprites_carregados:
            return
        
        try:
            print(f"[FULIGEM] Carregando sprites...")
            if os.path.exists(SPRITE_NEUTRO):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO).convert_alpha()
                print(f"[FULIGEM] ✓ Sprite neutro carregado")
            else:
                print(f"[FULIGEM] ✗ Sprite neutro não encontrado: {SPRITE_NEUTRO}")
            
            if os.path.exists(SPRITE_DESPRESO):
                self.sprite_despreso = pygame.image.load(SPRITE_DESPRESO).convert_alpha()
                print(f"[FULIGEM] ✓ Sprite desprezo carregado")
            else:
                print(f"[FULIGEM] ✗ Sprite desprezo não encontrado: {SPRITE_DESPRESO}")
            
            if os.path.exists(SPRITE_IRRITADO):
                self.sprite_irritado = pygame.image.load(SPRITE_IRRITADO).convert_alpha()
                print(f"[FULIGEM] ✓ Sprite irritado carregado")
            else:
                print(f"[FULIGEM] ✗ Sprite irritado não encontrado: {SPRITE_IRRITADO}")
            
            # Carregar fundo (usar fundo industrial/noite)
            caminho_fundo = os.path.join(DIR_PROJETO, "assets", "images", "ui", "cinturao_industrial_bg.png")
            if os.path.exists(caminho_fundo):
                self.sprite_fundo = pygame.image.load(caminho_fundo).convert_alpha()
                print(f"[FULIGEM] ✓ Fundo carregado")
            else:
                # Fallback para fundo genérico
                caminho_fundo = os.path.join(DIR_PROJETO, "assets", "images", "ui", "garage_bg.png")
                if os.path.exists(caminho_fundo):
                    self.sprite_fundo = pygame.image.load(caminho_fundo).convert_alpha()
                    print(f"[FULIGEM] ✓ Fundo fallback carregado")
                else:
                    print(f"[FULIGEM] ✗ Fundo não encontrado")
            
            self.sprites_carregados = True
        except Exception as e:
            print(f"[FULIGEM] Erro ao carregar sprites: {e}")
    
    def verificar_aparecer_primeira_vez(self) -> bool:
        """Verifica se deve mostrar a primeira aparição do Fuligem"""
        if not self.primeira_aparicao_mostrada:
            self.ativo = True
            self.fase_dialogo = "primeira_aparicao"
            self.parte_dialogo = 0
            self.sprite_atual = self.sprite_despreso or self.sprite_neutro
            self._iniciar_animacao_texto("Ei, você. Tá perdido, 'piloto'? Isso aqui não é estacionamento de shopping.")
            return True
        return False
    
    def verificar_horario_noite(self) -> bool:
        """Verifica se é noite (18h-6h)"""
        gerenciador_tempo = _get_gerenciador_tempo()
        hora_atual = gerenciador_tempo.obter_hora_atual()
        return hora_atual >= 18 or hora_atual < 6
    
    def ativar_corrida(self):
        """Ativa o menu de corridas do Cinturão"""
        if not self.verificar_horario_noite():
            # Não é noite, mostrar mensagem
            self.ativo = True
            self.fase_dialogo = "dia"
            self.sprite_atual = self.sprite_irritado or self.sprite_neutro
            self._iniciar_animacao_texto("Eles não fariam corridas assim de dia...")
            return False
        
        self.ativo = True
        self.fase_dialogo = "corrida"
        self.corrida_aberta = True
        self.sprite_atual = self.sprite_neutro or self.sprite_despreso
        return True
    
    def _iniciar_animacao_texto(self, texto: str):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
    
    def _atualizar_animacao_texto(self, dt: float):
        """Atualiza animação de texto letra por letra"""
        if not self.texto_completo:
            return
        
        if len(self.texto_exibido) < len(self.texto_completo):
            self.tempo_animacao += dt
            caracteres_para_adicionar = int(self.tempo_animacao * self.velocidade_texto)
            if caracteres_para_adicionar > len(self.texto_exibido):
                self.texto_exibido = self.texto_completo[:caracteres_para_adicionar]
    
    def processar_eventos(self, eventos):
        """Processa eventos do Fuligem"""
        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    if self.fase_dialogo == "primeira_aparicao":
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self.texto_exibido = self.texto_completo
                        else:
                            if self.parte_dialogo == 0:
                                self.parte_dialogo = 1
                                self._iniciar_animacao_texto("Aqui a gente corre no meio da ferrugem e do vapor. Se seu motor não aguentar o calor, ou se você tiver medo de amassar a lataria, dê meia volta.")
                            elif self.parte_dialogo == 1:
                                self.parte_dialogo = 2
                                self._iniciar_animacao_texto("Se quiser correr com os grandes da lama, a inscrição é comigo. O nome é Graxa. Não esquece.")
                            else:
                                # Finalizar primeira aparição
                                self.primeira_aparicao_mostrada = True
                                self.nome_revelado = True
                                self.salvar_estado()
                                self.fechar()
                                return "fechado"
                    elif self.fase_dialogo == "dia":
                        # Fechar mensagem de dia
                        self.fechar()
                        return "fechado"
                    elif self.fase_dialogo == "corrida":
                        # Processar seleção de corrida
                        if self.opcao_corrida_selecionada < len(self.corridas_disponiveis):
                            corrida = self.corridas_disponiveis[self.opcao_corrida_selecionada]
                            # Verificar se tem dinheiro
                            if gerenciador_progresso.tem_dinheiro(corrida["preco"]):
                                # Remover dinheiro e iniciar corrida
                                gerenciador_progresso.remover_dinheiro(corrida["preco"])
                                gerenciador_progresso.salvar()
                                self.pista_selecionada = corrida["pista"]
                                self.fechar()
                                return {"corrida": True, "pista": corrida["pista"], "preco": corrida["preco"]}
                            else:
                                # Não tem dinheiro suficiente
                                self._iniciar_animacao_texto(f"Você não tem dinheiro suficiente! Precisa de ${corrida['preco']:,}")
                                self.fase_dialogo = "sem_dinheiro"
                        elif self.opcao_corrida_selecionada == len(self.corridas_disponiveis):
                            # Opção "SAIR"
                            self.fechar()
                            return "fechado"
                elif evento.key in (pygame.K_UP, pygame.K_w):
                    if self.fase_dialogo == "corrida":
                        self.opcao_corrida_selecionada = (self.opcao_corrida_selecionada - 1) % (len(self.corridas_disponiveis) + 1)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    if self.fase_dialogo == "corrida":
                        self.opcao_corrida_selecionada = (self.opcao_corrida_selecionada + 1) % (len(self.corridas_disponiveis) + 1)
                elif evento.key == pygame.K_ESCAPE:
                    if self.fase_dialogo == "sem_dinheiro":
                        self.fase_dialogo = "corrida"
                    else:
                        self.fechar()
                        return "fechado"
                elif evento.key == pygame.K_ESCAPE:
                    self.fechar()
                    return "fechado"
        return None
    
    def atualizar(self, dt: float):
        """Atualiza o estado do Fuligem"""
        if self.ativo:
            self._atualizar_animacao_texto(dt)
            # Atualizar mensagem de falta de dinheiro
            if self.fase_dialogo == "sem_dinheiro":
                if len(self.texto_exibido) >= len(self.texto_completo):
                    # Mensagem completa, aguardar ESC para voltar
                    pass
    
    def desenhar(self, screen):
        """Desenha o Fuligem na tela"""
        if not self.ativo:
            return
        
        # Desenhar fundo
        if self.sprite_fundo:
            screen.blit(self.sprite_fundo, (0, 0))
        else:
            screen.fill((20, 20, 30))
        
        # Desenhar sprite do Fuligem
        if self.sprite_atual:
            x_fuligem = LARGURA - self.sprite_atual.get_width() - 50
            y_fuligem = ALTURA - self.sprite_atual.get_height() - 100
            screen.blit(self.sprite_atual, (x_fuligem, y_fuligem))
        
        # Desenhar caixa de diálogo
        if self.fase_dialogo in ["primeira_aparicao", "dia"]:
            caixa_y = ALTURA - 200
            caixa_altura = 150
            pygame.draw.rect(screen, (30, 30, 40), (20, caixa_y, LARGURA - 40, caixa_altura))
            pygame.draw.rect(screen, (100, 100, 120), (20, caixa_y, LARGURA - 40, caixa_altura), 2)
            
            # Texto
            render_text = _get_render_text()
            linhas_texto = []
            palavras = self.texto_exibido.split()
            linha_atual = ""
            for palavra in palavras:
                teste = linha_atual + (" " if linha_atual else "") + palavra
                largura_teste = render_text(teste, 24).get_width()
                if largura_teste > LARGURA - 80:
                    if linha_atual:
                        linhas_texto.append(linha_atual)
                    linha_atual = palavra
                else:
                    linha_atual = teste
            if linha_atual:
                linhas_texto.append(linha_atual)
            
            y_texto = caixa_y + 20
            for linha in linhas_texto:
                texto_surf = render_text(linha, 24)
                screen.blit(texto_surf, (40, y_texto))
                y_texto += 30
        
        # Desenhar menu de corridas
        elif self.fase_dialogo == "corrida":
            render_text = _get_render_text()
            
            # Texto do Fuligem
            texto_fuligem = "Voltou? O cheiro de óleo te atraiu ou sua carteira tá vazia? Tenho um grid se formando na Rota da Caldeira. 800 pratas a entrada. O vencedor leva o pote. Vai encarar ou vai ficar só olhando?"
            
            # Caixa de diálogo
            caixa_y = ALTURA - 350
            caixa_altura = 120
            pygame.draw.rect(screen, (30, 30, 40), (20, caixa_y, LARGURA - 40, caixa_altura))
            pygame.draw.rect(screen, (100, 100, 120), (20, caixa_y, LARGURA - 40, caixa_altura), 2)
            
            # Quebrar texto em linhas
            linhas_texto = []
            palavras = texto_fuligem.split()
            linha_atual = ""
            for palavra in palavras:
                teste = linha_atual + (" " if linha_atual else "") + palavra
                largura_teste = render_text(teste, 22).get_width()
                if largura_teste > LARGURA - 80:
                    if linha_atual:
                        linhas_texto.append(linha_atual)
                    linha_atual = palavra
                else:
                    linha_atual = teste
            if linha_atual:
                linhas_texto.append(linha_atual)
            
            y_texto = caixa_y + 15
            for linha in linhas_texto:
                texto_surf = render_text(linha, 22)
                screen.blit(texto_surf, (40, y_texto))
                y_texto += 25
            
            # Menu de corridas
            menu_y = caixa_y + caixa_altura + 20
            opcoes = [corrida["nome"] for corrida in self.corridas_disponiveis] + ["SAIR"]
            
            for i, opcao in enumerate(opcoes):
                cor = (255, 255, 0) if i == self.opcao_corrida_selecionada else (200, 200, 200)
                if i < len(self.corridas_disponiveis):
                    preco = self.corridas_disponiveis[i]["preco"]
                    texto_opcao = f"{opcao} - ${preco:,}"
                else:
                    texto_opcao = opcao
                
                texto_surf = render_text(texto_opcao, 28, cor)
                x_opcao = 40
                y_opcao = menu_y + i * 50
                screen.blit(texto_surf, (x_opcao, y_opcao))
            
            # Dinheiro atual
            dinheiro_texto = f"Créditos: ${gerenciador_progresso.dinheiro:,}"
            texto_dinheiro = render_text(dinheiro_texto, 24)
            screen.blit(texto_dinheiro, (LARGURA - texto_dinheiro.get_width() - 40, 40))
        
        elif self.fase_dialogo == "sem_dinheiro":
            # Mostrar mensagem de falta de dinheiro
            caixa_y = ALTURA - 200
            caixa_altura = 100
            pygame.draw.rect(screen, (30, 30, 40), (20, caixa_y, LARGURA - 40, caixa_altura))
            pygame.draw.rect(screen, (200, 50, 50), (20, caixa_y, LARGURA - 40, caixa_altura), 2)
            
            render_text = _get_render_text()
            texto_surf = render_text(self.texto_exibido, 24, (255, 100, 100))
            x_texto = (LARGURA - texto_surf.get_width()) // 2
            y_texto = caixa_y + (caixa_altura - texto_surf.get_height()) // 2
            screen.blit(texto_surf, (x_texto, y_texto))
    
    def fechar(self):
        """Fecha o diálogo do Fuligem"""
        self.ativo = False
        self.fase_dialogo = "fechado"
        self.corrida_aberta = False

# Instância global
fuligem = Fuligem()

