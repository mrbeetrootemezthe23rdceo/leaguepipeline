CREATE TABLE crawl_queue (
    puuid TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending' or 'done'
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);