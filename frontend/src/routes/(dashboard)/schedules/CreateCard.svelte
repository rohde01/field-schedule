<script lang="ts">
    import { Heading } from 'flowbite-svelte';
    import { Card } from 'flowbite-svelte';
    import type { PlaygroundProps } from '$lib/types/types';
  
    let { breadcrumb, title = 'Create something awesome here' }: PlaygroundProps = $props();
  </script>
  
  <main>
    <div class="grid grid-cols-1 pt-2 xl:grid-cols-3 xl:gap-4 xl:px-0 dark:bg-gray-900">
      <div class="col-span-full mb-4 xl:mb-2">
        {#if breadcrumb}
          {@render breadcrumb()}
        {/if}
        <Heading tag="h1" class="text-xl font-semibold sm:text-2xl">{title}</Heading>
      </div>
      <div class="col-span-full xl:col-auto">
        <Card size="xl" class="mb-4 h-80 w-full space-y-6 p-4 2xl:col-span-2">
          <div class="rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card header</h3></div>
          <div class="h-full rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card body</h3></div>
          <div class="rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card footer</h3></div>
        </Card>
      </div>
      <div class="col-span-2">
        <Card class="mb-4 h-80 max-w-none space-y-6 p-4">
          <div class="rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card header</h3></div>
          <div class="h-full rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card body</h3></div>
          <div class="rounded border border-dashed border-gray-200 px-4 py-2 text-gray-400 dark:border-gray-600"><h3>Card footer</h3></div>
        </Card>
      </div>
    </div>
  </main>
