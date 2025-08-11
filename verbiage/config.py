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
            "openai_api_key": "",
            "openai_model": "gpt-4.1-mini",
            "conversations_dir": str(self.global_config_dir / "conversations"),
            "agents_dir": str(self.global_config_dir / "agents"),
            "max_tokens": 2048,
            "temperature": 0.7,
            "use_responses_api": True,
            "debug_mode": False,
            "auto_save": True
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
    def openai_api_key(self) -> str:
        return self._config.get("openai_api_key", "")

    @property
    def openai_model(self) -> str:
        return self._config.get("openai_model", "gpt-4.1")

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
    def use_responses_api(self) -> bool:
        return self._config.get("use_responses_api", True)

    @property
    def debug_mode(self) -> bool:
        return self._config.get("debug_mode", False)

    @property
    def auto_save(self) -> bool:
        return self._config.get("auto_save", True)

    def validate(self) -> tuple[bool, list[str]]:
        """Valider la configuration"""
        errors = []

        if not self.openai_api_key:
            errors.append("openai_api_key non définie dans config.json")

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

    def print_config(self) -> None:
        """Afficher la configuration actuelle (sans la clé API)"""
        print("Configuration Verbiage (config.json):")
        print(f"  Modèle: {self.openai_model}")
        print(f"  Répertoire conversations: {self.conversations_dir}")
        print(f"  Max tokens: {self.max_tokens}")
        print(f"  Température: {self.temperature}")
        print(f"  API responses: {self.use_responses_api}")
        print(f"  Mode debug: {self.debug_mode}")
        print(f"  Sauvegarde auto: {self.auto_save}")
        print("Note: La clé API n'est pas affichée pour des raisons de sécurité.")


# Instance globale de configuration
config = Config()
