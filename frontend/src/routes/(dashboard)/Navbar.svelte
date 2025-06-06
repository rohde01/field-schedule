<script lang="ts">
  import { DarkMode, NavBrand, Navbar, DropdownDivider, DropdownItem, Button } from 'flowbite-svelte';
  import UserMenu from './UserMenu.svelte';
  import { ArrowUpRightFromSquareSolid } from 'flowbite-svelte-icons';
  
  export let session: App.PageData['session'] = null;
  
  const menuItems = [
    { text: 'Dashboard', href: '/' },
    { text: 'Settings', href: '/settings' }
  ];

  function handleLogoClick() {
    const url = new URL(window.location.href);
    let mainDomain;
    
    if (url.hostname.includes('localhost')) {
      mainDomain = 'localhost';
    } else {
      const parts = url.hostname.split('.');
      if (parts.length > 2) {
        mainDomain = parts.slice(-2).join('.');
      } else {
        mainDomain = url.hostname;
      }
    }
    
    const newUrl = `${url.protocol}//${mainDomain}${url.port ? ':' + url.port : ''}/`;
    window.location.href = newUrl;
  }
</script>

<Navbar fluid class="w-full px-6 py-3.75 text-black justify-between" color="default">
  <button on:click={handleLogoClick} class="flex items-center">
    <img src="/favicon.png" 
         class="me-3 h-8 sm:h-10" 
         alt="My Logo" />
  </button>

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