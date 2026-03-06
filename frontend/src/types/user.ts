/**
 * User types matching backend UserRead schema
 */

export enum UserRole {
  PATIENT = "patient",
  PROVIDER = "provider",
  ADMIN = "admin",
  RECEPTIONIST = "receptionist",
}

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string; // fastapi-users uses 'username' field for email
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  role: UserRole;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}
