import { defineStore } from 'pinia'
import { reactive, computed } from 'vue'

export const useApiConfigStore = defineStore('apiConfig', () => {
    let config = reactive({
        dataset: "RSITMD",
        embdingModel: "RemoteClip",
        platform: "百炼",
        modelName: "qwen-vl-max",
        task: "img2txt"
    })

    return { config }
})
