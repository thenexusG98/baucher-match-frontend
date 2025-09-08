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

const data = [
  { month: "Ene", ingreso: 1200 },
  { month: "Feb", ingreso: 800 },
  { month: "Mar", ingreso: 1500 },
  { month: "Abr", ingreso: 900 },
  { month: "May", ingreso: 1800 },
];

export default function Dashboard() {
    return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-[66rem] mx-auto">
      {/* Título + Gráfica */}
        <div className="col-span-2">
          <Card >
            <CardContent className="h-58">
            <h3 className="text-2xl text-black">Ingreso por mes</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="ingreso" fill="#19304C" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
  
        {/* Cards laterales */}
        <div className="flex flex-col gap-4">
          <Card >
            <CardContent>
              <h3 className="text-sm text-black">Transacciones detectadas</h3>
              <p className="text-3xl font-bold text-black">23</p>
            </CardContent>
          </Card>
          <Card >
            <CardContent>
              <h3 className="text-sm text-black">Archivo analizado</h3>
              <p className="text-lg font-semibold text-black">EstadoCuentaTEC.pdf</p>
              <p className="text-xs text-black">Hace 1 hora</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }