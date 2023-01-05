import json

from django.shortcuts import HttpResponse, redirect, render
from django.views.decorators.http import require_POST
from sqlalchemy import insert, select, update, func

from core import Session
from time_clock.forms import ShiftDataForm

from .models import ShiftData, LunchData, BreakData


def time_clock(request):
    """
    This view renders a time clock with actions and
    shift data for employees.

    Args:

        request (WSGIRequest): Request object of Django

    Returns:

        HttpResponse: Renders a time clock, and a table of
                      shift data for the employee.
    """

    # If the user didn't go through the login, they will
    # be redirected to the login page.
    employee_id = request.session.get("employee_id")
    if not employee_id:
        return redirect("login")

    # For the logged in user, query all shift data available
    # to be displayed below the time clock.
    shift_data = None
    with Session() as session:
        shift_data_query = (
            select(
                ShiftData.shift_id,
                func.to_char(ShiftData.start_time, "MM-DD-YYYY HH24:MI:SS").label("shift_start"),
                func.to_char(ShiftData.end_time, "MM-DD-YYYY HH24:MI:SS").label("shift_end"),
                ShiftData.is_active.label("active_shift"),
                func.to_char(LunchData.start_time, "MM-DD-YYYY HH24:MI:SS").label("lunch_start"),
                func.to_char(LunchData.end_time, "MM-DD-YYYY HH24:MI:SS").label("lunch_end"),
                func.to_char(BreakData.start_time, "MM-DD-YYYY HH24:MI:SS").label("break_start"),
                func.to_char(BreakData.end_time, "MM-DD-YYYY HH24:MI:SS").label("break_end"),
            )
            .outerjoin(LunchData, ShiftData.shift_id == LunchData.shift_data_id)
            .outerjoin(BreakData, ShiftData.shift_id == BreakData.shift_data_id)
            .where(ShiftData.employee_id == employee_id)
            .order_by(ShiftData.start_time.desc())
        )

        shift_data = [
            {
                "shift_id": row.shift_id,
                "shift_start": row.shift_start,
                "shift_end": row.shift_end,
                "active_shift": "Yes" if row.active_shift else "No",
                "lunch_start": row.lunch_start,
                "lunch_end": row.lunch_end,
                "break_start": row.break_start,
                "break_end": row.break_end
            }
        for row in session.execute(shift_data_query).mappings()]

    context = {
        "name": request.session.get("employee_name"), # used for greeting meesage
        "form": ShiftDataForm(initial={"employee_id": employee_id}), # employee_id should be hardcoded
        "shift_data": shift_data,   # data needed to display a table
    }
    return render(request, "time_clock/time_clock.html", context=context)


@require_POST
def shift_actions(request):
    """
    This view accepts posted data via an ajax call, 
    then processes the data and insert/updates the 
    database tables accordingly.

    Args:

        request (WSGIRequest): Request object of Django

    Returns:

        HttpResponse: Returns a success or error message
    """

    # Maps the shift action to the correct success message
    success_messages = {
        "start_shift": "Shift has started",
        "end_shift": "Shift has ended",
        "start_lunch": "Lunch has started",
        "end_lunch": "Lunch has ended",
        "start_break": "Break has started",
        "end_break": "Break has ended",
    }

    form_data = json.loads(request.body)
    employee_id = form_data.get("employee_id")
    shift_action_type = form_data.get("shift_action_type")
    time = form_data.get("time")
    date = form_data.get("date")
    time_punch = time + " " + date

    # The below query searches for an active shift
    shift_id, active_shift, active_lunch, active_break = None, None, None, None
    with Session() as session:
        active_shift_data = (
            session.execute(
                select(
                    ShiftData.shift_id,
                    ShiftData.is_active,
                    ShiftData.on_lunch,
                    ShiftData.on_break
                ).where(
                    ShiftData.is_active.is_(True), 
                    ShiftData.employee_id == employee_id
                )
            ).first()
        )
        
        if active_shift_data:
            shift_id, active_shift, active_lunch, active_break = active_shift_data

    # If there is no active shift, the only action that should work is "start_shift"
    if not active_shift and shift_action_type in {"end_shift", "start_lunch, end_lunch", "start_break", "end_break"}:
        return HttpResponse(content="There is no active shift", status=400)

    # If there is an active shift, user can not start another shift
    if active_shift and shift_action_type == "start_shift":
        return HttpResponse(content=f"A shift is already active", status=400)
    
    # If there is no active shift and the user chooses to start one, insert
    # a new row in the shift_data table.
    if not active_shift and shift_action_type == "start_shift":
        with Session.begin() as session:
            session.execute(
                insert(ShiftData).values(
                    employee_id=employee_id,
                    start_time=time_punch,
                    is_active=True,
                    on_lunch=False,
                    on_break=False
                )
            )
    
    # if there is an active shift and no active lunch/break and the user chooses to end the shift,
    # then update the end time and is_active flag for the active shift.
    if active_shift and not any([active_break, active_lunch]) and shift_action_type == "end_shift":
        with Session.begin() as session:
            session.execute(
                update(ShiftData).values(
                    end_time=time_punch,
                    is_active=False
                ).where(
                    ShiftData.employee_id == employee_id, 
                    ShiftData.is_active.is_(True)
                )
            )
    
    # user is unable to end a shift if there is a lunch or break active
    if active_shift and any([active_break, active_lunch]) and shift_action_type == "end_shift":
        message = "End break before ending shift" if active_break else "End lunch before ending shift"
        return HttpResponse(content=message, status=400)
    
    # if there is an active shift and no active lunch and the user chooses to start lunch,
    # then insert a row into the lunch_data table. Also update the on_lunch flag to True
    # for the active shift.
    if active_shift and not active_lunch and shift_action_type == "start_lunch":
        with Session.begin() as session:
            session.execute(
                insert(LunchData).values(
                    shift_data_id=shift_id,
                    start_time=time_punch,
                    is_active=True,
                )
            )

            session.execute(
                update(ShiftData).values(on_lunch=True).where(ShiftData.shift_id == shift_id)
            )

    # user is unable to start multiple lunch simultaneously
    if active_shift and active_lunch and shift_action_type == "start_lunch":
        return HttpResponse(content="End active lunch before starting a new lunch")

    # if there is an active shift and lunch and the user chooses to end their lunch,
    # then update the end time and is_active flag of the active lunch. Also update the
    #  on_lunch flag to False for the active shift
    if active_shift and active_lunch and shift_action_type == "end_lunch":
        with Session.begin() as session:
            session.execute(
                update(LunchData).values(
                    end_time=time_punch,
                    is_active=False
                ).where(
                    LunchData.shift_data_id == shift_id, 
                    LunchData.is_active.is_(True)
                )
            )

            session.execute(
                update(ShiftData).values(on_lunch=False).where(ShiftData.shift_id == shift_id)
            )

    # if there is an active shift and no active break and the user chooses to start a break,
    # then insert a new row into the break_data table. Also update the on_break flag to True
    # for the active shift.
    if active_shift and not active_break and shift_action_type == "start_break":
        with Session.begin() as session:
            session.execute(
                insert(BreakData).values(
                    shift_data_id=shift_id,
                    start_time=time_punch,
                    is_active=True,
                )
            )

            session.execute(
                update(ShiftData).values(on_break=True).where(ShiftData.shift_id == shift_id)
            )

    # user should not be able to start multiple breaks simultaneously.
    if active_shift and active_break and shift_action_type == "start_break":
        return HttpResponse(content="End active break before starting a new break")

    # If there is a an active shift and break and the user chooses to end their
    # break, then update the end_time and is_active flag to False of the active break.
    # Also, update the on_break flag to False for the active shift.
    if active_shift and active_break and shift_action_type == "end_break":
        with Session.begin() as session:
            session.execute(
                update(BreakData).values(
                    end_time=time_punch,
                    is_active=False
                ).where(
                    BreakData.shift_data_id == shift_id, 
                    BreakData.is_active.is_(True)
                )
            )

            session.execute(
                update(ShiftData).values(on_break=False).where(ShiftData.shift_id == shift_id)
            )

    return HttpResponse(content=success_messages[shift_action_type], status=200)
