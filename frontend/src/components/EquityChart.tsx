import { useEffect, useRef } from "react";
import { createChart, ColorType, type IChartApi, type ISeriesApi, type UTCTimestamp } from "lightweight-charts";
import type { EquityPoint } from "../types";

interface Props {
  equityCurve: EquityPoint[];
  marketMeta: string;
  engineText: string;
  engineTone: "neutral" | "ok" | "warn" | "danger";
  dataSource: string;
  dataSourceTone: "neutral" | "ok" | "warn" | "danger";
}

export function EquityChart({
  equityCurve,
  marketMeta,
  engineText,
  engineTone,
  dataSource,
  dataSourceTone,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Area"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 360,
      layout: {
        background: { type: ColorType.Solid, color: "#101214" },
        textColor: "#9ca6a6",
      },
      grid: {
        vertLines: { color: "#2f343a" },
        horzLines: { color: "#2f343a" },
      },
      rightPriceScale: { borderColor: "#343941" },
      timeScale: { borderColor: "#343941" },
    });
    const series = chart.addAreaSeries({
      lineColor: "#3ddc84",
      topColor: "rgba(61, 220, 132, 0.4)",
      bottomColor: "rgba(61, 220, 132, 0.0)",
      lineWidth: 2,
    });
    chartRef.current = chart;
    seriesRef.current = series;

    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current) return;
    const data = equityCurve
      .map((p) => {
        const t = Math.floor(Date.parse(p.timestamp) / 1000);
        if (Number.isNaN(t)) return null;
        return { time: t as UTCTimestamp, value: Number(p.equity) };
      })
      .filter((p): p is { time: UTCTimestamp; value: number } => p !== null);
    seriesRef.current.setData(data);
    if (chartRef.current && data.length) {
      chartRef.current.timeScale().fitContent();
    }
  }, [equityCurve]);

  return (
    <section className="chart-section">
      <div className="panel-head">
        <div>
          <h2>Equity Curve</h2>
          <p className="subline">{marketMeta}</p>
        </div>
        <div className="head-pills">
          <span className={`status-pill ${engineTone}`}>{engineText}</span>
          <span className={`status-pill ${dataSourceTone}`}>{dataSource}</span>
        </div>
      </div>
      <div ref={containerRef} className="equity-chart-container" />
    </section>
  );
}
