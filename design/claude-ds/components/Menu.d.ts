import * as React from "react";
import type { PlaceOpts } from "./Popover";

export interface MenuItem {
  /** cv-icons id (must resolve in assets/icons/cv-icons.js). */
  icon?: string;
  label: React.ReactNode;
  danger?: boolean;
  disabled?: boolean;
  value?: string | number;
  onSelect?: () => void;
}
export interface MenuSeparator {
  separator: true;
}

export interface MenuProps {
  /** The trigger element — cloned with the anchor ref + open/close toggle. */
  trigger: React.ReactElement;
  items: Array<MenuItem | MenuSeparator>;
  placement?: PlaceOpts["placement"];
  onOpenChange?: (open: boolean) => void;
  className?: string;
}
export declare function Menu(props: MenuProps): JSX.Element;
export default Menu;
