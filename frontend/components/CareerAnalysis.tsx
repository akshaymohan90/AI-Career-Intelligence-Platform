import { Badge, Card } from "@/components/ui";
import type { CareerAnalysis } from "@/lib/api";

const priorityTone: Record<string, "danger" | "warning" | "neutral"> = {
  high: "danger",
  medium: "warning",
  low: "neutral",
};

export default function CareerAnalysisResult({
  data,
}: {
  data: CareerAnalysis;
}) {
  return (
    <Card className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-900">
          Career analysis
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-brand-600">
            {Math.round(data.match_score)}%
          </span>
          <span className="text-sm text-slate-500">match</span>
        </div>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-brand-600"
          style={{ width: `${Math.min(100, Math.max(0, data.match_score))}%` }}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="mb-2 text-sm font-medium text-slate-700">
            Matched skills ({data.matched_skills.length})
          </p>
          <div className="flex flex-wrap gap-2">
            {data.matched_skills.length === 0 && (
              <span className="text-sm text-slate-500">None</span>
            )}
            {data.matched_skills.map((skill) => (
              <Badge key={skill} tone="success">
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <p className="mb-2 text-sm font-medium text-slate-700">
            Missing skills ({data.missing_skills.length})
          </p>
          <div className="flex flex-wrap gap-2">
            {data.missing_skills.length === 0 && (
              <span className="text-sm text-slate-500">None</span>
            )}
            {data.missing_skills.map((skill) => (
              <Badge key={skill} tone="danger">
                {skill}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      {data.recommendations.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-medium text-slate-700">
            Recommendations
          </p>
          <ul className="space-y-2">
            {data.recommendations.map((item) => (
              <li
                key={item.skill}
                className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
              >
                <span className="text-slate-700">{item.skill}</span>
                <Badge tone={priorityTone[item.priority?.toLowerCase()] ?? "neutral"}>
                  {item.priority}
                </Badge>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
