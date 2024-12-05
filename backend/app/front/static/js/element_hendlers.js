function extractUUIDs(input) {
    // Удаляем все символы табуляции, пробелы, скобки и прочее
    let cleanedInput = input.replace(/[\s\[\]\'\,]+/g, '');
    // Выделяем UUID через запятую
    let uuids = cleanedInput.match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/g);
    return uuids ? uuids.join(',') : '';
}

class ChoiceHandler {
    constructor(element, method) {
        this.method = method;
        this.element = element
        this.displayTitle = this.element.getAttribute('display-title');
        this.filter = this.element.getAttribute('filter');
        this.isFilter = this.element.getAttribute('is-filter');
        this.modelName = this.element.getAttribute('model-name');
        this.attrs = {
            allowHTML: true,
            placeholder: true,
            searchPlaceholderValue: 'Start typing to search',
            placeholderValue: "Enter " + this.displayTitle,
            itemSelectText: '',
            removeItemButton: !(method === 'get' || this.element.getAttribute('readonly'))
        };
        this.element.classList.add('form-control');
        this.choices = new Choices(this.element, this.attrs);
        this.init();
    }

    async init() {
        if (this.method === 'get' || this.element.getAttribute('readonly')) {
            this.choices.disable();
        } else if (this.method === 'update' && this.element.getAttribute('readonly')) {
            this.choices.containerInner.element.classList.add('disabled');
            this.choices.disable();
        }

        this.choices.containerInner.element.classList.add('form-control');

        this.element.addEventListener('search', async e => {
            this.element.focus();
            let value = e.detail.value;
            this.choices.clearChoices();
            this.choices.setChoices(await this.searchChoices(value));
        });

        this.element.addEventListener('choice', event => this.checkValid(event));
        this.element.addEventListener('showDropdown', async () => {
            this.choices.clearChoices();
            this.choices.setChoices(await this.searchChoices(''));
        });
        this.element.addEventListener('removeItem', event => this.checkValid(event));

        let initValues = await this.getValues();
        this.choices.removeActiveItems();
        this.choices.clearChoices();
        this.choices.setValue(initValues);
        this.checkValid();
    }

    checkValid(event) {
        if (this.method === 'get' || this.element.getAttribute('readonly')) {
            return;
        }
        if (this.element.required) {
            if (event) {
                if (event.type === 'choice' && event.detail.choice.value) {
                    this.choices.containerInner.element.classList.remove('is-invalid');
                    this.choices.containerInner.element.classList.add('is-valid');
                } else if (event.type === 'removeItem' && event.detail.value) {
                    if (!this.choices.containerInner.element.innerText) {
                        this.choices.containerInner.element.classList.add('is-invalid');
                        this.choices.containerInner.element.classList.remove('is-valid');
                    } else {
                        this.choices.containerInner.element.classList.add('is-valid');
                        this.choices.containerInner.element.classList.remove('is-invalid');
                    }
                }
            } else {
                if (!this.choices.containerInner.element.innerText) {
                    this.choices.containerInner.element.classList.add('is-invalid');
                    this.choices.containerInner.element.classList.remove('is-valid');
                } else {
                    this.choices.containerInner.element.classList.add('is-valid');
                    this.choices.containerInner.element.classList.remove('is-invalid');
                }
            }
        } else if (this.element.id.includes('__in')) {
            //this.choices.containerInner.element.classList.remove('is-invalid');
        } else {
            //this.choices.containerInner.element.classList.add('is-valid');
        }
    }

    async searchChoices(value) {
        try {
            const items = await fetch(`/base/search?model=${this.modelName}&filter=${this.filter}&q=${encodeURIComponent(value)}`);
            const results = await items.json();
            if (results.length === 0) {
                throw 'Empty!';
            }
            return results;
        } catch (err) {
            console.error(err);
        }
    }

    async getValues() {
        var id__in = ''
        let value = await this.choices.getValue();
        await this.choices.setValue([])
        let values = []
        if (!value) {
            return []
        } else if (!Array.isArray(value)) {
            values.push(value);
        } else {
            values = value;
        }

        for (let v in values) {
            let val = values[v].value;
            var maybe_cache = app.cache.results[val]
            if (!maybe_cache) {
                app.pushUUID(this.modelName, val)
            }
        }
        var result = []
        while (true) {
            for (let v in values) {
                id__in = values[v].value
                if (app.cache.results[id__in]) {
                    result.push({
                        value: values[v].label,
                        label: app.cache.results[id__in]
                    })
                    values.splice(v, 1)
                }
            }
            if (values.length === 0) {
                return result
            }
            await new Promise(r => setTimeout(r, 50));
        }
    }

}

async function choicesMultiBadges(element, method) {
    var model_name = element.getAttribute('model-name')

    async function getValues() {
        var id__in = ''
        var str = extractUUIDs(element.innerText).toLowerCase();
        let values = str ? str.split(',') : [];

        for (let v in values) {
            var maybe_cache = app.cache.results[values[v]]
            if (!maybe_cache) {
                app.pushUUID(model_name, values[v])
            }
        }
        var result = []
        while (true) {
            for (let v in values) {
                if (app.cache.results[values[v]]) {
                    result.push({
                        value: values[v],
                        label: app.cache.results[values[v]]
                    })
                    values.splice(v, 1)
                }
            }
            if (values.length === 0) {
                return result
            }
            await new Promise(r => setTimeout(r, 50));
        }
    }

    let res = await getValues()
    element.innerText = ''
    res.forEach(function (line) {
        element.insertAdjacentHTML('beforeend', '<span class="badge bg-secondary m-lg-1">' + line.label + '</span>');
    });
    if (!element.innerText && method === 'get') {
        element.innerText = '-'
    }
}

async function choicesUuidBadge(elId, method) {
    let element = document.getElementById(elId);
    var model_name = element.getAttribute('model-name')

    async function getValues() {
        var id__in = ''
        var str = extractUUIDs(element.innerText).toLowerCase();
        let values = str ? str.split(',') : [];

        for (let v in values) {
            var maybe_cache = app.cache.results[values[v]]
            if (!maybe_cache) {
                app.pushUUID(model_name, values[v])
            }
        }
        var result = []
        while (true) {
            for (let v in values) {
                if (app.cache.results[values[v]]) {
                    result.push({
                        value: values[v],
                        label: app.cache.results[values[v]]
                    })
                    values.splice(v, 1)
                }
            }
            if (values.length === 0) {
                return result
            }
            await new Promise(r => setTimeout(r, 50));
        }
    }

    let res = await getValues()
    if (res.length > 0) {
        element.innerText = res[0].label;
    } else {
        element.innerText = ''
    }
    if (!element.innerText && method === 'get') {
        element.innerText = '-'
    }
}

async function choiceMultiBabel(element) {
    var display_title = element.getAttribute('display-title')
    var filter = element.getAttribute('filter')
    var is_filter = element.getAttribute('is-filter')
    var model_name = element.getAttribute('model-name')
    var attrs = {
        allowHTML: true,
        placeholderValue: "Enter " + display_title
    }
    if (method === 'get' || element.getAttribute('readonly')) {
        attrs.removeItemButton = false
    } else {
        attrs.removeItemButton = true
    }
    let choices = new Choices(element, attrs);
    if (method === 'get' || element.getAttribute('readonly')) {
        choices.containerInner.element.classList.add('disabled');
        choices.disable()
    }
    choices.containerInner.element.classList.add('form-control');
    if (is_filter) {
        function check_valid() {
            if (element.required) {
                choices.containerInner.element.classList.add('is-invalid');
                choices.containerInner.element.classList.remove('is-valid');
            } else {
                choices.containerInner.element.classList.remove('is-invalid');
                choices.containerInner.element.classList.add('is-valid');
            }
        }

        check_valid()
    }

    function init() {
        choices.setChoices(async () => {
            try {
                const items = await fetch('/base/search?model=' + model_name + '&search=');
                const results = await items.json();
                if (0 === results.length) { // Handle error from result, for example.
                    throw 'Empty!';
                }
                return results;
            } catch (err) {
                console.error(err);
            }
        }).then(() => {
            choices.input.element.focus()
        });
    }

    init()

}

async function choiceOneBabel(elId, method) {
    var element = document.getElementById(elId);
    var display_title = element.getAttribute('display-title')
    var filter = element.getAttribute('filter')
    var is_filter = element.getAttribute('is-filter')
    var model_name = element.getAttribute('model-name')
    var attrs = {
        placeholderValue: "Enter " + display_title,
        allowHTML: true
    }
    if (method === 'get' || element.getAttribute('readonly')) {
        attrs.removeItemButton = false
    } else {
        attrs.removeItemButton = true
    }
    let choices = new Choices(element, attrs);
    if (method === 'get' || element.getAttribute('readonly')) {
        choices.containerInner.element.classList.add('disabled');
        choices.disable()
    }
    choices.containerInner.element.classList.add('form-control');
    if (is_filter) {

        function check_valid() {
            if (element.required) {
                choices.containerInner.element.classList.add('is-invalid');
                choices.containerInner.element.classList.remove('is-valid');
            } else {
                choices.containerInner.element.classList.remove('is-invalid');
                choices.containerInner.element.classList.add('is-valid');
            }
        }

        check_valid()
    }

    function init() {
        choices.setChoices(async () => {
            try {
                const items = await fetch('/base/search?model=' + model_name + '&search=');
                const results = await items.json();
                if (0 === results.length) { // Handle error from result, for example.
                    throw 'Empty!';
                }
                return results;
            } catch (err) {
                console.error(err);
            }
        }).then(() => {
            choices.input.element.focus()
        });
    }

    init()
}

async function choiceMultiEnum(element, method) {
    var display_title = element.getAttribute('display-title')
    var filter = element.getAttribute('filter')
    var is_filter = element.getAttribute('is-filter')
    var model_name = element.getAttribute('model-name')
    let attrs = {
        allowHTML: true,
        placeholder: true,
        searchPlaceholderValue: 'Start typing to search',
        placeholderValue: "Enter " + display_title,
        removeItemButton: !(method === 'get' || element.getAttribute('readonly'))
    };
    let choices = new Choices(element, attrs);
    if (method === 'get' || element.getAttribute('readonly')) {
        choices.containerInner.element.classList.add('disabled');
        choices.disable()
    }
    choices.containerInner.element.classList.add('form-control');

    function check_valid(event) {
        if (method === 'get' || element.getAttribute('readonly')) { // Если метод get или reanonly, то нет смысла от валидования
            // Если метод get или reanonly, то нет смысла от валидования
            return
        }
        if (element.required) {
            if (event) {
                if (event.type === 'choice') {
                    if (event.detail.choice.value) {
                        choices.containerInner.element.classList.remove('is-invalid');
                        choices.containerInner.element.classList.add('is-valid');
                    }
                } else if (event.type === 'removeItem') {
                    if (event.detail.value) {
                        if (!choices.containerInner.element.innerText) {
                            choices.containerInner.element.classList.add('is-invalid');
                            choices.containerInner.element.classList.remove('is-valid');
                        } else {
                            choices.containerInner.element.classList.add('is-valid');
                            choices.containerInner.element.classList.remove('is-invalid');
                        }

                    }
                }

            } else {
                if (!choices.containerInner.element.innerText) {
                    choices.containerInner.element.classList.add('is-invalid');
                    choices.containerInner.element.classList.remove('is-valid');
                } else {
                    choices.containerInner.element.classList.add('is-valid');
                    choices.containerInner.element.classList.remove('is-invalid');
                }
            }
        } else if (element.id.includes('__in')) {
            choices.containerInner.element.classList.remove('is-invalid');
            choices.containerInner.element.classList.remove('is-invalid');
        } else {
            try {
                choices.containerInner.element.classList.remove('is-invalid');
            } catch (err) {

            }
            choices.containerInner.element.classList.add('is-valid');
        }
    }

    choices.containerInner.element.classList.add('form-control');

    check_valid()
}

async function setTitle(element, method) {
    var model_name = element.getAttribute('model-name')
    var elem_value = element.innerText
    element.innerHTML = '<span class="spinner-border text-primary" role="status">\n' +
            '                    <span class="visually-hidden">Loading...</span>\n' +
            '                  </span>'
    async function getValues() {
        var id__in = ''
        var str = extractUUIDs(elem_value).toLowerCase();
        let values = str ? str.split(',') : [];

        for (let v in values) {
            var maybe_cache = app.cache.results[values[v]]
            if (!maybe_cache) {
                app.pushUUID(model_name, values[v])
            }
        }
        var result = []
        while (true) {
            for (let v in values) {
                if (app.cache.results[values[v]]) {
                    result.push({
                        value: values[v],
                        label: app.cache.results[values[v]]
                    })
                    values.splice(v, 1)
                }
            }
            if (values.length === 0) {
                return result
            }
            await new Promise(r => setTimeout(r, 50));
        }
    }

    let res = await getValues()
    if (res.length > 0) {
        element.innerText = res[0].label
    } else {
        element.innerText = '-'
    }

}

class ModalHandler {
    constructor(element) {
        this.modal = new bootstrap.Modal(element);
        this.init();
    }

    init() {
        //this.createDragModal();
        this.modal.show();
        document.addEventListener('hidden.bs.modal', (event) => {
            console.log(event);
            event.target.remove();
        });
        this.dragElement(this.modal._element);
    }

    // Функция для перемещения модального окна
    dragElement(element) {
        const header = element.querySelector('.modal-header');
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

        header.onmousedown = dragMouseDown;

        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }

        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
        }

        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }
}

