import Papa from "papaparse";

import type { Metadata, SitePersonRow } from "../types";

const dataUrl = (fileName: string) => `${import.meta.env.BASE_URL}data/${fileName}`;

const NUMERIC_FIELDS = new Set([
  "perwt23f",
  "agelast",
  "age_focus_17_23",
  "afford_any",
  "delay_any",
  "can_afford_all",
  "cost_reason_no_usc",
  "totexp23",
  "totslf23",
  "totprv23",
  "totmcr23",
  "totmcd23",
  "oop_share",
  "faminc23",
  "family_income_quintile",
  "educyr",
  "obtotv23",
  "ertot23",
  "ipdis23",
  "rxtot23",
  "low_risk",
  "low_spend",
  "cata_10k",
  "cata_20k",
  "chronic_ct",
  "limit_ct",
  "nonacute_util_ct",
  "acute_util_any",
]);

function parseValue(key: string, value: string): string | number | null {
  if (value === "") {
    return null;
  }
  if (NUMERIC_FIELDS.has(key)) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : null;
  }
  return value;
}

export async function loadMetadata(): Promise<Metadata> {
  const response = await fetch(dataUrl("metadata.json"));
  if (!response.ok) {
    throw new Error(`Failed to load metadata.json: ${response.status}`);
  }
  return (await response.json()) as Metadata;
}

export async function loadRows(): Promise<SitePersonRow[]> {
  const response = await fetch(dataUrl("people.csv"));
  if (!response.ok) {
    throw new Error(`Failed to load people.csv: ${response.status}`);
  }
  const csvText = await response.text();
  const parsed = Papa.parse<Record<string, string>>(csvText, {
    header: true,
    skipEmptyLines: true,
  });
  if (parsed.errors.length > 0) {
    throw new Error(parsed.errors[0]?.message ?? "Failed to parse people.csv");
  }
  return parsed.data.map((row) => {
    const normalized: SitePersonRow = {};
    for (const [key, value] of Object.entries(row)) {
      normalized[key] = parseValue(key, value ?? "");
    }
    return normalized;
  });
}
