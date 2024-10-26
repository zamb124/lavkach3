var userSettings = {
    Layout: "vertical", // vertical | horizontal
    SidebarType: "mini-sidebar", // full | mini-sidebar
    BoxedLayout: true, // true | false
    Direction: "ltr", // ltr | rtl
    Theme: "light", // light | dark
    ColorTheme: "Cyan_Theme", // Blue_Theme | Aqua_Theme | Purple_Theme | Green_Theme | Cyan_Theme | Orange_Theme
    cardBorder: true, // true | false
    locale: "en"
};

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

function initUserSettings() {
    var Layout = getCookieValue("Layout");
    if (Layout) {
        userSettings.Layout = Layout;
    } else {
        document.cookie = "Layout="+userSettings.Layout+";path=/;"
    }

    var SidebarType = getCookieValue("SidebarType");
    if (SidebarType) {
        userSettings.SidebarType = SidebarType;
    } else {
        document.cookie = "SidebarType="+userSettings.SidebarType+";path=/;"
    }

    var BoxedLayout = getCookieValue("BoxedLayout");
    if (BoxedLayout) {
        userSettings.BoxedLayout = BoxedLayout;
    } else {
      document.cookie = "BoxedLayout="+userSettings.BoxedLayout+";path=/;"
    }

    var Direction = getCookieValue("Direction");
    if (Direction) {
        userSettings.Direction = Direction;
    } else {
        document.cookie = "Direction="+userSettings.Direction+";path=/;"
    }

    var Theme = getCookieValue("Theme");
    if (Theme) {
        userSettings.Theme = Theme;
    } else {
        document.cookie = "Theme="+userSettings.Theme+";path=/;"
    }

    var ColorTheme = getCookieValue("ColorTheme");
    if (ColorTheme) {
        userSettings.ColorTheme = ColorTheme;
    } else {
        document.cookie = "ColorTheme="+userSettings.ColorTheme+";path=/;"
    }

    var cardBorder = getCookieValue("cardBorder");
    if (cardBorder) {
        userSettings.cardBorder = cardBorder;
    } else {
        document.cookie = "cardBorder="+userSettings.cardBorder+";path=/;"
    }
    var locale = getCookieValue("locale");
    if (locale) {
        userSettings.locale = locale;
    } else {
        document.cookie = "locale="+userSettings.locale+";path=/;"
    }

}
initUserSettings()
