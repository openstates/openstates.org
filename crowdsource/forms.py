from django import forms

from .models import CrowdSourceIssue, CrowdSourceIssueResolver

class IssueForm(forms.ModelForm):

    class Meta:
        model = CrowdSourceIssue
        fields = ('jurisdiction', 'issue', 'object_id', 
                  'reporter_name','reporter_email','message')

class ResolverForm(forms.ModelForm):

    class Meta:
        model = CrowdSourceIssueResolver
        fields = ('issue', 'new_value', 'note', 'source', 
                  'reporter_name', 'reporter_email')
