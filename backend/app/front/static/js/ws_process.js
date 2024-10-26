htmx.on('htmx:wsBeforeMessage', (e) => {
    console.log('wsBeforeMessage')
    const message = JSON.parse(e.detail.message)
    console.log(message)
    if (message.message_type === 'COMPANY_CHANGED') {
        refreshToken()
        var table = htmx.find("table")
        if (table) {
            htmx.trigger(table, 'update')
        }
        var form = htmx.find("form")
        if (form) {
            htmx.trigger(form, 'update')
        }
        var modal = htmx.find("modal")
        if (modal) {
            htmx.trigger(modal, 'update')
        }
    } else if (message.tag === 'MODEL') {
        // Ловим эвенты если записи изменились
        // Ищем элементы на странице, и если у них lsn больше  чем  lsn  из  записи  в  базе  данных
        // то ничего не меняем
        var elements = htmx.findAll(`[ui_key="${message.vars.model}--${message.vars.id}"]`)
        for (var i = elements.length - 1; i >= 0; i--) {
            var el = elements[i]
            if (message.vars.method === 'update') {
                console.log(el.attributes.lsn)
                var elLsn = Number(el.attributes.lsn.nodeValue)
                if (true) {
                    el.attributes.lsn.nodeValue = message.vars.lsn
                    htmx.trigger(el, 'backend_update')
                    var myToast = Toastify({
                        text: message.message,
                        duration: 3000,
                        style: {
                            className: "tost",
                        },
                    })
                    myToast.showToast();
                }

            } else if (message.vars.method === 'delete') {
                el.remove();
                var myToast = Toastify({
                    text: message.message,
                })
                myToast.showToast();
            }
        }
    } else if (message.tag === 'REFRESH') {
        refreshToken()
        setTimeout(() => {
            location.reload();
        }, 1000)
    }
})