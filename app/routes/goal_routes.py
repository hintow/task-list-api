from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from app.models.goal import Goal
from sqlalchemy import asc,desc
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

@bp.get("")
def get_all_goals():
    query = db.select(Goal)
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(asc(Goal.title))
    if sort_param == "desc":
        query = query.order_by(desc(Goal.title))   
    else:
        query = query.order_by(Goal.id)

    goals = db.session.scalars(query)

    tasks_response = []
    for goal in goals:
        tasks_response.append(goal.to_dict())

    return tasks_response

@bp.get("/<goal_id>")
def get_one_task_by_id(goal_id):
    goal = validate_goal(goal_id)

    return {"goal": goal.to_dict()}

# should it be refactored with from_dict??
@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return {"goal": goal.to_dict()}

# @bp.patch("/<task_id>/mark_complete")
# def mark_complete(task_id):
#     task = validate_task(task_id)

#     task.completed_at = datetime.now()
#     db.session.commit()

#     # send slack
#     url = "https://slack.com/api/chat.postMessage"

#     payload = json.dumps({
#         "channel": "task-notifications",
#         "text": f"You just completed task: {task.id}:{task.title}!"
#     })
#     headers = {
#         'Authorization': f'Bearer {os.environ.get("SLACK_API_TOKEN")}',
#         'Content-Type': 'application/json'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)
#     if response.status_code != 200:
#         response = {"message": f"Task {task_id} failed to notify slack with status {response.status_code}"}
#         abort(make_response(response , 400))        

#     return {"task": task.to_dict()}


# @bp.patch("/<goal_id>/mark_incomplete")
# def mark_incomplete(goal_id):
#     goal = validate_task(goal_id)

#     goal.completed_at = None
#     db.session.commit()

#     return {"goal": goal.to_dict()}



@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_goal(goal_id)
    db.session.delete(goal)
    db.session.commit()

    return  {
        "details": f'Goal {goal_id} "{goal.title}" successfully deleted'
    }

def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except:
        response = {"message": f"Goal {goal_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)

    if not goal:
        response = {"message": f"Goal {goal_id} not found"}
        abort(make_response(response, 404))

    return goal
