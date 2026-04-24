-- Admin view: one row per user with plan, renewal date, upsell/cross-sell aggregates.
-- Safe to run repeatedly; CREATE OR REPLACE makes this idempotent.
-- Requires PostgreSQL (LATERAL join).

CREATE OR REPLACE VIEW admin_user_overview AS
SELECT
    u.uid                              AS uid,
    u.name                             AS name,
    u.email                            AS email,
    u.phone_number                     AS phone_number,
    p.name                             AS plan_name,
    CAST(s.status AS VARCHAR)          AS subscription_status,
    CAST(s.billing_cycle AS VARCHAR)   AS billing_cycle,
    s.current_period_end               AS plan_renewal_date,
    s.auto_renew                       AS auto_renew,
    COALESCE(up.shown_upsell, 0)       AS upsell_offers_shown,
    COALESCE(up.accepted_upsell, 0)    AS upsell_offers_accepted,
    COALESCE(up.shown_cross, 0)        AS cross_sell_offers_shown,
    COALESCE(up.accepted_cross, 0)     AS cross_sell_offers_accepted,
    COALESCE(up.total_revenue, 0)      AS total_upsell_revenue,
    u.created_at                       AS user_created_at
FROM users u
LEFT JOIN plans p ON p.id = u.plan_id
LEFT JOIN LATERAL (
    SELECT *
    FROM subscriptions s2
    WHERE s2.user_uid = u.uid
    ORDER BY s2.started_at DESC
    LIMIT 1
) s ON TRUE
LEFT JOIN (
    SELECT
        user_uid,
        SUM(CASE WHEN offer_type = 'upsell' THEN 1 ELSE 0 END)                              AS shown_upsell,
        SUM(CASE WHEN offer_type = 'upsell' AND outcome = 'accepted' THEN 1 ELSE 0 END)     AS accepted_upsell,
        SUM(CASE WHEN offer_type = 'cross_sell' THEN 1 ELSE 0 END)                          AS shown_cross,
        SUM(CASE WHEN offer_type = 'cross_sell' AND outcome = 'accepted' THEN 1 ELSE 0 END) AS accepted_cross,
        SUM(COALESCE(revenue_amount, 0))                                                    AS total_revenue
    FROM upsell_cross_sell
    GROUP BY user_uid
) up ON up.user_uid = u.uid
ORDER BY u.created_at DESC;
