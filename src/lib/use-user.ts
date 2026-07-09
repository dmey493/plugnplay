"use client";

import { useCallback, useEffect, useState } from "react";
import { getUser, setUser as setUserStorage, clearUser, type User } from "./classes";

/**
 * Fake-login hook for the no-auth draft.
 *
 * `user` is `undefined` until we've hydrated from localStorage (so the
 * UI knows the difference between "still loading" and "definitely not
 * logged in"). `null` once we've read storage and confirmed nothing
 * is there yet.
 *
 * Updates from one tab broadcast to others via the browser's native
 * `storage` event so a logout in tab A reflects in tab B.
 *
 * When real auth lands, the only caller-facing change should be that
 * `user` comes from the auth session instead of localStorage — the
 * shape of `User` stays the same.
 */
export function useUser() {
  const [user, setUserState] = useState<User | null | undefined>(undefined);

  useEffect(() => {
    setUserState(getUser());
    const onStorage = (e: StorageEvent) => {
      if (e.key === "pnp:user") {
        setUserState(getUser());
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const login = useCallback((name: string) => {
    const next = setUserStorage(name);
    setUserState(next);
    return next;
  }, []);

  const logout = useCallback(() => {
    clearUser();
    setUserState(null);
  }, []);

  return { user, login, logout };
}
