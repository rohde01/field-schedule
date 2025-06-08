<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createTeamSchema, updateTeamSchema } from '$lib/schemas/team';
    export let data: { createForm: any; updateForm: any; deleteForm: any };
    import { Breadcrumb, BreadcrumbItem, Button, Checkbox, Heading, Indicator } from 'flowbite-svelte';
    import { Input, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, Badge } from 'flowbite-svelte';
    import { TableHeadCell, Toolbar, ToolbarButton } from 'flowbite-svelte';
    import { CogSolid, DotsVerticalOutline, DownloadSolid } from 'flowbite-svelte-icons';
    import { EditOutline, ExclamationCircleSolid, PlusOutline, TrashBinSolid } from 'flowbite-svelte-icons';
    import { teams, updateTeam, deleteTeam } from '$lib/stores/teams';
    import type { Team } from '$lib/schemas/team';
    import DeleteModal from '$lib/components/DeleteModal.svelte';
    import TeamModal from './TeamModal.svelte';
    import ToastMessage from '$lib/components/Toast.svelte';
    import { exportTeamsToExcel } from '$lib/utils/teams-excel';
    
    // Initialize superForms with client-side options
    const createForm = superForm(data.createForm, {
      validators: zodClient(createTeamSchema),
      resetForm: true,
      onResult: ({ result }) => {
        if (result.type === 'success') {
          // Close the modal after successful submission
          openUser = false;
        }
      }
    });
    
    const updateForm = superForm(data.updateForm, {
      validators: zodClient(updateTeamSchema),
      resetForm: false,
      onResult: ({ result }) => {
        if (result.type === 'success') {
          openUser = false;
        
          if (result.data?.team) {
            updateTeam(result.data.team);
          }
        }
      }
    });
    
    const deleteForm = superForm(data.deleteForm, {
      resetForm: true,
      onResult: ({ result }) => {
        if (result.type === 'success') {
          // Close the modal after successful deletion
          openDelete = false;
          
          // Remove the deleted team from the store
          if (teamIdToDelete) {
            deleteTeam(teamIdToDelete);
          }
        }
      }
    });

    // Destructure form data and messages
    const { message: createMessage } = createForm;
    const { message: updateMessage } = updateForm; 
    const { message: deleteMessage } = deleteForm;

    function formatFieldSize(size: number): string {
        switch (size) {
            case 1000:
                return '11v11';
            case 500:
                return '8v8, Half 11v11';
            case 250:
                return '5v5, Half 8v8, Quarter 11v11';
            case 125:
                return '3v3, Half 5v5, Quarter 8v8';
            default:
                return `${size}`;
        }
    }

    let openUser: boolean = false; // modal control
    let openDelete: boolean = false; // modal control
    let current_team: Team | any = {};
    let teamToDelete: Team | null = null;
    let teamIdToDelete: number | undefined;
    let isEditMode: boolean = false;
    let searchTerm: string = '';
    $: filteredTeams = $teams.filter(team => team.name.toLowerCase().includes(searchTerm.toLowerCase()));

    // Function to prepare form for adding a new team
    function addNewTeam() {
      current_team = {};
      isEditMode = false;
      createForm.reset();
      openUser = true;
    }

    // Function to prepare form for editing a team
    function editTeam(team: Team) {
      current_team = team;
      isEditMode = true;
      updateForm.reset({ 
        data: team 
      });
      openUser = true;
    }

    // Function to prepare for team deletion
    function prepareDeleteTeam(team: Team) {
      teamToDelete = team;
      teamIdToDelete = team.team_id;
      openDelete = true;
    }
</script>
  
<main class="relative h-full w-full overflow-y-auto bg-white dark:bg-gray-800">
  <h1 class="hidden">CRUD: Teams</h1>
  <div class="p-4">
    <Breadcrumb class="mb-5">
      <BreadcrumbItem home>Home</BreadcrumbItem>
      <BreadcrumbItem href="/crud/teams">Teams</BreadcrumbItem>
    </Breadcrumb>
    <Heading tag="h1" class="text-xl font-semibold text-gray-900 sm:text-2xl dark:text-white">Teams</Heading>

    <Toolbar embedded class="w-full py-4 text-gray-500  dark:text-gray-300">
      <Input bind:value={searchTerm} placeholder="Search for teams" class="me-4 w-80 border xl:w-96" />
      <div class="flex items-center space-x-2 ml-auto">
        <Button size="sm" class="gap-2 px-3 whitespace-nowrap" onclick={() => addNewTeam()}>
          <PlusOutline size="sm" />Add team
        </Button>
        <Button size="sm" color="alternative" class="gap-2 px-3" onclick={() => exportTeamsToExcel(filteredTeams)}>
          <DownloadSolid size="md" class="-ml-1" />Export
        </Button>
      </div>
    </Toolbar>
  </div>
  <Table>
    <TableHead class="border-y border-gray-200 bg-gray-100 dark:border-gray-700">
      <TableHeadCell class="w-4 p-4"><Checkbox /></TableHeadCell>
      {#each ['Name','Year','Gender','Academy','Level','Field Size','Weekly Trainings','Status','Actions'] as title}
        <TableHeadCell class="p-4 font-medium">{title}</TableHeadCell>
      {/each}
    </TableHead>
    <TableBody>
      {#each filteredTeams as team}
        <TableBodyRow class="text-base">
          <TableBodyCell class="w-4 p-4"><Checkbox /></TableBodyCell>
          <TableBodyCell class="p-4 font-medium">{team.name}</TableBodyCell>
          <TableBodyCell class="p-4">{team.year}</TableBodyCell>
          <TableBodyCell class="p-4">{team.gender}</TableBodyCell>
          <TableBodyCell class="p-4"><Checkbox checked={team.is_academy} disabled /></TableBodyCell>
          <TableBodyCell class="p-4">{team.level}</TableBodyCell>
          <TableBodyCell class="p-4">
            {#each formatFieldSize(team.minimum_field_size).split(', ') as size}
              <Badge border color="green" class="mr-2">{size}</Badge>
            {/each}
          </TableBodyCell>
          <TableBodyCell class="p-4">{team.weekly_trainings}</TableBodyCell>
          <TableBodyCell class="p-4">
            <div class="flex items-center gap-2">
              <Indicator color={team.is_active ? 'green' : 'red'} />
              {team.is_active ? 'Active' : 'Inactive'}
            </TableBodyCell>
          <TableBodyCell class="space-x-2 p-4">
            <Button size="sm" class="gap-2 px-3" onclick={() => editTeam(team)}>
              <EditOutline size="sm" /> Edit team
            </Button>
            <Button color="red" size="sm" class="gap-2 px-3" onclick={() => prepareDeleteTeam(team)}>
              <TrashBinSolid size="sm" /> Delete team
            </Button>
          </TableBodyCell>
        </TableBodyRow>
      {/each}
    </TableBody>
  </Table>
</main>
  
<!-- Modals -->
<TeamModal 
  bind:open={openUser} 
  data={current_team} 
  form={isEditMode ? updateForm : createForm} 
  actionPath={isEditMode ? '?/update' : '?/create'} 
/>
<DeleteModal 
  bind:open={openDelete} 
  form={deleteForm}
  actionName="deleteTeam"
  title={`Are you sure you want to delete the team "${teamToDelete?.name ?? ''}"?`}
  yes="Yes, delete team"
  no="No, cancel">
  <input type="hidden" name="team_id" value={teamIdToDelete ?? ''} />
</DeleteModal>

<!-- Toast messages -->
<ToastMessage message={$createMessage} />
<ToastMessage message={$updateMessage} />
<ToastMessage message={$deleteMessage} />
