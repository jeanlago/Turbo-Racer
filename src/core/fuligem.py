"""Sistema do Fuligem (apelido Graxa) - Organizador do Cinturão Industrial"""
import pygame
import os
import sys

# Adicionar o diretório src ao path se necessário (para quando executado diretamente)
if __name__ == "__main__":
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

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
# Tentar diferentes nomes de sprites disponíveis
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "fuligem_neutro - Copia.png")
SPRITE_DESPRESO = os.path.join(CAMINHO_SPRITES, "fuligem_bravo.png")
SPRITE_IRRITADO = os.path.join(CAMINHO_SPRITES, "fuligem_bravo.png")

class Fuligem:
    """Fuligem (apelido Graxa) - Organizador do Cinturão Industrial"""
    
    PRECO_ENTRADA_CORRIDA = 800
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_neutro = None
        self.sprite_despreso = None
        self.sprite_irritado = None
        self.sprite_fundo = None
        self.sprite_fundo_redimensionado = None  # Cache do fundo redimensionado
        self.sprites_redimensionados_cache = {}  # Cache de sprites redimensionados
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
        # Corridas com preços diferentes e recompensas diferentes
        # Corrida mais cara = mais recompensa
        self.corridas_disponiveis = [
            {"nome": "Rota da Caldeira", "pista": 4, "preco": 800, "recompensa": 2000, "dificuldade": "alta", "indice": 0},
            {"nome": "Circuito Industrial", "pista": 5, "preco": 1200, "recompensa": 3500, "dificuldade": "alta", "indice": 1},
            {"nome": "Torneio Industrial", "pista": 6, "preco": 2000, "recompensa": 6000, "dificuldade": "muito_alta", "indice": 2}
        ]
    
    def carregar_estado(self):
        """Carrega o estado do Fuligem do progresso.json"""
        self.nome_revelado = gerenciador_progresso.fuligem_nome_revelado if hasattr(gerenciador_progresso, 'fuligem_nome_revelado') else False
        self.primeira_aparicao_mostrada = gerenciador_progresso.fuligem_primeira_aparicao_mostrada if hasattr(gerenciador_progresso, 'fuligem_primeira_aparicao_mostrada') else False
        
        # Carregar corridas desbloqueadas
        if not hasattr(gerenciador_progresso, 'fuligem_corridas_desbloqueadas'):
            gerenciador_progresso.fuligem_corridas_desbloqueadas = [0]  # Corrida 1 (índice 0) sempre desbloqueada
        self.corridas_desbloqueadas = set(gerenciador_progresso.fuligem_corridas_desbloqueadas) if isinstance(gerenciador_progresso.fuligem_corridas_desbloqueadas, list) else set([0])
    
    def salvar_estado(self):
        """Salva o estado do Fuligem no progresso.json"""
        gerenciador_progresso.fuligem_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.fuligem_primeira_aparicao_mostrada = getattr(self, 'primeira_aparicao_mostrada', False)
        gerenciador_progresso.fuligem_corridas_desbloqueadas = list(self.corridas_desbloqueadas) if isinstance(self.corridas_desbloqueadas, set) else self.corridas_desbloqueadas
        gerenciador_progresso.salvar()
    
    def obter_corridas_disponiveis(self):
        """Retorna apenas as corridas desbloqueadas"""
        return [corrida for corrida in self.corridas_disponiveis if corrida["indice"] in self.corridas_desbloqueadas]
    
    def desbloquear_corrida(self, indice_corrida):
        """Desbloqueia uma corrida específica"""
        if indice_corrida not in self.corridas_desbloqueadas:
            self.corridas_desbloqueadas.add(indice_corrida)
            self.salvar_estado()
            print(f"[FULIGEM] Corrida {indice_corrida} desbloqueada!")
    
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
            
            # Carregar fundo (usar fundo cinturão noite)
            caminho_fundo = os.path.join(DIR_PROJETO, "assets", "images", "ui", "cinturao_noite.png")
            if os.path.exists(caminho_fundo):
                self.sprite_fundo = pygame.image.load(caminho_fundo).convert_alpha()
                # Redimensionar fundo para a resolução da tela
                from config import LARGURA, ALTURA
                self.sprite_fundo_redimensionado = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
                print(f"[FULIGEM] ✓ Fundo carregado e redimensionado")
            else:
                print(f"[FULIGEM] ✗ Fundo não encontrado: {caminho_fundo}")
            
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
                                # Salvar progresso e missões após interação
                                gerenciador_progresso.salvar()
                                from core.missoes import gerenciador_missoes
                                gerenciador_missoes.salvar()
                                self.fechar()
                                return "fechado"
                    elif self.fase_dialogo == "dia":
                        # Fechar mensagem de dia
                        # Salvar progresso antes de fechar
                        gerenciador_progresso.salvar()
                        self.fechar()
                        return "fechado"
                    elif self.fase_dialogo == "corrida":
                        # Processar seleção de corrida
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        if self.opcao_corrida_selecionada < len(corridas_disponiveis):
                            corrida = corridas_disponiveis[self.opcao_corrida_selecionada]
                            # Verificar se tem dinheiro
                            if gerenciador_progresso.tem_dinheiro(corrida["preco"]):
                                # Remover dinheiro e iniciar corrida
                                gerenciador_progresso.remover_dinheiro(corrida["preco"])
                                gerenciador_progresso.salvar()
                                self.pista_selecionada = corrida["pista"]
                                self.fechar()
                                return {"corrida": True, "pista": corrida["pista"], "preco": corrida["preco"], "recompensa": corrida["recompensa"], "indice": corrida["indice"]}
                            else:
                                # Não tem dinheiro suficiente
                                self._iniciar_animacao_texto(f"Você não tem dinheiro suficiente! Precisa de ${corrida['preco']:,}")
                                self.fase_dialogo = "sem_dinheiro"
                        elif self.opcao_corrida_selecionada == len(corridas_disponiveis):
                            # Opção "SAIR"
                            # Salvar progresso antes de fechar
                            gerenciador_progresso.salvar()
                            self.fechar()
                            return "fechado"
                elif evento.key in (pygame.K_UP, pygame.K_w):
                    if self.fase_dialogo == "corrida":
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        self.opcao_corrida_selecionada = (self.opcao_corrida_selecionada - 1) % (len(corridas_disponiveis) + 1)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    if self.fase_dialogo == "corrida":
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        self.opcao_corrida_selecionada = (self.opcao_corrida_selecionada + 1) % (len(corridas_disponiveis) + 1)
                elif evento.key == pygame.K_ESCAPE:
                    # ESC fecha o diálogo do Fuligem
                    if self.fase_dialogo == "sem_dinheiro":
                        self.fase_dialogo = "corrida"
                    else:
                        # Salvar progresso antes de fechar
                        gerenciador_progresso.salvar()
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
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Fuligem no estilo visual novel (igual aos outros NPCs)"""
        if not self.ativo:
            return
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        render_text = _get_render_text()
        
        # Usar fundo redimensionado em cache
        if self.sprite_fundo_redimensionado:
            tela.blit(self.sprite_fundo_redimensionado, (0, 0))
        elif self.sprite_fundo:
            # Se não tiver cache, criar uma vez (fallback)
            from config import LARGURA, ALTURA
            self.sprite_fundo_redimensionado = pygame.transform.scale(self.sprite_fundo, (LARGURA, ALTURA))
            tela.blit(self.sprite_fundo_redimensionado, (0, 0))
        else:
            # Fallback: overlay escuro
            from config import LARGURA, ALTURA
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            tela.blit(overlay, (0, 0))
        
        if self.sprite_atual:
            # Usar cache de sprite redimensionado (igual ao Boris)
            if self.sprite_atual not in self.sprites_redimensionados_cache:
                sprite_original_w = self.sprite_atual.get_width()
                sprite_original_h = self.sprite_atual.get_height()
                # Diminuir escala para 0.60 (60%) para deixar o Fuligem bem menor que o Boris
                sprite_novo_w = int(sprite_original_w * 0.30)
                sprite_novo_h = int(sprite_original_h * 0.30)
                self.sprites_redimensionados_cache[self.sprite_atual] = pygame.transform.scale(self.sprite_atual, (sprite_novo_w, sprite_novo_h))
            
            sprite_redimensionado = self.sprites_redimensionados_cache[self.sprite_atual]
            sprite_novo_w, sprite_novo_h = sprite_redimensionado.get_size()
            
            from config import LARGURA, ALTURA
            # Posicionar centralizado como o Boris
            sprite_x = LARGURA // 2 - sprite_novo_w // 2
            # Posicionar mais próximo do chão, bem acima da caixa de diálogo (igual ao Boris)
            sprite_y = ALTURA - sprite_novo_h - 130
            tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        # Garantir que LARGURA e ALTURA estão disponíveis
        from config import LARGURA, ALTURA
        
        # Desenhar caixa de diálogo
        if self.fase_dialogo in ["primeira_aparicao", "dia"]:
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
            nome = "GRAXA" if self.nome_revelado else "???"
            nome_texto = render_text(nome, 20, (255, 200, 0), bold=True, pixel_style=True)
            tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
            
            # Atualizar animação de texto
            self._atualizar_animacao_texto(dt)
            
            # Texto do diálogo com quebra de linha
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
            
            # Indicador de avanço
            if len(self.texto_exibido) >= len(self.texto_completo):
                indicador = render_text("Pressione ESPAÇO ou clique para continuar", 14, (150, 150, 150), bold=False, pixel_style=True)
                tela.blit(indicador, (caixa_x + caixa_largura - 400, caixa_y + caixa_altura - 30))
        
        # Desenhar menu de corridas
        elif self.fase_dialogo == "corrida":
            # Caixa de diálogo com texto do Fuligem (mesma posição das outras caixas)
            texto_fuligem = "Voltou? O cheiro de óleo te atraiu ou sua carteira tá vazia? Tenho um grid se formando na Rota da Caldeira. 800 pratas a entrada. O vencedor leva o pote. Vai encarar ou vai ficar só olhando?"
            
            caixa_largura = 1000
            caixa_altura = 200  # Mesmo tamanho das outras caixas
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = ALTURA - caixa_altura - 50  # Mesma posição das outras caixas
            
            # Fundo da caixa
            overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
            overlay_caixa.fill((0, 0, 0, 200))
            tela.blit(overlay_caixa, (caixa_x, caixa_y))
            
            # Borda da caixa
            pygame.draw.rect(tela, (100, 100, 100), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
            
            # Nome do personagem
            nome = "GRAXA" if self.nome_revelado else "???"
            nome_texto = render_text(nome, 20, (255, 200, 0), bold=True, pixel_style=True)
            tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
            
            # Quebrar texto em linhas
            palavras = texto_fuligem.split(' ')
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
            
            # Menu de corridas (centralizado na tela, acima da caixa de diálogo)
            corridas_disponiveis = self.obter_corridas_disponiveis()
            opcoes = [corrida["nome"] for corrida in corridas_disponiveis] + ["SAIR"]
            menu_largura = 600
            menu_altura = len(opcoes) * 50 + 20
            menu_x = (LARGURA - menu_largura) // 2  # Centralizar o menu
            menu_y = caixa_y - menu_altura - 30  # Acima da caixa de diálogo
            
            # Fundo do menu de corridas
            menu_overlay = pygame.Surface((menu_largura, menu_altura), pygame.SRCALPHA)
            menu_overlay.fill((0, 0, 0, 180))
            tela.blit(menu_overlay, (menu_x, menu_y))
            pygame.draw.rect(tela, (150, 150, 150), (menu_x, menu_y, menu_largura, menu_altura), 2)
            
            for i, opcao in enumerate(opcoes):
                cor = (255, 255, 0) if i == self.opcao_corrida_selecionada else (200, 200, 200)
                if i < len(corridas_disponiveis):
                    preco = corridas_disponiveis[i]["preco"]
                    texto_opcao = f"{opcao} - ${preco:,}"
                else:
                    texto_opcao = opcao
                
                texto_surf = render_text(texto_opcao, 28, cor, bold=True, pixel_style=True)
                x_opcao = menu_x + 20
                y_opcao = menu_y + 10 + i * 50
                tela.blit(texto_surf, (x_opcao, y_opcao))
            
            # Dinheiro atual
            dinheiro_texto = f"Créditos: ${gerenciador_progresso.dinheiro:,}"
            texto_dinheiro = render_text(dinheiro_texto, 24, (255, 255, 255), bold=True, pixel_style=True)
            tela.blit(texto_dinheiro, (LARGURA - texto_dinheiro.get_width() - 40, 40))
        
        elif self.fase_dialogo == "sem_dinheiro":
            # Mostrar mensagem de falta de dinheiro
            caixa_largura = 1000
            caixa_altura = 200
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = ALTURA - caixa_altura - 50
            
            # Fundo da caixa
            overlay_caixa = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
            overlay_caixa.fill((0, 0, 0, 200))
            tela.blit(overlay_caixa, (caixa_x, caixa_y))
            
            # Borda da caixa (vermelha para erro)
            pygame.draw.rect(tela, (200, 50, 50), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
            
            # Nome do personagem
            nome = "GRAXA" if self.nome_revelado else "???"
            nome_texto = render_text(nome, 20, (255, 200, 0), bold=True, pixel_style=True)
            tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
            
            # Atualizar animação de texto
            self._atualizar_animacao_texto(dt)
            
            # Texto da mensagem
            if self.texto_exibido:
                palavras = self.texto_exibido.split(' ')
                linhas = []
                linha_atual = ""
                for palavra in palavras:
                    teste_linha = linha_atual + (" " if linha_atual else "") + palavra
                    teste_render = render_text(teste_linha, 18, (255, 100, 100), bold=False, pixel_style=True)
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
                    linha_render = render_text(linha, 18, (255, 100, 100), bold=False, pixel_style=True)
                    tela.blit(linha_render, (caixa_x + 20, y_texto))
                    y_texto += 25
            
            # Indicador de avanço
            if len(self.texto_exibido) >= len(self.texto_completo):
                indicador = render_text("Pressione ESC para voltar", 14, (150, 150, 150), bold=False, pixel_style=True)
                tela.blit(indicador, (caixa_x + caixa_largura - 300, caixa_y + caixa_altura - 30))
    
    def fechar(self):
        """Fecha o diálogo do Fuligem"""
        self.ativo = False
        self.fase_dialogo = "fechado"
        self.corrida_aberta = False

# Instância global
fuligem = Fuligem()

