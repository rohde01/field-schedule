<script lang="ts">
    import { Heading, P, Button } from 'flowbite-svelte';
    import { ArrowRightOutline } from 'flowbite-svelte-icons';
</script>

<div class="flex items-center justify-center min-h-screen dark:bg-gray-900 pt-0 -mt-32">
    <div class="container max-w-6xl mx-auto px-8 py-24">
        <div class="text-center">
            <Heading tag="h1" class="mb-10" customSize="text-6xl font-extrabold md:text-7xl lg:text-8xl">Baneplanen.</Heading>
            
            <P class="mb-12 text-2xl lg:text-3xl sm:px-16 xl:px-40 dark:text-gray-400">
                En tidlig prototype udviklet i samarbejde med og for <span class="font-bold bg-gradient-to-r from-[#C8102E] to-blue-800 text-transparent bg-clip-text">Boldklubben af 1893</span>
            </P>
            
            <div class="mt-6">
                <Button size="xl" href="/auth" class="px-10 py-4 text-lg">
                    Get Started
                    <ArrowRightOutline class="w-6 h-6 ms-2" />
                </Button>
            </div>
        </div>
    </div>
</div>