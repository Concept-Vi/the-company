import * as React from "react";
/** Modal dialog — warm-dim backdrop + a raised panel. Controlled via open;
 *  closes on backdrop click, Escape, or the close button. */
export interface ModalProps extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean;
  onClose?: () => void;
  title?: React.ReactNode;
  footer?: React.ReactNode;
}
export declare function Modal(props: ModalProps): JSX.Element | null;
export default Modal;
