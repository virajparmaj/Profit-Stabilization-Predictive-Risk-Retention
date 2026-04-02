import { startTransition, useDeferredValue, useEffect, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";

import { FilterRail } from "./components/FilterRail";
import { QuestionCard } from "./components/QuestionCard";
import { applyFilters, numberValue, weightForRow, weightedTotal } from "./lib/analysis";
import { loadMetadata, loadRows } from "./lib/data";
import { formatPercent, formatPopulation } from "./lib/format";
import { getQuestionSpec } from "./questions";
import type { FilterState, Metadata, SitePersonRow } from "./types";

const INITIAL_FILTERS: FilterState = {
  weightMode: "weighted",
  insurance: "all",
  poverty: "all",
  region: "all",
  student: "all",
  ageBand: "all",
  affordability: "all",
  delay: "all",
  lowRisk: "all",
};

type KpiCard = {
  label: string;
  estimate: number;
  share: number;
};

function computeFlagKpi(rows: SitePersonRow[], field: string, weightMode: FilterState["weightMode"]): KpiCard {
  const valid = rows.filter((row) => {
    const value = row[field];
    return value === "1" || value === "2" || value === 1 || value === 0;
  });
  const yes = valid
    .filter((row) => row[field] === "1" || row[field] === 1)
    .reduce((sum, row) => sum + weightForRow(row, weightMode), 0);
  const total = valid.reduce((sum, row) => sum + weightForRow(row, weightMode), 0);
  return {
    label: field,
    estimate: yes,
    share: total === 0 ? 0 : yes / total,
  };
}

function makeOverviewFunnel(rows: SitePersonRow[], weightMode: FilterState["weightMode"]) {
  const filteredPopulation = weightedTotal(rows, weightMode);
  const delayed = rows
    .filter((row) => numberValue(row, "delay_any") === 1)
    .reduce((sum, row) => sum + weightForRow(row, weightMode), 0);
  const couldNotAfford = rows
    .filter((row) => numberValue(row, "afford_any") === 1)
    .reduce((sum, row) => sum + weightForRow(row, weightMode), 0);

  return {
    option: {
      tooltip: {
        trigger: "item",
        formatter: (params: { name: string; value: number }) =>
          `${params.name}<br/>${formatPopulation(params.value)}`,
      },
      series: [
        {
          type: "funnel",
          top: 16,
          bottom: 18,
          left: "10%",
          width: "80%",
          gap: 10,
          minSize: "30%",
          label: {
            color: "#231a18",
            formatter: (params: { name: string; value: number }) =>
              `${params.name}\n${formatPopulation(params.value)}`,
          },
          itemStyle: {
            borderColor: "#fff8ef",
            borderWidth: 3,
          },
          data: [
            { name: "Filtered population", value: filteredPopulation, itemStyle: { color: "#4f6078" } },
            { name: "Delayed due to cost", value: delayed, itemStyle: { color: "#c08f2d" } },
            { name: "Could not afford at least one type", value: couldNotAfford, itemStyle: { color: "#c55d3d" } },
          ],
        },
      ],
    },
    narrative:
      filteredPopulation === 0
        ? "No filtered cohort remains."
        : `${formatPercent(delayed / filteredPopulation)} of the filtered population reports any cost-related delay, and ${formatPercent(couldNotAfford / filteredPopulation)} reports at least one direct affordability barrier.`,
  };
}

export default function App() {
  const [rows, setRows] = useState<SitePersonRow[]>([]);
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([loadRows(), loadMetadata()])
      .then(([loadedRows, loadedMetadata]) => {
        setRows(loadedRows);
        setMetadata(loadedMetadata);
      })
      .catch((caughtError: Error) => {
        setError(caughtError.message);
      });
  }, []);

  const deferredFilters = useDeferredValue(filters);
  const filteredRows = useMemo(
    () => applyFilters(rows, deferredFilters),
    [rows, deferredFilters],
  );

  const overviewKpis = useMemo(() => {
    const config = [
      { field: "afrdca42", title: "Could not afford medical care" },
      { field: "afrddn42", title: "Could not afford dental care" },
      { field: "afrdpm42", title: "Could not afford medicine" },
      { field: "dlayca42", title: "Delayed medical care due to cost" },
      { field: "dlaydn42", title: "Delayed dental care due to cost" },
      { field: "dlaypm42", title: "Delayed medicine due to cost" },
    ];
    return config.map((item) => {
      const metric = computeFlagKpi(filteredRows, item.field, deferredFilters.weightMode);
      return { ...metric, title: item.title };
    });
  }, [filteredRows, deferredFilters.weightMode]);

  const funnel = useMemo(
    () => makeOverviewFunnel(filteredRows, deferredFilters.weightMode),
    [filteredRows, deferredFilters.weightMode],
  );

  const activeSections = metadata?.sections.filter((section) => section.id !== "overview") ?? [];

  if (error) {
    return <main className="status-screen">Failed to load explorer data: {error}</main>;
  }

  if (!metadata) {
    return <main className="status-screen">Loading MEPS affordability explorer…</main>;
  }

  return (
    <div className="app-shell">
      <FilterRail
        filters={filters}
        metadata={metadata}
        filteredCount={filteredRows.length}
        totalCount={rows.length}
        onChange={(field, value) => {
          startTransition(() => {
            setFilters((current) => ({ ...current, [field]: value }));
          });
        }}
        onReset={() => {
          startTransition(() => setFilters(INITIAL_FILTERS));
        }}
      />

      <main className="main-panel">
        <header className="hero-panel">
          <div className="hero-copy">
            <p className="eyebrow">MEPS 2023 Static Explorer</p>
            <h1>Affordability, delay, and fairness across income, education, and race</h1>
            <p className="hero-text">
              This local explorer uses MEPS 2023 to trace affordability barriers,
              delayed care, access gaps, and low-risk subsidy questions through one
              shared lens. Every card recomputes its chart, labels, and inference
              from the active filters so you can test how burden shifts across
              insurance, income, education, age, region, student status, and broad
              race groups.
            </p>
          </div>
          <div className="hero-stats">
            <div>
              <span>Filtered cohort</span>
              <strong>{filteredRows.length.toLocaleString()}</strong>
            </div>
            <div>
              <span>Weighted population</span>
              <strong>{formatPopulation(weightedTotal(filteredRows, deferredFilters.weightMode))}</strong>
            </div>
            <div>
              <span>Reporting mode</span>
              <strong>{deferredFilters.weightMode}</strong>
            </div>
          </div>
        </header>

        <nav className="section-nav">
          <a href="#overview">Overview</a>
          {activeSections.map((section) => (
            <a href={`#${section.id}`} key={section.id}>
              {section.title}
            </a>
          ))}
        </nav>

        <section className="overview-section" id="overview">
          <div className="section-heading">
            <p className="eyebrow">Minimum Graphics Pack</p>
            <h2>Landing summary</h2>
            <p>
              This top panel turns the core graphics pack into a fairness-and-acquisition
              snapshot: six KPI tiles, one affordability funnel, and featured cuts that
              surface income, education, and broad race patterns before you dive deeper.
            </p>
          </div>
          <p className="section-note">{metadata.proxyNotes.fairness}</p>

          <div className="kpi-grid">
            {overviewKpis.map((kpi) => (
              <article className="kpi-card" key={kpi.title}>
                <p>{kpi.title}</p>
                <strong>{formatPopulation(kpi.estimate)}</strong>
                <span>{formatPercent(kpi.share)} of valid responses</span>
              </article>
            ))}
          </div>

          <article className="hero-chart-card">
            <div className="question-head">
              <div>
                <p className="eyebrow">overview funnel</p>
                <h3>Affordability severity ladder</h3>
              </div>
            </div>
            <p className="reading-guide">
              Read this as a severity summary rather than a causal sequence: the
              full filtered population at the top, then the subset reporting delay
              due to cost, then the subset reporting direct inability to afford
              care.
            </p>
            <div className="chart-shell">
              <ReactECharts option={funnel.option} style={{ height: 340, width: "100%" }} />
            </div>
            <div className="inference-block">
              <p className="eyebrow">Inference</p>
              <p>{funnel.narrative}</p>
            </div>
            <p className="data-note">
              Variables:{" "}
              {[
                metadata.variableLabels.delay_any ?? "delay_any",
                metadata.variableLabels.afford_any ?? "afford_any",
                metadata.variableLabels.PERWT23F ?? "PERWT23F",
              ].join(", ")}
              . Weighting: {deferredFilters.weightMode}.
            </p>
          </article>

          <div className="overview-grid">
            {metadata.overview.highlightQuestionIds.map((id) => {
              const meta = metadata.questions.find((question) => question.id === id);
              if (!meta) return null;
              return (
                <QuestionCard
                  key={id}
                  rows={filteredRows}
                  metadata={metadata}
                  filters={deferredFilters}
                  meta={meta}
                  spec={getQuestionSpec(id)}
                />
              );
            })}
          </div>
        </section>

        {activeSections.map((section) => {
          const sectionQuestions = metadata.questions.filter(
            (question) => question.section === section.id,
          );
          return (
            <section className="detail-section" id={section.id} key={section.id}>
              <div className="section-heading">
                <p className="eyebrow">{section.title}</p>
                <h2>{section.title}</h2>
                <p>{section.description}</p>
              </div>

              {section.id === "no_usc" ? (
                <p className="section-note">{metadata.proxyNotes.no_usc}</p>
              ) : null}
              {section.id === "low_risk" ? (
                <>
                  <p className="section-note">{metadata.proxyNotes.low_risk}</p>
                  <p className="section-note">{metadata.proxyNotes.fairness}</p>
                </>
              ) : null}

              <div className="question-list">
                {sectionQuestions.map((meta) => (
                  <QuestionCard
                    key={meta.id}
                    rows={filteredRows}
                    metadata={metadata}
                    filters={deferredFilters}
                    meta={meta}
                    spec={getQuestionSpec(meta.id)}
                  />
                ))}
              </div>
            </section>
          );
        })}
      </main>
    </div>
  );
}
