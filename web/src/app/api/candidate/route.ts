import { NextResponse } from "next/server";
import { readFile } from "node:fs/promises";
import path from "node:path";

export async function GET() {
  const filePath = path.join(
    process.cwd(),
    "..",
    "data",
    "candidate",
    "profile.json",
  );

  const file = await readFile(filePath, "utf-8");
  const data = JSON.parse(file);

  return NextResponse.json(data);
}
