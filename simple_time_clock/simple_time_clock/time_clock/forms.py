from django import forms


class ShiftDataForm(forms.Form):
    """
    This form is used to capture the shift data. All inputs
    are hidden, because the values will be set via JavaScript.
    """

    employee_id = forms.CharField(widget=forms.HiddenInput())
    shift_action_type = forms.CharField(widget=forms.HiddenInput())
    time = forms.CharField(widget=forms.HiddenInput())
    date = forms.CharField(widget=forms.HiddenInput())
