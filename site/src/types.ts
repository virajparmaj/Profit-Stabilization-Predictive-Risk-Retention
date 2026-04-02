import type { EChartsOption } from "echarts";

export type WeightMode = "weighted" | "unweighted";
export type CellValue = string | number | null;
export type SitePersonRow = Record<string, CellValue>;

export type SectionMeta = {
  id: string;
  title: string;
  description: string;
};

export type QuestionMeta = {
  id: string;
  section: string;
  title: string;
  chartKind: string;
  variables: string[];
  howToRead: string;
  featured?: boolean;
};

export type Metadata = {
  source: {
    raw: string;
    lowRisk: string;
    generatedFrom: string;
  };
  dataset: {
    year: number;
    rowCount: number;
    quintileThresholds: number[];
  };
  specialValues: Record<string, string>;
  valueLabels: Record<string, Record<string, string>>;
  variableLabels: Record<string, string>;
  sections: SectionMeta[];
  questions: QuestionMeta[];
  overview: {
    heroMetricIds: string[];
    highlightQuestionIds: string[];
  };
  assumptions: string[];
  proxyNotes: Record<string, string>;
  validation: Array<{
    name: string;
    value: unknown;
    detail: string;
  }>;
};

export type FilterState = {
  weightMode: WeightMode;
  insurance: string;
  poverty: string;
  region: string;
  student: string;
  ageBand: string;
  affordability: string;
  delay: string;
  lowRisk: string;
};

export type QuestionMode = {
  id: string;
  label: string;
};

export type QuestionResult = {
  option?: EChartsOption;
  inference: string;
  excludedCount: number;
  validCount: number;
  note?: string;
  emptyState?: string;
};

export type QuestionSpec = {
  id: string;
  defaultMode?: string;
  modes?: QuestionMode[];
  build: (args: {
    rows: SitePersonRow[];
    metadata: Metadata;
    filters: FilterState;
    mode: string;
  }) => QuestionResult;
};
