# src/core/mapa_locations.py
"""
Sistema de Estados de Localizações no Mapa
Gerencia estados: invisível, bloqueado_visível, desbloqueado
"""
import json
import os
from typing import Dict, Optional, List
from config import DIR_PROJETO

CAMINHO_LOCATIONS = os.path.join(DIR_PROJETO, "data", "mapa_locations.json")

class EstadoLocalizacao:
    """Estados possíveis de uma localização"""
    INVISIVEL = "locked_hidden"  # Não aparece no mapa
    BLOQUEADO_VISIVEL = "locked_visible"  # Aparece com cadeado
    DESBLOQUEADO = "unlocked"  # Acessível

class GerenciadorLocalizacoes:
    """Gerencia os estados das localizações no mapa"""
    
    def __init__(self):
        self.locations = {}
        self.carregar()
    
    def carregar(self):
        """Carrega as localizações do arquivo JSON"""
        if os.path.exists(CAMINHO_LOCATIONS):
            try:
                with open(CAMINHO_LOCATIONS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for loc in data.get("locations", []):
                        self.locations[loc["id"]] = {
                            "nome": loc.get("nome", loc["id"]),
                            "state": loc.get("state", EstadoLocalizacao.INVISIVEL),
                            "lockedThought": loc.get("lockedThought"),
                            "unlockFlags": loc.get("unlockFlags", [])
                        }
            except Exception as e:
                print(f"Erro ao carregar localizações: {e}")
                import traceback
                traceback.print_exc()
        else:
            # Inicializar com valores padrão
            self._inicializar_padrao()
    
    def _inicializar_padrao(self):
        """Inicializa com valores padrão se o arquivo não existir"""
        self.locations = {
            "oficina": {
                "nome": "Oficina do Crank",
                "state": EstadoLocalizacao.DESBLOQUEADO,
                "lockedThought": None,
                "unlockFlags": []
            },
            "fosso_ferrugem": {
                "nome": "Fosso de Ferrugem",
                "state": EstadoLocalizacao.DESBLOQUEADO,
                "lockedThought": None,
                "unlockFlags": []
            }
        }
        self.salvar()
    
    def salvar(self):
        """Salva as localizações no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(CAMINHO_LOCATIONS), exist_ok=True)
            data = {
                "locations": [
                    {
                        "id": loc_id,
                        "nome": loc_data["nome"],
                        "state": loc_data["state"],
                        "lockedThought": loc_data.get("lockedThought"),
                        "unlockFlags": loc_data.get("unlockFlags", [])
                    }
                    for loc_id, loc_data in self.locations.items()
                ]
            }
            with open(CAMINHO_LOCATIONS, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar localizações: {e}")
    
    def obter_estado(self, location_id: str) -> str:
        """Obtém o estado atual de uma localização"""
        if location_id not in self.locations:
            return EstadoLocalizacao.INVISIVEL
        state = self.locations[location_id]["state"]
        # Garantir que retorna o valor correto do enum
        if state not in [EstadoLocalizacao.INVISIVEL, EstadoLocalizacao.BLOQUEADO_VISIVEL, EstadoLocalizacao.DESBLOQUEADO]:
            return EstadoLocalizacao.INVISIVEL
        return state
    
    def esta_visivel(self, location_id: str) -> bool:
        """Verifica se uma localização está visível no mapa"""
        state = self.obter_estado(location_id)
        return state in [EstadoLocalizacao.BLOQUEADO_VISIVEL, EstadoLocalizacao.DESBLOQUEADO]
    
    def esta_desbloqueado(self, location_id: str) -> bool:
        """Verifica se uma localização está desbloqueada"""
        return self.obter_estado(location_id) == EstadoLocalizacao.DESBLOQUEADO
    
    def obter_mensagem_bloqueado(self, location_id: str) -> Optional[str]:
        """Obtém a mensagem de pensamento quando a localização está bloqueada"""
        if location_id not in self.locations:
            return "Ainda não tenho motivo pra ir até lá..."
        return self.locations[location_id].get("lockedThought")
    
    def tornar_visivel(self, location_id: str):
        """Torna uma localização visível (mas ainda bloqueada)"""
        if location_id not in self.locations:
            # Criar entrada se não existir
            self.locations[location_id] = {
                "nome": location_id.replace("_", " ").title(),
                "state": EstadoLocalizacao.BLOQUEADO_VISIVEL,
                "lockedThought": "Ainda não tenho motivo pra ir até lá...",
                "unlockFlags": []
            }
        else:
            if self.locations[location_id]["state"] == EstadoLocalizacao.INVISIVEL:
                self.locations[location_id]["state"] = EstadoLocalizacao.BLOQUEADO_VISIVEL
        self.salvar()
    
    def desbloquear(self, location_id: str):
        """Desbloqueia uma localização"""
        if location_id not in self.locations:
            # Criar entrada se não existir
            self.locations[location_id] = {
                "nome": location_id.replace("_", " ").title(),
                "state": EstadoLocalizacao.DESBLOQUEADO,
                "lockedThought": None,
                "unlockFlags": []
            }
        else:
            self.locations[location_id]["state"] = EstadoLocalizacao.DESBLOQUEADO
        self.salvar()
    
    def processar_efeito_narrativa(self, effect: str):
        """Processa um efeito da narrativa que pode afetar localizações"""
        # Verificar unlockLocation:
        if effect.startswith("unlockLocation:"):
            location_id = effect.split(":", 1)[1]
            self.desbloquear(location_id)
        
        # Verificar unlockRaceSet: (pode desbloquear localização relacionada)
        elif effect.startswith("unlockRaceSet:"):
            race_set = effect.split(":", 1)[1]
            # Mapear race set para location
            race_to_location = {
                "cinturao_industrial": "cinturao_industrial",
                "montanha": "montanha",
                "circuito_coroa": "circuito_coroa"
            }
            if race_set in race_to_location:
                self.desbloquear(race_to_location[race_set])
        
        # Verificar menções na narrativa (tornar visível)
        # Isso será feito manualmente ou via flags específicas
        elif effect.startswith("mentionLocation:"):
            location_id = effect.split(":", 1)[1]
            self.tornar_visivel(location_id)

# Instância global
gerenciador_localizacoes = GerenciadorLocalizacoes()

