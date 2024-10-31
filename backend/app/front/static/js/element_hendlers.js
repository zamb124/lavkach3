class ChoiceHandler {
    constructor(elId, method) {
        this.element = document.getElementById(elId);
        this.method = method;
        this.displayTitle = this.element.getAttribute('display-title');
        this.filter = this.element.getAttribute('filter');
        this.isFilter = this.element.getAttribute('is-filter');
        this.modelName = this.element.getAttribute('model-name');
        this.attrs = {
            placeholder: true,
            searchPlaceholderValue: 'Start typing to search',
            placeholderValue: "Enter " + this.displayTitle,
            removeItemButton: !(method === 'get' || this.element.getAttribute('readonly'))
        };
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
        this.checkValid();

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
            this.choices.containerInner.element.classList.remove('is-invalid');
        } else {
            this.choices.containerInner.element.classList.add('is-valid');
        }
    }

    async searchChoices(value) {
        try {
            const items = await fetch(`/base/search?model=${this.modelName}&filter=${this.filter}&search=${encodeURIComponent(value)}`);
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
        if (!value){
            return []
        } else if (!Array.isArray(value)) {
            values.push(value);
        } else {
            values = value;
        }

        for (let v in values) {
            var maybe_cache = cache.results[v]
            if (!maybe_cache) {
                cache.pushUUID(this.modelName, values[v].value)
            }
        }
        var result = []
        while (true) {
            for (let v in values) {
                id__in = values[v].value
                if (cache.results[id__in]) {
                    result.push({
                        value: values[v].label,
                        label: cache.results[id__in]
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

async function choicesMultiBadges(elId, method) {
    let element = document.getElementById(elId);
    var model_name = element.getAttribute('model-name')

    async function getValues() {
        var id__in = ''
        var str = element.innerText.replace(/[\s\n\t]+/g, ' ').trim()
        let values = str ? str.split(',') : [];

        for (let v in values) {
            var maybe_cache = cache.results[values[v]]
            if (!maybe_cache) {
                cache.pushUUID(model_name, values[v])
            }
        }
        var result = []
        while (true) {
            for (let v in values) {
                if (cache.results[values[v]]) {
                    result.push({
                        value: values[v],
                        label: cache.results[values[v]]
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

        element.insertAdjacentHTML('beforeend', '<span class="badge bg-secondary">' + line.label + '</span>');
    });
}

async function choiceMultiBabel() {
    var display_title = element.getAttribute('display-title')
    var filter = element.getAttribute('filter')
    var is_filter = element.getAttribute('is-filter')
    var model_name = element.getAttribute('model-name')
    var attrs = {
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

async function choiceOneBabel() {
    var display_title = element.getAttribute('display-title')
    var filter = element.getAttribute('filter')
    var is_filter = element.getAttribute('is-filter')
    var model_name = element.getAttribute('model-name')
    var attrs = {
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

async function choiceMultiEnum(element, method) {
    var display_title = element.getAttribute('display-title')
    var filter = element.getAttribute('filter')
    var is_filter = element.getAttribute('is-filter')
    var model_name = element.getAttribute('model-name')
    var attrs = {
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


class ModalHandler {
    constructor(modalId) {
        this.modal = new bootstrap.Modal(modalId);
        this.init();
    }

    init() {
        this.createDragModal();
        this.modal.show();
        document.addEventListener('hidden.bs.modal', (event) => {
            console.log(event);
            event.target.remove();
        });
    }

    createDragModal() {
        const header = this.modal._element.querySelector('.modal-header');
        header.onmousedown = (e) => {
            const offsetX = e.clientX - this.modal._element.getBoundingClientRect().left;
            const offsetY = e.clientY - this.modal._element.getBoundingClientRect().top;

            const mouseMoveHandler = (e) => {
                this.modal._element.style.position = 'absolute';
                this.modal._element.style.left = `${e.clientX - offsetX}px`;
                this.modal._element.style.top = `${e.clientY - offsetY}px`;
            };

            const mouseUpHandler = () => {
                document.removeEventListener('mousemove', mouseMoveHandler);
                document.removeEventListener('mouseup', mouseUpHandler);
            };

            document.addEventListener('mousemove', mouseMoveHandler);
            document.addEventListener('mouseup', mouseUpHandler);
        };
    }
}
