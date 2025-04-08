<script lang="ts">
  import { page } from '$app/stores';
</script>

<div class="min-h-[80vh] flex items-center justify-center py-12">
    <div class="w-full max-w-md text-center">
        <div class="bg-white px-8 py-6 shadow-sm rounded-lg border border-sage-200">
            <h2 class="text-2xl font-semibold text-red-600 mb-4">Authentication Error</h2>
            <p class="text-sage-600 mb-6">There was a problem verifying your email. Please try signing up again.</p>
            <a 
                href="/auth"
                class="inline-block bg-mint-500 hover:bg-mint-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
            >
                Return to Sign In
            </a>
        </div>
    </div>
</div>