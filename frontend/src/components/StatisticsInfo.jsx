import React, { useEffect } from 'react';
import Card from './Card';
import Chart from 'chart.js/auto';

const StatisticsInfo = ({ statData = [] }) => {
  useEffect(() => {
    statData.forEach(sa => {
      const barCtx = document.getElementById(`barChart-${sa.year}`).getContext('2d');
      new Chart(barCtx, { type: 'bar', data: { labels: ['Staff','Volunteers'], datasets: [{ data: [sa.fullTime_other, sa.volunteers] }] } });
      const pieCtx = document.getElementById(`pieChart-${sa.year}`).getContext('2d');
      new Chart(pieCtx, { type: 'pie', data: { labels: ['Estimate'], datasets: [{ data: [sa.is_censusEstimate ? 100 : 0] }] } });
    });
  }, [statData]);

  return (
    <section id="stat-info">
      {statData.length > 0 ? statData.map(sa => (
        <div key={sa.year} className="mb-4">
          <Card title={`Staff & Volunteers (${sa.year})`}>
            <canvas id={`barChart-${sa.year}`} className="mt-3" />
          </Card>
          <Card title={`Census Breakdown (${sa.year})`}>
            {sa.is_censusEstimate ? <canvas id={`pieChart-${sa.year}`} className="mt-3" /> : <p><em>Not a census estimate for {sa.year}</em></p>}
          </Card>
        </div>
      )) : <p>No statistical data recorded</p>}
    </section>
  );
};

export default StatisticsInfo;