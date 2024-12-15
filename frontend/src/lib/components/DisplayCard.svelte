<script module lang="ts">
    export type FieldStyle = 'pill' | 'normal' | 'subfields' | 'multiline';
    
    export interface Field {
        label: string;
        value: string | number | boolean | Array<any>;
        style?: FieldStyle;
    }
    
    export interface Column {
        fields: Field[];
    }

    export interface DeleteConfig {
        enabled: boolean;
        itemId?: number;
        itemName?: string;
        onDelete?: (id: number) => void;
        actionPath?: string;
        formField?: string;
        enhance?: (form: HTMLFormElement) => void;
    }
</script>

<script lang="ts">
    import { fade } from 'svelte/transition';
    import type { SubmitFunction } from '@sveltejs/kit';

    let { title, columns, deleteConfig = { enabled: false } } = $props<{
        title: string;
        columns: Column[];
        deleteConfig?: DeleteConfig;
    }>();

    let showDeleteConfirm = $state(false);
    let isDeleting = $state(false);

    const handleDelete: SubmitFunction = () => {
        isDeleting = true;
        return async ({ result }) => {
            if (result.type === 'success') {
                showDeleteConfirm = false;
                if (deleteConfig.onDelete && deleteConfig.itemId) {
                    deleteConfig.onDelete(deleteConfig.itemId);
                }
            }
            isDeleting = false;
        };
    };
</script>

<div class="detail-card">
    <div class="relative">
        <h2 class="detail-card-title">{title}</h2>
        
        <div class="detail-card-content">
            <div class="two-column-grid">
                {#each columns as column, i}
                    <div class="column">
                        {#each column.fields as field}
                            <div>
                                <p class="detail-card-label">{field.label}</p>
                                {#if field.style === 'subfields' && Array.isArray(field.value)}
                                    <div class="flex flex-wrap gap-2 mt-1">
                                        {#each field.value as subfield}
                                            <span class="field-tag">
                                                {subfield.name}
                                            </span>
                                        {/each}
                                    </div>
                                {:else if field.style === 'multiline'}
                                    <p class="detail-card-value whitespace-pre-line">{field.value}</p>
                                {:else if field.style === 'pill'}
                                    <div class="flex flex-wrap gap-2 mt-1">
                                        <span class="field-tag">
                                            {field.value}
                                        </span>
                                    </div>
                                {:else}
                                    <p class="detail-card-value">{field.value}</p>
                                {/if}
                            </div>
                        {/each}
                    </div>
                {/each}
            </div>
        </div>

        {#if deleteConfig.enabled}
            <button
                type="button"
                class="btn-trash"
                onclick={() => showDeleteConfirm = true}
                aria-label="Delete item"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            </button>

            {#if showDeleteConfirm}
                <div class="modal-overlay" transition:fade={{ duration: 200 }}>
                    <div class="modal-container"
                         role="dialog"
                         aria-labelledby="delete-modal-title"
                         aria-describedby="delete-modal-description">
                        <h3 id="delete-modal-title" class="modal-title">Delete {deleteConfig.itemName || 'Item'}</h3>
                        <p id="delete-modal-description" class="modal-description">
                            Are you sure you want to delete {deleteConfig.itemName || 'this item'}? This action cannot be undone.
                        </p>
                        <div class="modal-actions">
                            <button
                                type="button"
                                class="btn-secondary"
                                onclick={() => showDeleteConfirm = false}
                                disabled={isDeleting}
                            >
                                Cancel
                            </button>
                            <form
                                method="POST"
                                action={deleteConfig.actionPath || "?/delete"}
                                class="inline"
                            >
                                <input 
                                    type="hidden" 
                                    name={deleteConfig.formField || "id"} 
                                    value={deleteConfig.itemId} 
                                />
                                <button
                                    type="submit"
                                    class="btn-danger"
                                    disabled={isDeleting}
                                >
                                    {isDeleting ? 'Deleting...' : 'Delete'}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            {/if}
        {/if}
    </div>
</div>

<style>
    .two-column-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .column {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    :global(.whitespace-pre-line) {
        white-space: pre-line;
    }
</style>
