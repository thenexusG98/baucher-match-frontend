import { useState, useEffect } from "react";
import Card from "./ui/Card"; 
import CardContent from "./ui/CardContent";
import { db } from "../services/database";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ProcessedFile {
  //filename: string;
  //timestamp: string;
  month: string;
  ingreso: number;
  totalCount?: number;
}

interface DashboardProps {
  processedFiles: ProcessedFile[];
}

export default function Dashboard({ processedFiles }: DashboardProps) {
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [chartData, setChartData] = useState<Array<{ month: string; ingreso: number }>>([]);

  // Cargar años disponibles al montar el componente
  useEffect(() => {
    const loadYears = async () => {
      // Generar rango de años: del 2020 al año actual + 2 años
      const currentYear = new Date().getFullYear();
      const startYear = 2020;
      const endYear = currentYear + 2;
      
      const yearsRange: number[] = [];
      for (let year = endYear; year >= startYear; year--) {
        yearsRange.push(year);
      }
      
      setAvailableYears(yearsRange);
      
      // Verificar si hay datos en la DB
      const dbYears = await db.getAvailableYears();
      if (dbYears.length > 0) {
        setSelectedYear(dbYears[0]); // Seleccionar el año más reciente con datos
      }
    };
    
    loadYears();
  }, [processedFiles]); // Re-cargar cuando haya nuevos archivos procesados

  // Cargar datos del año seleccionado
  useEffect(() => {
    loadChartData(selectedYear);
  }, [selectedYear, processedFiles]);

  const loadChartData = async (year: number) => {
    // Obtener todos los totales mensuales
    const monthlyTotals = await db.getMonthlyTotals();
    
    // Filtrar por año seleccionado
    const yearData = monthlyTotals.filter(item => item.year === year);

    // Datos por defecto (todos los meses en 0)
    const defaultData = [
      { month: "Ene", ingreso: 0 },
      { month: "Feb", ingreso: 0 },
      { month: "Mar", ingreso: 0 },
      { month: "Abr", ingreso: 0 },
      { month: "May", ingreso: 0 },
      { month: "Jun", ingreso: 0 },
      { month: "Jul", ingreso: 0 },
      { month: "Ago", ingreso: 0 },
      { month: "Sep", ingreso: 0 },
      { month: "Oct", ingreso: 0 },
      { month: "Nov", ingreso: 0 },
      { month: "Dic", ingreso: 0 },
    ];

    // Combinar datos por defecto con datos reales
    const combined = defaultData.map(defaultMonth => {
      const realData = yearData.find(item => item.month === defaultMonth.month);
      return {
        month: defaultMonth.month,
        ingreso: realData ? realData.ingreso : 0,
      };
    });

    setChartData(combined);
  };

  // Componente personalizado para el Tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{payload[0].payload.month} {selectedYear}</p>
          <p className="text-sm text-gray-600">
            Ingreso: <span className="font-bold text-[#19304C]">${payload[0].value.toLocaleString()}</span>
          </p>
        </div>
      );
    }
    return null;
  };  

    return (
    <div className="p-6  gap-6 max-w-[66rem] mx-auto">
      {/* Selector de Año */}
      <div className="mb-4 flex items-center gap-4">
        <label htmlFor="year-select" className="text-lg font-semibold text-gray-700">
          Año:
        </label>
        <select
          id="year-select"
          value={selectedYear}
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {availableYears.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      {/* Título + Gráfica */}
        <div className="col-span-2">
          <Card >
            <CardContent className="h-58">
            <h3 className="text-2xl text-black">Ingreso por mes - {selectedYear}</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="ingreso" fill="#19304C" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }