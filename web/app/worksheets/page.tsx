"use client";

import { useState, useEffect } from "react";
import { Printer, Download, Loader2, FileText, Sparkles } from "lucide-react";

interface WorksheetOptions {
  subject: string;
  questionType: string;
  count: number;
  mode: "practice" | "mock";
  randomize: boolean;
  title: string;
}

interface SubjectData {
  id: string;
  name: string;
  types: string[];
}

export default function WorksheetsPage() {
  const [loading, setLoading] = useState(false);
  const [generatedHtml, setGeneratedHtml] = useState<string | null>(null);
  const [options, setOptions] = useState<WorksheetOptions>({
    subject: "",
    questionType: "",
    count: 20,
    mode: "practice",
    randomize: true,
    title: "",
  });

  const subjects: SubjectData[] = [
    {
      id: "verbal_reasoning",
      name: "Verbal Reasoning",
      types: ["synonyms", "antonyms", "analogies", "odd_one_out", "code_words", "letter_sequences", "hidden_words", "compound_words"],
    },
    {
      id: "mathematics",
      name: "Mathematics",
      types: ["arithmetic", "fractions", "percentages", "ratio", "algebra", "geometry", "word_problems", "sequences"],
    },
    {
      id: "english",
      name: "English",
      types: ["spelling", "punctuation", "grammar", "vocabulary"],
    },
  ];

  const selectedSubjectData = subjects.find((s) => s.id === options.subject);

  const handleGenerate = async () => {
    setLoading(true);
    setGeneratedHtml(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/worksheets/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: options.subject || null,
          question_type: options.questionType || null,
          count: options.count,
          mode: options.mode,
          randomize: options.randomize,
          title: options.title || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate worksheet");
      }

      const data = await response.json();
      setGeneratedHtml(data.html);
    } catch (error) {
      console.error("Error generating worksheet:", error);
      alert("Failed to generate worksheet. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    if (!generatedHtml) return;

    const printWindow = window.open("", "_blank");
    if (printWindow) {
      printWindow.document.write(generatedHtml);
      printWindow.document.close();
      setTimeout(() => {
        printWindow.print();
      }, 250);
    }
  };

  const handleDownload = () => {
    if (!generatedHtml) return;

    const blob = new Blob([generatedHtml], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `worksheet-${Date.now()}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg">
              <Printer className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
                Printable Worksheets
              </h1>
              <p className="text-slate-600 dark:text-slate-400">
                Create custom practice worksheets for offline study
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Options Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6 space-y-6">
              <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-4">
                  Worksheet Options
                </h2>

                {/* Subject */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Subject
                  </label>
                  <select
                    value={options.subject}
                    onChange={(e) =>
                      setOptions({ ...options, subject: e.target.value, questionType: "" })
                    }
                    className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Subjects (Mixed)</option>
                    {subjects.map((subject) => (
                      <option key={subject.id} value={subject.id}>
                        {subject.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Question Type */}
                {selectedSubjectData && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Question Type
                    </label>
                    <select
                      value={options.questionType}
                      onChange={(e) =>
                        setOptions({ ...options, questionType: e.target.value })
                      }
                      className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">All Types (Mixed)</option>
                      {selectedSubjectData.types.map((type) => (
                        <option key={type} value={type}>
                          {type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Number of Questions */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Number of Questions: {options.count}
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    step="5"
                    value={options.count}
                    onChange={(e) =>
                      setOptions({ ...options, count: parseInt(e.target.value) })
                    }
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1">
                    <span>5</span>
                    <span>25</span>
                    <span>50</span>
                  </div>
                </div>

                {/* Mode */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Mode
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => setOptions({ ...options, mode: "practice" })}
                      className={`px-4 py-2 rounded-lg border transition-all ${
                        options.mode === "practice"
                          ? "bg-blue-500 text-white border-blue-500 shadow-lg"
                          : "bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600 hover:border-blue-400"
                      }`}
                    >
                      <FileText className="w-4 h-4 inline mr-2" />
                      Practice
                    </button>
                    <button
                      onClick={() => setOptions({ ...options, mode: "mock" })}
                      className={`px-4 py-2 rounded-lg border transition-all ${
                        options.mode === "mock"
                          ? "bg-purple-500 text-white border-purple-500 shadow-lg"
                          : "bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600 hover:border-purple-400"
                      }`}
                    >
                      <Sparkles className="w-4 h-4 inline mr-2" />
                      Mock Exam
                    </button>
                  </div>
                </div>

                {/* Randomize */}
                <div className="mb-4">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={options.randomize}
                      onChange={(e) =>
                        setOptions({ ...options, randomize: e.target.checked })
                      }
                      className="w-5 h-5 rounded border-slate-300 text-blue-500 focus:ring-2 focus:ring-blue-500"
                    />
                    <div>
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        Randomize Questions
                      </span>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Each worksheet will be unique
                      </p>
                    </div>
                  </label>
                </div>

                {/* Custom Title */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Custom Title (Optional)
                  </label>
                  <input
                    type="text"
                    value={options.title}
                    onChange={(e) => setOptions({ ...options, title: e.target.value })}
                    placeholder="e.g., Week 1 Practice"
                    className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Worksheet
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Info Card */}
            <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
              <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 text-sm">
                📋 About Worksheets
              </h3>
              <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
                <li>• Print-optimized format for offline practice</li>
                <li>• Answer key included on last page</li>
                <li>• Perfect for weekly homework or revision</li>
                <li>• Randomization ensures unique worksheets</li>
              </ul>
            </div>
          </div>

          {/* Preview Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                  Preview
                </h2>
                {generatedHtml && (
                  <div className="flex gap-2">
                    <button
                      onClick={handlePrint}
                      className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2 shadow-lg"
                    >
                      <Printer className="w-4 h-4" />
                      Print
                    </button>
                    <button
                      onClick={handleDownload}
                      className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center gap-2 shadow-lg"
                    >
                      <Download className="w-4 h-4" />
                      Download HTML
                    </button>
                  </div>
                )}
              </div>

              {!generatedHtml && !loading && (
                <div className="text-center py-20">
                  <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-600 flex items-center justify-center">
                    <Printer className="w-10 h-10 text-slate-400 dark:text-slate-500" />
                  </div>
                  <p className="text-slate-500 dark:text-slate-400 mb-2">
                    Configure your worksheet options and click Generate
                  </p>
                  <p className="text-sm text-slate-400 dark:text-slate-500">
                    Your worksheet preview will appear here
                  </p>
                </div>
              )}

              {loading && (
                <div className="text-center py-20">
                  <Loader2 className="w-12 h-12 mx-auto mb-4 text-blue-500 animate-spin" />
                  <p className="text-slate-600 dark:text-slate-400">
                    Generating your worksheet...
                  </p>
                </div>
              )}

              {generatedHtml && (
                <div className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                  <iframe
                    srcDoc={generatedHtml}
                    className="w-full h-[800px] bg-white"
                    title="Worksheet Preview"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
