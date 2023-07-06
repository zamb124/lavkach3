export const useCreateFetch = () =>
  $fetch.create({
    baseURL: useRuntimeConfig().public.apiUrl,
    onRequest({ options }) {
      options.headers = {
        Authorization: useUserToken().value,
      }
    },
  })
