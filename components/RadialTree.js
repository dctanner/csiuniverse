import { useEffect, useRef } from 'react'
import RadialObservableTree from "./RadialObservableTree";

export default function RadialTree({data}) {
  const chartRef = useRef();

  useEffect(() => {
    const chart = RadialObservableTree(data, {
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
