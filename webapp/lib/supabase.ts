
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

// Helper to log AI usage
export async function logAIUsage(
    orgId: string,
    feature: string,
    model: string,
    inputTokens: number,
    outputTokens: number,
    cost: number,
    meta?: any
) {
    if (!orgId) return;

    const { error } = await supabase.from('ai_usage_logs').insert({
        org_id: orgId,
        feature_name: feature,
        model_used: model,
        input_tokens: inputTokens,
        output_tokens: outputTokens,
        cost_usd: cost,
        metadata: meta
    });

    if (error) console.error("Failed to log AI usage:", error);
}
