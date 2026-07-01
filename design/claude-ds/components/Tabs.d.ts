import * as React from "react";
export interface TabItem { id?: string; label: React.ReactNode; }
/** Dashboard tab bar — active tab gets the gold underline. Controlled via value/onChange. */
export interface TabsProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange"> {
  items: Array<TabItem | string>;
  value?: string;
  onChange?: (id: string, e: React.MouseEvent) => void;
}
export declare function Tabs(props: TabsProps): JSX.Element;
export default Tabs;
