import { NextRequest, NextResponse } from "next/server";
import { supabase, logAIUsage } from "@/lib/supabase";


// 1. GET: List all documents for an Org
export async function GET(req: NextRequest) {
    const { searchParams } = new URL(req.url);
    const orgId = searchParams.get('orgId');

    if (!orgId) return NextResponse.json({ success: false, error: "Missing orgId" }, { status: 400 });

    try {
        // Fetch from Supabase
        const { data, error } = await supabase
            .from('knowledge_documents')
            .select('*')
            .eq('org_id', orgId)
            .order('created_at', { ascending: false });

        if (error) throw error;

        return NextResponse.json({ success: true, data: data || [] });

    } catch (e: any) {
        console.error("Supabase fetch failed:", e);
        return NextResponse.json({ success: false, error: "Fetch failed" }, { status: 500 });
    }
}

// 2. POST: Upload a new document
export async function POST(req: NextRequest) {
    try {
        const formData = await req.formData();
        const file = formData.get('file') as File;
        const orgId = formData.get('orgId') as string;

        if (!file || !orgId) {
            return NextResponse.json({ success: false, error: "Missing file or orgId" }, { status: 400 });
        }

        const fileName = file.name;
        // In a real app, we would upload the binary to S3/Supabase Storage.
        // For this "Workable POC", we will store the Metadata + Mock Indexing status.

        const docRecord = {
            org_id: orgId,
            filename: fileName,
            file_url: "stored_internally", // Placeholder
            status: "Indexed", // Auto-mark as indexed for demo
            size: `${(file.size / 1024).toFixed(2)} KB`
        };

        let finalId = crypto.randomUUID(); // Fallback ID

        // Attempt Supabase Write

        // Ensure Org Exists First (Prevent FK Error)
        const { error: orgError } = await supabase.from('organizations').upsert({
            id: orgId,
            name: "Demo Organization"
        }, { onConflict: 'id' });

        if (orgError) console.warn("Could not upsert org, doc insert might fail:", orgError);

        const { data, error } = await supabase.from('knowledge_documents').insert(docRecord).select().single();
        if (error) {
            console.error("Supabase insert failed", error);
            throw error;
        }
        if (data) finalId = data.id;

        // Log AI Usage
        await logAIUsage(
            orgId,
            "DocumentEmbedding",
            "text-embedding-3-small",
            Math.ceil(file.size / 4),
            0,
            0.0001,
            { filename: fileName }
        );

        return NextResponse.json({ success: true, data: { ...docRecord, id: finalId } });

    } catch (e) {
        return NextResponse.json({ success: false, error: "Upload failed" }, { status: 500 });
    }
}
