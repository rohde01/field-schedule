<script lang="ts">
    import { Button, Input, Label, Modal, Select, Helper, Timepicker } from 'flowbite-svelte';
    import type { FieldCreate } from '$lib/schemas/field';
    import type { SuperForm } from 'sveltekit-superforms';
    import { PlusOutline, MinusOutline, ClockOutline } from 'flowbite-svelte-icons';      
    import { selectedFacility } from '$lib/stores/facilities';
    
    let { open = $bindable(true), data = {} as FieldCreate, form }: { 
      open: boolean; 
      data: FieldCreate; 
      form: SuperForm<any, any>
    } = $props();
  
    const { form: formData, enhance, errors, message } = form;

    // Toggle half fields
    function toggleHalfFields() {
      const hf = $formData.half_fields;
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
      const hf = [...$formData.half_fields];
      hf[idx].quarter_fields = hf[idx].quarter_fields.length === 2
        ? []
        : [
            { name: '', field_type: 'quarter' },
            { name: '', field_type: 'quarter' }
          ];
      formData.update(fd => ({ ...fd, half_fields: hf }));
    }
</script>
  
  <Modal bind:open title={Object.keys(data).length ? 'Edit Field' : 'Add new Field'} size="md" class="m-4">
    <!-- Modal body -->
    <div class="space-y-6 p-0">
      <form method="POST" action="?/createField" use:enhance id="field-form">
        <!-- Hidden facility_id field -->
        <input type="hidden" name="facility_id" value={$selectedFacility?.facility_id} />
        
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
              <option value="11v11">11v11</option>
              <option value="8v8">8v8</option>
              <option value="5v5">5v5</option>
              <option value="3v3">3v3</option>
            </Select>
            {#if $errors.size}
              <Helper class="mt-2" color="red">{$errors.size}</Helper>
            {/if}
          </Label>
          
          <!-- Field type is always 'full' as per schema -->
          <input type="hidden" name="field_type" value="full" />
          
          <!-- Dynamic half and quarter fields -->
          <div class="col-span-6">
            <h3 class="text-lg font-medium">Half Fields</h3>
            {#if $formData.half_fields.length === 0}
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
          
          <!-- Availabilities section -->
          <div class="col-span-6">
            <h3 class="text-lg font-medium">Availabilities</h3>
            <!-- Dynamic availability slots -->
            {#each $formData.availabilities as availability, index}
              <div class="grid grid-cols-4 gap-2 mb-2 p-2 items-end">
                <Label class="col-span-1">
                  <span>Day</span>
                  <Select name={`availabilities[${index}].day_of_week`} bind:value={$formData.availabilities[index].day_of_week}>
                    {#each ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] as d}
                      <option value={d}>{d}</option>
                    {/each}
                  </Select>
                </Label>
                <Label class="col-span-2">
                  <span>Time Range</span>
                  <Timepicker
                  icon={ClockOutline as any}
                    type="range"
                    bind:value={$formData.availabilities[index].start_time}
                    bind:endValue={$formData.availabilities[index].end_time}
                    on:select={(e) => {
                      const { time, endTime } = e.detail;
                      formData.update(fd => {
                        const av = [...fd.availabilities];
                        av[index] = { ...av[index], start_time: time, end_time: endTime };
                        return { ...fd, availabilities: av };
                      });
                    }}
                  />
                </Label>
                <div class="col-span-1">
                  <Button type="button" size="sm" color="red" on:click={() => {
                    formData.update(fd => ({
                      ...fd,
                      availabilities: fd.availabilities.filter((_: any, i: number) => i !== index)
                    }));
                  }}>Remove</Button>
                </div>
              </div>
            {/each}
            
            <!-- Add new availability below slots -->
            <Button type="button" size="sm" class="mt-2" on:click={() => {
              formData.update(fd => ({
                ...fd,
                availabilities: [
                  ...fd.availabilities,
                  { day_of_week: 'Mon', start_time: '09:00', end_time: '10:00' }
                ]
              }));
            }}>Add Availability</Button>
            
            {#if $errors.availabilities}
              <Helper class="mt-2" color="red">{$errors.availabilities}</Helper>
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
      <Button type="submit" form="field-form">
        {Object.keys(data).length ? 'Save changes' : 'Add field'}
      </Button>
    </svelte:fragment>
  </Modal>

