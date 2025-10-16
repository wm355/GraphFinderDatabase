import { defineStore } from 'pinia';

export const useDatasetsStore = defineStore('datasets', {
  state: () => ({
    uploads: [] // each item: { id, title, y_label, datasets }
  }),
  actions: {
    addUpload(item) {
      // newest first
      this.uploads.unshift(item);
    }
  }
});
