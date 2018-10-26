import requests

def compare(old, new, prefix):
    prefix_str = '.'.join(prefix)

    if isinstance(old, list):
        if len(old) != len(new):
            print(f'    {prefix_str}{key} lengths differ')
        if len(old):
            compare(old[0], new[0], prefix + ['0'])
    elif isinstance(old, dict):
        for key, value in old.items():
            if key.startswith('+'):
                continue
            if key not in new:
                print(f'    missing key {prefix_str}{key}')
                continue
            compare(value, new[key], prefix + [key])
    else:
        if old != new:
            print(f'    values differ for {prefix_str}: {old} != {new}')


def api_compare(url):
    old = requests.get('https://openstates.org' + url).json()
    new = requests.get('http://localhost:8000' + url).json()
    compare(old, new, [])


urls = """
/api/v1/bills/?state=ny&chamber=lower&q=widow&updated_since=2018-10-22&search_window=session&apikey=na&sort=last
/api/v1/bills/ny/2017-2018/A%207982A/?apikey=na
""".strip().split()

for url in urls:
    print(url)
    api_compare(url)
