"use client";

import { useAuth } from "@/context/auth-context";
import type { UserRole } from "@/lib/types";

interface RoleGateProps {
  allowed: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGate({ allowed, children, fallback }: RoleGateProps) {
  const { user } = useAuth();
  if (!user || !allowed.includes(user.role)) {
    return fallback ? <>{fallback}</> : null;
  }
  return <>{children}</>;
}
