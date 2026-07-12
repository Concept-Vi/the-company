import * as React from "react";
export interface SelectOption { value: string; label?: React.ReactNode; disabled?: boolean; }
/** Select — an Input-like trigger opening a listbox popover (positioned by the
 *  shared Popover engine). Controlled via value/onChange. */
export interface SelectProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange"> {
  options: Array<SelectOption | string>;
  value?: string;
  onChange?: (value: string, e: React.MouseEvent) => void;
  placeholder?: string;
  disabled?: boolean;
}
export declare function Select(props: SelectProps): JSX.Element;
export default Select;
