export default defineNuxtRouteMiddleware((to, from) => {
  // Мидлваря запускается дважды: на сервере и на клиенте
  // localStorage доступен только на клиенте
  // пропускаем серверную мидлварю
  if (process.server) return

  const token = useUserToken()

  if (!token.value && !to.path.includes('auth')) {
    return navigateTo('/auth/login')
  }
})
