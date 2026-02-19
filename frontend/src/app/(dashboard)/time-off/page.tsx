"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { RoleGate } from "@/components/role-gate";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import type { TimeOffRequest } from "@/lib/types";

export default function TimeOffPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Time Off</h1>
        <p className="text-muted-foreground">Request time off or manage requests</p>
      </div>

      <RoleGate allowed={["student"]}>
        <StudentTimeOff />
      </RoleGate>

      <RoleGate allowed={["supervisor"]}>
        <SupervisorTimeOff />
      </RoleGate>
    </div>
  );
}

function StudentTimeOff() {
  const [requests, setRequests] = useState<TimeOffRequest[]>([]);
  const [requestType, setRequestType] = useState("time_off");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(() => {
    api.timeOff.getMine().then((d) => setRequests(d as TimeOffRequest[])).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.timeOff.create({
        request_type: requestType,
        start_date: startDate,
        end_date: endDate,
        reason: reason || null,
      });
      toast.success("Request submitted!");
      setStartDate("");
      setEndDate("");
      setReason("");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to submit");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>New Request</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Type</Label>
              <Select value={requestType} onValueChange={setRequestType}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="time_off">Time Off</SelectItem>
                  <SelectItem value="sick_day">Sick Day</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Reason (optional)</Label>
              <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Optional reason" />
            </div>
            <div className="space-y-2">
              <Label>Start Date</Label>
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label>End Date</Label>
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
            </div>
            <div className="sm:col-span-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Submitting..." : "Submit Request"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>My Requests</CardTitle>
        </CardHeader>
        <CardContent>
          <RequestsTable requests={requests} />
        </CardContent>
      </Card>
    </>
  );
}

function SupervisorTimeOff() {
  const [pending, setPending] = useState<TimeOffRequest[]>([]);
  const [all, setAll] = useState<TimeOffRequest[]>([]);

  const load = useCallback(() => {
    api.timeOff.getPending().then((d) => setPending(d as TimeOffRequest[])).catch(() => {});
    api.timeOff.getAll().then((d) => setAll(d as TimeOffRequest[])).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleReview = async (id: number, status: string) => {
    try {
      await api.timeOff.review(id, { status });
      toast.success(`Request ${status}`);
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Review failed");
    }
  };

  return (
    <>
      {pending.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pending Requests ({pending.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Student</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Dates</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pending.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell>{r.user_name}</TableCell>
                    <TableCell>{r.request_type}</TableCell>
                    <TableCell>{r.start_date} — {r.end_date}</TableCell>
                    <TableCell>{r.reason || "—"}</TableCell>
                    <TableCell className="flex gap-2">
                      <Button size="sm" onClick={() => handleReview(r.id, "approved")}>Approve</Button>
                      <Button size="sm" variant="destructive" onClick={() => handleReview(r.id, "denied")}>Deny</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>All Requests</CardTitle>
        </CardHeader>
        <CardContent>
          <RequestsTable requests={all} showUser />
        </CardContent>
      </Card>
    </>
  );
}

function RequestsTable({ requests, showUser }: { requests: TimeOffRequest[]; showUser?: boolean }) {
  if (requests.length === 0) return <p className="text-sm text-muted-foreground">No requests</p>;

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {showUser && <TableHead>Student</TableHead>}
          <TableHead>Type</TableHead>
          <TableHead>Dates</TableHead>
          <TableHead>Reason</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {requests.map((r) => (
          <TableRow key={r.id}>
            {showUser && <TableCell>{r.user_name}</TableCell>}
            <TableCell>{r.request_type}</TableCell>
            <TableCell>{r.start_date} — {r.end_date}</TableCell>
            <TableCell>{r.reason || "—"}</TableCell>
            <TableCell>
              <Badge variant={r.status === "approved" ? "default" : r.status === "denied" ? "destructive" : "secondary"}>
                {r.status}
              </Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
