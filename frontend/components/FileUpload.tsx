import React, { useRef } from 'react';

export default function FileUpload({ onSchema }: { onSchema: (schema: any) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    const formData = new FormData();
    formData.append('file', e.target.files[0]);
    const res = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    onSchema(data);
  };

  return (
    <div className="flex flex-col items-center">
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        className="mb-2"
        onChange={handleChange}
      />
    </div>
  );
}
