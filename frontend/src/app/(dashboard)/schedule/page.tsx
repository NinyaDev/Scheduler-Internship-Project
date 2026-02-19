"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { RoleGate } from "@/components/role-gate";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import type { Schedule, GenerateScheduleResponse, ScheduleWarning } from "@/lib/types";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

export default function SchedulePage() {
  const { user } = useAuth();
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [weekStart, setWeekStart] = useState("");
  const [warnings, setWarnings] = useState<ScheduleWarning[]>([]);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      if (user?.role === "supervisor") {
        const data = (await api.schedules.list()) as Schedule[];
        setSchedules(data);
        if (data.length > 0) setSchedule(data[0]);
      } else {
        const data = (await api.schedules.getCurrent()) as Schedule | null;
        setSchedule(data);
      }
    } catch {
      // no schedule yet
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!weekStart) {
      toast.error("Please select a week start date");
      return;
    }
    setGenerating(true);
    try {
      const resp = (await api.schedules.generate({ week_start_date: weekStart })) as GenerateScheduleResponse;
      setSchedule(resp.schedule);
      setWarnings(resp.warnings);
      toast.success("Schedule generated!");
      loadData();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const handlePublish = async (id: number) => {
    try {
      const updated = (await api.schedules.publish(id)) as Schedule;
      setSchedule(updated);
      toast.success("Schedule published!");
      loadData();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Publish failed");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.schedules.delete(id);
      toast.success("Schedule deleted");
      setSchedule(null);
      loadData();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed");
    }
  };

  if (loading) return <div className="text-muted-foreground">Loading schedule...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Schedule</h1>
          <p className="text-muted-foreground">
            {user?.role === "supervisor" ? "Generate and manage weekly schedules" : "View your weekly schedule"}
          </p>
        </div>
      </div>

      <RoleGate allowed={["supervisor"]}>
        <Card>
          <CardHeader>
            <CardTitle>Generate New Schedule</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end gap-4">
            <div className="space-y-2">
              <Label>Week Start Date (Monday)</Label>
              <Input type="date" value={weekStart} onChange={(e) => setWeekStart(e.target.value)} />
            </div>
            <Button onClick={handleGenerate} disabled={generating}>
              {generating ? "Generating..." : "Generate Schedule"}
            </Button>
          </CardContent>
        </Card>

        {warnings.length > 0 && (
          <Card className="border-yellow-500">
            <CardHeader>
              <CardTitle className="text-yellow-600">Warnings</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1 text-sm">
                {warnings.map((w, i) => (
                  <li key={i} className="text-yellow-700">
                    {w.day} - {w.location}: {w.message}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {schedules.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>All Schedules</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Week</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Shifts</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {schedules.map((s) => (
                    <TableRow key={s.id} className="cursor-pointer" onClick={() => setSchedule(s)}>
                      <TableCell>{s.week_start_date}</TableCell>
                      <TableCell>
                        <Badge variant={s.status === "published" ? "default" : s.status === "draft" ? "secondary" : "outline"}>
                          {s.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{s.shifts.length}</TableCell>
                      <TableCell className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                        {s.status === "draft" && (
                          <>
                            <Button size="sm" onClick={() => handlePublish(s.id)}>Publish</Button>
                            <Button size="sm" variant="destructive" onClick={() => handleDelete(s.id)}>Delete</Button>
                          </>
                        )}
                        {s.status === "published" && (
                          <Button size="sm" variant="outline" onClick={() => api.schedules.archive(s.id).then(() => loadData())}>Archive</Button>
                        )}
                        <a href={api.export.icsUrl(s.id)} className="inline-flex items-center">
                          <Button size="sm" variant="outline">ICS</Button>
                        </a>
                        <a href={api.export.csvUrl(s.id)} className="inline-flex items-center">
                          <Button size="sm" variant="outline">CSV</Button>
                        </a>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </RoleGate>

      {schedule && (
        <Card>
          <CardHeader>
            <CardTitle>
              Week of {schedule.week_start_date}
              <Badge className="ml-2" variant={schedule.status === "published" ? "default" : "secondary"}>
                {schedule.status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScheduleGrid schedule={schedule} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function ScheduleGrid({ schedule }: { schedule: Schedule }) {
  const hours = Array.from({ length: 10 }, (_, i) => i + 8);

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-20">Time</TableHead>
            {DAYS.map((d) => (
              <TableHead key={d}>{d}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {hours.map((h) => (
            <TableRow key={h}>
              <TableCell className="font-mono text-sm">{h}:00</TableCell>
              {DAYS.map((day) => {
                const shiftsAtSlot = schedule.shifts.filter(
                  (s) =>
                    s.day_of_week === day &&
                    parseInt(s.start_time) <= h &&
                    parseInt(s.end_time) > h
                );
                return (
                  <TableCell key={day} className="text-xs">
                    {shiftsAtSlot.map((s) => (
                      <div key={s.id} className="mb-1 rounded bg-primary/10 px-1 py-0.5">
                        <span className="font-medium">{s.user_name}</span>
                        <br />
                        <span className="text-muted-foreground">{s.location_name}</span>
                      </div>
                    ))}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
