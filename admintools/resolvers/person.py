from opencivicdata.core.models import Person, Jurisdiction
from admintools.models import DataQualityIssue, IssueResolverPatch


def create_patch(obj, status, old_value, new_value, category, alert, note,
                 source, reporter_name, reporter_email, applied_by):
    jur = Jurisdiction.objects.filter(
        organizations__memberships__person=obj).first()
    patch = IssueResolverPatch.objects.create(
        content_object=obj,
        jurisdiction=jur,
        status=status,
        old_value=old_value,
        new_value=new_value,
        category=category,
        alert=alert,
        note=note,
        source=source,
        reporter_name=reporter_name,
        reporter_email=reporter_email,
        applied_by=applied_by
    )
    patch.save()


def resolve_person_issues():
    pass
