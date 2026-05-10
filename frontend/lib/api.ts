export type Company = {
  id: string;
  name: string;
  domain: string | null;
  tier: "A" | "B" | "C" | null;
  country: string | null;
  region: string | null;
  careers_url: string | null;
  ats_type: string | null;
  visa_friendly_intern: "green" | "yellow" | "red" | "unknown" | null;
  status: "active" | "paused" | "rejected" | "won";
  created_at: string;
};

export type CompanyPayload = {
  name: string;
  domain?: string | null;
  tier?: "A" | "B" | "C" | null;
  country?: string | null;
  region?: string | null;
  careers_url?: string | null;
  ats_type?: string | null;
  visa_friendly_intern?: "green" | "yellow" | "red" | "unknown" | null;
  status?: "active" | "paused" | "rejected" | "won";
};

export type User = {
  id: string;
  name: string;
  email: string;
  role: "member" | "admin";
  profile_status: "incomplete" | "in_progress" | "ready";
  github_handle: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  cv_url: string | null;
  target_roles: string[] | null;
  target_regions: string[] | null;
  target_countries: string[] | null;
  target_company_types: string[] | null;
  preferred_industries: string[] | null;
  technical_interests: string[] | null;
  strong_skills: string[] | null;
  learning_goals: string[] | null;
  internship_goals: string | null;
  profile_completed_at: string | null;
  created_at: string;
};

export type UserPayload = {
  name: string;
  email: string;
  role?: "member" | "admin";
  profile_status?: "incomplete" | "in_progress" | "ready";
  github_handle?: string | null;
  linkedin_url?: string | null;
  portfolio_url?: string | null;
  cv_url?: string | null;
  target_roles?: string[] | null;
  target_regions?: string[] | null;
  target_countries?: string[] | null;
  target_company_types?: string[] | null;
  preferred_industries?: string[] | null;
  technical_interests?: string[] | null;
  strong_skills?: string[] | null;
  learning_goals?: string[] | null;
  internship_goals?: string | null;
  profile_completed_at?: string | null;
};

export type Contact = {
  id: string;
  company_id: string;
  full_name: string;
  role: string | null;
  email: string | null;
  linkedin_url: string | null;
  github_handle: string | null;
  twitter_handle: string | null;
  source: "manual" | "linkedin" | "github" | "apollo" | "hunter" | "arxiv" | "other";
  affinity_type: "alumni" | "colombian" | "latino" | "recruiter" | "engineer" | "none" | "unknown";
  affinity_score: number | null;
  role_relevance: number | null;
  total_score: number | null;
  metadata: Record<string, unknown> | null;
  contacted: boolean;
  created_at: string;
  refreshed_at: string | null;
};

export type ContactPayload = {
  company_id: string;
  full_name: string;
  role?: string | null;
  email?: string | null;
  linkedin_url?: string | null;
  github_handle?: string | null;
  twitter_handle?: string | null;
  source?: Contact["source"];
  affinity_type?: Contact["affinity_type"];
  affinity_score?: number | null;
  role_relevance?: number | null;
  total_score?: number | null;
  metadata?: Record<string, unknown> | null;
  contacted?: boolean;
  refreshed_at?: string | null;
};

export type Application = {
  id: string;
  company_id: string;
  user_id: string;
  contact_id: string | null;
  type: "formal" | "speculative" | "referral" | "networking" | "other";
  status:
    | "researching"
    | "contacted"
    | "responded"
    | "interviewing"
    | "offer"
    | "rejected"
    | "paused";
  applied_at: string | null;
  next_action: string | null;
  next_action_due: string | null;
  notes: string | null;
  created_at: string;
};

export type ApplicationPayload = {
  company_id: string;
  user_id: string;
  contact_id?: string | null;
  type: Application["type"];
  status: Application["status"];
  applied_at?: string | null;
  next_action?: string | null;
  next_action_due?: string | null;
  notes?: string | null;
};

export type DashboardSummary = {
  total_companies: number;
  total_users: number;
  total_contacts: number;
  total_applications: number;
  applications_by_status: Record<string, number>;
};

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; data: T; error: string };

function getApiUrl(): string {
  if (typeof window === "undefined") {
    return process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  }

  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export async function getCompanies(): Promise<ApiResult<Company[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/companies`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch companies", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load companies"
    };
  }
}

export async function getCompany(companyId: string): Promise<ApiResult<Company | null>> {
  try {
    const response = await fetch(`${getApiUrl()}/companies/${companyId}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch company", error);
    return {
      ok: false,
      data: null,
      error: error instanceof Error ? error.message : "Failed to load company"
    };
  }
}

export async function getCompanyContacts(companyId: string): Promise<ApiResult<Contact[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/companies/${companyId}/contacts`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch company contacts", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load company contacts"
    };
  }
}

export async function getCompanyApplications(companyId: string): Promise<ApiResult<Application[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/companies/${companyId}/applications`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch company applications", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load company applications"
    };
  }
}

export async function createCompany(payload: CompanyPayload): Promise<Company> {
  const response = await fetch(`${getApiUrl()}/companies`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function getUsers(): Promise<ApiResult<User[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/users`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch users", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load users"
    };
  }
}

export async function getUser(userId: string): Promise<ApiResult<User | null>> {
  try {
    const response = await fetch(`${getApiUrl()}/users/${userId}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch user", error);
    return {
      ok: false,
      data: null,
      error: error instanceof Error ? error.message : "Failed to load user"
    };
  }
}

export async function getUserApplications(userId: string): Promise<ApiResult<Application[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/users/${userId}/applications`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch user applications", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load user applications"
    };
  }
}

export async function createUser(payload: UserPayload): Promise<User> {
  const response = await fetch(`${getApiUrl()}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function updateUser(userId: string, payload: Partial<UserPayload>): Promise<User> {
  const response = await fetch(`${getApiUrl()}/users/${userId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function getContacts(): Promise<ApiResult<Contact[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/contacts`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch contacts", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load contacts"
    };
  }
}

export async function createContact(payload: ContactPayload): Promise<Contact> {
  const response = await fetch(`${getApiUrl()}/contacts`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function getApplications(): Promise<ApiResult<Application[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/applications`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch applications", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load applications"
    };
  }
}

export async function createApplication(payload: ApplicationPayload): Promise<Application> {
  const response = await fetch(`${getApiUrl()}/applications`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function updateApplication(
  applicationId: string,
  payload: Partial<ApplicationPayload>
): Promise<Application> {
  const response = await fetch(`${getApiUrl()}/applications/${applicationId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function deleteApplication(applicationId: string): Promise<void> {
  const response = await fetch(`${getApiUrl()}/applications/${applicationId}`, {
    method: "DELETE"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
}

export async function getDashboardSummary(): Promise<ApiResult<DashboardSummary>> {
  try {
    const response = await fetch(`${getApiUrl()}/dashboard/summary`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch dashboard summary", error);
    return {
      ok: false,
      data: {
        total_companies: 0,
        total_users: 0,
        total_contacts: 0,
        total_applications: 0,
        applications_by_status: {}
      },
      error: error instanceof Error ? error.message : "Failed to load dashboard summary"
    };
  }
}
