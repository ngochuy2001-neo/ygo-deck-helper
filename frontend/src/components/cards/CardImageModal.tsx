"use client";

import { useEffect, useRef } from "react";

import { cardStaticUrl } from "@/lib/cardImages";
import type { CardDetail } from "@/types";

interface CardImageModalProps {
  detail: CardDetail;
  open: boolean;
  onClose: () => void;
}

function croppedArtworkUrl(detail: CardDetail): string | null {
  const img = detail.images.find((i) => i.is_default) ?? detail.images[0];
  return cardStaticUrl(img?.image_cropped_path);
}

export function CardImageModal({ detail, open, onClose }: CardImageModalProps) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const cropped = croppedArtworkUrl(detail);

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);
    closeRef.current?.focus();

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="card-image-modal-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        aria-label="Đóng"
        onClick={onClose}
      />

      <div className="relative z-10 flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-xl border border-zinc-700 bg-zinc-950 shadow-2xl">
        <div className="flex shrink-0 items-center justify-between border-b border-zinc-800 px-4 py-3">
          <h2
            id="card-image-modal-title"
            className="truncate pr-4 text-sm font-semibold text-zinc-100"
          >
            {detail.name}
          </h2>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-lg px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800 hover:text-white"
          >
            Đóng
          </button>
        </div>

        <div className="flex min-h-0 flex-1 items-center justify-center p-4 sm:p-6">
          {cropped ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={cropped}
              alt={`${detail.name} — artwork`}
              className="max-h-[calc(92vh-4.5rem)] w-full object-contain"
            />
          ) : (
            <p className="text-sm text-zinc-500">Chưa có ảnh artwork (crop)</p>
          )}
        </div>
      </div>
    </div>
  );
}
