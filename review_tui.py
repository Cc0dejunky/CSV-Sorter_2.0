#!/usr/bin/env python3
"""Terminal Review TUI using requests + rich.

Usage: python review_tui.py --api http://localhost:8000

Features:
- List products needing review (GET /products-for-review)
- Display table with id, text, normalized, confidence
- Select an item to approve or submit a correction (POST /submit-feedback)
- Reload model (POST /reload_model)
- Trigger retrain (POST /trigger-retrain)

This TUI uses only `requests` and `rich` so it runs on Windows/WSL easily.
"""
import os 
import argparse
import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

console = Console()


def fetch_products(api_url):
    try:
        r = requests.get(f"{api_url.rstrip('/')}/products-for-review", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        console.print(f"[red]Failed to fetch products: {e}[/red]")
        return []


def display_products(items):
    if not items:
        console.print(Panel("No products need review right now.", title="Products for Review"))
        return

    table = Table(title="Products for Review", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Text", style="white")
    table.add_column("Normalized", style="green")
    table.add_column("Confidence", style="magenta", width=10)

    for it in items:
        table.add_row(str(it.get("id")), it.get("text") or "", str(it.get("normalized") or ""), str(it.get("confidence") or "0.0"))

    console.print(table)


def submit_feedback(api_url, product_id, is_approved, correction=None):
    payload = {
        "product_id": int(product_id),
        "is_approved": bool(is_approved),
    }
    if correction:
        payload["correction"] = str(correction)

    try:
        r = requests.post(f"{api_url.rstrip('/')}/submit-feedback", json=payload, timeout=10)
        r.raise_for_status()
        console.print("[green]Feedback submitted successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to submit feedback: {e}[/red]")


def reload_model(api_url):
    try:
        r = requests.post(f"{api_url.rstrip('/')}/reload_model", timeout=10)
        r.raise_for_status()
        console.print("[green]Model reloaded successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to reload model: {e}[/red]")


def trigger_retrain(api_url):
    try:
        r = requests.post(f"{api_url.rstrip('/')}/trigger-retrain", timeout=10)
        r.raise_for_status()
        console.print("[green]Retrain triggered successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to trigger retrain: {e}[/red]")


def choose_product(items):
    ids = [str(it.get("id")) for it in items]
    choice = Prompt.ask("Enter product ID to review (or blank to go back)")
    if not choice:
        return None
    if choice not in ids:
        console.print("[red]Invalid product ID.[/red]")
        return None
    # return the item
    for it in items:
        if str(it.get("id")) == choice:
            return it
    return None


def review_loop(api_url):
    while True:
        console.print(Panel("Human-in-the-loop Review TUI", style="bold cyan"))
        console.print("Options: [b]l[/b]=list, [b]r[/b]=reload model, [b]t[/b]=trigger retrain, [b]q[/b]=quit")
        cmd = Prompt.ask("Enter command").strip().lower()
        if cmd in ("q", "quit", "exit"):
            console.print("Bye!")
            return
        elif cmd in ("l", "list"):
            items = fetch_products(api_url)
            display_products(items)
            if items:
                it = choose_product(items)
                if it:
                    console.print(Panel(f"Selected product [cyan]{it['id']}[/cyan]\n{textwrap(it['text'])}", title="Review"))
                    action = Prompt.ask("Action: [a]pprove, [c]orrect, [s]kip", choices=["a", "c", "s"], default="s")
                    if action == "a":
                        submit_feedback(api_url, it["id"], True, None)
                    elif action == "c":
                        correction = Prompt.ask("Enter corrected value")
                        submit_feedback(api_url, it["id"], False, correction)
                    else:
                        console.print("Skipped")
        elif cmd in ("r", "reload"):
            reload_model(api_url)
        elif cmd in ("t", "trigger"):
            trigger_retrain(api_url)
        else:
            console.print("Unknown command")


def textwrap(text, width=80):
    if not text:
        return ""
    if len(text) <= width:
        return text
    return text[:width-3] + "..."


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--api", default=os.getenv("API_URL", "http://localhost:8000"), help="Base API URL")
    return p.parse_args()


def main():
    args = parse_args()
    console.print(f"Using API: [blue]{args.api}[/blue]")
    try:
        review_loop(args.api)
    except KeyboardInterrupt:
        console.print("\nExiting.")


if __name__ == "__main__":
    main()
