import * as React from "react";

export interface TableColumn {
  key: string;
  label: React.ReactNode;
  /** Right-aligned tabular numerals (.cv-table__num). */
  num?: boolean;
  /** The highlighted gold offer column (.cv-table__feature). */
  feature?: boolean;
}

/** React wrapper over the CSS-only .cv-table (comparison/pricing table).
 *  Declare columns + row objects keyed by column key, or pass children
 *  (<thead>/<tbody>) for full manual control. */
export interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  columns?: TableColumn[];
  rows?: Array<Record<string, React.ReactNode> & { key?: React.Key }>;
  striped?: boolean;
}
export declare function Table(props: TableProps): JSX.Element;
export default Table;
