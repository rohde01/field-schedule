import type { SupabaseClient, Session, User } from '@supabase/supabase-js';
import type { Database } from './types/supabase';

declare global {
	namespace App {
		interface Locals {
			supabase: SupabaseClient<Database>;
			user: User | null;
			token: string | null;
		}
	}
}
