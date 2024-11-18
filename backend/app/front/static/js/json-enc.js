htmx.defineExtension('json-enc', {
    onEvent: function (name, evt) {
        if (name === "htmx:configRequest") {
            evt.detail.headers['Content-Type'] = "application/json";
        }
    },


    encodeParameters: function (xhr, parameters, elt) {
        xhr.overrideMimeType('text/json');

        // Преобразование параметров в нужный формат
        let result = {};
        for (const [key, value] of Object.entries(parameters)) {
            if (key === 'search_terms') {
                continue; // Пропустить ключ 'search_terms'
            }
            const match = key.match(/(\w+)\[(\w+)\]\[(\w+)\]/);
            if (match) {
                const [_, listName, uuid, fieldName] = match;
                if (!result[listName]) {
                    result[listName] = {};
                }
                if (!result[listName][uuid]) {
                    result[listName][uuid] = {};
                }
                result[listName][uuid][fieldName] = value;
            } else {
                result[key] = value;
            }

            // Проверка наличия атрибута multiple и преобразование значения
            const element = elt.querySelector(`[name="${key}"]`);
            if (element && element.tagName === 'SELECT' && element.multiple) {
                if (typeof value === 'string') {
                    result[key] = value === '' ? [] : [value];
                }
            }

            // Проверка, заканчивается ли key на _ids и преобразование значения
            if (key.endsWith('_ids') && typeof value === 'string') {
                result[key] = value === '' ? [] : [value];
            }
        }

        function replaceEmptyStrings(obj) {
            if (typeof obj === 'string' && obj === '') {
                return null;
            } else if (Array.isArray(obj)) {
                return obj
            } else if (typeof obj === 'object' && obj !== null) {
                const newObj = {};
                for (const key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        newObj[key] = replaceEmptyStrings(obj[key]);
                    }
                }
                return newObj;
            }
            return obj;
        }

    // Преобразование объектов в списки только для тех, которые соответствуют паттерну
        for (const listName in result) {
            if (result.hasOwnProperty(listName) && typeof result[listName] === 'object' && !Array.isArray(result[listName])) {
                result[listName] = Object.values(result[listName]);
            }
        }

// Замена пустых строк на null рекурсивно
        result = replaceEmptyStrings(result);

        return JSON.stringify(result);
    }
});