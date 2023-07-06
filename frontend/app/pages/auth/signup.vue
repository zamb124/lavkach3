<script setup lang="ts">
definePageMeta({
  layout: 'empty',
})
</script>

<template>
  <div
    class="bg-muted-100 dark:bg-muted-900 relative flex min-h-screen w-full items-center justify-center overflow-hidden px-4"
  >
    <div class="relative mx-auto w-full max-w-2xl">
      <!--Form-->
      <div class="me-auto ms-auto mt-4 w-full">
        <form
          method="POST"
          action=""
          class="me-auto ms-auto mt-4 w-full max-w-md"
          novalidate
        >
          <div class="text-center">
            <BaseHeading as="h2" size="3xl" weight="medium">
              Welcome to Lavkach
            </BaseHeading>
            <BaseParagraph size="sm" class="text-muted-400 mb-6">
              Let's start by creating you account
            </BaseParagraph>
          </div>
          <div class="px-8 py-4">
            <div class="mb-4 space-y-4">
              <BaseInput
                type="email"
                label="Email address"
                placeholder="ex: maya@cssninja.io"
                autocomplete="email"
                :classes="{
                  input: 'h-12',
                }"
              />

              <BaseInput
                type="password"
                label="Password"
                placeholder="••••••••••"
                autocomplete="new-password"
                :classes="{
                  input: 'h-12',
                }"
              />

              <BaseInput
                type="password"
                label="Confirm Password"
                placeholder="••••••••••"
                :classes="{
                  input: 'h-12',
                }"
              />
            </div>
            <div class="mb-6">
              <div class="mt-6 flex items-center justify-between">
                <BaseCheckbox shape="rounded" color="primary">
                  <span>
                    <span>I accept the</span>
                    <a
                      href="#"
                      class="text-primary-500 hover:underline focus:underline"
                    >
                      Terms of Service
                    </a>
                  </span>
                </BaseCheckbox>
              </div>
            </div>
            <div class="mb-6">
              <BaseButton type="submit" color="primary" class="!h-12 w-full">
                Sign Up
              </BaseButton>
            </div>

            <!--No account link-->
            <p
              class="text-muted-400 mt-4 flex justify-between font-sans text-sm leading-5"
            >
              <span>Already have an account?</span>
              <NuxtLink
                to="/auth/login"
                class="text-primary-600 hover:text-primary-500 font-medium underline-offset-4 transition duration-150 ease-in-out hover:underline"
              >
                Sign in
              </NuxtLink>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
