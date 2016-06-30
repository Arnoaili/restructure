from flask import render_template
from . import department_views

@department_views.route('/department')
def login():
	return render_template('test.html')

@department_views.route('/err',methods=['GET', 'POST'])
def error():
	return render_template('error.html')
