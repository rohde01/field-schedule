<script lang="ts">
    import { writable } from 'svelte/store';
    import { tick } from 'svelte';
    import type { ValidationErrors } from 'sveltekit-superforms';

    export let form: Record<string, any>;
    export let errors: ValidationErrors<any>;
    export let name: string;
    export let label: string;
    export let type: 'text' | 'number' | 'select' | 'checkbox' = 'text';
    export let placeholder = '';
    export let required = false;
    export let view_mode_style: 'title' | 'pill' | 'normal' = 'normal';
    export let hide_label_in_view = false;
    export let min: number | undefined = undefined;
    export let max: number | undefined = undefined;
    export let options: { value: string | number; label: string }[] = [];

    let isEditMode = writable(true);
    let fieldError = '';

    $: fieldValue = form[name];
    $: {
        const error = errors[name];
        fieldError = error 
            ? Array.isArray(error) && error.length > 0 
                ? error[0] 
                : typeof error === 'string' ? error : ''
            : '';
    }
    $: selectedOption = options.find(opt => String(opt.value) === String(fieldValue ?? ''));

    async function handleBlur() {
        if (type === 'checkbox') {
            isEditMode.set(false);
        } else {
            if (fieldValue !== null && fieldValue !== undefined && fieldValue !== '') {
                isEditMode.set(false);
            }
        }
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter' && fieldValue) {
            isEditMode.set(false);
            event.preventDefault();
        }
    }

    function enterEditMode() {
        isEditMode.set(true);
        tick().then(() => {
            const input = document.getElementById(name) as HTMLInputElement | HTMLSelectElement | null;
            if (input && type !== 'checkbox') {
                input.focus();
            }
        });
    }
</script>

<div class="editable-field mb-4">
    {#if $isEditMode}
        <label for={name} class="form-label">
            {label}
        </label>
        {#if type === 'select'}
            <select 
                id={name}
                name={name}
                bind:value={form[name]}
                on:blur={handleBlur}
                class="form-input-sm"
                {required}
            >
                {#if !required}
                    <option value="">Select {label}</option>
                {/if}
                {#each options as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
        {:else if type === 'checkbox'}
            <div class="inline-flex items-center">
                <input 
                    id={name}
                    name={name}
                    type="checkbox"
                    bind:checked={form[name]}
                    class="rounded border-sage-300 text-mint-600 shadow-sm focus:border-mint-500 focus:ring-mint-500"
                    on:blur={handleBlur}
                />
                <span class="ml-2 text-sm text-sage-700">{label}</span>
            </div>
        {:else}
            <input 
                {type}
                id={name}
                {name}
                bind:value={form[name]}
                class="form-input-sm"
                {placeholder}
                {required}
                {min}
                {max}
                on:blur={handleBlur}
                on:keydown={handleKeydown}
            />
        {/if}
        {#if fieldError}
            <p class="text-sm text-red-600 mt-1">{fieldError}</p>
        {/if}
    {:else}
        <!-- Different view mode styles -->
        {#if !hide_label_in_view}
            <p class="detail-card-label">{label}</p>
        {/if}
        <div 
            class="{view_mode_style === 'title' ? 'detail-card-title' : view_mode_style === 'pill' ? 'field-tag' : 'detail-card-value'} cursor-pointer"
            on:click={enterEditMode}
            on:keydown={(e) => e.key === 'Enter' && enterEditMode()}
            role="button"
            tabindex="0"
        >
            {#if type === 'select'}
                {selectedOption?.label ?? fieldValue}
            {:else if type === 'checkbox'}
                {fieldValue ? 'Yes' : 'No'}
            {:else}
                {fieldValue}
            {/if}
        </div>
        <!-- Hidden input to ensure the value is included in the form submission even in view mode -->
        <input 
            type="hidden" 
            name={name} 
            value={
                type === 'checkbox'
                ? (fieldValue ? 'on' : '')
                : (fieldValue ?? '')
            } 
        />
    {/if}
</div>