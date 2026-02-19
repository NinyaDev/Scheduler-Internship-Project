"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/context/auth-context";
import { api } from "@/lib/api";
import { RoleGate } from "@/components/role-gate";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import type { ShiftSwap } from "@/lib/types";

export default function ShiftSwapPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Shift Swaps</h1>
        <p className="text-muted-foreground">Propose, respond to, and manage shift swaps</p>
      </div>

      <RoleGate allowed={["student"]}>
        <StudentSwaps />
      </RoleGate>

      <RoleGate allowed={["supervisor"]}>
        <SupervisorSwaps />
      </RoleGate>
    </div>
  );
}

function StudentSwaps() {
  const { user } = useAuth();
  const [swaps, setSwaps] = useState<ShiftSwap[]>([]);

  const load = useCallback(() => {
    api.shiftSwaps.getMine().then((d) => setSwaps(d as ShiftSwap[])).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleRespond = async (id: number, accept: boolean) => {
    try {
      await api.shiftSwaps.respond(id, { accept });
      toast.success(accept ? "Swap accepted!" : "Swap declined");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>My Shift Swaps</CardTitle>
      </CardHeader>
      <CardContent>
        {swaps.length === 0 ? (
          <p className="text-sm text-muted-foreground">No shift swaps</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>From</TableHead>
                <TableHead>To</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {swaps.map((s) => (
                <TableRow key={s.id}>
                  <TableCell>{s.requester_name}</TableCell>
                  <TableCell>{s.target_name}</TableCell>
                  <TableCell>
                    <Badge variant={
                      s.status === "approved" ? "default" :
                      s.status === "denied" ? "destructive" : "secondary"
                    }>
                      {s.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {s.status === "proposed" && s.target_id === user?.id && (
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => handleRespond(s.id, true)}>Accept</Button>
                        <Button size="sm" variant="destructive" onClick={() => handleRespond(s.id, false)}>Decline</Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function SupervisorSwaps() {
  const [pending, setPending] = useState<ShiftSwap[]>([]);

  const load = useCallback(() => {
    api.shiftSwaps.getPending().then((d) => setPending(d as ShiftSwap[])).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleReview = async (id: number, approve: boolean) => {
    try {
      await api.shiftSwaps.review(id, { approve });
      toast.success(approve ? "Swap approved!" : "Swap denied");
      load();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Review failed");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pending Swap Reviews ({pending.length})</CardTitle>
      </CardHeader>
      <CardContent>
        {pending.length === 0 ? (
          <p className="text-sm text-muted-foreground">No pending swaps</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Requester</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pending.map((s) => (
                <TableRow key={s.id}>
                  <TableCell>{s.requester_name}</TableCell>
                  <TableCell>{s.target_name}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{s.status}</Badge>
                  </TableCell>
                  <TableCell>
                    {s.status === "accepted" && (
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => handleReview(s.id, true)}>Approve</Button>
                        <Button size="sm" variant="destructive" onClick={() => handleReview(s.id, false)}>Deny</Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
