-- Migration 008: Social Follow/Following System & User Search
-- Enables users to search other users, follow/unfollow them, view followers & following counts,
-- and chat or connect seamlessly.

CREATE TABLE IF NOT EXISTS user_follows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT user_follows_unique UNIQUE (follower_id, following_id),
    CONSTRAINT user_cannot_follow_self CHECK (follower_id <> following_id)
);

CREATE INDEX IF NOT EXISTS idx_user_follows_follower ON user_follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_user_follows_following ON user_follows(following_id);

-- Optional trigger or helper view for counts
CREATE OR REPLACE VIEW user_follow_stats AS
SELECT 
    u.id AS user_id,
    COALESCE(followers.cnt, 0) AS followers_count,
    COALESCE(following.cnt, 0) AS following_count
FROM users u
LEFT JOIN (
    SELECT following_id, COUNT(*) AS cnt 
    FROM user_follows 
    GROUP BY following_id
) followers ON u.id = followers.following_id
LEFT JOIN (
    SELECT follower_id, COUNT(*) AS cnt 
    FROM user_follows 
    GROUP BY follower_id
) following ON u.id = following.follower_id;
