"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { Infrastructure, Country } from "@/lib/types";
import Link from "next/link";
import { formatInfraCategory } from "@/lib/format";

const CATEGORY_COLORS: Record<string, string> = {
  undersea_cable: "#4C8DFF",
  port: "#2FD6C0",
  railway: "#F0A83C",
  semiconductor: "#EF5B4E",
  power_grid: "#F0A83C",
  rare_earth: "#EF5B4E",
  data_center: "#4C8DFF",
};

const getCountryColor = (score: number) => {
  if (score === 0) return "rgba(71, 85, 105, 0.08)";
  if (score > 80) return "rgba(239, 91, 78, 0.55)";
  if (score > 60) return "rgba(240, 168, 60, 0.5)";
  if (score > 40) return "rgba(234, 179, 8, 0.45)";
  if (score > 20) return "rgba(76, 141, 255, 0.4)";
  return "rgba(47, 214, 192, 0.35)";
};

const getCountryBorderColor = (score: number) => {
  if (score === 0) return "rgba(71, 85, 105, 0.12)";
  if (score > 80) return "rgba(239, 91, 78, 0.75)";
  if (score > 60) return "rgba(240, 168, 60, 0.75)";
  if (score > 40) return "rgba(234, 179, 8, 0.7)";
  if (score > 20) return "rgba(76, 141, 255, 0.7)";
  return "rgba(47, 214, 192, 0.7)";
};

interface InfraMapProps {
  assets: Infrastructure[];
  countries: Country[];
}

export default function InfraMap({ assets, countries }: InfraMapProps) {
  const [geoJson, setGeoJson] = useState<any>(null);
  const points = assets.filter((a) => a.latitude != null && a.longitude != null);
  const countryMap = new Map(countries.map((c) => [c.iso3?.toUpperCase(), c]));

  useEffect(() => {
    fetch("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json")
      .then((res) => res.json())
      .then((data) => setGeoJson(data))
      .catch((err) => console.error("Failed to load world GeoJSON:", err));
  }, []);

  const styleCountry = (feature: any) => {
    const iso3 = feature.id?.toUpperCase();
    const country = countryMap.get(iso3);
    const score = country?.risk_score || 0;
    return {
      fillColor: getCountryColor(score),
      weight: score > 0 ? 1.5 : 0.8,
      opacity: 1,
      color: getCountryBorderColor(score),
      fillOpacity: 1,
    };
  };

  const onEachFeature = (feature: any, layer: any) => {
    const iso3 = feature.id?.toUpperCase();
    const country = countryMap.get(iso3);
    const name = feature.properties?.name || "Unknown";

    if (country && country.risk_score > 0) {
      layer.bindPopup(`
        <div style="font-family: inherit; color: #1e293b; padding: 2px;">
          <div style="display: flex; align-items: center; justify-content: space-between; font-weight: 600; margin-bottom: 4px; gap: 16px;">
            <span>${country.name}</span>
            <span style="font-size: 10px; font-family: monospace; padding: 1px 4px; border-radius: 4px; background: #f1f5f9; border: 1px solid #cbd5e1;">${iso3}</span>
          </div>
          <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Region: ${country.region || "N/A"}</div>
          <div style="display: flex; align-items: center; gap: 8px; border-top: 1px solid rgba(226, 232, 240, 0.8); padding-top: 8px;">
            <span style="font-size: 11px; font-weight: 500;">Geopolitical Risk:</span>
            <span style="font-size: 11px; font-family: monospace; font-weight: 600; padding: 2px 6px; border-radius: 4px; color: #ffffff; background-color: ${getCountryBorderColor(country.risk_score)}">${country.risk_score} / 100</span>
          </div>
          <div style="margin-top: 10px; text-align: right;">
            <a href="/countries/${country.id}" style="font-size: 11px; font-family: monospace; color: #4C8DFF; text-decoration: none; font-weight: 500;">VIEW DETAIL &rarr;</a>
          </div>
        </div>
      `);

      layer.on({
        mouseover: (e: any) => {
          const l = e.target;
          l.setStyle({
            fillOpacity: 0.85,
            weight: 2,
          });
        },
        mouseout: (e: any) => {
          const l = e.target;
          l.setStyle({
            fillOpacity: 1.0,
            weight: 1.5,
          });
        },
      });
    } else {
      layer.bindPopup(`
        <div style="font-family: inherit; color: #64748b; padding: 2px;">
          <div style="font-weight: 600; font-size: 13px; color: #1e293b;">${name}</div>
          <div style="font-size: 11px; margin-top: 4px;">No active geopolitical risk profile indexed.</div>
        </div>
      `);

      layer.on({
        mouseover: (e: any) => {
          const l = e.target;
          l.setStyle({
            fillColor: "rgba(148, 163, 184, 0.15)",
          });
        },
        mouseout: (e: any) => {
          const l = e.target;
          l.setStyle({
            fillColor: "rgba(71, 85, 105, 0.08)",
          });
        },
      });
    }
  };

  return (
    <MapContainer
      center={[20, 30]}
      zoom={2}
      minZoom={2}
      style={{ height: "100%", width: "100%" }}
      worldCopyJump
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors, CARTO'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      {geoJson && (
        <GeoJSON
          data={geoJson}
          style={styleCountry}
          onEachFeature={onEachFeature}
        />
      )}
      {points.map((asset) => (
        <CircleMarker
          key={asset.id}
          center={[asset.latitude as number, asset.longitude as number]}
          radius={5}
          pathOptions={{
            color: "#ffffff",
            fillColor: CATEGORY_COLORS[asset.category] || "#8996A9",
            fillOpacity: 0.9,
            weight: 1,
          }}
        >
          <Popup>
            <div className="text-sm">
              <div className="font-semibold">{asset.name}</div>
              <div className="text-xs text-gray-500 mb-1">{formatInfraCategory(asset.category)}</div>
              {asset.country && (
                <Link href={`/countries/${asset.country.id}`} className="text-xs text-blue-600 hover:underline">
                  {asset.country.name}
                </Link>
              )}
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
