export type AuthUser = {
  id: string;
  email?: string;
  profile?: {
    name?: string;
    avatar_url?: string | null;
  };
};
