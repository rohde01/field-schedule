<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { updateUserSchema } from '$lib/schemas/user';
    import { createClubSchema } from '$lib/schemas/club';
    import type { PageData } from './$types';

    import NameModal from './NameModal.svelte';
    import ClubModal from './ClubModal.svelte';
    import { Label, Select, Card, Heading, Button, Input, Helper } from 'flowbite-svelte';

    import type { InputField } from '$lib/types/types';

    import { Breadcrumb, BreadcrumbItem, Toast } from 'flowbite-svelte';
    import { CheckCircleSolid, CloseCircleSolid } from 'flowbite-svelte-icons';



    let { data } = $props<{ data: PageData }>();
    
    const nameForm = superForm(data.userForm, {
        validators: zodClient(updateUserSchema),
        resetForm: false,
        taintedMessage: null
    });

    const clubForm = superForm(data.clubForm, {
        validators: zodClient(createClubSchema),
        resetForm: false,
        taintedMessage: null
    });

    let openNameModal = $state(!data.user?.first_name || !data.user?.last_name);
    let openClubModal = $state(data.user?.first_name && data.user?.last_name && !data.hasClub);
  
    const clubInputs: InputField[] = [
      { label: 'Club Name', type: 'text', placeholder: 'My Club Name' }
    ];

    // Destructure the form object and explicitly type the errors
    const { form: userData, enhance: userEnhance, errors: userErrors, message: userMessage } = nameForm;
</script>

<!-- Modals -->
<NameModal bind:open={openNameModal} form={nameForm} data={{}} />
<ClubModal bind:open={openClubModal} form={clubForm} data={{}} />


<main class="p-4">
  <div class="grid grid-cols-1 space-y-2 xl:grid-cols-2 xl:gap-3.5 dark:bg-gray-900">
    <div class="col-span-full xl:mb-0">
      <Breadcrumb class="mb-6">
        <BreadcrumbItem home>Home</BreadcrumbItem>
        <BreadcrumbItem class="hover:text-primary-600 inline-flex items-center text-gray-700 dark:text-gray-300 dark:hover:text-white" href="/crud/users">Users</BreadcrumbItem>
        <BreadcrumbItem>Settings</BreadcrumbItem>
      </Breadcrumb>

      <Heading tag="h1" class="text-xl font-semibold text-gray-900 sm:text-2xl dark:text-white">Settings</Heading>
    </div>

    <div class="space-y-4">
      <Heading tag="h2" class="text-lg font-semibold dark:text-white">Club Details</Heading>
      
      <!-- Club GeneralInfo -->
      <Card size="xl" class="max-w-none shadow-sm -mt-px max-w-none p-4 sm:p-6">
        <div class="mt-px mb-4 lg:mb-0">
          <Heading tag="h3" class="mb-2 -ml-0.25 text-xl font-semibold dark:text-white">
            General Information
          </Heading>
        </div>
        <form class="grid grid-cols-6 gap-6">
          {#each clubInputs as { label, type, placeholder }}
            <Label class="col-span-6 space-y-2 sm:col-span-3">
              <span>{label}</span>
              <Input {type} {placeholder} class="border font-normal outline-none" />
            </Label>
          {/each}
          <Button class="w-fit whitespace-nowrap">Save all</Button>
        </form>
      </Card>
    </div>
    
    <div class="space-y-4">
      <Heading tag="h2" class="text-lg font-semibold dark:text-white">User Details</Heading>
      
      <!-- User GeneralInfo -->
      <Card size="xl" class="max-w-none shadow-sm -mt-px max-w-none p-4 sm:p-6">
        <div class="mt-px mb-4 lg:mb-0">
          <Heading tag="h3" class="mb-2 -ml-0.25 text-xl font-semibold dark:text-white">
            General Information
          </Heading>
        </div>
        <form method="POST" action="?/updateUser" use:userEnhance id="user-form" class="grid grid-cols-6 gap-6">
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>First Name</span>
            <Input name="first_name" id="first_name" type="text" bind:value={$userData.first_name} class="border font-normal outline-none" />
            {#if $userErrors?.first_name}<Helper class="mt-2" color="red">{$userErrors.first_name}</Helper>{/if}
          </Label>
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Last Name</span>
            <Input name="last_name" id="last_name" type="text" bind:value={$userData.last_name} class="border font-normal outline-none" />
            {#if $userErrors?.last_name}<Helper class="mt-2" color="red">{$userErrors.last_name}</Helper>{/if}
          </Label>
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Email</span>
            <Input name="email" id="email" type="email" bind:value={$userData.email} class="border font-normal outline-none" />
            {#if $userErrors?.email}<Helper class="mt-2" color="red">{$userErrors.email}</Helper>{/if}
          </Label>
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Role</span>
            <Input name="role" id="role" type="text" bind:value={$userData.role} class="border font-normal outline-none" />
            {#if $userErrors?.role}<Helper class="mt-2" color="red">{$userErrors.role}</Helper>{/if}
          </Label>
          {#if $userMessage}
            <Toast color={$userMessage.toLowerCase().includes('success') ? 'green' : 'red'} class="fixed top-20 right-4 z-50">
                <svelte:fragment slot="icon">
                    {#if $userMessage.toLowerCase().includes('success')}
                        <CheckCircleSolid class="w-5 h-5" />
                        <span class="sr-only">Check icon</span>
                    {:else}
                        <CloseCircleSolid class="w-5 h-5" />
                        <span class="sr-only">Error icon</span>
                    {/if}
                </svelte:fragment>
                {$userMessage}
            </Toast>
          {/if}
          <Button type="submit"  form="user-form" class="w-fit whitespace-nowrap">Save all</Button>
        </form>
      </Card>
      
      <!-- Password Information -->
      <Card size="xl" class="max-w-none shadow-sm max-w-none p-4 sm:p-6">
        <div class="mt-px mb-4 lg:mb-0">
          <Heading tag="h3" class="mb-2 -ml-0.25 text-xl font-semibold dark:text-white">
            Password Information
          </Heading>
        </div>
        <div class="grid grid-cols-6 gap-6">
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Current password</span>
            <Input placeholder="••••••••" class="border font-normal outline-none"></Input>
          </Label>
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>New password</span>
            <Input placeholder="••••••••" class="border font-normal outline-none"></Input>
          </Label>
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Confirm password</span>
            <Input placeholder="••••••••" class="border font-normal outline-none"></Input>
          </Label>
          <Button class="sm:col-full col-span-6 w-fit">Save all</Button>
        </div>
      </Card>
      
      <!-- Language Card -->
      <Card size="xl" class="max-w-none shadow-sm -mt-px max-w-none p-4 sm:p-6">
        <div class="mt-px mb-4 lg:mb-0">
          <Heading tag="h3" class="mb-2 -ml-0.25 text-xl font-semibold dark:text-white">
            Language
          </Heading>
        </div>
        <form class="grid grid-cols-6 gap-6">
          <Label class="col-span-6 sm:col-span-3 space-y-2">
            <span>Language</span>
            <Select class="border font-normal outline-none">
              <option value="en">English</option>
              <option value="da">Danish</option>
            </Select>
          </Label>
        </form>
      </Card>
    </div>
  </div>
</main>