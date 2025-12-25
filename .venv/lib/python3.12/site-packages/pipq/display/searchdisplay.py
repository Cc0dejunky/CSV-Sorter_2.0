from rich import print as Print
import rich.table as Table
IGNORE_LIST = ['','UNKNOWN']

def rawSearchPrint(pkglist):
    for pkg in pkglist:
        pkgver = '[green]' +pkg.find(class_='package-snippet__version').text.strip() + '[/green]'
        pkgname = pkg.find(class_='package-snippet__name').text.strip()
        pkgdesc = pkg.find(class_='package-snippet__description').text.strip() if str(pkg.find(class_='package-snippet__description').text.strip()) not in IGNORE_LIST else ' [bold]N/A'
        display ="   ‣{0:30}{1:25}{2}".format(pkgname,pkgver, pkgdesc)
        Print(display)

def SearchPrint(pkglist):
    table = Table.Table()
    table.add_column("Version", style="bold green", width=9)
    table.add_column("Package-Name", style='bold cyan')
    table.add_column("Package-Utility")
    table.add_column("Date", width=12)
    for pkg in pkglist:
        table.add_row(
        str(pkg.find(class_='package-snippet__version').text.strip()),
        str(pkg.find(class_='package-snippet__name').text.strip()),
        str(pkg.find(class_='package-snippet__description').text.strip()) if str(pkg.find(class_='package-snippet__description').text.strip()) not in IGNORE_LIST else ' [bold]N/A',
        str(pkg.find(class_='package-snippet__released').text.strip()),
        )
    Print(table)

def SpacedSearchPrint(pkglist):
    table = Table()
    c = 0
    table.add_column("Version", style="bold green", width=9)
    table.add_column("Package-Name", style='bold cyan')
    table.add_column("Package-Utility")
    table.add_column("Date", width=12)
    lenc = len(pkglist)
    for pkg in pkglist:
        c += 1
        table.add_row(
        str(pkg.find(class_='package-snippet__version').text.strip()),
        str(pkg.find(class_='package-snippet__name').text.strip()),
        str(pkg.find(class_='package-snippet__description').text.strip()) if str(pkg.find(class_='package-snippet__description').text.strip()) not in IGNORE_LIST else ' [bold]N/A',
        str(pkg.find(class_='package-snippet__released').text.strip()),
        )
        if c!=lenc:
            table.add_row("\n","\n","\n")
