import type { FilterState, Metadata } from "../types";

type FilterRailProps = {
  filters: FilterState;
  metadata: Metadata;
  filteredCount: number;
  totalCount: number;
  onChange: (field: keyof FilterState, value: string) => void;
  onReset: () => void;
};

const STUDENT_OPTIONS = [
  { value: "all", label: "All respondents" },
  { value: "focus17_23", label: "Ages 17-23 only" },
  { value: "full_time", label: "Full-time students" },
  { value: "part_time", label: "Part-time students" },
  { value: "not_student", label: "Non-students ages 17-23" },
];

const AGE_OPTIONS = [
  { value: "all", label: "All ages" },
  { value: "0-17", label: "0-17" },
  { value: "18-25", label: "18-25" },
  { value: "26-34", label: "26-34" },
  { value: "35-44", label: "35-44" },
  { value: "45-54", label: "45-54" },
  { value: "55-64", label: "55-64" },
  { value: "65+", label: "65+" },
];

const AFFORDABILITY_OPTIONS = [
  { value: "all", label: "All affordability states" },
  { value: "barrier", label: "Could not afford at least one type" },
  { value: "no_barrier", label: "No affordability problem" },
  { value: "unknown", label: "Composite affordability unknown" },
];

const DELAY_OPTIONS = [
  { value: "all", label: "All delay states" },
  { value: "delayed", label: "Delayed at least one type" },
  { value: "not_delayed", label: "No reported delay" },
  { value: "unknown", label: "Composite delay unknown" },
];

const LOW_RISK_OPTIONS = [
  { value: "all", label: "All low-risk states" },
  { value: "low_risk", label: "Low risk only" },
  { value: "not_low_risk", label: "Not low risk" },
];

function mappedOptions(
  labels: Record<string, string> | undefined,
  codes: string[],
  fallbackLabel: string,
) {
  return [
    { value: "all", label: fallbackLabel },
    ...codes.map((code) => ({
      value: code,
      label: labels?.[code] ?? code,
    })),
  ];
}

export function FilterRail({
  filters,
  metadata,
  filteredCount,
  totalCount,
  onChange,
  onReset,
}: FilterRailProps) {
  const insuranceOptions = mappedOptions(
    metadata.valueLabels.INSCOV23,
    ["1", "2", "3"],
    "All insurance groups",
  );
  const povertyOptions = mappedOptions(
    metadata.valueLabels.POVCAT23,
    ["1", "2", "3", "4", "5"],
    "All poverty groups",
  );
  const regionOptions = mappedOptions(
    metadata.valueLabels.REGION23,
    ["1", "2", "3", "4"],
    "All regions",
  );

  return (
    <aside className="filter-rail">
      <div className="filter-hero">
        <p className="eyebrow">Explorer Controls</p>
        <h2>Shape the cohort</h2>
        <p>
          Use these global filters to recompute every chart and inference from the
          filtered MEPS cohort.
        </p>
      </div>

      <div className="weight-toggle">
        <button
          className={filters.weightMode === "weighted" ? "active" : ""}
          onClick={() => onChange("weightMode", "weighted")}
          type="button"
        >
          Weighted
        </button>
        <button
          className={filters.weightMode === "unweighted" ? "active" : ""}
          onClick={() => onChange("weightMode", "unweighted")}
          type="button"
        >
          Unweighted
        </button>
      </div>

      <div className="filter-summary">
        <span>Filtered rows</span>
        <strong>
          {filteredCount.toLocaleString()} / {totalCount.toLocaleString()}
        </strong>
      </div>

      <label className="filter-group">
        <span>Insurance</span>
        <select
          value={filters.insurance}
          onChange={(event) => onChange("insurance", event.target.value)}
        >
          {insuranceOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Poverty category</span>
        <select
          value={filters.poverty}
          onChange={(event) => onChange("poverty", event.target.value)}
        >
          {povertyOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Region</span>
        <select
          value={filters.region}
          onChange={(event) => onChange("region", event.target.value)}
        >
          {regionOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Student lens</span>
        <select
          value={filters.student}
          onChange={(event) => onChange("student", event.target.value)}
        >
          {STUDENT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Age band</span>
        <select
          value={filters.ageBand}
          onChange={(event) => onChange("ageBand", event.target.value)}
        >
          {AGE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Affordability cohort</span>
        <select
          value={filters.affordability}
          onChange={(event) => onChange("affordability", event.target.value)}
        >
          {AFFORDABILITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Delay cohort</span>
        <select
          value={filters.delay}
          onChange={(event) => onChange("delay", event.target.value)}
        >
          {DELAY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="filter-group">
        <span>Low-risk cohort</span>
        <select
          value={filters.lowRisk}
          onChange={(event) => onChange("lowRisk", event.target.value)}
        >
          {LOW_RISK_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <button className="reset-button" onClick={onReset} type="button">
        Reset filters
      </button>

      <div className="assumption-card">
        <p className="eyebrow">Method</p>
        <ul>
          {metadata.assumptions.slice(0, 3).map((assumption) => (
            <li key={assumption}>{assumption}</li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
