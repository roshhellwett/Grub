"""Tests for preflight module."""

import pytest
from unittest.mock import patch


class TestPreflightChecks:
    """Tests for pre-flight system checks."""

    def test_check_platform(self):
        from projectgrub.preflight import check_platform

        result = check_platform()
        assert result.name == "Platform"
        assert result.critical is True

    def test_check_root(self):
        from projectgrub.preflight import check_root

        result = check_root()
        assert result.name == "Root Access"

    def test_check_disk_space(self):
        from projectgrub.preflight import check_disk_space_available

        result = check_disk_space_available()
        assert result.name == "Disk Space"

    def test_run_all_checks(self):
        from projectgrub.preflight import run_all_checks

        report = run_all_checks()
        assert isinstance(report.checks, list)
        assert len(report.checks) > 0
        assert report.critical_failures is not None

    def test_preflight_report_properties(self):
        from projectgrub.preflight import run_all_checks

        report = run_all_checks()

        assert isinstance(report.passed_count, int)
        assert isinstance(report.failed_count, int)
        assert report.passed_count + report.failed_count == len(report.checks)
