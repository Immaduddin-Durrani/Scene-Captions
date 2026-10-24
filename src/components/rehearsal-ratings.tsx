"use client";
import { ratingQuestions } from "@/lib/experiment";

export function RehearsalRatings({ ratings, onRate }: { ratings: Record<string, number>; onRate: (key: string, value: number) => void }) {
  return (
<div className="ratings">{ratingQuestions.map((question) => <fieldset key={question.key}><legend>{question.label}</legend><div className="rating-options">{[1, 2, 3, 4, 5, 6, 7].map((value) => <label key={value}><input type="radio" name={question.key} value={value} checked={ratings[question.key] === value} onChange={() => onRate(question.key, value)} /><span>{value}</span></label>)}</div><div className="range-labels"><span>1 · {question.low}</span><span>7 · {question.high}</span></div></fieldset>)}</div>
  );
}
