import * as React from "react";
/** On/off switch. The track turns gold when checked (gold = active voice). */
export interface SwitchProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onChange"> {
  checked?: boolean;
  onChange?: (next: boolean, e: React.MouseEvent) => void;
}
export declare function Switch(props: SwitchProps): JSX.Element;
export default Switch;
