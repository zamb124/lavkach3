from flask import Blueprint,render_template
from flask_login import login_required

apps = Blueprint('apps',__name__,template_folder='templates',
    static_folder='static',)
    
#calendar
@apps.route('/apps/calendar')
@login_required
def calendar():
    return render_template('apps/apps-calendar.html')

@apps.route('/apps/apps-calendar-month-grid')
@login_required
def month_grid_calendar():
    return render_template('apps/apps-calendar-month-grid.html')    

#chat
@apps.route('/apps/chat')
@login_required
def chat():
    return render_template('apps/apps-chat.html')

#File Manager
@apps.route('/apps/filemanager')
@login_required
def filemanager():
    return render_template('apps/apps-filemanager.html')

#Todo
@apps.route('/apps/todo')
@login_required
def todo():
    return render_template('apps/apps-todo.html')    

#Api-key
@apps.route('/apps/api_key')
@login_required
def api_key():
    return render_template('apps/apps-api-key.html')    

#Email Pages
@apps.route('/apps/email/mailbox')
@login_required
def mailbox():
    return render_template('apps/email/apps-mailbox.html')

@apps.route('/apps/email/email_basic')
@login_required
def email_basic():
    return render_template('apps/email/apps-email_basic.html')    

@apps.route('/apps/email/email_ecommerce')
@login_required
def email_ecommerce():
    return render_template('apps/email/apps-email_ecommerce.html')         

#Ecommerce Pages
@apps.route('/apps/ecommerce/products')
@login_required
def ecommerce_products():
    return render_template('apps/ecommerce/apps-ecommerce-products.html')         

@apps.route('/apps/ecommerce/product_details')
@login_required
def ecommerce_product_details():
    return render_template('apps/ecommerce/apps-ecommerce-product_details.html')    

@apps.route('/apps/ecommerce/add_product')
@login_required
def ecommerce_add_product():
    return render_template('apps/ecommerce/apps-ecommerce-add_product.html') 

@apps.route('/apps/ecommerce/orders')
@login_required
def ecommerce_orders():
    return render_template('apps/ecommerce/apps-ecommerce-orders.html')   

@apps.route('/apps/ecommerce/order_details')
@login_required
def ecommerce_order_details():
    return render_template('apps/ecommerce/apps-ecommerce-order_details.html')       

@apps.route('/apps/ecommerce/customer')
@login_required
def ecommerce_customer():
    return render_template('apps/ecommerce/apps-ecommerce_customer.html')       

@apps.route('/apps/ecommerce/cart')
@login_required
def ecommerce_cart():
    return render_template('apps/ecommerce/apps-ecommerce_cart.html')   

@apps.route('/apps/ecommerce/checkout')
@login_required
def ecommerce_checkout():
    return render_template('apps/ecommerce/apps-ecommerce_checkout.html')  

@apps.route('/apps/ecommerce/sellers')
@login_required
def ecommerce_sellers():
    return render_template('apps/ecommerce/apps-ecommerce_sellers.html')   

@apps.route('/apps/ecommerce/seller_details')
@login_required
def ecommerce_seller_details():
    return render_template('apps/ecommerce/apps-ecommerce-sellers_details.html')         

#Projects Pages
@apps.route('/apps/projects/list')
@login_required
def projects_list():
    return render_template('apps/projects/apps-projects-list.html') 

@apps.route('/apps/projects/overview')
@login_required
def projects_overview():
    return render_template('apps/projects/apps-projects-overview.html')       

@apps.route('/apps/projects/create')
@login_required
def projects_create():
    return render_template('apps/projects/apps-projects-create.html')   

#Task Pages    
@apps.route('/apps/tasks/kanban')
@login_required
def tasks_kanban():
    return render_template('apps/tasks/apps-tasks-kanban.html') 

@apps.route('/apps/tasks/listview')
@login_required
def tasks_listview():
    return render_template('apps/tasks/apps-tasks-list-view.html')

@apps.route('/apps/tasks/task_details')
@login_required
def tasks_task_details():
    return render_template('apps/tasks/apps-tasks-details.html') 

#CRM Pages
@apps.route('/apps/crm/contacts')
@login_required
def crm_contacts():
    return render_template('apps/crm/apps-crm-contacts.html')

@apps.route('/apps/crm/companies')
@login_required
def crm_companies():
    return render_template('apps/crm/apps-crm-companies.html')  

@apps.route('/apps/crm/deals')
@login_required
def crm_deals():
    return render_template('apps/crm/apps-crm-deals.html') 

@apps.route('/apps/crm/leads')
@login_required
def crm_leads():
    return render_template('apps/crm/apps-crm-leads.html')             

#Crypto Pages
@apps.route('/apps/crypto/transactions')
@login_required
def crypto_transactions():
    return render_template('apps/crypto/apps-crypto-transactions.html')        

@apps.route('/apps/crypto/buysell')
@login_required
def crypto_buysell():
    return render_template('apps/crypto/apps-crypto-buy-sell.html')  

@apps.route('/apps/crypto/orders')
@login_required
def crypto_orders():
    return render_template('apps/crypto/apps-crypto-orders.html')

@apps.route('/apps/crypto/wallet')
@login_required
def crypto_wallet():
    return render_template('apps/crypto/apps-crypto-wallet.html')              

@apps.route('/apps/crypto/ico')
@login_required
def crypto_ico():
    return render_template('apps/crypto/apps-crypto-ico.html')

@apps.route('/apps/crypto/kyc')
@login_required
def crypto_kyc():
    return render_template('apps/crypto/apps-crypto-kyc.html')  

#Invoices Pages     
@apps.route('/apps/invoices/list')
@login_required
def invoices_list():
    return render_template('apps/invoices/apps-invoices-list.html') 

@apps.route('/apps/invoices/details')
@login_required
def invoices_details():
    return render_template('apps/invoices/apps-invoices-details.html')     

@apps.route('/apps/invoices/create')
@login_required
def invoices_create():
    return render_template('apps/invoices/apps-invoices-create.html')  

#Support Tickets
@apps.route('/apps/tickets/list')
@login_required
def tickets_list():
    return render_template('apps/tickets/apps-tickets-list.html')  

@apps.route('/apps/tickets/details')
@login_required
def tickets_details():
    return render_template('apps/tickets/apps-tickets-details.html')   

#NFT Pages
@apps.route('/apps/nft/marketplace')
@login_required
def nft_marketplace():
    return render_template('apps/nft/apps-nft-marketplace.html')  

@apps.route('/apps/nft/explore')
@login_required
def nft_explore():
    return render_template('apps/nft/apps-nft-explore.html')                   

@apps.route('/apps/nft/auction')
@login_required
def nft_auction():
    return render_template('apps/nft/apps-nft-auction.html')   

@apps.route('/apps/nft/item_details')
@login_required
def nft_item_details():
    return render_template('apps/nft/apps-nft-item-details.html')   

@apps.route('/apps/nft/collections')
@login_required
def nft_collections():
    return render_template('apps/nft/apps-nft-collections.html')        

@apps.route('/apps/nft/creators')
@login_required
def nft_creators():
    return render_template('apps/nft/apps-nft-creators.html')    

@apps.route('/apps/nft/ranking')
@login_required
def nft_ranking():
    return render_template('apps/nft/apps-nft-ranking.html')  

@apps.route('/apps/nft/wallet')
@login_required
def nft_wallet():
    return render_template('apps/nft/apps-nft-wallet.html') 

@apps.route('/apps/nft/create')
@login_required
def nft_create():
    return render_template('apps/nft/apps-nft-create.html')    

#Job Pages          

@apps.route('/apps/job/application')
@login_required
def job_application():
    return render_template('apps/job/apps-job-application.html')

@apps.route('/apps/job/candidate_grid')
@login_required
def job_candidate_grid():
    return render_template('apps/job/apps-job-candidate-grid.html')

@apps.route('/apps/job/candidate_lists')
@login_required
def job_candidate_lists():
    return render_template('apps/job/apps-job-candidate-lists.html')

@apps.route('/apps/job/categories')
@login_required
def job_cetegories():
    return render_template('apps/job/apps-job-categories.html')

@apps.route('/apps/job/companies_lists')
@login_required
def job_companies_lists():
    return render_template('apps/job/apps-job-companies-lists.html')

@apps.route('/apps/job/details')
@login_required
def job_details():
    return render_template('apps/job/apps-job-details.html')

@apps.route('/apps/job/grid_lists')
@login_required
def job_grid_lists():
    return render_template('apps/job/apps-job-grid-lists.html')

@apps.route('/apps/job/lists')
@login_required
def job_lists():
    return render_template('apps/job/apps-job-lists.html')

@apps.route('/apps/job/new')
@login_required
def job_new():
    return render_template('apps/job/apps-job-new.html')

@apps.route('/apps/job/statistics')
@login_required
def job_statistics():
    return render_template('apps/job/apps-job-statistics.html')

