"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RoleGate } from "@/components/role-gate";
import { Calendar, Clock, Users, AlertTriangle } from "lucide-react";
import type { Schedule, Shift, TimeOffRequest, Notification as NotificationType } from "@/lib/types";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Welcome, {user?.first_name}!</h1>
        <p className="text-muted-foreground">
          {user?.role === "supervisor"
            ? "Manage schedules, review requests, and oversee the help desk."
            : "View your schedule, submit availability, and manage your shifts."}
        </p>
      </div>

      <RoleGate allowed={["student"]}>
        <StudentDashboard />
      </RoleGate>
      <RoleGate allowed={["supervisor"]}>
        <SupervisorDashboard />
      </RoleGate>
    </div>
  );
}

function StudentDashboard() {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [notifications, setNotifications] = useState<NotificationType[]>([]);

  useEffect(() => {
    api.shifts.getMine().then((d) => setShifts(d as Shift[])).catch(() => {});
    api.notifications.list().then((d) => setNotifications(d as NotificationType[])).catch(() => {});
  }, []);

  const upcoming = shifts.filter(
    (s) => new Date(s.actual_date) >= new Date(new Date().toDateString())
  ).slice(0, 5);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Upcoming Shifts</CardTitle>
          <Calendar className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{upcoming.length}</div>
          <p className="text-xs text-muted-foreground">shifts this week</p>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Next Shifts</CardTitle>
        </CardHeader>
        <CardContent>
          {upcoming.length === 0 ? (
            <p className="text-sm text-muted-foreground">No upcoming shifts</p>
          ) : (
            <div className="space-y-2">
              {upcoming.map((s) => (
                <div key={s.id} className="flex items-center justify-between rounded-md border p-2 text-sm">
                  <span>{s.day_of_week}, {s.actual_date}</span>
                  <span>{s.start_time.slice(0, 5)} - {s.end_time.slice(0, 5)}</span>
                  <Badge variant="outline">{s.location_name}</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="md:col-span-3">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Recent Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          {notifications.length === 0 ? (
            <p className="text-sm text-muted-foreground">No notifications</p>
          ) : (
            <div className="space-y-2">
              {notifications.slice(0, 5).map((n) => (
                <div key={n.id} className={`flex items-start gap-2 rounded-md border p-2 text-sm ${!n.is_read ? "bg-accent/50" : ""}`}>
                  <div>
                    <p className="font-medium">{n.title}</p>
                    <p className="text-muted-foreground">{n.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function SupervisorDashboard() {
  const [pendingTimeOff, setPendingTimeOff] = useState<TimeOffRequest[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);

  useEffect(() => {
    api.timeOff.getPending().then((d) => setPendingTimeOff(d as TimeOffRequest[])).catch(() => {});
    api.schedules.list().then((d) => setSchedules(d as Schedule[])).catch(() => {});
  }, []);

  const published = schedules.filter((s) => s.status === "published");
  const drafts = schedules.filter((s) => s.status === "draft");

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Published Schedules</CardTitle>
          <Calendar className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{published.length}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Draft Schedules</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{drafts.length}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Pending Time Off</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{pendingTimeOff.length}</div>
          <p className="text-xs text-muted-foreground">requests awaiting review</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Total Schedules</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{schedules.length}</div>
        </CardContent>
      </Card>
    </div>
  );
}
