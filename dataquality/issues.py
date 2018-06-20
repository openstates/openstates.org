

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
    def description_for(cls, slug):
        for i in cls._types:
            if i.slug == slug:
                return i.description

    @classmethod
    def get_issues_for(cls, related_class):
        issues = []
        for i in cls._types:
            if i.related_class == related_class:
                issues.append(i.slug)
        return issues

    @classmethod
    def related_class_choices(cls):
        return list(set([i.related_class for i in cls._types]))


# Person Related Issues
IssueType('missing-phone', 'Missing Phone Number', 'person', 'warning')
IssueType('missing-email', 'Missing Email', 'person', 'warning')
IssueType('missing-address', 'Missing Postal Address', 'person', 'warning')
IssueType('missing-photo', 'Missing Photo', 'person', 'warning')

# Organization Related Issues
IssueType('no-memberships', 'No Memberships', 'organization', 'error')

# Membership Related Issues
IssueType('unmatched-person', 'Unmatched Person', 'membership', 'warning')

# Post Related Issues
IssueType('many-memberships', 'Too Many People', 'post', 'error')
IssueType('few-memberships', 'Too Few people', 'post', 'warning')

# Bill Related Issues
IssueType('no-actions', 'Missing Actions', 'bill', 'error')
IssueType('no-sponsors', 'Missing Sponsors', 'bill', 'warning')
IssueType('no-versions', 'Missing Versions', 'bill', 'warning')
IssueType('unmatched-person-sponsor', 'Sponsor With Unmatched Person',
          'bill', 'warning')
IssueType('unmatched-org-sponsor', 'Sponsor With Unmatched Organization',
          'bill', 'warning')

# VoteEvent Related Issues
IssueType('missing-bill', 'Missing Bill', 'voteevent', 'error')
IssueType('missing-voters', 'Missing Voters', 'voteevent', 'warning')
IssueType('missing-counts', 'Missing Counts', 'voteevent', 'error')
IssueType('bad-counts', 'Bad Counts', 'voteevent', 'warning')
IssueType('unmatched-voter', 'Unmatched Voter', 'voteevent', 'warning')
