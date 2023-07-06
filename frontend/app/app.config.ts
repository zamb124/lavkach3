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
          {
            title: 'Customize',
            icon: { name: 'ph:drop-half-bottom-duotone', class: 'w-5 h-5' },
            click: () => {
              const isOpen = useState('switcher-open', () => false)
              isOpen.value = true
            },
            position: 'end',
          },
          {
            title: 'Search',
            icon: { name: 'ph:magnifying-glass-duotone', class: 'w-5 h-5' },
            click: () => {
              const isOpen = useState('search-open', () => false)
              isOpen.value = true
            },
            position: 'end',
          },
          {
            title: 'Settings',
            icon: { name: 'ph:gear-six-duotone', class: 'w-5 h-5' },
            to: '/layouts/profile-settings',
            position: 'end',
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
