"""Sistema do Crank - Mecânico rabugento que reage ao desempenho do jogador"""
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

CAMINHO_CRANK_DATA = os.path.join(DIR_PROJETO, "data", "crank.json")

CAMINHO_ICONS = os.path.join(DIR_PROJETO, "assets", "images", "icons")
ICONE_SETA = os.path.join(CAMINHO_ICONS, "seta.png")
ICONE_ENCARECEU = os.path.join(CAMINHO_ICONS, "encareceu.png")

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "crank")
SPRITE_NORMAL = os.path.join(CAMINHO_SPRITES, "normal.png")
SPRITE_ALEGRE = os.path.join(CAMINHO_SPRITES, "alegre.png")
SPRITE_BRAVO = os.path.join(CAMINHO_SPRITES, "bravo.png")
SPRITE_ESTRESSADO = os.path.join(CAMINHO_SPRITES, "estressado.png")
SPRITE_DUVIDA = os.path.join(CAMINHO_SPRITES, "duvida.png")
SPRITE_SURPRESO = os.path.join(CAMINHO_SPRITES, "surpreso.png")
SPRITE_TRISTE = os.path.join(CAMINHO_SPRITES, "triste.png")
SPRITE_CONVENCIDO = os.path.join(CAMINHO_SPRITES, "convencido.png")
SPRITE_INCREDULO = os.path.join(CAMINHO_SPRITES, "incredulo.png")

class Crank:
    """Crank - Mecânico rabugento que reage ao desempenho do jogador"""
    
    HUMOR_MUITO_BRAVO = -2
    HUMOR_BRAVO = -1
    HUMOR_NORMAL = 0
    HUMOR_FELIZ = 1
    HUMOR_MUITO_FELIZ = 2
    
    MULTIPLICADORES_PRECO = {
        HUMOR_MUITO_BRAVO: 1.5,
        HUMOR_BRAVO: 1.25,
        HUMOR_NORMAL: 1.0,
        HUMOR_FELIZ: 0.9,
        HUMOR_MUITO_FELIZ: 0.8
    }
    
    def __init__(self):
        self.nome_revelado = False
        self.carregar_estado()
        self.sprite_normal = None
        self.sprite_alegre = None
        self.sprite_bravo = None
        self.sprite_estressado = None
        self.sprite_duvida = None
        self.sprite_surpreso = None
        self.sprite_triste = None
        self.sprite_convencido = None
        self.sprite_incredulo = None
        self.sprites_carregados = False
        
        # Ícones para feedback de preço
        self.icone_seta = None
        self.icone_encareceu = None
        self.icones_carregados = False
        
        # Sprite do Glub para aparecer escurecido durante o diálogo
        self.glub_sprite_escurecido = None
        self.glub_sprite_carregado = False
        
        # Flag para evitar logs repetidos de erro de sprite
        self._erro_sprite_impresso = False
        
        # Estado atual da interação
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "veredito"  # "veredito", "resposta", "reacao", "dano_critico", "upsell", "tutorial", "fechado", "dialogo_alien"
        self.humor_atual = self.HUMOR_NORMAL  # Humor atual do mecânico
        self.opcao_selecionada = 0  # Opção selecionada nas respostas (0, 1, 2)
        self.precisa_resposta = False  # Se precisa de resposta do jogador
        self.mudanca_preco = 0  # Mudança de preço após resposta (-1 = diminuiu, 0 = manteve, 1 = aumentou)
        
        # Dados da última corrida (para reação)
        self.ultima_corrida = {
            'posicao': None,
            'colisoes': 0,
            'venceu': False
        }
        
        # Sistema de dano do carro (0.0 a 1.0, onde 1.0 = 100% saudável)
        # Nota: saude_carro é carregado em carregar_estado()
        self.prefixo_cor_ultimo_carro = None  # Rastreia qual carro teve dano registrado
        
        # Tutorial - primeira aparição
        # Nota: tutorial_mostrado e tutorial_upgrades_mostrado são carregados em carregar_estado()
        # Não resetar aqui, senão sobrescreve o estado salvo!
        self.tutorial_parte = 0  # Parte atual do tutorial (0 = apresentação sombra, 1 = dúvida, 2 = perguntar nome, 3, 4, 5 = partes normais)
        self.tutorial_fase_apresentacao = "sombra"  # "sombra" -> "duvida" -> "perguntar_nome" -> "tutorial"
        self.input_nome_ativo = False  # Flag para controlar input de nome
        self.nome_input = ""  # Nome sendo digitado
        self.tutorial_upgrades_parte = 0  # Parte atual do tutorial de upgrades
        
        
        # Diálogo raro sobre compras do mercador alien
        self.dialogo_alien_parte = 0  # Parte atual do diálogo sobre compra alien
        self.dialogo_alien_tipo = None  # 'golpe', 'upgrade_especial', 'multi_upgrade'
        
        # Sistema de animação de texto
        self.texto_completo = ""  # Texto completo a ser exibido
        self.texto_exibido = ""  # Texto já exibido (animação)
        self.tempo_animacao = 0.0  # Tempo acumulado para animação
        self.velocidade_texto = 80.0  # Caracteres por segundo (aumentado para 80 para reduzir lag)
        
    def carregar_sprites(self):
        """Carrega os sprites do Crank"""
        if self.sprites_carregados:
            return  # Já foram carregados
        
        try:
            # Garantir que pygame está inicializado
            if not pygame.get_init():
                print("AVISO: pygame não inicializado, tentando inicializar...")
                pygame.init()
            
            print(f"Tentando carregar sprites do Crank de: {CAMINHO_SPRITES}")
            
            if os.path.exists(SPRITE_NORMAL):
                self.sprite_normal = pygame.image.load(SPRITE_NORMAL).convert_alpha()
                print(f"✓ Sprite normal carregado")
            else:
                print(f"✗ AVISO: Sprite normal não encontrado: {SPRITE_NORMAL}")
            
            if os.path.exists(SPRITE_ALEGRE):
                self.sprite_alegre = pygame.image.load(SPRITE_ALEGRE).convert_alpha()
                print(f"✓ Sprite alegre carregado")
            else:
                print(f"✗ AVISO: Sprite alegre não encontrado: {SPRITE_ALEGRE}")
            
            if os.path.exists(SPRITE_BRAVO):
                self.sprite_bravo = pygame.image.load(SPRITE_BRAVO).convert_alpha()
                print(f"✓ Sprite bravo carregado")
            else:
                print(f"✗ AVISO: Sprite bravo não encontrado: {SPRITE_BRAVO}")
            
            if os.path.exists(SPRITE_ESTRESSADO):
                self.sprite_estressado = pygame.image.load(SPRITE_ESTRESSADO).convert_alpha()
                print(f"✓ Sprite estressado carregado")
            else:
                print(f"✗ AVISO: Sprite estressado não encontrado: {SPRITE_ESTRESSADO}")
            
            if os.path.exists(SPRITE_DUVIDA):
                self.sprite_duvida = pygame.image.load(SPRITE_DUVIDA).convert_alpha()
                print(f"✓ Sprite duvida carregado")
            else:
                print(f"✗ AVISO: Sprite duvida não encontrado: {SPRITE_DUVIDA}")
            
            if os.path.exists(SPRITE_SURPRESO):
                self.sprite_surpreso = pygame.image.load(SPRITE_SURPRESO).convert_alpha()
                print(f"✓ Sprite surpreso carregado")
            else:
                print(f"✗ AVISO: Sprite surpreso não encontrado: {SPRITE_SURPRESO}")
            
            if os.path.exists(SPRITE_TRISTE):
                self.sprite_triste = pygame.image.load(SPRITE_TRISTE).convert_alpha()
                print(f"✓ Sprite triste carregado")
            else:
                print(f"✗ AVISO: Sprite triste não encontrado: {SPRITE_TRISTE}")
            
            if os.path.exists(SPRITE_CONVENCIDO):
                self.sprite_convencido = pygame.image.load(SPRITE_CONVENCIDO).convert_alpha()
                print(f"✓ Sprite convencido carregado")
            else:
                print(f"✗ AVISO: Sprite convencido não encontrado: {SPRITE_CONVENCIDO}")
            
            if os.path.exists(SPRITE_INCREDULO):
                self.sprite_incredulo = pygame.image.load(SPRITE_INCREDULO).convert_alpha()
                print(f"✓ Sprite incredulo carregado")
            else:
                print(f"✗ AVISO: Sprite incredulo não encontrado: {SPRITE_INCREDULO}")
            
            self.sprites_carregados = True
            # Resetar flag de erro quando sprites são carregados com sucesso
            self._erro_sprite_impresso = False
            
            # Carregar sprite do Glub para aparecer escurecido durante o diálogo
            self._carregar_sprite_glub()
            
            # Carregar ícones
            self._carregar_icones()
        except Exception as e:
            print(f"ERRO ao carregar sprites do Crank: {e}")
            import traceback
            traceback.print_exc()
    
    def _carregar_icones(self):
        """Carrega os ícones para feedback de preço"""
        if self.icones_carregados:
            return
        
        try:
            if os.path.exists(ICONE_SETA):
                self.icone_seta = pygame.image.load(ICONE_SETA).convert_alpha()
                print(f"✓ Ícone seta carregado: {ICONE_SETA}")
            else:
                print(f"✗ AVISO: Ícone seta não encontrado: {ICONE_SETA}")
            
            if os.path.exists(ICONE_ENCARECEU):
                self.icone_encareceu = pygame.image.load(ICONE_ENCARECEU).convert_alpha()
                print(f"✓ Ícone encareceu carregado: {ICONE_ENCARECEU}")
            else:
                print(f"✗ AVISO: Ícone encareceu não encontrado: {ICONE_ENCARECEU}")
            
            self.icones_carregados = True
        except Exception as e:
            print(f"ERRO ao carregar ícones do Crank: {e}")
    
    def _carregar_sprite_glub(self):
        """Carrega o sprite do Glub para aparecer escurecido durante o diálogo"""
        if self.glub_sprite_carregado:
            return
        
        try:
            from config import DIR_PROJETO
            caminho_glub_sprites = os.path.join(DIR_PROJETO, "assets", "images", "characters", "glub")
            sprite_glub_encontro = os.path.join(caminho_glub_sprites, "encontro.png")
            
            if os.path.exists(sprite_glub_encontro):
                self.glub_sprite_escurecido = pygame.image.load(sprite_glub_encontro).convert_alpha()
                self.glub_sprite_carregado = True
                print(f"✓ Sprite do Glub carregado para diálogo do Crank")
            else:
                print(f"✗ AVISO: Sprite do Glub não encontrado: {sprite_glub_encontro}")
        except Exception as e:
            print(f"AVISO: Não foi possível carregar sprite do Glub: {e}")
    
    def carregar_estado(self):
        """Carrega o estado do Crank do progresso.json"""
        # Garantir que os valores padrão são usados se não existirem no progresso
        self.humor_atual = getattr(gerenciador_progresso, 'crank_humor_atual', 0)
        self.saude_carro = getattr(gerenciador_progresso, 'crank_saude_carro', 1.0)
        self.tutorial_mostrado = getattr(gerenciador_progresso, 'crank_tutorial_mostrado', False)
        self.tutorial_upgrades_mostrado = getattr(gerenciador_progresso, 'crank_tutorial_upgrades_mostrado', False)
        self.prefixo_cor_ultimo_carro = getattr(gerenciador_progresso, 'crank_prefixo_cor_ultimo_carro', None)
        self.nome_revelado = getattr(gerenciador_progresso, 'crank_nome_revelado', False)
    
    def salvar_estado(self):
        """Salva o estado do Crank no progresso.json"""
        gerenciador_progresso.crank_humor_atual = self.humor_atual
        gerenciador_progresso.crank_saude_carro = self.saude_carro
        gerenciador_progresso.crank_tutorial_mostrado = getattr(self, 'tutorial_mostrado', False)
        gerenciador_progresso.crank_tutorial_upgrades_mostrado = getattr(self, 'tutorial_upgrades_mostrado', False)
        gerenciador_progresso.crank_prefixo_cor_ultimo_carro = getattr(self, 'prefixo_cor_ultimo_carro', None)
        gerenciador_progresso.crank_nome_revelado = getattr(self, 'nome_revelado', False)
        gerenciador_progresso.salvar()
    
    def registrar_corrida(self, posicao, colisoes, venceu):
        """Registra os dados da última corrida"""
        from core.progresso import gerenciador_progresso
        from main import CARROS_DISPONIVEIS
        
        carro_p1_atual = gerenciador_progresso.obter_carro_atual(1)
        if carro_p1_atual is None:
            carro_p1_atual = 0
        
        if 0 <= carro_p1_atual < len(CARROS_DISPONIVEIS):
            prefixo_cor_atual = CARROS_DISPONIVEIS[carro_p1_atual]["prefixo_cor"]
        else:
            prefixo_cor_atual = "Car1"
        
        # Se o carro mudou, resetar saúde
        if not hasattr(self, 'prefixo_cor_ultimo_carro') or self.prefixo_cor_ultimo_carro != prefixo_cor_atual:
            self.saude_carro = 1.0
            self.prefixo_cor_ultimo_carro = prefixo_cor_atual
        
        self.ultima_corrida = {
            'posicao': posicao,
            'colisoes': colisoes,
            'venceu': venceu
        }
        
        # Calcular dano baseado em colisões (cada colisão reduz 5% da saúde)
        dano_por_colisao = 0.05
        self.saude_carro = max(0.0, self.saude_carro - (colisoes * dano_por_colisao))
        
        # Atualizar humor baseado no desempenho
        self._atualizar_humor()
        self.salvar_estado()
    
    def _atualizar_humor(self):
        """Atualiza o humor do Crank baseado no desempenho da corrida"""
        colisoes = self.ultima_corrida['colisoes']
        venceu = self.ultima_corrida['venceu']
        posicao = self.ultima_corrida['posicao']
        
        # REGRA PRINCIPAL: Dano excessivo sempre pesa mais que vitória
        # Se Colisões ≥ 5, o humor é sempre "Bravo" ou "Muito Bravo", 
        # independente se ele chegou em 1º ou último.
        
        if colisoes >= 5:
            # Muitas colisões = muito bravo (mesmo se venceu)
            self.humor_atual = self.HUMOR_MUITO_BRAVO
        elif colisoes >= 3:
            # Algumas colisões = bravo
            self.humor_atual = self.HUMOR_BRAVO
        elif venceu and colisoes == 0:
            # Venceu sem colisões = muito feliz
            self.humor_atual = self.HUMOR_MUITO_FELIZ
        elif venceu and colisoes < 3:
            # Venceu com poucas colisões = feliz
            self.humor_atual = self.HUMOR_FELIZ
        elif colisoes == 0:
            # Sem colisões mas perdeu = normal
            self.humor_atual = self.HUMOR_NORMAL
        else:
            # Poucas colisões mas perdeu = bravo
            self.humor_atual = self.HUMOR_BRAVO
    
    def verificar_aparecer_pos_corrida(self):
        """
        Verifica se o Crank deve aparecer após uma corrida (veredito)
        Retorna True se deve aparecer
        """
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Sempre aparecer após corrida para dar veredito
        if self.ultima_corrida['posicao'] is not None:
            self.ativo = True
            self.fase_dialogo = "veredito"
            self._definir_sprite_e_texto_veredito()
            return True
        
        return False
    
    def verificar_aparecer_dano_critico(self):
        """
        Verifica se o Crank deve aparecer por dano crítico
        Retorna True se saúde < 20%
        Verifica também se o carro mudou (se mudou, reseta a saúde)
        """
        from core.progresso import gerenciador_progresso
        from main import CARROS_DISPONIVEIS
        
        carro_p1_atual = gerenciador_progresso.obter_carro_atual(1)
        if carro_p1_atual is None:
            carro_p1_atual = 0
        
        if 0 <= carro_p1_atual < len(CARROS_DISPONIVEIS):
            prefixo_cor_atual = CARROS_DISPONIVEIS[carro_p1_atual]["prefixo_cor"]
        else:
            prefixo_cor_atual = "Car1"
        
        # Se não temos um prefixo_cor salvo ou mudou, resetar saúde
        if not hasattr(self, 'prefixo_cor_ultimo_carro') or self.prefixo_cor_ultimo_carro != prefixo_cor_atual:
            self.saude_carro = 1.0
            self.prefixo_cor_ultimo_carro = prefixo_cor_atual
            self.salvar_estado()
            return False  # Carro novo, não precisa reclamar
        
        if self.saude_carro < 0.2:
            if not self.sprites_carregados:
                self.carregar_sprites()
            
            self.ativo = True
            self.fase_dialogo = "dano_critico"
            self._definir_sprite_e_texto_dano_critico()
            return True
        
        return False
    
    def verificar_aparecer_dialogo_alien(self):
        """
        Verifica se o Crank deve aparecer para comentar sobre compras do mercador alien
        Retorna True se deve aparecer (apenas na primeira vez que vai na oficina após comprar)
        """
        from core.progresso import gerenciador_progresso
        
        ultima_compra = gerenciador_progresso.obter_ultima_compra_alien()
        if not ultima_compra:
            return False
        
        # Se o diálogo já foi mostrado para esta compra, não mostrar novamente
        if gerenciador_progresso.dialogo_alien_ja_mostrado:
            return False
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Definir tipo de diálogo baseado na compra
        self.dialogo_alien_tipo = ultima_compra.get('tipo')
        if not self.dialogo_alien_tipo:
            return False
        
        # Ativar diálogo
        self.ativo = True
        self.fase_dialogo = "dialogo_alien"
        self._iniciar_dialogo_alien()
        return True
    
    def _iniciar_dialogo_alien(self):
        """Inicia o diálogo raro sobre compras do mercador alien"""
        print(f"DEBUG: _iniciar_dialogo_alien chamado, tipo: {self.dialogo_alien_tipo}")
        self.dialogo_alien_parte = 0
        self._avancar_dialogo_alien()
        print(f"DEBUG: Após _avancar_dialogo_alien, texto_completo: {self.texto_completo[:50] if self.texto_completo else 'None'}...")
    
    def _finalizar_dialogo_alien(self):
        """Finaliza o diálogo alien e marca como já mostrado"""
        from core.progresso import gerenciador_progresso
        # Marcar que o diálogo já foi mostrado para esta compra
        gerenciador_progresso.dialogo_alien_ja_mostrado = True
        # Limpar a compra registrada
        gerenciador_progresso.limpar_ultima_compra_alien()
        # Fechar o diálogo
        self.fechar()
    
    def verificar_reacao_instalacao_upgrade(self, tipo_upgrade, nivel_novo, prefixo_cor):
        """
        Verifica se deve mostrar reação do Crank ao instalar um upgrade
        Retorna True se deve mostrar reação
        """
        # Não mostrar se já estiver ativo
        if self.ativo:
            return False
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Determinar qualidade da peça baseado no nível
        # Nível 1 = Lixo/Sucata
        # Nível 2-3 = Padrão/Honesta
        # Nível 4-5 = Alta Performance
        if nivel_novo == 1:
            qualidade = "lixo"
        elif nivel_novo in (2, 3):
            qualidade = "padrao"
        else:  # 4 ou 5
            qualidade = "alta_performance"
        
        # e motor, turbo, nitro são de força bruta
        pecas_drift = ['suspensao', 'pneus']
        pecas_forca_bruta = ['motor', 'turbo', 'nitro']
        
        origem = None
        if tipo_upgrade in pecas_drift:
            origem = "akira"  # Drift
        elif tipo_upgrade in pecas_forca_bruta:
            origem = "boris"  # Força bruta
        
        # Ativar diálogo
        self.ativo = True
        self.fase_dialogo = "reacao_instalacao"
        self.reacao_instalacao_qualidade = qualidade
        self.reacao_instalacao_origem = origem
        self.reacao_instalacao_tipo = tipo_upgrade
        self.reacao_instalacao_nivel = nivel_novo
        self._iniciar_reacao_instalacao()
        return True
    
    def _iniciar_reacao_instalacao(self):
        """Inicia a reação do Crank à instalação de upgrade"""
        qualidade = self.reacao_instalacao_qualidade
        origem = self.reacao_instalacao_origem
        tipo_upgrade = self.reacao_instalacao_tipo
        nivel = self.reacao_instalacao_nivel
        
        nome_upgrade = self._nome_upgrade_instalacao(tipo_upgrade)
        
        # Selecionar sprite e texto baseado na qualidade
        if qualidade == "lixo":
            # Peça lixo - ofensa pessoal
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_normal
            
            textos = [
                f"* [Cospe no chão] * Você chama isso de {nome_upgrade}? Eu chamo de peneira. Vou instalar, mas não venha chorar no meu ouvido quando o motor ferver na segunda volta.",
                f"Eu deveria cobrar taxa de insalubridade só por tocar nessa sucata. Você está insultando a máquina com essa peça, garoto.",
                f"Sério? Essa {nome_upgrade} parece que foi feita de elástico de dinheiro. Hmpf. É o seu funeral, não o meu.",
                f"Isso aqui não é peça, é um remendo temporário que vai durar cinco minutos. Você está jogando dinheiro fora."
            ]
        
        elif qualidade == "padrao":
            # Peça padrão - aceita sem entusiasmo
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_bravo
            
            textos = [
                f"Hmpf. Serve. Não é nenhuma maravilha da engenharia, mas pelo menos não parece que vai explodir na ignição.",
                f"Uma escolha... razoável. É o feijão com arroz. Vai fazer o trabalho, se você não forçar demais.",
                f"Instalado. Agora tente não quebrar isso na primeira curva, ok? Eu tenho mais o que fazer."
            ]
        
        else:  # alta_performance
            # Peça alta performance - impressionado
            if self.sprite_alegre:
                self.sprite_atual = self.sprite_alegre
            elif self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            else:
                self.sprite_atual = self.sprite_normal
            
            textos = [
                f"Olha só... {nome_upgrade.capitalize()} de qualidade. Onde você roubou isso? Não importa. * [Limpa a mão na roupa antes de tocar] * Instalar isso vai ser a melhor parte do meu dia. Tente não estragar meu trabalho.",
                f"Hmpf. Finalmente gastou dinheiro com algo que preste. Esse {nome_upgrade} é uma obra de arte. Não ouse fundir isso.",
                f"* [Assobio baixo] * {nome_upgrade.capitalize()} de ponta. Isso sim é música para os meus ouvidos. O motor vai roncar agradecido.",
                f"Agora estamos conversando. Isso não é só uma peça, é um investimento. Trate-a com respeito na pista."
            ]
        
        # Adicionar comentário sobre origem se aplicável
        texto_base = random.choice(textos)
        
        if origem == "akira" and qualidade in ("padrao", "alta_performance"):
            # Comentário sobre peças de drift
            comentario_origem = " Suspensão rebaixada e pneus slicks duros? Você andou tomando chá demais com aquela panda nas colinas, né? Hmpf. Ficar andando de lado só gasta borracha à toa. Mas se é isso que você quer..."
            texto_base = texto_base + comentario_origem
        elif origem == "boris" and qualidade in ("padrao", "alta_performance"):
            # Comentário sobre peças de força bruta
            comentario_origem = f" Esse {nome_upgrade} pesa uma tonelada e cheira a óleo queimado do ferro-velho do Javali. É estúpido, barulhento e bruto. * [Pausa dramática] * Eu adorei. Vamos fazer esse monstro gritar."
            texto_base = texto_base + comentario_origem
        
        self._iniciar_animacao_texto(texto_base)
    
    def _nome_upgrade_instalacao(self, tipo):
        """Retorna o nome amigável do upgrade para reações"""
        nomes = {
            'motor': 'motor',
            'freios': 'freios',
            'suspensao': 'suspensão',
            'pneus': 'pneus',
            'turbo': 'turbo',
            'nitro': 'nitro'
        }
        return nomes.get(tipo, 'peça')
    
    def _avancar_dialogo_alien(self):
        """Avança para a próxima parte do diálogo sobre compras alien"""
        if self.dialogo_alien_tipo == 'golpe':
            self._avancar_dialogo_alien_golpe()
        elif self.dialogo_alien_tipo == 'upgrade_especial':
            self._avancar_dialogo_alien_melhoria()
        elif self.dialogo_alien_tipo == 'multi_upgrade':
            self._avancar_dialogo_alien_multimelhoria()
    
    def _avancar_dialogo_alien_golpe(self):
        """Avança o diálogo sobre golpe do mercador alien"""
        if self.dialogo_alien_parte == 0:
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_normal if self.sprite_normal else None
            texto_completo = "Mas que P***ARIA é essa debaixo do capô?!"
            print(f"DEBUG: Iniciando animação texto: {texto_completo}")
            self._iniciar_animacao_texto(texto_completo)
            print(f"DEBUG: Após _iniciar_animacao_texto, texto_completo: {self.texto_completo}, texto_exibido: {self.texto_exibido}")
        
        elif self.dialogo_alien_parte == 1:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Pointing/Lecturing
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            texto_completo = "Eu fui trocar o filtro de óleo e achei ISSO conectado na bateria. Uma caixa de plástico que pisca luzinha roxa e faz 'bip-bop'."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 2:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Smug/Dismissive
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            texto_completo = "Deixa eu adivinhar... você comprou daquele vendedor de aspirador de pó intergaláctico, né? O magrelo verde que fala esquisito."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 3:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Smug/Dismissive
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            texto_completo = "Parabéns, piloto. Você trocou dinheiro bom por um peso de papel radioativo. Essa porcaria não faz absolutamente NADA além de drenar a bateria e interferir no rádio."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 4:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Neutral/Grumpy
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Eu já arranquei fora e joguei no lixo, onde é o lugar dessa 'tecnologia avançada'. Vê se aprende: se não tem pistão, não presta. Agora me paga pelo serviço de 'remoção de burrice'."
            self._iniciar_animacao_texto(texto_completo)
        
        else:
            self._finalizar_dialogo_alien()
    
    def _avancar_dialogo_alien_melhoria(self):
        """Avança o diálogo sobre melhoria boa do mercador alien"""
        if self.dialogo_alien_parte == 0:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Pointing/Lecturing (confuso)
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            texto_completo = "Ei. Vem cá. Me explica uma coisa."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 1:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Pointing/Lecturing
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            texto_completo = "Eu tô olhando pra esse... 'Módulo de Propulsão' que você instalou. Não tem entrada de combustível. Não tem escape. Não tem peças móveis. É só um cubo de gelo azul que zumbe."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 2:
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo  # Angry (frustração técnica)
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_normal if self.sprite_normal else None
            texto_completo = "Pelos manuais, isso não deveria funcionar! Isso viola três leis da termodinâmica e meia dúzia de regras de bom senso mecânico!"
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 3:
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_normal if self.sprite_normal else None
            texto_completo = "Mas... eu coloquei no dinamômetro. E o maldito cubo de gelo aumentou a cavalaria em 30%. Sem esquentar o motor."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 4:
            # Parte 5: "Eu não gosto disso..."
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Neutral/Grumpy, olhando para o lado
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Eu não gosto disso. É antinatural. É trapaça. Não é mecânica de verdade, é feitiçaria espacial."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 5:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Neutral/Grumpy
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Mas se faz você ganhar corridas e trazer meu dinheiro... (Suspira). Tá bom. Fica com essa aberração no carro. Mas se começar a nascer tentáculo no carburador, a culpa é sua."
            self._iniciar_animacao_texto(texto_completo)
        
        else:
            self.fechar()
    
    def _avancar_dialogo_alien_multimelhoria(self):
        """Avança o diálogo sobre multimelhoria do mercador alien"""
        if self.dialogo_alien_parte == 0:
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo  # Serious/Angry
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_normal if self.sprite_normal else None
            texto_completo = "..."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 1:
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo  # Serious/Angry
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_normal if self.sprite_normal else None
            texto_completo = "Eu abri o capô hoje de manhã. Eu não reconheci o motor que EU montei."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 2:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Pointing/Lecturing, gesticulando
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Fios de neon por todo lado. Injetores de plasma onde deviam estar as velas. O tanque de gasolina agora brilha no escuro. O que você fez com a minha máquina, seu maníaco?!"
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 3:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Pointing/Lecturing
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Você entregou a alma desse carro pra aquele ET trambiqueiro! Isso não é mais um veículo terrestre, é uma nave espacial de segunda mão!"
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 4:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Smug/Dismissive (amargo/triste)
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Olha, se você prefere confiar em tecnologia que pisca do que no bom e velho aço forjado e graxa... o problema é seu."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.dialogo_alien_parte == 5:
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal  # Neutral/Grumpy, batendo o pé
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            texto_completo = "Mas a minha chave de boca não encaixa nessas porcas alienígenas. Se essa traquitana quebrar lá na pista, não vem chorar pra mim, porque eu não sei consertar disco voador. Se vira."
            self._iniciar_animacao_texto(texto_completo)
        
        else:
            self._finalizar_dialogo_alien()
    
    def mostrar_tutorial(self):
        """Mostra o tutorial da primeira aparição do Crank na oficina"""
        if self.tutorial_mostrado:
            return False
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.ativo = True
        self.fase_dialogo = "tutorial"
        self.tutorial_parte = 0  # Começar com apresentação
        self.tutorial_fase_apresentacao = "sombra"  # Começar com sombra
        
        # Usar sprite normal como base para a sombra (será escurecido no desenho)
        if self.sprite_normal:
            self.sprite_atual = self.sprite_normal
        else:
            self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
        
        # Texto inicial: resmungo (sombra)
        texto_completo = "*resmunga* ... Onde está aquele imprestável? ... *resmunga*"
        self._iniciar_animacao_texto(texto_completo)
        
        return True
    
    def mostrar_tutorial_upgrades(self):
        """Mostra o tutorial da primeira vez que o jogador entra na tela de upgrades"""
        if self.tutorial_upgrades_mostrado:
            return False
        
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.ativo = True
        self.fase_dialogo = "tutorial_upgrades"
        self.tutorial_upgrades_parte = 0
        
        # Usar sprite normal/estressado (braços cruzados, impaciente) para começar
        if self.sprite_normal:
            self.sprite_atual = self.sprite_normal
        elif self.sprite_estressado:
            self.sprite_atual = self.sprite_estressado
        else:
            self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
        
        texto_completo = "Hmph. Finalmente parou de admirar a lataria e veio aonde a mágica acontece. Tava demorando."
        self._iniciar_animacao_texto(texto_completo)
        
        return True
    
    def pode_comprar_upgrade(self, tipo_upgrade):
        """
        Verifica se o jogador pode comprar um upgrade
        Retorna (pode_comprar, motivo_bloqueio)
        Se saúde < 20%, bloqueia a compra
        """
        if self.saude_carro < 0.2:
            return (False, "dano_critico")
        return (True, None)
    
    def bloquear_upgrade_dano_critico(self, tipo_upgrade):
        """
        Bloqueia a compra de upgrade por dano crítico
        Ativa o diálogo do Crank explicando o bloqueio
        """
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.ativo = True
        self.fase_dialogo = "dano_critico"
        
        # Texto específico para bloqueio de upgrade
        nome_upgrade = tipo_upgrade.replace('_', ' ').title()
        saude_percent = int(self.saude_carro * 100)
        
        if self.sprite_bravo:
            self.sprite_atual = self.sprite_bravo
        elif self.sprite_surpreso:
            self.sprite_atual = self.sprite_surpreso
        else:
            self.sprite_atual = self.sprite_normal
        
        texto_completo = f"Você tá maluco? Botar um {nome_upgrade} nessa sucata fumegante? " \
                        f"O carro tá com apenas {saude_percent}% de saúde! " \
                        "Conserta primeiro, depois a gente conversa sobre potência. " \
                        "Nem pense em comprar upgrades enquanto o carro estiver nesse estado!"
        self._iniciar_animacao_texto(texto_completo)
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.texto_atual = ""  # Garantir que texto_atual também começa vazio
        self.tempo_animacao = 0.0
        
        if not getattr(self, 'nome_revelado', False):
            texto_lower = texto.lower()
            if ("crank" in texto_lower or 
                "eu sou" in texto_lower or 
                "meu nome" in texto_lower or
                "pode me chamar de crank" in texto_lower or
                "me chamo crank" in texto_lower):
                self.nome_revelado = True
                self.salvar_estado()
                print(f"✓ Nome do Crank revelado: {texto[:50]}...")
    
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
                max_por_frame = max(1, int(self.velocidade_texto * dt * 5))  # Permitir até 5x a velocidade normal por frame (aumentado para reduzir lag)
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
    
    def _definir_sprite_e_texto_veredito(self):
        """Define sprite e texto baseado no veredito da corrida"""
        # Garantir que o texto comece vazio antes de iniciar a animação
        self.texto_atual = ""
        self.texto_exibido = ""
        self.texto_completo = ""
        self.tempo_animacao = 0.0
        
        colisoes = self.ultima_corrida['colisoes']
        venceu = self.ultima_corrida['venceu']
        
        if venceu and colisoes == 0:
            # Venceu sem colisões - feliz (não precisa resposta)
            if self.sprite_alegre:
                self.sprite_atual = self.sprite_alegre
            else:
                self.sprite_atual = self.sprite_normal
            texto_completo = "Hmph. Não quebrou nada dessa vez. Milagre. O carro tá pronto pra próxima."
            self._iniciar_animacao_texto(texto_completo)
            self.precisa_resposta = False
        elif venceu and colisoes < 3:
            # Venceu com poucas colisões - normal/feliz (não precisa resposta)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_alegre
            texto_completo = "Bom trabalho. Ganhou, mas podia ter cuidado mais com o carro. Tá tudo certo."
            self._iniciar_animacao_texto(texto_completo)
            self.precisa_resposta = False
        elif colisoes == 0:
            # Sem colisões mas perdeu - normal (não precisa resposta)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                # Fallback se sprite_normal não existir
                self.sprite_atual = self.sprite_alegre if self.sprite_alegre else None
            texto_completo = "Corrida limpa, mas não ganhou. Próxima vez você consegue. O carro tá ok."
            self._iniciar_animacao_texto(texto_completo)
            self.precisa_resposta = False
        elif colisoes >= 5:
            # Muitas colisões - muito bravo (mesmo se venceu - "Venceu Feio")
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            else:
                self.sprite_atual = self.sprite_normal
            
            # Escolher fala aleatória de muito bravo
            falas = self._obter_falas_muito_bravo()
            if venceu:
                # Adicionar fala específica de "venceu feio"
                falas.append(f"Você chegou em primeiro? Grande coisa! Olha o estado dessa suspensão! "
                            f"{colisoes} colisões! O prêmio não paga nem a tinta que você raspou! Isso vai custar caro, amigo!")
            
            texto_completo = random.choice(falas)
            self._iniciar_animacao_texto(texto_completo)
            self.precisa_resposta = True
        elif colisoes >= 3:
            # Algumas colisões - bravo (PRECISA RESPOSTA)
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            else:
                self.sprite_atual = self.sprite_normal
            
            # Escolher fala aleatória de bravo
            falas = self._obter_falas_bravo()
            texto_completo = random.choice(falas)
            self._iniciar_animacao_texto(texto_completo)
            self.precisa_resposta = True
        else:
            # Poucas colisões mas perdeu - normal/bravo (não precisa resposta)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            texto_completo = "Algumas batidas aí, mas nada demais. Toma mais cuidado da próxima vez."
            self._iniciar_animacao_texto(texto_completo)
            self.precisa_resposta = False
    
    def _definir_sprite_e_texto_dano_critico(self):
        """Define sprite e texto para dano crítico"""
        if self.sprite_bravo:
            self.sprite_atual = self.sprite_bravo
        elif self.sprite_surpreso:
            self.sprite_atual = self.sprite_surpreso
        else:
            self.sprite_atual = self.sprite_normal
        
        saude_percent = int(self.saude_carro * 100)
        texto_completo = f"Nem pense em voltar pra pista com essa banheira fumegante! " \
                        f"O carro tá com apenas {saude_percent}% de saúde! " \
                        "Vai explodir na primeira curva. Conserta isso AGORA ou não vou deixar você correr!"
        self._iniciar_animacao_texto(texto_completo)
        # Marcar que precisa resposta (reparar ou desistir)
        self.precisa_resposta = True
        self.opcao_confirmacao_selecionada = 0  # 0 = reparar, 1 = desistir
    
    def _avancar_tutorial(self):
        """Avança para a próxima parte do tutorial"""
        self.tutorial_parte += 1
        
        if self.tutorial_parte == 0:  # Apresentação - sombra
            # Já está na fase de sombra, não precisa fazer nada aqui
            pass
        elif self.tutorial_parte == 1:  # Apresentação - dúvida
            self.tutorial_fase_apresentacao = "duvida"
            if self.sprite_duvida:
                self.sprite_atual = self.sprite_duvida
            elif self.sprite_surpreso:
                self.sprite_atual = self.sprite_surpreso
            else:
                self.sprite_atual = self.sprite_normal
            
            texto_completo = "Hmm? Quem é você? Você não é o ajudante que eu contratei. " \
                            "Cadê aquele imprestável?"
            self._iniciar_animacao_texto(texto_completo)
        elif self.tutorial_parte == 2:  # Perguntar nome
            self.tutorial_fase_apresentacao = "perguntar_nome"
            if self.sprite_duvida:
                self.sprite_atual = self.sprite_duvida
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_surpreso if self.sprite_surpreso else None
            
            if gerenciador_progresso.nome_jogador != "JOGADOR":
                self.tutorial_parte = 3
                self._avancar_tutorial()
                return
            
            texto_completo = "Qual o seu nome?"
            self._iniciar_animacao_texto(texto_completo)
            self.input_nome_ativo = True
            self.nome_input = ""
        elif self.tutorial_parte == 3:  # Tutorial normal - parte 1 (após nome, usa convencido)
            self.tutorial_fase_apresentacao = "tutorial"
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            
            texto_completo = "Ah, espera. Você é o 'piloto prodígio' que a organização mandou, né? " \
                            "O novato que vai dirigir essa lata velha. Muito prazer. Pode me chamar de Crank. " \
                            "Eu sou o dono, o gerente, o mecânico chefe e o único ser vivo nessa garagem que sabe " \
                            "a diferença entre um pistão e uma panela de pressão."
            self._iniciar_animacao_texto(texto_completo)
        elif self.tutorial_parte == 4:  # Tutorial normal - parte 2 (usa incrédulo)
            if self.sprite_incredulo:
                self.sprite_atual = self.sprite_incredulo
            elif self.sprite_surpreso:
                self.sprite_atual = self.sprite_surpreso
            else:
                self.sprite_atual = self.sprite_normal if self.sprite_normal else None
            
            texto_completo = "Olha pra isso. Suspensão mole, pneus carecas, motor asmático... " \
                            "É um milagre isso ter terminado a primeira corrida. Mas... tem potencial. O chassi é bom."
            self._iniciar_animacao_texto(texto_completo)
        elif self.tutorial_parte == 5:  # Tutorial normal - parte 3 (volta para convencido)
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_bravo if self.sprite_bravo else None
            
            texto_completo = "Escuta aqui, novato. O trato é o seguinte: Você ganha as corridas e traz o dinheiro. " \
                            "Eu pego o dinheiro e transformo essa carroça num foguete. Simples. " \
                            "Mas tem uma regra sagrada na minha oficina: RESPEITE A MÁQUINA. " \
                            "Se você trouxer meu carro de volta parecendo uma lata de sardinha amassada, " \
                            "eu vou ficar muito bravo. E quando eu fico bravo, minhas peças ficam caras. Entendeu?"
            self._iniciar_animacao_texto(texto_completo)
        else:  # Parte 5 ou mais - finalizar
            self.tutorial_mostrado = True
            self.salvar_estado()
            self.fechar()
    
    def _avancar_tutorial_upgrades(self):
        """Avança para a próxima parte do tutorial de upgrades"""
        self.tutorial_upgrades_parte += 1
        
        if self.tutorial_upgrades_parte == 1:  # Parte 1 - Presta atenção
            # Sprite normal/estressado (braços cruzados, impaciente)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "Presta atenção, piloto, porque eu não vou repetir. Esta é a minha mesa de cirurgia. " \
                            "É aqui que a gente pega essa... 'coisa' manca que você chama de carro e tenta transformar " \
                            "em algo que não passe vergonha na pista."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 2:  # Parte 2 - O esquema é simples (apontando)
            # Sprite convencido (explicando/apontando)
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            
            texto_completo = "O esquema é simples, até você deve entender: Motor dá velocidade. " \
                            "Pneus seguram você na curva. Suspensão impede que seus dentes caiam nos buracos."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 3:  # Parte 3 - Mas tem um detalhezinho
            # Continua com sprite convencido
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            
            texto_completo = "Mas tem um detalhezinho importante..."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 4:  # Parte 4 - Potência custa caro (braços cruzados)
            # Volta para sprite normal/estressado (braços cruzados, sério)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "...Potência custa caro. Eu não trabalho de graça e peças de alta performance não caem do céu."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 5:  # Parte 5 - Você ganha as corridas
            # Usa sprite convencido
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            
            texto_completo = "Você ganha as corridas, traz os créditos, e eu faço o trabalho sujo. " \
                            "Se você não tiver dinheiro, nem perca meu tempo olhando o catálogo. Eu odeio vitrine."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 6:  # Parte 6 - Conselho de profissional
            # Continua com sprite normal/estressado
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "E um conselho de profissional: não adianta botar um motor V12 se você ainda usa freios de bicicleta. " \
                            "Tenta usar a cabeça... se é que tem algo aí dentro."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 7:  # Parte 7 - Dica de bastidores (smug/dismissive)
            # Sprite convencido ou normal (smug/dismissive)
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            
            texto_completo = "Ah, e uma última dica de bastidores, novato. Sobre a sucata que a gente vai arrancar desse carro..."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 8:  # Parte 8 - Não tenha pressa (neutra/braços cruzados)
            # Sprite normal/estressado (braços cruzados, olhando para o lado)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "Não tenha pressa em jogar no lixo. Tem uma... *coisa*... que aparece na garagem às vezes quando tá tudo quieto."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 9:  # Parte 9 - Não me pergunte o que é
            # Continua com sprite normal/estressado
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "Não me pergunte o que é aquilo. Parece uma gelatina que aprendeu a voar e engoliu uma lanterna. Bicho esquisito, nunca vi nada igual no ferro-velho."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 10:  # Parte 10 - Mas por algum motivo
            # Continua com sprite normal/estressado
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "Mas por algum motivo que escapa à minha compreensão mecânica, a criatura *adora* ferrugem e peças velhas. Chega a babar óleo."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 11:  # Parte 11 - Se você der de cara (smug/dismissive)
            # Sprite convencido ou normal (smug/dismissive, sorriso malandro)
            if self.sprite_convencido:
                self.sprite_atual = self.sprite_convencido
            elif self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            else:
                self.sprite_atual = self.sprite_estressado if self.sprite_estressado else None
            
            texto_completo = "Se você der de cara com essa assombração brilhante... tenta oferecer suas peças velhas antes de sair correndo. " \
                            "Dizem que ele paga bem pelo que não vale nada. Vai entender..."
            self._iniciar_animacao_texto(texto_completo)
        
        elif self.tutorial_upgrades_parte == 12:  # Parte 12 - Enfim, chega de papo (neutra/braços cruzados, impaciente)
            # Sprite normal/estressado (braços cruzados, bate o pé impaciente)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                self.sprite_atual = self.sprite_convencido if self.sprite_convencido else None
            
            texto_completo = "Enfim. Chega de papo furado sobre monstros de graxa. Minha chave de catraca tá esfriando. Escolhe logo o que vamos melhorar."
            self._iniciar_animacao_texto(texto_completo)
        
        else:  # Parte 13 ou mais - finalizar
            self.tutorial_upgrades_mostrado = True
            self.salvar_estado()
            self.fechar()
    
    def mostrar_confirmacao_upgrade(self, tipo_upgrade, preco, nivel, prefixo_cor):
        """Mostra diálogo de confirmação para compra de upgrade (sem sprite, apenas caixa simples)"""
        self.ativo = True
        self.fase_dialogo = "confirmar_upgrade"
        self.upgrade_pendente = {
            'tipo': tipo_upgrade,
            'preco': preco,
            'nivel': nivel,
            'prefixo_cor': prefixo_cor
        }
        self.confirmacao_resposta = None
        self.sprite_atual = None  # Não usar sprite na confirmação
        self.opcao_confirmacao_selecionada = 0  # Inicializar opção selecionada
        
        return True
    
    def _desenhar_confirmacao_upgrade_simples(self, tela, dt):
        """Desenha caixa de confirmação idêntica ao estilo do Boris"""
        render_text = _get_render_text()
        from core.i18n import t
        
        # Obter informações do upgrade pendente
        if not hasattr(self, 'upgrade_pendente') or self.upgrade_pendente is None:
            return
        
        tipo_upgrade = self.upgrade_pendente.get('tipo', '')
        preco = self.upgrade_pendente.get('preco', 0)
        nivel = self.upgrade_pendente.get('nivel', 0)
        
        # Nome do upgrade traduzido
        nome_upgrade = t(f"menu.upgrades.{tipo_upgrade}")
        
        # Inicializar opção selecionada se não existir
        if not hasattr(self, 'opcao_confirmacao_selecionada'):
            self.opcao_confirmacao_selecionada = 0
        
        # Desenhar caixa de confirmação (idêntica ao Boris)
        caixa_largura = 500
        caixa_altura = 180
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 260
        
        overlay = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        tela.blit(overlay, (caixa_x, caixa_y))
        pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 2)
        
        titulo = render_text("CONFIRMAÇÃO DE COMPRA", 22, (255, 255, 0), bold=True, pixel_style=True)
        tela.blit(titulo, (caixa_x + (caixa_largura - titulo.get_width()) // 2, caixa_y + 10))
        
        desc = render_text(f"{nome_upgrade.upper()} nível {nivel + 1}", 18, (220, 220, 220), bold=False, pixel_style=True)
        preco_txt = render_text(f"Preço: ${preco:,}", 18, (180, 255, 180), bold=False, pixel_style=True)
        tela.blit(desc, (caixa_x + 20, caixa_y + 45))
        tela.blit(preco_txt, (caixa_x + 20, caixa_y + 70))
        
        # Opções (idênticas ao Boris)
        opcoes = ["COMPRAR PEÇA", "SAIR"]
        for i, texto_opcao in enumerate(opcoes):
            cor = (0, 200, 255) if i == self.opcao_confirmacao_selecionada else (200, 200, 200)
            txt = render_text(texto_opcao, 20, cor, bold=True, pixel_style=True)
            y = caixa_y + 105 + i * 30
            tela.blit(txt, (caixa_x + 40, y))
    
    def calcular_preco_com_humor(self, preco_base):
        """Calcula o preço final baseado no humor do Crank"""
        multiplicador = self.MULTIPLICADORES_PRECO.get(self.humor_atual, 1.0)
        return int(preco_base * multiplicador)
    
    def reparar_carro(self, custo):
        """Repara o carro (restaura saúde)"""
        if gerenciador_progresso.tem_dinheiro(custo):
            gerenciador_progresso.remover_dinheiro(custo)
            # Restaurar 50% da saúde por reparo
            self.saude_carro = min(1.0, self.saude_carro + 0.5)
            self.salvar_estado()
            return True
        return False
    
    def _obter_falas_bravo(self):
        """Retorna lista de falas quando está Bravo (+25%)"""
        return [
            "Você sabe que o pedal do meio serve pra frear, né? Tenta usar na próxima vez, só pra variar.",
            "Olha esse para-choque... Eu passei horas alinhando isso ontem. Você acha que meu tempo é brincadeira?",
            "Hmph. Trouxe mais trabalho pra mim. Pelo menos o motor ainda tá no lugar. Por enquanto. Mas a conta da funilaria vai ser salgada.",
            "Você tava disputando corrida ou brincando de carrinho de bate-bate? Porque pareceu a segunda opção.",
            "A boa notícia é que o chassi não entortou. A má notícia é que eu vou ter que cobrar extra pra tirar essa tinta de outro carro da sua porta."
        ]
    
    def _obter_falas_muito_bravo(self):
        """Retorna lista de falas quando está Muito Bravo (+50%)"""
        return [
            "MAS O QUE É ISSO?! Você tava dirigindo de olhos fechados?! Olha o estado dessa lataria! É perda total!",
            "NÃO! Nem vem! Eu devia cobrar taxa de periculosidade só pra chegar perto dessa sucata fumegante. Você tem ideia do custo dessas peças?!",
            "É inacreditável! Eu construo uma máquina de precisão e você trata como lixo! A conta de hoje vai doer, piloto. Vai doer muito.",
            "Sai da frente! Sai da frente antes que eu perca a cabeça! Eu não acredito que você sobreviveu a isso. O carro certamente não sobreviveu.",
            "Escuta aqui: se você fizer isso de novo, eu me demito. Eu volto pro lixão. Lá pelo menos a sucata não me decepciona. Argh! Vai custar uma fortuna pra arrumar isso."
        ]
    
    def obter_opcoes_resposta(self):
        """Retorna as opções de resposta quando o Crank está bravo"""
        return [
            "Foi mal, Crank. Errei a freada. Assumo a culpa.",
            "Ah, relaxa. É só um amassadinho. Eu ganhei dinheiro suficiente pra pagar.",
            "A culpa não foi minha! Os freios não responderam quando eu pisei!"
        ]
    
    def processar_resposta(self, opcao):
        """Processa a resposta escolhida pelo jogador e atualiza o humor"""
        humor_anterior = self.humor_atual
        
        # Opção 0: A Humilde (Mitiga o dano)
        # Opção 1: A Arrogante/Despreocupada (Piora o dano)
        # Opção 2: Culpar o Carro (A Pior Opção)
        
        if opcao == 0:
            # Desculpa sincera - melhora humor
            if self.humor_atual == self.HUMOR_BRAVO:
                self.humor_atual = self.HUMOR_NORMAL
                self.mudanca_preco = -1  # Diminuiu
            elif self.humor_atual == self.HUMOR_MUITO_BRAVO:
                self.humor_atual = self.HUMOR_BRAVO
                self.mudanca_preco = -1  # Diminuiu
            else:
                self.mudanca_preco = 0  # Manteve
            
            texto_completo = "Tsc. Pelo menos assume o erro. Menos mal. Tá, eu vou dar um jeito sem cobrar a taxa de 'dor de cabeça'."
            self._iniciar_animacao_texto(texto_completo)
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
        elif opcao == 1:
            # Relativiza - piora humor
            if self.humor_atual == self.HUMOR_BRAVO:
                self.humor_atual = self.HUMOR_MUITO_BRAVO
                self.mudanca_preco = 1  # Aumentou
            else:
                self.mudanca_preco = 0  # Manteve (já estava no máximo)
            
            texto_completo = "Relaxa? RELAXA? Você acha que meu trabalho é piada só porque você tem uns trocados no bolso? " \
                            "Beleza, 'chefe'. Vamos ver se você paga essa aqui então."
            self._iniciar_animacao_texto(texto_completo)
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
        else:  # opcao == 2
            # Culpar o carro - piora MUITO
            self.humor_atual = self.HUMOR_MUITO_BRAVO
            self.mudanca_preco = 1  # Aumentou muito
            
            texto_completo = "O QUÊ?! Você ousa culpar a MINHA regulagem pela sua barbeiragem?! " \
                            "Agora você insultou o mestre. Sai daqui enquanto eu calculo a nova taxa de 'insulto ao mecânico'."
            self._iniciar_animacao_texto(texto_completo)
            if self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
        
        self.salvar_estado()
        self.fase_dialogo = "reacao"
    
    def processar_eventos(self, eventos):
        """Processa eventos de entrada do jogador"""
        if not self.ativo:
            return None
        
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if self.fase_dialogo == "veredito":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste pressionamento
                    elif self.precisa_resposta:
                        # Avançar para fase de resposta
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.fase_dialogo = "resposta"
                            self.opcao_selecionada = 0
                    else:
                        # Não precisa resposta, pode fechar
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            self.fechar()
                            return "fechado"
                
                elif self.fase_dialogo == "resposta":
                    if len(self.texto_exibido) >= len(self.texto_completo):
                        # Navegar entre opções
                        if ev.key in (pygame.K_UP, pygame.K_w):
                            self.opcao_selecionada = (self.opcao_selecionada - 1) % 3
                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                            self.opcao_selecionada = (self.opcao_selecionada + 1) % 3
                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Confirmar resposta
                            self.processar_resposta(self.opcao_selecionada)
                    elif ev.key == pygame.K_ESCAPE:
                        # Cancelar e fechar
                        self.fechar()
                        return "fechado"
                
                elif self.fase_dialogo == "reacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste pressionamento
                    else:
                        # Fechar após ver reação
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            self.fechar()
                            return "fechado"
                
                elif self.fase_dialogo == "reacao_instalacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste pressionamento
                    else:
                        # Fechar após ver reação
                        if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            self.fechar()
                            return "fechado"
                
                elif self.fase_dialogo == "dano_critico":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste pressionamento
                    else:
                        # Navegar entre opções ou confirmar/cancelar
                        from core.i18n import t
                        opcoes = [t("menu.reparar"), t("menu.desistir")]
                        
                        if not hasattr(self, 'opcao_confirmacao_selecionada'):
                            self.opcao_confirmacao_selecionada = 0
                        
                        if ev.key in (pygame.K_UP, pygame.K_w):
                            self.opcao_confirmacao_selecionada = (self.opcao_confirmacao_selecionada - 1) % len(opcoes)
                        elif ev.key in (pygame.K_DOWN, pygame.K_s):
                            self.opcao_confirmacao_selecionada = (self.opcao_confirmacao_selecionada + 1) % len(opcoes)
                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Confirmar seleção
                            if self.opcao_confirmacao_selecionada == 0:  # Reparar
                                # Calcular custo de reparo (baseado na saúde atual)
                                custo_reparo = int((1.0 - self.saude_carro) * 2000)  # Custo proporcional ao dano
                                if self.reparar_carro(custo_reparo):
                                    self.fechar()
                                    return "reparado"
                                else:
                                    # Não tem dinheiro suficiente
                                    return "sem_dinheiro"
                            else:  # Desistir
                                self.fechar()
                                return "desistido"
                        elif ev.key == pygame.K_ESCAPE:
                            # Cancelar (tratado como desistir)
                            self.fechar()
                            return "desistido"
                
                elif self.fase_dialogo == "tutorial":
                    # Se está na fase de input de nome
                    if self.input_nome_ativo:
                        if ev.key == pygame.K_RETURN:
                            # Confirmar nome
                            if self.nome_input.strip():
                                nome_final = self.nome_input.strip().upper()[:15]  # Limitar a 15 caracteres
                                if nome_final:
                                    gerenciador_progresso.nome_jogador = nome_final
                                    gerenciador_progresso.salvar()
                                    self.input_nome_ativo = False
                                    self.tutorial_parte = 3
                                    self._avancar_tutorial()
                            else:
                                # Nome vazio, usar padrão
                                gerenciador_progresso.nome_jogador = "JOGADOR"
                                gerenciador_progresso.salvar()
                                self.input_nome_ativo = False
                                self.tutorial_parte = 3
                                self._avancar_tutorial()
                        elif ev.key == pygame.K_BACKSPACE:
                            # Apagar caractere
                            if self.nome_input:
                                self.nome_input = self.nome_input[:-1]
                        elif ev.unicode and len(self.nome_input) < 15:
                            # Adicionar caractere (apenas letras, números e alguns caracteres especiais)
                            char = ev.unicode.upper()
                            if char.isalnum() or char in ['_', '-', ' ']:
                                self.nome_input += char
                    else:
                        if len(self.texto_exibido) < len(self.texto_completo):
                            self._completar_animacao_texto()
                            # Não fazer mais nada neste pressionamento
                        elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # Avançar tutorial
                            self._avancar_tutorial()
                        elif ev.key == pygame.K_ESCAPE:
                            self.tutorial_mostrado = True
                            self.salvar_estado()
                            self.fechar()
                            return "fechado"
                
                elif self.fase_dialogo == "tutorial_upgrades":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste pressionamento
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Avançar tutorial de upgrades
                        self._avancar_tutorial_upgrades()
                    elif ev.key == pygame.K_ESCAPE:
                        self.tutorial_upgrades_mostrado = True
                        self.salvar_estado()
                        self.fechar()
                        return "fechado"
                
                elif self.fase_dialogo == "dialogo_alien":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                        # Não fazer mais nada neste pressionamento
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Espaço/Enter avança o diálogo alien
                        self.dialogo_alien_parte += 1
                        self._avancar_dialogo_alien()
                        return "processado"
                    elif ev.key == pygame.K_ESCAPE:
                        # ESC fecha o diálogo e marca como já mostrado
                        self._finalizar_dialogo_alien()
                        return "processado"
                
                elif self.fase_dialogo == "confirmar_upgrade":
                    # Navegar entre opções ou confirmar/cancelar (estilo Boris)
                    opcoes = ["COMPRAR PEÇA", "SAIR"]
                    
                    if not hasattr(self, 'opcao_confirmacao_selecionada'):
                        self.opcao_confirmacao_selecionada = 0
                    
                    if ev.key in (pygame.K_UP, pygame.K_w):
                        self.opcao_confirmacao_selecionada = (self.opcao_confirmacao_selecionada - 1) % len(opcoes)
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        self.opcao_confirmacao_selecionada = (self.opcao_confirmacao_selecionada + 1) % len(opcoes)
                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # Confirmar seleção
                        if self.opcao_confirmacao_selecionada == 0:  # COMPRAR PEÇA
                            self.confirmacao_resposta = True
                            self.fechar()
                            return "confirmado"
                        else:  # SAIR
                            self.confirmacao_resposta = False
                            self.upgrade_pendente = None
                            self.fechar()
                            return "cancelado"
                    elif ev.key == pygame.K_ESCAPE:
                        # Cancelar upgrade
                        self.confirmacao_resposta = False
                        self.upgrade_pendente = None
                        self.fechar()
                        return "cancelado"
            
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                caixa_altura = int(ALTURA * 0.28)
                caixa_y = ALTURA - caixa_altura - 20
                botao_largura = 180
                botao_altura = 38
                
                if self.fase_dialogo == "veredito":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        # Texto completo, agora pode avançar
                        if self.precisa_resposta:
                            # Clicar em qualquer lugar avança para resposta
                            caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                            if caixa_rect.collidepoint(mouse_x, mouse_y):
                                self.fase_dialogo = "resposta"
                                self.opcao_selecionada = 0
                        else:
                            # Botão Fechar ou clicar na caixa fecha
                            fechar_x = LARGURA - botao_largura - 30
                            fechar_y = caixa_y + caixa_altura - 50
                            fechar_rect = pygame.Rect(fechar_x, fechar_y, botao_largura, botao_altura)
                            if fechar_rect.collidepoint(mouse_x, mouse_y):
                                self.fechar()
                                return "fechado"
                            # Ou clicar em qualquer lugar fecha
                            caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                            if caixa_rect.collidepoint(mouse_x, mouse_y):
                                self.fechar()
                                return "fechado"
                
                elif self.fase_dialogo == "resposta":
                    # Só processar clique se o texto estiver completo
                    if len(self.texto_exibido) >= len(self.texto_completo):
                        render_text = _get_render_text()
                        opcoes = self.obter_opcoes_resposta()
                        botao_largura_opcao = int(LARGURA * 0.45)  # Reduzido de 60% para 45%
                        botao_x_opcao = (LARGURA - botao_largura_opcao) // 2
                        espacamento_opcao = 25
                        
                        # Calcular posição Y (mesma lógica do desenho)
                        altura_total = 0
                        for opcao_texto in opcoes:
                            palavras_opcao = opcao_texto.split()
                            linhas_opcao = []
                            linha_opcao = ""
                            for palavra in palavras_opcao:
                                teste = linha_opcao + (" " if linha_opcao else "") + palavra
                                texto_teste = render_text(teste, 24, (255, 255, 255), bold=False, pixel_style=False)
                                if texto_teste.get_width() <= botao_largura_opcao - 60:  # Margem maior para texto menor
                                    linha_opcao = teste
                                else:
                                    if linha_opcao:
                                        linhas_opcao.append(linha_opcao)
                                    linha_opcao = palavra
                            if linha_opcao:
                                linhas_opcao.append(linha_opcao)
                            altura_total += len(linhas_opcao) * 28 + 35
                        
                        inicio_y_opcao = (ALTURA - altura_total) // 2
                        
                        # Calcular todas as hitboxes de forma consistente
                        hitboxes = []
                        y_calc = inicio_y_opcao
                        for opcao_texto in opcoes:
                            palavras_opcao = opcao_texto.split()
                            linhas_opcao = []
                            linha_opcao = ""
                            for palavra in palavras_opcao:
                                teste = linha_opcao + (" " if linha_opcao else "") + palavra
                                texto_teste = render_text(teste, 24, (255, 255, 255), bold=False, pixel_style=False)
                                if texto_teste.get_width() <= botao_largura_opcao - 60:  # Margem maior para texto menor
                                    linha_opcao = teste
                                else:
                                    if linha_opcao:
                                        linhas_opcao.append(linha_opcao)
                                    linha_opcao = palavra
                            if linha_opcao:
                                linhas_opcao.append(linha_opcao)
                            
                            texto_y_calc = y_calc
                            linha_y_calc = texto_y_calc + (len(linhas_opcao) * 28) + 5
                            altura_opcao = linha_y_calc - texto_y_calc + 10
                            hitboxes.append(pygame.Rect(botao_x_opcao, texto_y_calc, botao_largura_opcao, altura_opcao))
                            y_calc = linha_y_calc + espacamento_opcao
                        
                        for i, rect in enumerate(hitboxes):
                            if rect.collidepoint(mouse_x, mouse_y):
                                self.opcao_selecionada = i
                                self.processar_resposta(i)
                                break
                
                elif self.fase_dialogo == "reacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        # Clicar em qualquer lugar fecha
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fechar()
                            return "fechado"
                
                elif self.fase_dialogo == "reacao_instalacao":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        # Clicar em qualquer lugar fecha
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.fechar()
                            return "fechado"
                
                elif self.fase_dialogo == "dano_critico":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        from core.i18n import t
                        opcoes = [t("menu.reparar"), t("menu.desistir")]
                        espacamento = 25
                        botao_largura = int(LARGURA * 0.45)
                        botao_x = (LARGURA - botao_largura) // 2
                        altura_total = len(opcoes) * 40 + (len(opcoes) - 1) * espacamento
                        inicio_y = (ALTURA - altura_total) // 2
                        
                        # Calcular hitboxes
                        hitboxes = []
                        y_calc = inicio_y
                        for opcao_nome in opcoes:
                            render_text = _get_render_text()
                            texto_opcao_temp = render_text(opcao_nome, 24, (255, 255, 255), bold=False, pixel_style=False)
                            texto_y_calc = y_calc
                            linha_y_calc = texto_y_calc + texto_opcao_temp.get_height() + 5
                            altura_opcao = linha_y_calc - texto_y_calc + 10
                            hitboxes.append(pygame.Rect(botao_x, texto_y_calc, botao_largura, altura_opcao))
                            y_calc = linha_y_calc + espacamento
                        
                        # Verificar qual botão foi clicado
                        for i, rect in enumerate(hitboxes):
                            if rect.collidepoint(mouse_x, mouse_y):
                                if i == 0:  # Reparar
                                    custo_reparo = int((1.0 - self.saude_carro) * 2000)
                                    if self.reparar_carro(custo_reparo):
                                        self.fechar()
                                        return "reparado"
                                    else:
                                        return "sem_dinheiro"
                                else:  # Desistir
                                    self.fechar()
                                    return "desistido"
                
                elif self.fase_dialogo == "tutorial":
                    # Se está na fase de input de nome, NÃO permitir avançar com clique
                    if self.input_nome_ativo:
                        return "processado"  # Marcar que o evento foi processado (bloqueado)
                    
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        # Clicar em qualquer lugar da caixa avança o tutorial
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self._avancar_tutorial()
                            return "processado"  # Marcar que o evento foi processado
                
                elif self.fase_dialogo == "tutorial_upgrades":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        # Clicar em qualquer lugar da caixa avança o tutorial de upgrades
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self._avancar_tutorial_upgrades()
                            return "processado"  # Marcar que o evento foi processado
                
                elif self.fase_dialogo == "dialogo_alien":
                    if len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        # Clicar em qualquer lugar da caixa avança o diálogo alien
                        caixa_rect = pygame.Rect(0, caixa_y, LARGURA, caixa_altura)
                        if caixa_rect.collidepoint(mouse_x, mouse_y):
                            self.dialogo_alien_parte += 1
                            self._avancar_dialogo_alien()
                            return "processado"  # Marcar que o evento foi processado
                
                elif self.fase_dialogo == "confirmar_upgrade":
                    # Calcular retângulos dos botões (idêntico ao Boris)
                    if not hasattr(self, 'upgrade_pendente') or self.upgrade_pendente is None:
                        return None
                    
                    caixa_largura = 500
                    caixa_altura = 180
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = ALTURA - caixa_altura - 260
                    botao_y_base = caixa_y + 105
                    botao_altura = 30
                    
                    # Botão 0 = COMPRAR PEÇA
                    rect_comprar = pygame.Rect(caixa_x + 40, botao_y_base, caixa_largura - 80, botao_altura)
                    # Botão 1 = SAIR
                    rect_sair = pygame.Rect(caixa_x + 40, botao_y_base + 30, caixa_largura - 80, botao_altura)
                    
                    if rect_comprar.collidepoint(mouse_x, mouse_y):
                        # Confirmar compra
                        self.confirmacao_resposta = True
                        self.fechar()
                        return "confirmado"
                    elif rect_sair.collidepoint(mouse_x, mouse_y):
                        # Cancelar
                        self.confirmacao_resposta = False
                        self.upgrade_pendente = None
                        self.fechar()
                        return "cancelado"
        
        return None
    
    def fechar(self):
        """Fecha a interação com o Crank"""
        # Se estava em diálogo alien, marcar como já mostrado antes de fechar
        if self.fase_dialogo == "dialogo_alien":
            from core.progresso import gerenciador_progresso
            gerenciador_progresso.dialogo_alien_ja_mostrado = True
            gerenciador_progresso.limpar_ultima_compra_alien()
        
        self.ativo = False
        self.sprite_atual = None
        self.texto_atual = ""
        self.fase_dialogo = "fechado"
        # Resetar flag de erro para permitir novo aviso se necessário
        self._erro_sprite_impresso = False
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo do Crank na tela no estilo visual novel"""
        if not self.ativo:
            return
        
        # Se estiver em confirmação de upgrade, usar caixa simples sem sprite
        if self.fase_dialogo == "confirmar_upgrade":
            self._desenhar_confirmacao_upgrade_simples(tela, dt)
            return
        
        # Garantir que os sprites estão carregados (apenas para outros diálogos)
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        if not self.sprite_atual:
            # Tentar usar sprites em ordem de prioridade
            if self.sprite_normal:
                self.sprite_atual = self.sprite_normal
            elif self.sprite_alegre:
                self.sprite_atual = self.sprite_alegre
            elif self.sprite_bravo:
                self.sprite_atual = self.sprite_bravo
            elif self.sprite_estressado:
                self.sprite_atual = self.sprite_estressado
            else:
                # Imprimir erro apenas uma vez para evitar spam de logs
                if not self._erro_sprite_impresso:
                    print(f"ERRO: Nenhum sprite disponível para o Crank! Desativando diálogo.")
                    self._erro_sprite_impresso = True
                    # Desativar o Crank se não houver sprites
                    self.ativo = False
                return
        
        # Overlay escuro no fundo (estilo visual novel)
        # Se estiver em input de nome, usar overlay mais escuro para travar o fundo
        overlay_opacidade = 200 if self.input_nome_ativo else 140
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_opacidade))  # Preto com opacidade variável
        tela.blit(overlay, (0, 0))
        
        # Personagem no canto esquerdo (Crank fica à esquerda, diferente do alien)
        lado_direito = False
        
        # Tamanho do sprite
        sprite_altura_max = 400
        sprite_largura_max = 350
        
        # Se o sprite atual for "surpreso" ou "bravo", usar a mesma escala do "convencido" mas manter proporção
        usar_escala_referencia = False
        sprite_referencia = None
        if self.sprite_convencido:
            if self.sprite_atual == self.sprite_surpreso:
                usar_escala_referencia = True
                sprite_referencia = self.sprite_convencido
            elif self.sprite_atual == self.sprite_bravo:
                usar_escala_referencia = True
                sprite_referencia = self.sprite_convencido
        
        if self.sprite_atual:
            sprite_original_w = self.sprite_atual.get_width()
            sprite_original_h = self.sprite_atual.get_height()
            
            if usar_escala_referencia and sprite_referencia:
                # Calcular a escala do sprite de referência (convencido)
                ref_w = sprite_referencia.get_width()
                ref_h = sprite_referencia.get_height()
                escala_ref_w = sprite_largura_max / ref_w if ref_w > 0 else 1.0
                escala_ref_h = sprite_altura_max / ref_h if ref_h > 0 else 1.0
                escala_ref = min(escala_ref_w, escala_ref_h, 1.0)
                
                # Aplicar a MESMA ESCALA ao sprite atual (surpreso), mantendo sua proporção original
                # Isso garante que ambos tenham o mesmo tamanho visual, mas sem esticar
                sprite_w = int(sprite_original_w * escala_ref)
                sprite_h = int(sprite_original_h * escala_ref)
            else:
                # Calcular escala mantendo proporção normalmente
                escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
                escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
                escala = min(escala_w, escala_h, 1.0)  # Não aumentar além do original
                
                sprite_w = int(sprite_original_w * escala)
                sprite_h = int(sprite_original_h * escala)
            
            sprite_redimensionado = pygame.transform.scale(self.sprite_atual, (sprite_w, sprite_h))
        
        # Posição do sprite (mesma altura do Rex)
        sprite_y = ALTURA // 2 - sprite_h // 2 - 50
        
        if lado_direito:
            sprite_x = LARGURA - sprite_w - 20
        else:
            sprite_x = 20
        
        if self.sprite_atual:
            if self.fase_dialogo == "tutorial" and self.tutorial_parte == 0 and self.tutorial_fase_apresentacao == "sombra":
                # Desenhar como sombra (silhueta escura)
                # Criar uma cópia do sprite e escurecer drasticamente
                sprite_escurecido = sprite_redimensionado.copy()
                # Aplicar um filtro escuro (multiplicar por 0.1 para ficar bem escuro, quase preto)
                for y in range(sprite_h):
                    for x in range(sprite_w):
                        try:
                            pixel = sprite_redimensionado.get_at((x, y))
                            # Se o pixel não for transparente, escurecer
                            if pixel[3] > 0:  # Alpha > 0
                                r, g, b, a = pixel
                                # Escurecer drasticamente (manter apenas 10% do brilho)
                                r = max(0, min(20, int(r * 0.1)))  # Limitar a no máximo 20
                                g = max(0, min(20, int(g * 0.1)))
                                b = max(0, min(20, int(b * 0.1)))
                                sprite_escurecido.set_at((x, y), (r, g, b, a))
                        except:
                            pass
                tela.blit(sprite_escurecido, (sprite_x, sprite_y))
            else:
                # Desenhar sprite normal
                tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
        
        # Determinar cor do contorno baseado no sprite atual
        cor_contorno = (255, 255, 255)  # Branco padrão
        if self.sprite_atual == self.sprite_normal:
            cor_contorno = (200, 200, 200)  # Cinza claro para normal
        elif self.sprite_atual == self.sprite_alegre:
            cor_contorno = (255, 200, 0)  # Amarelo/dourado para alegre
        elif self.sprite_atual == self.sprite_bravo:
            cor_contorno = (255, 100, 100)  # Vermelho para bravo
        elif self.sprite_atual == self.sprite_estressado:
            cor_contorno = (255, 150, 0)  # Laranja para estressado
        elif self.sprite_atual == self.sprite_duvida:
            cor_contorno = (150, 200, 255)  # Azul claro para dúvida
        elif self.sprite_atual == self.sprite_surpreso:
            cor_contorno = (255, 255, 100)  # Amarelo claro para surpreso
        elif self.sprite_atual == self.sprite_triste:
            cor_contorno = (150, 150, 200)  # Azul acinzentado para triste
        elif self.sprite_atual == self.sprite_convencido:
            cor_contorno = (100, 255, 100)  # Verde para convencido
        elif self.sprite_atual == self.sprite_incredulo:
            cor_contorno = (255, 200, 100)  # Laranja claro para incrédulo
        
        # Desenhar caixa de diálogo (igual ao Rex)
        caixa_largura = 1000
        caixa_altura = 200
        caixa_x = (LARGURA - caixa_largura) // 2
        caixa_y = ALTURA - caixa_altura - 50
        
        # Desenhar Glub escurecido no canto direito durante as falas sobre ele (partes 8-12)
        if (self.fase_dialogo == "tutorial_upgrades" and 
            8 <= self.tutorial_upgrades_parte <= 12 and 
            self.glub_sprite_escurecido):
            # Carregar sprite do Glub se ainda não foi carregado
            if not self.glub_sprite_carregado:
                self._carregar_sprite_glub()
            
            if self.glub_sprite_escurecido:
                # Tamanho do sprite do Glub (similar ao do Crank)
                glub_sprite_altura_max = 400
                glub_sprite_largura_max = 350
                
                glub_original_w = self.glub_sprite_escurecido.get_width()
                glub_original_h = self.glub_sprite_escurecido.get_height()
                
                # Calcular escala mantendo proporção
                glub_escala_w = glub_sprite_largura_max / glub_original_w if glub_original_w > 0 else 1.0
                glub_escala_h = glub_sprite_altura_max / glub_original_h if glub_original_h > 0 else 1.0
                glub_escala = min(glub_escala_w, glub_escala_h, 1.0)
                
                glub_w = int(glub_original_w * glub_escala)
                glub_h = int(glub_original_h * glub_escala)
                
                glub_redimensionado = pygame.transform.scale(self.glub_sprite_escurecido, (glub_w, glub_h))
                
                # Posição no canto direito
                glub_x = LARGURA - glub_w - 20
                glub_y = caixa_y - glub_h + 100
                
                # Escurecer drasticamente o sprite (similar ao efeito de sombra)
                glub_escurecido = glub_redimensionado.copy()
                # Aplicar um filtro muito escuro (multiplicar por 0.15 para ficar bem escuro, quase silhueta)
                for y in range(glub_h):
                    for x in range(glub_w):
                        try:
                            pixel = glub_redimensionado.get_at((x, y))
                            # Se o pixel não for transparente, escurecer muito
                            if pixel[3] > 0:  # Alpha > 0
                                r = max(0, int(pixel[0] * 0.15))
                                g = max(0, int(pixel[1] * 0.15))
                                b = max(0, int(pixel[2] * 0.15))
                                glub_escurecido.set_at((x, y), (r, g, b, pixel[3]))
                        except:
                            pass
                
                tela.blit(glub_escurecido, (glub_x, glub_y))
        
        caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
        caixa_fundo.fill((0, 0, 0, 220))
        tela.blit(caixa_fundo, (caixa_x, caixa_y))
        pygame.draw.rect(tela, cor_contorno, (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
        
        # Desenhar nome do personagem (não mostrar na fase de sombra)
        render_text = _get_render_text()
        if not (self.fase_dialogo == "tutorial" and self.tutorial_parte == 0 and self.tutorial_fase_apresentacao == "sombra"):
            # Mostrar "???" se o nome ainda não foi revelado, senão mostrar "CRANK"
            nome_display = "???" if not getattr(self, 'nome_revelado', False) else "CRANK"
            nome_texto = render_text(nome_display, 24, (0, 255, 100), bold=True, pixel_style=True)
            tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
        
        # Atualizar animação de texto
        self._atualizar_animacao_texto(dt)
        
        # Desenhar texto do diálogo usando render_text com pixel_style
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
        
        # Desenhar campo de input de nome se estiver ativo
        if self.input_nome_ativo:
            # Campo de input
            input_y = caixa_y + 120
            input_largura = 400
            input_altura = 40
            input_x = caixa_x + (caixa_largura - input_largura) // 2
            
            # Fundo do campo
            input_fundo = pygame.Surface((input_largura, input_altura), pygame.SRCALPHA)
            input_fundo.fill((50, 50, 50, 255))
            tela.blit(input_fundo, (input_x, input_y))
            pygame.draw.rect(tela, (255, 255, 255), (input_x, input_y, input_largura, input_altura), 2)
            
            # Texto do input (com cursor piscante)
            import time
            cursor_visivel = int(time.time() * 2) % 2 == 0
            texto_input = self.nome_input + ("_" if cursor_visivel else "")
            if not texto_input:
                texto_input = "_" if cursor_visivel else ""
            
            input_texto_render = render_text(texto_input, 20, (255, 255, 255), bold=True, pixel_style=True)
            input_texto_x = input_x + 10
            input_texto_y = input_y + (input_altura - input_texto_render.get_height()) // 2
            tela.blit(input_texto_render, (input_texto_x, input_texto_y))
            
            # Instrução
            instrucao = render_text("Digite seu nome e pressione ENTER", 14, (200, 200, 200), bold=False, pixel_style=True)
            instrucao_x = caixa_x + (caixa_largura - instrucao.get_width()) // 2
            instrucao_y = input_y + input_altura + 10
            tela.blit(instrucao, (instrucao_x, instrucao_y))
        # Desenhar indicador de continuar sempre que o texto estiver completo (se não estiver em input de nome)
        elif len(self.texto_exibido) >= len(self.texto_completo):
            indicador = render_text("Pressione ENTER ou clique para continuar...", 16, (200, 200, 200), bold=False, pixel_style=True)
            indicador_x = caixa_x + caixa_largura - indicador.get_width() - 20
            indicador_y = caixa_y + caixa_altura - 30
            tela.blit(indicador, (indicador_x, indicador_y))
        
        # Desenhar opções de reparar/desistir (se estiver na fase de dano_critico e texto completo)
        if self.fase_dialogo == "dano_critico" and len(self.texto_exibido) >= len(self.texto_completo):
            from core.i18n import t
            opcoes = [t("menu.reparar"), t("menu.desistir")]
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
        
        # Desenhar opções de resposta no meio da tela (se estiver na fase de resposta e texto completo)
        elif self.fase_dialogo == "resposta" and len(self.texto_exibido) >= len(self.texto_completo):
            opcoes = self.obter_opcoes_resposta()
            espacamento = 25
            botao_largura = int(LARGURA * 0.45)  # Reduzido de 60% para 45% da largura da tela
            botao_x = (LARGURA - botao_largura) // 2  # Centralizado
            
            # Calcular posição Y para centralizar verticalmente
            # Primeiro, calcular altura total necessária
            altura_total = 0
            for opcao_texto in opcoes:
                palavras_opcao = opcao_texto.split()
                linhas_opcao = []
                linha_opcao = ""
                for palavra in palavras_opcao:
                    teste = linha_opcao + (" " if linha_opcao else "") + palavra
                    texto_teste = render_text(teste, 24, (255, 255, 255), bold=False, pixel_style=False)
                    if texto_teste.get_width() <= botao_largura - 60:  # Margem maior para texto menor
                        linha_opcao = teste
                    else:
                        if linha_opcao:
                            linhas_opcao.append(linha_opcao)
                        linha_opcao = palavra
                if linha_opcao:
                    linhas_opcao.append(linha_opcao)
                altura_total += len(linhas_opcao) * 28 + 35  # Altura do texto + linha + espaçamento
            
            inicio_y = (ALTURA - altura_total) // 2
            y_atual = inicio_y
            
            # Obter posição do mouse para hover
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Primeiro, calcular todas as hitboxes de forma consistente
            hitboxes = []
            y_calc = inicio_y
            for opcao_texto in opcoes:
                palavras_opcao = opcao_texto.split()
                linhas_opcao = []
                linha_opcao = ""
                for palavra in palavras_opcao:
                    teste = linha_opcao + (" " if linha_opcao else "") + palavra
                    texto_teste = render_text(teste, 24, (255, 255, 255), bold=False, pixel_style=False)
                    if texto_teste.get_width() <= botao_largura - 60:  # Margem maior para texto menor
                        linha_opcao = teste
                    else:
                        if linha_opcao:
                            linhas_opcao.append(linha_opcao)
                        linha_opcao = palavra
                if linha_opcao:
                    linhas_opcao.append(linha_opcao)
                
                texto_y_calc = y_calc
                linha_y_calc = texto_y_calc + (len(linhas_opcao) * 28) + 5
                altura_opcao = linha_y_calc - texto_y_calc + 10
                hitboxes.append(pygame.Rect(botao_x, texto_y_calc, botao_largura, altura_opcao))
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
            y_atual = inicio_y
            for i, opcao_texto in enumerate(opcoes):
                # Calcular quantas linhas o texto precisa
                palavras_opcao = opcao_texto.split()
                linhas_opcao = []
                linha_opcao = ""
                
                for palavra in palavras_opcao:
                    teste = linha_opcao + (" " if linha_opcao else "") + palavra
                    texto_teste = render_text(teste, 24, (255, 255, 255), bold=False, pixel_style=False)
                    if texto_teste.get_width() <= botao_largura - 60:  # Margem maior para texto menor
                        linha_opcao = teste
                    else:
                        if linha_opcao:
                            linhas_opcao.append(linha_opcao)
                        linha_opcao = palavra
                if linha_opcao:
                    linhas_opcao.append(linha_opcao)
                
                # Calcular área clicável (para hover e clique)
                texto_y = y_atual
                linha_y = texto_y + (len(linhas_opcao) * 28) + 5
                
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
                for j, linha_op in enumerate(linhas_opcao):
                    texto_opcao = render_text(linha_op, 24, cor_texto, bold=False, pixel_style=False)
                    texto_opcao_x = botao_x + (botao_largura - texto_opcao.get_width()) // 2
                    tela.blit(texto_opcao, (texto_opcao_x, texto_y + (j * 28)))
                
                # Desenhar linha embaixo do texto (mais fina e menor)
                linha_largura = botao_largura - 80
                linha_x = botao_x + (botao_largura - linha_largura) // 2
                pygame.draw.line(tela, cor_linha, (linha_x, linha_y), (linha_x + linha_largura, linha_y), 1)
                
                y_atual = linha_y + espacamento
        
        # Não desenhar botões - o jogador clica na caixa ou usa teclado para avançar/fechar
        
        # Feedback visual de mudança de preço (se houver) - desenhar próximo ao texto
        if self.fase_dialogo == "reacao" and self.mudanca_preco != 0:
            # Garantir que os ícones estão carregados
            if not self.icones_carregados:
                self._carregar_icones()
            
            # Desenhar seta indicando mudança próximo ao texto (usando coordenadas da caixa)
            seta_x = caixa_x + caixa_largura - 60
            seta_y = caixa_y + caixa_altura - 50
            
            if self.mudanca_preco == -1:
                # Seta para baixo (preço diminuiu) - usar seta.png rotacionada
                if self.icone_seta:
                    seta_redimensionada = pygame.transform.scale(self.icone_seta, (30, 30))
                    seta_rotacionada = pygame.transform.rotate(seta_redimensionada, 180)  # Rotacionar 180° para baixo
                    tela.blit(seta_rotacionada, (seta_x - 15, seta_y - 15))
            else:  # mudanca_preco == 1
                # Seta para cima (preço aumentou) - usar encareceu.png ou seta.png
                if self.icone_encareceu:
                    # Usar ícone de encareceu se disponível
                    icone_redimensionado = pygame.transform.scale(self.icone_encareceu, (30, 30))
                    tela.blit(icone_redimensionado, (seta_x - 15, seta_y - 15))
                elif self.icone_seta:
                    # Fallback para seta.png normal (apontando para cima)
                    seta_redimensionada = pygame.transform.scale(self.icone_seta, (30, 30))
                    tela.blit(seta_redimensionada, (seta_x - 15, seta_y - 15))

# Instância global
crank = Crank()

