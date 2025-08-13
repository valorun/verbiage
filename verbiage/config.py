#!/usr/bin/env python3
"""
Module de configuration pour Verbiage
Gestion des paramètres via fichier JSON
"""

import json
from pathlib import Path
from platformdirs import user_config_dir


class Config:
    """Classe de configuration pour l'application Verbiage"""

    def __init__(self):
        """Initialiser la configuration"""
        # Répertoire de configuration global
        self.global_config_dir = Path(user_config_dir("verbiage"))
        self.global_config_dir.mkdir(exist_ok=True, parents=True)
        self.config_file = self.global_config_dir / "config.json"
        
        # Créer le fichier config s'il n'existe pas
        if not self.config_file.exists():
            self._create_default_config()
            
        self._config = self._load_config()
        self._validate_dirs()

    def _create_default_config(self):
        """Créer une configuration par défaut"""
        default_config = {
            "api_key": "",
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "conversations_dir": str(self.global_config_dir / "conversations"),
            "agents_dir": str(self.global_config_dir / "agents"),
            "max_tokens": 2048,
            "temperature": 0.7,
            "debug_mode": False,
            "auto_save": True,
            "default_agent": "assistant"
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)

    def _load_config(self) -> dict:
        """Charger la configuration depuis le fichier JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return {}

    def _validate_dirs(self):
        """Valider et créer les répertoires de configuration"""
        Path(self.conversations_dir).mkdir(parents=True, exist_ok=True)
        Path(self.agents_dir).mkdir(parents=True, exist_ok=True)

    @property
    def api_key(self) -> str:
        return self._config.get("api_key", "")

    @property
    def model(self) -> str:
        return self._config.get("model", "deepseek/deepseek-chat-v3-0324:free")

    @property
    def conversations_dir(self) -> str:
        return self._config.get("conversations_dir", str(self.global_config_dir / "conversations"))

    @property
    def agents_dir(self) -> str:
        return self._config.get("agents_dir", str(self.global_config_dir / "agents"))

    @property
    def max_tokens(self) -> int:
        return self._config.get("max_tokens", 2048)

    @property
    def temperature(self) -> float:
        return self._config.get("temperature", 0.7)

    @property
    def debug_mode(self) -> bool:
        return self._config.get("debug_mode", False)

    @property
    def auto_save(self) -> bool:
        return self._config.get("auto_save", True)

    @property
    def default_agent(self) -> str:
        return self._config.get("default_agent", "assistant")

    def validate(self) -> tuple[bool, list[str]]:
        """Valider la configuration"""
        errors = []

        if not self.api_key:
            errors.append("Clé API OpenRouter manquante dans config.json")

        if not Path(self.conversations_dir).exists():
            try:
                Path(self.conversations_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Impossible de créer le répertoire conversations: {e}")

        if self.max_tokens <= 0:
            errors.append("max_tokens doit être supérieur à 0")

        if not 0 <= self.temperature <= 2:
            errors.append("temperature doit être entre 0 et 2")

        return len(errors) == 0, errors

    def print_config(self, ui) -> None:
        """Affiche la configuration via l'UI"""
        ui.print_info("⚙️ Configuration Verbiage")
        ui.print_info(f"Modèle: {self.model}")
        ui.print_info(f"Temperature: {self.temperature}")
        ui.print_info(f"Max tokens: {self.max_tokens}")
        ui.print_info(f"Auto-sauvegarde: {'activée' if self.auto_save else 'désactivée'}")
        ui.print_info(f"Debug mode: {'activé' if self.debug_mode else 'désactivé'}")
        ui.print_info(f"Répertoire conversations: {self.conversations_dir}")
        ui.print_info(f"Répertoire agents: {self.agents_dir}")
        ui.print_info(f"Agent par défaut: {self.default_agent}")


# Instance globale de configuration
config = Config()
