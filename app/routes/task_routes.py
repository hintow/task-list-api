from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from ..db import db
from sqlalchemy import asc,desc
from datetime import datetime
import requests
import json
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    title = request_body.get("title")
    description = request_body.get("description")

    if not title or not description:
        response = {
            "details": "Invalid data"
        }
        abort(make_response(response , 400))

    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()

    response = {
        "task": {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "is_complete":new_task.is_complete()
        }
    }
    return response, 201    


@tasks_bp.get("")
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
        tasks_response.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete()
        })

    return tasks_response

@tasks_bp.get("/<task_id>")
def get_one_task_by_id(task_id):
    task = validate_task(task_id)

    return {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete()
        }
    }


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    return {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete()
        }
    } 


@tasks_bp.patch("/<task_id>/mark_complete")
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

    return {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete()
        }
    } 


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_task(task_id)

    task.completed_at = None
    db.session.commit()

    return {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete()
        }
    } 



@tasks_bp.delete("/<task_id>")
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
