from typing import Optional
import typer
import rich.table as Table
from rich import print as Print
from .scrape import scrape
from .display import searchdisplay, pkgdisplay, versionsdisplay, display

app = typer.Typer(help="CLI tool for querying python packages. Since `pip search` doesn't work.")

@app.command(help="Search for packages by name")
def search(value: str, space: bool = False, raw: bool = False):
    Print('[dim]' + "Queried: " + '[/ dim]'  + '[bold cyan]'+ value + '[/bold cyan]')
    site  = "https://pypi.org/search/?q="
    link = site + value
    pkglist = scrape.getSearchData(link)
    if raw:
        searchdisplay.rawSearchPrint(pkglist) 
    else:
        if space:
            searchdisplay.SpacedSearchPrint(pkglist)
        else:
            searchdisplay.SearchPrint(pkglist)

@app.command(help="Get info regarding a package")
def pkg(name: str, det:bool = False):
    typer.echo(f"Package search:{name}")
    site = "https://pypi.org/project/"
    link = site + name
    pkg_data = scrape.getPkgData(link)
    try:
        title = pkg_data.find(class_='package-header__name').text.strip()
    except:
        title = "N/A"
    try:
        summary = pkg_data.find(class_="package-description__summary").text.strip()
    except:
        summary = "N/A"
    try:
        install = pkg_data.find(id='pip-command').text.strip()
    except:
        install = "N/A"
    try:
        repo = pkg_data.find(class_="fas fa-home").parent.get("href")
    except:
        repo = "N/A"
    
    version_data = scrape.getPkgData(link + "/#history")
    try:
        latest_version = version_data.find(class_='release release--current').find(class_='release__version').text.strip()
    except:
        latest_version = version_data.find(class_='release release--latest release--current').find(class_='release__version').text.strip()
    pkgdisplay.pkgPrint(title,latest_version,summary,install,repo)

@app.command(help="Get data regarding the version history of the package")
def versions(value: str, all: bool = False):
    link = "https://pypi.org/project/" + value
    version_data = scrape.getPkgData(link + "/#history")
    release_list_web = version_data.find(class_='release-timeline')
    rel_ver = release_list_web.find_all(class_='release__version')
    rel_date = release_list_web.find_all(class_='release__version-date')
    entries = len(rel_ver)
    if all:
        versionsdisplay.All_VersionPrint(entries,rel_ver,rel_date)
    else:
    	Print("[cyan bold]Version history for: [/ cyan bold]{0}".format(value))
    	try:
    		current_version = version_data.find(class_="release release--current");versionsdisplay.Current_VersionPrint(current_version,version_data)
        
    	except:
            current_version = version_data.find(class_="release release--latest release--current")
            versionsdisplay.Current_Latest_VersionPrint(current_version,version_data)

def main():
    app()
