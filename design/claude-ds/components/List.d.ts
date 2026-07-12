import * as React from "react";

export interface ListRowProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onSelect"> {
  /** Leading glyph/avatar slot. */
  leading?: React.ReactNode;
  /** Primary text — length-budgeted to --len-title, truncates past it. */
  primary?: React.ReactNode;
  /** Secondary text — length-budgeted to --len-desc, truncates past it. */
  secondary?: React.ReactNode;
  /** Trailing meta/action slot. */
  trailing?: React.ReactNode;
  /** Selection state (renders the shared .interactive selected wash). */
  selected?: boolean;
  onSelect?: (e: React.SyntheticEvent) => void;
}
export declare function ListRow(props: ListRowProps): JSX.Element;

export interface ListProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Row data — rendered as <ListRow {...row}/> per entry. Omit and pass
   *  <ListRow/> children directly for full manual control. */
  rows?: Array<ListRowProps & { key?: React.Key }>;
  /** Hairline divider between rows. Default true. */
  divided?: boolean;
}
export declare function List(props: ListProps): JSX.Element;
export default List;
