import { NextRequest, NextResponse } from "next/server";
import { supabase, logAIUsage } from "@/lib/supabase";

// Force dynamic ensures this route isn't statically cached
export const dynamic = 'force-dynamic';

// Configuration
const BACKEND_URL = process.env.NEXT_PUBLIC_APP_BACKEND_URL;

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { message, orgId = "default_org", filters } = body;

        // 1. Fetch Context (Identity)
        let identity = { name: "The Company", usp: "General Business", tone: "Professional" };

        try {
            const { data: orgData } = await supabase.from('organizations').select('*').eq('id', orgId).single();
            if (orgData) {
                identity = {
                    name: orgData.name || "The Company",
                    usp: orgData.identity_data?.usp || "General Business",
                    tone: orgData.identity_data?.tone || "Professional"
                };
            }
        } catch (e) {
            console.warn("Supabase Error during context fetch:", e);
        }

        // 2. Call Hugging Face Backend (Deep RAG)
        let aiResponseText = "";
        let sourcesUsed: any[] = [];
        let vizData = null;

        if (!BACKEND_URL) {
            console.warn("NEXT_PUBLIC_APP_BACKEND_URL is not set. Using fallback mock response.");
            aiResponseText = "System Configuration Error: Backend URL not set. Please configure the integration.";
        } else {
            try {
                // Determine API Endpoint (proxy to HF Space)
                // If the URL ends with / (e.g. https://space.hf.space/), trim it
                const baseUrl = BACKEND_URL.replace(/\/$/, "");
                const apiUrl = `${baseUrl}/api/v1/query`;

                console.log(`[Proxy] Forwarding query to: ${apiUrl}`);

                const backendResponse = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: message,
                        organization_id: orgId,
                        filters: filters || {}
                    })
                });

                if (!backendResponse.ok) {
                    throw new Error(`Backend API Error: ${backendResponse.statusText}`);
                }

                const data = await backendResponse.json();

                // Parse Response from Backend
                aiResponseText = data.answer;
                sourcesUsed = data.sources || [];
                vizData = data.viz_data;

            } catch (apiError) {
                console.error("HF Backend Call Failed:", apiError);
                aiResponseText = `I am currently unable to reach the neural core. Please check the backend connection. (Internal Error: ${apiError instanceof Error ? apiError.message : String(apiError)})`;
                // This file is unused if we call Python directly, BUT wait.
                // The frontend calls `api` which defaults to `/api`.
                // We need to check if there is a Next.js route for `/orgs`?
                // `webapp/lib/api.ts` -> `const API_BASE_URL = ... || "/api"`.
                // Wait, `queryAdhi` calls `/query`. That maps to `app/api/query/route.ts`? NO.
                // `queryAdhi` in `lib/api.ts` calls `/query`.
                // But `ManagerConsole` calls `/api/chat/manager`.
                // There is an inconsistency in the codebase.
                // `lib/api.ts` assumes a direct backend connection OR a Next.js proxy.
                // If valid Next.js routes don't exist, we must add them.
            }
        }

        // 3. Log Tokens (Estimated)
        await logAIUsage(
            orgId,
            "ManagerChat",
            "mixtral-8x7b", // or whatever model is behind the API
            500 + aiResponseText.length / 4,
            150,
            0.00, // Open Source = Free (or low cost)
            {
                message_fragment: message.substring(0, 20),
                provider: "huggingface",
                backend_url: BACKEND_URL
            }
        );

        // 4. Return
        return NextResponse.json({
            success: true,
            role: "ai",
            text: aiResponseText,
            timestamp: new Date().toISOString(),
            sources: sourcesUsed,
            viz: vizData,
            context_used: { identity_usp: identity.usp }
        });

    } catch (e) {
        console.error("Chat API Error:", e);
        return NextResponse.json({
            success: false,
            role: "ai",
            text: "I encountered a synchronization error. Please try again.",
            timestamp: new Date().toISOString()
        }, { status: 500 });
    }
}
