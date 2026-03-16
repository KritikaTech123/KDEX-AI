import React from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#8dd1e1', '#a4de6c', '#d0ed57'];

export default function ChartView({ chartData }: { chartData: any }) {
  if (!chartData) return null;
  const { chart_type, data, x_axis, y_axis } = chartData;

  if (!data || !x_axis || !y_axis) return <div className="text-red-500">Invalid chart data</div>;

  if (chart_type === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <XAxis dataKey={x_axis} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={y_axis} fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    );
  }
  if (chart_type === 'line') {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <XAxis dataKey={x_axis} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey={y_axis} stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    );
  }
  if (chart_type === 'pie') {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie data={data} dataKey={y_axis} nameKey={x_axis} cx="50%" cy="50%" outerRadius={120} fill="#8884d8">
            {data.map((entry: any, idx: number) => (
              <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  }
  return <div className="text-gray-500">Chart type not supported</div>;
}
