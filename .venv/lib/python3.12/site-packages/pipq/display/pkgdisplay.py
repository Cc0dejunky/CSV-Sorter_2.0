from rich import print as Print
from pipq.scrape import scrape

def pkgPrint(title,latest_version,summary,install,repo):
    display = [
        "Package name: [bold cyan]{}[/bold cyan]".format(title),
        "Latest version: [bold green]{}[/bold green]".format(latest_version),
        "Summary: {}".format(summary),
        "Install: {}".format(install),
        "Repository: {}".format(repo)        
    ]
    if "https://github.com" in repo:
           stars, forks = scrape.githubData(repo)
           display.append("Stars: [default bold blue]{0}[/default bold blue] Forks: [default bold blue]{1}[/default bold blue]".format(stars, forks))
    for i in display:
        Print(i)    