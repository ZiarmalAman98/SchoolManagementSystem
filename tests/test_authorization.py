from app.authorization import allowed_actions, has_permission


def test_teacher_has_limited_academic_permissions():
    assert has_permission("Teacher", "attendance", "create")
    assert has_permission("Teacher", "results", "edit")
    assert not has_permission("Teacher", "users", "manage")
    assert not has_permission("Teacher", "students", "delete")
    assert not has_permission("Teacher", "backup", "backup")


def test_accountant_cannot_access_academic_results():
    assert has_permission("Accountant", "fees", "collect")
    assert has_permission("Accountant", "fees", "print")
    assert not has_permission("Accountant", "results", "view")
    assert not has_permission("Accountant", "teachers", "edit")


def test_super_admin_can_manage_everything():
    assert has_permission("Super Admin", "users", "manage")
    assert has_permission("Super Admin", "backup", "restore")
    assert has_permission("Super Admin", "settings", "delete")


def test_allowed_actions_returns_only_authorized_actions():
    actions = allowed_actions("Teacher", "students")
    assert "view" in actions
    assert "create" in actions
    assert "edit" in actions
    assert "delete" not in actions
