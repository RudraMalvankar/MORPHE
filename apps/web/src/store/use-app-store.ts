import { create } from "zustand";

interface AppState {
  activeProject: string | null;
  selectedPublisher: string;
  setActiveProject: (id: string | null) => void;
  setSelectedPublisher: (publisher: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeProject: null,
  selectedPublisher: "ieee",
  setActiveProject: (id) => set({ activeProject: id }),
  setSelectedPublisher: (publisher) => set({ selectedPublisher: publisher }),
}));
