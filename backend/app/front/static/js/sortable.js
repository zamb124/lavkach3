async function createSortable(el) {
    const url = el.getAttribute('href');
    el.querySelectorAll('ul').forEach(function (el) {
        createSortable(el);
    });
    new Sortable(el, {
        animation: 150,
        group: {
            name: 'nested',
            pull: true,
            put: true
        },
        fallbackOnBody: true,
        swapThreshold: 0.65,
        onAdd: function (evt) {
            if (!evt.item.querySelector('ul')) {
                const nestedList = document.createElement('ul');
                nestedList.classList.add('nested');
                evt.item.appendChild(nestedList);
                createSortable(nestedList);
            }
        },
        onEnd: async function (evt) {
            const data = {
                id: evt.item.id,
                parent_id: evt.to.closest('li') ? evt.to.closest('li').id : null
            };
            try {
                const response = await fetch(evt.item.getAttribute('href'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                if (!response.ok) {
                    const responce_json = await response.json();
                    const detailCode = responce_json.detail?.code;
                    let toastText = 'Network response was not ok';
                    if (detailCode && app.translations[detailCode]) {
                        toastText = app.translations[detailCode];
                    } else if (detailCode) {
                        toastText = detailCode;
                    }
                    Toastify({
                        text: toastText,
                        duration: 3000,
                        close: true,
                        style: {
                            background: "var(--bs-primary)",
                        },
                    }).showToast();
                    throw new Error('Network response was not ok');
                }
                const responseData = await response.json();
                console.log('Success:', responseData);
            } catch (error) {
                console.error('Error:', error);
                evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
            }
        }
    });
}