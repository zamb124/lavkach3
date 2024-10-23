var cache = {};
function getCookieValue(name) {
    const nameString = name + "="

    const values = document.cookie.split(";").filter(item => {
        return item.includes(nameString)
    })
    if (values.length) {
        let value = []
        for (let val in values) {
            let is_value = values[val].split('=').filter(item => {
                return item.replace(' ', '') === name
            })
            if (is_value.length) {
                value = values[val]
                break
            }
        }
        if (value.length) {
            return value.substring(nameString.length, value.length).replace('=', '')
        }
    } else {
        return null
    }
}

function removeCookie(sKey, sPath, sDomain) {
    document.cookie = encodeURIComponent(sKey) +
        "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" +
        (sDomain ? "; domain=" + sDomain : "") +
        (sPath ? "; path=" + sPath : "");
}

function parseJwt(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}

// auth is a promise returned by our authentication system

// await the auth token and store it somewhere

var authToken = null
// gate htmx requests on the auth token
htmx.on("htmx:confirm", (e) => {
    let authToken = getCookieValue('token');
    // if there is no auth token
    if (authToken == null && !window.location.pathname.includes('login')) {
        e.preventDefault()

        window.history.pushState('Login', 'Login', '/basic/user/login');
        console.log('redirect login')
        document.location.replace('/basic/user/login')
        //console.log(authToken)
    }
});

async function refreshToken() {
    let user = {
        token: getCookieValue('token').replace('=', ''),
        refresh_token: getCookieValue('refresh_token').replace('=', '')
    };
    console.log('refreshing token')
    let response = await fetch('/basic/user/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
    });
    let result = await response.json();
    const parsed = parseJwt(result.token)
    const expires = await new Date(parsed.exp * 1000)
    document.cookie = "token=" + result.token + "; expires=" + expires + ";path=/;"
    document.cookie = "refresh_token=" + result.token + "; expires=" + expires + ";path=/;"
    return true

}

async function checkAuth() {
    var authToken = getCookieValue('token')
    if (!authToken) {
        authToken = getCookieValue('refresh_token')
        if (authToken) {
            authToken = refreshToken()
            authToken = getCookieValue('token')
        }
    }
    if (!authToken) {
        return false
    }
    var tokenData = parseJwt(authToken)
    var now = Date.now() / 1000
    if (tokenData.exp <= now) {
        await refreshToken()
    }
    return true
}

// add the auth token to the request as a header
htmx.on("htmx:configRequest", (e) => {
    //e.detail.headers["AUTH"] = authToken

    console.log('check cookie')
    const res = checkAuth()
    e.detail.headers["Authorization"] = getCookieValue('token')
})
htmx.on("htmx:afterRequest", (e) => {

    //e.detail.headers["AUTH"] = authToken
    if (authToken == null) {
        //console.log('afterRequest')
        if (e.detail.xhr.status || 200) {
            e.detail.shouldSwap = true;
            e.detail.isError = false;
        }
    }
})
htmx.on('htmx:beforeSwap', function (evt) {

    if (evt.detail.xhr.status === 200) {
        // do nothing
    } else if (evt.detail.xhr.status === 404) {
        // alert the user when a 404 occurs (maybe use a nicer mechanism than alert())
        var myToast = Toastify({
            text: evt.detail.pathInfo.requestPath + ' + ' + evt.detail.xhr.responseText,
            duration: 3000,
            close: true,
            style: {
                background: "#e94e1d",
            },

        })
        myToast.showToast();
    } else if (evt.detail.xhr.status === 403) {
        // Запрещено
        console.log('403')
        var message = evt.detail.xhr.responseText.replace(/\\n/g, '\n')
        var myToast = Toastify({
            text: message,
            duration: 3000,
            style: {
                background: "red",
            },
        })
        myToast.showToast();
    } else if (evt.detail.xhr.status === 401 && !window.location.pathname.includes('login')) {
        // Запрещено

        window.history.pushState('Login', 'Login', '/basic/user/login' + "?next=" + window.location.pathname);
        htmx.ajax('GET', '/basic/user/login', {
            target: '#htmx_content', headers: {
                'HX-Replace-Url': 'true'
            }
        })
    } else if (evt.detail.xhr.status === 418) {
        // if the response code 418 (I'm a teapot) is returned, retarget the
        // content of the response to the element with the id `teapot`
        evt.detail.shouldSwap = true;
        evt.detail.target = htmx.find("#teapot");

    } else {
        var myToast = Toastify({
            text: evt.detail.xhr.responseText,
            duration: 3000,
            close: true,
            style: {
                background: "#e94e1d",
            },

        })
        myToast.showToast();
    }
});
//htmx.logger = function (elt, event, data) {
//    if (console) {
//        console.log(event, elt, data);
//    }
//};
htmx.on('htmx:wsConfigReceive', (e) => {
    console.log('wsConfigReceive')
    console.log(e);
    e.detail.headers["Authorization"] = getCookieValue('token')
})
htmx.on('htmx:wsConfigSend', (e) => {
    console.log('wsConfigSend')
    console.log(e);
    e.detail.headers["Authorization"] = getCookieValue('token')
})