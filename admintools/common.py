
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
    ('unmatched_org_person', 'Organization with unmatched person'),

    # Vote Events
    ('voteevent_missing_bill', 'Vote Events with no associated bills'),
    ('unmatched_voter', 'Vote Event which has unmatched voter'),
    ('missing_voters', 'Vote Event without any voters'),
    ('missing_votes', 'Vote Event without yes & no vote counts'),
    ('bad_votes', 'Vote Event with bad vote count'),

    # Bills
    ('no_actions', 'Bill with no action'),
    ('no_sponsors', 'Bill with no sponsor'),
    ('unmatched_person_sponsor', 'Bill has sponsor with unmatched sponsor'),
    ('no_versions', 'Bill with no version'),
    ('unmatched_org_sponsor', 'Bill has sponsor with unmatched organization'),

)
