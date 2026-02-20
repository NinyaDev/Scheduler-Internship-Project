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

export interface Holiday {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  created_by: number | null;
  created_at: string;
}