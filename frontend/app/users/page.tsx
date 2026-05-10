import { getUsers } from "../../lib/api";
import { ProfileStatusBadge, UserCreateForm, UserEditForm } from "./user-forms";

export const dynamic = "force-dynamic";

export default async function UsersPage() {
  const result = await getUsers();
  const users = result.data;

  return (
    <section>
      <h1>Users</h1>
      <p className="muted">
        Progressive profiles for team members. Optional links and skills can be completed later.
      </p>

      <UserCreateForm />

      <div className="panel table-wrap" style={{ marginTop: 16 }}>
        {!result.ok ? <p className="notice error">Could not load users: {result.error}</p> : null}
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
            {users.length === 0 ? (
              <tr>
                <td colSpan={7} className="muted">
                  No users yet.
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id}>
                  <td>
                    <strong>{user.name}</strong>
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
    </section>
  );
}

