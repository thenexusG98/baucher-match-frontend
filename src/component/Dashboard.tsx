import Card from "./ui/Card"; 
import CardContent from "./ui/CardContent";

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
  // Datos por defecto
  const defaultData = [
    { month: "Ene", ingreso: 0 },
    { month: "Feb", ingreso: 0 },
    { month: "Mar", ingreso: 0 },
    { month: "Abr", ingreso: 0 },
    { month: "May", ingreso: 0 },
    { month: "Jun", ingreso: 0 },
  ];

  // Combinar datos por defecto con archivos procesados
  const chartData = processedFiles.length > 0 
    ? processedFiles.reduce((acc, file) => {
        const existingMonth = acc.find(item => item.month === file.month);
        if (existingMonth) {
          existingMonth.ingreso = file.ingreso;
        } else {
          acc.push({ month: file.month, ingreso: file.ingreso });
        }
        return acc;
      }, [...defaultData])
    : defaultData;

  // Componente personalizado para el Tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="text-sm font-semibold text-gray-700">{payload[0].payload.month}</p>
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
      {/* Título + Gráfica */}
        <div className="col-span-2">
          <Card >
            <CardContent className="h-58">
            <h3 className="text-2xl text-black">Ingreso por mes</h3>
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