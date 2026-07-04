"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { AuthUser } from "@/types/auth";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/services/authToken";
import { insforge } from "@/services/insforge";

type AuthSessionContextValue = {
  user: AuthUser | null;
  accessToken: string | null;
  isLoading: boolean;
  authMessage: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name?: string) => Promise<void>;
  verifyEmail: (email: string, otp: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthSessionContext = createContext<AuthSessionContextValue | null>(null);

type AuthSessionProviderProps = {
  children: ReactNode;
};

export function AuthSessionProvider({ children }: AuthSessionProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authMessage, setAuthMessage] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadCurrentUser() {
      setIsLoading(true);
      const storedToken = getAccessToken();
      setAccessTokenState(storedToken);

      const { data } = await insforge.auth.getCurrentUser();
      if (!isMounted) {
        return;
      }

      setUser((data?.user as AuthUser | null) ?? null);
      setIsLoading(false);
    }

    loadCurrentUser();

    return () => {
      isMounted = false;
    };
  }, []);

  const persistSession = useCallback((token: string, nextUser: AuthUser) => {
    setAccessToken(token);
    setAccessTokenState(token);
    setUser(nextUser);
  }, []);

  const signIn = useCallback(
    async (email: string, password: string) => {
      setAuthMessage(null);
      const { data, error } = await insforge.auth.signInWithPassword({
        email,
        password,
      });

      if (error || !data?.accessToken || !data.user) {
        throw new Error(error?.message ?? "Unable to sign in");
      }

      persistSession(data.accessToken, data.user as AuthUser);
    },
    [persistSession],
  );

  const signUp = useCallback(
    async (email: string, password: string, name?: string) => {
      setAuthMessage(null);
      const { data, error } = await insforge.auth.signUp({
        email,
        password,
        name,
      });

      if (error) {
        throw new Error(error.message);
      }

      if (data?.requireEmailVerification) {
        setAuthMessage("Check your email for the verification code, then enter it below.");
        return;
      }

      if (data?.accessToken && data.user) {
        persistSession(data.accessToken, data.user as AuthUser);
      }
    },
    [persistSession],
  );

  const verifyEmail = useCallback(
    async (email: string, otp: string) => {
      setAuthMessage(null);
      const { data, error } = await insforge.auth.verifyEmail({ email, otp });

      if (error || !data?.accessToken || !data.user) {
        throw new Error(error?.message ?? "Unable to verify email");
      }

      persistSession(data.accessToken, data.user as AuthUser);
    },
    [persistSession],
  );

  const signOut = useCallback(async () => {
    await insforge.auth.signOut();
    clearAccessToken();
    setAccessTokenState(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      accessToken,
      isLoading,
      authMessage,
      signIn,
      signUp,
      verifyEmail,
      signOut,
    }),
    [accessToken, authMessage, isLoading, signIn, signOut, signUp, user, verifyEmail],
  );

  return (
    <AuthSessionContext.Provider value={value}>
      {children}
    </AuthSessionContext.Provider>
  );
}

export function useAuthSession() {
  const context = useContext(AuthSessionContext);
  if (!context) {
    throw new Error("useAuthSession must be used inside AuthSessionProvider");
  }

  return context;
}
