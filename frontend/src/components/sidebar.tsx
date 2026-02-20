"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Calendar,
  Clock,
  Home,
  LogOut,
  MapPin,
  Users,
  CalendarDays,
} from "lucide-react";
import { useAuth } from "@/context/auth-context";
import { cn } from "@/lib/utils";

const studentLinks = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/schedule", label: "Schedule", icon: Calendar },
  { href: "/availability", label: "Availability", icon: Clock },
];

const supervisorLinks = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/schedule", label: "Schedule", icon: Calendar },
  { href: "/availability", label: "Availability", icon: Clock },
  { href: "/locations", label: "Locations", icon: MapPin },
  { href: "/holidays", label: "Holidays", icon: CalendarDays },
  { href: "/admin/users", label: "Users", icon: Users },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const links = user?.role === "supervisor" ? supervisorLinks : studentLinks;

  return (
    <aside className="flex h-full w-64 flex-col border-r bg-card">
      <div className="flex items-center gap-2 border-b p-4">
        <Calendar className="h-6 w-6 text-primary" />
        <span className="text-lg font-semibold">IT Help Desk</span>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent",
              pathname === href ? "bg-accent text-accent-foreground" : "text-muted-foreground"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
      <div className="border-t p-4">
        <div className="mb-2 text-sm text-muted-foreground">
          {user?.first_name} {user?.last_name}
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
