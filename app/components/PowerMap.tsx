"use client";

import { motion } from "framer-motion";
import { Zap } from "lucide-react";
import { Player } from "../types";
import PlayerDot from "./PlayerDot";

interface PowerMapProps {
  players: Player[];
  onPlayerClick: (player: Player) => void;
}

export default function PowerMap({ players, onPlayerClick }: PowerMapProps) {
  return (
    <motion.section
      className="mb-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        <motion.div
          animate={{ rotate: [0, 10, -10, 0] }}
          transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
        >
          <Zap className="text-yellow-500 w-5 h-5" />
        </motion.div>
        Live Power Map
      </h2>

      {/* Chart container with axis labels */}
      <div className="flex">
        {/* Y-axis label (rotated, outside) */}
        <div className="flex items-center justify-center w-12">
          <span className="text-sm font-bold text-white -rotate-90 whitespace-nowrap tracking-wide">
            WEEKLY POWER (PLW)
          </span>
        </div>

        <div className="flex-1">
          {/* Y-axis numbers + Chart */}
          <div className="flex">
            {/* Y-axis numbers */}
            <div className="flex flex-col justify-between items-end pr-3 py-2 w-12">
              {[400, 300, 200, 100, 0].map((val) => (
                <span key={val} className="text-sm text-slate-300 font-mono font-medium">
                  {val}
                </span>
              ))}
            </div>

            {/* Main chart */}
            <div className="flex-1 h-[500px] bg-slate-900 rounded-xl relative overflow-hidden shadow-inner border border-slate-800">
              {/* Grid background */}
              <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 opacity-10 pointer-events-none">
                {Array.from({ length: 16 }).map((_, i) => (
                  <div key={i} className="border border-slate-500" />
                ))}
              </div>

              {/* Player dots */}
        {players.map((player, index) => (
          <motion.div
            key={player.id}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
          >
            <PlayerDot
              player={player}
              onClick={() => onPlayerClick(player)}
            />
          </motion.div>
        ))}

              {/* Empty state */}
              {players.length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <motion.div
                    className="text-slate-500 text-center"
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <p className="text-lg">Loading players...</p>
                    <p className="text-sm">Run the scraper to populate data</p>
                  </motion.div>
                </div>
              )}
            </div>
          </div>

          {/* X-axis numbers */}
          <div className="flex justify-between pl-12 pr-0 pt-2">
            {[0, 500, 1000, 1500, 2000].map((val) => (
              <span key={val} className="text-sm text-slate-300 font-mono font-medium">
                {val}
              </span>
            ))}
          </div>

          {/* X-axis label */}
          <div className="text-center pt-3 pl-12">
            <span className="text-sm font-bold text-white tracking-wide">
              USCF RATING
            </span>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
