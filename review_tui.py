import argparse
import sys
import requests
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def fetch_products(api_url):
    try:
        # We strip any trailing slashes to avoid double slashes in the URL
        api_url = api_url.rstrip('/')
        response = requests.get(f"{api_url}/products")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[bold red]Error fetching products:[/bold red] {e}")
        return []

def display_products(products):
    table = Table(title="Pending Product Reviews")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Content", style="white")
    table.add_column("Status", style="green")

    for p in products:
        table.add_row(str(p["id"]), p["text_content"], p["status"])
    
    console.print(table)

def submit_feedback(api_url, product_id, action, correction=None):
    api_url = api_url.rstrip('/')
    # Aligned with our API: status updates and text updates
    payload = {}
    if action == "approve":
        payload["status"] = "approved"
    elif action == "correct":
        payload["status"] = "corrected"
        payload["text_content"] = correction
    
    try:
        # Updated URL to match @app.post("/products/{product_id}")
        res = requests.post(f"{api_url}/products/{product_id}", json=payload)
        res.raise_for_status()
        console.print("[bold green]Success![/bold green] Database updated.")
    except Exception as e:
        console.print(f"[bold red]Failed to submit:[/bold red] {e}")

def handle_selection(api_url, items, choice):
    it = next((item for item in items if str(item["id"]) == choice), None)
    if not it:
        console.print("[red]Invalid ID.[/red]")
        return

    console.print(Panel(f"Selected: [bold]{it['text_content']}[/bold]"))
    action = Prompt.ask("Action", choices=["a", "c", "s"], default="s")
    
    if action == "a":
        submit_feedback(api_url, it['id'], "approve")
    elif action == "c":
        correction = Prompt.ask("Enter the corrected text")
        submit_feedback(api_url, it['id'], "correct", correction)
    else:
        console.print("Skipped.")

def review_loop(api_url):
    console.print(Panel("[bold cyan]AI Product Reviewer TUI[/bold cyan]\nType 'l' to list, 'q' to quit"))
    while True:
        cmd = Prompt.ask("\n[bold yellow]Command[/bold yellow] (l/q)").lower().strip()
        
        if cmd in ("q", "quit"):
            break
        elif cmd == "l":
            items = fetch_products(api_url)
            if items:
                display_products(items)
                choice = Prompt.ask("Enter [bold white]ID[/bold white] to review (or press Enter to skip)")
                if choice:
                    handle_selection(api_url, items, choice)
            else:
                console.print("[yellow]No products found in database.[/yellow]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 127.0.0.1 is the most reliable way for local scripts to talk in Codespaces
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="API URL")
    args = parser.parse_args()
    
    review_loop(args.api)