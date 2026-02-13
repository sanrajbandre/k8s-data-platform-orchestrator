from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserMe(UserOut):
    permissions: list[str] = Field(default_factory=list)


class PermissionOut(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class ClusterCreate(BaseModel):
    name: str
    kubeconfig: str = Field(description="Raw kubeconfig to be encrypted before persistence")
    default_namespace_policy: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, Any] = Field(default_factory=dict)


class ClusterOut(BaseModel):
    id: int
    name: str
    kubeconfig_ref: str
    default_namespace_policy: dict[str, Any]
    labels: dict[str, Any]
    status: str

    model_config = {"from_attributes": True}


class NamespacePolicyCreate(BaseModel):
    user_id: int
    namespace: str
    allowed_actions: list[str] = Field(default_factory=list)
    denied_actions: list[str] = Field(default_factory=list)


class NamespacePolicyOut(BaseModel):
    id: int
    user_id: int
    cluster_id: int
    namespace: str
    allowed_actions: dict[str, list[str]]
    denied_actions: dict[str, list[str]]

    model_config = {"from_attributes": True}


class ScaleRequest(BaseModel):
    replicas: int = Field(ge=0, le=500)


class ResourceIntentCreate(BaseModel):
    cluster_id: int
    namespace: str
    spec_json: dict[str, Any]


class ResourceIntentOut(BaseModel):
    id: int
    resource_type: str
    mode: str | None
    cluster_id: int
    namespace: str
    spec_json: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ResourceRunOut(BaseModel):
    id: int
    intent_id: int
    action: str
    started_at: datetime
    ended_at: datetime | None
    result: str
    logs_ref: str | None
    retry_count: int

    model_config = {"from_attributes": True}


class KafkaIntentCreate(ResourceIntentCreate):
    kafka_mode: str
    kafka_version: str
    strimzi_version: str


class PromQueryRequest(BaseModel):
    query: str
    time: float | None = None


class PromRangeRequest(BaseModel):
    query: str
    start: float
    end: float
    step: str


class AlertRuleCreate(BaseModel):
    name: str
    scope: dict[str, Any]
    promql: str
    interval_sec: int = Field(default=60, ge=15)
    threshold: float
    severity: str = "medium"
    channels: list[str] = Field(default_factory=list)


class AlertRuleOut(BaseModel):
    id: int
    name: str
    scope: dict[str, Any]
    promql: str
    interval_sec: int
    threshold: float
    severity: str
    channels: list[str]
    enabled: bool

    model_config = {"from_attributes": True}


class IncidentOut(BaseModel):
    id: int
    rule_id: int | None
    severity: str
    state: str
    evidence_json: dict[str, Any]
    ai_summary_ref: str | None

    model_config = {"from_attributes": True}
