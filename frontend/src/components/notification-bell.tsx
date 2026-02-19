"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

export function NotificationBell() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    api.notifications.unreadCount().then((d) => setCount(d.count)).catch(() => {});
    const interval = setInterval(() => {
      api.notifications.unreadCount().then((d) => setCount(d.count)).catch(() => {});
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative">
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <Badge
          variant="destructive"
          className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full p-0 text-xs"
        >
          {count}
        </Badge>
      )}
    </div>
  );
}
