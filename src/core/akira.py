"""Sistema da Akira - Mestra do Fluxo que aparece antes e depois das corridas"""
import pygame
import os
import json
from config import DIR_PROJETO, LARGURA, ALTURA
from core.progresso import gerenciador_progresso
from core.estatisticas import gerenciador_estatisticas

def _get_render_text():
    """Importa render_text de forma lazy para evitar import circular"""
    from core.menu import render_text
    return render_text

CAMINHO_AKIRA_DATA = os.path.join(DIR_PROJETO, "data", "akira.json")

CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters", "akira")
SPRITE_NEUTRO = os.path.join(CAMINHO_SPRITES, "akira_neutra.png")
SPRITE_ENSINANDO = os.path.join(CAMINHO_SPRITES, "akira_sorriso_sutil.png")
SPRITE_FOCADA = os.path.join(CAMINHO_SPRITES, "akira_seria.png")
SPRITE_RESPEITO = os.path.join(CAMINHO_SPRITES, "akira_sorriso_sutil.png")  # Usar sorriso sutil para respeito
SPRITE_DECEPCIONADA = os.path.join(CAMINHO_SPRITES, "akira_seria.png")  # Usar séria para decepcionada

CAMINHO_CENA_FUNDO_PRE = os.path.join(DIR_PROJETO, "assets", "images", "ui", "pista_corrida.png")
CAMINHO_CENA_FUNDO_FIM = os.path.join(DIR_PROJETO, "assets", "images", "ui", "fim_corrida.png")

class Akira:
    """Akira - Mestra do Fluxo que aparece antes e depois das corridas"""
    
    def __init__(self):
        self.carregar_estado()
        self.sprite_neutro = None
        self.sprite_ensinando = None
        self.sprite_focada = None
        self.sprite_respeito = None
        self.sprite_decepcionada = None
        self.sprite_fundo_pre = None
        self.sprite_fundo_fim = None
        self.sprites_carregados = False
        self.sprites_redimensionados_cache = {}  # Cache de sprites redimensionados
        
        self.ativo = False
        self.opcao_corrida_selecionada = 0
        self.corridas_disponiveis = [
            {"nome": "Teste de Fluxo", "pista": 3, "preco": 0, "recompensa": 0, "dificuldade": "medio", "indice": 0, "race_id": "mountain_test"}
        ]
        self.corridas_desbloqueadas = [0]  # Por padrão, a primeira corrida está desbloqueada
        self.sprite_atual = None
        self.texto_atual = ""
        self.modo_dialogo = None
        self.numero_pista_atual = 1
        self.parte_dialogo = 0
        
        self.ultima_corrida = {
            'posicao': None,
            'colisoes': 0,
            'venceu': False
        }
        
        self.texto_completo = ""
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        self.velocidade_texto = 50.0
        
        self.nome_revelado = False
        self.primeira_aparicao_mostrada = False
        self.corrida_aceita = False
        
    def carregar_estado(self):
        """Carrega o estado da Akira APENAS de progresso.json"""
        if hasattr(gerenciador_progresso, 'akira_dialogos_pre_corrida_mostrados'):
            self.dialogos_pre_corrida_mostrados = gerenciador_progresso.akira_dialogos_pre_corrida_mostrados.copy() if gerenciador_progresso.akira_dialogos_pre_corrida_mostrados else {}
            self.nome_revelado = gerenciador_progresso.akira_nome_revelado if hasattr(gerenciador_progresso, 'akira_nome_revelado') else False
            self.primeira_aparicao_mostrada = gerenciador_progresso.akira_primeira_aparicao_mostrada if hasattr(gerenciador_progresso, 'akira_primeira_aparicao_mostrada') else False
        else:
            self.nome_revelado = False
            self.dialogos_pre_corrida_mostrados = {}
            self.primeira_aparicao_mostrada = False
        
        if os.path.exists(CAMINHO_AKIRA_DATA) and not self.dialogos_pre_corrida_mostrados:
            try:
                with open(CAMINHO_AKIRA_DATA, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not self.dialogos_pre_corrida_mostrados:
                        self.dialogos_pre_corrida_mostrados = data.get('dialogos_pre_corrida_mostrados', {})
                    if not self.nome_revelado:
                        self.nome_revelado = data.get('nome_revelado', False)
                    self.salvar_estado()
                    try:
                        os.remove(CAMINHO_AKIRA_DATA)
                        print("✓ Migrado akira.json para progresso.json e arquivo antigo removido")
                    except:
                        pass
            except Exception as e:
                print(f"Erro ao migrar akira.json: {e}")
    
    def salvar_estado(self):
        """Salva o estado da Akira APENAS em progresso.json"""
        # Salvar APENAS em progresso.json (sistema consolidado)
        if hasattr(gerenciador_progresso, 'akira_dialogos_pre_corrida_mostrados'):
            gerenciador_progresso.akira_nome_revelado = getattr(self, 'nome_revelado', False)
            gerenciador_progresso.akira_dialogos_pre_corrida_mostrados = getattr(self, 'dialogos_pre_corrida_mostrados', {}).copy()
            gerenciador_progresso.akira_primeira_aparicao_mostrada = getattr(self, 'primeira_aparicao_mostrada', False)
            gerenciador_progresso.salvar()
        else:
            print("AVISO: gerenciador_progresso não tem atributos da Akira")
    
    def carregar_sprites(self):
        """Carrega os sprites da Akira"""
        if self.sprites_carregados:
            return  # Já foram carregados
        
        try:
            # Garantir que pygame está inicializado
            if not pygame.get_init():
                print("AVISO: pygame não inicializado, tentando inicializar...")
                pygame.init()
            
            # Criar diretório se não existir
            os.makedirs(CAMINHO_SPRITES, exist_ok=True)
            
            # Carregar sprites com nomes corretos
            if os.path.exists(SPRITE_NEUTRO):
                self.sprite_neutro = pygame.image.load(SPRITE_NEUTRO).convert_alpha()
                print(f"[AKIRA] Sprite neutro carregado: {SPRITE_NEUTRO}")
            else:
                print(f"[AKIRA] AVISO: Sprite neutro não encontrado: {SPRITE_NEUTRO}")
                self.sprite_neutro = pygame.Surface((200, 200), pygame.SRCALPHA)
                self.sprite_neutro.fill((150, 100, 100, 255))
            
            if os.path.exists(SPRITE_ENSINANDO):
                self.sprite_ensinando = pygame.image.load(SPRITE_ENSINANDO).convert_alpha()
                print(f"[AKIRA] Sprite ensinando carregado: {SPRITE_ENSINANDO}")
            else:
                print(f"[AKIRA] AVISO: Sprite ensinando não encontrado: {SPRITE_ENSINANDO}, usando neutro")
                self.sprite_ensinando = self.sprite_neutro
            
            if os.path.exists(SPRITE_FOCADA):
                self.sprite_focada = pygame.image.load(SPRITE_FOCADA).convert_alpha()
                print(f"[AKIRA] Sprite focada carregado: {SPRITE_FOCADA}")
            else:
                print(f"[AKIRA] AVISO: Sprite focada não encontrado: {SPRITE_FOCADA}, usando neutro")
                self.sprite_focada = self.sprite_neutro
            
            if os.path.exists(SPRITE_RESPEITO):
                self.sprite_respeito = pygame.image.load(SPRITE_RESPEITO).convert_alpha()
                print(f"[AKIRA] Sprite respeito carregado: {SPRITE_RESPEITO}")
            else:
                print(f"[AKIRA] AVISO: Sprite respeito não encontrado: {SPRITE_RESPEITO}, usando neutro")
                self.sprite_respeito = self.sprite_neutro
            
            if os.path.exists(SPRITE_DECEPCIONADA):
                self.sprite_decepcionada = pygame.image.load(SPRITE_DECEPCIONADA).convert_alpha()
                print(f"[AKIRA] Sprite decepcionada carregado: {SPRITE_DECEPCIONADA}")
            else:
                print(f"[AKIRA] AVISO: Sprite decepcionada não encontrado: {SPRITE_DECEPCIONADA}, usando neutro")
                self.sprite_decepcionada = self.sprite_neutro
            
            if os.path.exists(CAMINHO_CENA_FUNDO_PRE):
                self.sprite_fundo_pre = pygame.image.load(CAMINHO_CENA_FUNDO_PRE).convert()
                self.sprite_fundo_pre = pygame.transform.scale(self.sprite_fundo_pre, (LARGURA, ALTURA))
            else:
                self.sprite_fundo_pre = None
            
            if os.path.exists(CAMINHO_CENA_FUNDO_FIM):
                self.sprite_fundo_fim = pygame.image.load(CAMINHO_CENA_FUNDO_FIM).convert()
                self.sprite_fundo_fim = pygame.transform.scale(self.sprite_fundo_fim, (LARGURA, ALTURA))
            else:
                self.sprite_fundo_fim = None
            
            self.sprites_carregados = True
        except Exception as e:
            print(f"ERRO ao carregar sprites da Akira: {e}")
            import traceback
            traceback.print_exc()
    
    def verificar_aparecer_primeira_vez(self):
        """Verifica se a Akira deve aparecer na primeira vez que o jogador visita a montanha"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        if self.primeira_aparicao_mostrada:
            return False
        
        # Garantir que os sprites estão carregados antes de ativar
        if not self.sprite_neutro:
            self.carregar_sprites()
        
        self.ativo = True
        self.modo_dialogo = "primeira_aparicao"
        self.parte_dialogo = 0
        self._iniciar_dialogo_primeira_aparicao()
        
        return True
    
    def _iniciar_dialogo_primeira_aparicao(self):
        """Inicia o diálogo de primeira aparição da Akira"""
        self.parte_dialogo = 0
        self._avancar_dialogo_primeira_aparicao()
    
    def _avancar_dialogo_primeira_aparicao(self):
        """Avança o diálogo de primeira aparição da Akira"""
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Garantir que pelo menos sprite_neutro existe
        if not self.sprite_neutro:
            print("[AKIRA] ERRO: sprite_neutro não carregado após carregar_sprites()")
            return
        
        if self.parte_dialogo == 0:
            self.sprite_atual = self.sprite_neutro
            self._iniciar_animacao_texto("…")
        elif self.parte_dialogo == 1:
            self.sprite_atual = self.sprite_neutro
            self._iniciar_animacao_texto("Você trouxe mais um carro barulhento pra minha montanha.")
        elif self.parte_dialogo == 2:
            self.sprite_atual = self.sprite_ensinando if self.sprite_ensinando else self.sprite_neutro
            self._iniciar_animacao_texto("Mas antes de você pensar em correr aqui, precisa entender algo importante.")
        elif self.parte_dialogo == 3:
            self.sprite_atual = self.sprite_focada if self.sprite_focada else self.sprite_neutro
            self._iniciar_animacao_texto("Minhas pistas exigem preparo. Você precisa de melhorias no seu carro, especialmente nos pneus.")
        elif self.parte_dialogo == 4:
            self.sprite_atual = self.sprite_ensinando if self.sprite_ensinando else self.sprite_neutro
            self._iniciar_animacao_texto("Eu não vendo nada aqui. Você pode comprar essas melhorias com o Boris na fábrica ou com o Crank na oficina.")
        elif self.parte_dialogo == 5:
            self.sprite_atual = self.sprite_focada if self.sprite_focada else self.sprite_neutro
            self._iniciar_animacao_texto("Para começar a correr aqui, você precisa ter pelo menos pneus nível 1 instalados no seu carro.")
        elif self.parte_dialogo == 6:
            self.sprite_atual = self.sprite_ensinando if self.sprite_ensinando else self.sprite_neutro
            self._iniciar_animacao_texto("O que busco aqui é o 'Fluxo'. A harmonia perfeita entre piloto, máquina e pista. Não é apenas velocidade - é técnica, controle e respeito pela estrada.")
        elif self.parte_dialogo == 7:
            self.sprite_atual = self.sprite_focada if self.sprite_focada else self.sprite_neutro
            self._iniciar_animacao_texto("Quando você encontrar o Fluxo, sentirá como se o carro fosse uma extensão do seu corpo. Cada curva será fluida, cada aceleração será precisa. É isso que separa um piloto comum de um verdadeiro mestre.")
        elif self.parte_dialogo == 8:
            self.sprite_atual = self.sprite_neutro
            self._iniciar_animacao_texto("Quando estiver pronto, volte aqui. Minhas pistas não perdoam quem não está preparado.")
        else:
            # Finalizar primeira aparição
            self.primeira_aparicao_mostrada = True
            self.salvar_estado()
            
            # Salvar também missões e localizações após primeira aparição
            try:
                from core.missoes import gerenciador_missoes
                from core.mapa_locations import gerenciador_localizacoes
                gerenciador_missoes.salvar()
                gerenciador_localizacoes.salvar()
                print("[AKIRA] Progresso completo salvo após primeira aparição")
            except Exception as e:
                print(f"[AKIRA] Erro ao salvar missões/localizações: {e}")
            
            # Após primeira aparição, verificar se tem pneus e oferecer corrida
            from core.progresso import gerenciador_progresso
            carro_atual = gerenciador_progresso.obter_carro_atual(1)
            if not carro_atual:
                carro_atual = "Car1"
            
            # Garantir que carro_atual é string (prefixo_cor)
            if isinstance(carro_atual, int):
                from config import CARROS_DISPONIVEIS
                if 0 <= carro_atual < len(CARROS_DISPONIVEIS):
                    carro_atual = CARROS_DISPONIVEIS[carro_atual].get("prefixo_cor", "Car1")
                else:
                    carro_atual = "Car1"
            
            nivel_pneu = gerenciador_progresso.obter_upgrade(carro_atual, "rodas")
            
            # Se tem pneus, ativar diálogo de corrida imediatamente
            if nivel_pneu >= 1:
                print(f"[AKIRA] Primeira aparição terminada, jogador tem pneus nível {nivel_pneu}, ativando diálogo de corrida")
                self.modo_dialogo = "corrida"
                self.opcao_corrida_selecionada = 0
                self.sprite_atual = self.sprite_neutro
                # Limpar texto da primeira aparição
                self.texto_completo = ""
                self.texto_exibido = ""
                self.tempo_animacao = 0.0
                # Não fechar - continuar ativo com menu de corridas
            else:
                # Não tem pneus - fechar normalmente
                print(f"[AKIRA] Primeira aparição terminada, jogador não tem pneus (nível {nivel_pneu}), fechando")
                self.fechar()
    
    def obter_corridas_disponiveis(self):
        """Retorna as corridas desbloqueadas da Akira"""
        return [corrida for corrida in self.corridas_disponiveis if corrida["indice"] in self.corridas_desbloqueadas]
    
    def ativar_dialogo_corrida(self):
        """Ativa o diálogo da Akira para oferecer corrida (sempre mostra menu de corridas)"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        # Verificar se tem pneu nível 1
        from core.progresso import gerenciador_progresso
        carro_atual = gerenciador_progresso.obter_carro_atual(1)
        
        # Se não tem carro definido, usar Car1 como padrão
        if not carro_atual:
            carro_atual = "Car1"
            print(f"[AKIRA] Carro atual não definido, usando Car1 como padrão")
        
        # Garantir que carro_atual é string (prefixo_cor)
        if isinstance(carro_atual, int):
            from config import CARROS_DISPONIVEIS
            if 0 <= carro_atual < len(CARROS_DISPONIVEIS):
                carro_atual = CARROS_DISPONIVEIS[carro_atual].get("prefixo_cor", "Car1")
            else:
                carro_atual = "Car1"
        
        nivel_pneu = gerenciador_progresso.obter_upgrade(carro_atual, "rodas")
        print(f"[AKIRA] Verificando pneus: carro_atual={carro_atual}, nivel_pneu={nivel_pneu}, upgrades={gerenciador_progresso.upgrades.get(carro_atual, {})}")
        
        # Verificar se tem pelo menos nível 1 (nivel_pneu >= 1)
        # nivel_pneu retorna 0 se não tiver upgrade, então precisa ser >= 1
        if nivel_pneu < 1:
            # Não tem pneus - mostrar mensagem e fechar
            print(f"[AKIRA] Jogador não tem pneus nível 1 (nível atual: {nivel_pneu})")
            self.ativo = True
            self.modo_dialogo = "sem_preparo"
            self.parte_dialogo = 0
            self.sprite_atual = self.sprite_focada if self.sprite_focada else self.sprite_neutro
            self._iniciar_animacao_texto("Você ainda não está pronto. Precisa ter pelo menos pneus nível 1 instalados no seu carro para correr aqui. Vá até o Boris ou o Crank para comprar melhorias.")
            return True
        else:
            # Tem pneus - mostrar diálogo de reconhecimento antes de oferecer corrida
            print(f"[AKIRA] Jogador tem pneus nível {nivel_pneu}, mostrando diálogo de reconhecimento")
            self.ativo = True
            self.modo_dialogo = "com_preparo"
            self.parte_dialogo = 0
            self.sprite_atual = self.sprite_ensinando if self.sprite_ensinando else self.sprite_neutro
            self._iniciar_dialogo_com_preparo()
            return True
    
    def _iniciar_dialogo_com_preparo(self):
        """Inicia o diálogo quando o jogador já tem os pneus nível 1"""
        self.parte_dialogo = 0
        self._avancar_dialogo_com_preparo()
    
    def _avancar_dialogo_com_preparo(self):
        """Avança o diálogo quando o jogador já tem os pneus nível 1"""
        if self.parte_dialogo == 0:
            self.sprite_atual = self.sprite_ensinando if self.sprite_ensinando else self.sprite_neutro
            self._iniciar_animacao_texto("Vejo que você se preparou. Seus pneus estão adequados para minhas pistas.")
        elif self.parte_dialogo == 1:
            self.sprite_atual = self.sprite_neutro
            self._iniciar_animacao_texto("Agora você pode testar suas habilidades aqui. Minhas pistas exigem técnica e controle, não apenas velocidade bruta.")
        elif self.parte_dialogo == 2:
            self.sprite_atual = self.sprite_ensinando if self.sprite_ensinando else self.sprite_neutro
            self._iniciar_animacao_texto("Escolha uma corrida quando estiver pronto. Lembre-se: busque o Fluxo, não apenas a vitória.")
        else:
            # Finalizar diálogo e abrir menu de corridas
            self.modo_dialogo = "corrida"
            self.opcao_corrida_selecionada = 0
            self.sprite_atual = self.sprite_neutro
            # Limpar texto do diálogo anterior
            self.texto_completo = ""
            self.texto_exibido = ""
            self.tempo_animacao = 0.0
    
    
    def verificar_aparecer_pre_corrida(self, numero_pista):
        """Verifica se a Akira deve aparecer antes de uma corrida"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        pista_key = str(numero_pista)
        
        if not hasattr(self, 'dialogos_pre_corrida_mostrados'):
            self.dialogos_pre_corrida_mostrados = {}
        
        if hasattr(gerenciador_progresso, 'akira_dialogos_pre_corrida_mostrados'):
            if gerenciador_progresso.akira_dialogos_pre_corrida_mostrados:
                self.dialogos_pre_corrida_mostrados = gerenciador_progresso.akira_dialogos_pre_corrida_mostrados.copy()
        
        if self.dialogos_pre_corrida_mostrados.get(pista_key, False):
            return False
        
        self.ativo = True
        self.modo_dialogo = "pre_corrida"
        self.numero_pista_atual = numero_pista
        self.parte_dialogo = 0
        self._iniciar_dialogo_pre_corrida()
        
        return True
    
    def verificar_aparecer_pos_corrida(self, posicao, colisoes, venceu):
        """Verifica se a Akira deve aparecer depois de uma corrida"""
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        self.ultima_corrida = {
            'posicao': posicao,
            'colisoes': colisoes,
            'venceu': venceu
        }
        
        self.ativo = True
        self.modo_dialogo = "fim_corrida"
        self.parte_dialogo = 0
        self._iniciar_dialogo_fim_corrida()
        
        return True
    
    def _iniciar_dialogo_pre_corrida(self):
        """Inicia o diálogo pré-corrida da Akira"""
        self.parte_dialogo = 0
        self._avancar_dialogo_pre_corrida()
    
    def _avancar_dialogo_pre_corrida(self):
        """Avança o diálogo pré-corrida baseado na pista (1-9)"""
        pista = self.numero_pista_atual
        
        if pista == 1:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Olá. Eu sou Akira. Vejo muitos pilotos novos chegarem aqui achando que velocidade é tudo. Rex é o rei desses tolos.")
            elif self.parte_dialogo == 1:
                self.sprite_atual = self.sprite_ensinando
                self._iniciar_animacao_texto("Eu busco o 'Fluxo'. A harmonia entre piloto, máquina e pista. Esta primeira pista é simples. Mostre-me que você tem disciplina para controlá-la, não apenas força bruta.")
            else:
                self.fechar()
        elif pista == 2:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Qualquer um pode acelerar numa reta. A verdade de um piloto se revela na curva.")
            elif self.parte_dialogo == 1:
                self.sprite_atual = self.sprite_ensinando
                self._iniciar_animacao_texto("Não lute contra o carro na virada. Respire. Sinta o peso transferir. Dance com a pista, não tente espancá-la.")
            else:
                self.fechar()
        elif pista == 3:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Estou vendo marcas de tinta nas paredes dos treinos anteriores. Agressividade excessiva é deselegante.")
            elif self.parte_dialogo == 1:
                self.sprite_atual = self.sprite_focada
                self._iniciar_animacao_texto("Bater não te faz mais rápido, apenas te faz parecer desesperado. Mantenha o carro limpo hoje. O Velho na oficina agradecerá.")
            else:
                self.fechar()
        elif pista == 4:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("O caminho se estreita agora. O espaço para erro é mínimo.")
            elif self.parte_dialogo == 1:
                self.sprite_atual = self.sprite_ensinando
                self._iniciar_animacao_texto("Sua mente está calma o suficiente para este desafio? Se você entrar em pânico aqui, a pista vai te engolir.")
            else:
                self.fechar()
        elif pista == 5:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Esta pista exige um ritmo perfeito. É como a cerimônia do chá. Se você errar o tempo da primeira curva, estragará todas as seguintes.")
            else:
                self.fechar()
        elif pista == 6:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_focada
                self._iniciar_animacao_texto("Observo seu progresso. Você tem potencial, mas ainda sinto hesitação nas suas manobras. Confie nos seus pneus. O carro sabe o caminho se você permitir.")
            else:
                self.fechar()
        elif pista == 7:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Muitos pilotos rápidos quebram nesta pista. Ela exige paciência nas entradas e explosão nas saídas. Não seja ganancioso.")
            else:
                self.fechar()
        elif pista == 8:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_ensinando
                self._iniciar_animacao_texto("Estamos perto do topo. O ar é rarefeito aqui em cima. Um erro de cálculo agora e todo o seu trabalho duro desaparece. Foco absoluto.")
            else:
                self.fechar()
        elif pista == 9:
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_focada
                self._iniciar_animacao_texto("A última prova. Não há mais nada para eu ensinar com palavras.")
            elif self.parte_dialogo == 1:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Agora é apenas você, a máquina e o asfalto. Torne-se um só com eles. Mostre-me a sua arte final.")
            else:
                self.fechar()
        else:
            # Pistas adicionais (10+)
            if self.parte_dialogo == 0:
                self.sprite_atual = self.sprite_neutro
                self._iniciar_animacao_texto("Continue buscando o Fluxo. Cada pista é uma nova lição.")
            else:
                self.fechar()
    
    def _iniciar_dialogo_fim_corrida(self):
        """Inicia o diálogo fim de corrida da Akira"""
        self.parte_dialogo = 0
        self._avancar_dialogo_fim_corrida()
    
    def _avancar_dialogo_fim_corrida(self):
        """Avança o diálogo fim de corrida baseado no desempenho"""
        from core.progresso import gerenciador_progresso
        from core.estatisticas import gerenciador_estatisticas
        
        posicao = self.ultima_corrida['posicao']
        colisoes = self.ultima_corrida['colisoes']
        venceu = self.ultima_corrida['venceu']
        
        # Verificar se é a primeira corrida ou se os flags ainda não foram desbloqueados
        # IMPORTANTE: Esta verificação acontece DEPOIS de registrar_corrida_completa ser chamado,
        # então se corridas_completas == 1, significa que esta é a primeira corrida que acabou de ser registrada
        # Também verificamos se os flags ainda não estão desbloqueados como fallback
        stats_gerais = gerenciador_estatisticas.obter_estatisticas_gerais()
        corridas_completas = stats_gerais.get("corridas_completas", 0)
        primeira_corrida = (corridas_completas == 1) or (corridas_completas >= 1 and not gerenciador_progresso.oficina_desbloqueada)
        
        # Determinar cenário
        boa_colocacao = venceu or (posicao is not None and posicao <= 3)
        carro_limpo = colisoes == 0 or colisoes <= 2
        
        if primeira_corrida:
            if self.parte_dialogo == 0:
                if boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_respeito
                    self._iniciar_animacao_texto("Impressionante. Você encontrou o Fluxo hoje. Rápido e suave, como a água contornando uma pedra. Uma vitória merecida e elegante.")
                elif boa_colocacao and not carro_limpo:
                    self.sprite_atual = self.sprite_neutro
                    self._iniciar_animacao_texto("Você venceu... mas a que custo? Sua condução foi bárbara. Você tratou a pista como um campo de batalha, não um parceiro de dança.")
                elif not boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_ensinando
                    self._iniciar_animacao_texto("Sua técnica foi limpa, houve respeito pela máquina. Isso é louvável. Mas faltou o espírito de luta.")
                else:
                    self.sprite_atual = self.sprite_decepcionada
                    self._iniciar_animacao_texto("Um desastre completo. Você foi lento e destrutivo. Correu como um elefante numa loja de porcelana.")
            elif self.parte_dialogo == 1:
                if boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_respeito
                    self._iniciar_animacao_texto("E o Velho ficará de bom humor hoje. É raro ver um carro voltar tão inteiro depois de uma vitória dessas.")
                elif boa_colocacao and not carro_limpo:
                    self.sprite_atual = self.sprite_decepcionada
                    self._iniciar_animacao_texto("Prepare os ouvidos. O mecânico vai ter uma longa noite desamassando essa lataria, e ele vai garantir que você ouça cada reclamação dele.")
                elif not boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_ensinando
                    self._iniciar_animacao_texto("O carro está inteiro, pelo menos. O Velho não vai gritar com você, mas a elegância sozinha não ganha troféus. Você precisa encontrar o equilíbrio entre a calma e o fogo.")
                else:
                    self.sprite_atual = self.sprite_decepcionada
                    self._iniciar_animacao_texto("Se eu fosse você, nem aparecia na oficina hoje. O Velho é capaz de te jogar uma chave inglesa na cabeça quando vir o estado desse carro. Lamentável.")
            elif self.parte_dialogo == 2:
                self.sprite_atual = self.sprite_ensinando
                self._iniciar_animacao_texto("Falando em oficina... Agora que você completou sua primeira corrida, pode visitar a oficina no menu principal. Lá você encontrará o Crank, o mecânico. Ele pode melhorar seu carro com upgrades, mas cuidado: ele é rabugento e reage ao estado do seu veículo.")
            elif self.parte_dialogo == 3:
                self.sprite_atual = self.sprite_ensinando
                self._iniciar_animacao_texto("E no menu, você também encontrará a 'Hierarquia'. É o ranking dos pilotos. Cada vitória te coloca mais alto, cada derrota te empurra para baixo. É lá que você verá sua posição entre os melhores pilotos das ruas.")
            else:
                gerenciador_progresso.hierarquia_desbloqueada = True
                gerenciador_progresso.oficina_desbloqueada = True
                gerenciador_progresso.salvar()
                self.fechar()
        else:
            if self.parte_dialogo == 0:
                if boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_respeito
                    self._iniciar_animacao_texto("Impressionante. Você encontrou o Fluxo hoje. Rápido e suave, como a água contornando uma pedra. Uma vitória merecida e elegante.")
                elif boa_colocacao and not carro_limpo:
                    self.sprite_atual = self.sprite_neutro
                    self._iniciar_animacao_texto("Você venceu... mas a que custo? Sua condução foi bárbara. Você tratou a pista como um campo de batalha, não um parceiro de dança.")
                elif not boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_ensinando
                    self._iniciar_animacao_texto("Sua técnica foi limpa, houve respeito pela máquina. Isso é louvável. Mas faltou o espírito de luta.")
                else:
                    self.sprite_atual = self.sprite_decepcionada
                    self._iniciar_animacao_texto("Um desastre completo. Você foi lento e destrutivo. Correu como um elefante numa loja de porcelana.")
            elif self.parte_dialogo == 1:
                if boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_respeito
                    self._iniciar_animacao_texto("E o Velho ficará de bom humor hoje. É raro ver um carro voltar tão inteiro depois de uma vitória dessas.")
                elif boa_colocacao and not carro_limpo:
                    self.sprite_atual = self.sprite_decepcionada
                    self._iniciar_animacao_texto("Prepare os ouvidos. O mecânico vai ter uma longa noite desamassando essa lataria, e ele vai garantir que você ouça cada reclamação dele.")
                elif not boa_colocacao and carro_limpo:
                    self.sprite_atual = self.sprite_ensinando
                    self._iniciar_animacao_texto("O carro está inteiro, pelo menos. O Velho não vai gritar com você, mas a elegância sozinha não ganha troféus. Você precisa encontrar o equilíbrio entre a calma e o fogo.")
                else:
                    self.sprite_atual = self.sprite_decepcionada
                    self._iniciar_animacao_texto("Se eu fosse você, nem aparecia na oficina hoje. O Velho é capaz de te jogar uma chave inglesa na cabeça quando vir o estado desse carro. Lamentável.")
            else:
                self.fechar()
    
    def _iniciar_animacao_texto(self, texto):
        """Inicia animação de texto letra por letra"""
        self.texto_completo = texto
        self.texto_exibido = ""
        self.tempo_animacao = 0.0
        
        if not getattr(self, 'nome_revelado', False):
            texto_lower = texto.lower()
            if "akira" in texto_lower or "eu sou" in texto_lower or "meu nome" in texto_lower:
                self.nome_revelado = True
                self.salvar_estado()
    
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
        
        # Verificar se corrida foi aceita
        if self.corrida_aceita:
            self.corrida_aceita = False
            return {
                "corrida": True,
                "pista": 3,  # Pista 3 - Montanha Akira
                "tipo": "desafio_touge",
                "nome": "Desafio de Montanha (Touge)",
                "race_id": "mountain_test",  # ID da corrida para campanha
                "voltas": 1,
                "dificuldade": "medio",
                "sem_bots": False
            }
        
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.modo_dialogo == "corrida":
                        # Processar seleção de corrida
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        if self.opcao_corrida_selecionada < len(corridas_disponiveis):
                            corrida = corridas_disponiveis[self.opcao_corrida_selecionada]
                            # Akira não cobra nada - iniciar corrida diretamente
                            self.fechar()
                            return {
                                "corrida": True,
                                "pista": corrida["pista"],
                                "tipo": "desafio_touge",
                                "nome": corrida["nome"],
                                "race_id": corrida.get("race_id", "mountain_test"),
                                "voltas": 1,
                                "dificuldade": corrida.get("dificuldade", "medio"),
                                "sem_bots": False
                            }
                        elif self.opcao_corrida_selecionada == len(corridas_disponiveis):
                            # Opção "SAIR"
                            self.fechar()
                            return "fechado"
                    elif len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        if self.modo_dialogo == "requisito_pneu" or self.modo_dialogo == "sem_preparo":
                            self.fechar()
                        else:
                            self.parte_dialogo += 1
                            if self.modo_dialogo == "primeira_aparicao":
                                self._avancar_dialogo_primeira_aparicao()
                            elif self.modo_dialogo == "pre_corrida":
                                self._avancar_dialogo_pre_corrida()
                            elif self.modo_dialogo == "fim_corrida":
                                self._avancar_dialogo_fim_corrida()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                    return "processado"
                elif ev.key == pygame.K_ESCAPE:
                    if self.modo_dialogo == "corrida":
                        self.fechar()
                        return "fechado"
                    elif len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        if self.modo_dialogo == "requisito_pneu" or self.modo_dialogo == "sem_preparo":
                            self.fechar()
                        else:
                            self.parte_dialogo += 1
                            if self.modo_dialogo == "primeira_aparicao":
                                self._avancar_dialogo_primeira_aparicao()
                            elif self.modo_dialogo == "pre_corrida":
                                self._avancar_dialogo_pre_corrida()
                            elif self.modo_dialogo == "fim_corrida":
                                self._avancar_dialogo_fim_corrida()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                    return "processado"
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    if self.modo_dialogo == "corrida":
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        self.opcao_corrida_selecionada = (self.opcao_corrida_selecionada - 1) % (len(corridas_disponiveis) + 1)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    if self.modo_dialogo == "corrida":
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        self.opcao_corrida_selecionada = (self.opcao_corrida_selecionada + 1) % (len(corridas_disponiveis) + 1)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.modo_dialogo == "corrida":
                    # Processar clique no menu de corridas (similar ao teclado)
                    corridas_disponiveis = self.obter_corridas_disponiveis()
                    mouse_x, mouse_y = ev.pos
                    # Verificar se clicou em alguma opção do menu
                    from config import LARGURA, ALTURA
                    caixa_largura = 1000
                    caixa_altura = 200
                    caixa_x = (LARGURA - caixa_largura) // 2
                    caixa_y = ALTURA - caixa_altura - 50
                    menu_largura = 600
                    menu_altura = (len(corridas_disponiveis) + 1) * 50 + 20
                    menu_x = (LARGURA - menu_largura) // 2
                    menu_y = caixa_y - menu_altura - 30
                    
                    if menu_x <= mouse_x <= menu_x + menu_largura and menu_y <= mouse_y <= menu_y + menu_altura:
                        opcao_clicada = (mouse_y - menu_y - 10) // 50
                        if 0 <= opcao_clicada < len(corridas_disponiveis) + 1:
                            self.opcao_corrida_selecionada = opcao_clicada
                            if opcao_clicada < len(corridas_disponiveis):
                                corrida = corridas_disponiveis[opcao_clicada]
                                self.fechar()
                                return {
                                    "corrida": True,
                                    "pista": corrida["pista"],
                                    "tipo": "desafio_touge",
                                    "nome": corrida["nome"],
                                    "race_id": corrida.get("race_id", "mountain_test"),
                                    "voltas": 1,
                                    "dificuldade": corrida.get("dificuldade", "medio"),
                                    "sem_bots": False
                                }
                            else:
                                self.fechar()
                                return "fechado"
                elif len(self.texto_exibido) < len(self.texto_completo):
                    self._completar_animacao_texto()
                else:
                    if self.modo_dialogo == "requisito_pneu" or self.modo_dialogo == "sem_preparo":
                        self.fechar()
                    else:
                        self.parte_dialogo += 1
                        if self.modo_dialogo == "primeira_aparicao":
                            self._avancar_dialogo_primeira_aparicao()
                        elif self.modo_dialogo == "pre_corrida":
                            self._avancar_dialogo_pre_corrida()
                        elif self.modo_dialogo == "fim_corrida":
                            self._avancar_dialogo_fim_corrida()
                        elif self.modo_dialogo == "com_preparo":
                            self._avancar_dialogo_com_preparo()
                return "processado"
            elif ev.type == pygame.JOYBUTTONDOWN:
                from core.gamepad_manager import gerenciador_gamepad
                tipo_controle = "generic"
                if ev.joy < len(gerenciador_gamepad.joysticks):
                    tipo_controle = gerenciador_gamepad._detectar_tipo_controle(ev.joy)
                
                botao_confirmar = (ev.button == 0)
                botao_pausa = False
                if tipo_controle == "xbox":
                    botao_pausa = (ev.button == 6 or ev.button == 7)
                elif tipo_controle in ["ps5", "ps4"]:
                    botao_pausa = (ev.button == 6 or ev.button == 8 or ev.button == 9)
                else:
                    botao_pausa = (ev.button == 6)
                
                if botao_confirmar:
                    if self.modo_dialogo == "corrida":
                        corridas_disponiveis = self.obter_corridas_disponiveis()
                        if self.opcao_corrida_selecionada < len(corridas_disponiveis):
                            corrida = corridas_disponiveis[self.opcao_corrida_selecionada]
                            self.fechar()
                            return {
                                "corrida": True,
                                "pista": corrida["pista"],
                                "tipo": "desafio_touge",
                                "nome": corrida["nome"],
                                "race_id": corrida.get("race_id", "mountain_test"),
                                "voltas": 1,
                                "dificuldade": corrida.get("dificuldade", "medio"),
                                "sem_bots": False
                            }
                        elif self.opcao_corrida_selecionada == len(corridas_disponiveis):
                            self.fechar()
                            return "fechado"
                    elif len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        if self.modo_dialogo == "requisito_pneu" or self.modo_dialogo == "sem_preparo":
                            self.fechar()
                        else:
                            self.parte_dialogo += 1
                            if self.modo_dialogo == "primeira_aparicao":
                                self._avancar_dialogo_primeira_aparicao()
                            elif self.modo_dialogo == "pre_corrida":
                                self._avancar_dialogo_pre_corrida()
                            elif self.modo_dialogo == "fim_corrida":
                                self._avancar_dialogo_fim_corrida()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                    return "processado"
                elif botao_pausa:
                    if self.modo_dialogo == "corrida":
                        self.fechar()
                        return "fechado"
                    elif len(self.texto_exibido) < len(self.texto_completo):
                        self._completar_animacao_texto()
                    else:
                        if self.modo_dialogo == "requisito_pneu" or self.modo_dialogo == "sem_preparo":
                            self.fechar()
                        else:
                            self.parte_dialogo += 1
                            if self.modo_dialogo == "primeira_aparicao":
                                self._avancar_dialogo_primeira_aparicao()
                            elif self.modo_dialogo == "pre_corrida":
                                self._avancar_dialogo_pre_corrida()
                            elif self.modo_dialogo == "fim_corrida":
                                self._avancar_dialogo_fim_corrida()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                            elif self.modo_dialogo == "com_preparo":
                                self._avancar_dialogo_com_preparo()
                    return "processado"
        
        return None
    
    def atualizar(self, dt):
        """Atualiza o estado da Akira"""
        if not self.ativo:
            return
        
        self._atualizar_animacao_texto(dt)
    
    def desenhar_dialogo(self, tela, dt):
        """Desenha o diálogo da Akira"""
        if not self.ativo:
            return
        
        # Garantir que os sprites estão carregados
        if not self.sprites_carregados:
            self.carregar_sprites()
        
        render_text = _get_render_text()
        
        sprite_fundo_atual = None
        if self.modo_dialogo == "primeira_aparicao":
            # Para primeira aparição, o fundo do território já foi desenhado pelo hub_territorio
            # Apenas adicionar overlay semi-transparente
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
        elif self.modo_dialogo == "sem_preparo":
            # Para sem_preparo, o fundo do território já foi desenhado pelo hub_territorio
            # Apenas adicionar overlay semi-transparente
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
        elif self.modo_dialogo == "com_preparo":
            # Para com_preparo, o fundo do território já foi desenhado pelo hub_territorio
            # Apenas adicionar overlay semi-transparente
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
        elif self.modo_dialogo == "corrida":
            # Para corrida, o fundo do território já foi desenhado pelo hub_territorio
            # Apenas adicionar overlay semi-transparente
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            tela.blit(overlay, (0, 0))
        elif self.modo_dialogo == "pre_corrida":
            sprite_fundo_atual = self.sprite_fundo_pre
        elif self.modo_dialogo == "fim_corrida":
            sprite_fundo_atual = self.sprite_fundo_fim
        
        if sprite_fundo_atual:
            tela.blit(sprite_fundo_atual, (0, 0))
        
        # Garantir que sprite_atual está definido (fallback para sprite_neutro se None)
        if not self.sprite_atual and self.sprite_neutro:
            self.sprite_atual = self.sprite_neutro
        
        if self.sprite_atual:
            try:
                # Usar cache de sprite redimensionado (igual ao Boris e outros NPCs)
                if self.sprite_atual not in self.sprites_redimensionados_cache:
                    sprite_original_w = self.sprite_atual.get_width()
                    sprite_original_h = self.sprite_atual.get_height()
                    
                    if sprite_original_w > 0 and sprite_original_h > 0:
                        # Tamanho máximo igual ao Barão e Crank
                        sprite_altura_max = 400
                        sprite_largura_max = 350
                        
                        # Calcular escala mantendo proporção
                        escala_w = sprite_largura_max / sprite_original_w if sprite_original_w > 0 else 1.0
                        escala_h = sprite_altura_max / sprite_original_h if sprite_original_h > 0 else 1.0
                        escala = min(escala_w, escala_h, 1.0)  # Não aumentar além do original
                        
                        sprite_novo_w = int(sprite_original_w * escala)
                        sprite_novo_h = int(sprite_original_h * escala)
                        self.sprites_redimensionados_cache[self.sprite_atual] = pygame.transform.scale(self.sprite_atual, (sprite_novo_w, sprite_novo_h))
                    else:
                        print(f"[AKIRA] AVISO: Sprite tem dimensões inválidas: {sprite_original_w}x{sprite_original_h}")
                        return
                
                sprite_redimensionado = self.sprites_redimensionados_cache.get(self.sprite_atual)
                if sprite_redimensionado:
                    sprite_novo_w, sprite_novo_h = sprite_redimensionado.get_size()
                    
                    sprite_x = LARGURA // 2 - sprite_novo_w // 2
                    if self.modo_dialogo == "fim_corrida":
                        sprite_y = ALTURA // 2 - sprite_novo_h // 2 + 50
                    else:
                        # Posicionar acima da caixa de diálogo (igual ao Boris)
                        sprite_y = ALTURA - sprite_novo_h - 130
                    tela.blit(sprite_redimensionado, (sprite_x, sprite_y))
            except Exception as e:
                print(f"[AKIRA] ERRO ao desenhar sprite: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[AKIRA] AVISO: sprite_atual é None, não pode desenhar")
        
        # Desenhar menu de corridas se estiver no modo corrida
        if self.modo_dialogo == "corrida":
            # Caixa de diálogo com texto da Akira
            texto_akira = "Minhas pistas testam técnica e controle. Escolha uma corrida para testar suas habilidades."
            
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
            nome_display = "AKIRA" if getattr(self, 'nome_revelado', False) else "???"
            nome_texto = render_text(nome_display, 20, (200, 100, 150), bold=True, pixel_style=True)
            tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
            
            # Quebrar texto em linhas
            palavras = texto_akira.split(' ')
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
                cor = (255, 200, 100) if i == self.opcao_corrida_selecionada else (200, 200, 200)
                # Akira não cobra nada - mostrar apenas o nome da corrida
                if i < len(corridas_disponiveis):
                    texto_opcao = f"{opcao} - GRÁTIS"
                else:
                    texto_opcao = opcao
                
                texto_surf = render_text(texto_opcao, 28, cor, bold=True, pixel_style=True)
                x_opcao = menu_x + 20
                y_opcao = menu_y + 10 + i * 50
                tela.blit(texto_surf, (x_opcao, y_opcao))
        else:
            # Desenhar caixa de diálogo normal para outros modos
            caixa_largura = 1000
            caixa_altura = 200
            caixa_x = (LARGURA - caixa_largura) // 2
            caixa_y = ALTURA - caixa_altura - 50
            
            caixa_fundo = pygame.Surface((caixa_largura, caixa_altura), pygame.SRCALPHA)
            caixa_fundo.fill((0, 0, 0, 220))
            tela.blit(caixa_fundo, (caixa_x, caixa_y))
            pygame.draw.rect(tela, (255, 255, 255), (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)
            
            nome_display = "???" if not getattr(self, 'nome_revelado', False) else "AKIRA"
            nome_texto = render_text(nome_display, 24, (200, 100, 150), bold=True, pixel_style=True)
            tela.blit(nome_texto, (caixa_x + 20, caixa_y + 10))
            
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
    
    def fechar(self):
        """Fecha o diálogo da Akira"""
        self.ativo = False
        
        if self.modo_dialogo == "pre_corrida":
            pista_key = str(self.numero_pista_atual)
            if not hasattr(self, 'dialogos_pre_corrida_mostrados'):
                self.dialogos_pre_corrida_mostrados = {}
            self.dialogos_pre_corrida_mostrados[pista_key] = True
            self.salvar_estado()
        
        self.modo_dialogo = None

# Instância global
akira = Akira()

