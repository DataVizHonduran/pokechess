"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Player } from "../types";
import { X } from "lucide-react";
import Image from "next/image";

interface PlayerCardProps {
  player: Player | null;
  onClose: () => void;
}

export default function PlayerCard({ player, onClose }: PlayerCardProps) {
  const isElite = player && player.tier === "legendary";

  return (
    <AnimatePresence>
      {player && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className={`relative w-full max-w-sm aspect-[2.5/3.5] rounded-xl shadow-2xl overflow-hidden ${
              isElite ? "border-4 border-yellow-500" : ""
            }`}
            initial={{ scale: 0.8, rotateY: -90, opacity: 0 }}
            animate={{ scale: 1, rotateY: 0, opacity: 1 }}
            exit={{ scale: 0.8, rotateY: 90, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Card background */}
            <div
              className={`h-full flex flex-col p-6 text-white ${
                isElite
                  ? "bg-gradient-to-br from-gray-900 to-black"
                  : "bg-gradient-to-br from-indigo-600 to-purple-700"
              }`}
            >
              {/* Close button */}
              <motion.button
                className="absolute top-4 right-4 text-white/60 hover:text-white"
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
              >
                <X size={24} />
              </motion.button>

              {/* Header */}
              <div className="flex justify-between items-start">
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <span className="font-bold text-xl block">{player.name}</span>
                  <span className="text-sm text-yellow-400 font-medium">
                    {player.pokemonName}
                  </span>
                </motion.div>
                <motion.span
                  className="text-xl font-black"
                  initial={{ x: 20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  HP {player.uscf}
                </motion.span>
              </div>

              {/* Pokemon image */}
              <div className="flex-1 flex items-center justify-center">
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{
                    type: "spring",
                    stiffness: 200,
                    damping: 15,
                    delay: 0.2,
                  }}
                >
                  <Image
                    src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${player.pokemonId}.png`}
                    alt={`${player.name}'s Pokemon`}
                    width={192}
                    height={192}
                    className="object-contain drop-shadow-2xl"
                    unoptimized
                  />
                </motion.div>
              </div>

              {/* Stats */}
              <motion.div
                className="bg-black/20 p-4 rounded-lg"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className="flex justify-between mb-2">
                  <span className="text-white/80">Puzzles Solved</span>
                  <motion.span
                    className="font-bold"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.4, type: "spring" }}
                  >
                    {player.puzzles}
                  </motion.span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/80">Group</span>
                  <motion.span
                    className="font-bold"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.45, type: "spring" }}
                  >
                    {player.group}
                  </motion.span>
                </div>
                <div className="mt-4 text-center border-t border-white/20 pt-4">
                  <motion.span
                    className="text-4xl font-black block"
                    initial={{ scale: 0 }}
                    animate={{ scale: [0, 1.2, 1] }}
                    transition={{ delay: 0.5, duration: 0.4 }}
                  >
                    {player.plw}
                  </motion.span>
                  <span className="text-xs uppercase opacity-60">
                    Weekly Power
                  </span>
                </div>
              </motion.div>

              {/* Elite badge */}
              {isElite && (
                <motion.div
                  className="absolute top-4 left-4"
                  initial={{ rotate: -45, scale: 0 }}
                  animate={{ rotate: 0, scale: 1 }}
                  transition={{ delay: 0.6, type: "spring" }}
                >
                  <span className="bg-yellow-500 text-black text-xs font-bold px-2 py-1 rounded">
                    ELITE
                  </span>
                </motion.div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
