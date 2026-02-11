import { create } from 'zustand';

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  permissions: string[];
  setTokens: (accessToken: string, refreshToken: string) => void;
  setPermissions: (permissions: string[]) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  permissions: [],
  setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
  setPermissions: (permissions) => set({ permissions }),
  clear: () => set({ accessToken: null, refreshToken: null, permissions: [] }),
}));
