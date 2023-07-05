<script setup>
const { open } = usePanels()
</script>

<template>
  <button
    type="button"
    class="border-muted-200 hover:ring-muted-200 dark:hover:ring-muted-700 dark:border-muted-700 dark:bg-muted-800 dark:ring-offset-muted-900 flex h-9 w-9 items-center justify-center rounded-full border bg-white ring-1 ring-transparent transition-all duration-300 hover:ring-offset-4"
    @click="open('language')"
  >
    <Icon name="circle-flags:ae" class="h-7 w-7" />
  </button>
</template>
