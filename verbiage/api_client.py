"""Interface avec l'API OpenRouter pour Verbiage"""

import requests
import json
from .config import config
from .api_utils import extract_text_from_response, extract_tools_from_response, extract_sources_from_response

def build_openrouter_payload(agent_manager, conversation_manager, message: str, web_search_enabled: bool) -> dict:
    """Construit le payload pour l'API OpenRouter"""
    messages = []
    
    # Message système
    system_msg = agent_manager.get_system_message()
    if system_msg:
        messages.append({"role": "system", "content": system_msg["content"]})
    
    # Historique de conversation
    if conversation_manager.current_conversation:
        for msg in conversation_manager.current_conversation["messages"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Nouveau message utilisateur
    messages.append({"role": "user", "content": message})

    # Configuration de l'agent
    current_agent = agent_manager.get_current_agent()
    
    payload = {
        "model": config.model,
        "messages": messages,
        "temperature": current_agent.temperature if current_agent else config.temperature,
        "max_tokens": current_agent.max_tokens if current_agent else config.max_tokens,
    }
    
    # Ajouter le plugin web seulement si activé
    if web_search_enabled:
        payload["plugins"] = [{"id": "web"}]
    
    return payload

def send_with_openrouter(agent_manager, conversation_manager, message: str, session: requests.Session, web_search_enabled: bool) -> tuple:
    """Envoyer une requête à l'API OpenRouter"""
    payload = build_openrouter_payload(agent_manager, conversation_manager, message, web_search_enabled)
    
    try:
        response = session.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            json=payload
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # Extraire le contenu, les outils et les sources
        content = extract_text_from_response(response_data)
        tools_used = extract_tools_from_response(response_data)
        sources = extract_sources_from_response(response_data)
        
        return content, tools_used, sources
        
    except Exception as e:
        return f"Erreur OpenRouter: {str(e)}", [], []
