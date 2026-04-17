import { useState, useEffect } from "react";

export const useOsShortcut = () => {
  const [isMac, setIsMac] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const ua = window.navigator?.userAgent || "";
      const platform = window.navigator?.platform || "";
      setIsMac(
        /Mac|iPod|iPhone|iPad/i.test(ua) ||
          /Mac|iPod|iPhone|iPad/i.test(platform),
      );
    }
  }, []);

  return {
    isMac,
    shortcutSymbol: isMac ? "⌘↵" : "Ctrl+↵",
    shortcutText: isMac ? "Cmd+Enter" : "Ctrl+Enter",
  };
};
