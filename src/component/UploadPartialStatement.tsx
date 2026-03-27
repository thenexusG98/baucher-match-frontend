import React, { useState } from "react";

interface HistoryEntry {
  filename: string;
  timestamp: string;
}

interface ProcessedFile {
  filename: string;
  timestamp: string;
  month: string;
  ingreso: number;
  totalCount?: number;
}

interface UploadPartialStatementProps {
  onFileProcessed?: (fileData: ProcessedFile) => void;
}

export default function UploadPartialStatement({ onFileProcessed }: UploadPartialStatementProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  // Estados para PDF bloqueado
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [pdfPassword, setPdfPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [checkingLock, setCheckingLock] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] || null;
    setFile(selected);
    setMessage("");
    setPdfPassword("");
    setPasswordError("");
  };

  const checkIfPdfLocked = async (selectedFile: File): Promise<boolean> => {
    const formData = new FormData();
    formData.append("file", selectedFile);
    const response = await fetch("http://localhost:8000/api/v1/check-pdf-locked", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error("Error al verificar el archivo PDF.");
    const data = await response.json();
    return data.locked as boolean;
  };

  const handleUpload = async (password?: string) => {
    if (!file) {
      setMessage("Selecciona un archivo PDF antes de continuar.");
      return;
    }

    // Si no tenemos contraseña aún, verificar si el PDF está bloqueado
    if (!password) {
      setCheckingLock(true);
      try {
        const locked = await checkIfPdfLocked(file);
        if (locked) {
          setCheckingLock(false);
          setShowPasswordModal(true);
          return;
        }
      } catch (err) {
        setCheckingLock(false);
        setMessage("Error al verificar el archivo PDF.");
        return;
      }
      setCheckingLock(false);
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    if (password) {
      formData.append("password", password);
    }

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/extract-partial-csv",
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.status === 401) {
        // Contraseña incorrecta
        setPasswordError("Contraseña incorrecta. Intenta de nuevo.");
        setShowPasswordModal(true);
        setLoading(false);
        return;
      }
      if (!response.ok) throw new Error("Error al procesar el archivo.");

      // 🟢 Convertir la respuesta a blob y descargar el archivo CSV

      const blob = await response.blob();

      // Obtener el tiempo de ejecución del header
      const executionTime = parseFloat(
        response.headers.get("X-Execution-Time") || "0"
      );

      // Obtener el total de transacciones del header
      const totalCount = parseInt(
        response.headers.get("X-Total-Count") || "0"
      );

      // Obtener el nombre del archivo del header Content-Disposition
      const contentDisposition = response.headers.get("Content-Disposition");
      const fileNameMatch = contentDisposition?.match(/filename="(.+)"/);
      const fileName = fileNameMatch
        ? fileNameMatch[1]
        : `${file.name.replace(/\.[^/.]+$/, "").replace(/ /g, "_")}.csv`;

      if (blob.size === 0) {
        setMessage("El archivo recibido está vacío.");
        return;
      }

      const url = window.URL.createObjectURL(blob);
      const csvFileName = `${file.name
        .replace(/\.[^/.]+$/, "")
        .replace(/ /g, "_")}.csv`;

      const timestamp = new Date().toLocaleString();
      setHistory((prev) => [
        { filename: csvFileName, timestamp },
        ...prev,
      ]);

      // Extraer el mes del nombre del archivo
      const monthMatch = fileName.match(/(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)/i);
      const monthName = monthMatch ? monthMatch[1] : new Date().toLocaleString('es', { month: 'long' });
      
      const monthMap: { [key: string]: string } = {
        'ENERO': 'Ene', 'FEBRERO': 'Feb', 'MARZO': 'Mar', 'ABRIL': 'Abr',
        'MAYO': 'May', 'JUNIO': 'Jun', 'JULIO': 'Jul', 'AGOSTO': 'Ago',
        'SEPTIEMBRE': 'Sep', 'OCTUBRE': 'Oct', 'NOVIEMBRE': 'Nov', 'DICIEMBRE': 'Dic'
      };
      const month = monthMap[monthName.toUpperCase()] || monthName.substring(0, 3);
      
      // Notificar al componente padre
      if (onFileProcessed) {
        onFileProcessed({
          filename: csvFileName,
          timestamp,
          month,
          ingreso: 500 + Math.floor(Math.random() * 500), // Valor parcial más bajo
          totalCount: totalCount // Total de transacciones del backend
        });
      }

      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setMessage(
        `Archivo CSV procesado y descargado correctamente en ${executionTime.toFixed(
          2
        )} segundos.`
      );
    } catch (err: unknown) {
      console.error(err);
      setMessage("Ocurrió un error al procesar el archivo parcial.");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = () => {
    if (!pdfPassword.trim()) {
      setPasswordError("Por favor ingresa la contraseña.");
      return;
    }
    setPasswordError("");
    setShowPasswordModal(false);
    handleUpload(pdfPassword);
  };

  return (
    <>
      <div className="bg-gray-100 p-6 rounded-2xl shadow max-w-[66rem] mx-auto mt-10">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Cargar Estado de Cuenta Parcial
        </h2>

        <div className="mb-4">
          <input
            type="file"
            name="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2 px-6 rounded-lg transition duration-300 disabled:opacity-50"
          />
          {file && (
            <p className="text-sm text-gray-600 mt-1">
              Archivo seleccionado:{" "}
              <span className="font-medium">{file.name}</span>
            </p>
          )}
        </div>

        <button
          onClick={() => handleUpload()}
          disabled={loading || checkingLock}
          className="bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2 px-6 rounded-lg transition duration-300 disabled:opacity-50"
        >
          {checkingLock ? "Verificando PDF..." : loading ? "Procesando..." : "Subir y Procesar"}
        </button>

        {message && (
          <p className="mt-4 text-sm text-gray-600 font-medium">{message}</p>
        )}
      </div>

      {/* Modal de contraseña para PDF bloqueado */}
      {showPasswordModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md mx-4">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🔒</span>
              <h3 className="text-lg font-semibold text-gray-800">
                PDF Protegido con Contraseña
              </h3>
            </div>
            <p className="text-sm text-gray-600 mb-5">
              El archivo <span className="font-medium">{file?.name}</span> está
              protegido. Ingresa la contraseña para continuar.
            </p>
            <input
              type="password"
              value={pdfPassword}
              onChange={(e) => {
                setPdfPassword(e.target.value);
                setPasswordError("");
              }}
              onKeyDown={(e) => e.key === "Enter" && handlePasswordSubmit()}
              placeholder="Contraseña del PDF"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
              autoFocus
            />
            {passwordError && (
              <p className="text-xs text-red-500 mb-3">{passwordError}</p>
            )}
            <div className="flex gap-3 mt-4">
              <button
                onClick={handlePasswordSubmit}
                disabled={loading}
                className="flex-1 bg-blue-700 hover:bg-blue-800 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 disabled:opacity-50"
              >
                {loading ? "Procesando..." : "Confirmar"}
              </button>
              <button
                onClick={() => {
                  setShowPasswordModal(false);
                  setPdfPassword("");
                  setPasswordError("");
                }}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-lg transition duration-300"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div className="bg-gray-100 p-6 rounded-2xl shadow max-w-[66rem] mx-auto mt-10">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Archivos parciales procesados recientemente:
          </h2>
          <div className="mt-6">
            <ul className="space-y-1 text-sm text-gray-600 list-disc list-inside">
              {history.map((entry, idx) => (
                <li key={idx}>
                  <span className="font-medium">{entry.filename}</span> –{" "}
                  <span className="text-xs text-gray-500">
                    {entry.timestamp}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}

