"use client";
import FileUpload from '../components/FileUpload';
import QueryInput from '../components/QueryInput';
import ChartView from '../components/ChartView';
import { useState, useRef } from 'react';

export default function Home() {
  const [step, setStep] = useState<'landing' | 'upload' | 'dashboard'>('landing');
  const [schema, setSchema] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [chat, setChat] = useState<Array<{role: string, content: string}>>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Handler for chat input
  const handleChat = async (prompt: string) => {
    setChat(prev => [...prev, { role: 'user', content: prompt }]);
    setLoading(true);
    const res = await fetch('http://localhost:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    setChartData(data);
    setChat(prev => [...prev, { role: 'assistant', content: `Chart generated for: ${prompt}` }]);
    setLoading(false);
  };

  // Handler for file upload
  const handleSchema = (schema: any) => {
    setSchema(schema);
    setStep('dashboard');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-100 to-pink-200 flex flex-col items-center justify-center">
      {step === 'landing' && (
        <section className="flex flex-col items-center justify-center h-screen w-full">
          <h1 className="text-5xl font-extrabold text-pink-700 mb-6 drop-shadow-lg">AI Data Dashboard Generator</h1>
          <p className="max-w-2xl text-center text-lg text-purple-700 mb-8">
            Effortlessly turn your CSV data into beautiful, interactive dashboards using AI. Upload your dataset, ask questions in natural language, and instantly visualize insights with stunning charts. Powered by LLMs and DuckDB for blazing-fast analytics.
          </p>
          <button
            className="px-8 py-4 rounded-full bg-gradient-to-r from-pink-400 to-purple-400 text-white text-xl font-semibold shadow-lg hover:scale-105 transition mb-2"
            onClick={() => setStep('upload')}
          >
            Try Now
          </button>
        </section>
      )}
      {step === 'upload' && (
        <section className="flex flex-col items-center justify-center h-screen w-full">
          <div className="bg-white/80 rounded-2xl shadow-xl p-10 flex flex-col items-center">
            <h2 className="text-2xl font-bold text-pink-700 mb-4">Upload your CSV dataset</h2>
            <FileUpload onSchema={handleSchema} />
            <button className="mt-6 text-purple-500 underline" onClick={() => setStep('landing')}>Back to Home</button>
          </div>
        </section>
      )}
      {step === 'dashboard' && (
        <section className="fixed inset-0 flex items-center justify-center z-10">
          <div className="relative w-[90vw] h-[80vh] flex rounded-3xl shadow-2xl overflow-hidden bg-white/90 border-2 border-pink-200">
            {/* Left: Graphs */}
            <div className="flex-1 bg-gradient-to-br from-pink-50 to-purple-50 p-8 flex flex-col">
              <h2 className="text-2xl font-bold text-pink-700 mb-2">Dashboard</h2>
              <div className="flex-1 flex items-center justify-center">
                <ChartView chartData={chartData} />
              </div>
              {schema && (
                <div className="mt-6 bg-white/70 rounded-lg p-4 text-xs text-gray-700 shadow-inner">
                  <div className="font-semibold text-purple-600 mb-1">Columns:</div>
                  <div className="mb-1">{schema.columns?.join(', ')}</div>
                  <div className="font-semibold text-purple-600 mb-1">Sample Rows:</div>
                  <pre className="whitespace-pre-wrap">{JSON.stringify(schema.sample_rows, null, 2)}</pre>
                </div>
              )}
            </div>
            {/* Right: Floating Chatbot */}
            <div className="w-[420px] bg-white/80 border-l border-pink-200 flex flex-col h-full relative">
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {chat.map((msg, idx) => (
                  <div key={idx} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                    <div className={`inline-block px-4 py-2 rounded-2xl shadow-md max-w-[80%] ${msg.role === 'user' ? 'bg-pink-200 text-pink-900 ml-auto' : 'bg-purple-100 text-purple-900 mr-auto'}`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="text-left">
                    <div className="inline-block px-4 py-2 rounded-2xl shadow-md bg-purple-100 text-purple-900 mr-auto animate-pulse">Thinking...</div>
                  </div>
                )}
              </div>
              <div className="p-4 border-t border-pink-100 bg-white/90">
                <form
                  className="flex gap-2"
                  onSubmit={e => {
                    e.preventDefault();
                    const prompt = inputRef.current?.value;
                    if (prompt) {
                      handleChat(prompt);
                      inputRef.current.value = '';
                    }
                  }}
                >
                  <input
                    ref={inputRef}
                    type="text"
                    className="flex-1 rounded-full border border-pink-200 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-pink-300 bg-white/80 text-pink-900"
                    placeholder="Ask a question about your data..."
                  />
                  <button
                    type="submit"
                    className="bg-gradient-to-r from-pink-400 to-purple-400 text-white px-6 py-2 rounded-full font-semibold shadow-md hover:scale-105 transition"
                    disabled={loading}
                  >
                    Send
                  </button>
                </form>
              </div>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
