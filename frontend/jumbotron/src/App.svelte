<script lang="ts">
  import { onMount } from "svelte";
  import { jumbotronInstance, Jumbotron } from "./classes/Jumbotron";
  import JumbotronDashboard from "./components/JumbotronDashboard.svelte";
  import { connections } from './stores/connectionsStore';
  import type { Connection } from "./types/Connection";
  import FaTrash from 'svelte-icons/fa/FaTrash.svelte';

  let jumbotronState : Jumbotron;

  jumbotronInstance.subscribe((state) => {
    jumbotronState = state;
  });

  let hostname = "";
  let port = 5000;

  async function attemptCurrentConnection() {
    if (await jumbotronInstance.attemptConnection(hostname, port)) {
      connections.addConnection({ hostname, port });
    }
  }

  async function attemptSelectiveConnection(connection: Connection) {
    await jumbotronInstance.attemptConnection(connection.hostname, connection.port);
  }
</script>

<svelte:head>
  <title>Jumbotron</title>
  <link rel="icon" href="/jumbotron.svg" />
</svelte:head>

<main class="w-full">
  {#if !jumbotronState}
    <p>Loading...</p>
  {/if}
  {#if !jumbotronState.isInitialized}
    <div class="flex flex-col place-items-center gap-4">
      <h1>Jumbotron</h1>
      <h3>Enter the details of your Jumbotron server to get started:</h3>
      <div class="flex gap-2 place-items-center">
        <p>http://</p>
        <input type="text" bind:value={hostname} on:keydown={e => e.key == 'Enter' && attemptCurrentConnection()} class="input input-bordered w-full max-w-xs" placeholder="Hostname" />
        <p>:</p>
        <input type="number" bind:value={port} on:keydown={e => e.key == 'Enter' && attemptCurrentConnection()} class="input input-bordered w-full max-w-xs" placeholder="Port" />
        <p>/jumbotron</p>
      </div>
      <div class="flex flex-col gap-3">
        <button on:click={attemptCurrentConnection}>Connect with Desktop View</button>
        <button on:click={attemptCurrentConnection}>Connect with Tablet View</button>
      </div>
      <p class="text-gray-300 text-opacity-25">
        You can also press <kbd class="kbd kbd-sm">Enter</kbd>!
      </p>
      <div class="divider">OR</div>
      <h2 class="text-2xl mb-2">Recent Connections</h2>
      <div class="flex gap-3">
        {#if $connections.length > 0}
          {#each $connections as connection}
          <button class="flex justify-content-center place-items-center gap-3" on:click={() => attemptSelectiveConnection({ hostname: connection.hostname, port: connection.port})}>
            <div class="flex justify-content-center items-center gap-3">
              <p><span>{connection.hostname}</span>:<span>{connection.port}</span></p>
              <button class="w-[55px] bg-red-600" on:click={() => connections.removeConnection({ hostname: connection.hostname, port: connection.port })}><FaTrash/></button>
            </div>
          </button>
          {/each}
        {:else}
        <p class="text-gray-400">No recent connections found.</p>
        {/if}
      </div>
    </div>
  {:else}
    <JumbotronDashboard />
  {/if}
</main>

<style>
</style>
