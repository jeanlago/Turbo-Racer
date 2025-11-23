# src/core/desafios.py
"""
Sistema de Desafios/Missões
"""
import json
import os
import random
from datetime import datetime, timedelta
from config import DIR_PROJETO

CAMINHO_DESAFIOS = os.path.join(DIR_PROJETO, "data", "desafios.json")

class GerenciadorDesafios:
    """Gerencia desafios diários, semanais e missões por pista"""
    
    def __init__(self):
        self.desafios_diarios = []
        self.desafios_semanais = []
        self.missoes_pista = {}  # {numero_pista: [missoes]}
        self.progresso = {}  # {desafio_id: progresso_atual}
        self.completados = set()  # IDs de desafios completados
        self.ultima_atualizacao_diaria = None
        self.ultima_atualizacao_semanal = None
        self.carregar()
        self.gerar_desafios_se_necessario()
    
    def carregar(self):
        """Carrega desafios do arquivo"""
        if os.path.exists(CAMINHO_DESAFIOS):
            try:
                with open(CAMINHO_DESAFIOS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.desafios_diarios = data.get('desafios_diarios', [])
                    self.desafios_semanais = data.get('desafios_semanais', [])
                    self.missoes_pista = data.get('missoes_pista', {})
                    self.progresso = data.get('progresso', {})
                    self.completados = set(data.get('completados', []))
                    self.ultima_atualizacao_diaria = data.get('ultima_atualizacao_diaria')
                    self.ultima_atualizacao_semanal = data.get('ultima_atualizacao_semanal')
            except Exception as e:
                print(f"Erro ao carregar desafios: {e}")
                self._inicializar_padrao()
        else:
            self._inicializar_padrao()
    
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
        """Salva desafios no arquivo"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_DESAFIOS), exist_ok=True)
            data = {
                'desafios_diarios': self.desafios_diarios,
                'desafios_semanais': self.desafios_semanais,
                'missoes_pista': self.missoes_pista,
                'progresso': self.progresso,
                'completados': list(self.completados),
                'ultima_atualizacao_diaria': self.ultima_atualizacao_diaria,
                'ultima_atualizacao_semanal': self.ultima_atualizacao_semanal
            }
            with open(CAMINHO_DESAFIOS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar desafios: {e}")
    
    def _gerar_desafio_diario(self):
        """Gera um desafio diário aleatório"""
        tipos = [
            {
                "tipo": "completar_corridas",
                "objetivo": random.randint(2, 5),
                "recompensa": random.randint(300, 600),
                "descricao": f"Complete {random.randint(2, 5)} corridas"
            },
            {
                "tipo": "vencer_corridas",
                "objetivo": random.randint(1, 3),
                "recompensa": random.randint(400, 800),
                "descricao": f"Vença {random.randint(1, 3)} corridas em 1º lugar"
            },
            {
                "tipo": "completar_voltas",
                "objetivo": random.randint(10, 20),
                "recompensa": random.randint(250, 500),
                "descricao": f"Complete {random.randint(10, 20)} voltas"
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
                "descricao": f"Use o turbo {random.randint(50, 100)} vezes"
            }
        ]
        desafio = random.choice(tipos)
        desafio["id"] = f"diario_{datetime.now().strftime('%Y%m%d')}_{len(self.desafios_diarios)}"
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
        
        # Verificar desafios diários
        if self.ultima_atualizacao_diaria is None:
            self.ultima_atualizacao_diaria = hoje.isoformat()
            self.desafios_diarios = [self._gerar_desafio_diario() for _ in range(3)]
        else:
            ultima_data = datetime.fromisoformat(self.ultima_atualizacao_diaria).date()
            if hoje > ultima_data:
                self.ultima_atualizacao_diaria = hoje.isoformat()
                self.desafios_diarios = [self._gerar_desafio_diario() for _ in range(3)]
                self.progresso = {k: v for k, v in self.progresso.items() if not k.startswith("diario_")}
        
        # Verificar desafios semanais
        if self.ultima_atualizacao_semanal is None:
            self.ultima_atualizacao_semanal = f"{hoje.year}-W{semana_atual}"
            self.desafios_semanais = [self._gerar_desafio_semanal() for _ in range(2)]
        else:
            ano_semana = self.ultima_atualizacao_semanal.split('-W')
            if len(ano_semana) == 2:
                ano_antigo, semana_antiga = int(ano_semana[0]), int(ano_semana[1])
                if hoje.year > ano_antigo or (hoje.year == ano_antigo and semana_atual > semana_antiga):
                    self.ultima_atualizacao_semanal = f"{hoje.year}-W{semana_atual}"
                    self.desafios_semanais = [self._gerar_desafio_semanal() for _ in range(2)]
                    self.progresso = {k: v for k, v in self.progresso.items() if not k.startswith("semanal_")}
        
        self.salvar()
    
    def atualizar_progresso(self, tipo, quantidade=1, gerenciador_progresso=None):
        """Atualiza o progresso de desafios"""
        recompensas_ganhas = []
        
        # Atualizar desafios diários
        for desafio in self.desafios_diarios:
            if desafio["tipo"] == tipo and desafio["id"] not in self.completados:
                if desafio["id"] not in self.progresso:
                    self.progresso[desafio["id"]] = 0
                self.progresso[desafio["id"]] += quantidade
                
                if self.progresso[desafio["id"]] >= desafio["objetivo"]:
                    self.completados.add(desafio["id"])
                    if gerenciador_progresso:
                        gerenciador_progresso.adicionar_dinheiro(desafio["recompensa"])
                    recompensas_ganhas.append(desafio)
        
        # Atualizar desafios semanais
        for desafio in self.desafios_semanais:
            if desafio["tipo"] == tipo and desafio["id"] not in self.completados:
                if desafio["id"] not in self.progresso:
                    self.progresso[desafio["id"]] = 0
                self.progresso[desafio["id"]] += quantidade
                
                if self.progresso[desafio["id"]] >= desafio["objetivo"]:
                    self.completados.add(desafio["id"])
                    if gerenciador_progresso:
                        gerenciador_progresso.adicionar_dinheiro(desafio["recompensa"])
                    recompensas_ganhas.append(desafio)
        
        # Atualizar missões por pista
        for pista_key, missoes in self.missoes_pista.items():
            for missao in missoes:
                if missao["tipo"] == tipo and missao["id"] not in self.completados:
                    if missao["id"] not in self.progresso:
                        self.progresso[missao["id"]] = 0
                    self.progresso[missao["id"]] += quantidade
                    
                    if self.progresso[missao["id"]] >= missao["objetivo"]:
                        self.completados.add(missao["id"])
                        if gerenciador_progresso:
                            gerenciador_progresso.adicionar_dinheiro(missao["recompensa"])
                        recompensas_ganhas.append(missao)
        
        if recompensas_ganhas:
            self.salvar()
        
        return recompensas_ganhas
    
    def obter_desafios_diarios(self):
        """Retorna desafios diários ativos"""
        return [d for d in self.desafios_diarios if d["id"] not in self.completados]
    
    def obter_desafios_semanais(self):
        """Retorna desafios semanais ativos"""
        return [d for d in self.desafios_semanais if d["id"] not in self.completados]
    
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
        """Obtém o progresso de um desafio"""
        return self.progresso.get(desafio_id, 0)
    
    def esta_completado(self, desafio_id):
        """Verifica se um desafio está completado"""
        return desafio_id in self.completados
    
    def contar_missoes_diarias_concluidas(self):
        """Conta quantas missões diárias foram concluídas (máximo 3)"""
        contador = 0
        for desafio_id in self.completados:
            if desafio_id.startswith("diario_"):
                contador += 1
        return min(contador, 3)  # Máximo de 3 missões diárias

gerenciador_desafios = GerenciadorDesafios()


