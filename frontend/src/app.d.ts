import type { Session, SupabaseClient } from '@supabase/supabase-js'
import type { Database } from './database.types.ts'
import type { User as CustomUser } from '$lib/schemas/user'
import type { Team } from '$lib/schemas/team'
import type { Facility } from '$lib/schemas/facility'
import type { Field } from '$lib/schemas/field'
import type { Schedule } from '$lib/schemas/schedule'
import type { EventSchedule } from '$lib/schemas/event'

declare global {
  namespace App {
    interface Locals {
      supabase: SupabaseClient<Database>
      safeGetSession: () => Promise<{ session: Session | null; user: CustomUser | null }>
      session: Session | null
      user: CustomUser | null
    }
    interface PageData {
      session: Session | null
      supabase: SupabaseClient<Database>
      user: CustomUser | null
      facilities: Facility[]
      fields: Field[]
      teams: Team[]
      schedules: Schedule[]
      cookies: Record<string, string>
    }
  }
}

declare module '@supabase/supabase-js' {
  interface User extends CustomUser {}
}

export {}