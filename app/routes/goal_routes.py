from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from app.models.goal import Goal
from ..db import db
import requests
import json
import os
                
bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()
    try:
        new_goal = Goal.from_dict(request_body)
    except KeyError as e:
        response = { "details": "Invalid data"}
        abort(make_response(response , 400))
    
    db.session.add(new_goal)
    db.session.commit()

    response = {"goal": new_goal.to_dict()}
    return response,201