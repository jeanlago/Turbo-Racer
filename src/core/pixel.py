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
SPRITE_DIGITANDO = os.path.join(CAMINHO_SPRITES, "digitando.png")
SPRITE_DIGITANDO_FALLBACK = os.path.join(CAMINHO_SPRITES, "ocupado.png")
SPRITE_ASSUSTADO = os.path.join(CAMINHO_SPRITES, "assustado.png")
SPRITE_ASSUSTADO_FALLBACK = os.path.join(CAMINHO_SPRITES, "silêncio.png")
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "neutro.png")
SPRITE_NEUTRO_FALLBACK = os.path.join(CAMINHO_SPRITES, "Gemini_Generated_Image_4kuc1f4kuc1f4kuc.png")
SPRITE_PARANOICO = os.path.join(CAMINHO_SPRITES, "paranoico.png")
SPRITE_PARANOICO_FALLBACK = os.path.join(CAMINHO_SPRITES, "silêncio.png")
SPRITE_VENDENDO = os.path.join(CAMINHO_SPRITES, "vendendo.png")
SPRITE_VENDENDO_FALLBACK = os.path.join(CAMINHO_SPRITES, "oferta.png")

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
        
        self.informacoes_disponiveis = []
        self._gerar_informacoes()
    
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
            # Carregar sprites com fallback para arquivos existentes
            if os.path.exists(SPRITE_DIGITANDO):
                self.sprite_digitando = pygame.image.load(SPRITE_DIGITANDO).convert_alpha()
            elif os.path.exists(SPRITE_DIGITANDO_FALLBACK):
                self.sprite_digitando = pygame.image.load(SPRITE_DIGITANDO_FALLBACK).convert_alpha()
            
            if os.path.exists(SPRITE_ASSUSTADO):
                self.sprite_assustado = pygame.image.load(SPRITE_ASSUSTADO).convert_alpha()
            elif os.path.exists(SPRITE_ASSUSTADO_FALLBACK):
                self.sprite_assustado = pygame.image.load(SPRITE_ASSUSTADO_FALLBACK).convert_alpha()
            
            if os.path.exists(SPRITE_NEUTRO):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO).convert_alpha()
            elif os.path.exists(SPRITE_NEUTRO_FALLBACK):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO_FALLBACK).convert_alpha()
            
            if os.path.exists(SPRITE_PARANOICO):
                self.sprite_paranoico = pygame.image.load(SPRITE_PARANOICO).convert_alpha()
            elif os.path.exists(SPRITE_PARANOICO_FALLBACK):
                self.sprite_paranoico = pygame.image.load(SPRITE_PARANOICO_FALLBACK).convert_alpha()
            
            if os.path.exists(SPRITE_VENDENDO):
                self.sprite_vendendo = pygame.image.load(SPRITE_VENDENDO).convert_alpha()
            elif os.path.exists(SPRITE_VENDENDO_FALLBACK):
                self.sprite_vendendo = pygame.image.load(SPRITE_VENDENDO_FALLBACK).convert_alpha()
            
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
                    self._iniciar_dialogo_explodiu()
                    return True
            # Se não ganhou todas ou já mostrou, abrir loja normalmente
            if not self.sprites_carregados:
                self.carregar_sprites()
            self.ativo = True
            self.fase_dialogo = "loja"
            self._abrir_loja()
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
            self.fase_dialogo = "loja"
            self._abrir_loja()
    
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
        self.sprite_atual = self.sprite_digitando if self.sprite_digitando else self.sprite_neutro
        
        saudacoes = [
            "Você de novo? Rápido, estou no meio de uma descriptografia de nível 5. O que você quer?",
            "Espero que não tenha sido seguido. Meus sensores de proximidade estão apitando que nem loucos. Fala logo.",
            "Se veio pedir fiado, a resposta é 404: Crédito Não Encontrado. Se veio comprar, o menu está na tela.",
            "Shhh. Estou ouvindo a frequência da polícia. Eles estão montando uma blitz na Avenida Central. Viu? Informação de graça. A próxima vai custar."
        ]
        texto = random.choice(saudacoes)
        self._iniciar_animacao_texto(texto)
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        
        texto_lower = texto.lower()
        if "pixel" in texto_lower or "meu nome" in texto_lower or "me chamo pixel" in texto_lower:
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
                elif evento.key == pygame.K_ESCAPE:
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
        
        if self.sprite_atual:
            sprite_original_w = self.sprite_atual.get_width()
            sprite_original_h = self.sprite_atual.get_height()
            sprite_novo_w = int(sprite_original_w * 0.7)
            sprite_novo_h = int(sprite_original_h * 0.7)
            sprite_redimensionado = pygame.transform.scale(self.sprite_atual, (sprite_novo_w, sprite_novo_h))
            
            sprite_x = LARGURA // 2 - sprite_novo_w // 2
            sprite_y = int(ALTURA * 0.6) - sprite_novo_h // 2
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        # Fundo da caixa
        overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay_caixa.fill((0, 0, 0, 200))
        tela.blit(overlay_caixa, (caixa_x, caixa_y))
        
        # Borda da caixa (verde para tema tecnológico)
        pygame.draw.rect(tela, (0, 255, 0), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Nome do personagem
        nome = "Pixel" if self.nome_revelado else "???"
        nome_texto = render_text(nome, 20, (0, 255, 100), bold=True, pixel_style=True)
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
    
    def fechar(self):
        """Fecha o diálogo do Pixel"""
        self.ativo = False
        self.loja_aberta = False
        self.informacao_selecionada = None

# Instância global
pixel = Pixel()

