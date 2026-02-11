"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"], unique=True)

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "permission_id",
            sa.Integer(),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("kubeconfig_ref", sa.Text(), nullable=False),
        sa.Column("default_namespace_policy", sa.JSON(), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_index("ix_clusters_name", "clusters", ["name"], unique=True)

    op.create_table(
        "user_namespace_scopes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("namespace", sa.String(128), nullable=False),
        sa.Column("allowed_actions", sa.JSON(), nullable=False),
        sa.Column("denied_actions", sa.JSON(), nullable=False),
        sa.UniqueConstraint("user_id", "cluster_id", "namespace", name="uq_user_ns_scope"),
    )

    op.create_table(
        "resource_intents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("mode", sa.String(64), nullable=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("namespace", sa.String(128), nullable=False),
        sa.Column("spec_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_intents_scope",
        "resource_intents",
        ["cluster_id", "namespace", "resource_type", "status"],
        unique=False,
    )

    op.create_table(
        "resource_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("intent_id", sa.Integer(), sa.ForeignKey("resource_intents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("result", sa.String(32), nullable=False),
        sa.Column("logs_ref", sa.String(255), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
    )

    op.create_table(
        "observed_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("namespace", sa.String(128), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_name", sa.String(150), nullable=False),
        sa.Column("observed_json", sa.JSON(), nullable=False),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("scope", sa.JSON(), nullable=False),
        sa.Column("promql", sa.Text(), nullable=False),
        sa.Column("interval_sec", sa.Integer(), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("channels", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_alert_rules_name", "alert_rules", ["name"], unique=True)

    op.create_table(
        "alert_firings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("fired_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_alert_firings_time", "alert_firings", ["fired_at"], unique=False)

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rule_id", sa.Integer(), sa.ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("ai_summary_ref", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "incident_timeline",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "ai_pricing",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("prompt_per_1k", sa.Float(), nullable=False),
        sa.Column("completion_per_1k", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_pricing_model", "ai_pricing", ["model"], unique=True)

    op.create_table(
        "ai_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("feature", sa.String(80), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("total_cost", sa.Float(), nullable=False),
        sa.Column("unit_costs", sa.JSON(), nullable=False),
        sa.Column("input_hash", sa.String(128), nullable=True),
        sa.Column("output_ref", sa.String(255), nullable=True),
        sa.Column("ts", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ai_requests_time", "ai_requests", ["ts"], unique=False)

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("resource_kind", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(120), nullable=False),
        sa.Column("diff_json", sa.JSON(), nullable=False),
        sa.Column("outcome", sa.String(32), nullable=False),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("ts", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_time", "audit_log", ["ts"], unique=False)

    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(120), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metadata", sa.JSON(), nullable=False),
    )
    op.create_index("ix_feature_flags_key", "feature_flags", ["key"], unique=True)

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("hashed_key", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "api_keys",
        "feature_flags",
        "audit_log",
        "ai_requests",
        "ai_pricing",
        "incident_timeline",
        "incidents",
        "alert_firings",
        "alert_rules",
        "observed_resources",
        "resource_runs",
        "resource_intents",
        "user_namespace_scopes",
        "clusters",
        "role_permissions",
        "user_roles",
        "permissions",
        "roles",
        "users",
    ]:
        op.drop_table(table)
