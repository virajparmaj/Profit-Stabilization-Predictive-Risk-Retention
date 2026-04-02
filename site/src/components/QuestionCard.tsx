import { useEffect, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";

import type { FilterState, Metadata, QuestionMeta, QuestionSpec, SitePersonRow } from "../types";

type QuestionCardProps = {
  rows: SitePersonRow[];
  metadata: Metadata;
  filters: FilterState;
  meta: QuestionMeta;
  spec: QuestionSpec;
};

export function QuestionCard({
  rows,
  metadata,
  filters,
  meta,
  spec,
}: QuestionCardProps) {
  const initialMode = spec.defaultMode ?? spec.modes?.[0]?.id ?? "default";
  const [mode, setMode] = useState(initialMode);

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode, spec.id]);

  const result = useMemo(
    () => spec.build({ rows, metadata, filters, mode }),
    [rows, metadata, filters, mode, spec],
  );

  const variableLabels = useMemo(
    () =>
      meta.variables.map(
        (variable) =>
          metadata.variableLabels[variable] ??
          metadata.variableLabels[variable.toUpperCase()] ??
          variable,
      ),
    [meta.variables, metadata.variableLabels],
  );

  return (
    <article className="question-card" id={meta.id}>
      <div className="question-head">
        <div>
          <p className="eyebrow">{meta.chartKind}</p>
          <h3>{meta.title}</h3>
        </div>
        {spec.modes && spec.modes.length > 0 ? (
          <label className="mode-select">
            <span>View</span>
            <select value={mode} onChange={(event) => setMode(event.target.value)}>
              {spec.modes.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ) : null}
      </div>

      <p className="reading-guide">{meta.howToRead}</p>

      <div className="chart-shell">
        {result.option ? (
          <ReactECharts option={result.option} style={{ height: 340, width: "100%" }} notMerge />
        ) : (
          <div className="empty-state">{result.emptyState ?? "No chart available."}</div>
        )}
      </div>

      <div className="inference-block">
        <p className="eyebrow">Inference</p>
        <p>{result.inference}</p>
      </div>

      {result.note ? <p className="proxy-note">{result.note}</p> : null}

      <p className="data-note">
        Variables: {variableLabels.join(", ")}. Weighting: {filters.weightMode}. Valid rows:{" "}
        {result.validCount.toLocaleString()}. Excluded rows: {result.excludedCount.toLocaleString()}.
      </p>
    </article>
  );
}
