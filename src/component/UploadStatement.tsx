import React, { useState } from "react";
import Card from "./ui/Card";
import CardContent from "./ui/CardContent";

interface HistoryEntry {
  filename: string;
  timestamp: string;
}

interface ProcessedFile {
  //filename: string;
  //timestamp: string;
  month: string;
  ingreso: number;
  totalCount?: number;
}

interface UploadStatementProps {
  onFileProcessed?: (fileData: ProcessedFile) => void;
}

export default function UploadStatement({
  onFileProcessed,
}: UploadStatementProps) {
  const [file, setFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [totalCounts, setTotalCounts] = useState(0);
  const [fileName, setFileName] = useState("");
  const [fileProcessedTime, setFileProcessedTime] = useState<Date | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] || null;
    setFile(selected);
    setMessage("");
  };

  // Función para calcular el tiempo transcurrido
  const getTimeAgo = (date: Date | null) => {
    if (!date) return "";
    
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / 60000);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) return "Hace unos segundos";
    if (diffInMinutes < 60) return `Hace ${diffInMinutes} minuto${diffInMinutes > 1 ? 's' : ''}`;
    if (diffInHours < 24) return `Hace ${diffInHours} hora${diffInHours > 1 ? 's' : ''}`;
    return `Hace ${diffInDays} día${diffInDays > 1 ? 's' : ''}`;
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Selecciona un archivo PDF antes de continuar.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/download-csv",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Error al procesar el archivo.");

      // 🟢 El backend devuelve el archivo directamente
      const blob = await response.blob();

      // Obtener el tiempo de ejecución del header
      //const executionTime = parseFloat(
        //response.headers.get("X-Execution-Time") || "0"
      //);
      let executionTime = 0;
      let totalCount = 0;
      let ingreso = 0;
      // Obtener el total de transacciones del header
      //const totalCount = parseInt(response.headers.get("X-Total-Count") || "0");

      // Obtener y parsear el JSON del header
      const jsonResString = response.headers.get("X-json");
      let jsonRes = null;

      if (jsonResString) {
        try {
          jsonRes = JSON.parse(jsonResString);

          executionTime = jsonRes.execution_time || 0; // Ejemplo de acceso a una propiedad
          totalCount = jsonRes.total_count || 0; // Ejemplo de acceso a una propiedad
          ingreso = jsonRes.income_month || 0; // Ejemplo de acceso a una propiedad
        } catch (error) {
          console.error("Error al parsear JSON del header:", error);
        }
      }
            
      setTotalCounts(totalCount);
      
      // Obtener el nombre del archivo del header Content-Disposition
      const contentDisposition = response.headers.get("Content-Disposition");
      const fileNameMatch = contentDisposition?.match(/filename="(.+)"/);
      const fileName = fileNameMatch
        ? fileNameMatch[1]
        : `${file.name.replace(/\.[^/.]+$/, "").replace(/ /g, "_")}.csv`;

    setFileName(fileName);
    setFileProcessedTime(new Date()); // Guardar el momento del procesamiento
      if (blob.size === 0) {
        setMessage("El archivo recibido está vacío.");
        return;
      }

      const url = window.URL.createObjectURL(blob);

      const timestamp = new Date().toLocaleString();
      setHistory((prev) => [{ filename: fileName, timestamp }, ...prev]);

      // Extraer el mes del nombre del archivo (ejemplo: "ESTADO_DE_CUENTA_MARZO__2024.csv")
      const monthMatch = fileName.match(
        /(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)/i
      );
      const monthName = monthMatch
        ? monthMatch[1]
        : new Date().toLocaleString("es", { month: "long" });

      // Mapear nombres de meses a abreviaciones
      const monthMap: { [key: string]: string } = {
        ENERO: "Ene",
        FEBRERO: "Feb",
        MARZO: "Mar",
        ABRIL: "Abr",
        MAYO: "May",
        JUNIO: "Jun",
        JULIO: "Jul",
        AGOSTO: "Ago",
        SEPTIEMBRE: "Sep",
        OCTUBRE: "Oct",
        NOVIEMBRE: "Nov",
        DICIEMBRE: "Dic",
      };
      const month =
        monthMap[monthName.toUpperCase()] || monthName.substring(0, 3);

      // Notificar al componente padre (puedes ajustar el ingreso según tus necesidades)
      if (onFileProcessed) {
        onFileProcessed({
          //filename: fileName,
          //timestamp,
          month,
          ingreso: ingreso, // Valor de ejemplo
          totalCount: totalCount, // Total de transacciones del backend
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
    } catch (err) {
      console.error(err);
      setMessage("Ocurrió un error al procesar el archivo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="max-w-[66rem] mx-auto mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Cargar Estado de Cuenta - Izquierda */}
        <div className="col-span-2 bg-gray-100 p-6 rounded-xl shadow">
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
                Archivo seleccionado:{" "}
                <span className="font-medium">{file.name}</span>
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
        </div>

        {/* Columna derecha con dos tarjetas apiladas */}
        <div className="col-span-1 flex flex-col gap-4">
          {/* Transacciones Detectadas - Arriba */}
          <Card>
            <CardContent>
              <h3 className="text-sm text-black">Transacciones detectadas</h3>
              <p className="text-3xl font-bold text-black">{totalCounts}</p>
            </CardContent>
          </Card>

          {/* Archivo Analizado - Abajo */}
          <Card>
            <CardContent>
              <h3 className="text-sm text-black">Archivo analizado</h3>
              {fileName && (
                <>
                  <p className="text-lg font-semibold text-black truncate" title={fileName}>
                    {fileName}
                  </p>
                  <p className="text-xs text-black">{getTimeAgo(fileProcessedTime)}</p>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Archivos Procesados Recientemente */}
      {history.length > 0 && (
        <div className="bg-gray-100 p-6 rounded-2xl shadow max-w-[66rem] mx-auto mt-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Archivos Procesados Recientemente:
          </h2>
          <div className="mt-2">
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
