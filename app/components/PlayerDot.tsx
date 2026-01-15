"use client";

import { motion } from "framer-motion";
import { Player } from "../types";

interface PlayerDotProps {
  player: Player;
  onClick: () => void;
}

export default function PlayerDot({ player, onClick }: PlayerDotProps) {
  const isElite = player.tier === "legendary";
  const xPos = Math.min((player.uscf / 2000) * 100, 98);
  const yPos = Math.min((player.plw / 400) * 100, 98);

  return (
    <motion.div
      className="absolute cursor-pointer group"
      style={{ left: `${xPos}%`, bottom: `${yPos}%` }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.3, zIndex: 10 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      onClick={onClick}
    >
      {/* Ping animation for rising players */}
      {player.delta > 0 && (
        <motion.div
          className="absolute -inset-4 rounded-full border border-yellow-500/50"
          animate={{ scale: [1, 1.5], opacity: [0.75, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}

      {/* Player dot */}
      <motion.div
        className={`relative w-10 h-10 rounded-full border-2 flex items-center justify-center shadow-lg ${
          isElite
            ? "bg-yellow-500 border-yellow-200"
            : "bg-slate-700 border-slate-500 group-hover:bg-indigo-500"
        }`}
        whileHover={{ rotate: [0, -5, 5, 0] }}
        transition={{ duration: 0.3 }}
      >
        <span className="text-[10px] font-bold text-white">
          {player.name.split(" ")[0].charAt(0)}
        </span>
      </motion.div>

      {/* Tooltip */}
      <motion.div
        className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none"
        initial={{ y: 5 }}
        whileHover={{ y: 0 }}
      >
        {player.name}
      </motion.div>
    </motion.div>
  );
}
