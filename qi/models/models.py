from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    flaky_count: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    git_commit: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")  # running / completed / blocked

    results: Mapped[list["TestResult"]] = relationship(back_populates="test_run")


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_run_id: Mapped[int] = mapped_column(ForeignKey("test_runs.id"))
    test_name: Mapped[str] = mapped_column(String(256), index=True)
    test_file: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32))  # passed / failed / skipped / flaky
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_flaky: Mapped[bool] = mapped_column(Boolean, default=False)
    failure_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    test_run: Mapped["TestRun"] = relationship(back_populates="results")
    evidence: Mapped[list["FailureEvidence"]] = relationship(back_populates="test_result")


class FailureEvidence(Base):
    __tablename__ = "failure_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_result_id: Mapped[int] = mapped_column(ForeignKey("test_results.id"))
    evidence_type: Mapped[str] = mapped_column(String(64))  # screenshot / log / api_response / stack_trace
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    test_result: Mapped["TestResult"] = relationship(back_populates="evidence")


class FlakyTestHistory(Base):
    __tablename__ = "flaky_test_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_name: Mapped[str] = mapped_column(String(256), index=True)
    total_runs: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_rate: Mapped[float] = mapped_column(Float, default=0.0)
    last_failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_currently_flaky: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))