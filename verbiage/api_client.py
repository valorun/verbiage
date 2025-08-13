"""Interface avec l'API OpenRouter pour Verbiage"""

import requests
import json
from .config import config

def build_openrouter_payload(agent_manager, conversation_manager, message: str) -> dict:
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
    
    return {
        "model": config.model,
        "messages": messages,
        "temperature": current_agent.temperature if current_agent else config.temperature,
        "max_tokens": current_agent.max_tokens if current_agent else config.max_tokens,
        "stop": None
    }

def send_with_openrouter(agent_manager, conversation_manager, message: str, session: requests.Session) -> tuple:
    """Envoyer une requête à l'API OpenRouter"""
    payload = build_openrouter_payload(agent_manager, conversation_manager, message)
    
    try:
        response = session.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": config.site_url,
                "X-Title": config.site_name
            },
            json=payload
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        content = response_data['choices'][0]['message']['content']
        # Pour compatibilité temporaire - à simplifier plus tard
        return content, [], []
        
    except Exception as e:
        return f"Erreur OpenRouter: {str(e)}", [], []
