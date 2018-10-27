import requests
import click


def compare(old, new, prefix):
    prefix_str = '.'.join(prefix)

    if isinstance(old, list):
        if len(old) != len(new):
            click.secho(f'    {prefix_str} lengths differ {len(old)} != {len(new)}', fg='blue')
        if len(old) and len(new):
            compare(old[0], new[0], prefix + ['0'])
    elif isinstance(old, dict):
        for key, value in old.items():
            if key.startswith('+'):
                continue
            if key not in new:
                click.secho(f'    missing key {prefix_str}.{key}', fg='red')
                continue
            compare(value, new[key], prefix + [key])
    else:
        if old != new:
            click.secho(f'    values differ for {prefix_str}: {old} != {new}', fg='yellow')


def api_compare(url):
    old = requests.get('https://openstates.org' + url).json()
    new = requests.get('http://localhost:8000' + url).json()
    compare(old, new, [])


urls = """
/api/v1/bills/?state=ny&chamber=lower&q=widow&updated_since=2018-10-22&search_window=session&apikey=na&sort=last
/api/v1/bills/ny/2017-2018/A%207982A/?apikey=na
/api/v1/bills/nc/2017/HB%20388/?apikey=na
/api/v1/legislators/WYL000100/?apikey=na
/api/v1/legislators/?apikey=na&state=nc
/api/v1/legislators/?apikey=na&state=va&chamber=upper
""".strip().split()

for url in urls:
    print(url)
    api_compare(url)
