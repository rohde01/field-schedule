export interface TeamModalProps {
    open: boolean;
    data: Record<string, string>;
  }

  export interface DeleteModalProps {
    open?: boolean;
    title?: string;
    yes?: string;
    no?: string;
  }