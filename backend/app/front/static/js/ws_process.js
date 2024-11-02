class WebSocketHandler {
    constructor() {
        this.initEventListeners();
    }

    initEventListeners() {
        htmx.on('htmx:wsBeforeMessage', this.handleMessage.bind(this));
    }

    handleMessage(e) {
        console.log('wsBeforeMessage');
        const message = JSON.parse(e.detail.message);
        console.log(message);
        switch (message.tag) {
            case 'COMPANY_CHANGED':
                this.handleCompanyChanged();
                break;
            case 'LOGOUT':
                this.handleLogout();
                break;
            case 'MODEL':
                this.handleModelMessage(message);
                break;
            case 'REFRESH':
                this.handleRefresh();
                break;
            default:
                console.warn('Unknown message type:', message.tag);
        }
    }

    handleCompanyChanged() {
        debugger
        document.location.reload();
    }

    handleLogout() {
        document.cookie = "token={{token}};expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;";
        document.cookie = "refresh_token={{refresh_token}};expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;";
        document.location.replace('/basic/user/login?/');
    }

    handleModelMessage(message) {
        const elements = htmx.findAll(`[ui_key="${message.vars.model}--${message.vars.id}"]`);
        switch (message.vars.method) {
            case 'create':
                this.handleModelCreate();
                break;
            case 'update':
                this.handleModelUpdate(elements, message);
                break;
            case 'delete':
                this.handleModelDelete(elements);
                break;
            default:
                console.warn('Unknown model method:', message.vars.method);
        }
    }

    handleModelCreate() {
        const elements = htmx.findAll('[id^="table--"]');
        elements.forEach(element => {
            htmx.trigger(element, 'update');
        });
        console.log('create');
    }

    handleModelUpdate(elements, message) {
        elements.forEach(el => {
            console.log(el.attributes.lsn);
            const elLsn = Number(el.attributes.lsn.nodeValue);
            el.attributes.lsn.nodeValue = message.vars.lsn;
            htmx.trigger(el, 'backend_update');
            if (message.vars.updated_fields) {
                this.showToast(message.message);
            }
        });
    }

    handleModelDelete(elements) {
        elements.forEach(element => {
            element.remove();
        });
        this.showToast('Object deleted');
    }

    handleRefresh() {
        this.refreshToken();
        setTimeout(() => {
            location.reload();
        }, 1000);
    }

    showToast(message) {
        Toastify({
            text: message,
            duration: 3000,
            style: {
                className: "tost",
            },
        }).showToast();
    }

    refreshToken() {
        app.refreshToken()
    }
}

// Инициализация обработчика WebSocket
new WebSocketHandler();