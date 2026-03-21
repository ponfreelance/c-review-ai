"use client";

import { useState, useRef } from "react";

// --- 型定義 ---
interface Risk {
  line: string;
  category: string;
  issue: string;
  risk: string;
  recommendation: string;
}

interface ReviewResult {
  risks: Risk[];
  risk_count: number;
}

// API URL（Docker 内では環境変数から取得、ブラウザからはlocalhost）
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- リスクカード ---
function RiskCard({ risk, index }: { risk: Risk; index: number }) {
  return (
    <div className="border border-red-200 bg-white rounded-lg p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        <span className="bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-0.5 rounded">
          Risk {index + 1}
        </span>
        {risk.line && risk.line !== "N/A" && (
          <span className="bg-gray-100 text-gray-700 text-xs px-2 py-0.5 rounded">
            Line: {risk.line}
          </span>
        )}
      </div>
      <table className="w-full text-sm">
        <tbody>
          <tr className="border-b border-gray-100">
            <td className="py-1 pr-3 font-medium text-gray-600 w-36">Category</td>
            <td className="py-1">{risk.category}</td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-1 pr-3 font-medium text-gray-600">Issue</td>
            <td className="py-1">{risk.issue}</td>
          </tr>
          <tr className="border-b border-gray-100">
            <td className="py-1 pr-3 font-medium text-gray-600">Risk</td>
            <td className="py-1">{risk.risk}</td>
          </tr>
          <tr>
            <td className="py-1 pr-3 font-medium text-gray-600">Recommendation</td>
            <td className="py-1">{risk.recommendation}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

// --- メインページ ---
export default function ReviewPage() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // テキスト入力でレビュー
  const handleReview = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `HTTP ${res.status}`);
      }
      const data: ReviewResult = await res.json();
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "レビューに失敗しました");
    } finally {
      setLoading(false);
    }
  };

  // ファイルアップロードでレビュー
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_URL}/review/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `HTTP ${res.status}`);
      }
      const data: ReviewResult = await res.json();
      // アップロードしたファイルの内容をテキストエリアにも表示
      const text = await file.text();
      setCode(text);
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "レビューに失敗しました");
    } finally {
      setLoading(false);
      // ファイル入力をリセット
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* ヘッダー */}
      <h1 className="text-2xl font-bold mb-1">c-review-ai</h1>
      <p className="text-gray-500 text-sm mb-6">
        C言語コードの危険箇所を検出するレビューAI
      </p>

      {/* 入力エリア */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cコードを入力
        </label>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder={"#include <stdio.h>\nint main() {\n  ...\n}"}
          className="w-full h-64 p-3 border border-gray-300 rounded-md font-mono text-sm resize-y focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />

        <div className="flex items-center gap-3 mt-3">
          {/* レビュー実行 */}
          <button
            onClick={handleReview}
            disabled={loading || !code.trim()}
            className="px-5 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "レビュー中..." : "レビュー実行"}
          </button>

          {/* ファイルアップロード */}
          <label className="px-4 py-2 border border-gray-300 rounded-md text-sm cursor-pointer hover:bg-gray-50">
            ファイル選択 (.c .h)
            <input
              ref={fileInputRef}
              type="file"
              accept=".c,.h"
              onChange={handleUpload}
              className="hidden"
              disabled={loading}
            />
          </label>
        </div>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {/* 結果表示 */}
      {result && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">検出結果</h2>
            <span className="bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
              リスク合計: {result.risk_count}件
            </span>
          </div>

          {result.risks.length === 0 ? (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
              リスクは検出されませんでした。
            </div>
          ) : (
            <div className="space-y-3">
              {result.risks.map((risk, i) => (
                <RiskCard key={i} risk={risk} index={i} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
