import Link from "next/link";
import { Button, Card } from "@/components/ui";

const features = [
  {
    title: "Live market scan",
    description:
      "Reads live Google Jobs postings through SerpApi and ranks the skills you're missing by how many real jobs each one unlocks per week of learning.",
  },
  {
    title: "Skill momentum",
    description:
      "12-month Google Trends data shows which skills are rising or falling in India, so you don't spend months on one that's fading.",
  },
  {
    title: "ATS CV builder",
    description:
      "Tailors your CV to any job using its exact keywords, without inventing experience. Download a PDF or an editable DOCX.",
  },
  {
    title: "Evidence, not guesses",
    description:
      "Every recommendation links to the live postings behind it, so you can check the numbers yourself.",
  },
];

export default function Home() {
  return (
    <div className="space-y-16">
      <section className="flex flex-col items-start gap-6 py-12">
        <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
          SkillRadar
        </span>
        <h1 className="max-w-2xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Learn the skill that unlocks the most jobs.
        </h1>
        <p className="max-w-xl text-lg text-slate-600">
          SkillRadar scans the live job market, tells you which skill to learn
          next and what it&apos;s worth in real job postings, then builds an
          ATS-ready CV that proves what you can do.
        </p>
        <div className="flex gap-3">
          <Link href="/register">
            <Button className="px-6 py-3 text-base">Get started free</Button>
          </Link>
          <Link href="/login">
            <Button variant="secondary" className="px-6 py-3 text-base">
              Sign in
            </Button>
          </Link>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2">
        {features.map((feature) => (
          <Card key={feature.title}>
            <h2 className="text-base font-semibold text-slate-900">
              {feature.title}
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              {feature.description}
            </p>
          </Card>
        ))}
      </section>
    </div>
  );
}
