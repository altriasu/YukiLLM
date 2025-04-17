import { get } from 'jquery';
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useApiConfigStore = defineStore('apiConfig', () => {
    const config = ref([{
        id: "default",
        dataset: "",
        embdingModel: "",
        platform: "ALIYUN",
        modelName: "qvq-max-latest",
        task: "chat"
    }]);

    const addConfig = (newConfig) => {
        config.value.push(newConfig);
    }

    const getConfigById = (id) => {
        return computed(() => {
            return config.value.find(item => item.id === id);
        });
    }

    const removeConfig = (id) => {
        config.value = config.value.filter(item => item.id!== id);
    }

    return { config, addConfig, removeConfig, getConfigById };
})
