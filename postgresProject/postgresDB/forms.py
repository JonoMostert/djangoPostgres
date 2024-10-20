from django import forms

class CSVUploadForm(forms.Form):
    csv_file1 = forms.FileField(label='Upload Monzo csv file')
    csv_file2 = forms.FileField(label='Upload Amex csv file')
