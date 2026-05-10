import { getUsers } from "../../lib/api";
import { UserCreateForm } from "./user-forms";
import { UserList } from "./user-list";

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

      {!result.ok ? <p className="notice error">Could not load users: {result.error}</p> : null}
      <UserList users={users} />
    </section>
  );
}
