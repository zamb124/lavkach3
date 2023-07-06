export const useFetchCreate = () => $fetch.create({
  baseURL: useRuntimeConfig().public.apiUrl,
})
