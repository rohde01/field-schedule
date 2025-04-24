<script lang="ts">
    import { Button, CloseButton, Heading, Input, Label, Select, Textarea, Toggle } from 'flowbite-svelte';
    import { CloseOutline } from 'flowbite-svelte-icons';
    import type { FacilityDrawerProps } from '../types/types';
    import type { FacilityCreate } from '../schemas/facility';
  
    let { hidden = $bindable(true), title = 'Add new facility' }: FacilityDrawerProps = $props();
    
    let facility: FacilityCreate = {
        club_id: 0,
        name: '',
        description: '',
        is_primary: false
    };
</script>
  
<Heading tag="h5" class="mb-6 text-sm font-semibold uppercase">{title}</Heading>
<CloseButton onclick={() => (hidden = true)} class="absolute top-2.5 right-2.5 text-gray-400 hover:text-black dark:text-white" />
  
<form action="#">
  <div class="space-y-4">
    <Label class="space-y-2">
      <span>Name</span>
      <Input name="name" bind:value={facility.name} class="border font-normal outline-none" placeholder="Type facility name" required />
    </Label>
  
    <Label class="space-y-2">
      <span>Description</span>
      <Textarea name="description" bind:value={facility.description} rows={4} placeholder="Enter facility description here" class="border-gray-300 font-normal outline-none"></Textarea>
    </Label>

    <Label class="flex items-center space-x-2">
      <span>Primary Facility</span>
      <Toggle bind:checked={facility.is_primary} />
    </Label>
  
    <div class="bottom-0 left-0 flex w-full justify-center space-x-4 pb-4 md:absolute md:px-4">
      <Button type="submit" class="w-full">Add facility</Button>
      <Button color="alternative" class="w-full" onclick={() => (hidden = true)}>
        <CloseOutline />
        Cancel
      </Button>
    </div>
  </div>
</form>
