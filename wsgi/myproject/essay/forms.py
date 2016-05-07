from django import forms


class DocumentForm(forms.Form):
    train_file = forms.FileField(
            label='Select a train file',
            help_text='xlsx supported'
            )
