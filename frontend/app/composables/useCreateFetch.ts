export const useCreateFetch = () =>
  $fetch.create({
    baseURL: useRuntimeConfig().public.apiUrl,
  })
