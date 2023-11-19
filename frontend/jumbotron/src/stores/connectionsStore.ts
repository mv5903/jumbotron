// connectionsStore.ts
import { writable } from 'svelte/store';
import type { Connection } from '../types/Connection';

function createConnectionsStore() {
    const localStorageKey = 'connections';
    const initialValue: Connection[] = JSON.parse(localStorage.getItem(localStorageKey) || '[]');

    const { subscribe, set, update } = writable(initialValue);

    subscribe((currentValue) => {
        localStorage.setItem(localStorageKey, JSON.stringify(currentValue));
    });

    function addConnection(newConnection: Connection) {
        update(connections => {
            const exists = connections.some(conn => 
                conn.hostname === newConnection.hostname && conn.port === newConnection.port
            );
            if (!exists) {
                return [...connections, newConnection];
            }
            return connections;
        });
    }

    function removeConnection(connection: Connection) {
        update(connections => {
            return connections.filter(conn => 
                conn.hostname !== connection.hostname || conn.port !== connection.port
            );
        });
    }

    return {
        subscribe,
        addConnection,
        removeConnection,
    };
}

export const connections = createConnectionsStore();
