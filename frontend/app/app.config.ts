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
            component: 'SelecLanguage',
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
    panels: [
      {
        name: 'language',
        position: 'right',
        component: 'PanelLanguage',
      },
    ],
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
})
