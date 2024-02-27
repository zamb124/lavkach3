from flask import Blueprint,render_template
from flask_login import login_required

layouts = Blueprint('layouts',__name__,template_folder='templates',
    static_folder='static',)
    
#calendar
@layouts.route('/layouts/horizontal')
@login_required
def layouts_horizontal():
    return render_template('layouts/layouts-horizontal.html')

@layouts.route('/layouts/detached')
@login_required
def layouts_detached():
    return render_template('layouts/layouts-detached.html')    

@layouts.route('/layouts/two_column')
@login_required
def layouts_two_column():
    return render_template('layouts/layouts-two-column.html')       

@layouts.route('/layouts/hovered')
@login_required
def layouts_hovered():
    return render_template('layouts/layouts-vertical-hovered.html')       

@layouts.route('/layouts/vertical')
@login_required
def layouts_vertical():
    return render_template('layouts/layouts-vertical.html')    