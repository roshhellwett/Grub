"""Tests for exceptions module."""

import pytest


class TestExceptions:
    """Tests for custom exceptions."""

    def test_project_grub_error(self):
        from projectgrub.exceptions import ProjectGRUBError

        error = ProjectGRUBError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.suggestion is None

    def test_project_grub_error_with_suggestion(self):
        from projectgrub.exceptions import ProjectGRUBError

        error = ProjectGRUBError("Test error", "Try this instead")
        assert "Test error" in str(error)
        assert "Try this instead" in str(error)

    def test_system_check_error(self):
        from projectgrub.exceptions import SystemCheckError, ProjectGRUBError

        error = SystemCheckError("System check failed")
        assert isinstance(error, ProjectGRUBError)

    def test_theme_validation_error(self):
        from projectgrub.exceptions import ThemeValidationError, ProjectGRUBError

        error = ThemeValidationError("Theme is invalid")
        assert isinstance(error, ProjectGRUBError)

    def test_permission_error(self):
        from projectgrub.exceptions import PermissionError, ProjectGRUBError

        error = PermissionError("Not allowed")
        assert isinstance(error, ProjectGRUBError)

    def test_installation_error(self):
        from projectgrub.exceptions import InstallationError, ProjectGRUBError

        error = InstallationError("Install failed")
        assert isinstance(error, ProjectGRUBError)

    def test_rollback_error(self):
        from projectgrub.exceptions import RollbackError, ProjectGRUBError

        error = RollbackError("Rollback failed")
        assert isinstance(error, ProjectGRUBError)
