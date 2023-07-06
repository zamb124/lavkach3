<script setup lang="ts">
const navigation = [
  {
    name: 'Sale Orders',
    children: [
      {
        name: 'Sale Orders Analytics',
        icon: 'dashicons:chart-pie',
        to: '/sale/orders/analytics',
        exact: true,
      },
      {
        name: 'Quatation Orders',
        icon: 'mdi:cart-arrow-down',
        to: '/sale/orders/quatation',
        exact: true,
      },
      {
        name: 'Processing Orders',
        icon: 'mdi:cart-arrow-right',
        to: '/sale/orders/processing',
        exact: true,
      },
      {
        name: 'Done Orders',
        icon: 'mdi:cart-check',
        to: '/sale/orders/done',
      },
      {
        name: 'All Orders',
        icon: 'mdi:cart',
        to: '/sale/orders/all',
      },
    ],
  },
  {
    name: 'Clients',
    children: [
      {
        name: 'Clients Analytics',
        icon: 'ph:gauge-duotone',
        to: '/sale/clients',
      },
      {
        name: 'Clients',
        icon: 'carbon:partnership',
        to: '/purchase/vendors/all',
      },
    ],
  },
  {
    divider: true,
  },
  {
    name: 'Settings',
    to: '/sale/settings',
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
