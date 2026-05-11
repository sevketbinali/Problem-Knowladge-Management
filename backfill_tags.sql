UPDATE problem_records SET tags = '["sl4 migrasyon", "firewall", "cluster migration", "vlan tagging"]' WHERE tags IS NULL OR tags = '[]'::jsonb;
UPDATE sessions SET tags = '["sl4 migrasyon", "firewall", "cluster migration", "vlan tagging"]' WHERE tags IS NULL OR tags = '[]'::jsonb;
