"use client";

import { useEffect, useState } from "react";
import { logout } from "../lib/api";
import { isLoggedIn } from "../lib/auth";

export function AuthStatus() {
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    setLoggedIn(isLoggedIn());
  }, []);

  if (!loggedIn) return null;

  return (
    <button type="button" className="link-button" onClick={logout}>
      Sign out
    </button>
  );
}
