-- Enable Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enums
DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('expense', 'income', 'transfer', 'credit', 'debit', 'investment');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'cancelled', 'reversed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE agent_run_status AS ENUM ('STARTED', 'COMPLETED', 'FAILED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    cpf TEXT,
    cnpj TEXT,
    complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: accounts
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_type TEXT NOT NULL,
    balance NUMERIC(19, 4) NOT NULL,
    currency CHAR(3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: transactions
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    category_id TEXT, -- Placeholder for future Category table relation
    amount NUMERIC(19, 4) NOT NULL,
    currency CHAR(3) NOT NULL,
    description TEXT NOT NULL,
    merchant TEXT NOT NULL,
    date TIMESTAMPTZ NOT NULL,
    status transaction_status NOT NULL,
    type transaction_type NOT NULL,
    embedding vector(1536), -- Vector embedding for search
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: agent_runs
CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    input_context JSONB DEFAULT '{}'::jsonb,
    output_result JSONB,
    status agent_run_status NOT NULL DEFAULT 'STARTED',
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    execution_time_ms INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
-- Vector Index (IVFFlat is lighter, HNSW is faster/more accurate but needs more memory. HNSW is good for general purpose)
-- Note: You need some data before creating an IVFFlat index effectively, but HNSW can be created empty.
CREATE INDEX IF NOT EXISTS idx_transactions_embedding ON transactions USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_agent_runs_user_id ON agent_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at ON agent_runs(created_at);

-- Trigger to update 'updated_at'
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_agent_runs_updated_at BEFORE UPDATE ON agent_runs FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Views

-- 1. Detailed Transaction View with Account Info
CREATE OR REPLACE VIEW v_transactions_details AS
SELECT 
    t.id AS transaction_id,
    t.description,
    t.merchant,
    t.amount,
    t.currency,
    t.date,
    t.type,
    t.status,
    t.category_id,
    u.id AS user_id,
    u.name AS user_name,
    a.id AS account_id,
    a.account_type,
    a.currency AS account_currency
FROM transactions t
JOIN users u ON t.user_id = u.id
LEFT JOIN accounts a ON t.account_id = a.id;

-- 2. Monthly Financial Summary View
CREATE OR REPLACE VIEW v_monthly_summary AS
SELECT 
    user_id,
    DATE_TRUNC('month', date) AS month,
    currency,
    SUM(CASE WHEN type = 'income' AND status = 'completed' THEN amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN type = 'expense' AND status = 'completed' THEN amount ELSE 0 END) AS total_expense,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY user_id, DATE_TRUNC('month', date), currency;

-- 3. Agent Usage Stats View
CREATE OR REPLACE VIEW v_agent_usage_stats AS
SELECT 
    agent_name,
    model_name,
    COUNT(*) AS total_runs,
    AVG(execution_time_ms) AS avg_execution_time,
    SUM(prompt_tokens) AS total_prompt_tokens,
    SUM(completion_tokens) AS total_completion_tokens
FROM agent_runs
GROUP BY agent_name, model_name;
