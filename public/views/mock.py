# Temporary mock data file, to help Olivia build out the views
# before the Django queries are all complete

LEGISLATOR_VOTES = {
    '2018-02-15': [
        {
            'bill_identifier': 'HB 1012',
            'motion_text': 'Read the third time and passed and ordered transmitted to the Senate.',
            'voter_name': 'Olszewski',
            'legislator_vote': 'yes',
            'counts': {
                'yes': 86,
                'no': 1,
                'other': 0,
                'total': 87
            }
        }
    ],
    '2017-04-11': [
        {
            'bill_identifier': 'HB 6',
            'motion_text': 'Do Concur',
            'voter_name': 'Olszewski',
            'legislator_vote': 'yes',
            'counts': {
                'yes': 50,
                'no': 0,
                'other': 0,
                'total': 50
            }
        },
        {
            'bill_identifier': 'HB 83',
            'motion_text': 'Passage, Third Reading',
            'voter_name': 'Olszewski',
            'legislator_vote': 'no',
            'counts': {
                'yes': 110,
                'no': 4,
                'other': 6,
                'total': 120
            }
        }
    ]
}
