from django import forms

from .models import CrowdSourceIssue

class IssueForm(forms.ModelForm):

    class Meta:
        model = CrowdSourceIssue
        fields = ('jurisdiction', 'issue', 'object_id', 
                  'reporter_name','reporter_email','message')
