import { defineConfig } from "vite"; import react from "@vitejs/plugin-react";
const target = process.env.VITE_API_TARGET || "http://localhost:8001";
export default defineConfig({plugins:[react()], server:{proxy:{"/videos": target, "/jobs":target, "/media":target}}});
