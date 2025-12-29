-- Add referral columns to organizations
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS referral_code VARCHAR(12) UNIQUE;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS bonus_optimizations INTEGER DEFAULT 0;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS total_referrals INTEGER DEFAULT 0;

-- Add referred_by to users
ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by_org_id UUID REFERENCES organizations(id) ON DELETE SET NULL;

-- Create referrals table
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    referred_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    referrer_reward INTEGER DEFAULT 50,
    referee_reward INTEGER DEFAULT 25,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on referral_code for fast lookups
CREATE INDEX IF NOT EXISTS idx_organizations_referral_code ON organizations(referral_code);
