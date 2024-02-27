from flask import Blueprint,render_template
from flask_login import login_required


components = Blueprint('components',__name__,template_folder='templates',
    static_folder='static',)
    
#Base UI
@components.route('/components/base-ui/alerts')
@login_required
def ui_alerts():
    return render_template('components/base-ui/ui-alerts.html')

@components.route('/components/base-ui/badges')
@login_required
def ui_badges():
    return render_template('components/base-ui/ui-badges.html')  

@components.route('/components/base-ui/buttons')
@login_required
def ui_buttons():
    return render_template('components/base-ui/ui-buttons.html')     

@components.route('/components/base-ui/colors')
@login_required
def ui_colors():
    return render_template('components/base-ui/ui-colors.html') 

@components.route('/components/base-ui/cards')
@login_required
def ui_cards():
    return render_template('components/base-ui/ui-cards.html')     

@components.route('/components/base-ui/carousel')
@login_required
def ui_carousel():
    return render_template('components/base-ui/ui-carousel.html')      

@components.route('/components/base-ui/dropdowns')
@login_required
def ui_dropdowns():
    return render_template('components/base-ui/ui-dropdowns.html')  

@components.route('/components/base-ui/grid')
@login_required
def ui_grid():
    return render_template('components/base-ui/ui-grid.html')              

@components.route('/components/base-ui/images')
@login_required
def ui_images():
    return render_template('components/base-ui/ui-images.html')      

@components.route('/components/base-ui/tabs')
@login_required
def ui_tabs():
    return render_template('components/base-ui/ui-tabs.html')         

@components.route('/components/base-ui/accordions')
@login_required
def ui_accordions():
    return render_template('components/base-ui/ui-accordions.html') 

@components.route('/components/base-ui/modals')
@login_required
def ui_modals():
    return render_template('components/base-ui/ui-modals.html')

@components.route('/components/base-ui/offcanvas')
@login_required
def ui_offcanvas():
    return render_template('components/base-ui/ui-offcanvas.html')        

@components.route('/components/base-ui/placeholders')
@login_required
def ui_placeholders():
    return render_template('components/base-ui/ui-placeholders.html')     

@components.route('/components/base-ui/progress')
@login_required
def ui_progress():
    return render_template('components/base-ui/ui-progress.html')     

@components.route('/components/base-ui/notifications')
@login_required
def ui_notifications():
    return render_template('components/base-ui/ui-notifications.html')       

@components.route('/components/base-ui/media')
@login_required
def ui_media():
    return render_template('components/base-ui/ui-media.html')       

@components.route('/components/base-ui/embed_video')
@login_required
def ui_embed_video():
    return render_template('components/base-ui/ui-embed-video.html')     

@components.route('/components/base-ui/typography')
@login_required
def ui_typography():
    return render_template('components/base-ui/ui-typography.html') 

@components.route('/components/base-ui/lists')
@login_required
def ui_lists():
    return render_template('components/base-ui/ui-lists.html')  

@components.route('/components/base-ui/links')
@login_required
def ui_links():
    return render_template('components/base-ui/ui-links.html')  

@components.route('/components/base-ui/general')
@login_required
def ui_general():
    return render_template('components/base-ui/ui-general.html')  

@components.route('/components/base-ui/ribbons')
@login_required
def ui_ribbons():
    return render_template('components/base-ui/ui-ribbons.html')     

@components.route('/components/base-ui/utilities')
@login_required
def ui_utilities():
    return render_template('components/base-ui/ui-utilities.html') 

#Advance UI Pages
@components.route('/components/advance-ui/sweetalerts')
@login_required
def ui_sweetalerts():
    return render_template('components/advance-ui/advance-ui-sweetalerts.html')

@components.route('/components/advance-ui/nestable')
@login_required
def ui_nestable():
    return render_template('components/advance-ui/advance-ui-nestable.html')

@components.route('/components/advance-ui/scrollbar')
@login_required
def ui_scrollbar():
    return render_template('components/advance-ui/advance-ui-scrollbar.html')      

@components.route('/components/advance-ui/animation')
@login_required
def ui_animation():
    return render_template('components/advance-ui/advance-ui-animation.html')

@components.route('/components/advance-ui/tour')
@login_required
def ui_tour():
    return render_template('components/advance-ui/advance-ui-tour.html')

@components.route('/components/advance-ui/swiper')
@login_required
def ui_swiper():
    return render_template('components/advance-ui/advance-ui-swiper.html')     

@components.route('/components/advance-ui/ratings')
@login_required
def ui_ratings():
    return render_template('components/advance-ui/advance-ui-ratings.html') 

@components.route('/components/advance-ui/highlight')
@login_required
def ui_highlight():
    return render_template('components/advance-ui/advance-ui-highlight.html') 
    
@components.route('/components/advance-ui/scrollspy')
@login_required
def ui_scrollspy():
    return render_template('components/advance-ui/advance-ui-scrollspy.html')     

@components.route('/components/widgets')
@login_required
def ui_widgets():
    return render_template('components/widgets/widgets.html')

#Forms 
@components.route('/components/forms/elements')
@login_required
def forms_elements():
    return render_template('components/forms/forms-elements.html') 

@components.route('/components/forms/formselect')
@login_required
def forms_formselect():
    return render_template('components/forms/forms-select.html') 

@components.route('/components/forms/forms-checkboxs-radios')
@login_required
def forms_checkboxs_radios():
    return render_template('components/forms/forms-checkboxs-radios.html')  

@components.route('/components/forms/forms-pickers')
@login_required
def forms_pickers():
    return render_template('components/forms/forms-pickers.html')  
    
@components.route('/components/forms/forms-masks')
@login_required
def forms_masks():
    return render_template('components/forms/forms-masks.html') 

@components.route('/components/forms/forms-advanced')
@login_required
def forms_advanced():
    return render_template('components/forms/forms-advanced.html')   

@components.route('/components/forms/forms-range-sliders')
@login_required
def forms_range_sliders():
    return render_template('components/forms/forms-range-sliders.html')    

@components.route('/components/forms/forms-validation')
@login_required
def forms_validation():
    return render_template('components/forms/forms-validation.html') 

@components.route('/components/forms/forms-wizard')
@login_required
def forms_wizard():
    return render_template('components/forms/forms-wizard.html')        

@components.route('/components/forms/forms-editors')
@login_required
def forms_editors():
    return render_template('components/forms/forms-editors.html')                  

@components.route('/components/forms/forms-file-uploads')
@login_required
def forms_file_uploads():
    return render_template('components/forms/forms-file-uploads.html')         

@components.route('/components/forms/forms-layouts')
@login_required
def forms_layouts():
    return render_template('components/forms/forms-layouts.html') 

@components.route('/components/forms/forms-select2')
@login_required
def forms_select2():
    return render_template('components/forms/forms-select2.html')

#Tables pages
@components.route('/components/tables/tables-basic')
@login_required
def tables_basic():
    return render_template('components/tables/tables-basic.html')    

@components.route('/components/tables/tables-gridjs')
@login_required
def tables_gridjs():
    return render_template('components/tables/tables-gridjs.html')     

@components.route('/components/tables/tables-listjs')
@login_required
def tables_listjs():
    return render_template('components/tables/tables-listjs.html') 

@components.route('/components/tables/tables-datatables')
@login_required
def tables_datatables():
    return render_template('components/tables/tables-datatables.html')    

#Charts pages
@components.route('/components/charts/charts-apex-line')
@login_required
def charts_apex_line():
    return render_template('components/charts/apexcharts/charts-apex-line.html')

@components.route('/components/charts/charts-apex-area')
@login_required
def charts_apex_area():
    return render_template('components/charts/apexcharts/charts-apex-area.html')  

@components.route('/components/charts/charts-apex-column')
@login_required
def charts_apex_column():
    return render_template('components/charts/apexcharts/charts-apex-column.html')       

@components.route('/components/charts/charts-apex-bar')
@login_required
def charts_apex_bar():
    return render_template('components/charts/apexcharts/charts-apex-bar.html')

@components.route('/components/charts/charts-apex-funnel')
@login_required
def charts_apex_funnel():
    return render_template('components/charts/apexcharts/charts-apex-funnel.html')

@components.route('/components/charts/charts-apex-rangearea')
@login_required
def rangearea():
    return render_template('components/charts/apexcharts/charts-apex-range-area.html')

@components.route('/components/charts/charts-apex-mixed')
@login_required
def charts_apex_mixed():
    return render_template('components/charts/apexcharts/charts-apex-mixed.html')  

@components.route('/components/charts/charts-apex-timeline')
@login_required
def charts_apex_timeline():
    return render_template('components/charts/apexcharts/charts-apex-timeline.html')  

@components.route('/components/charts/charts-apex-candlestick')
@login_required
def charts_apex_candlestick():
    return render_template('components/charts/apexcharts/charts-apex-candlestick.html')       

@components.route('/components/charts/charts-apex-boxplot')
@login_required
def charts_apex_boxplot():
    return render_template('components/charts/apexcharts/charts-apex-boxplot.html')    

@components.route('/components/charts/charts-apex-bubble')
@login_required
def charts_apex_bubble():
    return render_template('components/charts/apexcharts/charts-apex-bubble.html')         

@components.route('/components/charts/charts-apex-scatter')
@login_required
def charts_apex_scatter():
    return render_template('components/charts/apexcharts/charts-apex-scatter.html')    

@components.route('/components/charts/charts-apex-heatmap')
@login_required
def charts_apex_heatmap():
    return render_template('components/charts/apexcharts/charts-apex-heatmap.html')     

@components.route('/components/charts/charts-apex-treemap')
@login_required
def charts_apex_treemap():
    return render_template('components/charts/apexcharts/charts-apex-treemap.html') 

@components.route('/components/charts/charts-apex-pie')
@login_required
def charts_apex_pie():
    return render_template('components/charts/apexcharts/charts-apex-pie.html')      

@components.route('/components/charts/charts-apex-radialbar')
@login_required
def charts_apex_radialbar():
    return render_template('components/charts/apexcharts/charts-apex-radialbar.html')   

@components.route('/components/charts/charts-apex-radar')
@login_required
def charts_apex_radar():
    return render_template('components/charts/apexcharts/charts-apex-radar.html')   

@components.route('/components/charts/charts-apex-polar')
@login_required
def charts_apex_polar():
    return render_template('components/charts/apexcharts/charts-apex-polar.html')  

@components.route('/components/charts/charts-chartjs')
@login_required
def charts_chartjs():
    return render_template('components/charts/charts-chartjs.html')     

@components.route('/components/charts/charts-echarts')
@login_required
def charts_echarts():
    return render_template('components/charts/charts-echarts.html')                 

#Icons pages
@components.route('/components/icons/icons-remix')
@login_required
def icons_remix():
    return render_template('components/icons/icons-remix.html')

@components.route('/components/icons/icons-boxicons')
@login_required
def icons_boxicons():
    return render_template('components/icons/icons-boxicons.html')    

@components.route('/components/icons/icons-materialdesign')
@login_required
def icons_materialdesign():
    return render_template('components/icons/icons-materialdesign.html') 

@components.route('/components/icons/icons-lineawesome')
@login_required
def icons_lineawesome():
    return render_template('components/icons/icons-lineawesome.html') 

@components.route('/components/icons/icons-feather')
@login_required
def icons_feather():
    return render_template('components/icons/icons-feather.html')  

@components.route('/components/icons/icons-crypto')
@login_required
def icons_crypto():
    return render_template('components/icons/icons-crypto.html')       

#Maps pages
@components.route('/components/maps/maps-google')
@login_required
def maps_google():
    return render_template('components/maps/maps-google.html') 

@components.route('/components/maps/maps-vector')
@login_required
def maps_vector():
    return render_template('components/maps/maps-vector.html')     

@components.route('/components/maps/maps-leaflet')
@login_required
def maps_leaflet():
    return render_template('components/maps/maps-leaflet.html') 
