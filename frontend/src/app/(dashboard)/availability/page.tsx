"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { RoleGate } from "@/components/role-gate";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import type { AvailabilitySlot, UserAvailability } from "@/lib/types";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const HOURS = Array.from({ length: 10 }, (_, i) => i + 8); // 8-17

export default function AvailabilityPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Availability</h1>
        <p className="text-muted-foreground">
          {user?.role === "supervisor"
            ? "View and manage student availability"
            : "Set your weekly availability for scheduling"}
        </p>
      </div>

      <RoleGate allowed={["student"]}>
        <AvailabilityGrid />
      </RoleGate>

      <RoleGate allowed={["supervisor"]}>
        <SupervisorAvailabilityView />
      </RoleGate>
    </div>
  );
}

function AvailabilityGrid() {
  const [selected, setSelected] = useState<Record<string, Set<number>>>({});
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api.availability.getMine().then((data) => {
      const slots = data as AvailabilitySlot[];
      const map: Record<string, Set<number>> = {};
      DAYS.forEach((d) => (map[d] = new Set()));
      for (const s of slots) {
        const startH = parseInt(s.start_time);
        const endH = parseInt(s.end_time);
        for (let h = startH; h < endH; h++) {
          map[s.day_of_week]?.add(h);
        }
      }
      setSelected(map);
      setLoaded(true);
    }).catch(() => setLoaded(true));
  }, []);

  const toggle = (day: string, hour: number) => {
    setSelected((prev) => {
      const updated = { ...prev };
      const daySet = new Set(prev[day] || []);
      if (daySet.has(hour)) daySet.delete(hour);
      else daySet.add(hour);
      updated[day] = daySet;
      return updated;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Convert grid to time-range slots
      const slots: { day_of_week: string; start_time: string; end_time: string }[] = [];
      for (const day of DAYS) {
        const hours = Array.from(selected[day] || []).sort((a, b) => a - b);
        if (hours.length === 0) continue;
        let rangeStart = hours[0];
        let prev = hours[0];
        for (let i = 1; i < hours.length; i++) {
          if (hours[i] === prev + 1) {
            prev = hours[i];
          } else {
            slots.push({
              day_of_week: day,
              start_time: `${rangeStart.toString().padStart(2, "0")}:00:00`,
              end_time: `${(prev + 1).toString().padStart(2, "0")}:00:00`,
            });
            rangeStart = hours[i];
            prev = hours[i];
          }
        }
        slots.push({
          day_of_week: day,
          start_time: `${rangeStart.toString().padStart(2, "0")}:00:00`,
          end_time: `${(prev + 1).toString().padStart(2, "0")}:00:00`,
        });
      }
      await api.availability.submitMine({ slots, is_recurring: true });
      toast.success("Availability saved!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  if (!loaded) return <div className="text-muted-foreground">Loading...</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Weekly Availability</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4 text-sm text-muted-foreground">
          Click on time slots to toggle your availability. Green = available.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="w-20 border p-2 text-sm">Time</th>
                {DAYS.map((d) => (
                  <th key={d} className="border p-2 text-sm">{d}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {HOURS.map((h) => (
                <tr key={h}>
                  <td className="border p-2 text-center font-mono text-sm">{h}:00</td>
                  {DAYS.map((day) => {
                    const isSelected = selected[day]?.has(h);
                    return (
                      <td
                        key={day}
                        className={`cursor-pointer border p-2 text-center transition-colors ${
                          isSelected ? "bg-green-500/30 hover:bg-green-500/40" : "hover:bg-accent"
                        }`}
                        onClick={() => toggle(day, h)}
                      >
                        {isSelected ? "✓" : ""}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Availability"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function SupervisorAvailabilityView() {
  const [data, setData] = useState<UserAvailability[]>([]);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const load = useCallback(() => {
    api.availability.getAll().then((d) => setData(d as UserAvailability[])).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleUpload = async () => {
    if (!csvFile) return;
    setUploading(true);
    try {
      await api.availability.uploadCsv(csvFile);
      toast.success("CSV uploaded successfully!");
      setCsvFile(null);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Upload CSV Availability</CardTitle>
        </CardHeader>
        <CardContent className="flex items-end gap-4">
          <div className="space-y-2">
            <Label>CSV File</Label>
            <Input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files?.[0] || null)} />
          </div>
          <Button onClick={handleUpload} disabled={!csvFile || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All Student Availability</CardTitle>
        </CardHeader>
        <CardContent>
          {data.length === 0 ? (
            <p className="text-sm text-muted-foreground">No availability data</p>
          ) : (
            <div className="space-y-4">
              {data.filter((u) => u.slots.length > 0).map((u) => (
                <div key={u.user_id} className="rounded-md border p-3">
                  <h3 className="font-medium">{u.user_name}</h3>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {u.slots.map((s) => (
                      <span key={s.id} className="rounded bg-primary/10 px-2 py-0.5 text-xs">
                        {s.day_of_week} {s.start_time.slice(0, 5)}-{s.end_time.slice(0, 5)}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
}
