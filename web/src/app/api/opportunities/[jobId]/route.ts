import { NextResponse } from "next/server";
import { readFile } from "node:fs/promises";
import path from "node:path";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ jobId: string }> },
) {
  const { jobId } = await params;

  const filePath = path.join(
    process.cwd(),
    "..",
    "data",
    "jobs",
    "ranked_opportunities.json",
  );

  const file = await readFile(filePath, "utf-8");
  const data = JSON.parse(file);

  const opportunity = data.opportunities.find(
    (item: { job_id: string }) => item.job_id === jobId,
  );

  if (!opportunity) {
    return NextResponse.json(
      { error: "Opportunity not found" },
      { status: 404 },
    );
  }

  return NextResponse.json(opportunity);
}
