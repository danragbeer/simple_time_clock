from django.shortcuts import redirect, render
from sqlalchemy import insert, select

from core import Session
from time_clock.models import Employee
from .forms import LoginForm, RegistrationForm


def login(request):
    """
    This view renders a login page for the user.

    Args:

        request (WSGIRequest): Request object of Django

    Returns:
        HttpResponse: Redirects user to the time clock page if
                      login was successful, or renders login page 
                      again with errors if login was unsuccessful.
    """

    context = {"form": LoginForm()}

    if request.method == "POST":
        # Initialize login form with data posted to the view
        form = LoginForm(request.POST)
        
        # If form is not valid, (i.e. username and password don't exist in employee table)
        # then return the form with errors
        if not form.is_valid():
            context.update(form=form)
            return render(request, "login/login.html", context=context)

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        employee_id = None
        with Session() as session:
            employee_id, employee_name = session.execute(
                select(
                    Employee.employee_id,
                    (Employee.first_name + " " + Employee.last_name).label("employee_name")
                ).where(
                    Employee.username == username,
                    Employee.password == password,
                )
            ).first()
        
        # NOTE: When the login is successful, it's beneficial to store the 
        #       employee_id & employee_name in the request.session object, b/c
        #       those are fields that will be needed throughout the application.
        # Below code adds the employee_id and employee name to the request.session
        # object so we can access them throughout the application.
        request.session["employee_id"] = employee_id
        request.session["employee_name"] = employee_name
        
        return redirect("time_clock")

    return render(request, "login/login.html", context=context)


def register(request):
    """
    This view renders a registration page for the user.

    Args:

        request (WSGIRequest): Request object of Django

    Returns:
        HttpResponse: If the registration is successful 
                      redirects user to the login page
                      where they will be able to use 
                      registered username and password
                      to login.
                      If registration is unsuccessful,
                      renders the registration page again
                      with errors.
    """

    context = {"form": RegistrationForm()}

    if request.method == "POST":
        # Initialize registration form with data posted to the view.
        form = RegistrationForm(request.POST)
        
        # If the form is not valid, (i.e a username is taken), 
        # return the form with errors.
        if not form.is_valid():
            context.update(form=form)
            return render(request, "login/register.html", context=context)

        # insert registration data into the employee table
        with Session.begin() as session:
            session.execute(
                insert(Employee).values(**form.cleaned_data)
            )
        
        return redirect("login")

    return render(request, "login/register.html", context=context)


def logout(request):
    """
    This view logs a user out and clears their session
    data.

    Args:

        request (WSGIRequest): Request object of Django

    Returns:
        HttpResponse: Redirect user to the login page.
    """


    # Deletes the current session data from the session and deletes the session cookie. 
    # This is used if you want to ensure that the previous session data can’t be accessed 
    # again from the user’s browser 
    request.session.flush()

    return redirect("login")
