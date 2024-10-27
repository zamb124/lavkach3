htmx.on('htmx:wsBeforeMessage', (e) => {
    console.log('wsBeforeMessage')
    const message = JSON.parse(e.detail.message)
    console.log(message)
    if (message.message_type === 'COMPANY_CHANGED') {
        document.location.reload()
    } else if (message.tag === 'MODEL') {
        var elements = htmx.findAll(`[ui_key="${message.vars.model}--${message.vars.id}"]`)
        if (message.vars.method === 'create') {
            let elements = htmx.findAll('[id^="table--"]');
            elements.forEach(element => {
                htmx.trigger(element, 'update')
            });
            console.log('create')
        } else if (message.vars.method === 'update') {
            // Ловим эвенты если записи изменились
            // Ищем элементы на странице, и если у них lsn больше  чем  lsn  из  записи  в  базе  данных
            // то ничего не меняем
            for (var i = elements.length - 1; i >= 0; i--) {
                var el = elements[i]
                console.log(el.attributes.lsn)
                var elLsn = Number(el.attributes.lsn.nodeValue)
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
            elements.forEach(element => {
                element.remove(); // Удаляем каждый элемент
            });
            var myToast = Toastify({
                text: 'Object deleted',
            })
            myToast.showToast();
        }
    } else if (message.tag === 'REFRESH') {
        refreshToken()
        setTimeout(() => {
            location.reload();
        }, 1000)
    }
})