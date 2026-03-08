import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";


export async function GET(req: NextRequest) {
    try {
        // Fetch from Supabase
        const { data, error } = await supabase.from('organizations').select('id, name');

        if (error) throw error;

        if (data && data.length > 0) {
            // Map to frontend format
            return NextResponse.json(data.map(org => ({
                id: org.id,
                name: org.name || "Unnamed Org",
                slug: org.id
            })));
        }

        // Return empty list if no organizations found
        return NextResponse.json([]);

    } catch (e: any) {
        console.error("Supabase fetch failed:", e);
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
