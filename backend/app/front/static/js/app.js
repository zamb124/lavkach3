
async function choiceOneUUID(element, method) {
    var filter = element.getAttribute('filter')
    var model_name = element.getAttribute('model-name')
    var attrs = {
         placeholderValue: "Enter " + element.title
    }
    if (method==='get'||element.getAttribute('readonly')) {
       attrs.removeItemButton = false
    }else {
        attrs.removeItemButton = true
    }
    let choices = new Choices(element, attrs);
        if (method==='get'||element.getAttribute('readonly')) {
        choices.containerInner.element.classList.add('disabled');
        choices.disable()
    }
    function check_valid(event) {
        if (method === 'get'|| element.getAttribute('readonly')) { // Если метод get или reanonly, то нет смысла от валидования
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

    async function searchChoices(value) {
        try {
            const items = await fetch('/base/search?model=' + model_name + '&filter=' + filter + '&search=' + encodeURIComponent(value));
            const results = await items.json();
            if (0 === results.length) { // Handle error from result, for example.
                throw 'Empty!';
            }
            return results;
        } catch (err) {
            console.error(err);
        }
    }



    async function getValues() {
        var id__in = ''
        let value = await choices.getValue();
        try {
            if (!value) {
                return []
            } else {
                id__in = value.value
            }
            var maybe_cache = cache[id__in]
            if (maybe_cache) {
                return [{
                    value: id__in,
                    label: maybe_cache,
                }]
            }
            const items = await fetch('/base/get_by_ids?model=' + model_name + '&id__in=' + encodeURIComponent(id__in));
            const results = await items.json();
            for (let i = 0; i < results.length; i++) {
                cache[results[i].value] = results[i].label
            }
            if (0 === results.length) { // Handle error from result, for example.
                return []
            }
            return results;
        } catch (err) {
            console.error(err);
            return []
        }
    }

    let init_values = await getValues()
    choices.removeActiveItems()
    choices.clearChoices()
    choices.setValue(init_values)
    element.addEventListener('search', async e => {
        element.focus()
        let value = e.detail.value;
        choices.clearChoices()// Test!
        choices.setChoices(
            await searchChoices(value)
        )
    });

    check_valid()
    element.addEventListener('choice', function (event) {
        check_valid(event)
    });
    element.addEventListener('showDropdown', async e => {
        choices.clearChoices()// Test!
        choices.setChoices(
            await searchChoices('')
        )
    });
    element.addEventListener('removeItem', function (event) {
        check_valid(event)
    });
}


async function choiceMultiUUID(element) {
    var filter = element.getAttribute('filter')
    var model_name = element.getAttribute('model-name')
    var is_filter = element.getAttribute('is-filter')
    var title = element.getAttribute('display-title')
    var description = element.getAttribute('title')
    let choices = new Choices(element, {
        placeholder: true,
        placeholderValue: "Enter " + title,
        removeItemButton: true,
        description: description,
    });
    choices.containerInner.element.classList.add('form-control');
    if (element.getAttribute('readonly')) {
        choices.disable()
        choices.containerInner.element.classList.add('disabled');
    }

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

    async function getValues() {

        var id__in = ''
        let values = await choices.getValue();
        choices.setValue([])
        for (let v in values) {
            if (id__in === '') {
                id__in += values[v].value
            } else {
                id__in += ',' + values[v].value
            }
        }
        try {
            if (id__in === '') {
                return []
            }
            const items = await fetch('/base/get_by_ids?model=' + model_name + '&id__in=' + encodeURIComponent(id__in));
            const results = await items.json();
            if (0 === results.length) { // Handle error from result, for example.
                return []
            }
            return results;
        } catch (err) {
            console.error(err);
            choices.input.element.style = ""
            return []
        }
    }

    let init_values = await getValues()
    choices.removeActiveItems()
    choices.clearChoices()
    choices.setValue(init_values)
    element.addEventListener('search', async e => {
        element.focus()
        let value = e.detail.value;
        console.log(value);
        choices.clearChoices()// Test!
        choices.setChoices(async () => {
            try {
                const items = await fetch('/base/search?model=' + model_name + '&filter=' + filter + '&search=' + encodeURIComponent(value));
                const results = await items.json();
                if (0 === results.length) { // Handle error from result, for example.
                    throw 'Empty!';
                }
                return results;
            } catch (err) {
                console.error(err);
                choices.input.element.style = ""
            }
        }).then(() => {
            e.target.parentNode.querySelector('input').focus();
        });
        choices.input.element.style = ""
    });
    check_valid()
}

async function choiceMultiBabel() {
    var filter = element.getAttribute('filter')
    var model_name = element.getAttribute('model-name')
    var is_filter = element.getAttribute('is-filter')
    var title = element.getAttribute('display-title')
    var description = element.getAttribute('title')
    let choices = new Choices(element, {
        placeholderValue: "Enter {{ field.title }}",
        multiple: true,
        removeItemButton: true
    });
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
    var filter = element.getAttribute('filter')
    var model_name = element.getAttribute('model-name')
    var is_filter = element.getAttribute('is-filter')
    var title = element.getAttribute('display-title')
    var description = element.getAttribute('title')
    let choices = new Choices(element, {
        removeItemButton: true
    });
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
                const items = await fetch('/base/search?model='+ model_name +'&search=');
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