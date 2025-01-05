<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData } from './$types';
    export let form: ActionData;
    
    let submitting = false;
    let success = false;
</script>

<div class="fixed inset-0 z-20 overflow-y-auto">
    <!-- Overlay that fades the background -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm"></div>
    
    <!-- Modal container -->
    <div class="flex min-h-screen items-center justify-center p-4">
        <div class="relative bg-white p-12 rounded-2xl shadow-2xl w-full max-w-2xl z-30">
            {#if !success}
                <h1 class="text-4xl font-bold text-sage-800 mb-8 text-center">
                    Give your club a name to get started!
                </h1>

                <form 
                    method="POST" 
                    class="space-y-8"
                    use:enhance={() => {
                        submitting = true;
                        return async ({ update }) => {
                            await update();
                            submitting = false;
                            if (!form?.error) {
                                success = true;
                            }
                        };
                    }}
                >
                    <div class="space-y-3">
                        <label for="name" class="block text-lg font-medium text-sage-700"></label>
                        <input 
                            type="text" 
                            id="name" 
                            name="name" 
                            required 
                            disabled={submitting}
                            class="form-input text-lg py-3"
                            placeholder="Enter your club name"
                        />
                        {#if form?.error}
                            <p class="text-red-500 text-sm">{form.error}</p>
                        {/if}
                    </div>
                    <button 
                        type="submit" 
                        disabled={submitting}
                        class="btn-primary w-full text-lg py-3"
                    >
                        {submitting ? 'Creating...' : "Let's do it"}
                    </button>
                </form>
            {:else}
                <h1 class="text-4xl font-bold text-sage-800 mb-4 text-center">
                    Congrats on your new club! 🎉
                </h1>
                <p class="text-xl text-sage-600 mb-8 text-center">
                    Next we should map out your clubs training facilities 🏟️
                </p>
                <a 
                    href="/fields" 
                    class="btn-primary w-full text-lg py-3 text-center block mb-4"
                >
                    Take me there
                </a>
            {/if}
            
            <a 
                href={success ? "/club" : "/dashboard"} 
                class="btn-secondary w-full text-lg py-3 mt-4 text-center block hover:bg-sage-300 transition-colors"
            >
                Maybe Later
            </a>
        </div>
    </div>
</div>
