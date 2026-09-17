import { ButtonHTMLAttributes, HTMLAttributes } from "react";

export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white p-6 shadow-sm ${className}`}
      {...props}
    />
  );
}

export function Button({
  className = "",
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
}) {
  const styles = {
    primary:
      "bg-brand-600 text-white hover:bg-brand-700 disabled:bg-slate-300",
    secondary:
      "bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 disabled:text-slate-400",
    ghost: "text-brand-600 hover:bg-brand-50 disabled:text-slate-400",
  }[variant];

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${styles} ${className}`}
      {...props}
    />
  );
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      {...props}
    />
  );
}

export function Textarea(
  props: React.TextareaHTMLAttributes<HTMLTextAreaElement>
) {
  return (
    <textarea
      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
      {...props}
    />
  );
}

export function Label({ children }: { children: React.ReactNode }) {
  return (
    <label className="mb-1 block text-sm font-medium text-slate-700">
      {children}
    </label>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger";
}) {
  const styles = {
    neutral: "bg-slate-100 text-slate-700",
    success: "bg-emerald-100 text-emerald-700",
    warning: "bg-amber-100 text-amber-700",
    danger: "bg-red-100 text-red-700",
  }[tone];

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles}`}
    >
      {children}
    </span>
  );
}

export function Alert({
  children,
  tone = "danger",
  className = "",
}: {
  children: React.ReactNode;
  tone?: "danger" | "warning" | "success";
  className?: string;
}) {
  const styles = {
    danger: "bg-red-50 text-red-700 border-red-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
  }[tone];

  return (
    <div
      className={`rounded-lg border px-4 py-3 text-sm ${styles} ${className}`}
      role="alert"
    >
      {children}
    </div>
  );
}

export function Spinner() {
  return (
    <div
      className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600"
      role="status"
      aria-label="Loading"
    />
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
      <p className="text-sm font-medium text-slate-700">{title}</p>
      {description && (
        <p className="max-w-sm text-sm text-slate-500">{description}</p>
      )}
      {action}
    </div>
  );
}
