import uuid
from sqlalchemy import ( Column, Text, String, Boolean, Date, Integer, Numeric, ForeignKey, CheckConstraint, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    timezone = Column(Text, default="America/Sao_Paulo")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    accounts = relationship("Account", back_populates="user")
    categories = relationship("Category", back_populates="user")
    tags = relationship("Tag", back_populates="user")

class AccountType(Base):
    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True)
    key = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_type_id = Column(Integer, ForeignKey("account_types.id"), nullable=False)
    name = Column(Text, nullable=False)
    institution = Column(Text)
    currency = Column(String(3), default="BRL")
    initial_balance = Column(Numeric(18, 2), default=0)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="accounts")
    account_type = relationship("AccountType")
    credit_cards = relationship("CreditCard", back_populates="billing_account")

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    color_hex = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id])

    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')",
            name="chk_category_type"
        ),
    )

class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_tag_user_name"),
    )

class CreditCard(Base):
    __tablename__ = "credit_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    billing_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    issuer = Column(Text)
    name = Column(Text)
    last4 = Column(String(4))
    mask = Column(Text)
    credit_limit = Column(Numeric(18, 2))
    currency = Column(String(3), default="BRL")
    closing_day = Column(Integer)
    due_day = Column(Integer)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    billing_account = relationship("Account", back_populates="credit_cards")
    statements = relationship("CreditCardStatement", back_populates="credit_card")

class CreditCardStatement(Base):
    __tablename__ = "credit_card_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credit_card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    closing_date = Column(Date)
    due_date = Column(Date)
    total_amount = Column(Numeric(18, 2), default=0)
    paid_amount = Column(Numeric(18, 2), default=0)
    status = Column(Text, default="open")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    credit_card = relationship("CreditCard", back_populates="statements")

    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'closed', 'paid', 'partial')",
            name="chk_statement_status"
        ),
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    credit_card_id = Column(UUID(as_uuid=True), ForeignKey("credit_cards.id"))
    statement_id = Column(UUID(as_uuid=True), ForeignKey("credit_card_statements.id"))
    date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    description = Column(Text)
    type = Column(Text, nullable=False)
    status = Column(Text, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')",
            name="chk_transaction_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'posted', 'reconciled')",
            name="chk_transaction_status"
        ),
    )

class TransactionTag(Base):
    __tablename__ = "transaction_tags"

    transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )

class ScheduledTransaction(Base):
    __tablename__ = "scheduled_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    description = Column(Text)
    amount = Column(Numeric(18, 2), nullable=False)
    type = Column(Text, nullable=False)
    frequency = Column(Text, nullable=False)
    reference_day = Column(Integer)
    next_execution = Column(Date, nullable=False)
    end_date = Column(Date)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(18, 2))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
