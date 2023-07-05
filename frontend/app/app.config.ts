export default defineAppConfig({
  tairo: {
    sidebar: {
      circularMenu: {
        enabled: false,
        tools: [],
      },
      toolbar: {
        showNavBurger: true,
        tools: [
          {
            component: 'ThemeToggle',
          },
          {
            component: 'PanelLanguage',
          },
        ],
      },
      navigation: {
        enabled: true,
        startOpen: true,
        logo: {
          component: 'TairoLogo',
          resolve: true,
          props: {
            class: 'text-primary-600 h-10',
          },
        },
        items: [],
      },
    },
  },
  title: 'Tairo Quick Starter',
  error: {
    logo: {
      component: 'TairoLogo',
      resolve: true,
      props: {
        class: 'text-primary-500 mx-auto h-40 p-6',
      },
    },
  },
  panels: [],
})
