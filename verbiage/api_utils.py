#!/usr/bin/env python3
"""
Utilitaires API pour Verbiage - Fonctions d'extraction et de traitement des réponses
"""

from typing import Any, List, Dict


def extract_text_from_response(response: Dict[str, Any]) -> str:
    """Extraire le texte depuis la réponse JSON brute d’OpenRouter."""
    try:
        return response["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError):
        return str(response)


def extract_tools_from_response(response: Dict[str, Any]) -> List[str]:
    """Extraire la liste des outils utilisés depuis la réponse JSON brute."""
    tools = []
    try:
        tool_calls = response["choices"][0]["message"].get("tool_calls", [])
        for tc in tool_calls:
            tools.append(tc["function"]["name"])
    except (KeyError, IndexError):
        pass
    return tools


def extract_sources_from_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extraire les annotations de sources depuis la réponse JSON brute."""
    sources = []
    try:
        message = response["choices"][0]["message"]
        # OpenRouter renvoie les annotations dans le champ "annotations" du message
        for ann in message.get("annotations", []):
            if ann.get("type") == "url_citation":
                sources.append(ann["url_citation"])
    except (KeyError, IndexError):
        pass
    return sources
