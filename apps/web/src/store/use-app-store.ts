import { create } from "zustand";

type Tab =
  | "dashboard"
  | "workspaces"
  | "documents"
  | "nlp"
  | "generation"
  | "export"
  | "knowledge"
  | "analytics"
  | "settings";

interface AppState {
  activeProject: string | null;
  activeTab: Tab;
  setActiveProject: (id: string | null) => void;
  setActiveTab: (tab: Tab) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeProject: null,
  activeTab: "dashboard",
  setActiveProject: (id) => set({ activeProject: id }),
  setActiveTab: (tab) => set({ activeTab: tab }),
}));
