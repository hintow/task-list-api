from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from ..db import db
from sqlalchemy import asc,desc
from datetime import datetime
import requests
import json
import os
                
bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()
    try:
         new_task = Task.from_dict(request_body)
    except KeyError as e:        
        response = { "details": "Invalid data"}
        abort(make_response(response , 400))

    db.session.add(new_task)
    db.session.commit()

    response = { "task": new_task.to_dict()}
    return response, 201    


@bp.get("")
def get_all_tasks():
    query = db.select(Task)
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(asc(Task.title))
    if sort_param == "desc":
        query = query.order_by(desc(Task.title))   
    else:
        query = query.order_by(Task.id)

    tasks = db.session.scalars(query)

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_dict())

    return tasks_response

@bp.get("/<task_id>")
def get_one_task_by_id(task_id):
    task = validate_task(task_id)

    return {"task": task.to_dict()}

# should it be refactored with from_dict??
@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    return {"task": task.to_dict()}

@bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_task(task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    # send slack
    url = "https://slack.com/api/chat.postMessage"

    payload = json.dumps({
        "channel": "task-notifications",
        "text": f"You just completed task: {task.id}:{task.title}!"
    })
    headers = {
        'Authorization': f'Bearer {os.environ.get("SLACK_API_TOKEN")}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        response = {"message": f"Task {task_id} failed to notify slack with status {response.status_code}"}
        abort(make_response(response , 400))        

    return {"task": task.to_dict()}


@bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_task(task_id)

    task.completed_at = None
    db.session.commit()

    return {"task": task.to_dict()}



@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return  {
        "details": f'Task {task_id} "{task.title}" successfully deleted'
    }

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"Task {task_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": f"Task {task_id} not found"}
        abort(make_response(response, 404))

    return task
