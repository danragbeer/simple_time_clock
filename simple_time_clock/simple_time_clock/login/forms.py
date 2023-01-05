from django import forms
from django.core.exceptions import ValidationError
from sqlalchemy import select

from core import Session
from time_clock.models import Employee


class LoginForm(forms.Form):
    """
    This form is used to validate a user's login information
    (username and password)
    """

    username = forms.CharField(widget=forms.TextInput(), label="Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    def clean(self):
        
        super().clean()

        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        # Below code ensures the user inputted the valid login credentials.
        username_and_password_exists = None
        with Session() as session:
            username_and_password_exists = session.execute(
                select(Employee.employee_id).where(
                    Employee.username == username,
                    Employee.password == password
                )
            ).one_or_none()

        if not username_and_password_exists:
            self.add_error(None, ValidationError("Incorrect username and/or password"))


class RegistrationForm(forms.Form):
    """
    This form captures a user's employee information and submits
    it to the employee table.
    """

    first_name = forms.CharField(widget=forms.TextInput(), label="First Name")
    last_name = forms.CharField(widget=forms.TextInput(), label="Last Name")
    username = forms.CharField(widget=forms.TextInput(), label="Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    def clean(self):
        
        super().clean()

        username = self.cleaned_data["username"]

        # NOTE: We need to make sure usernames are unique.
        #       Below code ensures uniqueness.
        username_exists = None
        with Session() as session:
            username_exists = session.execute(
                select(Employee.employee_id).where(
                    Employee.username == username,
                )
            ).one_or_none()

        if username_exists:
            self.add_error(None, ValidationError("Username taken"))
