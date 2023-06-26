<template>
  <div>
    <NuxtLayout>
      <NuxtLoadingIndicator color="var(--color-primary-500)" />
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

globalThis.$fetch = $fetch.create({
  baseURL: config.public.apiUrl,
})
</script>
