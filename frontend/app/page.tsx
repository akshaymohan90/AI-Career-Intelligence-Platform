import Link from "next/link";
import { Button, Card } from "@/components/ui";

const features = [
  {
    title: "Resume parsing",
    description:
      "Upload a resume and the backend extracts text and skills automatically.",
  },
  {
    title: "Job matching",
    description:
      "Compare a resume against any job posting to get a match score and skill overlap.",
  },
  {
    title: "Skill-gap analysis",
    description:
      "See exactly which required skills are missing and get prioritized recommendations.",
  },
  {
    title: "AI career assistant",
    description:
      "Ask follow-up questions about a job/resume pairing and get an AI-generated answer.",
  },
];

export default function Home() {
  return (
    <div className="space-y-16">
      <section className="flex flex-col items-start gap-6 py-12">
        <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
          AI Career Intelligence Platform
        </span>
        <h1 className="max-w-2xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Know exactly where your resume stands against any job.
        </h1>
        <p className="max-w-xl text-lg text-slate-600">
          Upload your resume, pick a job posting, and get a match score,
          missing-skill breakdown, and AI-generated advice on how to close
          the gap.
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
