#!/usr/bin/env python3
"""
Module de configuration pour Verbiage
Gestion des variables d'environnement et paramètres
"""

import os
from pathlib import Path
from typing import Optional
from platformdirs import user_config_dir


class Config:
    """Classe de configuration pour l'application Verbiage"""

    def __init__(self):
        """Initialiser la configuration"""
        # Répertoire de configuration global
        self.global_config_dir = Path(user_config_dir("verbiage"))
        self.global_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger d'abord le .env global
        self._load_global_env()
        # Puis le .env local (s'il existe)
        self._load_env_file()

    def _load_global_env(self) -> None:
        """Charger .env du répertoire de config global"""
        env_file = self.global_config_dir / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and not os.getenv(key):
                                os.environ[key] = value
            except Exception as e:
                print(f"Erreur lors du chargement du .env global: {e}")

    def _load_env_file(self) -> None:
        """Charger le fichier .env local si présent"""
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and not os.getenv(key):
                                os.environ[key] = value
            except Exception as e:
                print(f"Erreur lors du chargement du fichier .env local: {e}")

    @property
    def openai_api_key(self) -> Optional[str]:
        """Obtenir la clé API OpenAI"""
        return os.getenv("OPENAI_API_KEY")

    @property
    def openai_model(self) -> str:
        """Obtenir le modèle OpenAI à utiliser"""
        return os.getenv("OPENAI_MODEL", "gpt-4.1")

    @property
    def openai_fallback_model(self) -> str:
        """Obtenir le modèle de fallback si l'API responses n'est pas disponible"""
        return os.getenv("OPENAI_FALLBACK_MODEL", "gpt-5-mini")

    def _get_path(self, env_var: str, default: str) -> str:
        """Résoudre un chemin avec priorité à l'env, sinon global"""
        if env_path := os.getenv(env_var):
            return env_path
        path = self.global_config_dir / default
        path.mkdir(exist_ok=True)
        return str(path)

    @property
    def conversations_dir(self) -> str:
        """Obtenir le répertoire des conversations"""
        return self._get_path("CONVERSATIONS_DIR", "conversations")

    @property
    def agents_dir(self) -> str:
        """Obtenir le répertoire des agents"""
        return self._get_path("AGENTS_DIR", "agents")

    @property
    def max_tokens(self) -> int:
        """Obtenir le nombre maximum de tokens"""
        try:
            return int(os.getenv("MAX_TOKENS", "2048"))
        except ValueError:
            return 2048

    @property
    def temperature(self) -> float:
        """Obtenir la température pour la génération"""
        try:
            return float(os.getenv("TEMPERATURE", "0.7"))
        except ValueError:
            return 0.7

    @property
    def use_responses_api(self) -> bool:
        """Déterminer si on doit utiliser l'API responses.create"""
        return os.getenv("USE_RESPONSES_API", "true").lower() in ("true", "1", "yes")

    @property
    def debug_mode(self) -> bool:
        """Vérifier si le mode debug est activé"""
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    @property
    def auto_save(self) -> bool:
        """Vérifier si la sauvegarde automatique est activée"""
        return os.getenv("AUTO_SAVE", "true").lower() in ("true", "1", "yes")

    def validate(self) -> tuple[bool, list[str]]:
        """Valider la configuration"""
        errors = []

        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY non définie")

        if not Path(self.conversations_dir).exists():
            try:
                Path(self.conversations_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Impossible de créer le répertoire conversations: {e}")

        if self.max_tokens <= 0:
            errors.append("MAX_TOKENS doit être supérieur à 0")

        if not 0 <= self.temperature <= 2:
            errors.append("TEMPERATURE doit être entre 0 et 2")

        return len(errors) == 0, errors

    def print_config(self) -> None:
        """Afficher la configuration actuelle (sans la clé API)"""
        print("Configuration Verbiage:")
        print(f"  Modèle: {self.openai_model}")
        print(f"  Modèle fallback: {self.openai_fallback_model}")
        print(f"  Répertoire conversations: {self.conversations_dir}")
        print(f"  Max tokens: {self.max_tokens}")
        print(f"  Température: {self.temperature}")
        print(f"  API responses: {self.use_responses_api}")
        print(f"  Mode debug: {self.debug_mode}")
        print(f"  Sauvegarde auto: {self.auto_save}")
        print("Note: La clé API n'est pas affichée pour des raisons de sécurité.")


# Instance globale de configuration
config = Config()
