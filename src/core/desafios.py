import json
import os
import random
from datetime import datetime, timedelta
from config import DIR_PROJETO

CAMINHO_DESAFIOS = os.path.join(DIR_PROJETO, "data", "desafios.json")

class GerenciadorDesafios:
    """Gerencia desafios diários, semanais e missões por pista"""
    
    def __init__(self):
        from core.progresso import gerenciador_progresso
        self.gerenciador_progresso = gerenciador_progresso
        self.carregar()
        self.gerar_desafios_se_necessario()
    
    @property
    def desafios_diarios(self):
        """Retorna os desafios diários do progresso.json"""
        return self.gerenciador_progresso.desafios_diarios
    
    @desafios_diarios.setter
    def desafios_diarios(self, value):
        """Define os desafios diários no progresso.json"""
        self.gerenciador_progresso.desafios_diarios = value
        self.gerenciador_progresso.salvar()
    
    @property
    def desafios_semanais(self):
        """Retorna os desafios semanais do progresso.json"""
        return self.gerenciador_progresso.desafios_semanais
    
    @desafios_semanais.setter
    def desafios_semanais(self, value):
        """Define os desafios semanais no progresso.json"""
        self.gerenciador_progresso.desafios_semanais = value
        self.gerenciador_progresso.salvar()
    
    @property
    def missoes_pista(self):
        """Retorna as missões por pista do progresso.json"""
        return self.gerenciador_progresso.missoes_pista
    
    @missoes_pista.setter
    def missoes_pista(self, value):
        """Define as missões por pista no progresso.json"""
        self.gerenciador_progresso.missoes_pista = value
        self.gerenciador_progresso.salvar()
    
    @property
    def progresso(self):
        """Retorna o progresso dos desafios do progresso.json"""
        return self.gerenciador_progresso.desafios_progresso
    
    @progresso.setter
    def progresso(self, value):
        """Define o progresso dos desafios no progresso.json"""
        self.gerenciador_progresso.desafios_progresso = value
        self.gerenciador_progresso.salvar()
    
    @property
    def completados(self):
        """Retorna os desafios completados do progresso.json (sempre como set)"""
        completados = self.gerenciador_progresso.desafios_completados
        # Garantir que sempre retorna um set
        if not isinstance(completados, set):
            completados = set(completados) if completados else set()
            self.gerenciador_progresso.desafios_completados = completados
        return completados
    
    @completados.setter
    def completados(self, value):
        """Define os desafios completados no progresso.json"""
        self.gerenciador_progresso.desafios_completados = value if isinstance(value, set) else set(value) if value else set()
        self.gerenciador_progresso.salvar()
    
    @property
    def ultima_atualizacao_diaria(self):
        """Retorna a última atualização diária do progresso.json"""
        return self.gerenciador_progresso.ultima_atualizacao_diaria
    
    @ultima_atualizacao_diaria.setter
    def ultima_atualizacao_diaria(self, value):
        """Define a última atualização diária no progresso.json"""
        self.gerenciador_progresso.ultima_atualizacao_diaria = value
        self.gerenciador_progresso.salvar()
    
    @property
    def ultima_atualizacao_semanal(self):
        """Retorna a última atualização semanal do progresso.json"""
        return self.gerenciador_progresso.ultima_atualizacao_semanal
    
    @ultima_atualizacao_semanal.setter
    def ultima_atualizacao_semanal(self, value):
        """Define a última atualização semanal no progresso.json"""
        self.gerenciador_progresso.ultima_atualizacao_semanal = value
        self.gerenciador_progresso.salvar()
    
    def carregar(self):
        """Carrega desafios do progresso.json"""
        self._corrigir_ids_duplicados()
    
    def _corrigir_ids_duplicados(self):
        """Corrige IDs duplicados nos desafios diários e semanais"""
        hoje = datetime.now().date()
        data_hoje_str = hoje.strftime('%Y%m%d')
        
        # Corrigir desafios diários
        ids_vistos = {}
        desafios_corrigidos = []
        precisa_salvar = False
        
        for i, desafio in enumerate(self.desafios_diarios):
            desafio_id = desafio.get("id", "")
            if not desafio_id.startswith(f"diario_{data_hoje_str}_") or desafio_id in ids_vistos:
                novo_id = f"diario_{data_hoje_str}_{i}"
                tentativas = 0
                while novo_id in ids_vistos or novo_id in [d.get("id") for d in desafios_corrigidos]:
                    tentativas += 1
                    novo_id = f"diario_{data_hoje_str}_{i + tentativas}"
                
                # Atualizar progresso e completados se o ID antigo existir
                if desafio_id in self.progresso:
                    self.progresso[novo_id] = self.progresso.pop(desafio_id)
                    precisa_salvar = True
                if desafio_id in self.completados:
                    self.completados.discard(desafio_id)
                    # Só adicionar ao completados se o progresso realmente atingiu o objetivo
                    progresso_atual = self.progresso.get(novo_id, 0)
                    if progresso_atual >= desafio.get("objetivo", 0):
                        self.completados.add(novo_id)
                    precisa_salvar = True
                
                desafio = desafio.copy()
                desafio["id"] = novo_id
            ids_vistos[desafio["id"]] = True
            desafios_corrigidos.append(desafio)
        
        if desafios_corrigidos != self.desafios_diarios:
            self.desafios_diarios = desafios_corrigidos
            precisa_salvar = True
        
        # Corrigir desafios semanais
        semana_atual = hoje.isocalendar()[1]
        ano_semana_str = f"{hoje.year}{semana_atual:02d}"
        ids_vistos_semanais = {}
        desafios_semanais_corrigidos = []
        
        for i, desafio in enumerate(self.desafios_semanais):
            desafio_id = desafio.get("id", "")
            if not desafio_id.startswith(f"semanal_{hoje.year}") or desafio_id in ids_vistos_semanais:
                novo_id = f"semanal_{ano_semana_str}_{i}"
                tentativas = 0
                while novo_id in ids_vistos_semanais or novo_id in [d.get("id") for d in desafios_semanais_corrigidos]:
                    tentativas += 1
                    novo_id = f"semanal_{ano_semana_str}_{i + tentativas}"
                
                # Atualizar progresso e completados se o ID antigo existir
                if desafio_id in self.progresso:
                    self.progresso[novo_id] = self.progresso.pop(desafio_id)
                    precisa_salvar = True
                if desafio_id in self.completados:
                    self.completados.discard(desafio_id)
                    # Só adicionar ao completados se o progresso realmente atingiu o objetivo
                    progresso_atual = self.progresso.get(novo_id, 0)
                    if progresso_atual >= desafio.get("objetivo", 0):
                        self.completados.add(novo_id)
                    precisa_salvar = True
                
                desafio = desafio.copy()
                desafio["id"] = novo_id
            ids_vistos_semanais[desafio["id"]] = True
            desafios_semanais_corrigidos.append(desafio)
        
        if desafios_semanais_corrigidos != self.desafios_semanais:
            self.desafios_semanais = desafios_semanais_corrigidos
            precisa_salvar = True
        
        if precisa_salvar:
            self.salvar()
    
    def _inicializar_padrao(self):
        """Inicializa com valores padrão"""
        self.desafios_diarios = []
        self.desafios_semanais = []
        self.missoes_pista = {}
        self.progresso = {}
        self.completados = set()
        self.ultima_atualizacao_diaria = None
        self.ultima_atualizacao_semanal = None
    
    def salvar(self):
        """Salva desafios no progresso.json"""
        self.gerenciador_progresso.salvar()
    
    def _gerar_desafio_diario(self, indice=None):
        """Gera um desafio diário aleatório
        
        Args:
            indice: Índice do desafio (0, 1, 2). Se None, será calculado automaticamente.
        """
        tipos = [
            {
                "tipo": "completar_corridas",
                "objetivo": random.randint(2, 5),
                "recompensa": random.randint(300, 600),
                "descricao": None
            },
            {
                "tipo": "vencer_corridas",
                "objetivo": random.randint(1, 3),
                "recompensa": random.randint(400, 800),
                "descricao": None
            },
            {
                "tipo": "completar_voltas",
                "objetivo": random.randint(10, 20),
                "recompensa": random.randint(250, 500),
                "descricao": None
            },
            {
                "tipo": "estabelecer_recorde",
                "objetivo": 1,
                "recompensa": random.randint(500, 1000),
                "descricao": "Estabeleça um novo recorde"
            },
            {
                "tipo": "usar_turbo",
                "objetivo": random.randint(50, 100),
                "recompensa": random.randint(200, 400),
                "descricao": None
            }
        ]
        desafio = random.choice(tipos).copy()
        
        if desafio["descricao"] is None:
            if desafio["tipo"] == "completar_corridas":
                desafio["descricao"] = f"Complete {desafio['objetivo']} corridas"
            elif desafio["tipo"] == "vencer_corridas":
                desafio["descricao"] = f"Vença {desafio['objetivo']} corridas em 1º lugar"
            elif desafio["tipo"] == "completar_voltas":
                desafio["descricao"] = f"Complete {desafio['objetivo']} voltas"
            elif desafio["tipo"] == "usar_turbo":
                desafio["descricao"] = f"Use o turbo {desafio['objetivo']} vezes"
        
        hoje = datetime.now().date()
        data_hoje_str = hoje.strftime('%Y%m%d')
        if indice is None:
            desafios_hoje = [d for d in self.desafios_diarios if d.get("id", "").startswith(f"diario_{data_hoje_str}_")]
            indice = len(desafios_hoje)
        desafio["id"] = f"diario_{data_hoje_str}_{indice}"
        desafio["progresso"] = 0
        return desafio
    
    def _gerar_desafio_semanal(self):
        """Gera um desafio semanal aleatório"""
        tipos = [
            {
                "tipo": "completar_corridas",
                "objetivo": random.randint(10, 20),
                "recompensa": random.randint(1500, 3000),
                "descricao": f"Complete {random.randint(10, 20)} corridas"
            },
            {
                "tipo": "vencer_corridas",
                "objetivo": random.randint(5, 10),
                "recompensa": random.randint(2000, 4000),
                "descricao": f"Vença {random.randint(5, 10)} corridas em 1º lugar"
            },
            {
                "tipo": "completar_voltas",
                "objetivo": random.randint(50, 100),
                "recompensa": random.randint(1000, 2000),
                "descricao": f"Complete {random.randint(50, 100)} voltas"
            },
            {
                "tipo": "estabelecer_recorde",
                "objetivo": random.randint(3, 5),
                "recompensa": random.randint(2000, 4000),
                "descricao": f"Estabeleça {random.randint(3, 5)} novos recordes"
            }
        ]
        desafio = random.choice(tipos)
        desafio["id"] = f"semanal_{datetime.now().strftime('%Y%W')}_{len(self.desafios_semanais)}"
        desafio["progresso"] = 0
        return desafio
    
    def gerar_desafios_se_necessario(self):
        """Gera novos desafios se necessário"""
        hoje = datetime.now().date()
        semana_atual = hoje.isocalendar()[1]
        data_hoje_str = hoje.strftime('%Y%m%d')
        
        # Verificar desafios diários
        if self.ultima_atualizacao_diaria is None:
            self.ultima_atualizacao_diaria = hoje.isoformat()
            self.desafios_diarios = [self._gerar_desafio_diario(indice=i) for i in range(3)]
            self.completados = {c for c in self.completados if not c.startswith("diario_")}
        else:
            ultima_data = datetime.fromisoformat(self.ultima_atualizacao_diaria).date()
            if hoje > ultima_data:
                self.ultima_atualizacao_diaria = hoje.isoformat()
                self.desafios_diarios = [self._gerar_desafio_diario(indice=i) for i in range(3)]
                self.progresso = {k: v for k, v in self.progresso.items() if not k.startswith("diario_")}
                self.completados = {c for c in self.completados if not c.startswith("diario_")}
        
        # Verificar desafios semanais
        if self.ultima_atualizacao_semanal is None:
            self.ultima_atualizacao_semanal = f"{hoje.year}-W{semana_atual}"
            self.desafios_semanais = [self._gerar_desafio_semanal() for _ in range(2)]
            self.completados = {c for c in self.completados if not c.startswith("semanal_")}
        else:
            ano_semana = self.ultima_atualizacao_semanal.split('-W')
            if len(ano_semana) == 2:
                ano_antigo, semana_antiga = int(ano_semana[0]), int(ano_semana[1])
                if hoje.year > ano_antigo or (hoje.year == ano_antigo and semana_atual > semana_antiga):
                    self.ultima_atualizacao_semanal = f"{hoje.year}-W{semana_atual}"
                    self.desafios_semanais = [self._gerar_desafio_semanal() for _ in range(2)]
                    self.progresso = {k: v for k, v in self.progresso.items() if not k.startswith("semanal_")}
                    self.completados = {c for c in self.completados if not c.startswith("semanal_")}
        
        self.salvar()
    
    def atualizar_progresso(self, tipo, quantidade=1, gerenciador_progresso=None):
        """Atualiza o progresso de desafios"""
        recompensas_ganhas = []
        
        # Atualizar desafios diários
        for desafio in self.desafios_diarios:
            if desafio["tipo"] == tipo and desafio["id"] not in self.completados:
                if desafio["id"] not in self.progresso:
                    self.progresso[desafio["id"]] = 0
                progresso_antes = self.progresso[desafio["id"]]
                self.progresso[desafio["id"]] = min(desafio["objetivo"], self.progresso[desafio["id"]] + quantidade)
                
                if self.progresso[desafio["id"]] >= desafio["objetivo"]:
                    if not isinstance(self.completados, set):
                        self.completados = set(self.completados) if self.completados else set()
                    self.completados.add(desafio["id"])
                    self.salvar()
                    if gerenciador_progresso:
                        gerenciador_progresso.adicionar_dinheiro(desafio["recompensa"])
                    recompensas_ganhas.append(desafio)
        
        # Atualizar desafios semanais
        for desafio in self.desafios_semanais:
            if desafio["tipo"] == tipo and desafio["id"] not in self.completados:
                if desafio["id"] not in self.progresso:
                    self.progresso[desafio["id"]] = 0
                self.progresso[desafio["id"]] = min(desafio["objetivo"], self.progresso[desafio["id"]] + quantidade)
                
                if self.progresso[desafio["id"]] >= desafio["objetivo"]:
                    if not isinstance(self.completados, set):
                        self.completados = set(self.completados) if self.completados else set()
                    self.completados.add(desafio["id"])
                    self.salvar()
                    if gerenciador_progresso:
                        gerenciador_progresso.adicionar_dinheiro(desafio["recompensa"])
                    recompensas_ganhas.append(desafio)
        
        # Atualizar missões por pista
        for pista_key, missoes in self.missoes_pista.items():
            for missao in missoes:
                if missao["tipo"] == tipo and missao["id"] not in self.completados:
                    if missao["id"] not in self.progresso:
                        self.progresso[missao["id"]] = 0
                    self.progresso[missao["id"]] = min(missao["objetivo"], self.progresso[missao["id"]] + quantidade)
                    
                    if self.progresso[missao["id"]] >= missao["objetivo"]:
                        self.completados.add(missao["id"])
                        if gerenciador_progresso:
                            gerenciador_progresso.adicionar_dinheiro(missao["recompensa"])
                        recompensas_ganhas.append(missao)
        
        if recompensas_ganhas:
            self.salvar()
        
        return recompensas_ganhas
    
    def obter_desafios_diarios(self):
        """Retorna todos os desafios diários (incluindo completados)"""
        return self.desafios_diarios
    
    def obter_desafios_semanais(self):
        """Retorna todos os desafios semanais (incluindo completados)"""
        return self.desafios_semanais
    
    def obter_missoes_pista(self, numero_pista):
        """Retorna missões de uma pista específica"""
        pista_key = str(numero_pista)
        if pista_key not in self.missoes_pista:
            self._gerar_missoes_pista(numero_pista)
        return [m for m in self.missoes_pista[pista_key] if m["id"] not in self.completados]
    
    def _gerar_missoes_pista(self, numero_pista):
        """Gera missões para uma pista"""
        pista_key = str(numero_pista)
        if pista_key not in self.missoes_pista:
            self.missoes_pista[pista_key] = []
        
        missoes = [
            {
                "id": f"pista_{pista_key}_vencer",
                "tipo": "vencer_pista",
                "objetivo": 1,
                "recompensa": 500,
                "descricao": f"Vença a pista {numero_pista} em 1º lugar",
                "pista": numero_pista
            },
            {
                "id": f"pista_{pista_key}_recorde",
                "tipo": "estabelecer_recorde",
                "objetivo": 1,
                "recompensa": 800,
                "descricao": f"Estabeleça um recorde na pista {numero_pista}",
                "pista": numero_pista
            },
            {
                "id": f"pista_{pista_key}_sem_colisao",
                "tipo": "completar_sem_colisao",
                "objetivo": 1,
                "recompensa": 600,
                "descricao": f"Complete a pista {numero_pista} sem colisões",
                "pista": numero_pista
            }
        ]
        
        for missao in missoes:
            if missao["id"] not in [m["id"] for m in self.missoes_pista[pista_key]]:
                missao["progresso"] = 0
                self.missoes_pista[pista_key].append(missao)
        
        self.salvar()
    
    def obter_progresso(self, desafio_id):
        """Obtém o progresso de um desafio (limitado ao objetivo)"""
        progresso = self.progresso.get(desafio_id, 0)
        # Encontrar o desafio para obter o objetivo
        for desafio in self.desafios_diarios + self.desafios_semanais:
            if desafio["id"] == desafio_id:
                return min(progresso, desafio["objetivo"])
        # Verificar missões por pista
        for missoes in self.missoes_pista.values():
            for missao in missoes:
                if missao["id"] == desafio_id:
                    return min(progresso, missao["objetivo"])
        return progresso
    
    def esta_completado(self, desafio_id):
        """Verifica se um desafio está completado - verifica tanto o set quanto o progresso"""
        if desafio_id in self.completados:
            progresso_atual = self.obter_progresso(desafio_id)
            for desafio in self.desafios_diarios + self.desafios_semanais:
                if desafio["id"] == desafio_id:
                    objetivo = desafio.get("objetivo", 0)
                    if progresso_atual >= objetivo:
                        return True
                    else:
                        if isinstance(self.completados, set):
                            self.completados.discard(desafio_id)
                        else:
                            self.completados = set(self.completados) if self.completados else set()
                            self.completados.discard(desafio_id)
                        self.salvar()
                        return False
            for missoes in self.missoes_pista.values():
                for missao in missoes:
                    if missao["id"] == desafio_id:
                        objetivo = missao.get("objetivo", 0)
                    if progresso_atual >= objetivo:
                        return True
                    else:
                        if isinstance(self.completados, set):
                            self.completados.discard(desafio_id)
                        else:
                            self.completados = set(self.completados) if self.completados else set()
                            self.completados.discard(desafio_id)
                        self.salvar()
                        return False
            return True
        return False
    
    def contar_missoes_diarias_concluidas(self):
        """Conta quantas missões diárias do dia atual foram concluídas (máximo 3)"""
        hoje = datetime.now().date()
        data_hoje_str = hoje.strftime('%Y%m%d')
        contador = 0
        
        completados_set = self.completados
        if not isinstance(completados_set, set):
            completados_set = set(completados_set) if completados_set else set()
            if completados_set != self.gerenciador_progresso.desafios_completados:
                self.gerenciador_progresso.desafios_completados = completados_set
        
        for desafio in self.desafios_diarios:
            desafio_id = desafio.get("id", "")
            objetivo = desafio.get("objetivo", 0)
            if desafio_id.startswith(f"diario_{data_hoje_str}_"):
                progresso_atual = self.obter_progresso(desafio_id)
                if progresso_atual >= objetivo:
                    if desafio_id in completados_set:
                        contador += 1
                    else:
                        completados_set.add(desafio_id)
                        self.gerenciador_progresso.desafios_completados = completados_set
                        self.salvar()
                        contador += 1
                elif desafio_id in completados_set:
                    completados_set.discard(desafio_id)
                    self.gerenciador_progresso.desafios_completados = completados_set
                    self.salvar()
        
        return min(contador, 3)

gerenciador_desafios = GerenciadorDesafios()


