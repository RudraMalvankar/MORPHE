import { create } from "zustand";

interface AppState {
  activeProject: string | null;
  selectedPublisher: string;
  activeTab: string;
  setActiveProject: (id: string | null) => void;
  setSelectedPublisher: (publisher: string) => void;
  setActiveTab: (tab: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeProject: null,
  selectedPublisher: "ieee",
  activeTab: "workspaces",
  setActiveProject: (id) => {
    console.log("ZUSTAND: setActiveProject called with:", id);
    set({ activeProject: id });
  },
  setSelectedPublisher: (publisher) => set({ selectedPublisher: publisher }),
  setActiveTab: (tab) => {
    console.log("ZUSTAND: setActiveTab called with:", tab);
    set({ activeTab: tab });
  },
}));

