import type { FilterState, SitePersonRow, WeightMode } from "../types";

export function stringValue(row: SitePersonRow, field: string): string {
  const value = row[field];
  if (value === null || value === undefined) {
    return "";
  }
  return String(value);
}

export function numberValue(row: SitePersonRow, field: string): number | null {
  const value = row[field];
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function weightForRow(row: SitePersonRow, weightMode: WeightMode): number {
  if (weightMode === "unweighted") {
    return 1;
  }
  return numberValue(row, "perwt23f") ?? 0;
}

export function applyFilters(rows: SitePersonRow[], filters: FilterState): SitePersonRow[] {
  return rows.filter((row) => {
    if (filters.insurance !== "all" && stringValue(row, "inscov23") !== filters.insurance) {
      return false;
    }
    if (filters.poverty !== "all" && stringValue(row, "povcat23") !== filters.poverty) {
      return false;
    }
    if (filters.region !== "all" && stringValue(row, "region23") !== filters.region) {
      return false;
    }
    if (filters.ageBand !== "all" && stringValue(row, "age_band") !== filters.ageBand) {
      return false;
    }
    if (filters.student === "focus17_23" && numberValue(row, "age_focus_17_23") !== 1) {
      return false;
    }
    if (filters.student === "full_time" && stringValue(row, "ftstu23x") !== "1") {
      return false;
    }
    if (filters.student === "part_time" && stringValue(row, "ftstu23x") !== "2") {
      return false;
    }
    if (filters.student === "not_student" && stringValue(row, "ftstu23x") !== "3") {
      return false;
    }
    if (filters.affordability === "barrier" && numberValue(row, "afford_any") !== 1) {
      return false;
    }
    if (filters.affordability === "no_barrier" && numberValue(row, "can_afford_all") !== 1) {
      return false;
    }
    if (filters.affordability === "unknown" && numberValue(row, "afford_any") !== null) {
      return false;
    }
    if (filters.delay === "delayed" && numberValue(row, "delay_any") !== 1) {
      return false;
    }
    if (filters.delay === "not_delayed" && numberValue(row, "delay_any") !== 0) {
      return false;
    }
    if (filters.delay === "unknown" && numberValue(row, "delay_any") !== null) {
      return false;
    }
    if (filters.lowRisk === "low_risk" && numberValue(row, "low_risk") !== 1) {
      return false;
    }
    if (filters.lowRisk === "not_low_risk" && numberValue(row, "low_risk") !== 0) {
      return false;
    }
    return true;
  });
}

export function weightedTotal(rows: SitePersonRow[], weightMode: WeightMode): number {
  return rows.reduce((sum, row) => sum + weightForRow(row, weightMode), 0);
}

export function weightedMean(
  rows: SitePersonRow[],
  field: string,
  weightMode: WeightMode,
): number | null {
  let weightTotal = 0;
  let weightedValue = 0;
  for (const row of rows) {
    const value = numberValue(row, field);
    if (value === null) {
      continue;
    }
    const weight = weightForRow(row, weightMode);
    weightTotal += weight;
    weightedValue += value * weight;
  }
  if (weightTotal === 0) {
    return null;
  }
  return weightedValue / weightTotal;
}

export function weightedQuantile(
  rows: SitePersonRow[],
  field: string,
  quantile: number,
  weightMode: WeightMode,
): number | null {
  const points = rows
    .map((row) => ({
      value: numberValue(row, field),
      weight: weightForRow(row, weightMode),
    }))
    .filter((point) => point.value !== null && point.weight > 0) as Array<{
      value: number;
      weight: number;
    }>;

  if (points.length === 0) {
    return null;
  }

  points.sort((left, right) => left.value - right.value);
  const totalWeight = points.reduce((sum, point) => sum + point.weight, 0);
  const target = totalWeight * quantile;
  let cumulative = 0;
  for (const point of points) {
    cumulative += point.weight;
    if (cumulative >= target) {
      return point.value;
    }
  }
  return points.at(-1)?.value ?? null;
}

export function weightedFiveNumber(
  rows: SitePersonRow[],
  field: string,
  weightMode: WeightMode,
): [number, number, number, number, number] | null {
  const min = weightedQuantile(rows, field, 0, weightMode);
  const q1 = weightedQuantile(rows, field, 0.25, weightMode);
  const median = weightedQuantile(rows, field, 0.5, weightMode);
  const q3 = weightedQuantile(rows, field, 0.75, weightMode);
  const max = weightedQuantile(rows, field, 1, weightMode);
  if ([min, q1, median, q3, max].some((value) => value === null)) {
    return null;
  }
  return [min!, q1!, median!, q3!, max!];
}

export function histogramBins(
  rows: SitePersonRow[],
  field: string,
  weightMode: WeightMode,
  binCount = 10,
): Array<{ label: string; low: number; high: number; total: number }> {
  const values = rows
    .map((row) => ({
      value: numberValue(row, field),
      weight: weightForRow(row, weightMode),
    }))
    .filter((item) => item.value !== null && item.weight > 0) as Array<{
      value: number;
      weight: number;
    }>;

  if (values.length === 0) {
    return [];
  }

  const max = Math.max(...values.map((item) => item.value));
  const min = Math.min(...values.map((item) => item.value));

  if (max === min) {
    return [
      {
        label: `${min}`,
        low: min,
        high: max,
        total: values.reduce((sum, item) => sum + item.weight, 0),
      },
    ];
  }

  const span = max - min;
  const step = span / binCount;
  const bins = Array.from({ length: binCount }, (_, index) => ({
    low: min + step * index,
    high: index === binCount - 1 ? max : min + step * (index + 1),
    total: 0,
    label: "",
  }));

  for (const item of values) {
    const rawIndex = Math.floor((item.value - min) / step);
    const index = Math.min(rawIndex, binCount - 1);
    bins[index].total += item.weight;
  }

  return bins.map((bin) => ({
    ...bin,
    label: `${Math.round(bin.low).toLocaleString()}-${Math.round(bin.high).toLocaleString()}`,
  }));
}
