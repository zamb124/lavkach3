export default defineAppConfig({
  tairo: {
    sidebar: {
      toolbar: {
        showNavBurger: true,
        tools: [
          {
            component: 'ThemeToggle',
          },
          {
            component: 'SelectLanguage',
          },
          {
            component: 'ToolbarAccount',
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
        items: [
          {
            title: 'Purchase',
            icon: { name: 'gg:briefcase', class: 'w-6 h-10' },
            subsidebar: { component: 'PurchaseSidebar' },
            activePath: '/purchase',
          },
          {
            title: 'Sales',
            icon: {
              name: 'streamline:shopping-cart-2-shopping-cart-checkout',
              class: 'w-6 h-10',
            },
            subsidebar: { component: 'SalesSidebar' },
            activePath: '/sales',
          },
          {
            title: 'Accounting',
            icon: { name: 'carbon:money', class: 'w-6 h-10' },
            subsidebar: { component: 'AccountingSidebar' },
            activePath: '/accounting',
          },
        ],
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
