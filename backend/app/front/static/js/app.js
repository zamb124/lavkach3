class CacheHandler {
    constructor() {
        this.temp = [];
        this.results = {};
        Object.freeze(this);
        this.run();
    }

    async pushUUID(model, uuid) {
        let modelList = this.temp[model];
        if (!modelList) {
            this.temp[model] = [];
            this.temp[model].push(uuid);
        } else {
            if (!this.temp[model].includes(uuid)) {
                this.temp[model].push(uuid);
            }
        }
    }

    async run() {
        console.log('Бесконечно идем в цикл');
        while (true) {
            let promises = [];
            for (let model in this.temp) {
                if (this.temp[model].length > 0) {
                    let ids_str = this.temp[model].join(',');
                    const items = fetch('/base/get_by_ids?model=' + model + '&id__in=' + encodeURIComponent(ids_str));
                    promises.push(items);
                } else {
                    continue;
                }
                this.temp[model] = [];
            }
            for (let i = 0; i < promises.length; i++) {
                const item = await promises[i];
                const results = await item.json();
                for (let j = 0; j < results.length; j++) {
                    var label = results[j].label || 'No Title';
                    this.results[results[j].value] = label;
                }
            }
            await new Promise(r => setTimeout(r, 300));
            if (Object.keys(this.results).length > 2000) {
                this.results = Object.fromEntries(Object.entries(this.results).slice(100));
            }
        }
    }
}

class AuthHandler {
    constructor() {
        this.initEventListeners();
    }

    getCookieValue(name) {
        const nameString = name + "=";
        const values = document.cookie.split(";").filter(item => item.includes(nameString));
        if (values.length) {
            let value = values.find(val => val.trim().startsWith(nameString));
            if (value) {
                return value.substring(nameString.length).trim();
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

    async refreshToken() {
        let user = {
            token: this.getCookieValue('token').replace('=', ''),
            refresh_token: this.getCookieValue('refresh_token').replace('=', '')
        };
        console.log('refreshing token');
        let response = await fetch('/basic/user/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(user)
        });
        let result = await response.json();
        const parsed = this.parseJwt(result.token);
        const expires = new Date(parsed.exp * 1000);
        document.cookie = "token=" + result.token + "; expires=" + expires + ";path=/;";
        document.cookie = "refresh_token=" + result.token + "; expires=" + expires + ";path=/;";
        return true;
    }

    async checkAuth() {
        var authToken = this.getCookieValue('token');
        if (!authToken) {
            authToken = this.getCookieValue('refresh_token');
            if (authToken) {
                await this.refreshToken();
                authToken = this.getCookieValue('token');
            }
        }
        if (!authToken) {
            return false;
        }
        var tokenData = this.parseJwt(authToken);
        var now = Date.now() / 1000;
        if (tokenData.exp <= now) {
            await this.refreshToken();
        }
        return true;
    }

    initEventListeners() {
        htmx.on("htmx:confirm", async (e) => {
            let authToken = this.getCookieValue('token');
            if (authToken == null && !window.location.pathname.includes('login')) {
                e.preventDefault();
                window.history.pushState('Login', 'Login', '/basic/user/login');
                console.log('redirect login');
                document.location.replace('/basic/user/login');
            }
        });

        htmx.on("htmx:configRequest", async (e) => {
            console.log('check cookie');
            await this.checkAuth();
            e.detail.headers["Authorization"] = this.getCookieValue('token');
        });

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
                // do nothing
            } else if (evt.detail.xhr.status === 404) {
                this.showToast(evt.detail.pathInfo.requestPath + ' + ' + evt.detail.xhr.responseText, "#e94e1d");
            } else if (evt.detail.xhr.status === 403) {
                console.log('403');
                this.showToast(evt.detail.xhr.responseText.replace(/\\n/g, '\n'), "red");
            } else if (evt.detail.xhr.status === 401 && !window.location.pathname.includes('login')) {
                window.history.pushState('Login', 'Login', '/basic/user/login' + "?next=" + window.location.pathname);
                htmx.ajax('GET', '/basic/user/login', {
                    target: '#htmx_content', headers: {
                        'HX-Replace-Url': 'true'
                    }
                });
            } else if (evt.detail.xhr.status === 418) {
                evt.detail.shouldSwap = true;
                evt.detail.target = htmx.find("#teapot");
            } else {
                this.showToast(evt.detail.xhr.responseText, "#e94e1d");
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
    login() {
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
            if (response.status === 200) {
                response.json().then(data => {
                    this.saveTokensAndRedirect(data.token, data.refresh_token, data.next);
                });
            } else {
                response.json().then(data => {
                    this.showToast(data.message, "red");
                });
            }
        });
    }

    // Новая функция для сохранения токенов и редиректа
    saveTokensAndRedirect(token, refresh_token, next) {
        const parsedToken = this.parseJwt(token);
        const parsedRefreshToken = this.parseJwt(refresh_token);
        const tokenExpires = new Date(parsedToken.exp * 1000);
        const refreshTokenExpires = new Date(parsedRefreshToken.exp * 1000);

        document.cookie = `token=${token}; expires=${tokenExpires.toUTCString()}; path=/;`;
        document.cookie = `refresh_token=${refresh_token}; expires=${refreshTokenExpires.toUTCString()}; path=/;`;

        const redirectUrl = next || '/';
        window.location.replace(redirectUrl);
    }
}
let cache = new CacheHandler();
// Инициализация обработчика аутентификации
const authHandler = new AuthHandler();

