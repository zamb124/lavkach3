<script setup lang="ts">
const navigation = [
  {
    name: 'Accounting',
    children: [
      {
        name: 'Invoices Analytics',
        icon: 'dashicons:chart-pie',
        to: '/accounting/documents/analytics',
        exact: true,
      },
      {
        name: 'My documents',
        icon: 'carbon:document-attachment',
        to: '/accounting/documents/my',
        exact: true,
      },
      {
        name: 'Bills',
        icon: 'heroicons-solid:document-add',
        to: '/accounting/documents/bills',
        exact: true,
      },
      {
        name: 'Notes',
        icon: 'heroicons-solid:document-remove',
        to: '/accounting/documents/notes',
      },
      {
        name: 'All Documents',
        icon: 'carbon:document-multiple-02',
        to: '/accounting/documents/all',
      },
    ],
  },
  {
    name: 'Payments',
    children: [
      {
        name: 'Payments',
        icon: 'carbon:currency-dollar',
        to: '/accounting/payments/all',
      },
    ],
  },
  {
    name: 'Taxes',
    children: [
      {
        name: 'Accounting Analytics',
        icon: 'fa-solid:percentage',
        to: '/accounting/taxes',
      },
    ],
  },
  {
    divider: true,
  },
  {
    name: 'Settings',
    to: '/accounting/settings',
  },
  {
    divider: true,
  },
]
</script>

<template>
  <TairoSubsidebar>
    <template #header>
      <TairoSubsidebarHeader />
    </template>

    <TairoSubsidebarMenu :navigation="navigation" />
  </TairoSubsidebar>
</template>
