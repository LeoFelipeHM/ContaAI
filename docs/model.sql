
-- Primeiro esse

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Depois cria as tabelas

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  timezone TEXT DEFAULT 'America/Sao_Paulo',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE account_types (
  id SERIAL PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  account_type_id INT NOT NULL,
  name TEXT NOT NULL,
  institution TEXT,
  currency CHAR(3) DEFAULT 'BRL',
  initial_balance NUMERIC(18,2) DEFAULT 0,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_accounts_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT fk_accounts_type
    FOREIGN KEY (account_type_id) REFERENCES account_types(id)
);

CREATE TABLE categories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  parent_category_id UUID,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  color_hex TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_categories_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT fk_parent_category
    FOREIGN KEY (parent_category_id) REFERENCES categories(id),

  CONSTRAINT chk_category_type
    CHECK (type IN ('income', 'expense', 'transfer'))
);

CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_tags_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT uq_tag_user_name UNIQUE (user_id, name)
);

CREATE TABLE credit_cards (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  billing_account_id UUID,
  issuer TEXT,
  name TEXT,
  last4 CHAR(4),
  mask TEXT,
  credit_limit NUMERIC(18,2),
  currency CHAR(3) DEFAULT 'BRL',
  closing_day INT,
  due_day INT,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_credit_card_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT fk_credit_card_account
    FOREIGN KEY (billing_account_id) REFERENCES accounts(id)
);

CREATE TABLE credit_card_statements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  credit_card_id UUID NOT NULL,
  user_id UUID NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  closing_date DATE,
  due_date DATE,
  total_amount NUMERIC(18,2) DEFAULT 0,
  paid_amount NUMERIC(18,2) DEFAULT 0,
  status TEXT DEFAULT 'open',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_statement_card
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id),

  CONSTRAINT fk_statement_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT chk_statement_status
    CHECK (status IN ('open', 'closed', 'paid', 'partial'))
);

CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  account_id UUID,
  category_id UUID,
  date DATE NOT NULL,
  amount NUMERIC(18,2) NOT NULL,
  description TEXT,
  type TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  credit_card_id UUID,
  statement_id UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_transactions_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT fk_transactions_account
    FOREIGN KEY (account_id) REFERENCES accounts(id),

  CONSTRAINT fk_transactions_category
    FOREIGN KEY (category_id) REFERENCES categories(id),

  CONSTRAINT fk_transactions_card
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id),

  CONSTRAINT fk_transactions_statement
    FOREIGN KEY (statement_id) REFERENCES credit_card_statements(id),

  CONSTRAINT chk_transaction_type
    CHECK (type IN ('income', 'expense', 'transfer')),

  CONSTRAINT chk_transaction_status
    CHECK (status IN ('pending', 'posted', 'reconciled'))
);

CREATE TABLE scheduled_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  account_id UUID NOT NULL,
  category_id UUID,
  description TEXT,
  amount NUMERIC(18,2) NOT NULL,
  type TEXT NOT NULL,
  frequency TEXT NOT NULL,
  reference_day INT,
  next_execution DATE NOT NULL,
  end_date DATE,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_scheduled_user
    FOREIGN KEY (user_id) REFERENCES users(id),

  CONSTRAINT fk_scheduled_account
    FOREIGN KEY (account_id) REFERENCES accounts(id),

  CONSTRAINT fk_scheduled_category
    FOREIGN KEY (category_id) REFERENCES categories(id),

  CONSTRAINT chk_scheduled_type
    CHECK (type IN ('income', 'expense', 'transfer'))
);

CREATE TABLE budgets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_amount NUMERIC(18,2),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_budget_user
    FOREIGN KEY (user_id) REFERENCES users(id)
);


CREATE TABLE transaction_tags (
  transaction_id UUID NOT NULL,
  tag_id UUID NOT NULL,

  PRIMARY KEY (transaction_id, tag_id),

  CONSTRAINT fk_transaction_tag_transaction
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,

  CONSTRAINT fk_transaction_tag_tag
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

