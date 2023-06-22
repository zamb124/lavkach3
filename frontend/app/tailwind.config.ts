import { withShurikenUI } from '@shuriken-ui/tailwind'
import colors from 'tailwindcss/colors'

/**
 * This is the Tailwind config file for the demo.
 * It extends the default config from @shuriken-ui/tailwind
 *
 * You can add/override your own customizations here.
 */

export default withShurikenUI({
  content: [],
  theme: {
    extend: {
      colors: {
        primary: colors.red,
        muted: colors.stone,
      },
    },
  },
})
