"use client";

import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type LabMarkdownVariant = "user" | "assistant";

interface LabMarkdownMessageProps {
  content: string;
  variant: LabMarkdownVariant;
}

function buildComponents(variant: LabMarkdownVariant): Components {
  const isUser = variant === "user";

  const heading = "font-semibold tracking-tight";
  const muted = isUser ? "text-zinc-300" : "text-zinc-600 dark:text-zinc-400";
  const strong = isUser ? "font-semibold text-white" : "font-semibold text-zinc-900 dark:text-zinc-50";
  const codeBg = isUser
    ? "bg-white/15 text-zinc-100"
    : "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-100";
  const preBg = isUser
    ? "bg-black/25 text-zinc-100"
    : "bg-zinc-100 text-zinc-800 dark:bg-zinc-900 dark:text-zinc-100";
  const link = isUser
    ? "text-amber-200 underline underline-offset-2"
    : "text-violet-700 underline underline-offset-2 dark:text-violet-300";
  const hr = isUser ? "border-white/20" : "border-zinc-200 dark:border-zinc-700";
  const blockquote = isUser
    ? "border-white/30 text-zinc-200"
    : "border-zinc-300 text-zinc-600 dark:border-zinc-600 dark:text-zinc-400";

  return {
    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
    h1: ({ children }) => (
      <h1 className={`mb-2 mt-3 text-base ${heading} first:mt-0`}>{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className={`mb-2 mt-3 text-sm ${heading} first:mt-0`}>{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className={`mb-1.5 mt-2 text-sm ${heading} first:mt-0`}>{children}</h3>
    ),
    strong: ({ children }) => <strong className={strong}>{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    ul: ({ children }) => (
      <ul className={`mb-2 list-disc space-y-1 pl-5 last:mb-0 ${muted}`}>{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className={`mb-2 list-decimal space-y-1 pl-5 last:mb-0 ${muted}`}>{children}</ol>
    ),
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
    hr: () => <hr className={`my-3 ${hr}`} />,
    blockquote: ({ children }) => (
      <blockquote className={`my-2 border-l-2 pl-3 text-sm ${blockquote}`}>
        {children}
      </blockquote>
    ),
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className={link}>
        {children}
      </a>
    ),
    code: ({ className, children }) => {
      if (!className) {
        return (
          <code className={`rounded px-1 py-0.5 text-[0.85em] ${codeBg}`}>{children}</code>
        );
      }
      return <code className={`block text-xs ${codeBg}`}>{children}</code>;
    },
    pre: ({ children }) => (
      <pre className={`my-2 overflow-x-auto rounded-lg p-3 text-xs last:mb-0 ${preBg}`}>
        {children}
      </pre>
    ),
    table: ({ children }) => (
      <div className="my-2 overflow-x-auto last:mb-0">
        <table className="w-full border-collapse text-left text-xs">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th
        className={
          isUser
            ? "border border-white/20 bg-white/10 px-2 py-1 font-medium"
            : "border border-zinc-200 bg-zinc-50 px-2 py-1 font-medium dark:border-zinc-700 dark:bg-zinc-900"
        }
      >
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td
        className={
          isUser
            ? "border border-white/20 px-2 py-1"
            : "border border-zinc-200 px-2 py-1 dark:border-zinc-700"
        }
      >
        {children}
      </td>
    ),
  };
}

/** Render nội dung chat Lab dưới dạng Markdown (GFM). */
export function LabMarkdownMessage({ content, variant }: LabMarkdownMessageProps) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={buildComponents(variant)}>
      {content}
    </ReactMarkdown>
  );
}
