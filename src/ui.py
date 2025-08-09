#!/usr/bin/env python3
"""
Module d'interface utilisateur pour Verbiage
Gestion de l'affichage et des interactions utilisateur
"""

from datetime import datetime

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import config


class VerbiageUI:
    """Interface utilisateur pour l'application Verbiage"""

    def __init__(self):
        self.console = Console()
        self.history = InMemoryHistory()
        self.key_bindings = self._setup_key_bindings()

    def clear(self) -> None:
        """Effacer l'écran du terminal"""
        self.console.clear()

    def _setup_key_bindings(self):
        """Configurer les raccourcis clavier"""
        kb = KeyBindings()

        @kb.add("c-j")  # Ctrl+j pour nouvelle ligne
        def _(event):
            """Ctrl+enter pour nouvelle ligne"""
            event.current_buffer.insert_text("\n")

        @kb.add("enter")
        def _(event):
            """Enter pour envoyer le message"""
            buffer = event.current_buffer
            # Si c'est un buffer multi-ligne et qu'il y a déjà du contenu avec des sauts de ligne
            if "\n" in buffer.text and not buffer.text.strip().endswith("\n\n"):
                buffer.insert_text("\n")
            else:
                buffer.validate_and_handle()

        return kb

    def show_welcome(self) -> None:
        """Afficher l'écran d'accueil"""
        self.console.clear()
        welcome_text = """
# 🤖 Verbiage - Chat GPT avec Outils

Bienvenue dans Verbiage ! Votre assistant IA avec accès aux outils web.

**Commandes disponibles :**
- `/new` - Nouvelle conversation
- `/load` - Charger une conversation existante
- `/list` - Lister les conversations
- `/help` - Afficher l'aide
- `/quit` - Quitter l'application
"""

        self.console.print(
            Panel(Markdown(welcome_text), title="Verbiage", border_style="blue")
        )

    def show_conversations_list(self, conversations) -> None:
        """Afficher la liste des conversations"""
        self.clear()
        if not conversations:
            self.console.print("[yellow]Aucune conversation trouvée.[/yellow]")
            return

        table = Table(title="Conversations disponibles")
        table.add_column("ID", style="cyan")
        table.add_column("Titre", style="green")
        table.add_column("Messages", justify="center")
        table.add_column("Créée le", style="dim")

        for conv in conversations:
            created_date = datetime.fromisoformat(conv["created_at"]).strftime(
                "%d/%m/%Y %H:%M"
            )
            table.add_row(
                conv["id"],
                conv["title"][:40] + "..."
                if len(conv["title"]) > 40
                else conv["title"],
                str(conv["message_count"]),
                created_date,
            )

        self.console.print(table)

    def display_message(
        self, role: str, content: str, tools_used=None, sources=None, message_index=None
    ) -> None:
        """Afficher un message dans un panel approprié"""
        tools_used = tools_used or []
        sources = sources or []

        if role == "user":
            # Message utilisateur aligné à droite avec largeur limitée
            max_width = min(60, self.console.size.width // 2)
            title = "👤 Vous"
            if message_index is not None:
                title += f" #{message_index}"

            user_panel = Panel(
                Markdown(content),
                title=title,
                title_align="left",
                border_style="blue",
                padding=(0, 1),
                width=max_width,
            )
            self.console.print(user_panel, justify="right")
        else:
            # Message assistant aligné à gauche
            title = "🤖 Assistant"
            if message_index is not None:
                title += f" #{message_index}"

            assistant_panel = Panel(
                Markdown(content),
                title=title,
                title_align="left",
                border_style="green",
                padding=(0, 1),
            )
            self.console.print(assistant_panel)

            # Afficher les outils utilisés
            if tools_used:
                tools_text = ", ".join(tools_used)
                self.console.print(f"[dim]🔧 Outils utilisés: {tools_text}[/dim]")

            # Afficher les sources/annotations
            if sources:
                self.console.print("[dim]📚 Sources:[/dim]")
                for i, source in enumerate(sources, 1):
                    source_text = Text()
                    source_text.append(f"  [{i}] ", style="dim")
                    source_text.append(f"{source.get('title', 'Source')}", style="link")
                    if source.get("url"):
                        source_text.append(f" - {source['url']}", style="dim blue")
                    self.console.print(source_text)

        self.console.print()

    def display_conversation_history(self, conversation) -> None:
        """Afficher l'historique d'une conversation"""
        # Effacer l'écran avant d'afficher l'historique
        self.clear()
        if not conversation:
            return

        messages = conversation["messages"]
        for i, message in enumerate(messages):
            role = message["role"]
            content = message["content"]
            tools_used = message.get("tools_used", [])
            sources = message.get("sources", [])
            self.display_message(role, content, tools_used, sources, i + 1)

    def show_help(self) -> None:
        """Afficher l'aide et attendre l'entrée pour revenir"""
        self.clear()
        help_text = """
## Commandes disponibles

### Conversations
- `/new` - Créer une nouvelle conversation
- `/load <id>` - Charger une conversation par ID
- `/list` - Lister toutes les conversations

### Messages
- `/undo` - Supprimer le dernier message
- `/edit <n>` - Modifier le message numéro n
- `/delete <n>` - Supprimer le message numéro n

### Agents
- `/agent <name>` - Changer d'agent
- `/agents` - Lister les agents disponibles
- `/create-agent` - Créer un nouvel agent

### Système
- `/config` - Afficher la configuration
- `/quit` - Quitter l'application
- `/help` - Afficher cette aide

## Saisie
- **Ctrl+J** : Nouvelle ligne (mode multi-ligne)
- **Enter** : Envoyer le message

## Utilisation

Tapez votre message pour discuter avec l'assistant IA.
L'assistant peut utiliser des outils comme la recherche web.
        """
        self.console.print(
            Panel(Markdown(help_text), title="Aide", border_style="yellow")
        )
        self.wait_for_enter()

    def get_user_input(self, conversation_id: str | None = None) -> str:
        """Obtenir la saisie utilisateur avec prompt formaté et support multi-ligne"""
        if conversation_id:
            # Convertir YYYYMMDD_HHMMSS en format lisible
            try:
                date_part, time_part = conversation_id.split("_")
                formatted_date = f"{date_part[6:8]}/{date_part[4:6]}/{date_part[:4]}"
                formatted_time = f"{time_part[:2]}:{time_part[2:4]}"
                prompt_text = f"[{formatted_date} {formatted_time}] Votre message: "
            except (ValueError, IndexError):
                prompt_text = f"[{conversation_id}] Votre message: "
        else:
            prompt_text = "Votre message: "

        # Afficher l'aide pour la saisie multi-ligne
        self.console.print(
            "[dim]💡 Ctrl+J pour nouvelle ligne, Enter pour envoyer[/dim]"
        )

        return prompt(
            prompt_text,
            history=self.history,
            key_bindings=self.key_bindings,
            multiline=True,
        ).strip()

    def show_processing(self):
        """Afficher un indicateur de traitement"""
        return self.console.status("[bold green]🤖 Assistant réfléchit...")

    def print_success(self, message: str) -> None:
        """Afficher un message de succès"""
        self.console.print(f"[green]{message}[/green]")

    def print_error(self, message: str) -> None:
        """Afficher un message d'erreur"""
        self.console.print(f"[red]{message}[/red]")

    def print_warning(self, message: str) -> None:
        """Afficher un avertissement"""
        self.console.print(f"[yellow]{message}[/yellow]")

    def print_info(self, message: str) -> None:
        """Afficher une information"""
        self.console.print(message)

    def show_agents_list(self, agents) -> None:
        """Afficher la liste des agents disponibles"""
        self.clear()
        if not agents:
            self.print_warning("Aucun agent trouvé.")
            return

        table = Table(title="Agents disponibles")
        table.add_column("Nom", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Température", justify="center")
        table.add_column("Outils", style="dim")

        for agent in agents:
            table.add_row(
                agent["name"],
                agent["description"][:50] + "..."
                if len(agent["description"]) > 50
                else agent["description"],
                str(agent["temperature"]),
                ", ".join(agent["tools"]),
            )

        self.console.print(table)

    def get_agent_creation_input(self) -> dict:
        """Obtenir les informations pour créer un agent"""
        self.print_info("\n🤖 Création d'un nouvel agent")

        name = prompt("Nom de l'agent: ").strip()
        if not name:
            return None

        description = prompt("Description: ").strip()
        system_prompt = prompt("Prompt système: ", multiline=True).strip()

        if not system_prompt:
            return None

        try:
            temperature = float(
                prompt("Température (0.0-2.0) [0.7]: ").strip() or "0.7"
            )
        except ValueError:
            temperature = 0.7

        return {
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "temperature": temperature,
        }

    def get_message_edit_input(self, current_content: str) -> str:
        """Obtenir le nouveau contenu pour modifier un message"""
        self.print_info("\n✏️  Message actuel:")
        self.print_info(f"[dim]{current_content}[/dim]")
        self.print_info("\n📝 Nouveau contenu (laissez vide pour annuler):")

        return prompt(
            ">> ",
            multiline=True,
            key_bindings=self.key_bindings,
            default=current_content,
        ).strip()

    def print_raw_message(self, content: str) -> None:
        """Afficher le message en brut sans formatage"""
        self.console.clear()
        self.console.print(content)

    def wait_for_enter(self) -> None:
        """Attendre que l'utilisateur appuie sur Entrée"""
        self.console.print("\n[dim]Appuyez sur Entrée pour revenir à la conversation...[/dim]")
        # On utilise prompt_toolkit pour attendre l'entrée sans conflit avec le reste
        prompt("", key_bindings=self.key_bindings)
        # On efface l'écran après l'appui sur Entrée pour éviter le doublon
        self.console.clear()
