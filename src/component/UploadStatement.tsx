import React, { useState } from "react";

interface HistoryEntry {
  filename: string;
  timestamp: string;
}

export default function UploadStatement() {
    const [file, setFile] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [history, setHistory] = useState<HistoryEntry[]>([]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0] || null;
        setFile(selected ? selected.name : null);
        setMessage("");
    };

    const handleUpload = async () => {
        if (!file) {
          setMessage("Selecciona un archivo PDF antes de continuar.");
          return;
        }
      
        setLoading(true);
        const nameFile = `${file.replace(/\.[^/.]+$/, "").replace(/ /g, "_")}.json`;

        const formData = new FormData();
        const inputFile = (document.querySelector('input[type="file"]') as HTMLInputElement)?.files?.[0];
        if (inputFile) {
          formData.append("file", inputFile);
        }
      
        try {
          const response = await fetch("http://localhost:8000/api/v1/upload-pdf", {
            method: "POST",
            body: formData,
          });
      
          if (!response.ok) throw new Error("Error al procesar el archivo.");
      
          // 🟢 Convertir a blob y descargar el archivo
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
      
          const a = document.createElement("a");
          a.href = url;
          a.download = nameFile; // Reemplaza la extensión por .json
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
      
          setMessage("Archivo procesado y descargado correctamente.");
        } catch (err) {
          console.error(err);
          setMessage("Ocurrió un error al procesar el archivo.");
        } finally {
          setLoading(false);
        }
      };

    return (
        <div className="bg-gray-100 p-6 rounded-2xl shadow max-w-[66rem] mx-auto mt-10">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Cargar Estado de Cuenta
            </h2>

            <div className="mb-4">
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="text-sm text-gray-700"
                />
                {file && (
                    <p className="text-sm text-gray-600 mt-1">
                        Archivo seleccionado: <span className="font-medium">{file}</span>
                    </p>
                )}
            </div>

            <button
                onClick={handleUpload}
                disabled={loading}
                className="bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2 px-6 rounded-lg transition duration-300 disabled:opacity-50"
            >
                {loading ? "Procesando..." : "Subir y Procesar"}
            </button>

            {message && (
                <p className="mt-4 text-sm text-gray-600 font-medium">{message}</p>
            )}

            {history.length > 0 && (
                <div className="mt-6">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">
                        Archivos Procesados Recientemente:
                    </h3>
                    <ul className="space-y-1 text-sm text-gray-600 list-disc list-inside">
                        {history.map((entry, idx) => (
                            <li key={idx}>
                                <span className="font-medium">{entry.filename}</span> –{" "}
                                <span className="text-xs text-gray-500">{entry.timestamp}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
