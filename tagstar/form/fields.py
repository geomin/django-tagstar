from django import forms

class TagsField(forms.CharField):
    """
        Validate the tags
    """
    def __init__(self,*args, **kwargs):
        super(TagsField, self).__init__( *args, **kwargs)

    def clean(self, value):
        value = super(TagsField, self).clean(value)
        value = value.replace(',', ' ').strip().replace('  ', ' ').split(' ')
        value = set([x.strip().lower() for x in value if x.strip()])
        return ",".join(set(value))
