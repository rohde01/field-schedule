<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import { zodClient } from 'sveltekit-superforms/adapters';
    import { createTeamSchema } from '$lib/schemas/team';
    export let data: { createForm: any; deleteForm: any };
    import { Breadcrumb, BreadcrumbItem, Button, Checkbox, Heading, Indicator } from 'flowbite-svelte';
    import { Input, Table, TableBody, TableBodyCell, TableBodyRow, TableHead } from 'flowbite-svelte';
    import { TableHeadCell, Toolbar, ToolbarButton } from 'flowbite-svelte';
    import { CogSolid, DotsVerticalOutline, DownloadSolid } from 'flowbite-svelte-icons';
    import { EditOutline, ExclamationCircleSolid, PlusOutline, TrashBinSolid } from 'flowbite-svelte-icons';
    import { teams } from '$lib/stores/teams';
    import type { Team } from '$lib/schemas/team';
    import DeleteModal from '$lib/components/DeleteModal.svelte';
    import TeamModal from '$lib/components/TeamModal.svelte';
    
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
    
    const deleteForm = superForm(data.deleteForm, {
      resetForm: true,
      onResult: ({ result }) => {
        if (result.type === 'success') {
          // Close the modal after successful deletion
          openDelete = false;
          // Remove the deleted team from the store
          if (result.data?.action === 'delete' && teamToDelete) {
            teams.update(currentTeams => 
              currentTeams.filter(team => team.team_id !== teamToDelete!.team_id)
            );
          }
        }
      }
    });

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

    // Function to prepare form for adding a new team
    function addNewTeam() {
      current_team = {};
      // Reset the form to defaults
      createForm.reset();
      openUser = true;
    }

    // Function to prepare form for editing a team
    function editTeam(team: Team) {
      current_team = team;
      createForm.reset(team);
      openUser = true;
    }

    // Function to prepare for team deletion
    function prepareDeleteTeam(team: Team) {
      teamToDelete = team;
      teamIdToDelete = team.team_id;
      openDelete = true;
      console.log('Opening delete modal for team:', team.name, 'Modal state:', openDelete);
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
        <Input placeholder="Search for teams" class="me-4 w-80 border xl:w-96" />
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
          <Button size="sm" class="gap-2 px-3 whitespace-nowrap" onclick={() => addNewTeam()}>
            <PlusOutline size="sm" />Add team
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
        {#each ['Name','Year','Gender','Academy','Level','Min Field Size','Preferred Field Size','Weekly Trainings','Status','Actions'] as title}
          <TableHeadCell class="p-4 font-medium">{title}</TableHeadCell>
        {/each}
      </TableHead>
      <TableBody>
        {#each $teams as team}
          <TableBodyRow class="text-base">
            <TableBodyCell class="w-4 p-4"><Checkbox /></TableBodyCell>
            <TableBodyCell class="p-4 font-medium">{team.name}</TableBodyCell>
            <TableBodyCell class="p-4">{team.year}</TableBodyCell>
            <TableBodyCell class="p-4">{team.gender}</TableBodyCell>
            <TableBodyCell class="p-4"><Checkbox checked={team.is_academy} disabled /></TableBodyCell>
            <TableBodyCell class="p-4">{team.level}</TableBodyCell>
            <TableBodyCell class="p-4">{formatFieldSize(team.minimum_field_size)}</TableBodyCell>
            <TableBodyCell class="p-4">{team.preferred_field_size ? formatFieldSize(team.preferred_field_size) : '–'}</TableBodyCell>
            <TableBodyCell class="p-4">{team.weekly_trainings}</TableBodyCell>
            <TableBodyCell class="p-4">
              <div class="flex items-center gap-2">
                <Indicator color={team.is_active ? 'green' : 'red'} />
                {team.is_active ? 'Active' : 'Inactive'}
              </div>
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
<TeamModal bind:open={openUser} data={current_team} form={createForm} />
<DeleteModal 
  bind:open={openDelete} 
  form={deleteForm}
  actionName="deleteTeam"
  title={`Are you sure you want to delete the team "${teamToDelete?.name ?? ''}"?`}
  yes="Yes, delete team"
  no="No, cancel">
  <input type="hidden" name="team_id" value={teamIdToDelete ?? ''} />
</DeleteModal>
