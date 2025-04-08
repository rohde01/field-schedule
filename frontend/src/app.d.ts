import type { Session, SupabaseClient } from '@supabase/supabase-js'
import type { Database } from './database.types.ts'
import type { User as CustomUser } from '$lib/schemas/user'

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
    }
  }
}

declare module '@supabase/supabase-js' {
  interface User extends CustomUser {}
}

export {}