import type { EChartsOption } from "echarts";

import {
  histogramBins,
  numberValue,
  stringValue,
  weightForRow,
  weightedFiveNumber,
  weightedMean,
  weightedQuantile,
  weightedTotal,
} from "./lib/analysis";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  formatPopulation,
} from "./lib/format";
import type {
  FilterState,
  Metadata,
  QuestionResult,
  QuestionSpec,
  SitePersonRow,
} from "./types";

const COLORS = {
  ink: "#231a18",
  panel: "#fff8ef",
  accent: "#c55d3d",
  accentSoft: "#eac1b1",
  forest: "#547762",
  gold: "#c08f2d",
  slate: "#4f6078",
  rose: "#ba6d7d",
  fog: "#d7cec2",
  muted: "#7c6c63",
  unavailable: "#b88376",
};

const METRIC_LABELS: Record<string, { label: string; formatter: (value: number) => string }> =
  {
    totexp23: { label: "Annual total spend", formatter: formatCurrency },
    totslf23: { label: "Annual out-of-pocket spend", formatter: formatCurrency },
    obtotv23: { label: "Office-based visits", formatter: formatNumber },
    ertot23: { label: "ER visits", formatter: formatNumber },
    ipdis23: { label: "Inpatient discharges", formatter: formatNumber },
    rxtot23: { label: "Prescriptions filled", formatter: formatNumber },
    oop_share: { label: "Out-of-pocket share", formatter: (value) => formatPercent(value, 1) },
    chronic_ct: { label: "Chronic condition count", formatter: formatNumber },
    limit_ct: { label: "Functional limitation count", formatter: formatNumber },
    nonacute_util_ct: { label: "Non-acute utilization count", formatter: formatNumber },
  };

const AGE_BAND_ORDER = ["0-17", "18-25", "26-34", "35-44", "45-54", "55-64", "65+"];
const EDUCATION_ORDER = [
  "Less than high school",
  "High school",
  "Some college",
  "Bachelor",
  "Graduate",
];
const EMPLOYMENT_ORDER = [
  "Employed at interview date",
  "Has a job to return to",
  "Unemployed",
  "Not employed during round",
];
const STUDENT_ORDER = ["Full-time student", "Part-time student", "Not a student"];
const RACE_ORDER = ["1", "2", "3", "4", "5"];

function getQuestionMeta(metadata: Metadata, id: string) {
  const match = metadata.questions.find((question) => question.id === id);
  if (!match) {
    throw new Error(`Missing metadata for question ${id}`);
  }
  return match;
}

function fieldLabel(metadata: Metadata, field: string, value: string | number) {
  return (
    metadata.valueLabels[field]?.[String(value)] ??
    metadata.valueLabels[field.toUpperCase()]?.[String(value)] ??
    String(value)
  );
}

function baseTextStyle() {
  return {
    fontFamily: "Instrument Sans, sans-serif",
    color: COLORS.ink,
  };
}

function barOption(params: {
  categories: string[];
  values: number[];
  seriesName: string;
  color?: string;
  yAxisLabel?: string;
  valueFormatter?: (value: unknown) => string;
}): EChartsOption {
  return {
    animationDuration: 400,
    grid: { left: 58, right: 18, top: 20, bottom: 48, containLabel: true },
    textStyle: baseTextStyle(),
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      valueFormatter: params.valueFormatter as ((value: unknown) => string) | undefined,
    },
    xAxis: {
      type: "category",
      data: params.categories,
      axisLabel: { color: COLORS.ink, interval: 0, rotate: params.categories.length > 6 ? 20 : 0 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: COLORS.fog } },
    },
    yAxis: {
      type: "value",
      name: params.yAxisLabel,
      nameTextStyle: { color: COLORS.muted, padding: [0, 0, 8, 0] },
      axisLabel: {
        color: COLORS.muted,
        formatter: (value: number) =>
          params.valueFormatter ? params.valueFormatter(value) : formatNumber(value),
      },
      splitLine: { lineStyle: { color: "#ebdfd4" } },
    },
    series: [
      {
        type: "bar",
        name: params.seriesName,
        data: params.values,
        itemStyle: {
          color: params.color ?? COLORS.accent,
          borderRadius: [10, 10, 0, 0],
        },
        emphasis: { focus: "series" },
      },
    ],
  };
}

function stackedOption(params: {
  categories: string[];
  yesValues: number[];
  noValues: number[];
  yesLabel: string;
  noLabel: string;
}): EChartsOption {
  return {
    animationDuration: 400,
    grid: { left: 52, right: 18, top: 16, bottom: 54, containLabel: true },
    textStyle: baseTextStyle(),
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      valueFormatter: ((value: unknown) => formatPercent(Number(value))) as (
        value: unknown,
      ) => string,
    },
    legend: {
      bottom: 0,
      textStyle: { color: COLORS.muted, fontFamily: "Instrument Sans, sans-serif" },
    },
    xAxis: {
      type: "category",
      data: params.categories,
      axisLabel: { color: COLORS.ink, interval: 0, rotate: params.categories.length > 5 ? 18 : 0 },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      max: 1,
      axisLabel: { formatter: (value: number) => formatPercent(value), color: COLORS.muted },
      splitLine: { lineStyle: { color: "#ebdfd4" } },
    },
    series: [
      {
        type: "bar",
        stack: "share",
        name: params.yesLabel,
        data: params.yesValues,
        itemStyle: { color: COLORS.accent, borderRadius: [8, 8, 0, 0] },
      },
      {
        type: "bar",
        stack: "share",
        name: params.noLabel,
        data: params.noValues,
        itemStyle: { color: COLORS.fog, borderRadius: [8, 8, 0, 0] },
      },
    ],
  };
}

function donutOption(slices: Array<{ name: string; value: number; color: string }>): EChartsOption {
  return {
    animationDuration: 400,
    textStyle: baseTextStyle(),
    tooltip: {
      trigger: "item",
      valueFormatter: ((value: unknown) => formatPopulation(Number(value))) as (
        value: unknown,
      ) => string,
      formatter: ((params: any) =>
        `${params.name}<br/>${formatPopulation(params.value)}<br/>${params.percent.toFixed(1)}%`) as any,
    },
    legend: {
      bottom: 0,
      textStyle: { color: COLORS.muted, fontFamily: "Instrument Sans, sans-serif" },
    },
    series: [
      {
        type: "pie",
        radius: ["45%", "72%"],
        center: ["50%", "44%"],
        label: { color: COLORS.ink, formatter: "{b}\n{d}%" },
        data: slices.map((slice) => ({
          name: slice.name,
          value: slice.value,
          itemStyle: { color: slice.color },
        })),
      },
    ],
  };
}

function lineOption(categories: string[], values: number[], seriesName: string): EChartsOption {
  return {
    animationDuration: 400,
    grid: { left: 52, right: 18, top: 20, bottom: 46, containLabel: true },
    textStyle: baseTextStyle(),
    tooltip: {
      trigger: "axis",
      valueFormatter: ((value: unknown) => formatPercent(Number(value))) as (
        value: unknown,
      ) => string,
    },
    xAxis: {
      type: "category",
      data: categories,
      axisLabel: { color: COLORS.ink },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      max: 1,
      axisLabel: { formatter: (value: number) => formatPercent(value), color: COLORS.muted },
      splitLine: { lineStyle: { color: "#ebdfd4" } },
    },
    series: [
      {
        type: "line",
        name: seriesName,
        data: values,
        smooth: true,
        symbolSize: 9,
        lineStyle: { width: 3, color: COLORS.slate },
        itemStyle: { color: COLORS.slate },
        areaStyle: { color: "rgba(79, 96, 120, 0.12)" },
      },
    ],
  };
}

function boxOption(params: {
  categories: string[];
  values: Array<[number, number, number, number, number]>;
  metricField: string;
}): EChartsOption {
  const formatter = METRIC_LABELS[params.metricField]?.formatter ?? formatNumber;
  return {
    animationDuration: 400,
    grid: { left: 58, right: 18, top: 20, bottom: 52, containLabel: true },
    textStyle: baseTextStyle(),
    tooltip: {
      trigger: "item",
      formatter: ((paramsValue: any) => {
        const [min, q1, median, q3, max] = paramsValue.data;
        return [
          `<strong>${paramsValue.name}</strong>`,
          `Min: ${formatter(min)}`,
          `Q1: ${formatter(q1)}`,
          `Median: ${formatter(median)}`,
          `Q3: ${formatter(q3)}`,
          `Max: ${formatter(max)}`,
        ].join("<br/>");
      }) as any,
    },
    xAxis: {
      type: "category",
      data: params.categories,
      axisLabel: { color: COLORS.ink, interval: 0, rotate: params.categories.length > 4 ? 16 : 0 },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: COLORS.muted, formatter: (value: number) => formatter(value) },
      splitLine: { lineStyle: { color: "#ebdfd4" } },
    },
    series: [
      {
        type: "boxplot",
        data: params.values,
        itemStyle: {
          color: COLORS.accentSoft,
          borderColor: COLORS.accent,
          borderWidth: 2,
        },
      },
    ],
  };
}

function funnelOption(stages: Array<{ name: string; value: number }>): EChartsOption {
  return {
    animationDuration: 400,
    textStyle: baseTextStyle(),
    tooltip: {
      trigger: "item",
      formatter: ((params: any) => `${params.name}<br/>${formatPopulation(params.value)}`) as any,
    },
    series: [
      {
        type: "funnel",
        top: 12,
        bottom: 24,
        left: "12%",
        width: "76%",
        minSize: "32%",
        maxSize: "100%",
        gap: 10,
        sort: "descending",
        label: {
          color: COLORS.ink,
          formatter: ((params: any) => `${params.name}\n${formatPopulation(params.value)}`) as any,
        },
        itemStyle: {
          borderColor: COLORS.panel,
          borderWidth: 3,
        },
        data: stages.map((stage, index) => ({
          ...stage,
          itemStyle: {
            color: [COLORS.slate, COLORS.forest, COLORS.accent][index] ?? COLORS.gold,
          },
        })),
      },
    ],
  };
}

function unavailableOption(): EChartsOption {
  return {
    grid: { left: 40, right: 40, top: 34, bottom: 28 },
    xAxis: {
      type: "value",
      max: 100,
      axisLabel: { formatter: "{value}%", color: COLORS.muted },
      splitLine: { lineStyle: { color: "#ebdfd4" } },
    },
    yAxis: {
      type: "category",
      data: ["Dataset coverage"],
      axisLabel: { color: COLORS.ink },
      axisTick: { show: false },
    },
    series: [
      {
        type: "bar",
        stack: "coverage",
        data: [0],
        name: "Directly available",
        itemStyle: { color: COLORS.forest },
      },
      {
        type: "bar",
        stack: "coverage",
        data: [100],
        name: "Not directly in MEPS",
        itemStyle: { color: COLORS.unavailable, borderRadius: [10, 10, 10, 10] },
        label: {
          show: true,
          position: "inside",
          formatter: "0% direct",
          color: "#fff8ef",
          fontWeight: 700,
        },
      },
    ],
  };
}

function filteredBinaryRows(rows: SitePersonRow[], field: string) {
  const valid = rows.filter((row) => {
    const value = stringValue(row, field);
    return value === "1" || value === "2" || value === "0";
  });
  return { valid, excludedCount: rows.length - valid.length };
}

function binaryValue(row: SitePersonRow, field: string): number | null {
  const raw = row[field];
  if (raw === 1 || raw === "1") {
    return 1;
  }
  if (raw === 0 || raw === "0" || raw === "2") {
    return 0;
  }
  return null;
}

function collectByCategory(
  rows: SitePersonRow[],
  categoryField: string,
  weightMode: FilterState["weightMode"],
  options?: {
    categoryOrder?: string[];
    include?: (category: string) => boolean;
  },
) {
  const totals = new Map<string, number>();
  for (const row of rows) {
    const category = stringValue(row, categoryField);
    if (!category) {
      continue;
    }
    if (options?.include && !options.include(category)) {
      continue;
    }
    totals.set(category, (totals.get(category) ?? 0) + weightForRow(row, weightMode));
  }
  const categories = options?.categoryOrder
    ? options.categoryOrder.filter((category) => totals.has(category))
    : Array.from(totals.keys());
  return categories.map((category) => ({
    category,
    total: totals.get(category) ?? 0,
  }));
}

function buildBinaryBarQuestion(id: string, field: string): QuestionSpec {
  return {
    id,
    build: ({ rows, metadata, filters }) => {
      const { valid, excludedCount } = filteredBinaryRows(rows, field);
      const yes = valid
        .filter((row) => binaryValue(row, field) === 1)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const no = valid
        .filter((row) => binaryValue(row, field) === 0)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const total = yes + no;
      const yesShare = total === 0 ? 0 : yes / total;
      return {
        option: barOption({
          categories: [fieldLabel(metadata, field, 1), fieldLabel(metadata, field, 2)],
          values: [yes, no],
          seriesName: "Population estimate",
          color: COLORS.accent,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference: `Under the current filters, ${filters.weightMode === "weighted" ? "an estimated" : ""} ${filters.weightMode === "weighted" ? formatPopulation(yes) : formatNumber(yes)} people answered Yes, which is ${formatPercent(yesShare)} of valid responses.`,
        excludedCount,
        validCount: valid.length,
      };
    },
  };
}

function buildCompositeDonutQuestion(id: string, field: string, yesLabel: string, noLabel: string): QuestionSpec {
  return {
    id,
    build: ({ rows, filters }) => {
      const valid = rows.filter((row) => numberValue(row, field) !== null);
      const yes = valid
        .filter((row) => numberValue(row, field) === 1)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const no = valid
        .filter((row) => numberValue(row, field) === 0)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const total = yes + no;
      const yesShare = total === 0 ? 0 : yes / total;
      return {
        option: donutOption([
          { name: yesLabel, value: yes, color: COLORS.accent },
          { name: noLabel, value: no, color: COLORS.fog },
        ]),
        inference: `${filters.weightMode === "weighted" ? "An estimated" : ""} ${filters.weightMode === "weighted" ? formatPopulation(yes) : formatNumber(yes)} people fall into the ${yesLabel.toLowerCase()} group, equal to ${formatPercent(yesShare)} of valid respondents under the current filters.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildHistogramQuestion(id: string, metricField: string, subset: (row: SitePersonRow) => boolean): QuestionSpec {
  return {
    id,
    build: ({ rows, filters }) => {
      const subsetRows = rows.filter(subset);
      const valid = subsetRows.filter((row) => numberValue(row, metricField) !== null);
      const bins = histogramBins(valid, metricField, filters.weightMode, 10);
      const values = bins.map((bin) => bin.total);
      const median = weightedQuantile(valid, metricField, 0.5, filters.weightMode);
      const p75 = weightedQuantile(valid, metricField, 0.75, filters.weightMode);
      const metric = METRIC_LABELS[metricField];
      return {
        option: barOption({
          categories: bins.map((bin) => bin.label),
          values,
          seriesName: metric.label,
          color: COLORS.slate,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          median === null || p75 === null
            ? "No valid values remain after the current filters."
            : `Within this cohort, the weighted median ${metric.label.toLowerCase()} is ${metric.formatter(median)} and the 75th percentile is ${metric.formatter(p75)}, showing how concentrated the upper tail becomes after affordability filters are applied.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildMetricComparisonQuestion(id: string, cohortField: string): QuestionSpec {
  const modes = [
    { id: "totexp23", label: "Total spend" },
    { id: "totslf23", label: "Out-of-pocket spend" },
    { id: "obtotv23", label: "Office visits" },
    { id: "ertot23", label: "ER visits" },
    { id: "ipdis23", label: "Inpatient discharges" },
    { id: "rxtot23", label: "Prescriptions" },
  ];
  return {
    id,
    modes,
    defaultMode: "totexp23",
    build: ({ rows, filters, mode }) => {
      const valid = rows.filter(
        (row) => numberValue(row, cohortField) !== null && numberValue(row, mode) !== null,
      );
      const withFlag = valid.filter((row) => numberValue(row, cohortField) === 1);
      const withoutFlag = valid.filter((row) => numberValue(row, cohortField) === 0);
      const metric = METRIC_LABELS[mode];
      const withBox = weightedFiveNumber(withFlag, mode, filters.weightMode);
      const withoutBox = weightedFiveNumber(withoutFlag, mode, filters.weightMode);
      if (!withBox || !withoutBox) {
        return {
          inference: "No valid comparison remains under the current filters.",
          excludedCount: rows.length - valid.length,
          validCount: valid.length,
          emptyState: "No valid comparison remains under the current filters.",
        };
      }
      const withMedian = weightedQuantile(withFlag, mode, 0.5, filters.weightMode) ?? 0;
      const withoutMedian = weightedQuantile(withoutFlag, mode, 0.5, filters.weightMode) ?? 0;
      return {
        option: boxOption({
          categories: ["Affordability barrier", "No affordability barrier"],
          values: [withBox, withoutBox],
          metricField: mode,
        }),
        inference: `For ${metric.label.toLowerCase()}, the weighted median is ${metric.formatter(withMedian)} for people with an affordability barrier versus ${metric.formatter(withoutMedian)} for those without one.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildStackedRateQuestion(
  id: string,
  categoryField: string,
  binaryField: string,
  categoryOrder?: string[],
  rowSubset?: (row: SitePersonRow) => boolean,
  seriesLabels: { yes: string; no: string; subject: string } = {
    yes: "Affordability barrier",
    no: "No barrier",
    subject: "affordability-barrier",
  },
): QuestionSpec {
  return {
    id,
    build: ({ rows, metadata, filters }) => {
      const subsetRows = rowSubset ? rows.filter(rowSubset) : rows;
      const valid = subsetRows.filter(
        (row) =>
          stringValue(row, categoryField) !== "" && numberValue(row, binaryField) !== null,
      );
      const categories = collectByCategory(valid, categoryField, filters.weightMode, {
        categoryOrder,
      });
      const yesValues: number[] = [];
      const noValues: number[] = [];
      for (const category of categories) {
        const group = valid.filter(
          (row) => stringValue(row, categoryField) === category.category,
        );
        const total = weightedTotal(group, filters.weightMode);
        const yes = group
          .filter((row) => numberValue(row, binaryField) === 1)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
        yesValues.push(total === 0 ? 0 : yes / total);
        noValues.push(total === 0 ? 0 : 1 - yes / total);
      }
      const maxCategoryIndex = yesValues.reduce(
        (bestIndex, value, index, all) => (value > all[bestIndex] ? index : bestIndex),
        0,
      );
      return {
        option: stackedOption({
          categories: categories.map((category) =>
            fieldLabel(metadata, categoryField.toUpperCase(), category.category),
          ),
          yesValues,
          noValues,
          yesLabel: seriesLabels.yes,
          noLabel: seriesLabels.no,
        }),
        inference:
          categories.length === 0
            ? "No valid grouped responses remain after filtering."
            : `${fieldLabel(metadata, categoryField.toUpperCase(), categories[maxCategoryIndex].category)} shows the highest weighted ${seriesLabels.subject} rate at ${formatPercent(yesValues[maxCategoryIndex])} within the current filters.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildOrderedRateQuestion(
  id: string,
  categoryField: string,
  cohortField: string,
  categoryOrder: string[],
  categoryLabelField?: string,
  rowSubset?: (row: SitePersonRow) => boolean,
): QuestionSpec {
  return {
    id,
    build: ({ rows, filters }) => {
      const subsetRows = rowSubset ? rows.filter(rowSubset) : rows;
      const valid = subsetRows.filter(
        (row) =>
          stringValue(row, categoryField) !== "" && numberValue(row, cohortField) !== null,
      );
      const categories = categoryOrder.filter((category) =>
        valid.some((row) => stringValue(row, categoryField) === category),
      );
      const rates = categories.map((category) => {
        const group = valid.filter((row) => stringValue(row, categoryField) === category);
        const total = weightedTotal(group, filters.weightMode);
        const yes = group
          .filter((row) => numberValue(row, cohortField) === 1)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
        return total === 0 ? 0 : yes / total;
      });
      const maxRate = rates.length === 0 ? 0 : Math.max(...rates);
      const bestIndex = rates.findIndex((rate) => rate === maxRate);
      const displayLabels = categories.map((category) =>
        categoryLabelField
          ? stringValue(
              valid.find((row) => stringValue(row, categoryField) === category)!,
              categoryLabelField,
            )
          : category,
      );
      const minRate = rates.length === 0 ? 0 : Math.min(...rates);
      const lowestIndex = rates.findIndex((rate) => rate === minRate);
      const peakLabel = displayLabels[bestIndex];
      const lowLabel = displayLabels[lowestIndex];
      const peakRate = rates[bestIndex];
      return {
        option: barOption({
          categories: displayLabels,
          values: rates,
          seriesName: "Rate",
          color: COLORS.forest,
          yAxisLabel: "Rate",
          valueFormatter: (value) => formatPercent(Number(value)),
        }),
        inference:
          categories.length === 0
            ? "No valid responses remain after the current filters."
            : ({
                "afford-income-quintile": `${peakLabel} carries the highest weighted affordability-barrier rate at ${formatPercent(peakRate)}. Compare the full left-to-right slope to see how sharply barriers ease, or persist, as income rises.`,
                "afford-education": `${peakLabel} shows the highest weighted affordability-barrier rate at ${formatPercent(peakRate)}. Read the sequence from less schooling to more schooling as a descriptive education gradient, not a causal proof.`,
                "afford-race": `${peakLabel} shows the highest weighted affordability-barrier rate at ${formatPercent(peakRate)} under the current filters. The spread between groups is descriptive evidence about access differences, not a standalone explanation of why they exist.`,
                "delay-race": `${peakLabel} shows the highest weighted delayed-due-to-cost rate at ${formatPercent(peakRate)} under the current filters. Compare it with ${lowLabel} to see how delay risk varies across broad race groups.`,
                "education-delay-rate": `${peakLabel} has the highest weighted delayed-due-to-cost rate at ${formatPercent(peakRate)}. The pattern across education bands shows whether cost-related delay recedes or persists as educational attainment rises.`,
                "income-afford-rate": `${peakLabel} has the highest weighted affordability-barrier rate at ${formatPercent(peakRate)}. Compare it with ${lowLabel} to see how much relief appears higher up the income ladder.`,
                "low-risk-race": `${peakLabel} shows the highest weighted low-risk share at ${formatPercent(peakRate)} under the current filters. Use the spread across broad race groups as a fairness check on low-risk targeting assumptions, not a causal claim.`,
              }[id] ?? `${peakLabel} has the highest weighted rate at ${formatPercent(peakRate)}.`),
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildAgeLineQuestion(id: string): QuestionSpec {
  return {
    id,
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) => stringValue(row, "age_band") !== "" && numberValue(row, "afford_any") !== null,
      );
      const categories = AGE_BAND_ORDER.filter((category) =>
        valid.some((row) => stringValue(row, "age_band") === category),
      );
      const rates = categories.map((category) => {
        const group = valid.filter((row) => stringValue(row, "age_band") === category);
        const total = weightedTotal(group, filters.weightMode);
        const yes = group
          .filter((row) => numberValue(row, "afford_any") === 1)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
        return total === 0 ? 0 : yes / total;
      });
      const peakIndex = rates.reduce(
        (bestIndex, value, index, all) => (value > all[bestIndex] ? index : bestIndex),
        0,
      );
      return {
        option: lineOption(categories, rates, "Affordability barrier rate"),
        inference:
          categories.length === 0
            ? "No valid age-banded affordability pattern remains after filtering."
            : `${categories[peakIndex]} has the highest weighted affordability-barrier rate at ${formatPercent(rates[peakIndex])}.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildAffordRegionQuestion(): QuestionSpec {
  return {
    id: "afford-region",
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) => stringValue(row, "region23") !== "" && numberValue(row, "afford_any") !== null,
      );
      const categories = ["1", "2", "3", "4"].filter((region) =>
        valid.some((row) => stringValue(row, "region23") === region),
      );
      const rates = categories.map((region) => {
        const group = valid.filter((row) => stringValue(row, "region23") === region);
        const total = weightedTotal(group, filters.weightMode);
        const yes = group
          .filter((row) => numberValue(row, "afford_any") === 1)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
        return total === 0 ? 0 : yes / total;
      });
      const topIndex = rates.reduce(
        (bestIndex, value, index, all) => (value > all[bestIndex] ? index : bestIndex),
        0,
      );
      const labels = categories.map((region) =>
        ({
          "1": "Northeast",
          "2": "Midwest",
          "3": "South",
          "4": "West",
        })[region] ?? region,
      );
      return {
        option: barOption({
          categories: labels,
          values: rates,
          seriesName: "Affordability barrier rate",
          color: COLORS.gold,
          yAxisLabel: "Rate",
          valueFormatter: (value) => formatPercent(Number(value)),
        }),
        inference:
          labels.length === 0
            ? "No valid regional pattern remains after filtering."
            : `${labels[topIndex]} has the highest weighted affordability-barrier rate at ${formatPercent(rates[topIndex])}.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildBinaryCohortBoxQuestion(
  id: string,
  metricField: string,
  cohortField: string,
  labels: [string, string],
): QuestionSpec {
  return {
    id,
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) => numberValue(row, cohortField) !== null && numberValue(row, metricField) !== null,
      );
      const first = valid.filter((row) => numberValue(row, cohortField) === 1);
      const second = valid.filter((row) => numberValue(row, cohortField) === 0);
      const firstBox = weightedFiveNumber(first, metricField, filters.weightMode);
      const secondBox = weightedFiveNumber(second, metricField, filters.weightMode);
      if (!firstBox || !secondBox) {
        return {
          inference: "No valid distribution remains after the current filters.",
          excludedCount: rows.length - valid.length,
          validCount: valid.length,
          emptyState: "No valid distribution remains after the current filters.",
        };
      }
      const firstMedian = weightedQuantile(first, metricField, 0.5, filters.weightMode) ?? 0;
      const secondMedian = weightedQuantile(second, metricField, 0.5, filters.weightMode) ?? 0;
      const metric = METRIC_LABELS[metricField];
      return {
        option: boxOption({
          categories: labels,
          values: [firstBox, secondBox],
          metricField,
        }),
        inference: `The weighted median ${metric.label.toLowerCase()} is ${metric.formatter(firstMedian)} for ${labels[0].toLowerCase()} versus ${metric.formatter(secondMedian)} for ${labels[1].toLowerCase()}.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildReasonRankedQuestion(): QuestionSpec {
  return {
    id: "usc-reasons",
    build: ({ rows, metadata, filters }) => {
      const valid = rows.filter(
        (row) => stringValue(row, "haveus42") === "2" && stringValue(row, "ynousc42_m18") !== "",
      );
      const categories = collectByCategory(valid, "ynousc42_m18", filters.weightMode)
        .sort((left, right) => right.total - left.total)
        .filter((item) => !["-7", "-8", "-1"].includes(item.category));
      return {
        option: barOption({
          categories: categories.map((item) =>
            fieldLabel(metadata, "YNOUSC42_M18", item.category),
          ),
          values: categories.map((item) => item.total),
          seriesName: "Population estimate",
          color: COLORS.rose,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          categories.length === 0
            ? "No valid no-USC reasons remain after filtering."
            : `${fieldLabel(metadata, "YNOUSC42_M18", categories[0].category)} is the most common weighted reason among people without a usual source of care.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
        note: metadata.proxyNotes.no_usc,
      };
    },
  };
}

function buildUscCostShareQuestion(): QuestionSpec {
  return {
    id: "usc-cost-share",
    build: ({ rows, metadata, filters }) => {
      const valid = rows.filter((row) => stringValue(row, "haveus42") === "2");
      const cost = valid
        .filter((row) => stringValue(row, "ynousc42_m18") === "9")
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const other = valid
        .filter((row) => stringValue(row, "ynousc42_m18") !== "9" && stringValue(row, "ynousc42_m18") !== "")
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const total = cost + other;
      return {
        option: donutOption([
          { name: fieldLabel(metadata, "YNOUSC42_M18", "9"), value: cost, color: COLORS.accent },
          { name: "All other reasons", value: other, color: COLORS.fog },
        ]),
        inference:
          total === 0
            ? "No valid no-USC reason remains after filtering."
            : `${formatPercent(cost / total)} of the weighted no-USC population cites cost of medical care as the main reason.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
        note: metadata.proxyNotes.no_usc,
      };
    },
  };
}

function buildUscCostInsuranceQuestion(): QuestionSpec {
  return {
    id: "usc-cost-insurance",
    build: ({ rows, metadata, filters }) => {
      const valid = rows.filter(
        (row) => stringValue(row, "haveus42") === "2" && stringValue(row, "ynousc42_m18") === "9",
      );
      const categories = ["1", "2", "3"].map((code) => {
        const total = valid
          .filter((row) => stringValue(row, "inscov23") === code)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
        return { code, total };
      });
      return {
        option: barOption({
          categories: categories.map((item) => fieldLabel(metadata, "INSCOV23", item.code)),
          values: categories.map((item) => item.total),
          seriesName: "Population estimate",
          color: COLORS.slate,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          valid.length === 0
            ? "No cost-reason subgroup remains after filtering."
            : `${fieldLabel(metadata, "INSCOV23", categories.sort((left, right) => right.total - left.total)[0].code)} is the largest weighted insurance group inside the cost-reason subgroup.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
        note: metadata.proxyNotes.no_usc,
      };
    },
  };
}

function buildUscCostIncomeQuestion(): QuestionSpec {
  return {
    id: "usc-cost-income",
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) => stringValue(row, "haveus42") === "2" && stringValue(row, "ynousc42_m18") === "9",
      );
      const povertyCategories = ["1", "2", "3", "4", "5"];
      const incomeCategories = ["1", "2", "3", "4", "5"];
      const povertyValues = povertyCategories.map((category) =>
        valid
          .filter((row) => stringValue(row, "povcat23") === category)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0),
      );
      const incomeValues = incomeCategories.map((category) =>
        valid
          .filter((row) => stringValue(row, "family_income_quintile") === category)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0),
      );
      return {
        option: {
          grid: [
            { left: 52, right: "55%", top: 18, bottom: 48, containLabel: true },
            { left: "58%", right: 18, top: 18, bottom: 48, containLabel: true },
          ],
          xAxis: [
            {
              type: "category",
              gridIndex: 0,
              data: povertyCategories.map((category) => `P${category}`),
              axisLabel: { color: COLORS.ink },
              axisTick: { show: false },
            },
            {
              type: "category",
              gridIndex: 1,
              data: incomeCategories.map((category) => `Q${category}`),
              axisLabel: { color: COLORS.ink },
              axisTick: { show: false },
            },
          ],
          yAxis: [
            {
              type: "value",
              gridIndex: 0,
              axisLabel: { color: COLORS.muted, formatter: (value: number) => formatPopulation(value) },
              splitLine: { lineStyle: { color: "#ebdfd4" } },
            },
            {
              type: "value",
              gridIndex: 1,
              axisLabel: { color: COLORS.muted, formatter: (value: number) => formatPopulation(value) },
              splitLine: { lineStyle: { color: "#ebdfd4" } },
            },
          ],
          series: [
            {
              type: "bar",
              xAxisIndex: 0,
              yAxisIndex: 0,
              data: povertyValues,
              itemStyle: { color: COLORS.accent, borderRadius: [8, 8, 0, 0] },
            },
            {
              type: "bar",
              xAxisIndex: 1,
              yAxisIndex: 1,
              data: incomeValues,
              itemStyle: { color: COLORS.slate, borderRadius: [8, 8, 0, 0] },
            },
          ],
          title: [
            { text: "Poverty category", left: "20%", top: 0, textStyle: { color: COLORS.ink, fontFamily: "Fraunces, serif", fontSize: 14 } },
            { text: "Income quintile", left: "72%", top: 0, textStyle: { color: COLORS.ink, fontFamily: "Fraunces, serif", fontSize: 14 } },
          ],
          textStyle: baseTextStyle(),
        },
        inference:
          valid.length === 0
            ? "No cost-reason subgroup remains after filtering."
            : "This proxy subgroup can be read two ways at once: poverty category on the left and fixed family-income quintiles on the right.",
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
        note: "Proxy-only: this reflects no-USC cost reason, not a direct purchase reason.",
      };
    },
  };
}

function buildDualBoxQuestion(id: string, subset: (row: SitePersonRow) => boolean, labels: [string, string]): QuestionSpec {
  return {
    id,
    build: ({ rows, filters }) => {
      const subsetRows = rows.filter(subset);
      const spendRows = subsetRows.filter((row) => numberValue(row, "totexp23") !== null);
      const oopRows = subsetRows.filter((row) => numberValue(row, "totslf23") !== null);
      const spendBox = weightedFiveNumber(spendRows, "totexp23", filters.weightMode);
      const oopBox = weightedFiveNumber(oopRows, "totslf23", filters.weightMode);
      if (!spendBox || !oopBox) {
        return {
          inference: "No valid spending values remain after the current filters.",
          excludedCount: rows.length - subsetRows.length,
          validCount: subsetRows.length,
          emptyState: "No valid spending values remain after the current filters.",
        };
      }
      const spendMedian = weightedQuantile(spendRows, "totexp23", 0.5, filters.weightMode) ?? 0;
      const oopMedian = weightedQuantile(oopRows, "totslf23", 0.5, filters.weightMode) ?? 0;
      return {
        option: boxOption({
          categories: labels,
          values: [spendBox, oopBox],
          metricField: "totexp23",
        }),
        inference: `Within this subgroup, the weighted median annual total spend is ${formatCurrency(spendMedian)} and the weighted median out-of-pocket spend is ${formatCurrency(oopMedian)}.`,
        excludedCount: rows.length - subsetRows.length,
        validCount: subsetRows.length,
      };
    },
  };
}

function buildCanAffordEducationSpend(): QuestionSpec {
  return {
    id: "can-afford-education-spend",
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) =>
          numberValue(row, "can_afford_all") === 1 &&
          stringValue(row, "education_band") !== "" &&
          numberValue(row, "totexp23") !== null,
      );
      const categories = EDUCATION_ORDER.filter((category) =>
        valid.some((row) => stringValue(row, "education_band") === category),
      );
      const boxes = categories
        .map((category) =>
          weightedFiveNumber(
            valid.filter((row) => stringValue(row, "education_band") === category),
            "totexp23",
            filters.weightMode,
          ),
        )
        .filter(Boolean) as Array<[number, number, number, number, number]>;
      const medians = categories.map((category) =>
        weightedQuantile(
          valid.filter((row) => stringValue(row, "education_band") === category),
          "totexp23",
          0.5,
          filters.weightMode,
        ) ?? 0,
      );
      return {
        option: boxOption({ categories, values: boxes, metricField: "totexp23" }),
        inference:
          categories.length === 0
            ? "No adult can-afford cohort remains after filtering."
            : `${categories[medians.indexOf(Math.max(...medians))]} shows the highest weighted median annual total spend inside the can-afford cohort. Even among people reporting no direct affordability barrier, spending still differs across education bands.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildCanAffordIncomeSpend(): QuestionSpec {
  return {
    id: "can-afford-income-spend",
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) =>
          numberValue(row, "can_afford_all") === 1 &&
          stringValue(row, "povcat23") !== "" &&
          numberValue(row, "totexp23") !== null,
      );
      const categories = ["1", "2", "3", "4", "5"].filter((code) =>
        valid.some((row) => stringValue(row, "povcat23") === code),
      );
      const labels = categories.map((category) =>
        ({
          "1": "Poor",
          "2": "Near poor",
          "3": "Low income",
          "4": "Middle income",
          "5": "High income",
        })[category] ?? category,
      );
      const boxes = categories
        .map((category) =>
          weightedFiveNumber(
            valid.filter((row) => stringValue(row, "povcat23") === category),
            "totexp23",
            filters.weightMode,
          ),
        )
        .filter(Boolean) as Array<[number, number, number, number, number]>;
      const medians = categories.map((category) =>
        weightedQuantile(
          valid.filter((row) => stringValue(row, "povcat23") === category),
          "totexp23",
          0.5,
          filters.weightMode,
        ) ?? 0,
      );
      return {
        option: boxOption({ categories: labels, values: boxes, metricField: "totexp23" }),
        inference:
          labels.length === 0
            ? "No can-afford poverty split remains under the current filters."
            : `${labels[medians.indexOf(Math.max(...medians))]} shows the highest weighted median spend inside the can-afford cohort. This lets you compare how reported affordability and realized spending can still diverge across income groups.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildGroupedBoxByCategoryQuestion(params: {
  id: string;
  metricField: string;
  categoryField: string;
  categories: string[];
  labelField?: string;
  subset: (row: SitePersonRow) => boolean;
}): QuestionSpec {
  return {
    id: params.id,
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) =>
          params.subset(row) &&
          stringValue(row, params.categoryField) !== "" &&
          numberValue(row, params.metricField) !== null,
      );
      const categories = params.categories.filter((category) =>
        valid.some((row) => stringValue(row, params.categoryField) === category),
      );
      const labels = categories.map((category) =>
        params.labelField
          ? stringValue(
              valid.find((row) => stringValue(row, params.categoryField) === category)!,
              params.labelField,
            )
          : category,
      );
      const boxes = categories
        .map((category) =>
          weightedFiveNumber(
            valid.filter((row) => stringValue(row, params.categoryField) === category),
            params.metricField,
            filters.weightMode,
          ),
        )
        .filter(Boolean) as Array<[number, number, number, number, number]>;
      const medians = categories.map((category) =>
        weightedQuantile(
          valid.filter((row) => stringValue(row, params.categoryField) === category),
          params.metricField,
          0.5,
          filters.weightMode,
        ) ?? 0,
      );
      return {
        option: boxOption({
          categories: labels,
          values: boxes,
          metricField: params.metricField,
        }),
        inference:
          labels.length === 0
            ? "No valid grouped distribution remains after filtering."
            : ({
                "race-total-spend": `${labels[medians.indexOf(Math.max(...medians))]} shows the highest weighted median annual total spend. Read the differences across broad race groups as descriptive burden patterns within the filtered cohort.`,
                "race-oop-burden": `${labels[medians.indexOf(Math.max(...medians))]} shows the highest weighted median annual out-of-pocket spend. Compare the full set of boxes to see where direct financial burden is heaviest under the current filters.`,
                "income-oop-share": `${labels[medians.indexOf(Math.max(...medians))]} shows the highest weighted median out-of-pocket share. The sequence across quintiles reveals how directly paid burden changes across the income distribution.`,
              }[params.id] ??
              `${labels[medians.indexOf(Math.max(...medians))]} shows the highest weighted median ${METRIC_LABELS[params.metricField].label.toLowerCase()}.`),
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildLowRiskProxyQuestion(): QuestionSpec {
  return {
    id: "low-risk-proxy",
    build: ({ rows, filters }) => {
      const valid = rows.filter((row) => numberValue(row, "low_risk") !== null);
      const lowRisk = valid
        .filter((row) => numberValue(row, "low_risk") === 1)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const notLowRisk = valid
        .filter((row) => numberValue(row, "low_risk") === 0)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const total = lowRisk + notLowRisk;
      return {
        option: barOption({
          categories: ["Low risk", "Not low risk"],
          values: [lowRisk, notLowRisk],
          seriesName: "Population estimate",
          color: COLORS.forest,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          total === 0
            ? "No valid low-risk classification remains after filtering."
            : `${formatPercent(lowRisk / total)} of the filtered population is tagged as low risk in the existing processed cohort.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildLowRiskPayerMix(): QuestionSpec {
  return {
    id: "low-risk-payer-mix",
    build: ({ rows, filters }) => {
      const valid = rows.filter((row) => numberValue(row, "low_risk") === 1);
      const totals = {
        Private: valid.reduce(
          (sum, row) => sum + (numberValue(row, "totprv23") ?? 0) * weightForRow(row, filters.weightMode),
          0,
        ),
        Medicare: valid.reduce(
          (sum, row) => sum + (numberValue(row, "totmcr23") ?? 0) * weightForRow(row, filters.weightMode),
          0,
        ),
        Medicaid: valid.reduce(
          (sum, row) => sum + (numberValue(row, "totmcd23") ?? 0) * weightForRow(row, filters.weightMode),
          0,
        ),
        "Out of pocket": valid.reduce(
          (sum, row) => sum + (numberValue(row, "totslf23") ?? 0) * weightForRow(row, filters.weightMode),
          0,
        ),
      };
      const totalSpend = Object.values(totals).reduce((sum, value) => sum + value, 0);
      const categories = Object.keys(totals);
      const values = categories.map((category) => (totalSpend === 0 ? 0 : totals[category as keyof typeof totals] / totalSpend));
      return {
        option: stackedOption({
          categories: ["Low-risk cohort"],
          yesValues: [values[0] + values[1]],
          noValues: [values[2] + values[3]],
          yesLabel: "Private + Medicare share",
          noLabel: "Medicaid + OOP share",
        }),
        inference:
          totalSpend === 0
            ? "No low-risk payer mix remains after filtering."
            : `Private and Medicare together account for ${formatPercent(values[0] + values[1])} of weighted payment volume in the low-risk cohort.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildLowRiskTargetable(): QuestionSpec {
  return {
    id: "low-risk-targetable",
    build: ({ rows, filters }) => {
      const full = weightedTotal(rows, filters.weightMode);
      const lowRisk = rows
        .filter((row) => numberValue(row, "low_risk") === 1)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const uninsuredLowRisk = rows
        .filter(
          (row) => numberValue(row, "low_risk") === 1 && stringValue(row, "unins23") === "1",
        )
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      return {
        option: funnelOption([
          { name: "Filtered population", value: full },
          { name: "Low-risk cohort", value: lowRisk },
          { name: "Uninsured low-risk", value: uninsuredLowRisk },
        ]),
        inference:
          full === 0
            ? "No scenario remains after filtering."
            : `The conservative uninsured low-risk targetable segment equals ${formatPercent(uninsuredLowRisk / full)} of the currently filtered population.`,
        excludedCount: 0,
        validCount: rows.length,
      };
    },
  };
}

function buildLowRiskCoveredLives(): QuestionSpec {
  return {
    id: "low-risk-covered-lives",
    build: ({ rows, filters }) => {
      const population = weightedTotal(rows, filters.weightMode);
      const uninsured = rows
        .filter((row) => stringValue(row, "unins23") === "1")
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const uninsuredLowRisk = rows
        .filter(
          (row) => stringValue(row, "unins23") === "1" && numberValue(row, "low_risk") === 1,
        )
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      return {
        option: barOption({
          categories: ["Filtered population", "All uninsured", "Uninsured low-risk"],
          values: [population, uninsured, uninsuredLowRisk],
          seriesName: "Scenario size",
          color: COLORS.gold,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          population === 0
            ? "No scenario remains after filtering."
            : `The uninsured low-risk segment is ${formatPercent(uninsuredLowRisk / population)} of the filtered population and ${uninsured === 0 ? "0.0%" : formatPercent(uninsuredLowRisk / uninsured)} of all uninsured people.`,
        excludedCount: 0,
        validCount: rows.length,
      };
    },
  };
}

function buildStudentInsurance(): QuestionSpec {
  return {
    id: "student-insurance",
    build: ({ rows, filters, metadata }) => {
      const valid = rows.filter(
        (row) =>
          numberValue(row, "age_focus_17_23") === 1 && stringValue(row, "ftstu23x") === "1",
      );
      const categories = ["1", "2", "3"].map((code) => ({
        code,
        total: valid
          .filter((row) => stringValue(row, "inscov23") === code)
          .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0),
      }));
      return {
        option: barOption({
          categories: categories.map((category) => fieldLabel(metadata, "INSCOV23", category.code)),
          values: categories.map((category) => category.total),
          seriesName: "Full-time students",
          color: COLORS.slate,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          valid.length === 0
            ? "No full-time student cohort remains after filtering."
            : `${fieldLabel(metadata, "INSCOV23", categories.sort((left, right) => right.total - left.total)[0].code)} is the largest insurance group among full-time students ages 17-23.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildStudentDelay(): QuestionSpec {
  return {
    id: "student-delay",
    build: ({ rows, filters }) => {
      const valid = rows.filter(
        (row) =>
          numberValue(row, "age_focus_17_23") === 1 &&
          stringValue(row, "ftstu23x") === "1" &&
          numberValue(row, "delay_any") !== null,
      );
      const delayed = valid
        .filter((row) => numberValue(row, "delay_any") === 1)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const noDelay = valid
        .filter((row) => numberValue(row, "delay_any") === 0)
        .reduce((sum, row) => sum + weightForRow(row, filters.weightMode), 0);
      const total = delayed + noDelay;
      return {
        option: barOption({
          categories: ["Delayed due to cost", "No reported delay"],
          values: [delayed, noDelay],
          seriesName: "Full-time students",
          color: COLORS.rose,
          yAxisLabel: filters.weightMode === "weighted" ? "People" : "Respondents",
          valueFormatter: (value) =>
            filters.weightMode === "weighted"
              ? formatPopulation(Number(value))
              : formatNumber(Number(value)),
        }),
        inference:
          total === 0
            ? "No full-time student cohort remains after filtering."
            : `${formatPercent(delayed / total)} of full-time students ages 17-23 report delaying at least one care type due to cost.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

function buildStudentLowRiskSignals(): QuestionSpec {
  return {
    id: "student-low-risk-signals",
    modes: [
      { id: "chronic_ct", label: "Chronic condition count" },
      { id: "limit_ct", label: "Functional limitation count" },
      { id: "nonacute_util_ct", label: "Non-acute utilization count" },
    ],
    defaultMode: "chronic_ct",
    build: ({ rows, filters, mode }) => {
      const valid = rows.filter(
        (row) =>
          numberValue(row, "age_focus_17_23") === 1 &&
          (stringValue(row, "ftstu23x") === "1" || stringValue(row, "ftstu23x") === "3") &&
          numberValue(row, mode) !== null,
      );
      const studentRows = valid.filter((row) => stringValue(row, "ftstu23x") === "1");
      const nonStudentRows = valid.filter((row) => stringValue(row, "ftstu23x") === "3");
      const studentBox = weightedFiveNumber(studentRows, mode, filters.weightMode);
      const nonStudentBox = weightedFiveNumber(nonStudentRows, mode, filters.weightMode);
      if (!studentBox || !nonStudentBox) {
        return {
          inference: "No comparable 17-23 student and non-student groups remain after filtering.",
          excludedCount: rows.length - valid.length,
          validCount: valid.length,
          emptyState: "No comparable 17-23 student and non-student groups remain after filtering.",
        };
      }
      const metric = METRIC_LABELS[mode];
      const studentMedian = weightedQuantile(studentRows, mode, 0.5, filters.weightMode) ?? 0;
      const nonStudentMedian = weightedQuantile(nonStudentRows, mode, 0.5, filters.weightMode) ?? 0;
      return {
        option: boxOption({
          categories: ["Full-time students", "Non-students"],
          values: [studentBox, nonStudentBox],
          metricField: mode,
        }),
        inference: `For ${metric.label.toLowerCase()}, the weighted median is ${metric.formatter(studentMedian)} for full-time students versus ${metric.formatter(nonStudentMedian)} for non-students ages 17-23.`,
        excludedCount: rows.length - valid.length,
        validCount: valid.length,
      };
    },
  };
}

export const QUESTION_SPECS: QuestionSpec[] = [
  buildBinaryBarQuestion("afford-med", "afrdca42"),
  buildBinaryBarQuestion("afford-dental", "afrddn42"),
  buildBinaryBarQuestion("afford-rx", "afrdpm42"),
  buildCompositeDonutQuestion(
    "afford-any",
    "afford_any",
    "Could not afford at least one type",
    "No reported affordability barrier",
  ),
  buildHistogramQuestion("afford-total-spend", "totexp23", (row) => numberValue(row, "afford_any") === 1),
  buildHistogramQuestion("afford-oop-spend", "totslf23", (row) => numberValue(row, "afford_any") === 1),
  buildMetricComparisonQuestion("afford-sicker-or-skipping", "afford_any"),
  buildStackedRateQuestion("afford-insurance", "inscov23", "afford_any"),
  buildStackedRateQuestion("afford-poverty", "povcat23", "afford_any", ["1", "2", "3", "4", "5"]),
  buildOrderedRateQuestion(
    "afford-income-quintile",
    "family_income_quintile",
    "afford_any",
    ["1", "2", "3", "4", "5"],
    "family_income_quintile_label",
  ),
  buildOrderedRateQuestion(
    "afford-education",
    "education_band",
    "afford_any",
    EDUCATION_ORDER,
    "education_band_label",
  ),
  buildOrderedRateQuestion(
    "afford-race",
    "racethx",
    "afford_any",
    RACE_ORDER,
    "racethx_label",
  ),
  buildOrderedRateQuestion(
    "afford-employment",
    "employment_band",
    "afford_any",
    EMPLOYMENT_ORDER,
    "employment_band_label",
  ),
  buildAgeLineQuestion("afford-age"),
  buildAffordRegionQuestion(),
  buildBinaryCohortBoxQuestion(
    "afford-er",
    "ertot23",
    "afford_any",
    ["Affordability barrier", "No affordability barrier"],
  ),
  buildBinaryBarQuestion("delay-med", "dlayca42"),
  buildBinaryBarQuestion("delay-dental", "dlaydn42"),
  buildBinaryBarQuestion("delay-rx", "dlaypm42"),
  buildCompositeDonutQuestion(
    "delay-any",
    "delay_any",
    "Delayed at least one type",
    "No reported delay",
  ),
  buildOrderedRateQuestion(
    "delay-race",
    "racethx",
    "delay_any",
    RACE_ORDER,
    "racethx_label",
  ),
  buildBinaryCohortBoxQuestion("delay-er", "ertot23", "delay_any", ["Delayed care", "No delay"]),
  buildBinaryCohortBoxQuestion(
    "delay-ipdis",
    "ipdis23",
    "delay_any",
    ["Delayed care", "No delay"],
  ),
  buildBinaryCohortBoxQuestion("delay-oop", "totslf23", "delay_any", ["Delayed care", "No delay"]),
  buildReasonRankedQuestion(),
  buildUscCostShareQuestion(),
  buildUscCostInsuranceQuestion(),
  buildUscCostIncomeQuestion(),
  buildDualBoxQuestion(
    "usc-cost-burden",
    (row) => stringValue(row, "haveus42") === "2" && stringValue(row, "ynousc42_m18") === "9",
    ["Annual total spend", "Annual out-of-pocket spend"],
  ),
  buildCanAffordEducationSpend(),
  buildCanAffordIncomeSpend(),
  buildGroupedBoxByCategoryQuestion({
    id: "race-total-spend",
    metricField: "totexp23",
    categoryField: "racethx",
    categories: RACE_ORDER,
    labelField: "racethx_label",
    subset: () => true,
  }),
  buildGroupedBoxByCategoryQuestion({
    id: "race-oop-burden",
    metricField: "totslf23",
    categoryField: "racethx",
    categories: RACE_ORDER,
    labelField: "racethx_label",
    subset: () => true,
  }),
  buildGroupedBoxByCategoryQuestion({
    id: "income-oop-share",
    metricField: "oop_share",
    categoryField: "family_income_quintile",
    categories: ["1", "2", "3", "4", "5"],
    labelField: "family_income_quintile_label",
    subset: () => true,
  }),
  buildOrderedRateQuestion(
    "education-delay-rate",
    "education_band",
    "delay_any",
    EDUCATION_ORDER,
    "education_band_label",
  ),
  buildOrderedRateQuestion(
    "income-afford-rate",
    "povcat23",
    "afford_any",
    ["1", "2", "3", "4", "5"],
    "povcat23_label",
  ),
  buildLowRiskProxyQuestion(),
  buildBinaryCohortBoxQuestion("low-risk-spend", "totexp23", "low_risk", ["Low risk", "Not low risk"]),
  buildBinaryCohortBoxQuestion("low-risk-oop", "totslf23", "low_risk", ["Low risk", "Not low risk"]),
  buildStackedRateQuestion(
    "low-risk-uninsured",
    "unins23",
    "low_risk",
    ["1", "2"],
    undefined,
    { yes: "Low risk", no: "Not low risk", subject: "low-risk" },
  ),
  buildLowRiskTargetable(),
  buildLowRiskPayerMix(),
  buildOrderedRateQuestion(
    "low-risk-race",
    "racethx",
    "low_risk",
    RACE_ORDER,
    "racethx_label",
  ),
  buildLowRiskCoveredLives(),
  buildStackedRateQuestion(
    "student-affordability",
    "ftstu23x",
    "afford_any",
    ["1", "2", "3"],
    (row) => numberValue(row, "age_focus_17_23") === 1,
  ),
  buildDualBoxQuestion(
    "student-spend",
    (row) => numberValue(row, "age_focus_17_23") === 1 && stringValue(row, "ftstu23x") === "1",
    ["Annual total spend", "Annual out-of-pocket spend"],
  ),
  buildStudentInsurance(),
  buildStudentDelay(),
  buildStudentLowRiskSignals(),
];

export function getQuestionSpec(id: string): QuestionSpec {
  const match = QUESTION_SPECS.find((question) => question.id === id);
  if (!match) {
    throw new Error(`Missing question spec for ${id}`);
  }
  return match;
}
