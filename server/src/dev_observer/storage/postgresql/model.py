import datetime
from typing import Optional

from sqlalchemy import DateTime, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GitRepoEntity(Base):
    __tablename__ = "git_repo"

    __table_args__ = (
        UniqueConstraint('full_name', 'provider', name='uq_git_repo_full_name_provider'),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(index=True)
    provider: Mapped[int] = mapped_column(index=True, default=0)
    json_data: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"GitRepoEntity(id={self.id}, json_data={self.json_data})"


# class RepoTokenEntity(Base):
#     __tablename__ = "repo_token"
#
#     id: Mapped[str] = mapped_column(primary_key=True)
#     namespace: Mapped[str] = mapped_column(index=True)
#     provider: Mapped[int] = mapped_column()
#     workspace: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
#     repo: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
#     system: Mapped[bool] = mapped_column(default=False)
#     token: Mapped[str] = mapped_column()
#     expires_at: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True
#     )
#     created_at: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         nullable=False
#     )
#     updated_at: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#         nullable=False
#     )
#
#     def __repr__(self):
#         return f"RepoTokenEntity(id={self.id}, namespace={self.namespace}, provider={self.provider}, repo={self.repo})"


class GlobalConfigEntity(Base):
    __tablename__ = "global_config"

    id: Mapped[str] = mapped_column(primary_key=True)
    json_data: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"GlobalConfigEntity(id={self.id}, json_data={self.json_data})"


class ProcessingItemEntity(Base):
    __tablename__ = "processing_item"
    key: Mapped[str] = mapped_column(primary_key=True)
    json_data: Mapped[str]
    next_processing: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    last_processed: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]]
    namespace: Mapped[Optional[str]] = mapped_column(index=True, default=None)
    created_by: Mapped[Optional[str]] = mapped_column(index=True, default=None)
    reference_id: Mapped[Optional[str]] = mapped_column(index=True, default=None)
    request_type: Mapped[Optional[str]] = mapped_column(index=True, default=None)
    no_processing: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    processing_started_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    def __repr__(self):
        return f"ProcessingItemEntity(key={self.key}, json_data={self.json_data}, next_processing={self.next_processing}, last_processed={self.last_processed}, last_error={self.last_error}, no_processing={self.no_processing})"


class WebsiteEntity(Base):
    __tablename__ = "web_site"

    id: Mapped[str] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(index=True, unique=True)
    json_data: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"WebsiteEntity(id={self.id}, json_data={self.json_data})"


class ProcessingItemResultEntity(Base):
    __tablename__ = "processing_item_result"

    id: Mapped[str] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(index=True)
    json_data: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(default=None)
    created_by: Mapped[Optional[str]] = mapped_column(default=None)
    namespace: Mapped[Optional[str]] = mapped_column(default=None)
    reference_id: Mapped[Optional[str]] = mapped_column(index=True, default=None)
    request_type: Mapped[Optional[str]] = mapped_column(index=True, default=None)

    def __repr__(self):
        return f"ProcessingItemResultEntity(id={self.id}, key={self.key}, json_data={self.json_data})"
