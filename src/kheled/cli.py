import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from kheled import Agent, LMStudioClient, registry
import kheled.tools.file_tools  # Registers default log & file tools

console = Console()

def display_welcome(url: str, model: str):
    console.print(
        Panel.fit(
            f"[bold cyan]kheled AI Agent Interface[/bold cyan]\n"
            f"[dim]Connected to LM Studio at {url}[/dim]\n"
            f"[dim]Model: {model}[/dim]\n\n"
            f"Type [bold yellow]/help[/bold yellow] for commands, or [bold yellow]exit[/bold yellow] to quit.",
            border_style="cyan",
        )
    )

def display_help():
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("  [yellow]/reset[/yellow]  - Clear conversation history and reset agent state")
    console.print("  [yellow]/tools[/yellow]  - List all currently registered tools and their schemas")
    console.print("  [yellow]/help[/yellow]   - Show this help menu")
    console.print("  [yellow]exit[/yellow]    - Quit the CLI session\n")

def list_registered_tools():
    schemas = registry.get_schemas()
    console.print(f"\n[bold green]Registered Tools ({len(schemas)}):[/bold green]")
    for schema in schemas:
        fn = schema["function"]
        console.print(f"• [bold cyan]{fn['name']}[/bold cyan]: {fn['description']}")
    console.print()

def run_cli():
    parser = argparse.ArgumentParser(description="kheled: Local Agent CLI")
    parser.add_argument(
        "--url",
        default="http://192.168.178.78:1234/v1",
        help="LM Studio base URL (default: http://192.168.178.78:1234/v1)",
    )
    parser.add_argument(
        "--model",
        # default="qwen2.5-coder-32b-instruct",
        default="mistral-small-3.2-24b-instruct-2506",
        help="Model identifier configured in LM Studio",
    )
    args = parser.parse_args()

    client = LMStudioClient(base_url=args.url, model=args.model)
    agent = Agent(llm=client, registry=registry)

    display_welcome(args.url, args.model)

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]kheled>[/bold green]").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break

            if user_input.startswith("/"):
                cmd = user_input.lower()
                if cmd == "/help":
                    display_help()
                elif cmd == "/reset":
                    agent.messages.clear()
                    console.print("[yellow]Agent conversation history reset.[/yellow]")
                elif cmd == "/tools":
                    list_registered_tools()
                else:
                    console.print(f"[red]Unknown command '{user_input}'. Type /help for options.[/red]")
                continue

            # Execute agent reasoning loop with terminal status indicator
            with console.status("[bold blue]Agent thinking & executing tools...", spinner="dots"):
                response = agent.run(user_input)

            console.print("\n[bold cyan]kheled Response:[/bold cyan]")
            console.print(Panel(response, border_style="blue"))

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Exiting...[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    run_cli()

if __name__ == "__main__":
    main()
