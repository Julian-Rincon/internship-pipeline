"use client";

import { FormEvent, useState } from "react";
import { createUser, updateUser, type User, type UserPayload } from "../../lib/api";

const roles = ["member", "admin"] as const;
const statuses = ["incomplete", "in_progress", "ready"] as const;

function nullableValue(formData: FormData, name: string) {
  const raw = formData.get(name)?.toString().trim();
  return raw ? raw : null;
}

function listValue(formData: FormData, name: string) {
  const raw = nullableValue(formData, name);
  return raw
    ? raw
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
    : null;
}

function profilePayload(formData: FormData): UserPayload {
  return {
    name: nullableValue(formData, "name") ?? "",
    email: nullableValue(formData, "email") ?? "",
    role: nullableValue(formData, "role") as UserPayload["role"],
    profile_status: nullableValue(formData, "profile_status") as UserPayload["profile_status"],
    github_handle: nullableValue(formData, "github_handle"),
    linkedin_url: nullableValue(formData, "linkedin_url"),
    portfolio_url: nullableValue(formData, "portfolio_url"),
    cv_url: nullableValue(formData, "cv_url"),
    target_roles: listValue(formData, "target_roles"),
    target_regions: listValue(formData, "target_regions"),
    target_countries: listValue(formData, "target_countries"),
    target_company_types: listValue(formData, "target_company_types"),
    preferred_industries: listValue(formData, "preferred_industries"),
    technical_interests: listValue(formData, "technical_interests"),
    strong_skills: listValue(formData, "strong_skills"),
    learning_goals: listValue(formData, "learning_goals"),
    internship_goals: nullableValue(formData, "internship_goals")
  };
}

export function ProfileStatusBadge({ status }: { status: User["profile_status"] }) {
  return <span className={`badge badge-${status}`}>{status}</span>;
}

export function UserCreateForm() {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const payload: UserPayload = {
      name: nullableValue(formData, "name") ?? "",
      email: nullableValue(formData, "email") ?? "",
      role: nullableValue(formData, "role") as UserPayload["role"],
      profile_status: nullableValue(formData, "profile_status") as UserPayload["profile_status"]
    };

    try {
      await createUser(payload);
      event.currentTarget.reset();
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not create user");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <h2>Add user</h2>
      {error ? <p className="notice error">{error}</p> : null}
      <div className="form-grid">
        <label>
          Name
          <input name="name" required />
        </label>
        <label>
          Email
          <input name="email" type="email" required />
        </label>
        <label>
          Role
          <select name="role" defaultValue="member">
            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </label>
        <label>
          Profile status
          <select name="profile_status" defaultValue="incomplete">
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
      </div>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create user"}
      </button>
    </form>
  );
}

export function UserEditForm({ user }: { user: User }) {
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await updateUser(user.id, profilePayload(new FormData(event.currentTarget)));
      window.location.reload();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Could not update user");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <details className="edit-details">
      <summary>Edit profile</summary>
      <form className="form compact-form" onSubmit={onSubmit}>
        {error ? <p className="notice error">{error}</p> : null}
        <div className="form-grid">
          <label>
            Name
            <input name="name" defaultValue={user.name} required />
          </label>
          <label>
            Email
            <input name="email" type="email" defaultValue={user.email} required />
          </label>
          <label>
            Role
            <select name="role" defaultValue={user.role}>
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </label>
          <label>
            Profile status
            <select name="profile_status" defaultValue={user.profile_status}>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label>
            GitHub handle
            <input name="github_handle" defaultValue={user.github_handle ?? ""} />
          </label>
          <label>
            LinkedIn URL
            <input name="linkedin_url" type="url" defaultValue={user.linkedin_url ?? ""} />
          </label>
          <label>
            Portfolio URL
            <input name="portfolio_url" type="url" defaultValue={user.portfolio_url ?? ""} />
          </label>
          <label>
            CV URL
            <input name="cv_url" type="url" defaultValue={user.cv_url ?? ""} />
          </label>
          <label>
            Target roles
            <input name="target_roles" defaultValue={user.target_roles?.join(", ") ?? ""} />
          </label>
          <label>
            Target regions
            <input name="target_regions" defaultValue={user.target_regions?.join(", ") ?? ""} />
          </label>
          <label>
            Target countries
            <input name="target_countries" defaultValue={user.target_countries?.join(", ") ?? ""} />
          </label>
          <label>
            Company types
            <input
              name="target_company_types"
              defaultValue={user.target_company_types?.join(", ") ?? ""}
            />
          </label>
          <label>
            Industries
            <input
              name="preferred_industries"
              defaultValue={user.preferred_industries?.join(", ") ?? ""}
            />
          </label>
          <label>
            Technical interests
            <input
              name="technical_interests"
              defaultValue={user.technical_interests?.join(", ") ?? ""}
            />
          </label>
          <label>
            Strong skills
            <input name="strong_skills" defaultValue={user.strong_skills?.join(", ") ?? ""} />
          </label>
          <label>
            Learning goals
            <input name="learning_goals" defaultValue={user.learning_goals?.join(", ") ?? ""} />
          </label>
        </div>
        <label className="full-width">
          Internship goals
          <textarea name="internship_goals" defaultValue={user.internship_goals ?? ""} />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Save profile"}
        </button>
      </form>
    </details>
  );
}

