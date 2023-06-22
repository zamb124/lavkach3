/**
 * This file is used to configure the app
 *
 * If you have the "Cannot find name 'defineAppConfig'.ts(2304)" error
 * update the root tsconfig.json file to include the following:
 *
 *  "extends": "./app/.nuxt/tsconfig.json"
 *
 */

export default defineAppConfig({
  sidebar: {
    circularMenu: {
      enabled: false,
      tools: [],
    },
    toolbar: {
      enabled: true,
      showTitle: true,
      showNavBurger: false,
      tools: [],
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
