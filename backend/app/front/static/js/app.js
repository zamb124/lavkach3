// Initiate the class on page load
class App {
    constructor() {
        this.userSettings = {
            Layout: "vertical", // vertical | horizontal
            SidebarType: "mini-sidebar", // full | mini-sidebar
            BoxedLayout: true, // true | false
            Direction: "ltr", // ltr | rtl
            Theme: "light", // light | dark
            ColorTheme: "Cyan_Theme", // Blue_Theme | Aqua_Theme | Purple_Theme | Green_Theme | Cyan_Theme | Orange_Theme
            cardBorder: true, // true | false
            locale: "en"
        };
        this.cache = {
            temp: [],
            results: {}
        };
        this.user = {};
        this.loaded = false;
        this.userSettings = Object.assign({}, this.userSettings);
        this.locale = this.userSettings.locale;
        this.translations = {};
        Object.freeze(this.cache);
        this.initEventListeners();
        this.observeDOMClass('uuid', this.handleMyClass);
        this.runCacheHandler();
        this.initUserSettings();
        this.initTheme();
        this.initSidebarMenu();
        this.AdminSettingsInit();
        this.setSsettings();

        document.addEventListener("DOMContentLoaded", () => {
            this.onDocumentLoaded();
        });
    }


    // Методы Cache
    async pushUUID(model, uuid) {
        let modelList = this.cache.temp[model];
        if (!modelList) {
            this.cache.temp[model] = [];
            this.cache.temp[model].push(uuid);
        } else {
            if (!this.cache.temp[model].includes(uuid)) {
                this.cache.temp[model].push(uuid);
            }
        }
    }

    async runCacheHandler() {
        console.log('Бесконечно идем в цикл');
        while (true) {
            let promises = [];
            for (let model in this.cache.temp) {
                if (this.cache.temp[model].length > 0) {
                    let ids_str = this.cache.temp[model].join(',').toLowerCase();
                    const items = fetch('/base/get_by_ids?model=' + model + '&id__in=' + encodeURIComponent(ids_str));
                    promises.push(items);
                } else {
                    continue;
                }
                this.cache.temp[model] = [];
            }
            for (let i = 0; i < promises.length; i++) {
                var prom = promises[i];
                try {
                    const item = await prom;
                    const results = await item.json();
                    for (let j = 0; j < results.length; j++) {
                        var label = results[j].label || 'No Title';
                        this.cache.results[results[j].value] = label;
                    }
                } catch (e) {
                    console.error(e);
                }


            }
            await new Promise(r => setTimeout(r, 300));
            if (Object.keys(this.cache.results).length > 2000) {
                this.cache.results = Object.fromEntries(Object.entries(this.cache.results).slice(100));
            }
        }
    }

    // ------------

    // Htmx
    initEventListeners() {
        htmx.on("htmx:confirm", (e) => {

            console.log('htmx:confirm');
            let authToken = this.getCookieValue('token');
            if (authToken == null && window.location.pathname.indexOf('login') === -1) {
                e.preventDefault();
                window.history.pushState('Login', 'Login', '/basic/user/login');
                console.log('redirect login');
                document.location.replace('/basic/user/login');
            }
        });
        htmx.on("htmx:onLoad", (e) => { // Событие после загрузки контента
            console.log('htmx:onLoad');
        });

        htmx.on("htmx:afterSwap", (e) => {
            console.log('htmx:afterSwap');
        });

        htmx.on("htmx:configRequest", (e) => {
            e.detail.headers["Authorization"] = this.getCookieValue('token');
        })

        htmx.on("htmx:afterRequest", (e) => {
            if (this.authToken == null) {
                if (e.detail.xhr.status || 200) {
                    e.detail.shouldSwap = true;
                    e.detail.isError = false;
                }
            }
        });

        htmx.on('htmx:beforeSwap', (evt) => {
            if (evt.detail.xhr.status === 200) {
                console.log('BeforeSwap');
            } else if (evt.detail.xhr.status === 404) {
                this.showToast(evt.detail.pathInfo.requestPath + ' + ' + evt.detail.xhr.responseText, "#e94e1d");
            } else if (evt.detail.xhr.status === 403) {
                console.log('403');
                this.showToast(evt.detail.xhr.responseText.replace(/\\n/g, '\n'), "red");
            } else if (evt.detail.xhr.status === 401 && window.location.pathname.indexOf('login') === -1) {
                window.history.pushState('Login', 'Login', '/basic/user/login' + "?next=" + window.location.pathname);
                htmx.ajax('GET', '/basic/user/login', {
                    target: '#htmx_content', headers: {
                        'HX-Replace-Url': 'true'
                    }
                });
            } else if (evt.detail.xhr.status === 418) {
                evt.detail.shouldSwap = true;
                evt.detail.target = htmx.find("#teapot");
            } else if (evt.detail.xhr.status === 422) {
                const responseText = JSON.parse(evt.detail.xhr.responseText);
                if (responseText.detail) {
                    responseText.detail.forEach(error => {
                        const fieldName = error.loc[error.loc.length - 1];
                        let errorMessage = error.msg;

                        // Найти элементы, у которых name равен или содержит fieldName в квадратных скобках
                        let elements = document.querySelectorAll(`[name="${fieldName}"], [name*="[${fieldName}]"]`);
                        if (elements.length === 0) {
                            // Показать Toast на 5 секунд с цветом primary
                            Toastify({
                                text: `${fieldName}: ${errorMessage}`,
                                duration: 5000,
                                close: true,
                                style: {
                                    background: "var(--bs-primary)",
                                },
                            }).showToast();
                        } else {
                            elements.forEach(element => {
                                // Создать тултип
                                Toastify({
                                text: `${fieldName}: ${errorMessage}`,
                                duration: 5000,
                                close: true,
                                style: {
                                    background: "var(--bs-primary)",
                                },
                            }).showToast();
                            });
                        }
                    });
                }
            } else {
                const responseText = JSON.parse(evt.detail.xhr.responseText);
                if (responseText.detail) {

                    let message = app.translations[`t-${responseText.detail.code}`] || responseText.detail.msg || responseText.detail.code;
                    if (responseText.detail.args) {
                        for (const [key, value] of Object.entries(responseText.detail.args)) {
                            message = message.replace(`{${key}}`, value);
                        }
                    }
                    this.showToast(message, "#e94e1d");
                } else {
                    this.showToast(
                        evt.detail.xhr.responseText,
                        "#e94e1d",
                    );
                }
            }
        });

        htmx.on('htmx:wsConfigReceive', (e) => {
            console.log('wsConfigReceive');
            e.detail.headers["Authorization"] = this.getCookieValue('token');
        });

        htmx.on('htmx:wsConfigSend', (e) => {
            console.log('wsConfigSend');
            e.detail.headers["Authorization"] = this.getCookieValue('token');
        });
        htmx.on('htmx:wsBeforeMessage', this.handleMessage.bind(this));
    }

    showToast(message, background) {
        Toastify({
            text: message,
            duration: 3000,
            close: true,
            style: {
                background: background,
            },
        }).showToast();
    }

    // Методы работы с Websockets
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

    // Методы Auth
    getCookieValue(name) {
        const nameString = name + "=";
        const values = document.cookie.split(";").filter(item => item.indexOf(nameString) !== -1);
        if (values.length) {
            let value = values.find(val => val.trim().startsWith(nameString));
            if (value) {
                return value.substring(nameString.length + 1).trim();
            }
        }
        return null;
    }

    removeCookie(sKey, sPath, sDomain) {
        document.cookie = encodeURIComponent(sKey) +
            "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" +
            (sDomain ? "; domain=" + sDomain : "") +
            (sPath ? "; path=" + sPath : "/");
    }

    parseJwt(token) {
        var base64Url = token.split('.')[1];
        var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    }

    async fetchRoles() {
        if (!this.user || !this.user.role_ids) return;

        try {
            const response = await fetch('/api/roles', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({role_ids: this.user.role_ids})
            });

            if (response.ok) {
                const roles = await response.json();
                this.permits = roles;
            } else {
                console.error('Failed to fetch roles:', response.statusText);
            }
        } catch (error) {
            console.error('Error fetching roles:', error);
        }
    }

    login(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение формы
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const user = {
            username: username,
            password: password
        };
        fetch('/basic/user/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(user)
        }).then(response => {
            response.json().then(data => {
                this.saveTokensAndRedirect(data.token, data.refresh_token, data.next);
            });

        }).catch(error => {
            console.error('Error:', error);
        });
        setTimeout(() => {
        }, 500); // Задержка в 500 миллисекунд
    }

    async saveTokensAndRedirect(token, refresh_token, next) {
        this.user = this.parseJwt(token);
        const parsedToken = this.parseJwt(token);
        const parsedRefreshToken = this.parseJwt(refresh_token);
        const tokenExpires = new Date(parsedToken.exp * 1000);
        const refreshTokenExpires = new Date(parsedRefreshToken.exp * 1000);

        document.cookie = `token=${token}; expires=${tokenExpires.toUTCString()}; path=/;`;
        document.cookie = `refresh_token=${refresh_token}; expires=${refreshTokenExpires.toUTCString()}; path=/;`;
        await this.fetchRoles();
        let redirectUrl;
        if (this.user.company_ids && this.user.company_ids.length > 0) {
            redirectUrl = next || '/';
        } else {
            redirectUrl = '/company/create';
        }
        window.location.replace(redirectUrl);
    }

    async getUser() {
        await this.refreshToken()
    }

    async refreshToken() {
        const token = this.getCookieValue('token')?.replace('=', '');
        const refreshToken = this.getCookieValue('refresh_token')?.replace('=', '');

        if (!token || !refreshToken) return false;

        for (let attempt = 0; attempt < 15; attempt++) {
            const response = await fetch('/basic/user/refresh', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({token, refresh_token: refreshToken})
            });

            if (response.ok) {
                const result = await response.json();
                const parsedToken = this.parseJwt(result.token);
                const expires = new Date(parsedToken.exp * 1000);

                document.cookie = `token=${result.token}; expires=${expires.toUTCString()}; path=/;`;
                document.cookie = `refresh_token=${result.token}; expires=${expires.toUTCString()}; path=/;`;

                this.user = parsedToken;
                await this.fetchRoles();
                return true;
            }

            await new Promise(r => setTimeout(r, 1000)); // Задержка в 1 секунду перед следующей попыткой
        }

        // Если все попытки неудачны, удаляем куки
        this.removeCookie('token');
        this.removeCookie('refresh_token');
        return false;
    }

    async checkAuth() {
        let authToken = this.getCookieValue('token') || this.getCookieValue('refresh_token');
        if (!authToken) return false;

        let tokenData = this.parseJwt(authToken);
        if (tokenData.exp <= Date.now() / 1000) {
            await this.refreshToken();
            authToken = this.getCookieValue('token');
            if (!authToken) return false;
        }
        return true;
    }

    async onDocumentLoaded() {
        htmx.onLoad(function (elt) {
            if (!app.loaded) {
                // Смотрим, если все элементы прогрузились
                var ver = document.getElementsByClassName('with-vertical')
                var hor = document.getElementsByClassName('with-horizontal')
                var themeEditor = document.getElementById('offcanvasExample')
                if (ver.length > 1 && hor.length > 1 && themeEditor) {
                    //app.AdminSettingsInit() // Применяем пользовательские настройки фронта
                    app.setSsettings() // Применяем скрипты темы
                    //app.initSidebarMenu() // Прогружаем navbar
                    app.loaded = true; // Устанавливаем флаг, что все прогрузили
                }
            }
            var elements = elt.querySelectorAll('[data-key], [data-key-description]');
            if (elements) {
                elements.forEach(app.translateElement);
            }

            var elements_tooltips = elt.querySelectorAll('[data-bs-toggle="tooltip"]');
            var tooltipList = Array.from(elements_tooltips).map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    delay: {"show": 500, "hide": 500}
                });
            });

            const elmts = elt.querySelectorAll('.modal, .uuid-create, .uuid-update, .list-uuid-create, .list-uuid-update, .uuid-get, .list-uuid-get, .babel-create, .babel-update, .list-str, .list-enum-update, .list-enum-get, .list-enum-create, .list-rel');
            if (elt.classList.contains('modal')) {
                new ModalHandler(elt);
            }
            elmts.forEach(element => {
                if (element.classList.contains('modal')) {
                    new ModalHandler(element);
                } else if (element.classList.contains('uuid-update') || element.classList.contains('list-uuid-update')) {
                    new ChoiceHandler(element, 'update');
                } else if (element.classList.contains('uuid-create') || element.classList.contains('list-uuid-create')) {
                    new ChoiceHandler(element, 'create');
                } else if (element.classList.contains('uuid-get')) {
                    setTitle(element, 'get');
                } else if (element.classList.contains('list-uuid-get')) {
                    choicesMultiBadges(element, 'get');
                } else if (element.classList.contains('list-uuid-update')) {
                    new ChoiceHandler(element, 'update');
                } else if (element.classList.contains('list-enum-update')) {
                    choiceMultiEnum(element, 'update');
                } else if (element.classList.contains('list-enum-create')) {
                    choiceMultiEnum(element, 'create');
                } else if (element.classList.contains('babel-create') || element.classList.contains('babel-update')) {
                    choiceMultiBabel(element, 'update');
                } else if (element.classList.contains('list-str')) {
                    let choices = new Choices(element, {
                        placeholderValue: "Enter...",
                        multiple: true,
                        removeItemButton: true
                    });
                    choices.containerInner.element.classList.add('form-control');
                } else if (element.classList.contains('list-enum-update') || element.classList.contains('list-enum-get')) {
                    choiceMultiEnum(element, 'update');
                } else if (element.classList.contains('list-enum-create')) {
                    choicesMultiBadges(element, 'create');
                } else if (element.classList.contains('list-rel') || element.classList.contains('list-enum-get')) {
                    let choices = new Choices(element, {
                        placeholderValue: "Enter ....",
                        multiple: true,
                        removeItemButton: true
                    });
                    choices.containerInner.element.classList.add('form-control');
                    choices.containerInner.element.classList.add('disabled');

                    function check_valid(event) {
                        if (element.required) {
                            if (event) {
                                if (event.type === 'choice') {
                                    if (event.detail.choice.value) {
                                        choices.containerInner.element.classList.remove('is-invalid');
                                        choices.containerInner.element.classList.add('is-valid');
                                    }
                                } else if (event.type === 'removeItem') {
                                    if (event.detail.value) {
                                        choices.containerInner.element.classList.add('is-invalid');
                                        choices.containerInner.element.classList.remove('is-valid');
                                    }
                                }

                            } else {
                                choices.containerInner.element.classList.add('is-invalid');
                                choices.containerInner.element.classList.remove('is-valid');
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

                    check_valid()
                }
            });
        })
        await this.setLocale(this.userSettings.locale);
        // Здесь можно вызвать любые другие методы или выполнить нужные действия

    }


    // Методы интернацианализации
    async setLocale(newLocale) {
        document.getElementsByTagName('html')[0].setAttribute('lang', newLocale);
        this.userSettings.locale = newLocale;
        document.cookie = "locale=" + this.userSettings.locale + ";path=/;";
        //if (newLocale === this.locale) return;

        const newTranslations = await this.fetchTranslationsFor(newLocale);

        this.locale = newLocale;
        this.translations = newTranslations;

        this.translatePage();
    }

    async fetchTranslationsFor(newLocale) {
        const response = await fetch(`/static/i18n/${newLocale}.json`);
        return await response.json();
    }

    translatePage() {
        document.querySelectorAll("[data-key]").forEach(element => this.translateElement(element));
    }

    translateElement(element) {
        const key = element.getAttribute("data-key");
        if (key) {
            const translation = app.translations[key];
            if (!translation) {
                console.warn(`No translation found for key: ${key}`);
            } else {
                element.innerText = translation;
            }
        }


        const keyDescription = element.getAttribute("data-key-description");
        if (keyDescription) {
            const descriptionTranslation = app.translations[keyDescription];
            if (!descriptionTranslation) {
                console.warn(`No translation found for key description: ${keyDescription}`);
            } else {
                element.setAttribute("title", descriptionTranslation);
            }
        }
    }

    // -------

    // Новый метод для обработки появления определенного класса в DOM-дереве (пригодиться)
    observeDOMClass(className, callback) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains(className)) {
                        callback(node);
                    }
                });
            });
        });
        observer.observe(document.body, {childList: true, subtree: true});
    }

    handleMyClass(element) {
        //console.log('Элемент с классом my-class добавлен в DOM:', element);
        // Добавьте здесь обработчик для элемента
    }

    // Методы работы со стилем и прочим
    AdminSettingsInit() {
        this.ManageThemeLayout();
        this.ManageSidebarType();
        this.ManageBoxedLayout();
        this.ManageDirectionLayout();
        this.ManageDarkThemeLayout();
        this.ManageColorThemeLayout();
        this.ManageCardLayout();
    }

    initTheme() {
        document.addEventListener("DOMContentLoaded", () => {
            "use strict";
            // Tooltip
            const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

            // Popover
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

            // Hide preloader
            const preloader = document.querySelector(".preloader");
            if (preloader) {
                preloader.style.display = "none";
            }

            // Increment & Decrement
            const quantityButtons = document.querySelectorAll(".minus, .add");
            if (quantityButtons) {
                quantityButtons.forEach(button => {
                    button.addEventListener("click", () => {
                        const qtyInput = button.closest("div").querySelector(".qty");
                        let currentVal = parseInt(qtyInput.value);
                        const isAdd = button.classList.contains("add");

                        if (!isNaN(currentVal)) {
                            qtyInput.value = isAdd ? ++currentVal : currentVal > 0 ? --currentVal : currentVal;
                        }
                    });
                });
            }
        });
    }

    initSidebarMenu() {
        const sidebarMenu = () => {
            const at = document.documentElement.getAttribute("data-layout");
            if (at === "vertical") {
                this.loadSidebarPagesVertical();
            } else if (at === "horizontal") {
                this.loadSidebarPagesHorizontal();
            }
        };

        sidebarMenu();
    }

    loadSidebarPagesVertical() {
        "use strict";
        const isSidebar = document.getElementsByClassName("side-mini-panel");
        if (isSidebar.length > 0) {
            const url = window.location + "";
            const path = url.replace(window.location.protocol + "//" + window.location.host + "/", "");

            const findMatchingElement = () => {
                const currentUrl = window.location.href;
                const anchors = document.querySelectorAll("#sidebarnav a");
                for (let i = 0; i < anchors.length; i++) {
                    if (anchors[i].href === currentUrl) {
                        return anchors[i];
                    }
                }
                document.location.replace('/inventory/order');
            };

            const elements = findMatchingElement();
            if (elements) {
                elements.classList.add("active");
            }

            document.querySelectorAll("#sidebarnav a").forEach(link => {
                link.addEventListener("click", function (e) {
                    const isActive = this.classList.contains("active");
                    const parentUl = this.closest("ul");

                    if (!isActive) {
                        parentUl.querySelectorAll("ul").forEach(submenu => submenu.classList.remove("in"));
                        parentUl.querySelectorAll("a").forEach(navLink => navLink.classList.remove("active"));

                        const submenu = this.nextElementSibling;
                        if (submenu) {
                            submenu.classList.add("in");
                        }
                        this.classList.add("active");
                    } else {
                        this.classList.remove("active");
                        parentUl.classList.remove("active");
                        const submenu = this.nextElementSibling;
                        if (submenu) {
                            submenu.classList.remove("in");
                        }
                    }
                });
            });

            document.querySelectorAll("#sidebarnav > li > a.has-arrow").forEach(link => {
                link.addEventListener("click", function (e) {
                    e.preventDefault();
                });
            });

            const closestNav = elements.closest("nav[class^=sidebar-nav]");
            const menuid = (closestNav && closestNav.id) || "menu-right-mini-1";
            const menu = menuid.split('-').pop();

            document.getElementById("menu-right-" + menu).classList.add("d-block");
            document.getElementById("mini-" + menu).classList.add("selected");

            document.querySelectorAll("ul#sidebarnav ul li a.active").forEach(link => {
                link.closest("ul").classList.add("in");
                link.closest("ul").parentElement.classList.add("selected");
            });

            document.querySelectorAll(".mini-nav .mini-nav-item").forEach(item => {
                item.addEventListener("click", function () {
                    const id = this.id.split('-').pop();
                    document.querySelectorAll(".mini-nav .mini-nav-item").forEach(navItem => navItem.classList.remove("selected"));
                    this.classList.add("selected");
                    document.querySelectorAll(".sidebarmenu nav").forEach(nav => nav.classList.remove("d-block"));
                    document.getElementById("menu-right-" + id).classList.add("d-block");
                    document.body.setAttribute("data-sidebartype", "full");
                });
            });
        }
    }

    loadSidebarPagesHorizontal() {
        const findMatchingElement = () => {
            const currentUrl = window.location.href;
            const anchors = document.querySelectorAll("#sidebarnavh ul#sidebarnav a");
            for (let i = 0; i < anchors.length; i++) {
                if (anchors[i].href === currentUrl) {
                    return anchors[i];
                }
            }
            return null;
        };

        const elements = findMatchingElement();
        if (elements) {
            elements.classList.add("active");
        }

        document.querySelectorAll("#sidebarnavh ul#sidebarnav a.active").forEach(link => {
            link.closest("a").parentElement.classList.add("selected");
            link.closest("ul").parentElement.classList.add("selected");
        });
    }

    initUserSettings() {
        const settings = ["Layout", "SidebarType", "BoxedLayout", "Direction", "Theme", "ColorTheme", "cardBorder", "locale"];
        settings.forEach(setting => {
            const value = this.getCookieValue(setting);
            if (value) {
                this.userSettings[setting] = value;
            } else {
                document.cookie = `${setting}=${this.userSettings[setting]};path=/;`;
            }
        });
    }


    ManageThemeLayout() {
        const horizontalLayoutElement = document.getElementById("horizontal-layout");
        const verticalLayoutElement = document.getElementById("vertical-layout");

        switch (this.userSettings.Layout) {
            case "horizontal":
                if (horizontalLayoutElement) {
                    horizontalLayoutElement.checked = true;
                }
                document.documentElement.setAttribute("data-layout", "horizontal");
                break;
            case "vertical":
                if (verticalLayoutElement) {
                    verticalLayoutElement.checked = true;
                }
                document.documentElement.setAttribute("data-layout", "vertical");
                break;
            default:
                break;
        }
    }

    ManageSidebarType() {
        switch (this.userSettings.SidebarType) {
            case "full":
                const fullSidebarElement = document.querySelector("#full-sidebar");
                if (fullSidebarElement) {
                    fullSidebarElement.checked = true;
                }
                document.body.setAttribute("data-sidebartype", "full");

                const setSidebarType = () => {
                    const width = window.innerWidth > 0 ? window.innerWidth : screen.width;
                    if (width < 1300) {
                        document.body.setAttribute("data-sidebartype", "mini-sidebar");
                    } else {
                        document.body.setAttribute("data-sidebartype", "full");
                    }
                };
                window.addEventListener("DOMContentLoaded", setSidebarType);
                window.addEventListener("resize", setSidebarType);
                break;

            case "mini-sidebar":
                const miniSidebarElement = document.querySelector("#mini-sidebar");
                if (miniSidebarElement) {
                    miniSidebarElement.checked = true;
                }
                document.body.setAttribute("data-sidebartype", "mini-sidebar");
                break;

            default:
                break;
        }
    }

    ManageBoxedLayout() {
        const boxedLayoutElement = document.getElementById("boxed-layout");
        const fullLayoutElement = document.getElementById("full-layout");
        if (boxedLayoutElement) boxedLayoutElement.checked = true;
        switch (this.userSettings.BoxedLayout) {
            case true:
                document.documentElement.setAttribute("data-boxed-layout", "boxed");
                if (boxedLayoutElement) boxedLayoutElement.checked = true;
                break;
            case false:
                document.documentElement.setAttribute("data-boxed-layout", "full");
                if (fullLayoutElement) fullLayoutElement.checked = true;
                break;
            default:
                break;
        }
    }

    ManageDirectionLayout() {
        const ltrLayoutElement = document.getElementById("ltr-layout");
        const rtlLayoutElement = document.getElementById("rtl-layout");

        switch (this.userSettings.Direction) {
            case "ltr":
                if (ltrLayoutElement) {
                    ltrLayoutElement.checked = true;
                }
                document.documentElement.setAttribute("dir", "ltr");
                const offcanvasStart = document.querySelector(".offcanvas-start");
                if (offcanvasStart) {
                    offcanvasStart.classList.toggle("offcanvas-end");
                    offcanvasStart.classList.remove("offcanvas-start");
                }
                break;
            case "rtl":
                document.documentElement.setAttribute("dir", "rtl");
                const offcanvasEnd = document.querySelector(".offcanvas-end");
                if (offcanvasEnd) {
                    offcanvasEnd.classList.toggle("offcanvas-start");
                    offcanvasEnd.classList.remove("offcanvas-end");
                }
                if (rtlLayoutElement) {
                    rtlLayoutElement.checked = true;
                }
                break;
            default:
                break;
        }
    }

    ManageCardLayout() {
        const cardWithoutBorderElement = document.getElementById("card-without-border");
        const cardWithBorderElement = document.getElementById("card-with-border");

        if (cardWithoutBorderElement) cardWithoutBorderElement.checked = true;
        switch (this.userSettings.cardBorder) {
            case true:
                document.documentElement.setAttribute("data-card", "border");
                if (cardWithBorderElement) cardWithBorderElement.checked = true;
                break;
            case false:
                document.documentElement.setAttribute("data-card", "shadow");
                if (cardWithoutBorderElement) cardWithoutBorderElement.checked = true;
                break;
            default:
                break;
        }
    }

    ManageDarkThemeLayout() {
        const setTheme = (theme, hideElements, showElements, hideElements2) => {
            document.documentElement.setAttribute("data-bs-theme", theme);
            const themeLayoutElement = document.getElementById(`${theme}-layout`);
            if (themeLayoutElement) {
                themeLayoutElement.checked = true;
            }

            hideElements.forEach((el) =>
                document.querySelectorAll(`.${el}`).forEach((e) => (e.style.display = "none"))
            );
            showElements.forEach((el) =>
                document.querySelectorAll(`.${el}`).forEach((e) => (e.style.display = "flex"))
            );
            hideElements2.forEach((el) =>
                document.querySelectorAll(`.${el}`).forEach((e) => (e.style.display = "none"))
            );
        };

        switch (this.userSettings.Theme) {
            case "light":
                setTheme("light", ["light-logo"], ["moon"], ["sun"]);
                break;
            case "dark":
                setTheme("dark", ["dark-logo"], ["sun"], ["moon"]);
                break;
            default:
                break;
        }
    }

    ManageColorThemeLayout() {
        const {ColorTheme} = this.userSettings;
        const colorThemeElement = document.getElementById(ColorTheme);
        document.documentElement.setAttribute("data-color-theme", ColorTheme);
    }

    setSsettings() {
        // Theme Direction RTL LTR click
        function handleDirection() {
            const rtlLayoutElement = document.getElementById("rtl-layout");
            const ltrLayoutElement = document.getElementById("ltr-layout");

            if (rtlLayoutElement) {
                rtlLayoutElement.addEventListener("click", function () {
                    document.documentElement.setAttribute("dir", "rtl");
                    const offcanvasEnd = document.querySelector(".offcanvas-end");
                    if (offcanvasEnd) {
                        offcanvasEnd.classList.toggle("offcanvas-start");
                        offcanvasEnd.classList.remove("offcanvas-end");
                    }
                });
                document.cookie = "Direction=" + "rtl" + ";path=/;"
            }

            if (ltrLayoutElement) {
                ltrLayoutElement.addEventListener("click", function () {
                    document.documentElement.setAttribute("dir", "ltr");
                    const offcanvasStart = document.querySelector(".offcanvas-start");
                    if (offcanvasStart) {
                        offcanvasStart.classList.toggle("offcanvas-end");
                        offcanvasStart.classList.remove("offcanvas-start");
                    }
                });
                document.cookie = "Direction=" + "ltr" + ";path=/;"
            }
        }

        handleDirection();

        // Theme Layout Box or Full
        function handleBoxedLayout() {
            const boxedLayout = document.getElementById("boxed-layout");
            const fullLayout = document.getElementById("full-layout");
            const containerFluid = document.querySelectorAll(".container-fluid");
            if (boxedLayout) {
                boxedLayout.addEventListener("click", function () {
                    containerFluid.forEach((element) => element.classList.remove("mw-100"));
                    document.documentElement.setAttribute("data-boxed-layout", "boxed");
                    this.checked;
                    document.cookie = "BoxedLayout=" + "true" + ";path=/;"
                });
            }

            if (fullLayout) {
                fullLayout.addEventListener("click", function () {
                    containerFluid.forEach((element) => element.classList.add("mw-100"));
                    document.documentElement.setAttribute("data-boxed-layout", "full");
                    this.checked;
                    document.cookie = "BoxedLayout=" + "false" + ";path=/;"
                });
            }
        }

        handleBoxedLayout();

        // Theme Layout Vertical or Horizontal
        function handleLayout() {
            const verticalLayout = document.getElementById("vertical-layout");
            const horizontalLayout = document.getElementById("horizontal-layout");

            if (verticalLayout) {
                verticalLayout.addEventListener("click", function () {
                    document.documentElement.setAttribute("data-layout", "vertical");
                    this.checked;
                    document.cookie = "Layout=" + "vertical" + ";path=/;"
                });
            }

            if (horizontalLayout) {
                horizontalLayout.addEventListener("click", function () {
                    document.documentElement.setAttribute("data-layout", "horizontal");
                    this.checked;
                    document.cookie = "Layout=" + "horizontal" + ";path=/;"
                });
            }
        }

        handleLayout();

        // Theme mode Dark or Light
        function handleTheme() {
            function setThemeAttributes(
                theme,
                darkDisplay,
                lightDisplay,
                sunDisplay,
                moonDisplay
            ) {
                document.documentElement.setAttribute("data-bs-theme", theme);
                const themeLayoutElement = document.getElementById(`${theme}-layout`);
                if (themeLayoutElement) {
                    themeLayoutElement.checked = true;
                }
                if (theme == 'dark') {
                    document.cookie = "Theme=" + "dark" + ";path=/;"
                } else {
                    document.cookie = "Theme=" + "light" + ";path=/;"
                }

                document.querySelectorAll(`.${darkDisplay}`)
                    .forEach((el) => (el.style.display = "none"));
                document.querySelectorAll(`.${lightDisplay}`)
                    .forEach((el) => (el.style.display = "flex"));
                document.querySelectorAll(`.${sunDisplay}`)
                    .forEach((el) => (el.style.display = "none"));
                document.querySelectorAll(`.${moonDisplay}`)
                    .forEach((el) => (el.style.display = "flex"));
            }

            document.querySelectorAll(".dark-layout").forEach((element) => {
                element.addEventListener("click", () =>
                    setThemeAttributes("dark", "dark-logo", "light-logo", "moon", "sun")
                );
            });

            document.querySelectorAll(".light-layout").forEach((element) => {
                element.addEventListener("click", () =>
                    setThemeAttributes("light", "light-logo", "dark-logo", "sun", "moon")
                );
            });
        }

        handleTheme();

        // Theme card with Border or Shadow
        function handleCardLayout() {
            function setCardAttribute(cardType) {
                document.documentElement.setAttribute("data-card", cardType);
            }

            const cardWithBorderElement = document.getElementById("card-with-border");
            const cardWithoutBorderElement = document.getElementById(
                "card-without-border"
            );

            if (cardWithBorderElement) {
                cardWithBorderElement.addEventListener("click", () =>
                    setCardAttribute("border")
                );
            }
            if (cardWithoutBorderElement) {
                cardWithoutBorderElement.addEventListener("click", () =>
                    setCardAttribute("shadow")
                );
            }
        }

        handleCardLayout();

        // Theme Sidebar
        function handleSidebarToggle() {
            function setSidebarType(sidebarType) {
                document.body.setAttribute("data-sidebartype", sidebarType);
            }

            const fullSidebarElement = document.getElementById("full-sidebar");
            const miniSidebarElement = document.getElementById("mini-sidebar");

            if (fullSidebarElement) {
                fullSidebarElement.addEventListener("click", () =>
                    setSidebarType("full")
                );
                document.cookie = "SidebarType=" + "full" + ";path=/;"
            }
            if (miniSidebarElement) {
                miniSidebarElement.addEventListener("click", () =>
                    setSidebarType("mini-sidebar")
                );
                document.cookie = "SidebarType=" + "mini-sidebar" + ";path=/;"
            }
        }

        handleSidebarToggle();

        // Toggle Sidebar
        function handleSidebar() {
            document.querySelectorAll(".sidebartoggler").forEach((element) => {
                element.addEventListener("click", function () {
                    document.querySelectorAll(".sidebartoggler").forEach((el) => {
                        el.checked = true;
                    });
                    document
                        .getElementById("main-wrapper")
                        .classList.toggle("show-sidebar");
                    document.querySelectorAll(".sidebarmenu").forEach((el) => {
                        el.classList.toggle("close");
                    });
                    const dataTheme = document.body.getAttribute("data-sidebartype");
                    if (dataTheme === "full") {
                        document.body.setAttribute("data-sidebartype", "mini-sidebar");
                        document.cookie = "SidebarType=" + "mini-sidebar" + ";path=/;"
                    } else {
                        document.body.setAttribute("data-sidebartype", "full");
                        document.cookie = "SidebarType=" + "full" + ";path=/;"
                    }
                });
            });
        }

        handleSidebar();
    }
}


// Инициализация класса App
const app = new App();
document.write('<script src="/static/js/element_hendlers.js"></script>');

