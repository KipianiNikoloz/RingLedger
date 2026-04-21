import { startTransition, useEffect, useState } from "react";

function readPathname(): string {
  if (typeof window === "undefined") {
    return "/";
  }

  return window.location.pathname || "/";
}

export interface PathnameController {
  pathname: string;
  navigate: (to: string) => void;
}

export function usePathname(): PathnameController {
  const [pathname, setPathname] = useState(readPathname);

  useEffect(() => {
    function handleLocationChange(): void {
      startTransition(() => {
        setPathname(readPathname());
      });
    }

    window.addEventListener("popstate", handleLocationChange);
    return () => {
      window.removeEventListener("popstate", handleLocationChange);
    };
  }, []);

  function navigate(to: string): void {
    if (typeof window === "undefined" || to === pathname) {
      return;
    }

    window.history.pushState({}, "", to);
    window.dispatchEvent(new PopStateEvent("popstate"));
  }

  return { pathname, navigate };
}
