<script lang="ts">
  import { DarkMode, NavBrand, Navbar, DropdownDivider, DropdownItem } from 'flowbite-svelte';
  import UserMenu from './UserMenu.svelte';
  const menuItems = ['Dashboard', 'Settings'];
</script>

<Navbar class="text-black" color="default">
  <NavBrand href="/">
    <img src="/favicon.png" 
         class="me-2.5 h-6 sm:h-8" 
         alt="My Logo" />
  </NavBrand>
  <div class="ms-auto flex items-center text-gray-500 sm:order-2 dark:text-gray-300">
    <DarkMode />
    <UserMenu name="Carl-Emil" avatar="" email="dev@rohdee.dk" {menuItems}>
      <DropdownDivider />
      <DropdownItem>Sign out</DropdownItem>
    </UserMenu>
  </div>
</Navbar>