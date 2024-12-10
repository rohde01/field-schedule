
export type Team = {
    team_id: number;
    name: string;
    year: string;
    club_id: number;
    gender: 'boys' | 'girls';
    is_academy: boolean;
    minimum_field_size: number;
    preferred_field_size: number | null;
    level: number;
    is_active: boolean;
};

export type TeamCreate = Omit<Team, 'team_id'>;

export type TeamUpdate = Partial<TeamCreate>;