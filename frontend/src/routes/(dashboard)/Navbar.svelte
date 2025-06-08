<script lang="ts">
  import { DarkMode, NavBrand, Navbar, DropdownDivider, DropdownItem, Button, Spinner } from 'flowbite-svelte';
  import UserMenu from './UserMenu.svelte';
  import { ArrowUpRightFromSquareSolid } from 'flowbite-svelte-icons';
  import { page } from '$app/stores';
  import { clubs } from '$lib/stores/clubs';
  
  let { session = null, transparent = false }: { session?: App.PageData['session'], transparent?: boolean } = $props();
  
  let signingOut = $state(false);
  
  // Get current club from store based on URL
  const currentClub = $derived($clubs.find(club => {
    if (!club.club_url) return false;
    const currentHost = window?.location?.hostname;
    
    // Check if we're on a subdomain that matches the club
    if (currentHost.includes('.')) {
      const subdomain = currentHost.split('.')[0];
      return subdomain === club.club_url;
    }
    
    return false;
  }));
  
  // Use club logo from store only for authenticated users, otherwise use default favicon
  const logoUrl = $derived.by(() => {
    // If user is authenticated and has a club, use their club's logo
    if (session && $page.data.user?.club_id) {
      const userClub = $clubs.find(club => club.club_id === $page.data.user?.club_id);
      if (userClub?.logo_url) return userClub.logo_url;
    }
    
    // Fallback to current club (subdomain match) or page data club
    return currentClub?.logo_url || 
           $page.data.club?.logo_url || 
           '/favicon.png';
  });
  
  const menuItems = [
    { text: 'My club', href: '/schedules' },
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

<Navbar fluid class="w-full px-6 py-3.75 text-black justify-between {transparent ? 'bg-transparent' : ''}" color={transparent ? "none" : "default"}>
  <button aria-label="Home" onclick={handleLogoClick} class="flex items-center">
    <img src={logoUrl} class="me-3 h-8 sm:h-10" alt="Club logo" />
  </button>

  <div class="ms-auto flex items-center text-gray-500 sm:order-2 dark:text-gray-300">
    <DarkMode />
    {#if session}
      <UserMenu name="Welcome!" avatar="" email="" {menuItems}>
        <DropdownDivider />
        <DropdownItem>
          <form action="/schedules?/logout" method="post" onsubmit={() => signingOut = true}>
            <Button size="xs" type="submit" disabled={signingOut}>
              {#if signingOut}
                <Spinner class="me-2" size="3" />Signing out...
              {:else}
                <ArrowUpRightFromSquareSolid class="w-4 h-4 me-2" />
                Sign out
              {/if}
            </Button>
          </form>
        </DropdownItem>
      </UserMenu>
    {/if}
  </div>
</Navbar>