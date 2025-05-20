import nox


@nox.session(venv_backend="uv")
def lint(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    _install_dev_deps(session)
    session.run("ruff", "check", *session.posargs)


@nox.session(venv_backend="uv")
def check_format(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    _install_dev_deps(session)
    session.run("ruff", "format", "--check", *session.posargs)


@nox.session(venv_backend="uv")
def format(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    _install_dev_deps(session)
    session.run("ruff", "format", *session.posargs)


@nox.session(venv_backend="uv")
def fix(session: nox.Session) -> None:
    """Fix formatting and linting"""
    _install_dev_deps(session)
    session.run("ruff", "check", "--fix")
    session.run("ruff", "format")


@nox.session(venv_backend="uv")
def test(session: nox.Session) -> None:
    """Run tests"""
    _install_all_deps(session)
    session.run("pytest")


def _install_dev_deps(session: nox.Session) -> None:
    _run_install(session, only_dev=True)


def _install_all_deps(session: nox.Session) -> None:
    _run_install(session, only_dev=False)


def _run_install(session: nox.Session, only_dev: bool) -> None:
    cmd = ["uv", "sync"]
    if only_dev:
        cmd.append("--only-dev")
    session.run_install(
        *cmd,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
