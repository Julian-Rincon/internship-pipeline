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
  owner_user_id: string | null;
  ownership_status: "unclaimed" | "claimed" | "paused" | "done";
  claimed_at: string | null;
  ownership_notes: string | null;
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

export type CompanyClaimPayload = {
  user_id: string;
  ownership_notes?: string | null;
};

export type CompanyOwnershipPayload = {
  ownership_status?: "claimed" | "paused" | "done";
  ownership_notes?: string | null;
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

export type JobPostingApplicationPayload = {
  user_id: string;
  contact_id?: string | null;
  type?: Application["type"];
  status?: Application["status"];
  next_action?: string | null;
  next_action_due?: string | null;
  notes?: string | null;
};

export type DiscoveryCandidate = {
  id: string;
  company_name: string;
  domain: string | null;
  careers_url: string | null;
  source: string;
  source_url: string | null;
  detected_job_title: string | null;
  detected_job_url: string | null;
  country: string | null;
  region: string | null;
  ats_type: string | null;
  confidence_score: number | null;
  status: "pending_review" | "approved" | "rejected" | "ignored";
  notes: string | null;
  created_at: string;
  reviewed_at: string | null;
};

export type JobPosting = {
  id: string;
  company_id: string | null;
  title: string;
  url: string;
  location: string | null;
  remote: boolean | null;
  description: string | null;
  source: string;
  detected_at: string;
  closed_at: string | null;
  status: "open" | "closed" | "archived";
};

export type DemoDiscoveryResult = {
  candidates_created: number;
  job_postings_created: number;
  candidates: DiscoveryCandidate[];
};

export type DiscoverySource = {
  id: string;
  name: string;
  source_type: "greenhouse" | "lever" | "ashby";
  source_key: string;
  base_url: string | null;
  company_hint: string | null;
  country: string | null;
  region: string | null;
  enabled: boolean;
  last_run_at: string | null;
  last_status: string | null;
  last_error: string | null;
  created_at: string;
};

export type DiscoverySourcePayload = {
  name: string;
  source_type: DiscoverySource["source_type"];
  source_key: string;
  base_url?: string | null;
  company_hint?: string | null;
  country?: string | null;
  region?: string | null;
  enabled?: boolean;
};

export type DiscoverySourceRunResult = {
  source_id: string;
  source_name: string;
  fetched_count: number;
  internship_like_count: number;
  candidates_created: number;
  candidates_skipped: number;
  job_postings_created: number;
  errors: string[];
};

export type DashboardSummary = {
  total_companies: number;
  total_users: number;
  total_contacts: number;
  total_applications: number;
  unclaimed_companies: number;
  claimed_companies: number;
  paused_companies: number;
  done_companies: number;
  overdue_reminders: number;
  due_today_reminders: number;
  due_soon_reminders: number;
  pending_review_reminders: number;
  applications_by_status: Record<string, number>;
};

export type Reminder = {
  id: string;
  type:
    | "application_overdue"
    | "application_due_today"
    | "application_due_soon"
    | "discovery_pending_review"
    | "claimed_company_stale";
  severity: "low" | "medium" | "high";
  title: string;
  description: string;
  related_entity_type: "application" | "discovery_candidate" | "company";
  related_entity_id: string;
  due_date: string | null;
  created_reference_date: string;
  metadata: Record<string, unknown>;
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

export async function claimCompany(companyId: string, payload: CompanyClaimPayload): Promise<Company> {
  const response = await fetch(`${getApiUrl()}/companies/${companyId}/claim`, {
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

export async function releaseCompany(companyId: string): Promise<Company> {
  const response = await fetch(`${getApiUrl()}/companies/${companyId}/release`, {
    method: "POST"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function updateCompanyOwnership(
  companyId: string,
  payload: CompanyOwnershipPayload
): Promise<Company> {
  const response = await fetch(`${getApiUrl()}/companies/${companyId}/ownership`, {
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

export async function getDiscoveryCandidates(): Promise<ApiResult<DiscoveryCandidate[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/discovery-candidates`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch discovery candidates", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load discovery candidates"
    };
  }
}

export async function getJobPostings(filters?: {
  status?: string;
  source?: string;
  title?: string;
  company_id?: string;
}): Promise<ApiResult<JobPosting[]>> {
  try {
    const params = new URLSearchParams();
    if (filters?.status) params.set("status", filters.status);
    if (filters?.source) params.set("source", filters.source);
    if (filters?.title) params.set("title", filters.title);
    if (filters?.company_id) params.set("company_id", filters.company_id);
    const query = params.toString();
    const response = await fetch(`${getApiUrl()}/job-postings${query ? `?${query}` : ""}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch job postings", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load job postings"
    };
  }
}

export async function linkJobPostingCompany(jobPostingId: string, companyId: string): Promise<JobPosting> {
  const response = await fetch(`${getApiUrl()}/job-postings/${jobPostingId}/link-company`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ company_id: companyId })
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function createApplicationFromJobPosting(
  jobPostingId: string,
  payload: JobPostingApplicationPayload
): Promise<Application> {
  const response = await fetch(`${getApiUrl()}/job-postings/${jobPostingId}/create-application`, {
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

export async function runDemoDiscovery(): Promise<DemoDiscoveryResult> {
  const response = await fetch(`${getApiUrl()}/discovery-candidates/run-demo-discovery`, {
    method: "POST"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function approveDiscoveryCandidate(candidateId: string): Promise<Company> {
  const response = await fetch(`${getApiUrl()}/discovery-candidates/${candidateId}/approve`, {
    method: "POST"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function rejectDiscoveryCandidate(candidateId: string): Promise<DiscoveryCandidate> {
  const response = await fetch(`${getApiUrl()}/discovery-candidates/${candidateId}/reject`, {
    method: "POST"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function getDiscoverySources(): Promise<ApiResult<DiscoverySource[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/discovery-sources`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch discovery sources", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load discovery sources"
    };
  }
}

export async function createDiscoverySource(payload: DiscoverySourcePayload): Promise<DiscoverySource> {
  const response = await fetch(`${getApiUrl()}/discovery-sources`, {
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

export async function updateDiscoverySource(
  sourceId: string,
  payload: Partial<DiscoverySourcePayload>
): Promise<DiscoverySource> {
  const response = await fetch(`${getApiUrl()}/discovery-sources/${sourceId}`, {
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

export async function deleteDiscoverySource(sourceId: string): Promise<void> {
  const response = await fetch(`${getApiUrl()}/discovery-sources/${sourceId}`, {
    method: "DELETE"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
}

export async function runDiscoverySource(sourceId: string): Promise<DiscoverySourceRunResult> {
  const response = await fetch(`${getApiUrl()}/discovery-sources/${sourceId}/run`, {
    method: "POST"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function runEnabledDiscoverySources(): Promise<DiscoverySourceRunResult[]> {
  const response = await fetch(`${getApiUrl()}/discovery-sources/run-enabled`, {
    method: "POST"
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }

  return response.json();
}

export async function getReminders(daysAhead = 7): Promise<ApiResult<Reminder[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/reminders?days_ahead=${daysAhead}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch reminders", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load reminders"
    };
  }
}

export type Interview = {
  id: string;
  company_id: string;
  user_id: string;
  interview_type: "phone" | "technical" | "system_design" | "behavioral" | "onsite" | "hr";
  scheduled_at: string | null;
  interviewer_role: string | null;
  questions: string[] | null;
  outcome: "passed" | "failed" | "pending";
  notes: string | null;
  created_at: string;
};

export type InterviewPayload = {
  company_id: string;
  user_id: string;
  interview_type: Interview["interview_type"];
  scheduled_at?: string | null;
  interviewer_role?: string | null;
  questions?: string[] | null;
  outcome?: Interview["outcome"];
  notes?: string | null;
};

export type VisaData = {
  id: string;
  company_id: string;
  country: string;
  intern_friendly: "green" | "yellow" | "red" | "unknown";
  visa_type: string | null;
  sponsor_verified: boolean;
  evidence_url: string | null;
  notes: string | null;
  last_verified: string | null;
  created_at: string;
};

export type VisaDataPayload = {
  company_id: string;
  country: string;
  intern_friendly?: VisaData["intern_friendly"];
  visa_type?: string | null;
  sponsor_verified?: boolean;
  evidence_url?: string | null;
  notes?: string | null;
  last_verified?: string | null;
};

export async function getInterviews(filters?: {
  company_id?: string;
  user_id?: string;
  outcome?: string;
}): Promise<ApiResult<Interview[]>> {
  try {
    const params = new URLSearchParams();
    if (filters?.company_id) params.set("company_id", filters.company_id);
    if (filters?.user_id) params.set("user_id", filters.user_id);
    if (filters?.outcome) params.set("outcome", filters.outcome);
    const query = params.toString();
    const response = await fetch(`${getApiUrl()}/interviews${query ? `?${query}` : ""}`, {
      cache: "no-store"
    });
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch interviews", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load interviews"
    };
  }
}

export async function createInterview(payload: InterviewPayload): Promise<Interview> {
  const response = await fetch(`${getApiUrl()}/interviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
  return response.json();
}

export async function getVisaData(): Promise<ApiResult<VisaData[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/visa`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch visa data", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load visa data"
    };
  }
}

export async function getVisaByCompany(companyId: string): Promise<ApiResult<VisaData[]>> {
  try {
    const response = await fetch(`${getApiUrl()}/visa/by-company/${companyId}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }
    return { ok: true, data: await response.json() };
  } catch (error) {
    console.error("Failed to fetch visa data for company", error);
    return {
      ok: false,
      data: [],
      error: error instanceof Error ? error.message : "Failed to load visa data for company"
    };
  }
}

export async function createVisaData(payload: VisaDataPayload): Promise<VisaData> {
  const response = await fetch(`${getApiUrl()}/visa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Backend returned ${response.status}`);
  }
  return response.json();
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
        unclaimed_companies: 0,
        claimed_companies: 0,
        paused_companies: 0,
        done_companies: 0,
        overdue_reminders: 0,
        due_today_reminders: 0,
        due_soon_reminders: 0,
        pending_review_reminders: 0,
        applications_by_status: {}
      },
      error: error instanceof Error ? error.message : "Failed to load dashboard summary"
    };
  }
}
