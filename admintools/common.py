
ALERT_CHOICES = (
    ('error', 'Error'),
    ('warning', 'Warning'),
)

ISSUE_CHOICES = (
    # Person Related Issues
    # contact_issues
    ('address', 'Missing Postal Address'),
    ('email', 'Missing Email'),
    ('voice', 'Missing Voice Phone'),
    # other_issues
    ('image', 'Missing Photo URL'),

    # Organization Related Issues
    ('org_no_memberships', 'Organization with no memberships'),
    ('unmatched_org_person', 'Organization with Person ID = None'),

    # Vote Events
    ('voteevent_missing_bill', 'Vote Events with no associated bills'),
    ('unmatched_voter', 'Vote Event which has a voter with Person ID == None'),
    ('missing_voters', 'Vote Event without any voters'),
    ('missing_votes', 'Vote Event without yes & no vote counts'),
    ('bad_votes', 'Vote Event with bad vote count'),
)
