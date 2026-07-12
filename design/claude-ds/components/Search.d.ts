import * as React from "react";

/** React wrapper over the CSS-only .cv-search pill (icon + input, gold
 *  focus-within ring). Controlled via value/onChange (string value). */
export interface SearchProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange"> {
  value?: string;
  onChange?: (value: string, e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  /** cv-icons id for the leading glyph (default "search"); null omits it. */
  icon?: string | null;
  /** Trailing slot (shortcut hint, clear button…). */
  trailing?: React.ReactNode;
}
export declare function Search(props: SearchProps): JSX.Element;
export default Search;
