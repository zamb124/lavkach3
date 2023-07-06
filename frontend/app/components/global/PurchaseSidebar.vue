<script setup lang="ts">
const navigation = [
  {
    name: 'Orders',
    children: [
      {
        name: 'Orders Analytics',
        icon: 'dashicons:chart-pie',
        to: '/purchase/orders/analytics',
        exact: true,
      },
      {
        name: 'My Orders',
        icon: 'carbon:document-attachment',
        to: '/purchase/orders/my',
        exact: true,
      },
      {
        name: 'Processing Orders',
        icon: 'carbon:document-protected',
        to: '/purchase/orders/processing',
        exact: true,
      },
      {
        name: 'RFQ',
        icon: 'carbon:request-quote',
        to: '/purchase/orders/rfq',
      },
      {
        name: 'All Orders',
        icon: 'carbon:document-multiple-02',
        to: '/purchase/orders/all',
      },
    ],
  },
  {
    name: 'Vendors',
    children: [
      {
        name: 'Vendors Analytics',
        icon: 'ph:gauge-duotone',
        to: '/purchase/vendors/analytics',
      },
      {
        name: 'Vendors',
        icon: 'carbon:partnership',
        to: '/purchase/vendors/all',
      },
      {
        name: 'Vendors Contracts',
        icon: 'carbon:document',
        to: '/purchase/vendors/contracts',
      },
    ],
  },
  {
    divider: true,
  },
  {
    name: 'Settings',
    to: '/purchase/settings',
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
