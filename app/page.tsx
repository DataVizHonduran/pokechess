"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, X } from "lucide-react";
import { Player } from "./types";
import PowerMap from "./components/PowerMap";
import PlayerCard from "./components/PlayerCard";

export default function Home() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [status, setStatus] = useState<"loading" | "connected" | "error">(
    "loading"
  );

  // Filter players based on search query
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const query = searchQuery.toLowerCase();
    return players.filter(
      (p) =>
        p.name.toLowerCase().includes(query) ||
        p.pokemonName.toLowerCase().includes(query)
    );
  }, [players, searchQuery]);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_PATH || ""}/players.json?v=${Date.now()}`);
        if (!res.ok) throw new Error("Failed to load");
        const data = await res.json();
        setPlayers(data);
        setStatus("connected");
      } catch {
        console.error("No players.json found yet. Run the scraper!");
        setStatus("error");
      }
    }
    loadData();
  }, []);

  return (
    <div className="bg-slate-950 text-slate-200 font-sans min-h-screen p-8">
      {/* Header */}
      <motion.header
        className="max-w-5xl mx-auto mb-8 flex justify-between items-end"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div>
          <motion.h1
            className="text-4xl font-black tracking-tight text-white mb-2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <span className="text-indigo-500">POKE</span>CHESS{" "}
            <span className="text-sm font-mono text-slate-500">v2.0</span>
          </motion.h1>
          <motion.p
            className="text-slate-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            PS11 Chess Team Performance Ecosystem
            (only displays trainers with PLW > 20)
          </motion.p>
        </div>
        <motion.div
          className="text-right"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="text-xs uppercase tracking-widest text-slate-500">
            Live Data Status
          </div>
          <motion.div
            className={`font-mono text-xl ${
              status === "connected"
                ? "text-green-500"
                : status === "error"
                ? "text-red-500"
                : "text-yellow-500"
            }`}
            animate={
              status === "loading" ? { opacity: [1, 0.5, 1] } : { opacity: 1 }
            }
            transition={
              status === "loading" ? { duration: 1, repeat: Infinity } : {}
            }
          >
            {status === "connected"
              ? "CONNECTED"
              : status === "error"
              ? "OFFLINE"
              : "LOADING..."}
          </motion.div>
        </motion.div>
      </motion.header>

      {/* Search bar */}
      <motion.div
        className="max-w-5xl mx-auto mb-6 relative"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5" />
          <input
            type="text"
            placeholder="Search players or Pokemon..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl py-3 pl-12 pr-12 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Search results dropdown */}
        <AnimatePresence>
          {searchResults.length > 0 && (
            <motion.div
              className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-700 rounded-xl overflow-hidden z-40 shadow-xl"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {searchResults.slice(0, 5).map((player) => (
                <button
                  key={player.id}
                  onClick={() => {
                    setSelectedPlayer(player);
                    setSearchQuery("");
                  }}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-800 transition-colors text-left"
                >
                  <div>
                    <span className="font-medium text-white">{player.name}</span>
                    <span className="ml-2 text-sm text-yellow-400">
                      {player.pokemonName}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm text-slate-400">PLW: {player.plw}</span>
                    <span className="ml-3 text-sm text-slate-500">USCF: {player.uscf}</span>
                  </div>
                </button>
              ))}
              {searchResults.length > 5 && (
                <div className="px-4 py-2 text-sm text-slate-500 text-center border-t border-slate-800">
                  +{searchResults.length - 5} more results
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Main content */}
      <main className="max-w-5xl mx-auto">
        <PowerMap
          players={players}
          onPlayerClick={(player) => setSelectedPlayer(player)}
        />

        {/* Stats summary */}
        {players.length > 0 && (
          <motion.section
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <StatCard
              label="Total Players"
              value={players.length}
              delay={0.7}
            />
            <StatCard
              label="Legendary"
              value={players.filter((p) => p.tier === "legendary").length}
              delay={0.8}
            />
            <StatCard
              label="Avg USCF"
              value={Math.round(
                players.reduce((sum, p) => sum + p.uscf, 0) / players.length
              )}
              delay={0.9}
            />
            <StatCard
              label="Total Puzzles"
              value={players.reduce((sum, p) => sum + p.puzzles, 0)}
              delay={1.0}
            />
          </motion.section>
        )}
      </main>

      {/* Player card modal */}
      <PlayerCard
        player={selectedPlayer}
        onClose={() => setSelectedPlayer(null)}
      />
    </div>
  );
}

function StatCard({
  label,
  value,
  delay,
}: {
  label: string;
  value: number;
  delay: number;
}) {
  return (
    <motion.div
      className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      whileHover={{ scale: 1.05, borderColor: "rgb(99 102 241)" }}
    >
      <motion.div
        className="text-2xl font-bold text-white"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 0.1, type: "spring" }}
      >
        {value}
      </motion.div>
      <div className="text-xs text-slate-500 uppercase tracking-wider">
        {label}
      </div>
    </motion.div>
  );
}
