from django import forms

from dataquality.models import DataQualityIssue, IssueResolverPatch


class IssueForm(forms.ModelForm):

    class Meta:
        model = DataQualityIssue
        fields = ('jurisdiction', 'issue', 'object_id',
                  'message')


class ResolverForm(forms.ModelForm):

    class Meta:
        model = IssueResolverPatch
        fields = ('jurisdiction', 'object_id', 'category', 'old_value',
                  'new_value', 'note', 'source', 'reporter_name', 'reporter_email')
