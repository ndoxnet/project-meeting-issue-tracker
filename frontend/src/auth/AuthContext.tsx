// Concept by MrHan (08974747477)
import { createContext } from 'react';
import type { AuthContextValue } from './authTypes';

export const AuthContext = createContext<AuthContextValue | null>(null);
