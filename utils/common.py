
def jid_to_abbr(j):
    return j.split(':')[-1].split('/')[0]


def abbr_to_jid(abbr):
    if abbr == 'dc':
        return 'ocd-jurisdiction/country:us/district:dc/government'
    elif abbr == 'pr':
        return 'ocd-jurisdiction/country:us/territory:pr/government'
    else:
        return f'ocd-jurisdiction/country:us/state:{abbr}/government'
