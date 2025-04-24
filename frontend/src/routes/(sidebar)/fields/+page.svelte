<script lang="ts">
    import { fields, deleteField, addField } from '$lib/stores/fields.js';
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { facilitySchema } from '$lib/schemas/facility';
    import { showCreateFacility, toggleCreateFacility, selectedFacility } from '$lib/stores/facilities';
    import FacilityDrawer from '$lib/components/FacilityDrawer.svelte';
    import { Drawer } from 'flowbite-svelte';
    import DeleteModal from '$lib/components/DeleteModal.svelte';
    import type { Field } from '$lib/schemas/field';
    import { fieldCreateSchema } from '$lib/schemas/field';
    import FieldModal from '$lib/components/FieldModal.svelte';

    import { Breadcrumb, BreadcrumbItem, Button, Checkbox, Heading, Indicator } from 'flowbite-svelte';
    import { Input, Table, TableBody, TableBodyCell, TableBodyRow, TableHead } from 'flowbite-svelte';
    import { TableHeadCell, Toolbar, ToolbarButton } from 'flowbite-svelte';
    import { CogSolid, DotsVerticalOutline, DownloadSolid } from 'flowbite-svelte-icons';
    import { EditOutline, ExclamationCircleSolid, PlusOutline, TrashBinSolid } from 'flowbite-svelte-icons';

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
        validators: zodClient(facilitySchema),
        resetForm: true,
        onResult: ({ result }) => {
            if (result.type === 'success') {
                hiddenDrawer = true;
            }
        }
    });

    const createForm = superForm(data.createFieldForm, {
        taintedMessage: null,
        dataType: 'json',
        validators: zodClient(fieldCreateSchema),
        resetForm: true,
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: ({ result }) => {
            console.log('Form submission result:', result);
            if (result.type === 'success' && result.data?.field) {
                addField(result.data.field);
                openFieldModal = false;
            }
        },
        onError: (err) => {
            console.error('Form submission error:', err);
        }
    });

    let hiddenDrawer = $state(true);
    let openDelete: boolean = $state(false);
    let fieldToDelete: Field | null = $state(null);
    let fieldIdToDelete: number | undefined = $state(undefined);
    let openFieldModal: boolean = $state(false);
    let currentField: Field | any = $state({});

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
        createForm.reset(field);
        openFieldModal = true;
    }

    function prepareDeleteField(field: Field) {
        fieldToDelete = field;
        fieldIdToDelete = field.field_id;
        openDelete = true;
        console.log('Opening delete modal for field:', field.name, 'Modal state:', openDelete);
    }

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
    <Table>
      <TableHead class="border-y border-gray-200 bg-gray-100 dark:border-gray-700">
        <TableHeadCell class="w-4 p-4"><Checkbox /></TableHeadCell>
        {#each ['Name', 'Size', 'Field Type', 'Status', 'Actions'] as title}
          <TableHeadCell class="p-4 font-medium">{title}</TableHeadCell>
        {/each}
      </TableHead>
      <TableBody>
        {#each $fields as field}
          <TableBodyRow class="text-base">
            <TableBodyCell class="w-4 p-4"><Checkbox /></TableBodyCell>
            <TableBodyCell class="p-4 font-medium">{field.name}</TableBodyCell>
            <TableBodyCell class="p-4">{field.size}</TableBodyCell>
            <TableBodyCell class="p-4">{field.field_type}</TableBodyCell>
            <TableBodyCell class="p-4">
              <div class="flex items-center gap-2">
                <Indicator color={field.is_active ? 'green' : 'red'} />
                {field.is_active ? 'Active' : 'Inactive'}
              </div>
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

<FieldModal bind:open={openFieldModal} data={currentField} form={createForm} />
