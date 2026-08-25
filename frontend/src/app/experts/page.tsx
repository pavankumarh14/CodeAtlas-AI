"use client";

import React, { useState, useEffect } from "react";
import { Users, Mail, ShieldAlert, Award, Star, Loader2 } from "lucide-react";

export default function ExpertFinder() {
  const [services, setServices] = useState<string[]>([
    "Checkout Service", "Payment Service", "Inventory Service", "Order Service", 
    "Cart Service", "Notifications Service", "Auth Service", "User Service"
  ]);
  const [selectedService, setSelectedService] = useState("Checkout Service");
  const [loading, setLoading] = useState(false);
  const [experts, setExperts] = useState<any>({
    owners: [
      "Sarah Smith (Lead Engineer) - sarah.smith@company.com",
      "Commerce Team (Team)"
    ],
    contributors: [
      "Sarah Smith", "John Doe", "David Miller"
    ],
    architects: [
      "Alex Architect (Chief Architect)"
    ],
    subject_matter_experts: [
      "Sarah Smith (Domain SME)", "John Doe (Stripe Integration)"
    ]
  });

  useEffect(() => {
    async function fetchExperts() {
      setLoading(true);
      try {
        const res = await fetch(`/api/v1/experts?service=${encodeURIComponent(selectedService)}`);
        if (res.ok) {
          const data = await res.json();
          setExperts(data);
        }
      } catch (err) {
        console.warn("Backend offline, running on mock expert registry.", err);
        // Stagger mocks based on selection
        if (selectedService === "Notifications Service") {
          setExperts({
            owners: ["Emma Jones (Engineer) - emma.jones@company.com", "Notifications Team (Team)"],
            contributors: ["Emma Jones", "Sophia Martin", "Joshua Garcia"],
            architects: ["Alex Architect (Chief Architect)"],
            subject_matter_experts: ["Emma Jones (WhatsApp/SMS SME)"]
          });
        } else if (selectedService === "Auth Service") {
          setExperts({
            owners: ["Emily Thomas (Lead Engineer) - emily.thomas@company.com", "Identity Team (Team)"],
            contributors: ["Emily Thomas", "Matthew Jackson", "Olivia White"],
            architects: ["Alex Architect (Chief Architect)"],
            subject_matter_experts: ["Emily Thomas (OAuth SME)", "Matthew Jackson (MFA SME)"]
          });
        } else {
          setExperts({
            owners: ["Sarah Smith (Lead Engineer) - sarah.smith@company.com", "Commerce Team (Team)"],
            contributors: ["Sarah Smith", "John Doe", "David Miller"],
            architects: ["Alex Architect (Chief Architect)"],
            subject_matter_experts: ["Sarah Smith (Domain SME)", "John Doe (Stripe Integration)"]
          });
        }
      } finally {
        setLoading(false);
      }
    }
    fetchExperts();
  }, [selectedService]);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Selector Area */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h3 className="font-bold text-base text-white">Identify Service Experts & Owners</h3>
          <p className="text-slate-400 text-xs mt-1">
            Select a service from the living ontology to discover its owners, code contributors, and designated architects.
          </p>
        </div>
        <select
          value={selectedService}
          onChange={(e) => setSelectedService(e.target.value)}
          className="px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl text-sm text-slate-200 outline-none w-64 cursor-pointer"
        >
          {services.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24 gap-3 bg-slate-900/40 rounded-2xl border border-slate-800">
          <Loader2 className="h-6 w-6 text-indigo-500 animate-spin" />
          <span className="text-slate-400 text-sm font-medium">Scanning ontology experts...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Owners Card */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Users className="h-4.5 w-4.5 text-blue-400" />
              Service Owners & Teams
            </h3>
            <div className="space-y-3">
              {experts.owners?.map((owner: string, idx: number) => (
                <div key={idx} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-200 truncate">{owner.split(" - ")[0]}</p>
                    {owner.includes("@") && (
                      <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1 mt-1">
                        <Mail className="h-3 w-3" />
                        {owner.split(" - ")[1]}
                      </span>
                    )}
                  </div>
                  <span className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold uppercase">
                    Owner
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Subject Matter Experts (SMEs) */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Award className="h-4.5 w-4.5 text-yellow-400" />
              Subject Matter Experts (SMEs)
            </h3>
            <div className="space-y-3">
              {experts.subject_matter_experts?.map((sme: string, idx: number) => (
                <div key={idx} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-200">{sme.includes(" (") ? sme.split(" (")[0] : sme}</p>
                    {sme.includes(" (") && (
                      <p className="text-xs text-slate-400 mt-0.5">{sme.split(" (")[1].replace(")", "")}</p>
                    )}
                  </div>
                  <Star className="h-4.5 w-4.5 text-yellow-500 fill-yellow-500 shrink-0" />
                </div>
              ))}
            </div>
          </div>

          {/* Code Contributors */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Users className="h-4.5 w-4.5 text-purple-400" />
              Active Git Code Contributors
            </h3>
            <div className="grid grid-cols-2 gap-4 bg-slate-950 p-4 rounded-xl border border-slate-850">
              {experts.contributors?.map((contrib: string, idx: number) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                  <span className="h-1.5 w-1.5 rounded-full bg-purple-400 shrink-0"></span>
                  <span className="truncate">{contrib}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Escalation / Architects */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldAlert className="h-4.5 w-4.5 text-emerald-400" />
              Designated System Architects
            </h3>
            <div className="space-y-3">
              {experts.architects?.map((arch: string, idx: number) => (
                <div key={idx} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-200">{arch.includes(" (") ? arch.split(" (")[0] : arch}</p>
                    {arch.includes(" (") && (
                      <p className="text-xs text-slate-400 mt-0.5">{arch.split(" (")[1].replace(")", "")}</p>
                    )}
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase">
                    Architect
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
