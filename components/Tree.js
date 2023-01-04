import { useEffect, useRef } from 'react'
import ObservableTree from "./ObservableTree";

export default function Tree({data}) {
  const chartRef = useRef();

  useEffect(() => {
    const chart = ObservableTree(data, {
      label: d => d.name,
      title: (d, n) => `${n.ancestors().reverse().map(d => d.data.name).join(" > ")}`, // hover text
      width: 1152,
      height: 1152,
      margin: 100
    })
    
    chartRef.current.append(chart);
    return () => chart.remove();
  }, []);

  return (
    <div className="">
      <div ref={chartRef} />
    </div>
  );
}
