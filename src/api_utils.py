#!/usr/bin/env python3
"""
Utilitaires API pour Verbiage - Fonctions d'extraction et de traitement des réponses
"""

from typing import Any, List, Dict


def extract_text_from_response(response: Any) -> str:
    """Extraire le texte de manière intelligente depuis différents formats de réponse"""

    # Si c'est déjà une string
    if isinstance(response, str):
        return response

    # Format responses.create
    if hasattr(response, "output") and response.output:
        texts = []
        for output_item in response.output:
            if hasattr(output_item, "content") and output_item.content:
                for content_item in output_item.content:
                    if hasattr(content_item, "text"):
                        texts.append(content_item.text)
        if texts:
            return "\n".join(texts)

    # Format chat.completions
    if hasattr(response, "choices") and response.choices:
        choice = response.choices[0]
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            return choice.message.content or ""

    # Attribut content direct
    if hasattr(response, "content"):
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            texts = []
            for item in response.content:
                if hasattr(item, "text"):
                    texts.append(item.text)
                elif isinstance(item, str):
                    texts.append(item)
            return "\n".join(texts)

    # Fallback vers la représentation string
    return str(response)


def extract_tools_from_response(response: Any) -> List[str]:
    """Extraire la liste des outils utilisés depuis différents formats de réponse"""
    tools_used = []

    # Format responses.create - vérifier l'attribut tools
    if hasattr(response, "tools") and response.tools:
        for tool in response.tools:
            if hasattr(tool, "type"):
                tools_used.append(tool.type)

    # Format chat.completions - tool_calls
    if hasattr(response, "choices") and response.choices:
        choice = response.choices[0]
        if hasattr(choice, "message") and hasattr(choice.message, "tool_calls"):
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    if hasattr(tool_call, "function") and hasattr(
                        tool_call.function, "name"
                    ):
                        tools_used.append(tool_call.function.name)

    return tools_used


def extract_sources_from_response(response: Any) -> List[dict]:
    """Extraire les annotations de sources depuis différents formats de réponse"""
    sources: List[dict] = []
    # Traiter le format responses.create
    if hasattr(response, "output") and response.output:
        for output_item in response.output:
            if hasattr(output_item, "content") and output_item.content:
                for content_item in output_item.content:
                    if (
                        hasattr(content_item, "annotations")
                        and content_item.annotations
                    ):
                        for annotation in content_item.annotations:
                            # annotation peut être un dict ou un objet
                            if isinstance(annotation, dict):
                                sources.append(annotation)
                            else:
                                try:
                                    sources.append(annotation.__dict__)
                                except Exception:
                                    sources.append({"annotation": str(annotation)})
    # On peut étendre pour d'autres formats si nécessaire
    return sources
