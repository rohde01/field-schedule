<script lang="ts">
  import { DarkMode, NavBrand, Navbar, DropdownDivider, DropdownItem, Button } from 'flowbite-svelte';
  import UserMenu from './UserMenu.svelte';
  import { ArrowUpRightFromSquareSolid } from 'flowbite-svelte-icons';
  
  export let session: App.PageData['session'] = null;
  
  const menuItems = [
    { text: 'Dashboard', href: '/' },
    { text: 'Settings', href: '/settings' }
  ];
</script>

<Navbar fluid class="w-full px-6 py-3.75 text-black justify-between" color="default">
  <NavBrand href="/">
    <img src="/favicon.png" 
         class="me-3 h-8 sm:h-10" 
         alt="My Logo" />
  </NavBrand>

  <div class="ms-auto flex items-center text-gray-500 sm:order-2 dark:text-gray-300">
    <DarkMode />
    {#if session}
      <UserMenu name="Carl-Emil" avatar="" email="dev@rohdee.dk" {menuItems}>
        <DropdownDivider />
        <DropdownItem>
          <form action="/auth?/logout" method="post">
            <Button size="xs" type="submit">
              <ArrowUpRightFromSquareSolid class="w-4 h-4 me-2" />
              Sign out
            </Button>
          </form>
        </DropdownItem>
      </UserMenu>
    {/if}
  </div>
</Navbar>