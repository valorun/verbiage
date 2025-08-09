#!/usr/bin/env python3
"""
Verbiage - Chat GPT avec outils en terminal
Application principale
"""

import sys

from openai import OpenAI

from agents import AgentManager
from api_utils import (
    extract_sources_from_response,
    extract_text_from_response,
    extract_tools_from_response,
)
from config import config
from conversation import ConversationManager
from ui import VerbiageUI


class VerbiageChat:
    """Application principale de chat GPT avec outils"""

    def refresh_display(self):
        """Effacer et réafficher en-tête, astuces et historique"""
        # effacer l'écran
        self.ui.clear()
        # en-tête agent
        current_agent = self.agent_manager.get_current_agent()
        if current_agent:
            self.ui.print_info(
                f"Agent actuel: {current_agent.name} - {current_agent.description}"
            )
        # astuces saisie
        self.ui.print_info("💡 Ctrl+J pour nouvelle ligne, Enter pour envoyer")
        # historique
        self.ui.display_conversation_history(
            self.conversation_manager.current_conversation
        )

    def __init__(self):
        self.ui = VerbiageUI()
        self.conversation_manager = ConversationManager(config.conversations_dir)
        self.agent_manager = AgentManager()

        # Validation de la configuration
        is_valid, errors = config.validate()
        if not is_valid:
            self.ui.print_error("Erreur de configuration:")
            for error in errors:
                self.ui.print_info(f"  - {error}")
            sys.exit(1)

        self.client = OpenAI(api_key=config.openai_api_key)
        self.available_tools = [{"type": "web_search_preview"}]
        self.debug = config.debug_mode

        # Dictionnaire des handlers de commande
        self.cmd_handlers = {
            "/quit": self._cmd_quit,
            "/clear": self._cmd_clear,
            "/new": self._cmd_new,
            "/list": self._cmd_list,
            "/load": self._cmd_load,
            "/undo": self._cmd_undo,
            "/delete": self._cmd_delete,
            "/edit": self._cmd_edit,
            "/help": self._cmd_help,
            "/agents": self._cmd_agents,
            "/agent": self._cmd_agent,
            "/create-agent": self._cmd_create_agent,
            "/raw": self._cmd_raw,
        }

    def send_message_to_gpt(self, message: str) -> tuple[str, list[str], list[dict]]:
        """Envoyer un message à GPT et obtenir la réponse"""
        if config.use_responses_api:
            try:
                return self._send_with_responses_api(message)
            except Exception as e:
                if self.debug:
                    self.ui.print_warning(f"API responses échouée, fallback: {e}")
                return self._send_with_chat_api(message)
        else:
            return self._send_with_chat_api(message)

    def _build_message_context(self) -> list:
        """Construit le contexte des messages pour les API"""
        messages = []
        system_msg = self.agent_manager.get_system_message()
        if system_msg:
            messages.append(system_msg)

        if self.conversation_manager.current_conversation:
            for msg in self.conversation_manager.current_conversation["messages"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        return messages

    def _get_agent_config(self) -> tuple:
        """Retourne la configuration (temp, tokens) de l'agent ou par défaut"""
        current_agent = self.agent_manager.get_current_agent()
        temperature = current_agent.temperature if current_agent else config.temperature
        max_tokens = current_agent.max_tokens if current_agent else config.max_tokens
        return temperature, max_tokens

    def _send_with_responses_api(
        self, message: str
    ) -> tuple[str, list[str], list[dict]]:
        """Envoyer avec l'API responses.create"""
        # Construire le contexte sous forme de chaîne
        context_messages = []
        messages = self._build_message_context()
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            context_messages.append(f"{role}: {content}")

        # Ajouter le message actuel
        context_messages.append(f"user: {message}")
        full_input = "\n".join(context_messages)

        # Récupérer les outils
        current_agent = self.agent_manager.get_current_agent()
        tools = [
            {"type": tool}
            for tool in (
                current_agent.tools if current_agent else ["web_search_preview"]
            )
        ]

        response = self.client.responses.create(
            model=config.openai_model, tools=tools, input=full_input
        )

        response_content = extract_text_from_response(response)
        tools_used = extract_tools_from_response(response)
        sources = self._extract_sources_from_response(response)
        return response_content, tools_used, sources

    def _send_with_chat_api(self, message: str) -> tuple[str, list[str], list[dict]]:
        """Envoyer avec l'API chat.completions.create standard"""
        try:
            messages = self._build_message_context()
            messages.append({"role": "user", "content": message})

            temperature, max_tokens = self._get_agent_config()

            response = self.client.chat.completions.create(
                model=config.openai_fallback_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            assistant_message = response.choices[0].message
            response_content = assistant_message.content or ""
            tools_used = []
            sources = []

            return response_content, tools_used, sources

        except Exception as e:
            return f"Erreur lors de l'appel à l'API: {str(e)}", [], []

    def _extract_sources_from_response(self, response) -> list[dict]:
        """Extraire les sources/annotations de la réponse"""
        return extract_sources_from_response(response)

    def _cmd_quit(self, command: str) -> bool:
        self.ui.print_warning("Au revoir ! 👋")
        return False

    def _cmd_clear(self, command: str) -> bool:
        self.refresh_display()
        return True

    def _cmd_new(self, command: str) -> bool:
        self.conversation_manager.current_conversation = None
        self.ui.print_success(
            "Nouvelle conversation créée. Tapez votre premier message !"
        )
        self.refresh_display()
        return True

    def _cmd_list(self, command: str) -> bool:
        self.refresh_display()
        conversations = self.conversation_manager.list_conversations()
        self.ui.show_conversations_list(conversations)
        self.ui.wait_for_enter()
        self.refresh_display()
        return True

    def _cmd_load(self, command: str) -> bool:
        parts = command.split()
        if len(parts) != 2:
            self.ui.print_error("Usage: /load <id>")
        else:
            conversation_id = parts[1]
            if self.conversation_manager.load_conversation(conversation_id):
                self.ui.print_success(f"Conversation {conversation_id} chargée !")
                self.ui.display_conversation_history(
                    self.conversation_manager.current_conversation
                )
            else:
                self.ui.print_error(f"Conversation {conversation_id} non trouvée.")
        return True

    def _cmd_undo(self, command: str) -> bool:
        if self.conversation_manager.delete_last_message():
            self.ui.print_success("Dernier message supprimé")
        else:
            self.ui.print_error("Aucun message à supprimer")
        self.refresh_display()
        return True

    def _cmd_delete(self, command: str) -> bool:
        parts = command.split()
        if len(parts) != 2:
            self.ui.print_error("Usage: /delete <numéro>")
        else:
            try:
                msg_num = int(parts[1])
                if self.conversation_manager.delete_message(msg_num):
                    self.ui.print_success(f"Message #{msg_num} supprimé")
                else:
                    self.ui.print_error(
                        f"Impossible de supprimer le message #{msg_num}"
                    )
            except ValueError:
                self.ui.print_error("Numéro de message invalide")
        self.refresh_display()
        return True

    def _cmd_edit(self, command: str) -> bool:
        parts = command.split()
        if len(parts) != 2:
            self.ui.print_error("Usage: /edit <numéro>")
        else:
            try:
                msg_num = int(parts[1])
                current_msg = self.conversation_manager.get_message(msg_num)
                if current_msg:
                    new_content = self.ui.get_message_edit_input(
                        current_msg["content"]
                    )
                    if new_content:
                        if self.conversation_manager.edit_message(
                            msg_num, new_content
                        ):
                            self.ui.print_success(f"Message #{msg_num} modifié")
                            msgs = self.conversation_manager.current_conversation[
                                "messages"
                            ]
                            self.conversation_manager.current_conversation[
                                "messages"
                            ] = msgs[:msg_num]
                            if current_msg["role"] == "user":
                                with self.ui.show_processing():
                                    response_content, tools_used, sources = (
                                        self.send_message_to_gpt(new_content)
                                    )
                                self.conversation_manager.add_message(
                                    "assistant",
                                    response_content,
                                    tools_used,
                                    sources,
                                )
                        else:
                            self.ui.print_error("Erreur lors de la modification")
                    else:
                        self.ui.print_info("Modification annulée")
                else:
                    self.ui.print_error(f"Message #{msg_num} non trouvé")
            except ValueError:
                self.ui.print_error("Numéro de message invalide")
        self.refresh_display()
        return True

    def _cmd_help(self, command: str) -> bool:
        self.refresh_display()
        self.ui.show_help()
        self.refresh_display()
        return True

    def _cmd_agents(self, command: str) -> bool:
        agents = self.agent_manager.list_agents()
        current = self.agent_manager.get_current_agent()
        self.ui.print_info(f"Agent actuel: {current.name if current else 'Aucun'}")
        self.ui.show_agents_list(agents)
        self.ui.wait_for_enter()
        self.refresh_display()
        return True

    def _cmd_agent(self, command: str) -> bool:
        parts = command.split()
        if len(parts) != 2:
            self.ui.print_error("Usage: /agent <nom>")
        else:
            agent_name = parts[1]
            if self.agent_manager.switch_agent(agent_name):
                current = self.agent_manager.get_current_agent()
                self.ui.print_success(
                    f"Agent changé: {current.name} - {current.description}"
                )
            else:
                self.ui.print_error(f"Agent '{agent_name}' non trouvé")
        self.refresh_display()
        return True

    def _cmd_create_agent(self, command: str) -> bool:
        self.refresh_display()
        agent_data = self.ui.get_agent_creation_input()
        if agent_data:
            try:
                agent = self.agent_manager.create_agent(**agent_data)
                self.ui.print_success(f"Agent '{agent.name}' créé avec succès")
            except Exception as e:
                self.ui.print_error(f"Erreur lors de la création: {e}")
        else:
            self.ui.print_info("Création annulée")
        return True

    def _cmd_raw(self, command: str) -> bool:
        if not self.conversation_manager.current_conversation:
            self.ui.print_error("Aucune conversation active")
            return True

        parts = command.split()
        messages = self.conversation_manager.current_conversation["messages"]
        if not messages:
            self.ui.print_error("Aucun message dans cette conversation")
            return True

        if len(parts) == 1:
            self.ui.print_raw_message(messages[-1]["content"])
            self.ui.wait_for_enter()
            self.refresh_display()
        else:
            try:
                msg_index = int(parts[1])
                if msg_index < 1 or msg_index > len(messages):
                    self.ui.print_error(f"Numéro de message invalide. Doit être entre 1 et {len(messages)}")
                else:
                    msg = messages[msg_index - 1]
                    self.ui.print_raw_message(msg["content"])
                    self.ui.wait_for_enter()
                    self.refresh_display()
            except ValueError:
                self.ui.print_error("Numéro de message invalide")
        return True

    def _cmd_unknown(self, command: str) -> bool:
        self.ui.print_error(f"Commande inconnue: {command}")
        return True

    def handle_command(self, command: str) -> bool:
        """Gérer les commandes spéciales. Retourne True si l'application doit continuer"""
        command = command.lower().strip()
        cmd = command.split()[0]  # Premier mot

        handler = self.cmd_handlers.get(cmd, self._cmd_unknown)
        return handler(command)

    def run(self) -> None:
        """Boucle principale de l'application"""
        self.ui.show_welcome()

        # Afficher l'agent actuel
        current_agent = self.agent_manager.get_current_agent()
        if current_agent:
            self.ui.print_info(
                f"Agent actuel: {current_agent.name} - {current_agent.description}"
            )

        while True:
            try:
                # Obtenir l'ID de conversation pour le prompt
                conv_id = None
                if self.conversation_manager.current_conversation:
                    conv_id = self.conversation_manager.current_conversation["id"]

                user_input = self.ui.get_user_input(conv_id)

                if not user_input:
                    continue

                # Gérer les commandes
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break
                    continue

                # Créer une nouvelle conversation si nécessaire
                if not self.conversation_manager.current_conversation:
                    self.conversation_manager.create_new_conversation(user_input)

                # Ajouter le message utilisateur
                self.conversation_manager.add_message("user", user_input)
                self.refresh_display()

                # Obtenir la réponse
                with self.ui.show_processing():
                    response_content, tools_used, sources = self.send_message_to_gpt(
                        user_input
                    )

                # Ajouter la réponse de l'assistant
                self.conversation_manager.add_message(
                    "assistant", response_content, tools_used, sources
                )
                self.refresh_display()

                # Sauvegarder la conversation si activé
                if config.auto_save:
                    self.conversation_manager.save_conversation()

            except KeyboardInterrupt:
                self.ui.print_warning(
                    "\nInterruption détectée. Tapez /quit pour quitter proprement."
                )
            except Exception as e:
                self.ui.print_error(f"Erreur inattendue: {str(e)}")


def main():
    """Point d'entrée de l'application"""
    app = VerbiageChat()
    app.run()


if __name__ == "__main__":
    main()
