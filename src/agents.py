#!/usr/bin/env python3
"""
Module de gestion des agents et presets pour Verbiage
Permet de définir différents agents avec des prompts système personnalisés
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Agent:
    """Représente un agent avec son prompt système et sa configuration"""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        description: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Union[str, dict]]] = None,
        created_at: str = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools or ["web_search_preview"]
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convertir l'agent en dictionnaire"""
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "description": self.description,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "tools": self.tools,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Agent":
        """Créer un agent à partir d'un dictionnaire"""
        return cls(**data)


class AgentManager:
    """Gestionnaire des agents et presets"""

    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = Path(agents_dir)
        self.agents_dir.mkdir(exist_ok=True)
        self.current_agent: Optional[Agent] = None
        self._create_default_agents()

    def _create_default_agents(self):
        """Créer les agents par défaut s'ils n'existent pas"""
        default_agents = [
            Agent(
                name="assistant",
                system_prompt="Tu es un assistant IA serviable, précis et amical. Réponds de manière claire et concise.",
                description="Assistant général polyvalent",
                temperature=0.7,
                tools=["web_search_preview"],
            ),
            Agent(
                name="developer",
                system_prompt="Tu es un développeur expert en programmation. Fournis du code propre, bien documenté et explique tes solutions étape par étape. Utilise les meilleures pratiques.",
                description="Expert en développement et programmation",
                temperature=0.3,
                tools=["web_search_preview"],
            ),
            Agent(
                name="researcher",
                system_prompt="Tu es un chercheur méticuleux. Fournis des informations précises, cite tes sources et présente des analyses approfondies. Toujours vérifier les faits avec la recherche web.",
                description="Chercheur spécialisé dans l'analyse et la recherche",
                temperature=0.4,
                tools=["web_search_preview"],
            ),
            Agent(
                name="creative",
                system_prompt="Tu es un créatif inspiré. Pense de manière originale, propose des idées innovantes et des solutions créatives. N'hésite pas à sortir des sentiers battus.",
                description="Agent créatif pour brainstorming et idées originales",
                temperature=0.9,
                tools=["web_search_preview"],
            ),
            Agent(
                name="teacher",
                system_prompt="Tu es un professeur pédagogue. Explique les concepts complexes de manière simple, utilise des exemples concrets et adapte ton niveau à ton interlocuteur.",
                description="Enseignant spécialisé dans l'explication pédagogique",
                temperature=0.6,
                tools=["web_search_preview"],
            ),
        ]

        for agent in default_agents:
            agent_file = self.agents_dir / f"{agent.name}.json"
            if not agent_file.exists():
                self.save_agent(agent)

        # Définir l'assistant comme agent par défaut
        self.current_agent = default_agents[0]

    def save_agent(self, agent: Agent) -> None:
        """Sauvegarder un agent"""
        agent_file = self.agents_dir / f"{agent.name}.json"
        with open(agent_file, "w", encoding="utf-8") as f:
            json.dump(agent.to_dict(), f, indent=2, ensure_ascii=False)

    def load_agent(self, name: str) -> Optional[Agent]:
        """Charger un agent par nom"""
        agent_file = self.agents_dir / f"{name}.json"
        if not agent_file.exists():
            return None

        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Agent.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def list_agents(self) -> List[Dict]:
        """Lister tous les agents disponibles"""
        agents = []
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                with open(agent_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                agents.append(
                    {
                        "name": data["name"],
                        "description": data["description"],
                        "temperature": data["temperature"],
                        "tools": data["tools"],
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue

        return sorted(agents, key=lambda x: x["name"])

    def switch_agent(self, name: str) -> bool:
        """Changer d'agent actuel"""
        agent = self.load_agent(name)
        if agent:
            self.current_agent = agent
            return True
        return False

    def create_agent(
        self,
        name: str,
        system_prompt: str,
        description: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: List[str] = None,
    ) -> Agent:
        """Créer un nouvel agent"""
        agent = Agent(
            name=name,
            system_prompt=system_prompt,
            description=description,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
        )
        self.save_agent(agent)
        return agent

    def delete_agent(self, name: str) -> bool:
        """Supprimer un agent"""
        if name in ["assistant"]:  # Protéger l'agent par défaut
            return False

        agent_file = self.agents_dir / f"{name}.json"
        if agent_file.exists():
            agent_file.unlink()
            if self.current_agent and self.current_agent.name == name:
                # Revenir à l'assistant par défaut
                self.current_agent = self.load_agent("assistant")
            return True
        return False

    def get_current_agent(self) -> Optional[Agent]:
        """Obtenir l'agent actuel"""
        return self.current_agent

    def get_system_message(self) -> Optional[Dict[str, str]]:
        """Obtenir le message système pour l'API"""
        if self.current_agent:
            return {"role": "system", "content": self.current_agent.system_prompt}
        return None

    def export_agent(self, name: str, export_path: str) -> bool:
        """Exporter un agent vers un fichier"""
        agent = self.load_agent(name)
        if not agent:
            return False

        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(agent.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def import_agent(self, import_path: str) -> Optional[Agent]:
        """Importer un agent depuis un fichier"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            agent = Agent.from_dict(data)
            self.save_agent(agent)
            return agent
        except Exception:
            return None
