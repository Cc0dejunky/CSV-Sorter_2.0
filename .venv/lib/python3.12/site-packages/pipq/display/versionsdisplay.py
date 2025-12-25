from rich import print as Print

def Current_VersionPrint(current_version, version_data):
    pre_release_versions = version_data.find_all("div",class_='release',limit=3)
    old_versions = current_version.find_next_siblings('div', limit = 2)
    Print("[bold white]⤷  Current Version:[/bold white]")
    Print("	[bold green]{0:15}[/bold green]{1:15}".format(current_version.find(class_="release__version").text.replace("\n","").strip(),current_version.find('time').text.replace("\n","").strip()))
    Print("[bold white]" + "⤷  Pre-Releases:" +"[/bold white]")
    for x in pre_release_versions:
        Print("	[bold green]{0:15}[/bold green]{1:15}".format(x.find(class_="release__version").text.replace("\n","").strip().split()[0],x.find('time').text.replace("\n","").strip()))
    Print("[bold white]⤷  Older Versions:[/bold white]")
    for x in old_versions:
        Print("	[bold green]{0:15}[/bold green]{1:15}".format(x.find(class_="release__version").text.replace("\n","").strip(),x.find('time').text.replace("\n","").strip()))

def Current_Latest_VersionPrint(current_version, version_data):
    		pre_release_versions = version_data.find_all("div",class_='release',limit=3)
    		old_versions = current_version.find_next_siblings('div', limit = 2)
    		Print("[bold white]⤷  Current Version:[/bold white]")
    		Print("	[bold green]{0:15}[/bold green]{1:15}".format(current_version.find(class_="release__version").text.replace("\n","").strip(),current_version.find('time').text.replace("\n","").strip()))
    		Print("[bold white]" + "⤷  Pre-Releases:" +"[/bold white]")
    		Print("\t[not italic default]None[/not italic default]")
    		Print("[bold white]⤷  Older Versions:[/bold white]")
    		for x in old_versions:
    			Print("	[bold green]{0:15}[/bold green]{1:15}".format(x.find(class_="release__version").text.replace("\n","").strip(),x.find('time').text.replace("\n","").strip()))

def All_VersionPrint(entries,rel_ver,rel_date):
    for i in range(entries):
        tags = ""
        cver = str(rel_ver[i].text.strip().replace("\n","")).strip()
        if " " in cver:
            tags = cver.split()
            cver = tags.pop(0)
            tags = " ".join(tags)
        cdate = rel_date[i].find('time').text.strip().replace("\n","")
        data = "[bold green] ⤷ {0:20}[/bold green][bold]{1:20}[/bold][bold red]{2:10}[/bold red]"
        data = data.format(cver, cdate, tags)
        Print(data)