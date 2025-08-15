"""Handlers de commande pour Verbiage"""

from verbiage.api_client import send_with_openrouter


def handle_quit(app, command: str) -> bool:
    app.ui.print_warning("Au revoir ! 👋")
    return False


def handle_clear(app, command: str) -> bool:
    app.refresh_display()
    return True


def handle_new(app, command: str) -> bool:
    app.conversation_manager.current_conversation = None
    app.ui.print_success("Nouvelle conversation créée. Tapez votre premier message !")
    app.refresh_display()
    return True


def handle_list(app, command: str) -> bool:
    app.refresh_display()
    conversations = app.conversation_manager.list_conversations()
    app.ui.show_conversations_list(conversations)
    app.ui.wait_for_enter()
    app.refresh_display()
    return True


def handle_load(app, command: str) -> bool:
    parts = command.split()
    if len(parts) != 2:
        app.ui.print_error("Usage: /load <id>")
    else:
        conversation_id = parts[1]
        if app.conversation_manager.load_conversation(conversation_id):
            app.ui.print_success(f"Conversation {conversation_id} chargée !")
            app.ui.display_conversation_history(
                app.conversation_manager.current_conversation
            )
        else:
            app.ui.print_error(f"Conversation {conversation_id} non trouvée.")
    return True


def handle_undo(app, command: str) -> bool:
    if app.conversation_manager.delete_last_message():
        app.ui.print_success("Dernier message supprimé")
    else:
        app.ui.print_error("Aucun message à supprimer")
    app.refresh_display()
    return True


def handle_delete(app, command: str) -> bool:
    parts = command.split()
    if len(parts) != 2:
        app.ui.print_error("Usage: /delete <numéro>")
    else:
        try:
            msg_num = int(parts[1])
            if app.conversation_manager.delete_message(msg_num):
                app.ui.print_success(f"Message #{msg_num} supprimé")
            else:
                app.ui.print_error(f"Impossible de supprimer le message #{msg_num}")
        except ValueError:
            app.ui.print_error("Numéro de message invalide")
    app.refresh_display()
    return True


def handle_edit(app, command: str) -> bool:
    parts = command.split()
    if len(parts) != 2:
        app.ui.print_error("Usage: /edit <numéro>")
        return True

    try:
        msg_num = int(parts[1])
    except ValueError:
        app.ui.print_error("Numéro de message invalide")
        return True

    current_msg = app.conversation_manager.get_message(msg_num)
    if not current_msg:
        app.ui.print_error(f"Message #{msg_num} non trouvé")
        return True

    new_content = app.ui.get_message_edit_input(
        current_msg["content"],
        app.conversation_manager.current_conversation
    )
    if not new_content:
        app.ui.print_info("Modification annulée")
        return True

    # Détection /web
    web_search = new_content.startswith("/web")
    if web_search:
        new_content = new_content[4:].strip()
        if not new_content:
            app.ui.print_error("Usage : /web <votre message>")
            return True

    # Mise à jour du message utilisateur
    if not app.conversation_manager.edit_message(msg_num, new_content):
        app.ui.print_error("Erreur lors de la modification")
        return True

    # Troncature et regénération
    msgs = app.conversation_manager.current_conversation["messages"]
    app.conversation_manager.current_conversation["messages"] = msgs[:msg_num]

    with app.ui.show_processing():
        response_content, tools_used, sources = send_with_openrouter(
            app.agent_manager,
            app.conversation_manager,
            new_content,
            app.client_session,
            web_search=web_search
        )

    app.conversation_manager.add_message(
        "assistant", response_content, tools_used, sources
    )
    app.refresh_display()
    return True


def handle_help(app, command: str) -> bool:
    app.refresh_display()
    app.ui.show_help()
    app.refresh_display()
    return True


def handle_agents(app, command: str) -> bool:
    agents = app.agent_manager.list_agents()
    current = app.agent_manager.get_current_agent()
    app.ui.print_info(f"Agent actuel: {current.name if current else 'Aucun'}")
    app.ui.show_agents_list(agents)
    app.ui.wait_for_enter()
    app.refresh_display()
    return True


def handle_agent(app, command: str) -> bool:
    app.refresh_display()
    parts = command.split()
    if len(parts) != 2:
        app.ui.print_error("Usage: /agent <nom>")
    else:
        agent_name = parts[1]
        if app.agent_manager.switch_agent(agent_name):
            current = app.agent_manager.get_current_agent()
            app.ui.print_success(f"Agent changé: {current.name} - {current.description}")
        else:
            app.ui.print_error(f"Agent '{agent_name}' non trouvé")
    return True


def handle_create_agent(app, command: str) -> bool:
    app.refresh_display()
    agent_data = app.ui.get_agent_creation_input()
    if agent_data:
        try:
            agent = app.agent_manager.create_agent(**agent_data)
            app.ui.print_success(f"Agent '{agent.name}' créé avec succès")
        except Exception as e:
            app.ui.print_error(f"Erreur lors de la création: {e}")
    else:
        app.ui.print_info("Création annulée")
    return True


def handle_raw(app, command: str) -> bool:
    if not app.conversation_manager.current_conversation:
        app.ui.print_error("Aucune conversation active")
        return True

    parts = command.split()
    messages = app.conversation_manager.current_conversation["messages"]
    if not messages:
        app.ui.print_error("Aucun message dans cette conversation")
        return True

    if len(parts) == 1:
        app.ui.print_raw_message(messages[-1]["content"])
        app.ui.wait_for_enter()
        app.refresh_display()
    else:
        try:
            msg_index = int(parts[1])
            if msg_index < 1 or msg_index > len(messages):
                app.ui.print_error(f"Numéro de message invalide. Doit être entre 1 et {len(messages)}")
            else:
                msg = messages[msg_index - 1]
                app.ui.print_raw_message(msg["content"])
                app.ui.wait_for_enter()
                app.refresh_display()
        except ValueError:
            app.ui.print_error("Numéro de message invalide")
    return True


def handle_config(app, command: str) -> bool:
    app.config.print_config(app.ui)
    app.ui.wait_for_enter()
    app.refresh_display()
    return True


def handle_unknown(app, command: str) -> bool:
    app.ui.print_error(f"Commande inconnue: {command}")
    return True
