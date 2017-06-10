

class IssueType:

    _types = [
    ]

    def __init__(self, slug, description, related_class, level):
        self.slug = slug
        self.description = description
        self.related_class = related_class
        self.level = level

        IssueType._types.append(self)

    @classmethod
    def choices(cls):
        return [(i.slug, i.description) for i in cls._types]

    @classmethod
    def level_for(cls, slug):
        for i in cls._types:
            if i.slug == slug:
                return i.level

    @classmethod
    def class_for(cls, slug):
        for i in cls._types:
            if i.slug == slug:
                return i.related_class

    @classmethod
    def get_issues_for(cls, related_class):
        issues = []
        for i in cls._types:
            if i.related_class == related_class:
                issues.append(i.slug)
        return issues


def main():
    # Person Related Issues
    IssueType('missing_phone', 'Missing Phone Number', 'person', 'warning')
    IssueType('missing_email', 'Missing Email', 'person', 'warning')
    IssueType('missing_address', 'Missing Postal Address', 'person', 'warning')
    IssueType('missing_photo', 'Missing Photo', 'person', 'warning')

    # Organization Related Issues
    IssueType('no_memberships', 'No Memberships', 'organization', 'error')
    IssueType('unmatched_person', 'Unmatched Person', 'membership', 'warning')

    # Bill Related Issues
    IssueType('no_actions', 'Missing Actions', 'bill', 'error')
    IssueType('no_sponsors', 'Missing Sponsors', 'bill', 'warning')
    IssueType('no_versions', 'Missing Versions', 'bill', 'warning')
    IssueType('unmatched_person_sponsor', 'Sponsor With Unmatched Person',
              'bill', 'warning')
    IssueType('unmatched_org_sponsor', 'Sponsor With Unmatched Organization',
              'bill', 'warning')

    # VoteEvent Related Issues
    IssueType('missing_bill', 'Missing Bill', 'voteevent', 'error')
    IssueType('missing_voters', 'Missing Voters', 'voteevent', 'warning')
    IssueType('missing_counts', 'Missing Counts', 'voteevent', 'error')
    IssueType('bad_counts', 'Bad Counts', 'voteevent', 'warning')
    IssueType('unmatched_voter', 'Unmatched Voter', 'voteevent', 'warning')
