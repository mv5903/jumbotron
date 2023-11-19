<script lang="ts">
    import Navbar from "./Navbar.svelte";

    import { jumbotronInstance, Jumbotron } from '../classes/Jumbotron';

    let jumbotronState: Jumbotron;

    jumbotronInstance.subscribe(state => {
        jumbotronState = state;
    });
</script>

<div>
    <Navbar />
</div>

<style>

</style>