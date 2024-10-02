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
</script>


<div class="modal-box">
{#if !currentPreviewURL}
    <h3 class="font-bold text-lg">Previous Items</h3>
{#if savedMatrixes.length == 0}
    <p class="py-4">No previous items found. Save something first!</p>
    {:else}
        {#if savedMatrixes.length > 0}
            <p class="py-4">Choose an item to activate:</p>
            <div class="flex flex-col gap-3 max-h-[50vh] overflow-y-auto">
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
                        <p class="mx-2">{matrix.filename.split('.')[0]}</p>
                        <button id="del" class="btn bg-red-600 hover:bg-red-800 flex justify-center text-white"  on:click={async (e) => {
                            e.stopPropagation(); // This will prevent event bubbling
                            if (!confirm('Are you sure you want to delete this?')) return;
                            await jumbotronInstance.deleteSavedItem(matrix.filename);
                            savedMatrixes = await jumbotronInstance.getSavedItems();
                        }}>
                            <FaTrash />
                        </button>
                    </button>
                {/each}
            </div>
        {/if}
    {/if}
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