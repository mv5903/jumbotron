// src/types/svelte-icons.d.ts
// Made this so Typescript will shut up about importing SVGs
declare module 'svelte-icons/fa/*' {
  const content: any;
  export default content;
}