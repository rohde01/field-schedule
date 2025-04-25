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

  export interface InputField {
    label: string;
    type: InputType;
    placeholder: string;
  }