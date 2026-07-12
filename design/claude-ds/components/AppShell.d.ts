import * as React from "react";

export interface AppShellNavItem {
  id: string;
  label: React.ReactNode;
  /** cv-icons id (must resolve in assets/icons/cv-icons.js). */
  icon?: string;
}

export interface AppShellProps extends React.HTMLAttributes<HTMLDivElement> {
  nav?: AppShellNavItem[];
  activeId?: string;
  onNavigate?: (id: string) => void;
  /** Full custom header (overrides `title`). Pass null to omit entirely. */
  header?: React.ReactNode;
  /** Convenience: renders a plain .cv-appbar with this title when `header` is omitted. */
  title?: React.ReactNode;
}
export declare function AppShell(props: AppShellProps): JSX.Element;
export default AppShell;
