<script lang="ts">
    import { onMount } from 'svelte';
    import { jumbotronInstance, Jumbotron } from '../classes/Jumbotron';
    import FaTrash from 'svelte-icons/fa/FaTrash.svelte';
    import FaImage from 'svelte-icons/fa/FaImage.svelte';
    import FaVideo from 'svelte-icons/fa/FaVideo.svelte';

    let jumbotronState: Jumbotron;

    jumbotronInstance.subscribe(state => {
        jumbotronState = state;
    });

    export let savedMatrixes: any[] = [];
    let currentName: string = ""
    let currentPreviewURL: string = "";

    async function showPreviewHandler(e: MouseEvent, name: string) {
        console.log(e.currentTarget);
        currentName = name;
        currentPreviewURL = await jumbotronInstance.getSavedItemPreview(name);
    }

    async function activateThisMatrix() {
        await jumbotronInstance.activateSavedItem(currentName);
        currentPreviewURL = '';
    }

    onMount(async () => {
        setInterval(async () => {
            savedMatrixes = await jumbotronInstance.getSavedItems();
        }, 1000);
    });
</script>


<div class="modal-box">
    {#if !currentPreviewURL}
    <h3 class="font-bold text-lg">Previous Items</h3>
    <p class="py-4">Choose an item to activate:</p>
    <div class="grid grid-cols-2 gap-4 text-center">
        {#if savedMatrixes.length == 0}
            <p class="py-4">No previous items found. Save something first!</p>
        {/if}
        {#if savedMatrixes.length > 0}
            {#each savedMatrixes as matrix}
                <button class="flex place-items-center justify-between bg-base-300 btn-full" on:click={e => showPreviewHandler(e, matrix.filename)}>
                    {#if matrix.type == 'image'}
                    <div class="h-[20px]">
                        <FaImage />
                    </div>
                    {:else if matrix.type == 'video'}
                    <div class="h-[20px]">
                        <FaVideo />
                    </div>
                    {/if}
                    <p>{matrix.filename.split('.')[0]}</p>
                    <button id="del" class="h-[40px] bg-red-600 w-[40px] flex justify-center"  on:click={async (e) => {
                        e.stopPropagation(); // This will prevent event bubbling
                        if (!confirm('Are you sure you want to delete this?')) return;
                        await jumbotronInstance.deleteSavedItem(matrix.filename);
                    }}>
                        X
                    </button>
                </button>
            {/each}
        {/if}
    </div>
    <div class="modal-action">
        <form method="dialog">
            <button class="btn">Close</button>
        </form>
    </div>
    {:else}
    <div class="flex flex-col">
        <p>Activate this?</p>
        <img class="m-8" src={currentPreviewURL} alt="Preview"/>
        <div class="modal-action">
            <form method="dialog">
                <button class="btn" on:click={activateThisMatrix}>Yes</button>
                <button class="btn btn-ghost" on:click={() => currentPreviewURL = ''}>No</button>
            </form>
        </div>
    </div>
    {/if}
</div>

<style>
</style>