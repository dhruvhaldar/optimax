import { useEffect, useRef } from "react";

/**
 * Custom hook to manage focus when asynchronous results load.
 * Returns a ref to attach to the target element (usually the Results heading).
 *
 * @param {boolean} isLoading - Current loading state
 * @param {any} result - The result object, null if no result
 */
export const useResultFocus = (isLoading, result) => {
  const resultRef = useRef(null);

  // Keep track of previous loading state to detect transition from true -> false
  const prevLoadingRef = useRef(isLoading);

  useEffect(() => {
    // If we just finished loading and we have a result
    if (prevLoadingRef.current && !isLoading && result && resultRef.current) {
      // Small timeout to ensure DOM has updated with the new result
      setTimeout(() => {
        if (resultRef.current) {
          resultRef.current.focus();
        }
      }, 50);
    }

    // Update previous loading state
    prevLoadingRef.current = isLoading;
  }, [isLoading, result]);

  return resultRef;
};
