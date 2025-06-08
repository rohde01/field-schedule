<script lang="ts">
  import { filteredFields, deleteField, addField } from '$lib/stores/fields.js';
  import { superForm } from 'sveltekit-superforms/client';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import { facilityCreateSchema } from '$lib/schemas/facility';
  import { showCreateFacility, toggleCreateFacility, selectedFacility } from '$lib/stores/facilities';
  import FacilityDrawer from '$lib/components/FacilityDrawer.svelte';
  import { Drawer } from 'flowbite-svelte';
  import DeleteModal from '$lib/components/DeleteModal.svelte';
  import type { Field } from '$lib/schemas/field';
  import { fieldCreateSchema, updateFieldSchema } from '$lib/schemas/field';
  import FieldModal from './FieldModal.svelte';
  import ToastMessage from '$lib/components/Toast.svelte';

  import { Breadcrumb, BreadcrumbItem, Button, Checkbox, Heading, Indicator } from 'flowbite-svelte';
  import { Input, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, Badge } from 'flowbite-svelte';
  import { TableHeadCell, Toolbar, ToolbarButton } from 'flowbite-svelte';
  import { CogSolid, DotsVerticalOutline, DownloadSolid } from 'flowbite-svelte-icons';
  import { EditOutline, ExclamationCircleSolid, PlusOutline, TrashBinSolid } from 'flowbite-svelte-icons';
  import { derived } from 'svelte/store';

  let { data } = $props();
  
  const deleteForm = superForm(data.deleteForm, {
      resetForm: true,
      onResult: ({ result }) => {
          if (result.type === 'success') {
              // Close the modal after successful deletion
              openDelete = false;
              // Remove the deleted field from the store
              if (result.data?.action === 'deleted field' && fieldToDelete) {
                  deleteField(fieldToDelete.field_id);
              }
          }
      }
  });

  const facilityForm = superForm(data.facilityForm, {
      validators: zodClient(facilityCreateSchema),
      resetForm: true,
      onResult: ({ result }) => {
          if (result.type === 'success') {
              hiddenDrawer = true;
          }
      }
  });

  const createForm = superForm(data.createFieldForm, {
      dataType: 'json',
      validators: zodClient(fieldCreateSchema),
      resetForm: true,
      onResult: ({ result }) => {
          if (result.type === 'success' && result.data?.field) {
              addField(result.data.field);
              openFieldModal = false;
          }
      },
  });

  const updateForm = superForm(data.updateFieldForm, {
      validators: zodClient(updateFieldSchema),
      resetForm: false,
      onResult: ({ result }) => {
          if (result.type === 'success') {
              openFieldModal = false;
          }
      }
  });

    // Destructure form data and messages
    const { message: createMessage } = createForm;
    const { message: updateMessage } = updateForm; 
    const { message: deleteMessage } = deleteForm;
    const { message: facilityMessage } = facilityForm;

  let hiddenDrawer = $state(true);
  let openDelete: boolean = $state(false);
  let fieldToDelete: Field | null = $state(null);
  let fieldIdToDelete: number | undefined = $state(undefined);
  let openFieldModal: boolean = $state(false);
  let currentField: Field | any = $state({});
  let isEditMode: boolean = $state(false);

  $effect(() => {
      hiddenDrawer = !$showCreateFacility;
  });

  $effect(() => {
      if (!hiddenDrawer) {
          toggleCreateFacility(true);
      } else {
          toggleCreateFacility(false);
      }
  });

  function addNewField() {
      currentField = {};
      isEditMode = false;
      createForm.reset();
      createForm.form.update(data => ({
          ...data,
          facility_id: $selectedFacility?.facility_id ?? 0,
          name: '',
          size: '11v11',
          field_type: 'full',
          half_fields: [],
          availabilities: []
      }));
      openFieldModal = true;
  }

  function editField(field: Field) {
      currentField = field;
      isEditMode = true;
      updateForm.reset();
      updateForm.form.set({
          field_id: field.field_id,
          facility_id: field.facility_id,
          name: field.name,
          size: field.size,
          field_type: field.field_type,
          is_active: field.is_active
      });
      // Clear any tainted state
      updateForm.tainted.set(undefined);
      openFieldModal = true;
  }

  function prepareDeleteField(field: Field) {
      fieldToDelete = field;
      fieldIdToDelete = field.field_id;
      openDelete = true;
  }

  const showHalfFields = derived(filteredFields, $filteredFields => 
    $filteredFields.some(f => (f.half_subfields?.length ?? 0) > 0)
  );
  const showQuarterFields = derived(filteredFields, $filteredFields => 
    $filteredFields.some(f => 
      ((f.quarter_subfields?.length ?? 0) > 0) ||
      ((f.half_subfields?.some(h => (h.quarter_subfields?.length ?? 0) > 0)) ?? false)
    )
  );

</script>


<main class="relative h-full w-full overflow-y-auto bg-white dark:bg-gray-800">
  <h1 class="hidden">Fields</h1>
  <div class="p-4">
    <Breadcrumb class="mb-5">
      <BreadcrumbItem home>Home</BreadcrumbItem>
      <BreadcrumbItem href="/fields">Fields</BreadcrumbItem>
    </Breadcrumb>
    <Heading tag="h1" class="text-xl font-semibold text-gray-900 sm:text-2xl dark:text-white">Fields</Heading>

    <Toolbar embedded class="w-full py-4 text-gray-500 dark:text-gray-300">
      <Input placeholder="Search for fields" class="me-4 w-80 border xl:w-96" />
      <div class="border-l border-gray-100 pl-2 dark:border-gray-700">
        <ToolbarButton color="dark" class="m-0 rounded p-1 hover:bg-gray-100 focus:ring-0 dark:hover:bg-gray-700">
          <CogSolid size="lg" />
        </ToolbarButton>
        <ToolbarButton color="dark" class="m-0 rounded p-1 hover:bg-gray-100 focus:ring-0 dark:hover:bg-gray-700">
          <TrashBinSolid size="lg" />
        </ToolbarButton>
        <ToolbarButton color="dark" class="m-0 rounded p-1 hover:bg-gray-100 focus:ring-0 dark:hover:bg-gray-700">
          <ExclamationCircleSolid size="lg" />
        </ToolbarButton>
        <ToolbarButton color="dark" class="m-0 rounded p-1 hover:bg-gray-100 focus:ring-0 dark:hover:bg-gray-700">
          <DotsVerticalOutline size="lg" />
        </ToolbarButton>
      </div>
      <div class="flex items-center space-x-2">
        <Button size="sm" class="gap-2 px-3 whitespace-nowrap" onclick={() => addNewField()}>
          <PlusOutline size="sm" />Add field
        </Button>
        <Button size="sm" color="alternative" class="gap-2 px-3">
          <DownloadSolid size="md" class="-ml-1" />Export
        </Button>
      </div>
    </Toolbar>
  </div>
  
  {#if !$selectedFacility}
    <div class="flex items-center justify-center p-8">
      <div class="text-center">
        <p class="text-gray-500 dark:text-gray-400 text-lg">
          To get started here, create your first facility in the bottom left
        </p>
      </div>
    </div>
  {:else}
    <Table>
      <TableHead class="border-y border-gray-200 bg-gray-100 dark:border-gray-700">
        <TableHeadCell class="w-4 p-4"><Checkbox /></TableHeadCell>
        <TableHeadCell class="p-4 font-medium">Name</TableHeadCell>
        <TableHeadCell class="p-4">Size</TableHeadCell>
        <TableHeadCell class="p-4">Field Type</TableHeadCell>
        {#if $showHalfFields}
          <TableHeadCell class="p-4">Half Fields</TableHeadCell>
        {/if}
        {#if $showQuarterFields}
          <TableHeadCell class="p-4">Quarter Fields</TableHeadCell>
        {/if}
        <TableHeadCell class="p-4">Status</TableHeadCell>
        <TableHeadCell class="p-4">Actions</TableHeadCell>
      </TableHead>
      <TableBody>
        {#each $filteredFields as field}
          <TableBodyRow class="text-base">
            <TableBodyCell class="w-4 p-4"><Checkbox /></TableBodyCell>
            <TableBodyCell class="p-4 font-medium">{field.name}</TableBodyCell>
            <TableBodyCell class="p-4">{field.size}</TableBodyCell>
            <TableBodyCell class="p-4">{field.field_type}</TableBodyCell>
            {#if $showHalfFields}
              <TableBodyCell class="p-4">
                {#each field.half_subfields ?? [] as h (h.field_id)}
                  <Badge border color="blue" class="mr-2">{h.name}</Badge>
                {/each}
              </TableBodyCell>
            {/if}
            {#if $showQuarterFields}
              <TableBodyCell class="p-4">
                {#each [...(field.quarter_subfields ?? []), ...((field.half_subfields?.flatMap(h => h.quarter_subfields ?? [])) ?? [])] as q (q.field_id)}
                  <Badge border color="blue" class="mr-2">{q.name}</Badge>
                {/each}
              </TableBodyCell>
            {/if}
            <TableBodyCell class="p-4">
              <div class="flex items-center gap-2">
                <Indicator color={field.is_active ? 'green' : 'red'} />
                {field.is_active ? 'Active' : 'Inactive'}
              </TableBodyCell>
            <TableBodyCell class="space-x-2 p-4">
              <Button size="sm" class="gap-2 px-3" onclick={() => editField(field)}>
                <EditOutline size="sm" /> Edit
              </Button>
              <Button color="red" size="sm" class="gap-2 px-3" onclick={() => prepareDeleteField(field)}>
                <TrashBinSolid size="sm" /> Delete Field
              </Button>
            </TableBodyCell>
          </TableBodyRow>
        {/each}
      </TableBody>
    </Table>
  {/if}
</main>

<Drawer placement="right" bind:hidden={hiddenDrawer}>
  <FacilityDrawer title="Add New Facility" bind:hidden={hiddenDrawer} form={facilityForm} />
</Drawer>

<!-- Delete Modal -->
<DeleteModal 
bind:open={openDelete} 
form={deleteForm} 
actionName="deleteField"
title={`Are you sure you want to delete the field "${fieldToDelete?.name ?? ''}"?`}
yes="Yes, delete field"
no="No, cancel">
<input type="hidden" name="field_id" value={fieldIdToDelete ?? ''} />
</DeleteModal>

<!-- Field Modal -->
<FieldModal 
bind:open={openFieldModal} 
data={currentField} 
form={isEditMode ? updateForm : createForm} 
actionPath={isEditMode ? '?/updateField' : '?/createField'} 
/>

<!-- Toast messages -->
<ToastMessage message={$createMessage} />
<ToastMessage message={$updateMessage} />
<ToastMessage message={$deleteMessage} />
<ToastMessage message={$facilityMessage} />