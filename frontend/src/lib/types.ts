export type UserRole = "student" | "supervisor";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  max_hours_per_week: number;
  is_active: boolean;
  created_at: string;
}

export interface Location {
  id: number;
  name: string;
  min_staff: number;
  max_staff: number;
  priority: number;
  is_active: boolean;
}

export interface AvailabilitySlot {
  id: number;
  user_id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  effective_date: string | null;
  is_recurring: boolean;
}

export interface UserAvailability {
  user_id: number;
  user_name: string;
  slots: AvailabilitySlot[];
}

export type ScheduleStatus = "draft" | "published" | "archived";
export type ShiftStatus = "scheduled" | "completed" | "missed" | "swapped";

export interface Shift {
  id: number;
  schedule_id: number;
  user_id: number;
  user_name?: string;
  location_id: number;
  location_name?: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  actual_date: string;
  status: ShiftStatus;
}

export interface Schedule {
  id: number;
  week_start_date: string;
  status: ScheduleStatus;
  generated_by: number | null;
  notes: string | null;
  created_at: string;
  shifts: Shift[];
}

export interface ScheduleWarning {
  day: string;
  time_slot: string;
  location: string;
  message: string;
}

export interface GenerateScheduleResponse {
  schedule: Schedule;
  warnings: ScheduleWarning[];
}

export type RequestType = "time_off" | "sick_day";
export type RequestStatus = "pending" | "approved" | "denied";

export interface TimeOffRequest {
  id: number;
  user_id: number;
  user_name?: string;
  request_type: RequestType;
  start_date: string;
  end_date: string;
  reason: string | null;
  status: RequestStatus;
  reviewed_by: number | null;
  created_at: string;
}

export type SwapStatus = "proposed" | "accepted" | "approved" | "denied" | "cancelled";

export interface ShiftSwap {
  id: number;
  requester_id: number;
  requester_name?: string;
  target_id: number;
  target_name?: string;
  requester_shift_id: number;
  target_shift_id: number | null;
  reason: string | null;
  status: SwapStatus;
  reviewed_by: number | null;
  created_at: string;
}

export interface Holiday {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  created_by: number | null;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  link: string | null;
  created_at: string;
}
