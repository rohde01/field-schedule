<script>
  import { invalidate } from '$app/navigation'
  import { navigating, page } from '$app/stores'
  import { onMount } from 'svelte'
  import '../app.css'
  import Navbar from './(dashboard)/Navbar.svelte'
  import { Spinner } from 'flowbite-svelte'

  let { data, children } = $props()
  let { session, supabase } = data

  onMount(() => {
    const { data } = supabase.auth.onAuthStateChange((_, newSession) => {
      if (newSession?.expires_at !== session?.expires_at) {
        invalidate('supabase:auth')
      }
    })

    return () => data.subscription.unsubscribe()
  })
  
</script>

{#if !($page.data.hasSubdomain && $page.url.pathname === '/')}
<header class="fixed top-0 z-40 mx-auto w-full flex-none border-b border-gray-200 bg-white dark:border-gray-600 dark:bg-gray-800">
  <Navbar {session}/>
</header>
{/if}

{#if $navigating}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
    <div class="flex flex-col items-center gap-4">
      <Spinner/>
      <p class="text-gray-600 dark:text-gray-400">Loading...</p>
    </div>
  </div>
{/if}

{@render children()}
