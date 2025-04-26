import { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const redIcon = new L.Icon({
  iconUrl: "/src/assets/pin_rojo.png",
  iconSize: [30, 50],
  iconAnchor: [15, 50],
});

const greenIcon = new L.Icon({
  iconUrl: "/src/assets/pin_verde.png",
  iconSize: [30, 50],
  iconAnchor: [15, 50],
});

const Tasador = () => {
  const [form, setForm] = useState({
    barrio: "",
    direccion: "",
    ambientes: 1,
    banos: 1,
    antiguedad: 10,
    cercania: 1,
    m2: 1,
  });
  const [valorM2, setValorM2] = useState(null);
  const [valorTotal, setValorTotal] = useState(null);
  const [comparables, setComparables] = useState([]);
  const [geo, setGeo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        ambientes: Number(form.ambientes),
        banos: Number(form.banos),
        antiguedad: Number(form.antiguedad),
        cercania: Number(form.cercania),
        m2: Number(form.m2),
      };

      const res = await axios.post("http://localhost:8000/tasar", payload);
      setValorM2(res.data.valor_m2);
      setValorTotal(res.data.valor_total);
      setComparables(res.data.comparables);
      setGeo(res.data.geo);
      setSubmitted(true);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setError("⚠️ No se encontraron propiedades comparables con los criterios ingresados.");
      } else if (err.response) {
        setError(err.response.data.detail || "Error desconocido en el tasador.");
      } else if (err.request) {
        setError("No se pudo contactar al servidor. ¿Está activo el backend?");
      } else {
        setError("Error inesperado: " + err.message);
      }
      setValorM2(null);
      setValorTotal(null);
      setComparables([]);
      setGeo(null);
      setSubmitted(false);
    }
    setLoading(false);
  };

  const campos = [
    { name: "barrio", label: "Barrio o zona", type: "text" },
    { name: "direccion", label: "Dirección exacta", type: "text" },
    { name: "ambientes", label: "Cantidad de ambientes", type: "number" },
    { name: "banos", label: "Cantidad de baños", type: "number" },
    { name: "antiguedad", label: "Antigüedad de la propiedad (años)", type: "number" },
    { name: "cercania", label: "Distancia máxima de propiedades comparables (km)", type: "number", step: 0.1 },
    { name: "m2", label: "Metros cuadrados cubiertos", type: "number" },
  ];

  const propiedadCoords =
    Array.isArray(comparables) && comparables.length > 0
      ? { lat: comparables[0].lat, lon: comparables[0].lon }
      : null;

  return (
    <div className="min-h-screen w-screen bg-white text-black p-10 flex items-start justify-center">
      <div className={`transition-all duration-700 ease-in-out flex w-full max-w-[1800px] ${submitted ? "gap-20" : "justify-center"}`}>
        <div className={`transition-all duration-700 ease-in-out ${submitted ? "w-1/3" : "w-full max-w-xl"} bg-white rounded-3xl shadow-2xl p-10`}>
          <div className="flex justify-center mb-8">
            <img src="/src/assets/logo.png" alt="Logo" className="w-80 h-80" />
          </div>
          {error && <div className="text-red-600 font-semibold text-center mb-4">{error}</div>}
          <div className="space-y-4">
            {campos.map(({ name, label, type, step }) => (
              <div key={name}>
                <label className="block text-sm font-medium text-black mb-1">{label}</label>
                <input
                  name={name}
                  type={type}
                  step={step}
                  value={form[name]}
                  onChange={handleChange}
                  className="w-full p-3 border border-black rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>
            ))}
            <button
              onClick={handleSubmit}
              className="w-full py-3 bg-black text-white font-semibold rounded-xl hover:bg-gray-900 transition"
            >
              {loading ? "Cargando..." : "Buscar comparables"}
            </button>
          </div>
        </div>

        {submitted && (
          <div className="w-2/3 flex flex-col items-center gap-10">
            <div className="w-full">
              <h2 className="text-md font-semibold text-black mb-2">📋 Propiedades comparables:</h2>
              <div className="max-h-103 overflow-y-auto border border-black rounded-xl">
                <table className="w-full text-left bg-white text-lg">
                  <thead className="bg-black text-white sticky top-0">
                    <tr>
                      <th className="px-4 py-2 border-b">Dirección</th>
                      <th className="px-4 py-2 border-b">Superficie</th>
                      <th className="px-4 py-2 border-b">Antigüedad</th>
                      <th className="px-4 py-2 border-b">Precio (USD)</th>
                      <th className="px-4 py-2 border-b">Distancia</th>
                      <th className="px-4 py-2 border-b">Página</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparables.map((c, i) => (
                      <tr key={i} className="hover:bg-gray-100">
                        <td className="px-4 py-2 border-b">{c.Direccion}</td>
                        <td className="px-4 py-2 border-b">{c.Cubierta}</td>
                        <td className="px-4 py-2 border-b">{c.Antigüedad}</td>
                        <td className="px-4 py-2 border-b">{parseFloat(c.Precio)}</td>
                        <td className="px-4 py-2 border-b">{c.distancia_km}</td>
                        <td className="px-4 py-2 border-b">{c.Publicada_en}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {propiedadCoords && (
              <div className="h-96 w-full rounded-xl overflow-hidden border border-black">
                <MapContainer center={[propiedadCoords.lat, propiedadCoords.lon]} zoom={15} style={{ height: "100%", width: "100%" }}>
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  <Marker position={geo} icon={redIcon}><Popup>Propiedad a tasar</Popup></Marker>
                  {comparables.map((c, i) =>
                    c.lat && c.lon && (
                      <Marker key={i} position={[c.lat, c.lon]} icon={greenIcon}><Popup>{c.Direccion}</Popup></Marker>
                    )
                  )}
                </MapContainer>
              </div>
            )}

            {(valorM2 && valorTotal) && (
              <div className="flex space-x-8 items-center">
               <div>
                <div className="text-xl font-semibold text-gray-800">Precio M² promedio</div>
                <div className="text-3xl font-bold text-green-700">USD {valorM2.toFixed(2)}</div>
               </div>
               <div className="flex flex-col items-center">
                <div className="text-xl font-semibold text-gray-800">Estimación</div>
                <div className="text-3xl font-bold text-blue-700">
                  USD {valorTotal.toLocaleString("es-AR", { minimumFractionDigits: 2 })}
               </div>
               </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Tasador;


