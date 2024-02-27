from flask import Blueprint,render_template
from flask_login import login_required

dashboards = Blueprint('dashboards',__name__,template_folder='templates',
    static_folder='static',)
    

@dashboards.route('/')
@login_required
def index():
    return render_template('dashboards/index.html')

@dashboards.route('/dashboard-analytics/')
@login_required
def dashboard_analytics():
    return render_template('dashboards/dashboard-analytics.html')

@dashboards.route('/dashboard-crm/')
@login_required
def dashboard_crm():
    return render_template('dashboards/dashboard-crm.html')

@dashboards.route('/dashboard-crypto/')
@login_required
def dashboard_crypto():
    return render_template('dashboards/dashboard-crypto.html')   

@dashboards.route('/dashboard-projects/')
@login_required
def dashboard_projects():
    return render_template('dashboards/dashboard-projects.html')   

@dashboards.route('/dashboard-nft/')
@login_required
def dashboard_nft():
    return render_template('dashboards/dashboard-nft.html')    

@dashboards.route('/dashboard-job/')
@login_required
def dashboard_job():
    return render_template('dashboards/dashboard-job.html')    