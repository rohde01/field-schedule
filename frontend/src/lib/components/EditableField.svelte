<script lang="ts">
    import { writable, type Writable } from 'svelte/store';
    import { tick } from 'svelte';
    import type { ValidationErrors } from 'sveltekit-superforms';

    export let form: Writable<Record<string, any>>;
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

    const initialEditMode = (() => {
        const keys = name.split(/[\[\].]+/).filter(Boolean);
        const lastKey = keys[keys.length - 1];
        return !(lastKey === 'start_time' || lastKey === 'end_time');
    })();
    
    let isEditMode = writable(initialEditMode);
    let fieldError = '';

    $: fieldValue = (() => {
        const keys = name.split(/[\[\].]+/).filter(Boolean);
        let value = $form;
        for (const key of keys) {
            if (value && typeof value === 'object') {
                const index = parseInt(key);
                value = isNaN(index) ? value[key] : value[index];
            } else {
                return undefined;
            }
        }
        return value;
    })();

    // Initialize default values after fieldValue is computed
    $: {
        const keys = name.split(/[\[\].]+/).filter(Boolean);
        const lastKey = keys[keys.length - 1];
        const isEmpty = 
            fieldValue === undefined || 
            fieldValue === null || 
            (typeof fieldValue === 'string' && fieldValue === '');
        
        if ((lastKey === 'start_time' || lastKey === 'end_time') && isEmpty) {
            const defaultValue = lastKey === 'start_time' ? '16:00' : '22:00';
            updateFormValue(defaultValue);
        }
    }

    $: {
        const error = errors[name];
        fieldError = error 
            ? Array.isArray(error) && error.length > 0 
                ? error[0] 
                : typeof error === 'string' ? error : ''
            : '';
    }
    $: selectedOption = options.find(opt => String(opt.value) === String(fieldValue ?? ''));

    $: hide_label_in_view = (() => {
        const keys = name.split(/[\[\].]+/).filter(Boolean);
        const lastKey = keys[keys.length - 1];
        return hide_label_in_view || lastKey === 'start_time' || lastKey === 'end_time';
    })();

    function updateFormValue(value: any) {
        form.update(f => {
            const keys = name.split(/[\[\].]+/).filter(Boolean);
            let current: any = f;
            
            for (let i = 0; i < keys.length - 1; i++) {
                const key = keys[i];
                const index = parseInt(key);
                
                if (isNaN(index)) {
                    if (typeof current !== 'object') current = {};
                    if (!current[key]) current[key] = {};
                    current = current[key];
                } else {
                    if (!Array.isArray(current)) current = [];
                    while (current.length <= index) {
                        current.push({});
                    }
                    current = current[index];
                }
            }
            
            const lastKey = keys[keys.length - 1];
            const lastIndex = parseInt(lastKey);
            if (isNaN(lastIndex)) {
                if (typeof current !== 'object') current = {};
                current[lastKey] = value;
            } else {
                if (!Array.isArray(current)) current = [];
                while (current.length <= lastIndex) {
                    current.push(null);
                }
                current[lastIndex] = value;
            }
            
            return f;
        });
    }

    async function handleBlur() {
        if (type === 'checkbox') {
            isEditMode.set(false);
        } else {
            const hasValue = fieldValue !== null && fieldValue !== undefined && 
                (typeof fieldValue !== 'string' || fieldValue !== '');
            const isNestedField = name.includes('[') && name.includes(']');
            
            if (hasValue || isNestedField) {
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
            const input = document.getElementById(name);
            input?.focus();
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
                value={$form[name]}
                on:change={(e) => {
                    const target = e.target as HTMLSelectElement;
                    updateFormValue(target.value);
                }}
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
                    checked={$form[name]}
                    on:change={(e) => {
                        const target = e.target as HTMLInputElement;
                        updateFormValue(target.checked);
                    }}
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
                value={$form[name] ?? ''}
                on:input={(e) => {
                    const target = e.target as HTMLInputElement;
                    updateFormValue(target.value);
                }}
                on:blur={handleBlur}
                on:keydown={handleKeydown}
                class="form-input-sm"
                {placeholder}
                {required}
                {min}
                {max}
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
                {selectedOption?.label ?? fieldValue ?? ''}
            {:else if type === 'checkbox'}
                {fieldValue ? 'Yes' : 'No'}
            {:else}
                {fieldValue ?? ''}
            {/if}
        </div>
        <!-- Hidden input to ensure the value is included in the form submission even in view mode -->
        <input 
            type="hidden" 
            name={name} 
            bind:value={$form[name]}
        />
    {/if}
</div>