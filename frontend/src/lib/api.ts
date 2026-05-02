export type Source = {
  title?: string | null;
  url: string;
  snippet?: string | null;
};

export type FinalAnswer = {
  answer: string;
  sources: Source[];
  confidence: "low" | "medium" | "high";
  what_was_verified: string[];
  what_could_not_be_verified: string[];
};

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
