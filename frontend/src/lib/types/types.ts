import type { Snippet } from 'svelte';

export interface TeamModalProps {
    open: boolean;
    data: Record<string, string>;
  }

  export interface DeleteModalProps {
    open?: boolean;
    title?: string;
    yes?: string;
    no?: string;
    actionName?: string;
  }

  export interface FacilityDrawerProps {
    hidden?: boolean;
    title?: string;
  }

  export interface PlaygroundProps {
    breadcrumb?: Snippet;
    title?: string;
  }