import { useState, useEffect } from 'react'
import { MapContainer, GeoJSON } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'

const RATIOS = [
  { key: 'trailingPE',         label: 'P/E'       },
  { key: 'forwardPE',          label: 'Fwd P/E'   },
  { key: 'enterpriseToEbitda', label: 'EV/EBITDA' },
  { key: 'pegRatio',           label: 'PEG'       },
  { key: 'priceToBook',        label: 'P/B'       },
]

const COUNTRY_COLORS = {
  'US': '#1d4ed8', 'BR': '#15803d', 'CN': '#b91c1c',
  'DE': '#854d0e', 'GB': '#6d28d9', 'CA': '#0e7490', 'JP': '#be185d'
}

const ISO_NUM_TO_A2 = {
  '840':'US','076':'BR','156':'CN','276':'DE','826':'GB','124':'CA','392':'JP'
}

const fmt = v => (v !== null && v !== undefined) ? Number(v).toFixed(1) : null

function valClass(val, avg) {
  if (val === null || avg === null || avg === undefined) return 'val-neutral'
  const pct = (val - avg) / avg
  if (pct < -0.15) return 'val-cheap'
  if (pct >  0.15) return 'val-expensive'
  return 'val-fair'
}

function RatioVal({ val, avg }) {
  const v = fmt(val)
  if (!v) return <span className="val-na">-</span>
  const cls = avg !== undefined ? valClass(val, avg) : 'val-neutral'
  return <span className={`company-ratio-val ${cls}`}>{v}</span>
}

function EtfCard({ etf }) {
  return (
    <div className="etf-card">
      <div className="etf-label">ETF representativo</div>
      <div className="etf-ticker">{etf.ticker} - {etf.name}</div>
      <div className="etf-ratios">
        {RATIOS.map(r => (
          <div className="etf-ratio" key={r.key}>
            <div className="etf-ratio-label">{r.label}</div>
            <div className="etf-ratio-val">{fmt(etf[r.key]) ?? '-'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SectorList({ country, onSelectSector }) {
  return (
    <>
      <EtfCard etf={country.etf} />
      <div className="ratio-header">
        {RATIOS.map(r => (
          <div className="ratio-header-label" key={r.key}>{r.label}</div>
        ))}
      </div>
      {Object.entries(country.sectors).map(([sectorName, sectorData]) => (
        <div className="sector-card" key={sectorName} onClick={() => onSelectSector(sectorName)}>
          <div className="sector-card-header">
            <span className="sector-name">{sectorName}</span>
            <span className="sector-count">{sectorData.companies.length} empresas</span>
          </div>
          <div className="sector-ratios">
            {RATIOS.map(r => (
              <div className="ratio-cell" key={r.key}>
                <div className="ratio-val val-neutral">{fmt(sectorData.averages[r.key]) ?? '-'}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  )
}

function CompanyList({ sectorName, sectorData, onBack }) {
  const avgs = sectorData.averages
  return (
    <>
      <div className="back-btn" onClick={onBack}>Volver a sectores</div>
      <div className="sector-avg-row">
        <span className="sector-avg-label">Promedio sector</span>
        <div className="sector-avg-ratios">
          {RATIOS.map(r => (
            <div className="sector-avg-val" key={r.key}>{fmt(avgs[r.key]) ?? '-'}</div>
          ))}
        </div>
      </div>
      <div className="ratio-header">
        {RATIOS.map(r => (
          <div className="ratio-header-label" key={r.key}>{r.label}</div>
        ))}
      </div>
      {sectorData.companies.map(company => (
        <div className="company-card" key={company.ticker}>
          <div className="company-header">
            <div>
              <div className="company-ticker">{company.ticker}</div>
              <div className="company-name">{company.name}</div>
            </div>
          </div>
          <div className="company-ratios">
            {RATIOS.map(r => (
              <div className="company-ratio" key={r.key}>
                <div className="company-ratio-label">{r.label}</div>
                <RatioVal val={company[r.key]} avg={avgs[r.key]} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  )
}

function SidePanel({ selectedCountry, data }) {
  const [selectedSector, setSelectedSector] = useState(null)
  useEffect(() => { setSelectedSector(null) }, [selectedCountry])

  if (!selectedCountry) {
    return (
      <div className="side-panel">
        <div className="empty-state">
          <div className="empty-icon">M</div>
          <div className="empty-title">Selecciona un pais</div>
          <div className="empty-sub">Hace clic en un pais resaltado del mapa</div>
        </div>
      </div>
    )
  }

  const country = data.countries[selectedCountry]
  const totalCompanies = Object.values(country.sectors).reduce((a, s) => a + s.companies.length, 0)

  return (
    <div className="side-panel">
      <div className="panel-header">
        <div className="panel-title">{country.name}</div>
        <div className="panel-sub">
          {selectedSector
            ? `Sector: ${selectedSector}`
            : `${Object.keys(country.sectors).length} sectores - ${totalCompanies} empresas`
          }
        </div>
      </div>
      <div className="panel-body">
        {selectedSector ? (
          <CompanyList
            sectorName={selectedSector}
            sectorData={country.sectors[selectedSector]}
            onBack={() => setSelectedSector(null)}
          />
        ) : (
          <SectorList country={country} onSelectSector={setSelectedSector} />
        )}
      </div>
      <div className="legend">
        <span>Vs promedio sector:</span>
        <div className="legend-item"><div className="legend-dot" style={{background:'#34d399'}}></div> Barato</div>
        <div className="legend-item"><div className="legend-dot" style={{background:'#fbbf24'}}></div> Justo</div>
        <div className="legend-item"><div className="legend-dot" style={{background:'#f87171'}}></div> Caro</div>
      </div>
    </div>
  )
}

export default function App() {
  const [data, setData] = useState(null)
  const [selectedCountry, setSelectedCountry] = useState(null)
  const [geoData, setGeoData] = useState(null)

  useEffect(() => {
    fetch('./data.json')
      .then(r => r.json())
      .then(setData)
      .catch(e => console.error('Error cargando data.json:', e))
  }, [])

  useEffect(() => {
    fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
      .then(r => r.json())
      .then(topo => {
        import('topojson-client').then(({ feature }) => {
          const geojson = feature(topo, topo.objects.countries)
          setGeoData(geojson)
        })
      })
      .catch(e => console.error('Error cargando mapa:', e))
  }, [])

  if (!data) {
    return (
      <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100vh',color:'#64748b',fontSize:'14px'}}>
        Cargando datos...
      </div>
    )
  }

  const styleFeature = (feature) => {
    const isoNum = String(feature.id).padStart(3, '0')
    const code = ISO_NUM_TO_A2[isoNum]
    const isSelected = code === selectedCountry
    if (!code) return { fillColor: '#1a2235', weight: 0.5, color: '#0a0e1a', fillOpacity: 1 }
    return {
      fillColor: isSelected ? COUNTRY_COLORS[code] : '#1e3a5f',
      weight: isSelected ? 2 : 0.5,
      color: isSelected ? '#60a5fa' : '#0a0e1a',
      fillOpacity: 1
    }
  }

  const onEachFeature = (feature, layer) => {
    const isoNum = String(feature.id).padStart(3, '0')
    const code = ISO_NUM_TO_A2[isoNum]
    if (!code) return
    layer.on({
      click: () => setSelectedCountry(code),
      mouseover: (e) => {
        e.target.setStyle({ fillColor: '#2d4a7a' })
        const el = e.target.getElement()
        if (el) el.style.cursor = 'pointer'
      },
      mouseout: (e) => { e.target.setStyle(styleFeature(feature)) }
    })
  }

  const selectedCountryName = selectedCountry ? data.countries[selectedCountry]?.name : null

  return (
    <>
      <div className="header">
        <div className="header-left">
          <div className="header-logo">C</div>
          <div>
            <div className="header-title">CEDEAR Valuation Map</div>
            <div className="header-sub">Multiplos de valoracion por pais y sector</div>
          </div>
        </div>
        <div className="header-updated">Actualizado: {data.updated}</div>
      </div>

      <div className="breadcrumb">
        <span
          className={selectedCountry ? 'breadcrumb-item' : 'breadcrumb-current'}
          onClick={() => setSelectedCountry(null)}
        >
          Mundo
        </span>
        {selectedCountryName && (
          <>
            <span className="breadcrumb-sep">›</span>
            <span className="breadcrumb-current">{selectedCountryName}</span>
          </>
        )}
      </div>

      <div className="main">
        <div className="map-container">
          {geoData ? (
            <MapContainer
              center={[20, 10]}
              zoom={2}
              minZoom={1}
              maxZoom={6}
              style={{ width: '100%', height: '100%', background: '#0a0e1a' }}
              zoomControl={true}
              attributionControl={false}
            >
              <GeoJSON
                key={selectedCountry}
                data={geoData}
                style={styleFeature}
                onEachFeature={onEachFeature}
              />
            </MapContainer>
          ) : (
            <div style={{color:'#64748b',fontSize:'13px'}}>Cargando mapa...</div>
          )}
        </div>
        <SidePanel selectedCountry={selectedCountry} data={data} />
      </div>
    </>
  )
}
