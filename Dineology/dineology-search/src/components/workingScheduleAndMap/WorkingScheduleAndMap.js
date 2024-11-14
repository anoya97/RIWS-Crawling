import React from 'react';
import './WorkingScheduleAndMap.css';

const WorkingScheduleAndMap = ({ schedule, coordinates, loading }) => (
  <div className="workingScheduleContainer">
    <div className="workingSchedule">
      <h2>Horario de trabajo</h2>
      <div className="workingScheduleAndMapContainer">
        <table className="workingScheduleTable">
          <thead>
            <tr>
              <th>Día</th>
              <th>Horario</th>
            </tr>
          </thead>
          <tbody>
            {schedule && Object.keys(schedule).length > 0 ? (
              Object.entries(schedule).map(([day, hours]) => (
                <tr key={day}>
                  <td>{day}</td>
                  <td>
                    {hours.length > 0 ? hours.map((hour, index) => (
                      <div key={index} style={{ marginBottom: index !== hours.length - 1 ? '8px' : '0' }}>
                        {hour}
                      </div>
                    )) : "-"}
                  </td>
                </tr>
              ))
            ) : (
              ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"].map(day => (
                <tr key={day}>
                  <td>{day}</td>
                  <td>-</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        <div className="mapContainer">
          {loading ? (
            <p>Cargando mapa...</p>
          ) : coordinates ? (
            <iframe
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${coordinates.lon - 0.01},${coordinates.lat - 0.01},${coordinates.lon + 0.01},${coordinates.lat + 0.01}&layer=mapnik&marker=${coordinates.lat},${coordinates.lon}`}
              width="100%"
              height="600px"
              style={{ border: 0 }}
              allowFullScreen=""
              loading="lazy"
              title="Mapa"
            />
          ) : (
            <p>Mapa no disponible en estos momentos.</p>
          )}
        </div>
      </div>
    </div>
  </div>
);

export default WorkingScheduleAndMap;
