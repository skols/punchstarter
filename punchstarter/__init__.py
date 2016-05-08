import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, url_for, redirect, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Server
import datetime

app = Flask(__name__)
app.config.from_object('punchstarter.default_settings')
manager = Manager(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager.add_command('db', MigrateCommand)

# Has to be here, not at the top
from punchstarter.models import *

manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True,
    host = os.getenv('IP', '0.0.0.0'),
    port = int(os.getenv('PORT',5000))
    )
)

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/projects/create/", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")
    elif request.method == "POST":
        # Handle the form submission
        
        now = datetime.datetime.now()
        time_end = request.form.get("funding_end_date")
        time_end = datetime.datetime.strptime(time_end, "%m/%d/%Y")
        
        new_project = Project(
            member_id = 1, # Guest Creator
            name = request.form.get("project_name"),
            short_description = request.form.get("short_description"),
            long_description = request.form.get("long_description"),
            goal_amount = request.form.get("funding_goal"),
            time_start = now,
            time_end = time_end,
            time_created = now
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return redirect(url_for("create"))

@app.route("/projects/<int:project_id>/")
def project_detail(project_id):
    project = db.session.query(Project).get(project_id)
    if project is None:
        abort(404)
    
    return render_template("project_detail.html", project=project)