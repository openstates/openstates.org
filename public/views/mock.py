# Temporary mock data file, to help Olivia build out the views
# before the Django queries are all complete

LEGISLATOR_VOTES = {
    '2018-02-15': [
        {
            'bill_identifier': 'HB 1012',
            'motion_text': 'Read the third time and passed and ordered transmitted to the Senate.',
            'voter_name': 'Olszewski',
            'legislator_vote': 'yes',
            'result': 'pass'
        }
    ],
    '2017-04-11': [
        {
            'bill_identifier': 'HB 6',
            'motion_text': 'Do Concur',
            'voter_name': 'Olszewski',
            'legislator_vote': 'yes',
            'result': 'fail'
        },
        {
            'bill_identifier': 'HB 83',
            'motion_text': 'Passage, Third Reading',
            'voter_name': 'Olszewski',
            'legislator_vote': 'no',
            'result': 'pass'
        }
    ]
}
