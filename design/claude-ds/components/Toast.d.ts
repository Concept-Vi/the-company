import * as React from "react";

export interface ToastAction {
  label: React.ReactNode;
  onClick?: () => void;
}

export interface ToastOptions {
  tone?: "gold" | "success" | "warning" | "error" | "comm";
  title?: React.ReactNode;
  message?: React.ReactNode;
  action?: ToastAction;
  /** ms before auto-dismiss; 0 disables auto-dismiss. Default 4200. */
  duration?: number;
}

/** The window-level queue — the ONE home for toasts. Call from anywhere;
 *  mount ONE <ToastHost/> to render it. */
export interface CvToastGlobal {
  show(opts: ToastOptions): number;
  dismiss(id: number): void;
  subscribe(fn: (items: Array<ToastOptions & { id: number; exiting: boolean }>) => void): () => void;
}
declare global {
  interface Window { CV_TOAST: CvToastGlobal; }
}

export interface ToastHostProps {
  position?: "top-right" | "top-center" | "top-left" | "bottom-right" | "bottom-center" | "bottom-left";
  className?: string;
}
export declare function ToastHost(props: ToastHostProps): JSX.Element | null;
export default ToastHost;
