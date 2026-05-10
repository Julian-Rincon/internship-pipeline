"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { User } from "../../lib/api";
import { ProfileStatusBadge, UserEditForm } from "./user-forms";

export function UserList({ users }: { users: User[] }) {
  const [query, setQuery] = useState("");

  const filteredUsers = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return users;
    }

    return users.filter((user) =>
      [
        user.name,
        user.email,
        user.role,
        user.profile_status,
        user.github_handle,
        user.linkedin_url,
        user.target_roles?.join(" "),
        user.technical_interests?.join(" "),
        user.strong_skills?.join(" ")
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery)
    );
  }, [query, users]);

  return (
    <div className="panel table-wrap" style={{ marginTop: 16 }}>
      <label className="search-field">
        Search users
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by name, email, profile status or skills"
        />
      </label>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Profile</th>
            <th>GitHub</th>
            <th>LinkedIn</th>
            <th>Edit</th>
          </tr>
        </thead>
        <tbody>
          {filteredUsers.length === 0 ? (
            <tr>
              <td colSpan={7} className="muted">
                No users match the current search.
              </td>
            </tr>
          ) : (
            filteredUsers.map((user) => (
              <tr key={user.id}>
                <td>
                  <Link href={`/users/${user.id}`}>
                    <strong>{user.name}</strong>
                  </Link>
                </td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <ProfileStatusBadge status={user.profile_status} />
                </td>
                <td>{user.github_handle ?? "-"}</td>
                <td>
                  {user.linkedin_url ? (
                    <a href={user.linkedin_url} target="_blank" rel="noreferrer">
                      LinkedIn
                    </a>
                  ) : (
                    "-"
                  )}
                </td>
                <td>
                  <UserEditForm user={user} />
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
