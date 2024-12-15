<script lang="ts">
    import { superForm } from 'sveltekit-superforms/client';
    import type { SuperValidated } from 'sveltekit-superforms';
    import { fieldCreateSchema } from '$lib/schemas/field';
    import { page } from '$app/stores';
    import EditableField from './EditableField.svelte';
    import { z } from 'zod';
    import { dropdownState } from '$stores/FacilityDropdownState';
    import {dropdownState as fieldDropdownState} from '$stores/fieldDropdownState';
	import SuperDebug from 'sveltekit-superforms';
	import { addField } from '$stores/fields';

    type FieldFormData = SuperValidated<z.infer<typeof fieldCreateSchema>>;

    let { form: formData } = $props<{ form: FieldFormData }>();
    let formElement: HTMLFormElement;

    const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const;
    let nextDayIndex = $state(0);

    const { form, errors, enhance, message } = superForm(formData, {
        taintedMessage: null,
        dataType: 'json',
        onUpdate: ({ form }) => {
            console.log('Form data being submitted:', form.data);
        },
        onResult: ({ result }) => {
            console.log('Form submission result:', result);
            if (result.type === 'success') {
                if (result.data?.field) {
                    addField(result.data.field);
                    fieldDropdownState.update(state => ({
                        ...state,
                        showCreateField: false,
                        selectedField: result.data?.field || null
                    }));
                }
            }
        },
        onError: (err) => {
            console.error('Form submission error:', err);
        }
    });

    $form.is_active = true;

    const fieldSizeOptions = [
        { value: '11v11', label: '11v11' },
        { value: '8v8', label: '8v8' },
        { value: '5v5', label: '5v5' },
        { value: '3v3', label: '3v3' }
    ];
    // Subscribe to the facility dropdown state and update the form's facility_id
    $effect(() => {
        if ($dropdownState.selectedFacility) {
            form.update($form => ({
                ...$form,
                facility_id: $dropdownState.selectedFacility?.facility_id
            }));
        }
    });

    function addHalfFields() {
        form.update(($form) => ({
            ...$form,
            half_fields: [
                { name: '', field_type: 'half', quarter_fields: [] },
                { name: '', field_type: 'half', quarter_fields: [] }
            ]
        }));
    }

    function addQuarterFields(halfFieldIndex: number) {
        form.update(($form) => {
            const newForm = { ...$form };
            newForm.half_fields[halfFieldIndex].quarter_fields = [
                { name: '', field_type: 'quarter' },
                { name: '', field_type: 'quarter' }
            ];
            return newForm;
        });
    }

    function addAvailability() {
        if (nextDayIndex < daysOfWeek.length) {
            const day = daysOfWeek[nextDayIndex];
            form.update($form => {
                const availabilities = ($form.availabilities || []);
                const newAvailability = {
                    day_of_week: day,
                    start_time: '16:00',
                    end_time: '22:00'
                };
                nextDayIndex++;
                return {
                    ...$form,
                    availabilities: [...availabilities, newAvailability]
                };
            });
        }
    }

    function removeAvailability(index: number) {
        form.update($form => {
            const availabilities = [...($form.availabilities || [])];
            availabilities.splice(index, 1);
            return {
                ...$form,
                availabilities
            };
        });
        nextDayIndex--;
    }
</script>

<!-- <SuperDebug data={form} /> -->

<div class="detail-card">
    {#if $page.status === 400 && $page.form?.error}
        <div class="mb-4 p-4 rounded bg-red-100 text-red-700">
            {$page.form.error}
        </div>
    {/if}

    {#if !$dropdownState.selectedFacility}
        <div class="mb-4 p-4 rounded bg-yellow-100 text-yellow-700">
            Please select a facility first
        </div>
    {/if}

    <form
        method="POST"
        action="?/createField"
        use:enhance
        bind:this={formElement}
        class="space-y-4"
    >
        <EditableField
            {form}
            errors={$errors}
            name="name"
            label="Field Name"
            type="text"
            required={true}
            view_mode_style="title"
            hide_label_in_view={true}
        />

        <div class="detail-card-grid">
            <!-- Left Column - Existing Fields -->
            <div class="detail-card-content">
                <div class="space-y-4">
                    <EditableField
                        {form}
                        errors={$errors}
                        name="field_size"
                        label="Field Size"
                        type="select"
                        options={fieldSizeOptions}
                        required={true}
                    />

                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <h3 class="text-lg font-semibold">Half Fields</h3>
                            {#if !$form.half_fields?.length}
                                <button
                                    type="button"
                                    class="btn-add"
                                    onclick={addHalfFields}
                                >
                                    Add Half Fields
                                </button>
                            {/if}
                        </div>

                        {#if $form.half_fields?.length > 0}
                            {#each $form.half_fields as halfField, halfFieldIndex}
                                <div class="pl-4 border-l-2 border-gray-200 space-y-4">
                                    <div class="flex items-center gap-4">
                                        <EditableField
                                            {form}
                                            errors={$errors}
                                            name={`half_fields[${halfFieldIndex}].name`}
                                            label={`Half Field ${halfFieldIndex + 1} Name`}
                                            required={true}
                                            view_mode_style="pill"
                                            hide_label_in_view={true}
                                        />
                                    </div>

                                    <div class="space-y-4">
                                        <div class="flex justify-between items-center">
                                            <h4 class="text-md font-medium">Quarter Fields</h4>
                                            {#if !halfField.quarter_fields?.length}
                                                <button
                                                    type="button"
                                                    class="btn-add"
                                                    onclick={() => addQuarterFields(halfFieldIndex)}
                                                >
                                                    Add Quarter Fields
                                                </button>
                                            {/if}
                                        </div>

                                        {#if halfField.quarter_fields?.length > 0}
                                            {#each halfField.quarter_fields as quarterField, quarterFieldIndex}
                                                <div class="pl-4 border-l-2 border-gray-200">
                                                    <EditableField
                                                        {form}
                                                        errors={$errors}
                                                        name={`half_fields[${halfFieldIndex}].quarter_fields[${quarterFieldIndex}].name`}
                                                        label={`Quarter Field ${quarterFieldIndex + 1} Name`}
                                                        required={true}
                                                        view_mode_style="pill"
                                                        hide_label_in_view={true}
                                                    />
                                                </div>
                                            {/each}
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Right Column - Availability Management -->
            <div class="detail-card-content">
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold">Field Availability</h3>
                    <div class="space-y-4">
                        {#if $form.availabilities?.length > 0}
                            {#each $form.availabilities as availability, index}
                                <div class="flex items-center gap-4">
                                    <div class="w-24">
                                        <label 
                                            class="form-label" 
                                            for={`day-of-week-${index}`}
                                        >
                                            {availability.day_of_week}
                                        </label>
                                        <input 
                                            type="hidden" 
                                            id={`day-of-week-${index}`} 
                                            value={availability.day_of_week}
                                        />
                                    </div>
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name={`availabilities[${index}].start_time`}
                                        label="Start Time"
                                        type="text"
                                        placeholder="HH:MM"
                                    />
                                    <EditableField
                                        {form}
                                        errors={$errors}
                                        name={`availabilities[${index}].end_time`}
                                        label="End Time"
                                        type="text"
                                        placeholder="HH:MM"
                                    />
                                    <button
                                        type="button"
                                        class="btn-remove"
                                        onclick={() => removeAvailability(index)}
                                    >
                                        ×
                                    </button>
                                </div>
                            {/each}
                        {/if}
                        <button
                            type="button"
                            class="btn-add"
                            onclick={addAvailability}
                            disabled={nextDayIndex >= daysOfWeek.length}
                        >
                            Add Availability
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-end gap-4">
            <button type="submit" class="btn-primary">Create Field</button>
        </div>
    </form>
</div>

<style>
    .detail-card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
    }

    .detail-card-content {
        padding: 1rem;
    }
</style>
