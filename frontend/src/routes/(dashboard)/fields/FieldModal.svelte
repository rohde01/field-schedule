<script lang="ts">
    import { Button, Input, Label, Modal, Select, Helper, Timepicker, Spinner } from 'flowbite-svelte';
    import { PlusOutline, MinusOutline, ClockOutline } from 'flowbite-svelte-icons';      
    import { selectedFacility } from '$lib/stores/facilities';
    import type { Field, FieldCreate } from '$lib/schemas/field';
    import { fieldSizeEnum, dayOfWeekEnum } from '$lib/schemas/field';
    import type { SuperForm } from 'sveltekit-superforms';
    
    let { 
      open = $bindable(true), 
      data = {} as Field | FieldCreate, 
      form: serverForm,
      actionPath = '?/createField'
    }: { 
      open: boolean; 
      data: Field | FieldCreate; 
      form: SuperForm<any, any>;
      actionPath?: string;
    } = $props();
  
    const { form: formData, enhance, errors, message, submitting } = serverForm;
    let saving = $state(false);
    
    $effect(() => {
      saving = $submitting;
    });
    
    // Check if we're in edit mode by checking if field_id exists in data
    // Using type guard to ensure TypeScript understands the type
    const isEditMode = $derived(() => {
      return 'field_id' in data && typeof data.field_id === 'number';
    });

    $effect(() => {
      if (open && data && Object.keys(data).length > 0) {
        formData.set(data);
      } else if (open && !isEditMode()) {
        formData.update(fd => ({
          ...fd,
          facility_id: $selectedFacility?.facility_id ?? fd.facility_id
        }));
      }
    });

    // Toggle half fields
    function toggleHalfFields() {
      const hf = $formData.half_fields || [];
      formData.update(fd => ({
        ...fd,
        half_fields: hf.length === 2 ? [] : [
          { name: '', field_type: 'half', quarter_fields: [] },
          { name: '', field_type: 'half', quarter_fields: [] }
        ]
      }));
    }
    // Toggle quarter fields for a given half-field index
    function toggleQuarterFields(idx: number) {
      const hf = [...($formData.half_fields || [])];
      if (!hf[idx]) return;
      
      hf[idx].quarter_fields = hf[idx].quarter_fields.length === 2
        ? []
        : [
            { name: '', field_type: 'quarter' },
            { name: '', field_type: 'quarter' }
          ];
      formData.update(fd => ({ ...fd, half_fields: hf }));
    }
</script>
  
  <Modal bind:open title={isEditMode() ? 'Edit Field' : 'Add new Field'} size="md" class="m-4">
    <!-- Modal body -->
    <div class="space-y-6 p-0">
      <form method="POST" action={actionPath} use:enhance id="field-form">
        <!-- Hidden fields -->
        {#if isEditMode()}
          <input type="hidden" name="field_id" value={isEditMode() ? (data as Field).field_id : undefined} />
        {/if}
        <input type="hidden" name="facility_id" value={$selectedFacility?.facility_id || $formData.facility_id} />
        <input type="hidden" name="field_type" value="full" />
        
        <div class="grid grid-cols-6 gap-6">
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Name</span>
            <Input name="name" id="name" class="border outline-none" placeholder="Field name" 
              bind:value={$formData.name} required />
            {#if $errors.name}
              <Helper class="mt-2" color="red">{$errors.name}</Helper>
            {/if}
          </Label>
          
          <Label class="col-span-6 space-y-2 sm:col-span-3">
            <span>Size</span>
            <Select name="size" id="size" bind:value={$formData.size} required>
              {#each Object.values(fieldSizeEnum.enum) as size}
                <option value={size}>{size}</option>
              {/each}
            </Select>
            {#if $errors.size}
              <Helper class="mt-2" color="red">{$errors.size}</Helper>
            {/if}
          </Label>
          
          {#if isEditMode()}
            <Label class="col-span-6 space-y-2 sm:col-span-3">
              <span>Status</span>
              <Select items={[{value:true,name:'Active'},{value:false,name:'Inactive'}]} bind:value={$formData.is_active} name="is_active" />
            </Label>
          {/if}
          
          <!-- Half fields section -->
          {#if !isEditMode()}
            <div class="col-span-6">
              <h3 class="text-lg font-medium">Half Fields</h3>
              
              {#if !$formData.half_fields?.length}
                <Button size="sm" outline on:click={toggleHalfFields} class="mb-2">
                  <PlusOutline size="sm" class="mr-1"/>Add Half Fields
                </Button>
              {:else}
                <Button size="sm" outline on:click={toggleHalfFields} class="mb-2">
                  <MinusOutline size="sm" class="mr-1"/>Remove Half Fields
                </Button>
                <div class="space-y-4">
                  {#each $formData.half_fields as half, idx}
                    <div class="p-2">
                      <Label class="space-y-2">
                        <span>Half Field {idx + 1} Name</span>
                        <Input name={`half_fields[${idx}].name`} bind:value={$formData.half_fields[idx].name} clearable required />
                      </Label>
                      {#if half.quarter_fields.length === 0}
                        <Button size="xs" outline on:click={() => toggleQuarterFields(idx)} class="mt-2">
                          <PlusOutline size="sm" class="mr-1"/>Add Quarter Fields
                        </Button>
                      {:else}
                        <Button size="xs" outline on:click={() => toggleQuarterFields(idx)} class="mt-2">
                          <MinusOutline size="sm" class="mr-1"/>Remove Quarter Fields
                        </Button>
                        <div class="ml-4 space-y-2">
                          {#each half.quarter_fields as q, qidx}
                            <Label class="space-y-2">
                              <span>Quarter Field {qidx + 1} Name</span>
                              <Input name={`half_fields[${idx}].quarter_fields[${qidx}].name`} bind:value={$formData.half_fields[idx].quarter_fields[qidx].name} size="sm" clearable required />
                            </Label>
                          {/each}
                        </div>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
          
          <!-- Availabilities section -->
          <div class="col-span-6">
            <h3 class="text-lg font-medium">Availabilities</h3>
            
            {#if !isEditMode()}
              <!-- Dynamic availability slots in create mode -->
              {#each $formData.availabilities || [] as availability, index}
                <div class="grid grid-cols-4 gap-2 mb-2 p-2 items-end">
                  <Label class="col-span-1">
                    <span>Day</span>
                    <Select name={`availabilities[${index}].day_of_week`} bind:value={$formData.availabilities[index].day_of_week}>
                      {#each Object.values(dayOfWeekEnum.enum) as day}
                        <option value={day}>{day}</option>
                      {/each}
                    </Select>
                  </Label>
                  <Label class="col-span-2">
                    <span>Time Range</span>
                    <Timepicker
                      icon={ClockOutline as any}
                      type="range"
                      bind:value={$formData.availabilities[index].start_time!}
                      bind:endValue={$formData.availabilities[index].end_time!}
                      on:select={(e) => {
                        const { time, endTime } = e.detail;
                        formData.update(fd => {
                          const av = [...(fd.availabilities || [])];
                          av[index] = { ...av[index], start_time: time, end_time: endTime! };
                          return { ...fd, availabilities: av };
                        });
                      }}
                    />
                  </Label>
                  <div class="col-span-1">
                    <Button type="button" size="sm" color="red" on:click={() => {
                      formData.update(fd => ({
                        ...fd,
                        availabilities: (fd.availabilities || []).filter((_: any, i: number) => i !== index)
                      }));
                    }}>Remove</Button>
                  </div>
                </div>
              {/each}
              
              <!-- Add new availability below slots -->
              <Button type="button" size="sm" class="mt-2" on:click={() => {
                formData.update(fd => {
                  const days = Object.values(dayOfWeekEnum.enum);
                  const lastDay = fd.availabilities?.[fd.availabilities.length - 1]?.day_of_week;
                  const idx = days.indexOf(lastDay as any);
                  const nextDay = days[(idx + 1) % days.length];
                  return {
                    ...fd,
                    availabilities: [
                      ...(fd.availabilities || []),
                      { day_of_week: nextDay, start_time: '16:00', end_time: '20:30' }
                    ]
                  };
                });
              }}>Add Availability</Button>
              
              {#if $errors.availabilities}
                <Helper class="mt-2" color="red">{$errors.availabilities}</Helper>
              {/if}
            {:else}
              <!-- In edit mode, show existing availabilities with disabled inputs -->
              {#if (data as Field).availability && Object.keys((data as Field).availability).length > 0}
                <div class="space-y-2">
                  {#each Object.entries((data as Field).availability) as [day, timeSlot], index}
                    <div class="grid grid-cols-4 gap-2 mb-2 p-2 items-end">
                      <Label class="col-span-1">
                        <span>Day</span>
                        <Input disabled readonly value={day} />
                      </Label>
                      <Label class="col-span-3">
                        <span>Time Range</span>
                        <Input disabled readonly value={`${timeSlot.start_time} - ${timeSlot.end_time}`} />
                      </Label>
                    </div>
                  {/each}
                </div>
              {:else}
                <Input disabled readonly value="No availabilities set for this field" />
              {/if}
            {/if}
          </div>
        </div>
        
        {#if $message}
          <div class="mt-4 text-sm text-red-600">{$message}</div>
        {/if}
      </form>
    </div>
  
    <!-- Modal footer -->
    <svelte:fragment slot="footer">
      <Button type="submit" form="field-form" disabled={saving}>
        {#if saving}
          <Spinner class="me-3" size="4" color="white" />Saving...
        {:else}
          {isEditMode() ? 'Save changes' : 'Add field'}
        {/if}
      </Button>
    </svelte:fragment>
  </Modal>

