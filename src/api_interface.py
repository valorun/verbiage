"""Interface avec l'API OpenAI pour Verbiage"""

from config import config
from api_utils import extract_text_from_response, extract_tools_from_response, extract_sources_from_response

def build_message_context(agent_manager, conversation_manager) -> list:
    """Construit le contexte des messages pour les API"""
    messages = []
    system_msg = agent_manager.get_system_message()
    if system_msg:
        messages.append(system_msg)

    if conversation_manager.current_conversation:
        for msg in conversation_manager.current_conversation["messages"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    return messages

def get_agent_config(agent_manager) -> tuple:
    """Retourne la configuration de l'agent"""
    current_agent = agent_manager.get_current_agent()
    temperature = current_agent.temperature if current_agent else config.temperature
    max_tokens = current_agent.max_tokens if current_agent else config.max_tokens
    return temperature, max_tokens

def send_with_responses_api(client, agent_manager, conversation_manager, message: str) -> tuple:
    """Envoyer avec l'API responses.create"""
    messages = build_message_context(agent_manager, conversation_manager)
    context_messages = [f"{msg['role']}: {msg['content']}" for msg in messages]
    context_messages.append(f"user: {message}")
    full_input = "\n".join(context_messages)

    current_agent = agent_manager.get_current_agent()
    tools = [{"type": tool} for tool in (current_agent.tools if current_agent else ["web_search_preview"])]

    response = client.responses.create(
        model=config.openai_model, 
        tools=tools, 
        input=full_input
    )

    return (
        extract_text_from_response(response),
        extract_tools_from_response(response),
        extract_sources_from_response(response)
    )

def send_with_chat_api(client, agent_manager, conversation_manager, message: str) -> tuple:
    """Envoyer avec l'API chat.completions.create standard"""
    try:
        messages = build_message_context(agent_manager, conversation_manager)
        messages.append({"role": "user", "content": message})
        temperature, max_tokens = get_agent_config(agent_manager)

        response = client.chat.completions.create(
            model=config.openai_fallback_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        assistant_message = response.choices[0].message
        return assistant_message.content or "", [], []

    except Exception as e:
        return f"Erreur lors de l'appel à l'API: {str(e)}", [], []
