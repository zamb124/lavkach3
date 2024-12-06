htmx.defineExtension('json-enc', {
    onEvent: function (name, evt) {
        if (name === "htmx:configRequest") {
            evt.detail.headers['Content-Type'] = "application/json";
        }
    },

    encodeParameters: function (xhr, parameters, elt) {
        xhr.overrideMimeType('text/json');

        let result = {};
        for (const [key, value] of Object.entries(parameters)) {
            if (key === 'search_terms') {
                continue;
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

            const element = elt.querySelector(`[name="${key}"]`);
            if (element && element.tagName === 'SELECT' && element.multiple) {
                if (typeof value === 'string') {
                    result[key] = value === '' ? [] : [value];
                }
            }

            if (key.endsWith('_ids') && typeof value === 'string') {
                result[key] = value === '' ? [] : [value];
            }
        }

        function replaceEmptyStrings(obj) {
            if (typeof obj === 'string' && obj === '') {
                return null;
            } else if (Array.isArray(obj)) {
                return obj.map(replaceEmptyStrings);
            } else if (typeof obj === 'object' && obj !== null) {
                const newObj = {};
                for (const key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        if (key.startsWith('is_') && Array.isArray(obj[key]) && obj[key].length === 2) {
                            newObj[key] = true;
                        } else {
                            newObj[key] = replaceEmptyStrings(obj[key]);
                        }
                    }
                }
                return newObj;
            } else {
                return obj;
            }
        }

        for (const listName in result) {
            if (result.hasOwnProperty(listName) && typeof result[listName] === 'object' && !Array.isArray(result[listName])) {
                result[listName] = Object.values(result[listName]);
            }
        }

       // result = replaceEmptyStrings(result);

        return JSON.stringify(result);
    }
});