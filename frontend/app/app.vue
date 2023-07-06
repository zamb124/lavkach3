<template>
  <div>
    <NuxtLayout>
      <NuxtLoadingIndicator color="var(--color-primary-500)" />
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
globalThis.$fetch = useCreateFetch()
</script>
