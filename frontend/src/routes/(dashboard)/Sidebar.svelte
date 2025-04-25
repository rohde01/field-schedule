<script lang="ts">
  import { afterNavigate } from '$app/navigation';
  import { page } from '$app/state';

  import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper, Button, Dropdown, DropdownItem, DropdownDivider } from 'flowbite-svelte';
  import { ChartPieOutline, TableColumnSolid, RectangleListSolid, GithubSolid, ClipboardListSolid, ChevronUpOutline } from 'flowbite-svelte-icons';
  import { facilities, selectedFacility, setSelectedFacility, showCreateFacility, toggleCreateFacility } from '$lib/stores/facilities';
  import type { Facility } from '$lib/schemas/facility';

  let { drawerHidden = $bindable() } = $props();
  const closeDrawer = () => {
    drawerHidden = true;
  };

  let iconClass = 'flex-shrink-0 w-6 h-6 text-gray-500 transition duration-75 group-hover:text-gray-900 dark:text-gray-300 dark:group-hover:text-white';
  let itemClass = 'flex items-center p-2 text-base text-gray-900 transition duration-75 rounded-lg hover:bg-gray-100 group dark:text-gray-200 dark:hover:bg-gray-700 w-full';
  let itemLinkClass = 'flex items-center p-0 py-2 text-base text-gray-900 transition duration-75 rounded-lg hover:bg-gray-100 group dark:text-gray-200 dark:hover:bg-gray-700 w-full';
  let activeClass = 'text-green-500 dark:text-green-300 hover:text-green-700 dark:hover:text-green-500';
  let groupClass = 'pt-2 space-y-2 mb-3';

  let mainSidebarUrl = $derived(page.url.pathname);
  let activeMainSidebar = '';

  afterNavigate((nav) => {
    document.getElementById('svelte')?.scrollTo({ top: 0 });
    closeDrawer();
    activeMainSidebar = nav.to?.url.pathname ?? '';
  });

  let posts = [
    { name: 'Dashboard', Icon: ChartPieOutline, href: '/dashboard' },
    { name: 'Schedules', Icon: ClipboardListSolid, href: '/schedules' },
    { name: 'Fields', Icon: TableColumnSolid, href: '/fields' },
    { name: 'Teams', Icon: RectangleListSolid, href: '/teams' }
  ];

  let links = [
    { label: 'GitHub Repository', href: 'https://github.com/rohde01/field-schedule.git', Icon: GithubSolid }
  ];

  function selectFacility(facility: Facility) {
    setSelectedFacility(facility);
    document.getElementById('bottom-dropdown')?.click();
  }

  function handleAddFacility() {
    toggleCreateFacility(true);
    document.getElementById('bottom-dropdown')?.click();
  }
</script>

<Sidebar
  activeUrl={mainSidebarUrl}
  activeClass="bg-gray-100 dark:bg-gray-700"
  class="{drawerHidden ? 'hidden' : ''} fixed inset-0 z-30 h-full w-64 flex-none border-e border-gray-200 lg:block lg:h-auto lg:overflow-y-visible lg:pt-16 dark:border-gray-600"
>
  <h4 class="sr-only">Main menu</h4>
  <SidebarWrapper divClass="overflow-y-auto px-3 pt-20 lg:pt-5 h-full bg-white scrolling-touch max-w-2xs lg:h-[calc(100vh-4rem)] lg:block dark:bg-gray-800 lg:me-0 lg:sticky top-2">
    <div>
      <SidebarGroup class={groupClass}>
        {#each posts as { name, Icon, href }}
          <SidebarItem label={name} href={href} spanClass="ml-3" class={itemLinkClass}>
            <Icon slot="icon" class={iconClass}/>
          </SidebarItem>
        {/each}
      </SidebarGroup>
      <SidebarGroup class={groupClass}>
        {#each links as { label, href, Icon }}
          <SidebarItem label={label} href={href} spanClass="ml-3" class={itemLinkClass} target="_blank">
            <Icon slot="icon" class={iconClass}/>
          </SidebarItem>
        {/each}
      </SidebarGroup>
    </div>
    
    <!-- Dropdown button at the bottom -->
    <div class="absolute bottom-0 left-0 right-0 px-3 pb-4">
      <Button id="bottom-dropdown" class="w-full">{$selectedFacility ? $selectedFacility.name : 'Facilities'}<ChevronUpOutline class="w-6 h-6 ms-2 text-white dark:text-white" /></Button>
      
      <Dropdown placement="top" triggeredBy="#bottom-dropdown">
        {#each $facilities as facility}
          <DropdownItem on:click={() => selectFacility(facility)} class={facility === $selectedFacility ? activeClass : ''}>{facility.name}</DropdownItem>
        {/each}
        <DropdownDivider />
        <DropdownItem on:click={handleAddFacility} class="text-mint-600 hover:text-mint-700 hover:bg-mint-50">
          Add Facility
        </DropdownItem>
      </Dropdown>
    </div>
  </SidebarWrapper>
</Sidebar>

<div hidden={drawerHidden} class="fixed inset-0 z-20 bg-gray-900/50 dark:bg-gray-900/60" onclick={closeDrawer} onkeydown={closeDrawer} role="presentation"></div>