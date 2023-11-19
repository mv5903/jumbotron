// Jumbotron.ts
import { writable } from 'svelte/store';

export class Jumbotron {
    rows: number = 0;
    columns: number = 0;
    hostname: string = '';
    port: number = 5000;
    isInitialized: boolean = false;
    // Create a Svelte store for Jumbotron's state
    private _state = writable({
        rows: 0,
        columns: 0,
        hostname: '',
        port: 5000,
        isInitialized: false,
    } as Jumbotron);

    private static instance: Jumbotron;
    subscribe = this._state.subscribe;

    public static getInstance(): Jumbotron {
        if (!this.instance) {
            this.instance = new Jumbotron();
        }
        return this.instance;
    }

    async attemptConnection(hostname: string, port: number) {
        try {
            const response = await fetch(`http://${hostname}:${port}/jumbotron`);
            const json = await response.json();
            if (json) {
                this._state.set({
                    hostname,
                    port,
                    rows: json.rows,
                    columns: json.columns,
                    isInitialized: true,
                } as Jumbotron);
            }
            return json !== undefined;
        } catch (e) {
            alert(`Error connecting to Jumbotron: ${e}`);
            return false;
        }
    }

    async disconnect() {
        this._state.set({
            rows: 0,
            columns: 0,
            hostname: '',
            port: 5000,
            isInitialized: false,
        } as Jumbotron);
    }
}

export const jumbotronInstance = Jumbotron.getInstance();