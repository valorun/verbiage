#!/usr/bin/env python3
"""
Module de gestion des agents et presets pour Verbiage
Permet de définir différents agents avec des prompts système personnalisés
"""

import json
from datetime import datetime
from pathlib import Path


class Agent:
    """Représente un agent avec son prompt système et sa configuration"""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        description: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: list[str | dict] | None = None,
        created_at: str | None = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools or ["web_search_preview"]
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
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
    def from_dict(cls, data: dict) -> "Agent":
        """Créer un agent à partir d'un dictionnaire"""
        return cls(**data)


class AgentManager:
    """Gestionnaire des agents et presets"""

    def __init__(self, agents_dir: str):
        self.agents_dir = Path(agents_dir)
        self.agents_dir.mkdir(exist_ok=True, parents=True)
        self.current_agent: Agent | None = None

        # Créer les agents par défaut seulement si le dossier est vide
        if not any(self.agents_dir.glob("*.json")):
            self._create_default_agents()

        # Charger l'agent par défaut
        self.switch_agent("assistant")

    def _format_agent_filename(self, name: str) -> str:
        return f"{name.replace(' ', '_').lower()}.json"

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
        ]

        for agent in default_agents:
            self.save_agent(agent)

    def save_agent(self, agent: Agent) -> None:
        """Sauvegarder un agent"""
        agent_file = self.agents_dir / f"{self._format_agent_filename(agent.name)}"
        with open(agent_file, "w", encoding="utf-8") as f:
            json.dump(agent.to_dict(), f, indent=2, ensure_ascii=False)

    def load_agent(self, name: str) -> Agent | None:
        """Charger un agent par nom"""
        agent_file = self.agents_dir / f"{self._format_agent_filename(name)}"
        if not agent_file.exists():
            print(agent_file)
            return None

        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Agent.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def list_agents(self) -> list[dict]:
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
        tools: list[str] | None = None,
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

    def get_current_agent(self) -> Agent | None:
        """Obtenir l'agent actuel"""
        return self.current_agent

    def get_system_message(self) -> dict[str, str] | None:
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

    def import_agent(self, import_path: str) -> Agent | None:
        """Importer un agent depuis un fichier"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            agent = Agent.from_dict(data)
            self.save_agent(agent)
            return agent
        except Exception:
            return None
