<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { updateUserSchema } from '$lib/schemas/user';
    import { createClubSchema, updateClubSchema } from '$lib/schemas/club';
    import type { PageData } from './$types';

    import NameModal from './NameModal.svelte';
    import ClubModal from './ClubModal.svelte';
    import { Label, Select, Card, Heading, Button, Input, Helper, Spinner, Fileupload } from 'flowbite-svelte';
    import { Breadcrumb, BreadcrumbItem } from 'flowbite-svelte';
    import ToastMessage from '$lib/components/Toast.svelte';

    let { data } = $props<{ data: PageData }>();
    
    const nameForm = superForm(data.userForm, {
        validators: zodClient(updateUserSchema),
        resetForm: false,
        taintedMessage: null,
        id: 'user-update-form'
    });

    const clubForm = superForm(data.clubForm, {
        validators: zodClient(createClubSchema),
        resetForm: false,
        taintedMessage: null,
        id: 'club-create-form'
    });

    const updateClubForm = superForm(data.updateClubForm, {
        validators: zodClient(updateClubSchema),
        resetForm: false,
        taintedMessage: null,
        id: 'club-update-form'
    });

    let openNameModal = $state(!data.user?.first_name || !data.user?.last_name);
    let openClubModal = $state(data.user?.first_name && data.user?.last_name && !data.hasClub);
  
    // Destructure the form objects and explicitly type the errors
    const { form: userData, enhance: userEnhance, errors: userErrors, message: userMessage, submitting: userSubmitting } = nameForm;
    const { form: clubUpdateData, enhance: clubUpdateEnhance, errors: clubUpdateErrors, message: clubUpdateMessage, submitting: clubSubmitting } = updateClubForm;
    
    let userSaving = $state(false);
    let clubSaving = $state(false);
    
    $effect(() => {
        userSaving = $userSubmitting;
    });
    
    $effect(() => {
        clubSaving = $clubSubmitting;
    });
</script>

<!-- Modals -->
<NameModal bind:open={openNameModal} form={nameForm} data={{}} />
<ClubModal bind:open={openClubModal} form={clubForm} data={{}} />

<!-- Toast messages -->
<ToastMessage message={$userMessage} />
<ToastMessage message={$clubUpdateMessage} />

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
        <form method="POST" action="?/updateClub" use:clubUpdateEnhance id="club-form" class="grid grid-cols-6 gap-6">
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Club Name</span>
            <Input name="name" id="name" type="text" bind:value={$clubUpdateData.name} class="border font-normal outline-none" />
            {#if $clubUpdateErrors?.name}<Helper class="mt-2" color="red">{$clubUpdateErrors.name}</Helper>{/if}
          </Label>
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Club URL</span>
            <Input name="club_url" id="club_url" type="text" bind:value={$clubUpdateData.club_url} class="border font-normal outline-none" />
            {#if $clubUpdateErrors?.club_url}<Helper class="mt-2" color="red">{$clubUpdateErrors.club_url}</Helper>{/if}
          </Label>
          <Button type="submit" form="club-form" class="w-fit whitespace-nowrap" disabled={clubSaving}>
            {#if clubSaving}
              <Spinner class="me-3" size="4" color="white" />Saving...
            {:else}
              Save all
            {/if}
          </Button>
        </form>
      </Card>
      <Card size="xl" class="max-w-none shadow-sm -mt-px max-w-none p-4 sm:p-6">
        <div class="mt-px mb-4 lg:mb-0">
          <Heading tag="h3" class="mb-2 -ml-0.25 text-xl font-semibold dark:text-white">
            Club Logo
          </Heading>
        </div>
        {#if data.clubData?.logo_url}
          <img src={data.clubData.logo_url} alt="Club Logo" class="mb-4 w-40 h-30 object-cover rounded" />
        {/if}
        <form method="POST" action="?/uploadLogo" enctype="multipart/form-data" class="grid grid-cols-6 gap-6 items-end">
          <Label for="logo" class="col-span-6 space-y-2 sm:col-span-3">
            <span>Upload Logo</span>
            <Fileupload id="logo" name="logo" class="mb-2" />
            <Helper>SVG, PNG, JPG or GIF (MAX. 800x400px).</Helper>
          </Label>
          <Button type="submit" class="col-span-6 sm:col-span-3 w-fit">
            Upload
          </Button>
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
          <Button type="submit" form="user-form" class="w-fit whitespace-nowrap" disabled={userSaving}>
            {#if userSaving}
              <Spinner class="me-3" size="4" color="white" />Saving...
            {:else}
              Save all
            {/if}
          </Button>
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